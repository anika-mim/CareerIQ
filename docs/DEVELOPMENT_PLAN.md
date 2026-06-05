# CareerIQ Development Plan

## Guiding Principle

Build one useful module at a time. Each milestone should produce something visible, testable, and explainable in an interview.

## Milestone 1: Architecture and Database

Goal:

- Define the system architecture
- Design the SQLite schema
- Create the starter project structure

Deliverables:

- README
- Architecture document
- Database design document
- SQL schema

Why this matters:

- Good projects are easier to build when the data model is clear.
- This shows product thinking and engineering discipline.

## Milestone 2: Job Market Data Loader

Goal:

- Load a CSV of Canadian job postings into SQLite.

Deliverables:

- Sample job posting CSV
- Data cleaning script
- Database loader
- Basic SQL validation queries

Junior analyst explanation:

- Think of this as turning messy spreadsheet data into structured database tables.
- Once the data is structured, dashboards and analysis become much easier.

Status:

- Complete for Version 1 sample data.

Run:

```bash
python scripts/load_sample_jobs.py
python -m unittest discover -s tests -v
```

## Milestone 3: Resume Text Extraction

Goal:

- Upload a PDF resume and extract clean text.

Deliverables:

- Streamlit upload page
- pdfplumber extraction function
- Text cleaning function
- Unit tests for text cleaning

Junior analyst explanation:

- A resume PDF is not analysis-ready data.
- The first job is to convert it into clean text that Python can process.

Status:

- Complete for Version 1 PDF text extraction.

Run:

```bash
streamlit run app.py
python -m unittest discover -s tests -v
```

## Milestone 4: Resume Profile Parser

Goal:

- Extract structured career information from resume text.

Deliverables:

- Skill extraction
- Education extraction
- Certification extraction
- Experience extraction
- Candidate profile storage

Junior analyst explanation:

- This turns unstructured text into fields we can compare against job postings.

Status:

- Complete for Version 1 rule-based parsing and SQLite profile saving.

Run:

```bash
streamlit run app.py
python -m unittest discover -s tests -v
```

## Milestone 5: Market Intelligence Dashboard

Goal:

- Visualize job market trends.

Deliverables:

- Most in-demand skills chart
- Top hiring cities chart
- Experience requirement chart
- Role filter

Junior analyst explanation:

- This is business intelligence: summarizing raw records into insights people can act on.

Status:

- Complete for Version 1 sample job market dashboard.

Run:

```bash
python scripts/load_sample_jobs.py
streamlit run app.py
python -m unittest discover -s tests -v
```

## Milestone 6: Candidate Scoring Engine

Goal:

- Compare candidate skills against the job market.

Deliverables:

- Market Competitiveness Score
- Employability Score
- Job Match Score
- Skill gap table

Junior analyst explanation:

- A score is just a business rule converted into math.
- The score should be simple enough that a recruiter or hiring manager can understand it.

Status:

- Complete for Version 1 explainable candidate scoring.

Run:

```bash
python scripts/load_sample_jobs.py
streamlit run app.py
python -m unittest discover -s tests -v
```

## Milestone 7: Career Roadmap Generator

Goal:

- Recommend what the candidate should learn next.

Deliverables:

- Skill priority ranking
- Suggested certifications
- Suggested projects
- Target roles

Junior analyst explanation:

- The roadmap connects the analysis to action.
- Insights are more valuable when they tell users what to do next.

Status:

- Complete for Version 1 career roadmap recommendations.

Run:

```bash
python scripts/load_sample_jobs.py
streamlit run app.py
python -m unittest discover -s tests -v
```

## Milestone 8: Testing, Documentation, and Deployment

Goal:

- Make the project portfolio-ready.

Deliverables:

- Unit tests
- README screenshots
- Sample resume
- Sample dataset
- Streamlit Cloud deployment
- GitHub project board or issues

## GitHub Best Practices

- Use clear commit messages.
- Keep commits small and focused.
- Write a README that explains the business problem, not just the code.
- Add screenshots or GIFs after the app is running.
- Include setup instructions.
- Include a short architecture section.
- Include limitations and future improvements.

## Testing Best Practices

Start with practical tests:

- Text cleaning tests
- Skill matching tests
- Scoring logic tests
- Database loading tests

The goal is not 100 percent coverage. The goal is confidence in the most important logic.

## Deployment Plan

Use Streamlit Community Cloud for free deployment.

Required files later:

- `requirements.txt`
- `app.py`
- SQLite database creation or seed step
- README deployment instructions

Status:

- Complete for Version 1 deployment readiness.
