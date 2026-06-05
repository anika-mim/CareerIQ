"""Candidate scoring engine for CareerIQ."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from careeriq.dashboard.market_dashboard import ROLE_CATEGORY_SQL, read_sql
from careeriq.resume.profile_parser import CandidateProfile


TARGET_ROLE_CATEGORY = {
    "Data Analyst": "Data and BI",
    "Business Analyst": "Business Analysis",
    "Software Engineer": "Software Engineering",
    "Software Developer": "Software Engineering",
    "Full Stack Engineer": "Software Engineering",
    "Frontend Developer": "Software Engineering",
    "Backend Developer": "Software Engineering",
    "IT Support Technician": "IT and User Support",
    "User Support Technician": "IT and User Support",
    "Project Manager": "Project and Product Management",
    "Product Manager": "Project and Product Management",
    "HR Specialist": "Human Resources",
    "Recruiter": "Human Resources",
    "Marketing Coordinator": "Sales and Marketing",
    "Sales Representative": "Sales and Marketing",
    "Operations Coordinator": "Operations",
    "Entry-level Tech Professional": "All",
    "General Career Explorer": "All",
}


@dataclass(frozen=True)
class SkillGap:
    """A high-demand skill missing from the candidate profile."""

    skill_name: str
    skill_category: str
    demand_count: int
    demand_percentage: float
    priority_level: str
    recommendation_reason: str


@dataclass(frozen=True)
class JobMatch:
    """A candidate-to-job match result."""

    job_id: int
    job_title: str
    company: str
    location: str
    job_match_score: float
    matched_skills: list[str]
    missing_skills: list[str]


@dataclass(frozen=True)
class CandidateScoreResult:
    """Complete scoring result for one parsed candidate profile."""

    target_role: str
    role_category: str
    market_competitiveness_score: float
    employability_score: float
    average_job_match_score: float
    best_job_match_score: float
    matched_market_skills: list[str] = field(default_factory=list)
    missing_skills: list[SkillGap] = field(default_factory=list)
    top_job_matches: list[JobMatch] = field(default_factory=list)
    scoring_notes: list[str] = field(default_factory=list)


def clamp_score(value: float) -> float:
    """Clamp a score to the 0-100 range and round for display."""

    return round(max(0.0, min(100.0, value)), 1)


def target_role_to_category(target_role: str) -> str:
    """Map a user-facing target role to a dashboard role category."""

    return TARGET_ROLE_CATEGORY.get(target_role, "All")


def role_category_where_clause(role_category: str) -> tuple[str, tuple]:
    """Return a SQL WHERE clause for role category filtering."""

    if role_category == "All":
        return "", ()
    return f"WHERE {ROLE_CATEGORY_SQL} = ?", (role_category,)


def candidate_skill_names(profile: CandidateProfile) -> set[str]:
    """Return normalized candidate skill names for set comparisons."""

    return {skill.name.lower() for skill in profile.skills}


def load_market_skill_demand(database_path: Path, role_category: str) -> pd.DataFrame:
    """Load demand counts for skills in the selected role category."""

    where_clause, params = role_category_where_clause(role_category)
    return read_sql(
        database_path,
        f"""
        SELECT
            s.skill_name,
            s.skill_category,
            COUNT(*) AS demand_count
        FROM job_posting_skills AS jps
        JOIN skills AS s
            ON s.skill_id = jps.skill_id
        JOIN job_postings AS jp
            ON jp.job_id = jps.job_id
        {where_clause}
        GROUP BY s.skill_id, s.skill_name, s.skill_category
        ORDER BY demand_count DESC, s.skill_name;
        """,
        params,
    )


def load_job_skill_matrix(database_path: Path, role_category: str) -> pd.DataFrame:
    """Load one row per job-skill relationship for job match scoring."""

    where_clause, params = role_category_where_clause(role_category)
    return read_sql(
        database_path,
        f"""
        SELECT
            jp.job_id,
            jp.job_title,
            jp.company,
            jp.city || ', ' || jp.province AS location,
            s.skill_name
        FROM job_postings AS jp
        JOIN job_posting_skills AS jps
            ON jps.job_id = jp.job_id
        JOIN skills AS s
            ON s.skill_id = jps.skill_id
        {where_clause}
        ORDER BY jp.job_id, s.skill_name;
        """,
        params,
    )


def calculate_weighted_skill_coverage(market_skills: pd.DataFrame, candidate_skills: set[str]) -> float:
    """Calculate demand-weighted skill coverage as a percentage."""

    if market_skills.empty:
        return 0.0

    total_demand = float(market_skills["demand_count"].sum())
    if total_demand == 0:
        return 0.0

    matched_demand = market_skills[
        market_skills["skill_name"].str.lower().isin(candidate_skills)
    ]["demand_count"].sum()
    return float(matched_demand) / total_demand * 100


def calculate_profile_depth_score(profile: CandidateProfile) -> float:
    """Score how complete the parsed resume profile is."""

    score = 0.0
    score += min(len(profile.skills), 8) / 8 * 40
    score += 15 if profile.education else 0
    score += 15 if profile.certifications else 0
    score += 20 if profile.experience else 0
    score += 10 if profile.projects else 0
    return clamp_score(score)


def calculate_skill_breadth_score(profile: CandidateProfile) -> float:
    """Score candidate breadth based on number of detected relevant skills."""

    return clamp_score(min(len(profile.skills), 10) / 10 * 100)


def build_skill_gaps(
    market_skills: pd.DataFrame,
    candidate_skills: set[str],
    total_postings: int,
    limit: int = 8,
) -> list[SkillGap]:
    """Return high-demand skills missing from the candidate profile."""

    if market_skills.empty:
        return []

    missing = market_skills[~market_skills["skill_name"].str.lower().isin(candidate_skills)].copy()
    if missing.empty:
        return []

    gaps = []
    for _, row in missing.head(limit).iterrows():
        demand_count = int(row["demand_count"])
        demand_percentage = round(demand_count / total_postings * 100, 1) if total_postings else 0.0
        if demand_percentage >= 60:
            priority = "high"
        elif demand_percentage >= 35:
            priority = "medium"
        else:
            priority = "low"
        gaps.append(
            SkillGap(
                skill_name=row["skill_name"],
                skill_category=row["skill_category"],
                demand_count=demand_count,
                demand_percentage=demand_percentage,
                priority_level=priority,
                recommendation_reason=f"Appears in {demand_count} relevant postings.",
            )
        )
    return gaps


def calculate_job_matches(job_skills: pd.DataFrame, candidate_skills: set[str], limit: int = 5) -> list[JobMatch]:
    """Calculate match scores for individual job postings."""

    if job_skills.empty:
        return []

    matches = []
    for job_id, group in job_skills.groupby("job_id"):
        required_skills = sorted(set(group["skill_name"].tolist()))
        matched = [skill for skill in required_skills if skill.lower() in candidate_skills]
        missing = [skill for skill in required_skills if skill.lower() not in candidate_skills]
        score = len(matched) / len(required_skills) * 100 if required_skills else 0.0
        first_row = group.iloc[0]
        matches.append(
            JobMatch(
                job_id=int(job_id),
                job_title=first_row["job_title"],
                company=first_row["company"],
                location=first_row["location"],
                job_match_score=clamp_score(score),
                matched_skills=matched,
                missing_skills=missing,
            )
        )

    return sorted(matches, key=lambda item: item.job_match_score, reverse=True)[:limit]


def score_candidate_profile(
    profile: CandidateProfile,
    target_role: str,
    database_path: Path,
    job_match_limit: int = 5,
) -> CandidateScoreResult:
    """Score a parsed candidate profile against the job market database."""

    role_category = target_role_to_category(target_role)
    market_skills = load_market_skill_demand(database_path, role_category)
    job_skills = load_job_skill_matrix(database_path, role_category)
    candidate_skills = candidate_skill_names(profile)

    weighted_skill_coverage = calculate_weighted_skill_coverage(market_skills, candidate_skills)
    profile_depth = calculate_profile_depth_score(profile)
    skill_breadth = calculate_skill_breadth_score(profile)
    total_relevant_postings = int(job_skills["job_id"].nunique()) if not job_skills.empty else 0
    gaps = build_skill_gaps(market_skills, candidate_skills, total_relevant_postings)
    job_matches = calculate_job_matches(job_skills, candidate_skills, limit=job_match_limit)

    matched_market_skills = market_skills[
        market_skills["skill_name"].str.lower().isin(candidate_skills)
    ]["skill_name"].tolist()

    best_job_match = job_matches[0].job_match_score if job_matches else 0.0
    average_job_match = (
        sum(match.job_match_score for match in job_matches) / len(job_matches) if job_matches else 0.0
    )

    market_competitiveness = weighted_skill_coverage * 0.7 + best_job_match * 0.2 + profile_depth * 0.1
    employability = weighted_skill_coverage * 0.5 + skill_breadth * 0.25 + profile_depth * 0.25

    notes = [
        "Market competitiveness weights demand-weighted skill coverage, best job match, and profile depth.",
        "Employability weights demand-weighted skill coverage, skill breadth, and resume profile completeness.",
        "Job match compares detected candidate skills with required skills from each posting.",
    ]

    return CandidateScoreResult(
        target_role=target_role,
        role_category=role_category,
        market_competitiveness_score=clamp_score(market_competitiveness),
        employability_score=clamp_score(employability),
        average_job_match_score=clamp_score(average_job_match),
        best_job_match_score=clamp_score(best_job_match),
        matched_market_skills=matched_market_skills,
        missing_skills=gaps,
        top_job_matches=job_matches,
        scoring_notes=notes,
    )
