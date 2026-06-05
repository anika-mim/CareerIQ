# Milestone 4 - Resume Profile Parser

## Goal

Milestone 4 converts cleaned resume text into a structured candidate profile.

The app now extracts:

- Skills
- Education
- Certifications
- Work experience lines
- Project lines

It can also save the parsed profile into SQLite.

## Files Added

```text
src/careeriq/resume/profile_parser.py
src/careeriq/resume/profile_repository.py
tests/test_resume_profile_parser.py
docs/MILESTONE_4_RESUME_PROFILE_PARSER.md
```

## Files Updated

```text
app.py
README.md
docs/DEVELOPMENT_PLAN.md
```

## How The Parser Works

Version 1 uses transparent rule-based extraction.

That means the code looks for known skill phrases such as:

- SQL
- Excel
- Power BI
- Python
- Active Directory
- Ticketing Systems

It also looks for resume section headers such as:

- Education
- Certifications
- Work Experience
- Projects

This is intentionally simple. For a portfolio interview, it is better to explain a clear rule-based baseline than to hide the logic inside a black-box model.

## Why This Matters

The app now moves from raw text extraction to structured career intelligence.

Cleaned resume text is useful, but not enough. The scoring engine needs structured fields so it can compare the candidate against job market data.

Example:

```text
Candidate skills: SQL, Excel, Power BI
Market skills: SQL, Excel, Power BI, Python, Data Cleaning
Missing skills: Python, Data Cleaning
```

That comparison becomes the foundation for Milestone 5 and Milestone 6.

## How To Run

From the project root:

```bash
streamlit run app.py
```

Upload a PDF resume. The app will show:

- Resume metadata
- Parsed profile counts
- Detected skills table
- Education lines
- Certification lines
- Experience lines
- Project lines

Click `Save parsed profile` to store the result in SQLite.

## How To Test

From the project root:

```bash
python -m unittest discover -s tests -v
```

The tests check:

- Skill extraction
- Education extraction
- Certification extraction
- Experience extraction
- Project extraction
- Candidate profile database persistence

## Junior Analyst Explanation

Think of the resume as a messy paragraph and the parsed profile as a clean table.

Before:

```text
I used SQL, Excel, and Power BI in a dashboard project.
```

After:

```text
Skills: SQL, Excel, Power BI
Projects: dashboard project
```

That structured format is what makes scoring and skill gap analysis possible.

## Future Improvement

Later versions can add spaCy entity recognition or an LLM layer. The Version 1 baseline should stay rule-based because it is predictable, testable, and easy to explain.

