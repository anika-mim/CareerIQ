# CareerIQ Database Design

## Design Goals

The database should support three core workflows:

1. Store job market data.
2. Store extracted resume profile data.
3. Compare candidates against market demand.

SQLite is used in Version 1 because it is simple, portable, and portfolio-friendly.

## Entity Overview

```text
job_postings
  |
  | many-to-many
  v
skills

candidate_profiles
  |
  | many-to-many
  v
skills

candidate_profiles
  |-- candidate_education
  |-- candidate_certifications
  |-- candidate_experience
  |-- candidate_projects

analysis_runs
  |-- skill_gap_results
  |-- job_match_results
```

## Core Tables

### job_postings

Stores one row per job posting.

Important fields:

- job title
- company
- city
- province
- employment type
- experience level
- posting date
- source

### skills

Stores normalized skill names.

Example:

- Python
- SQL
- Excel
- Power BI
- Tableau
- Active Directory
- Ticketing Systems

Keeping skills in a separate table avoids duplicates and makes dashboard queries easier.

### job_posting_skills

Connects job postings to required skills.

This is a many-to-many table because:

- One job requires many skills.
- One skill appears in many jobs.

### candidate_profiles

Stores one row per uploaded resume profile.

Version 1 can treat each upload as a separate candidate profile. A future SaaS version can connect profiles to user accounts.

### candidate_skills

Connects candidates to extracted skills.

Includes confidence because extracted resume skills may not always be perfect.

### candidate_education

Stores education extracted from the resume.

### candidate_certifications

Stores certifications extracted from the resume.

### candidate_experience

Stores work experience signals from the resume.

### candidate_projects

Stores portfolio or academic projects from the resume.

### analysis_runs

Stores each time a candidate is analyzed.

This is useful because the job market dataset may change over time.

### skill_gap_results

Stores missing and recommended skills from an analysis run.

### job_match_results

Stores role-level or posting-level match scores.

## Scoring Fields

Scores should be stored as numeric values from 0 to 100:

- market_competitiveness_score
- employability_score
- job_match_score

Version 1 scoring should be simple and explainable:

- Skill overlap
- Demand frequency of matched skills
- Experience alignment
- Education or certification bonus

## Schema File

The first executable schema is stored in:

```text
database/schema.sql
```

