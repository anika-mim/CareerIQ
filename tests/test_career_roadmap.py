from pathlib import Path
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from careeriq.analysis.roadmap import generate_career_roadmap, readiness_label
from careeriq.analysis.scoring import score_candidate_profile
from careeriq.jobs.load_job_postings import load_job_postings
from careeriq.resume.profile_parser import parse_resume_profile


SAMPLE_RESUME = """
Data Analyst

Skills
SQL, Excel, Power BI, Communication

Education
Diploma in Business Analytics

Work Experience
Reporting Analyst Intern, 2025

Projects
Power BI dashboard project
"""


class CareerRoadmapTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "careeriq_roadmap_test.sqlite"
        load_job_postings(
            csv_path=PROJECT_ROOT / "data" / "raw" / "sample_canadian_job_postings.csv",
            database_path=self.database_path,
            schema_path=PROJECT_ROOT / "database" / "schema.sql",
            replace=True,
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_readiness_label_boundaries(self):
        self.assertEqual(readiness_label(80), "Strong")
        self.assertEqual(readiness_label(60), "Competitive with gaps")
        self.assertEqual(readiness_label(40), "Developing")
        self.assertEqual(readiness_label(20), "Early stage")

    def test_generate_career_roadmap_returns_actionable_sections(self):
        profile = parse_resume_profile(SAMPLE_RESUME)
        score_result = score_candidate_profile(profile, "Data Analyst", self.database_path)
        roadmap = generate_career_roadmap(profile, score_result)

        self.assertGreaterEqual(len(roadmap.learning_path), 1)
        self.assertGreaterEqual(len(roadmap.certifications), 1)
        self.assertGreaterEqual(len(roadmap.projects), 1)
        self.assertIn("Data Analyst", roadmap.target_roles)
        self.assertIn("Readiness:", roadmap.summary)


if __name__ == "__main__":
    unittest.main()

