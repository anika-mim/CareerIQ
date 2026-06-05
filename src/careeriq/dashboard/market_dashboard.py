"""Job market dashboard queries for CareerIQ."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


ROLE_CATEGORY_SQL = """
CASE
    WHEN LOWER(job_title) LIKE '%software%'
      OR LOWER(job_title) LIKE '%developer%'
      OR LOWER(job_title) LIKE '%full stack%'
      OR LOWER(job_title) LIKE '%frontend%'
      OR LOWER(job_title) LIKE '%front-end%'
      OR LOWER(job_title) LIKE '%backend%'
      OR LOWER(job_title) LIKE '%back-end%'
      OR LOWER(job_title) LIKE '%devops%'
      OR LOWER(job_title) LIKE '%qa%'
      THEN 'Software Engineering'
    WHEN LOWER(job_title) LIKE '%data%'
      OR LOWER(job_title) LIKE '%bi%'
      OR LOWER(job_title) LIKE '%report%'
      THEN 'Data and BI'
    WHEN LOWER(job_title) LIKE '%business%'
      OR LOWER(job_title) LIKE '%process%'
      THEN 'Business Analysis'
    WHEN LOWER(job_title) LIKE '%project manager%'
      OR LOWER(job_title) LIKE '%project coordinator%'
      OR LOWER(job_title) LIKE '%program manager%'
      OR LOWER(job_title) LIKE '%product manager%'
      THEN 'Project and Product Management'
    WHEN LOWER(job_title) LIKE '%hr%'
      OR LOWER(job_title) LIKE '%human resources%'
      OR LOWER(job_title) LIKE '%recruit%'
      OR LOWER(job_title) LIKE '%talent%'
      THEN 'Human Resources'
    WHEN LOWER(job_title) LIKE '%marketing%'
      OR LOWER(job_title) LIKE '%sales%'
      OR LOWER(job_title) LIKE '%customer success%'
      THEN 'Sales and Marketing'
    WHEN LOWER(job_title) LIKE '%operations%'
      OR LOWER(job_title) LIKE '%coordinator%'
      THEN 'Operations'
    WHEN LOWER(job_title) LIKE '%support%'
      OR LOWER(job_title) LIKE '%desk%'
      OR LOWER(job_title) LIKE '%technician%'
      OR LOWER(job_title) LIKE '%it analyst%'
      THEN 'IT and User Support'
    ELSE 'Other'
END
"""


def read_sql(database_path: Path, query: str, params: tuple = ()) -> pd.DataFrame:
    """Read a SQL query into a DataFrame and close the connection."""

    connection = sqlite3.connect(database_path)
    try:
        return pd.read_sql_query(query, connection, params=params)
    finally:
        connection.close()


def job_postings_exist(database_path: Path) -> bool:
    """Return True when the job market database has postings."""

    if not database_path.exists():
        return False

    connection = sqlite3.connect(database_path)
    try:
        result = connection.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type = 'table' AND name = 'job_postings';"
        ).fetchone()
        if not result or result[0] == 0:
            return False
        count = connection.execute("SELECT COUNT(*) FROM job_postings;").fetchone()[0]
        return int(count) > 0
    finally:
        connection.close()


def load_role_categories(database_path: Path) -> list[str]:
    """Return role categories found in the job posting table."""

    dataframe = read_sql(
        database_path,
        f"""
        SELECT DISTINCT {ROLE_CATEGORY_SQL} AS role_category
        FROM job_postings
        ORDER BY role_category;
        """,
    )
    return dataframe["role_category"].tolist()


def build_role_category_filter(role_category: str) -> tuple[str, tuple]:
    """Build a reusable SQL filter for role category selections."""

    if role_category == "All":
        return "", ()

    return f"WHERE {ROLE_CATEGORY_SQL} = ?", (role_category,)


def load_market_overview(database_path: Path, role_category: str = "All") -> dict[str, int]:
    """Return top-level job market metrics."""

    where_clause, params = build_role_category_filter(role_category)
    dataframe = read_sql(
        database_path,
        f"""
        SELECT
            COUNT(*) AS posting_count,
            COUNT(DISTINCT company) AS company_count,
            COUNT(DISTINCT city || ', ' || province) AS location_count,
            COUNT(DISTINCT employment_type) AS employment_type_count
        FROM job_postings
        {where_clause};
        """,
        params,
    )
    row = dataframe.iloc[0].to_dict()
    return {key: int(value or 0) for key, value in row.items()}


def load_top_skills(database_path: Path, role_category: str = "All", limit: int = 12) -> pd.DataFrame:
    """Return the most frequently requested skills."""

    where_clause, params = build_role_category_filter(role_category)
    return read_sql(
        database_path,
        f"""
        SELECT
            s.skill_name,
            s.skill_category,
            COUNT(*) AS posting_count
        FROM job_posting_skills AS jps
        JOIN skills AS s
            ON s.skill_id = jps.skill_id
        JOIN job_postings AS jp
            ON jp.job_id = jps.job_id
        {where_clause}
        GROUP BY s.skill_id, s.skill_name, s.skill_category
        ORDER BY posting_count DESC, s.skill_name
        LIMIT ?;
        """,
        params + (limit,),
    )


def load_top_cities(database_path: Path, role_category: str = "All", limit: int = 10) -> pd.DataFrame:
    """Return cities with the most job postings."""

    where_clause, params = build_role_category_filter(role_category)
    return read_sql(
        database_path,
        f"""
        SELECT
            city || ', ' || province AS location,
            COUNT(*) AS posting_count
        FROM job_postings
        {where_clause}
        GROUP BY city, province
        ORDER BY posting_count DESC, location
        LIMIT ?;
        """,
        params + (limit,),
    )


def load_experience_requirements(database_path: Path, role_category: str = "All") -> pd.DataFrame:
    """Return job posting counts by experience level."""

    where_clause, params = build_role_category_filter(role_category)
    return read_sql(
        database_path,
        f"""
        SELECT
            experience_level,
            COUNT(*) AS posting_count,
            ROUND(AVG(min_years_experience), 1) AS avg_min_years
        FROM job_postings
        {where_clause}
        GROUP BY experience_level
        ORDER BY posting_count DESC, experience_level;
        """,
        params,
    )


def load_role_category_demand(database_path: Path) -> pd.DataFrame:
    """Return posting counts by broad role category."""

    return read_sql(
        database_path,
        f"""
        SELECT
            {ROLE_CATEGORY_SQL} AS role_category,
            COUNT(*) AS posting_count
        FROM job_postings
        GROUP BY role_category
        ORDER BY posting_count DESC, role_category;
        """,
    )


def load_employment_type_mix(database_path: Path, role_category: str = "All") -> pd.DataFrame:
    """Return posting counts by employment type."""

    where_clause, params = build_role_category_filter(role_category)
    return read_sql(
        database_path,
        f"""
        SELECT
            employment_type,
            COUNT(*) AS posting_count
        FROM job_postings
        {where_clause}
        GROUP BY employment_type
        ORDER BY posting_count DESC, employment_type;
        """,
        params,
    )
