from pathlib import Path
import csv
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from careeriq.dashboard.market_dashboard import (
    job_postings_exist,
    load_experience_requirements,
    load_market_overview,
    load_role_categories,
    load_role_category_demand,
    load_top_cities,
    load_top_skills,
)
from careeriq.jobs.load_job_postings import load_job_postings


def sample_job_count():
    with open(PROJECT_ROOT / "data" / "raw" / "sample_canadian_job_postings.csv", newline="", encoding="utf-8") as csv_file:
        return sum(1 for _ in csv.DictReader(csv_file))


class MarketDashboardTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "careeriq_dashboard_test.sqlite"
        load_job_postings(
            csv_path=PROJECT_ROOT / "data" / "raw" / "sample_canadian_job_postings.csv",
            database_path=self.database_path,
            schema_path=PROJECT_ROOT / "database" / "schema.sql",
            replace=True,
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_job_postings_exist_returns_true_after_load(self):
        self.assertTrue(job_postings_exist(self.database_path))

    def test_market_overview_counts_loaded_sample_data(self):
        overview = load_market_overview(self.database_path)

        self.assertEqual(overview["posting_count"], sample_job_count())
        self.assertGreaterEqual(overview["company_count"], 20)
        self.assertGreaterEqual(overview["location_count"], 10)

    def test_top_skills_returns_dashboard_ready_dataframe(self):
        top_skills = load_top_skills(self.database_path, limit=5)

        self.assertEqual(list(top_skills.columns), ["skill_name", "skill_category", "posting_count"])
        self.assertIn("SQL", set(top_skills["skill_name"]))
        self.assertGreaterEqual(int(top_skills["posting_count"].max()), 10)

    def test_role_category_filter_changes_overview(self):
        all_overview = load_market_overview(self.database_path)
        data_overview = load_market_overview(self.database_path, role_category="Data and BI")

        self.assertLess(data_overview["posting_count"], all_overview["posting_count"])
        self.assertGreater(data_overview["posting_count"], 0)

    def test_dashboard_dimension_queries_return_rows(self):
        self.assertGreater(len(load_role_categories(self.database_path)), 0)
        self.assertGreater(len(load_top_cities(self.database_path)), 0)
        self.assertGreater(len(load_experience_requirements(self.database_path)), 0)
        self.assertGreater(len(load_role_category_demand(self.database_path)), 0)

    def test_expanded_role_categories_include_technical_and_non_technical_roles(self):
        categories = set(load_role_categories(self.database_path))

        self.assertIn("Software Engineering", categories)
        self.assertIn("Human Resources", categories)
        self.assertIn("Project and Product Management", categories)


if __name__ == "__main__":
    unittest.main()
