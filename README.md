<<<<<<< HEAD
# CareerIQ - AI-Powered Job Market Intelligence Platform

CareerIQ is a minimalist portfolio project that helps job seekers understand how competitive they are in the Canadian job market.

Users upload a resume, the app extracts career signals, compares them with job posting data, and returns practical insights such as match scores, missing skills, high-demand skills, and a focused learning roadmap.

## Target Users

- Data Analysts
- Business Analysts
- IT Support Technicians
- User Support Technicians
- Entry-level Tech Professionals
- Software Engineers
- Developers
- Full Stack Engineers
- Project Managers
- Product Managers
- HR and Recruiting Professionals
- Marketing, Sales, and Operations Professionals

## Version 1 Scope

Version 1 is intentionally practical and portfolio-focused:

- Streamlit frontend
- Python backend
- SQLite database
- Pandas for analysis
- pdfplumber for PDF resume text extraction
- spaCy for NLP-assisted parsing
- Personalized post-upload profile page with candidate greeting
- Simple scoring logic that is easy to explain in interviews
- Dashboard views for job market intelligence
- Visitor counter for portfolio engagement tracking

## Portfolio Skills Demonstrated

- Data analytics and dashboarding
- SQL schema design and querying
- Python data pipelines
- Resume parsing with NLP
- Skill gap analysis
- Product thinking
- Clean project structure
- Testing and documentation

## Project Status

Current phase: Version 1 complete.

See:

- [System Architecture](docs/ARCHITECTURE.md)
- [Database Design](docs/DATABASE_DESIGN.md)
- [Development Plan](docs/DEVELOPMENT_PLAN.md)
- [Milestone 2 Job Data Loader](docs/MILESTONE_2_JOB_DATA_LOADER.md)
- [Milestone 3 Resume Text Extraction](docs/MILESTONE_3_RESUME_TEXT_EXTRACTION.md)
- [Milestone 4 Resume Profile Parser](docs/MILESTONE_4_RESUME_PROFILE_PARSER.md)
- [Milestone 5 Job Market Dashboard](docs/MILESTONE_5_JOB_MARKET_DASHBOARD.md)
- [Milestone 6 Candidate Scoring Engine](docs/MILESTONE_6_CANDIDATE_SCORING_ENGINE.md)
- [Milestone 7 Career Roadmap Generator](docs/MILESTONE_7_CAREER_ROADMAP_GENERATOR.md)
- [Milestone 8 Portfolio Polish and Deployment](docs/MILESTONE_8_PORTFOLIO_POLISH_DEPLOYMENT.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Portfolio Review](docs/PORTFOLIO_REVIEW.md)

## Features

- Upload PDF resumes
- Extract clean resume text
- Parse skills, education, certifications, experience, and projects
- Load Canadian job postings into SQLite
- Analyze in-demand skills and hiring cities
- Calculate explainable candidate scores
- Identify missing high-demand skills
- Recommend a career roadmap
- Visualize job market trends in Streamlit
- Greet the candidate by extracted name when available
- Show an optional profile image or professional initials avatar
- Highlight highest and lowest bars in dashboard charts
- Provide clear messages when a PDF cannot be extracted reliably

## Run The App

From the project root:

```bash
pip install -r requirements.txt
python scripts/load_sample_jobs.py
streamlit run app.py
```

## Run Milestone 2 Data Load

From the project root:

```bash
python scripts/load_sample_jobs.py
python -m unittest discover -s tests -v
```

The loader creates a local SQLite database at:

```text
data/processed/careeriq_dev.sqlite
```

That generated database is ignored by Git. The source CSV is tracked because it is a small curated sample dataset for portfolio demonstration.

The sample dataset currently includes 41 Canadian postings across technical and non-technical role families.

## Run Tests

```bash
python -m unittest discover -s tests -v
```

## Project Structure

```text
CareerGuide/
  app.py
  data/
  database/
  docs/
  scripts/
  src/careeriq/
  tests/
```

## Deployment

CareerIQ is ready for Streamlit Community Cloud. See [Deployment Guide](docs/DEPLOYMENT.md).
=======
# CareerIQ
>>>>>>> 8285f99c2feebcddb8a941325e9c07bcdb9df1bc
