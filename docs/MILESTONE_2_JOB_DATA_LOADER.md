# Milestone 2 - Job Market Data Loader

## Goal

Milestone 2 turns a flat CSV file of Canadian job postings into a structured SQLite database.

This is the first data engineering step in CareerIQ. Before we can build dashboards, scoring, or resume comparisons, job market data must be clean, queryable, and connected to normalized skills.

## Files Added

```text
data/raw/sample_canadian_job_postings.csv
src/careeriq/jobs/load_job_postings.py
scripts/load_sample_jobs.py
database/validation_queries.sql
tests/test_job_posting_loader.py
requirements.txt
```

## What The Loader Does

1. Reads the CSV with Pandas.
2. Validates that all required columns exist.
3. Cleans text fields.
4. Converts numeric fields such as salary and years of experience.
5. Splits the `skills_required` field into individual skills.
6. Normalizes skill names such as `sql` into `SQL` and `power bi` into `Power BI`.
7. Inserts job postings into SQLite.
8. Inserts unique skills into the `skills` table.
9. Creates many-to-many relationships in `job_posting_skills`.

## Why This Matters

A CSV is easy to read, but it is not the best structure for analysis.

For example, one job posting can require many skills, and one skill can appear in many job postings. This is a many-to-many relationship. In SQL, we model that using:

- `job_postings`
- `skills`
- `job_posting_skills`

This design makes dashboard questions easy to answer:

- Which skills are most in demand?
- Which cities have the most postings?
- Which role categories are hiring?
- What experience level appears most often?

## How To Run

From the project root:

```bash
python scripts/load_sample_jobs.py
```

Expected result:

```text
CareerIQ sample job data loaded
Rows read: 41
Job postings loaded: 41
Unique skills loaded: 59
Job-skill links loaded: 246
```

## How To Test

From the project root:

```bash
python -m unittest discover -s tests -v
```

The tests check that:

- Skill parsing normalizes names and removes duplicates.
- The sample CSV loads into SQLite.
- Expected job, skill, and relationship records are created.

## Validation Queries

Reusable SQL queries are stored in:

```text
database/validation_queries.sql
```

Example insights from the sample data:

- Top skills: Excel, SQL, Communication, Documentation, Power BI
- Top cities: Toronto, Vancouver, Montreal, Ottawa
- Strong categories: Data Analytics, Software Engineering, Business Intelligence, IT Support, Business Analysis, HR, Project Management

## Junior Analyst Explanation

Think of this milestone as moving from spreadsheet thinking to database thinking.

In a spreadsheet, the skills are stored in one cell:

```text
SQL; Excel; Power BI; Python
```

That is readable for a human, but hard for analytics. The loader splits those skills into separate records so SQL can count demand correctly.

This is the foundation for the future dashboard and candidate scoring engine.
