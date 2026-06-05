# Milestone 5 - Job Market Dashboard

## Goal

Milestone 5 turns the loaded job posting data into a business intelligence dashboard.

The dashboard answers practical job market questions:

- Which skills are most in demand?
- Which cities have the most postings?
- What experience levels are employers asking for?
- Which role categories are most active?
- What employment types appear in the market?
- How demand differs across technical and non-technical role families?

## Files Added

```text
src/careeriq/dashboard/market_dashboard.py
tests/test_market_dashboard.py
docs/MILESTONE_5_JOB_MARKET_DASHBOARD.md
```

## Files Updated

```text
app.py
README.md
docs/DEVELOPMENT_PLAN.md
```

## Dashboard Views

The Streamlit app now has two main tabs:

- Resume intelligence
- Job market dashboard

The dashboard includes:

- Job postings count
- Company count
- Location count
- Employment type count
- Most in-demand skills
- Top hiring cities
- Experience requirements
- Hiring by role category
- Employment type mix
- Highlighted highest and lowest bars using soothing colors

## How The Data Flows

```text
CSV job postings
   |
   v
SQLite tables
   |
   v
Dashboard SQL queries
   |
   v
Pandas DataFrames
   |
   v
Streamlit charts and tables
```

## Why This Matters

This milestone demonstrates business intelligence.

A recruiter or hiring manager does not want to inspect raw job posting rows. They want summarized patterns. The dashboard turns raw records into market-level insights that can support career decisions.

## How To Run

From the project root:

```bash
python scripts/load_sample_jobs.py
streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

## How To Test

From the project root:

```bash
python -m unittest discover -s tests -v
```

The tests check:

- Job posting data exists after loading
- Market overview metrics are correct
- Top skills query returns dashboard-ready data
- Role category filtering works
- Dashboard dimension queries return rows

## Junior Analyst Explanation

This milestone is like building a reporting dashboard from a cleaned database.

The raw table has one row per job posting. The dashboard groups those rows by skill, city, experience level, and role category. This is the same pattern used in business reporting tools like Power BI, Tableau, and Looker.

## Portfolio Talking Point

This milestone shows that CareerIQ is not only an NLP project. It is also a data analytics and BI product with a real database, SQL queries, metrics, filters, and dashboard visuals.
