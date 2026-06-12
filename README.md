<<<<<<<HEAD
# CareerIQ - AI-Powered Job Market Intelligence Platform

CareerIQ is a job market intelligence app that helps job seekers understand how well their resume matches the Canadian job market.

Users can upload a PDF resume, and the app extracts key career signals such as skills, education, experience, certifications, and projects. It then compares the profile with sample Canadian job posting data and provides practical insights like match scores, missing skills, in-demand skills, hiring cities, and a focused learning roadmap.

## Why I Built This

Many job seekers apply without knowing how their resume compares to real job postings. I built CareerIQ to make that process more data-driven and easier to understand.

This project combines data analytics, resume parsing, NLP, SQL, and dashboarding in one practical portfolio project.

## Tech Stack

Python
Streamlit
SQLite
Pandas
pdfplumber
spaCy
SQL
Data visualization

## Main Features

Upload and extract text from PDF resumes
Parse skills, education, experience, certifications, and projects
Load job posting data into a SQLite database
Analyze high-demand skills and hiring locations
Calculate an explainable candidate match score
Identify missing skills based on job market demand
Generate a focused learning roadmap
Show job market insights through Streamlit dashboards
Display a personalized profile page after resume upload

## How It Works

The user uploads a PDF resume.
The app extracts and cleans the resume text.
Resume information is parsed into structured career signals.
Job posting data is loaded from a sample dataset into SQLite.
The app compares the candidate profile with job market data.
Results are shown through scores, insights, charts, and recommendations.

## Project Highlights

This project demonstrates:

Data analytics and dashboard development
SQL database design and querying
Python data pipelines
Resume parsing with NLP
Skill gap analysis
Job market analysis
Product thinking
Clean project structure
Testing and documentation

## Run The App

pip install -r requirements.txt
python scripts/load_sample_jobs.py
streamlit run app.py
## Run Milestone 2 Data Load

## Run Tests

python -m unittest discover -s tests -v
The loader creates a local SQLite database at:


## Project Structure

CareerGuide/
  app.py
  data/
  database/
  docs/
  scripts/
  src/careeriq/
  tests/


## Dataset

The project uses a small curated sample dataset of Canadian job postings for portfolio demonstration. The current sample includes 41 postings across technical and non-technical role families.

## APP
>>>>>>>>>>>>    https://careeriq-h3zf.onrender.com/
