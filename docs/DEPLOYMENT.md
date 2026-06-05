# CareerIQ Deployment Guide

## Local Run

From the project root:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/load_sample_jobs.py
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

## Streamlit Community Cloud Deployment

1. Push the project to GitHub.
2. Go to Streamlit Community Cloud.
3. Create a new app.
4. Select the GitHub repository.
5. Set the main file path:

```text
app.py
```

6. Deploy the app.

## Important Notes

The SQLite database at `data/processed/careeriq_dev.sqlite` is generated locally and ignored by Git.

For the deployed app, users can load sample job data from the dashboard tab. The app uses:

```text
data/raw/sample_canadian_job_postings.csv
```

as the seed dataset.

## Recommended Python Runtime

The project includes:

```text
runtime.txt
```

with:

```text
python-3.11
```

Python 3.11 is recommended for deployment even though the project also runs locally on Python 3.8.

