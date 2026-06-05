# Milestone 6 - Candidate Scoring Engine

## Goal

Milestone 6 compares a parsed resume profile against the job market database.

The app now generates:

- Market Competitiveness Score
- Employability Score
- Best Job Match Score
- Average Top Match Score
- Matched market skills
- Missing high-demand skills
- Top matching job postings

## Files Added

```text
src/careeriq/analysis/scoring.py
src/careeriq/analysis/repository.py
tests/test_candidate_scoring.py
docs/MILESTONE_6_CANDIDATE_SCORING_ENGINE.md
```

## Files Updated

```text
app.py
README.md
docs/DEVELOPMENT_PLAN.md
```

## How The Scoring Works

The scoring is intentionally transparent.

### Market Competitiveness Score

This score estimates how competitive the candidate is against the selected market slice.

Formula:

```text
70% demand-weighted skill coverage
20% best job match score
10% resume profile completeness
```

### Employability Score

This score estimates overall readiness for entry-level tech roles.

Formula:

```text
50% demand-weighted skill coverage
25% skill breadth
25% resume profile completeness
```

### Job Match Score

Each posting is scored by comparing candidate skills with required job skills.

Formula:

```text
matched required skills / total required skills * 100
```

## Why This Matters

This milestone turns CareerIQ from a dashboard into a decision-support product.

The user no longer only sees market trends. They can now answer:

- How strong is my current profile?
- Which job postings do I match best?
- Which high-demand skills am I missing?
- What should I learn next?

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

Upload a PDF resume in the Resume intelligence tab. The Career scores section appears after parsing.

## How To Test

From the project root:

```bash
python -m unittest discover -s tests -v
```

The tests check:

- Target role to market category mapping
- Profile depth scoring
- Candidate score generation
- Missing skill recommendations
- Job match generation
- Analysis result persistence in SQLite

## Junior Analyst Explanation

Think of scoring as turning a business rule into math.

If the market asks for SQL in many postings and your resume includes SQL, your score improves. If many postings ask for Power BI and Python but your resume does not mention them, those skills become recommended gaps.

The score is not magic. It is a structured comparison between:

```text
Candidate profile
vs.
Job market demand
```

## Portfolio Talking Point

This milestone demonstrates product analytics, SQL-backed analysis, and explainable scoring logic. It is more interview-friendly than a black-box model because every score can be traced back to job posting data and resume signals.

