"""SQLite persistence for CareerIQ analysis results."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from careeriq.analysis.scoring import CandidateScoreResult
from careeriq.jobs.load_job_postings import get_or_create_skill, initialize_database


def save_analysis_result(
    database_path: Path,
    schema_path: Path,
    candidate_id: int,
    result: CandidateScoreResult,
) -> int:
    """Save one candidate analysis run and return the analysis id."""

    connection = sqlite3.connect(database_path)
    try:
        initialize_database(connection, schema_path)
        cursor = connection.execute(
            """
            INSERT INTO analysis_runs (
                candidate_id,
                target_role,
                market_competitiveness_score,
                employability_score,
                notes
            )
            VALUES (?, ?, ?, ?, ?);
            """,
            (
                candidate_id,
                result.target_role,
                result.market_competitiveness_score,
                result.employability_score,
                "\n".join(result.scoring_notes),
            ),
        )
        analysis_id = int(cursor.lastrowid)

        for match in result.top_job_matches:
            connection.execute(
                """
                INSERT INTO job_match_results (
                    analysis_id,
                    job_id,
                    role_title,
                    job_match_score,
                    matched_skill_count,
                    missing_skill_count
                )
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (
                    analysis_id,
                    match.job_id,
                    match.job_title,
                    match.job_match_score,
                    len(match.matched_skills),
                    len(match.missing_skills),
                ),
            )

        for gap in result.missing_skills:
            skill_id = get_or_create_skill(connection, gap.skill_name)
            connection.execute(
                """
                INSERT INTO skill_gap_results (
                    analysis_id,
                    skill_id,
                    demand_count,
                    demand_percentage,
                    priority_level,
                    recommendation_reason
                )
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (
                    analysis_id,
                    skill_id,
                    gap.demand_count,
                    gap.demand_percentage,
                    gap.priority_level,
                    gap.recommendation_reason,
                ),
            )

        connection.commit()
        return analysis_id
    finally:
        connection.close()

