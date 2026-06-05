"""Career roadmap generation for CareerIQ."""

from __future__ import annotations

from dataclasses import dataclass, field

from careeriq.analysis.scoring import CandidateScoreResult
from careeriq.resume.profile_parser import CandidateProfile


CERTIFICATION_RECOMMENDATIONS = {
    "Data and BI": [
        "Microsoft Power BI Data Analyst Associate",
        "Google Data Analytics Professional Certificate",
        "Tableau Desktop Specialist",
    ],
    "Business Analysis": [
        "ECBA - Entry Certificate in Business Analysis",
        "Microsoft Power BI Data Analyst Associate",
        "Scrum Fundamentals Certified",
    ],
    "IT and User Support": [
        "CompTIA A+",
        "Microsoft 365 Fundamentals",
        "ITIL 4 Foundation",
    ],
    "Software Engineering": [
        "Meta Front-End Developer Professional Certificate",
        "AWS Cloud Practitioner",
        "Microsoft Azure Fundamentals",
    ],
    "Project and Product Management": [
        "Certified Associate in Project Management",
        "Scrum Fundamentals Certified",
        "Google Project Management Professional Certificate",
    ],
    "Human Resources": [
        "CHRP Knowledge Exam Preparation",
        "LinkedIn Learning HR Foundations",
        "HRPA Essentials of HR Law",
    ],
    "Sales and Marketing": [
        "Google Digital Marketing and E-commerce Certificate",
        "HubSpot Inbound Marketing Certification",
        "Google Analytics Certification",
    ],
    "Operations": [
        "Lean Six Sigma Yellow Belt",
        "Google Project Management Professional Certificate",
        "Excel Skills for Business",
    ],
    "All": [
        "Google Data Analytics Professional Certificate",
        "Microsoft 365 Fundamentals",
        "Scrum Fundamentals Certified",
    ],
}

PROJECT_RECOMMENDATIONS = {
    "Data and BI": [
        "Build a Power BI dashboard using the CareerIQ job posting dataset.",
        "Create a SQL portfolio project that analyzes hiring trends by city and skill.",
        "Publish a Python data cleaning notebook for messy job posting data.",
    ],
    "Business Analysis": [
        "Create a requirements document and process map for a job application tracker.",
        "Build a Power BI dashboard that tracks support ticket KPIs.",
        "Write user stories and acceptance criteria for a resume analysis feature.",
    ],
    "IT and User Support": [
        "Document a help desk ticket triage workflow with escalation rules.",
        "Create a knowledge base sample for common Microsoft 365 support issues.",
        "Build a simple asset inventory tracker using SQLite and Streamlit.",
    ],
    "Software Engineering": [
        "Build a full-stack CRUD app with authentication and a relational database.",
        "Create a REST API with tests and deployment documentation.",
        "Refactor an existing project and write a technical case study explaining the architecture.",
    ],
    "Project and Product Management": [
        "Create a project charter, timeline, risk register, and stakeholder communication plan.",
        "Write a product requirements document for a resume intelligence feature.",
        "Build a lightweight dashboard that tracks project delivery KPIs.",
    ],
    "Human Resources": [
        "Create a recruiting funnel dashboard with candidate stages and conversion rates.",
        "Design an onboarding checklist and HR policy knowledge base.",
        "Analyze employee engagement survey data and summarize recommendations.",
    ],
    "Sales and Marketing": [
        "Create a marketing campaign dashboard with leads, conversions, and ROI.",
        "Write a customer segmentation analysis using spreadsheet or SQL data.",
        "Build a CRM pipeline report and explain sales performance trends.",
    ],
    "Operations": [
        "Create an operations KPI dashboard for service levels and backlog.",
        "Document a process improvement case study with before-and-after metrics.",
        "Build an inventory or scheduling tracker with SQLite and Streamlit.",
    ],
    "All": [
        "Create a dashboard that summarizes skills demand by target role.",
        "Write a case study explaining how CareerIQ scores a resume.",
        "Build one small project that uses SQL, Python, and a dashboard together.",
    ],
}

TARGET_ROLE_PROGRESSIONS = {
    "Data Analyst": ["Junior Data Analyst", "Data Analyst", "BI Analyst", "Analytics Consultant"],
    "Business Analyst": ["Junior Business Analyst", "Business Analyst", "Business Systems Analyst", "Product Analyst"],
    "Software Engineer": ["Junior Software Developer", "Software Engineer", "Full Stack Engineer", "Senior Software Engineer"],
    "Software Developer": ["Junior Software Developer", "Software Developer", "Full Stack Developer", "Software Engineer"],
    "Full Stack Engineer": ["Junior Full Stack Developer", "Full Stack Engineer", "Software Engineer", "Technical Lead"],
    "Frontend Developer": ["Junior Frontend Developer", "Frontend Developer", "Full Stack Developer", "UI Engineer"],
    "Backend Developer": ["Junior Backend Developer", "Backend Developer", "Software Engineer", "API Platform Engineer"],
    "IT Support Technician": ["Help Desk Technician", "IT Support Technician", "Service Desk Analyst", "Systems Support Analyst"],
    "User Support Technician": ["User Support Technician", "Service Desk Analyst", "Technical Support Analyst", "Customer Success Operations Analyst"],
    "Project Manager": ["Project Coordinator", "Junior Project Manager", "Project Manager", "Program Manager"],
    "Product Manager": ["Product Coordinator", "Associate Product Manager", "Product Manager", "Senior Product Manager"],
    "HR Specialist": ["HR Coordinator", "HR Specialist", "HR Generalist", "HR Business Partner"],
    "Recruiter": ["Recruiting Coordinator", "Recruiter", "Talent Acquisition Specialist", "Talent Partner"],
    "Marketing Coordinator": ["Marketing Assistant", "Marketing Coordinator", "Digital Marketing Specialist", "Marketing Manager"],
    "Sales Representative": ["Sales Development Representative", "Account Executive", "Sales Manager", "Revenue Operations Analyst"],
    "Operations Coordinator": ["Operations Assistant", "Operations Coordinator", "Operations Analyst", "Operations Manager"],
    "Entry-level Tech Professional": ["Support Analyst", "Junior Data Analyst", "Business Analyst", "BI Analyst"],
    "General Career Explorer": ["Coordinator", "Analyst", "Specialist", "Manager"],
}


@dataclass(frozen=True)
class RoadmapStep:
    """One recommended roadmap action."""

    priority: int
    title: str
    action: str
    reason: str


@dataclass(frozen=True)
class CareerRoadmap:
    """Generated roadmap for a candidate."""

    readiness_label: str
    summary: str
    learning_path: list[RoadmapStep] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    projects: list[str] = field(default_factory=list)
    target_roles: list[str] = field(default_factory=list)


def readiness_label(score: float) -> str:
    """Convert an employability score into a clear readiness label."""

    if score >= 75:
        return "Strong"
    if score >= 55:
        return "Competitive with gaps"
    if score >= 35:
        return "Developing"
    return "Early stage"


def build_learning_path(score_result: CandidateScoreResult) -> list[RoadmapStep]:
    """Convert missing skills into ordered learning actions."""

    steps = []
    for index, gap in enumerate(score_result.missing_skills[:5], start=1):
        steps.append(
            RoadmapStep(
                priority=index,
                title=f"Learn {gap.skill_name}",
                action=f"Complete a small project or course that demonstrates {gap.skill_name}.",
                reason=(
                    f"{gap.skill_name} appears in {gap.demand_percentage}% of relevant postings "
                    f"and is marked {gap.priority_level} priority."
                ),
            )
        )

    if not steps:
        steps.append(
            RoadmapStep(
                priority=1,
                title="Strengthen portfolio evidence",
                action="Add one project that clearly demonstrates your strongest matched skills.",
                reason="No major missing skills were detected, so the next improvement is stronger proof of ability.",
            )
        )

    return steps


def build_roadmap_summary(score_result: CandidateScoreResult, profile: CandidateProfile) -> str:
    """Create a concise plain-English roadmap summary."""

    label = readiness_label(score_result.employability_score)
    skill_count = len(profile.skills)
    missing_count = len(score_result.missing_skills)
    return (
        f"Readiness: {label}. CareerIQ detected {skill_count} skills and "
        f"{missing_count} priority skill gaps for {score_result.target_role}."
    )


def generate_career_roadmap(
    profile: CandidateProfile,
    score_result: CandidateScoreResult,
) -> CareerRoadmap:
    """Generate a career roadmap from parsed resume data and scoring results."""

    role_category = score_result.role_category
    return CareerRoadmap(
        readiness_label=readiness_label(score_result.employability_score),
        summary=build_roadmap_summary(score_result, profile),
        learning_path=build_learning_path(score_result),
        certifications=CERTIFICATION_RECOMMENDATIONS.get(role_category, CERTIFICATION_RECOMMENDATIONS["All"]),
        projects=PROJECT_RECOMMENDATIONS.get(role_category, PROJECT_RECOMMENDATIONS["All"]),
        target_roles=TARGET_ROLE_PROGRESSIONS.get(score_result.target_role, TARGET_ROLE_PROGRESSIONS["Entry-level Tech Professional"]),
    )
