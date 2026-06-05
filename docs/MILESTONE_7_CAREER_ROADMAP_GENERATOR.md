# Milestone 7 - Career Roadmap Generator

## Goal

Milestone 7 turns score results into a practical career action plan.

The app now recommends:

- Learning path
- Certifications
- Portfolio projects
- Target role progression

## Files Added

```text
src/careeriq/analysis/roadmap.py
tests/test_career_roadmap.py
docs/MILESTONE_7_CAREER_ROADMAP_GENERATOR.md
```

## Files Updated

```text
app.py
README.md
docs/DEVELOPMENT_PLAN.md
```

## How The Roadmap Works

The roadmap uses the score result from Milestone 6.

Input:

- Candidate skills
- Missing high-demand skills
- Employability score
- Target role
- Role category

Output:

- Readiness label
- Learning priorities
- Certification suggestions
- Project suggestions
- Role progression

## Why This Matters

A score is useful, but a user also needs action.

For example, telling a candidate that they scored 58 out of 100 is not enough. CareerIQ should also explain what to improve next.

## Example

If a Data Analyst candidate is missing Python and Data Cleaning, the roadmap may recommend:

- Learn Python
- Build a Python data cleaning notebook
- Create a Power BI dashboard project
- Consider the Microsoft Power BI Data Analyst Associate certification

## Junior Analyst Explanation

Think of the roadmap as turning analysis into recommendations.

Analysis answers:

```text
What is happening?
```

The roadmap answers:

```text
What should I do next?
```

## How To Run

From the project root:

```bash
python scripts/load_sample_jobs.py
streamlit run app.py
```

Upload a resume. The roadmap appears in the Parsed profile tab after scoring.

## How To Test

From the project root:

```bash
python -m unittest discover -s tests -v
```

