# Milestone 3 - Resume Text Extraction

## Goal

Milestone 3 lets a user upload a PDF resume and extract clean text from it.

This is the first resume intelligence step. A PDF resume is unstructured data. Before CareerIQ can detect skills, education, certifications, or experience, the app needs reliable text extraction.

## Files Added

```text
app.py
src/careeriq/resume/text_extraction.py
tests/test_resume_text_extraction.py
docs/MILESTONE_3_RESUME_TEXT_EXTRACTION.md
```

## What The Module Does

1. Validates that the uploaded file is a PDF.
2. Uses `pdfplumber` to extract text from each page.
3. Joins page text into one resume text string.
4. Cleans spacing, line breaks, and blank lines.
5. Returns a structured result with file name, raw text, cleaned text, page count, and word count.

## Why This Matters

Resume parsing starts with text extraction.

For a junior analyst, think of this like importing raw data before cleaning it. If the extraction step is messy, every later analysis step becomes weaker.

The cleaned text becomes the input for Milestone 4:

- Skill extraction
- Education extraction
- Certification extraction
- Experience extraction
- Project extraction

## How To Run The App

From the project root:

```bash
streamlit run app.py
```

Then open the local URL Streamlit prints, usually:

```text
http://localhost:8501
```

## How To Test

From the project root:

```bash
python -m unittest discover -s tests -v
```

The tests check:

- Resume text cleaning
- Word counting
- PDF file validation

## Portfolio Talking Point

This milestone shows that the project can handle unstructured data. That matters because real resumes are not clean tables. CareerIQ starts by converting a PDF into structured text that later modules can analyze.

