# CareerIQ System Architecture

## Product Goal

CareerIQ gives job seekers a clear answer to one question:

> How competitive am I for the roles I want, and what should I improve next?

For a portfolio project, the app should feel realistic, focused, and easy to explain. The goal is not to build every SaaS feature in Version 1. The goal is to show that you can design, build, analyze, and communicate an end-to-end data product.

Version 1 supports both technical and non-technical role families, including analytics, business analysis, software engineering, IT support, project/product management, HR, marketing, sales, and operations.

## Version 1 Architecture

```text
PDF Resume
   |
   v
Streamlit Upload UI
   |
   v
Resume Parser
   |-- pdfplumber extracts raw text
   |-- spaCy helps identify entities and noun phrases
   |-- rule-based matching extracts known skills, education, certifications
   |
   v
Candidate Profile
   |
   v
SQLite Database <-------- Job Posting Loader
   |                         |
   |                         v
   |                    CSV job posting data
   |
   v
Analysis Engine
   |-- market competitiveness score
   |-- employability score
   |-- job match score
   |-- missing skills
   |-- high-demand skills
   |
   v
Career Roadmap Generator
   |
   v
Streamlit Dashboard
```

## Main Components

### 1. Streamlit Frontend

Streamlit provides the user interface for:

- Uploading a resume PDF
- Selecting target roles
- Viewing scores
- Reviewing missing skills
- Exploring the job market dashboard

Why Streamlit:

- Fast to build
- Free deployment options
- Ideal for data portfolio projects
- Lets recruiters interact with the project without complex setup

### 2. Resume Parsing Module

This module converts a resume PDF into structured candidate data.

Responsibilities:

- Extract raw text from PDF files
- Clean and normalize text
- Detect skills, education, certifications, projects, and experience signals
- Store extracted profile data for analysis

Version 1 should combine NLP and rules. This is realistic because resumes are messy, and a fully automated parser is hard to make perfect.

### 3. Job Market Data Module

This module loads Canadian job posting data into SQLite.

Responsibilities:

- Import job postings from CSV
- Normalize job titles, cities, skills, and experience levels
- Store postings and skill relationships
- Support dashboard queries

For Version 1, the dataset can be a curated CSV from public job postings or a manually prepared sample dataset. The important portfolio story is the data model and analysis workflow.

### 4. Market Analysis Engine

This module compares a candidate profile against job postings.

Example outputs:

- Market Competitiveness Score
- Employability Score
- Job Match Score by role
- Missing skills
- High-demand skills
- Recommended next skills

The scoring logic should be transparent. In interviews, transparent scoring is often better than a black-box model because you can explain the business reasoning.

### 5. Career Roadmap Generator

This module converts analysis results into recommendations.

Example outputs:

- Skills to learn next
- Certifications to consider
- Suggested projects
- Target roles
- Career progression path

For Version 1, this can be rules-based. Later versions can add LLM-generated explanations.

### 6. Dashboard Module

The dashboard turns job posting data into business intelligence.

Views:

- Most in-demand skills
- Top hiring cities
- Experience requirements
- Hiring trends by role
- Skill demand by job category

## Folder Structure

```text
CareerGuide/
  README.md
  docs/
    ARCHITECTURE.md
    DATABASE_DESIGN.md
    DEVELOPMENT_PLAN.md
  database/
    schema.sql
  data/
    raw/
    processed/
  src/
    careeriq/
      resume/
      jobs/
      analysis/
      dashboard/
  tests/
```

## Technology Choices

### Python

Python is the best fit because the project combines data analysis, NLP, backend logic, and dashboard development.

### Streamlit

Chosen for fast, clean portfolio deployment. It avoids frontend complexity while still creating an interactive product.

### SQLite

Chosen because it is simple, free, portable, and excellent for demonstrating SQL skills. It can later be replaced by PostgreSQL if the product grows.

### Pandas

Chosen for cleaning job posting data, creating summary tables, and supporting analytics.

### pdfplumber

Chosen because it extracts text from PDF resumes more reliably than basic PDF readers.

### spaCy

Chosen for NLP tasks such as tokenization, entity recognition, phrase extraction, and future resume intelligence improvements.

### GitHub

Chosen for version control, documentation, issue tracking, and portfolio visibility.

## Future SaaS Evolution

Version 1 should stay minimal. Future versions can add:

- User accounts
- PostgreSQL
- Background job ingestion
- Live job board APIs
- LLM-generated resume feedback
- Paid career reports
- Admin dashboard
- Multi-country support
