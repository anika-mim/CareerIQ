"""Command wrapper for loading the CareerIQ sample job market dataset."""

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from careeriq.jobs.load_job_postings import load_job_postings


if __name__ == "__main__":
    summary = load_job_postings(
        csv_path=PROJECT_ROOT / "data" / "raw" / "sample_canadian_job_postings.csv",
        database_path=PROJECT_ROOT / "data" / "processed" / "careeriq_dev.sqlite",
        schema_path=PROJECT_ROOT / "database" / "schema.sql",
        replace=True,
    )
    print("CareerIQ sample job data loaded")
    print(f"Rows read: {summary.rows_read}")
    print(f"Job postings loaded: {summary.job_postings_loaded}")
    print(f"Unique skills loaded: {summary.unique_skills_loaded}")
    print(f"Job-skill links loaded: {summary.job_skill_links_loaded}")

