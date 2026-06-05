# Milestone 8 - Portfolio Polish and Deployment

## Goal

Milestone 8 makes CareerIQ portfolio-ready.

This milestone focuses on:

- Clean README
- Deployment instructions
- Test coverage
- Streamlit configuration
- GitHub presentation
- Clear project narrative

## Files Added

```text
.streamlit/config.toml
runtime.txt
docs/MILESTONE_8_PORTFOLIO_POLISH_DEPLOYMENT.md
docs/DEPLOYMENT.md
docs/PORTFOLIO_REVIEW.md
```

## Version 1 Features Completed

CareerIQ Version 1 includes:

- PDF resume upload
- Resume text extraction
- Personalized candidate greeting
- Optional profile image display
- Resume profile parsing
- SQLite job market database
- Job market dashboard
- Candidate scoring engine
- Skill gap analysis
- Career roadmap generator
- Site visit counter
- Highlighted dashboard chart colors
- Unit tests
- Streamlit deployment readiness

## How To Verify Locally

From the project root:

```bash
python scripts/load_sample_jobs.py
python -m unittest discover -s tests -v
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

## Deployment Target

Recommended free deployment:

- Streamlit Community Cloud

Why:

- Free
- Simple GitHub integration
- Good fit for Python data apps
- Recruiters can open a public link

## GitHub Portfolio Checklist

Before sharing publicly:

- Push project to GitHub.
- Add screenshots to the README.
- Add the Streamlit app URL.
- Add a short LinkedIn project post.
- Pin the repository on GitHub.
- Make sure no private resumes or generated databases are committed.

## Future Improvements

CareerIQ can evolve into a SaaS product by adding:

- User accounts
- PostgreSQL
- Real job board ingestion
- LLM resume feedback
- Resume improvement suggestions
- Paid career reports
- Admin dashboard
