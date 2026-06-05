from pathlib import Path
import csv
import sqlite3
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from careeriq.jobs.load_job_postings import load_job_postings, parse_skills


def sample_job_count():
    with open(PROJECT_ROOT / "data" / "raw" / "sample_canadian_job_postings.csv", newline="", encoding="utf-8") as csv_file:
        return sum(1 for _ in csv.DictReader(csv_file))


class JobPostingLoaderTests(unittest.TestCase):
    def test_parse_skills_normalizes_and_removes_duplicates(self):
        skills = parse_skills(" sql ; SQL; power bi ; Excel ")

        self.assertEqual(skills, ["SQL", "Power BI", "Excel"])

    def test_load_sample_jobs_creates_expected_database_records(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "careeriq_test.sqlite"
            summary = load_job_postings(
                csv_path=PROJECT_ROOT / "data" / "raw" / "sample_canadian_job_postings.csv",
                database_path=database_path,
                schema_path=PROJECT_ROOT / "database" / "schema.sql",
                replace=True,
            )

            expected_rows = sample_job_count()
            self.assertEqual(summary.rows_read, expected_rows)
            self.assertEqual(summary.job_postings_loaded, expected_rows)
            self.assertGreaterEqual(summary.unique_skills_loaded, 25)
            self.assertGreaterEqual(summary.job_skill_links_loaded, 100)

            connection = sqlite3.connect(database_path)
            try:
                top_skill = connection.execute(
                    """
                    SELECT s.skill_name
                    FROM job_posting_skills AS jps
                    JOIN skills AS s
                        ON s.skill_id = jps.skill_id
                    GROUP BY s.skill_id, s.skill_name
                    ORDER BY COUNT(*) DESC, s.skill_name
                    LIMIT 1;
                    """
                ).fetchone()
            finally:
                connection.close()

            self.assertIsNotNone(top_skill)
            self.assertIn(top_skill[0], {"Excel", "SQL", "Communication", "Ticketing Systems"})


if __name__ == "__main__":
    unittest.main()
