"""SQLite persistence for parsed candidate profiles."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from careeriq.jobs.load_job_postings import get_or_create_skill, initialize_database
from careeriq.resume.profile_parser import CandidateProfile


def save_candidate_profile(
    database_path: Path,
    schema_path: Path,
    resume_file_name: str,
    raw_resume_text: str,
    target_role: str,
    profile: CandidateProfile,
) -> int:
    """Save one parsed resume profile and return the candidate id."""

    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    try:
        initialize_database(connection, schema_path)
        cursor = connection.execute(
            """
            INSERT INTO candidate_profiles (
                resume_file_name,
                raw_resume_text,
                target_role,
                total_years_experience
            )
            VALUES (?, ?, ?, NULL);
            """,
            (resume_file_name, raw_resume_text, target_role),
        )
        candidate_id = int(cursor.lastrowid)

        for skill in profile.skills:
            skill_id = get_or_create_skill(connection, skill.name)
            connection.execute(
                """
                INSERT OR IGNORE INTO candidate_skills (
                    candidate_id,
                    skill_id,
                    confidence_score,
                    extraction_method
                )
                VALUES (?, ?, ?, ?);
                """,
                (candidate_id, skill_id, skill.confidence_score, skill.extraction_method),
            )

        for education in profile.education:
            connection.execute(
                """
                INSERT INTO candidate_education (candidate_id, program)
                VALUES (?, ?);
                """,
                (candidate_id, education),
            )

        for certification in profile.certifications:
            connection.execute(
                """
                INSERT INTO candidate_certifications (candidate_id, certification_name)
                VALUES (?, ?);
                """,
                (candidate_id, certification),
            )

        for experience in profile.experience:
            connection.execute(
                """
                INSERT INTO candidate_experience (candidate_id, description)
                VALUES (?, ?);
                """,
                (candidate_id, experience),
            )

        for project in profile.projects:
            connection.execute(
                """
                INSERT INTO candidate_projects (candidate_id, description)
                VALUES (?, ?);
                """,
                (candidate_id, project),
            )

        connection.commit()
        return candidate_id
    finally:
        connection.close()

