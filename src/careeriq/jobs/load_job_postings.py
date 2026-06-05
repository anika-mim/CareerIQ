"""Load Canadian job posting data into the CareerIQ SQLite database."""

from __future__ import annotations

import argparse
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd


REQUIRED_COLUMNS = {
    "job_title",
    "company",
    "city",
    "province",
    "employment_type",
    "experience_level",
    "min_years_experience",
    "max_years_experience",
    "salary_min",
    "salary_max",
    "posting_date",
    "source",
    "source_url",
    "description",
    "skills_required",
}

SKILL_CATEGORY_LOOKUP = {
    "a/b testing": "Analytics",
    "active directory": "IT Support",
    "agile": "Project Management",
    "api development": "Software Engineering",
    "attention to detail": "Professional Skills",
    "ats": "Human Resources",
    "benefits administration": "Human Resources",
    "budgeting": "Project Management",
    "c#": "Programming",
    "change management": "Project Management",
    "communication": "Professional Skills",
    "conflict resolution": "Human Resources",
    "crm": "Sales and Marketing",
    "css": "Software Engineering",
    "customer service": "Professional Skills",
    "dax": "Business Intelligence",
    "data cleaning": "Data Analytics",
    "data modeling": "Business Intelligence",
    "data quality": "Data Analytics",
    "data visualization": "Data Analytics",
    "django": "Software Engineering",
    "documentation": "Professional Skills",
    "employee relations": "Human Resources",
    "excel": "Data Analytics",
    "fastapi": "Software Engineering",
    "flask": "Software Engineering",
    "git": "Software Engineering",
    "google analytics": "Sales and Marketing",
    "hardware support": "IT Support",
    "html": "Software Engineering",
    "interviewing": "Human Resources",
    "java": "Programming",
    "javascript": "Software Engineering",
    "jira": "Business Analysis",
    "knowledge base": "IT Support",
    "kpi reporting": "Business Intelligence",
    "leadership": "Professional Skills",
    "market research": "Sales and Marketing",
    "microsoft 365": "IT Support",
    "networking": "IT Support",
    "node.js": "Software Engineering",
    "onboarding": "Human Resources",
    "payroll": "Human Resources",
    "performance management": "Human Resources",
    "power bi": "Business Intelligence",
    "process mapping": "Business Analysis",
    "product analytics": "Data Analytics",
    "project management": "Project Management",
    "python": "Programming",
    "react": "Software Engineering",
    "recruiting": "Human Resources",
    "requirements gathering": "Business Analysis",
    "risk management": "Project Management",
    "scrum": "Project Management",
    "seo": "Sales and Marketing",
    "sql": "Data Analytics",
    "stakeholder communication": "Project Management",
    "stakeholder management": "Business Analysis",
    "statistics": "Data Analytics",
    "talent acquisition": "Human Resources",
    "tableau": "Business Intelligence",
    "test automation": "Software Engineering",
    "ticketing systems": "IT Support",
    "troubleshooting": "IT Support",
    "typescript": "Software Engineering",
    "user stories": "Business Analysis",
    "vendor management": "Project Management",
    "windows": "IT Support",
}

SKILL_DISPLAY_NAMES = {
    "a/b testing": "A/B Testing",
    "ats": "ATS",
    "c#": "C#",
    "crm": "CRM",
    "css": "CSS",
    "dax": "DAX",
    "excel": "Excel",
    "fastapi": "FastAPI",
    "git": "Git",
    "html": "HTML",
    "java": "Java",
    "javascript": "JavaScript",
    "jira": "Jira",
    "kpi reporting": "KPI Reporting",
    "microsoft 365": "Microsoft 365",
    "node.js": "Node.js",
    "power bi": "Power BI",
    "python": "Python",
    "react": "React",
    "seo": "SEO",
    "sql": "SQL",
    "typescript": "TypeScript",
}


@dataclass(frozen=True)
class LoadSummary:
    """Simple result object for the job posting load process."""

    rows_read: int
    job_postings_loaded: int
    unique_skills_loaded: int
    job_skill_links_loaded: int


def clean_text(value: object) -> Optional[str]:
    """Return stripped text or None for blank values."""

    if pd.isna(value):
        return None
    text = str(value).strip()
    return text or None


def normalize_skill(skill: object) -> Optional[str]:
    """Normalize a skill name while keeping display-friendly capitalization."""

    text = clean_text(skill)
    if not text:
        return None
    normalized = " ".join(word.strip() for word in text.split()).lower()
    return SKILL_DISPLAY_NAMES.get(normalized, normalized.title())


def parse_skills(raw_skills: object) -> list[str]:
    """Split a semicolon-delimited skill field into unique normalized skills."""

    text = clean_text(raw_skills)
    if not text:
        return []

    skills: list[str] = []
    seen: set[str] = set()
    for item in text.split(";"):
        skill = normalize_skill(item)
        if skill and skill.lower() not in seen:
            skills.append(skill)
            seen.add(skill.lower())
    return skills


def skill_category(skill_name: str) -> str:
    """Return the skill category used for dashboard grouping."""

    return SKILL_CATEGORY_LOOKUP.get(skill_name.lower(), "Other")


def validate_columns(dataframe: pd.DataFrame) -> None:
    """Raise a clear error when the source CSV does not match expectations."""

    missing = REQUIRED_COLUMNS.difference(dataframe.columns)
    if missing:
        missing_columns = ", ".join(sorted(missing))
        raise ValueError(f"Missing required column(s): {missing_columns}")


def read_job_postings(csv_path: Path) -> pd.DataFrame:
    """Read and lightly clean the job postings CSV."""

    dataframe = pd.read_csv(csv_path)
    validate_columns(dataframe)

    for column in REQUIRED_COLUMNS:
        if column not in {"min_years_experience", "max_years_experience", "salary_min", "salary_max"}:
            dataframe[column] = dataframe[column].map(clean_text)

    numeric_columns = ["min_years_experience", "max_years_experience", "salary_min", "salary_max"]
    for column in numeric_columns:
        dataframe[column] = pd.to_numeric(dataframe[column], errors="coerce")

    dataframe["posting_date"] = pd.to_datetime(dataframe["posting_date"], errors="coerce").dt.date.astype(str)
    return dataframe


def initialize_database(connection: sqlite3.Connection, schema_path: Path) -> None:
    """Create database tables from the schema file."""

    connection.execute("PRAGMA foreign_keys = ON;")
    connection.executescript(schema_path.read_text(encoding="utf-8"))


def reset_job_market_tables(connection: sqlite3.Connection) -> None:
    """Remove job market records so a sample load can be repeated cleanly."""

    connection.execute("DELETE FROM job_posting_skills;")
    connection.execute("DELETE FROM job_postings;")
    connection.execute(
        """
        DELETE FROM skills
        WHERE skill_id NOT IN (
            SELECT skill_id FROM candidate_skills
            UNION
            SELECT skill_id FROM skill_gap_results
        );
        """
    )


def get_or_create_skill(connection: sqlite3.Connection, skill_name: str) -> int:
    """Insert a skill if needed and return its primary key."""

    connection.execute(
        """
        INSERT OR IGNORE INTO skills (skill_name, skill_category)
        VALUES (?, ?);
        """,
        (skill_name, skill_category(skill_name)),
    )
    result = connection.execute(
        "SELECT skill_id FROM skills WHERE skill_name = ?;",
        (skill_name,),
    ).fetchone()
    if result is None:
        raise RuntimeError(f"Could not create or find skill: {skill_name}")
    return int(result[0])


def find_existing_job_id(connection: sqlite3.Connection, row: pd.Series) -> Optional[int]:
    """Find an existing job posting using a practical source identity."""

    result = connection.execute(
        """
        SELECT job_id
        FROM job_postings
        WHERE job_title = ?
          AND company = ?
          AND city = ?
          AND province = ?
          AND posting_date = ?
          AND source_url = ?
        LIMIT 1;
        """,
        (
            row["job_title"],
            row["company"],
            row["city"],
            row["province"],
            row["posting_date"],
            row["source_url"],
        ),
    ).fetchone()
    return int(result[0]) if result else None


def upsert_job_posting(connection: sqlite3.Connection, row: pd.Series) -> int:
    """Insert or update one job posting and return its primary key."""

    values = (
        row["job_title"],
        row["company"],
        row["city"],
        row["province"],
        "Canada",
        row["employment_type"],
        row["experience_level"],
        row["min_years_experience"],
        row["max_years_experience"],
        row["salary_min"],
        row["salary_max"],
        row["posting_date"],
        row["source"],
        row["source_url"],
        row["description"],
    )
    existing_job_id = find_existing_job_id(connection, row)

    if existing_job_id:
        connection.execute(
            """
            UPDATE job_postings
            SET job_title = ?,
                company = ?,
                city = ?,
                province = ?,
                country = ?,
                employment_type = ?,
                experience_level = ?,
                min_years_experience = ?,
                max_years_experience = ?,
                salary_min = ?,
                salary_max = ?,
                posting_date = ?,
                source = ?,
                source_url = ?,
                description = ?
            WHERE job_id = ?;
            """,
            values + (existing_job_id,),
        )
        connection.execute("DELETE FROM job_posting_skills WHERE job_id = ?;", (existing_job_id,))
        return existing_job_id

    cursor = connection.execute(
        """
        INSERT INTO job_postings (
            job_title,
            company,
            city,
            province,
            country,
            employment_type,
            experience_level,
            min_years_experience,
            max_years_experience,
            salary_min,
            salary_max,
            posting_date,
            source,
            source_url,
            description
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        values,
    )
    return int(cursor.lastrowid)


def link_job_skills(connection: sqlite3.Connection, job_id: int, skills: Iterable[str]) -> int:
    """Create relationships between one job posting and its required skills."""

    link_count = 0
    for skill in skills:
        skill_id = get_or_create_skill(connection, skill)
        connection.execute(
            """
            INSERT OR IGNORE INTO job_posting_skills (job_id, skill_id, is_required)
            VALUES (?, ?, 1);
            """,
            (job_id, skill_id),
        )
        link_count += 1
    return link_count


def load_job_postings(
    csv_path: Path,
    database_path: Path,
    schema_path: Path,
    replace: bool = False,
) -> LoadSummary:
    """Load job posting CSV records into SQLite."""

    dataframe = read_job_postings(csv_path)
    database_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(database_path)
    try:
        initialize_database(connection, schema_path)
        if replace:
            reset_job_market_tables(connection)

        postings_loaded = 0
        skill_links_loaded = 0
        for _, row in dataframe.iterrows():
            job_id = upsert_job_posting(connection, row)
            skill_links_loaded += link_job_skills(connection, job_id, parse_skills(row["skills_required"]))
            postings_loaded += 1

        unique_skills = connection.execute("SELECT COUNT(*) FROM skills;").fetchone()[0]
        unique_links = connection.execute("SELECT COUNT(*) FROM job_posting_skills;").fetchone()[0]
        connection.commit()
    finally:
        connection.close()

    return LoadSummary(
        rows_read=len(dataframe),
        job_postings_loaded=postings_loaded,
        unique_skills_loaded=int(unique_skills),
        job_skill_links_loaded=int(unique_links if replace else skill_links_loaded),
    )


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line interface for the loader."""

    parser = argparse.ArgumentParser(description="Load CareerIQ job posting data into SQLite.")
    parser.add_argument("--csv", type=Path, default=Path("data/raw/sample_canadian_job_postings.csv"))
    parser.add_argument("--database", type=Path, default=Path("data/processed/careeriq_dev.sqlite"))
    parser.add_argument("--schema", type=Path, default=Path("database/schema.sql"))
    parser.add_argument("--replace", action="store_true", help="Clear job market tables before loading.")
    return parser


def main() -> None:
    """Run the job posting loader from the command line."""

    args = build_parser().parse_args()
    summary = load_job_postings(
        csv_path=args.csv,
        database_path=args.database,
        schema_path=args.schema,
        replace=args.replace,
    )
    print("CareerIQ job market load complete")
    print(f"Rows read: {summary.rows_read}")
    print(f"Job postings loaded: {summary.job_postings_loaded}")
    print(f"Unique skills in database: {summary.unique_skills_loaded}")
    print(f"Job-skill links in database: {summary.job_skill_links_loaded}")


if __name__ == "__main__":
    main()
