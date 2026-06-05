from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from careeriq.resume.profile_parser import ParsedSkill, parse_resume_profile
from careeriq.resume.profile_repository import save_candidate_profile


SAMPLE_RESUME_TEXT = """
Jane Candidate
Data Analyst

Skills
SQL, Excel, Power BI, Python, Data Cleaning, Communication

Education
Diploma in Business Analytics, Toronto College, 2025

Certifications
Google Data Analytics Certificate
Microsoft Certified: Power BI Data Analyst

Work Experience
Junior Analyst Intern, NorthStar Retail, 2025
Built weekly KPI reports using SQL and Excel.

Projects
Sales Dashboard Project
Created a Power BI dashboard to track regional sales trends.
"""


class ResumeProfileParserTests(unittest.TestCase):
    def test_parse_resume_profile_extracts_core_sections(self):
        profile = parse_resume_profile(SAMPLE_RESUME_TEXT)
        skill_names = {skill.name for skill in profile.skills}

        self.assertEqual(profile.candidate_name, "Jane Candidate")
        self.assertIn("SQL", skill_names)
        self.assertIn("Power BI", skill_names)
        self.assertIn("Data Cleaning", skill_names)
        self.assertTrue(any("Diploma in Business Analytics" in item for item in profile.education))
        self.assertTrue(any("Google Data Analytics" in item for item in profile.certifications))
        self.assertTrue(any("Junior Analyst Intern" in item for item in profile.experience))
        self.assertTrue(any("Sales Dashboard Project" in item for item in profile.projects))

    def test_save_candidate_profile_persists_related_records(self):
        profile = parse_resume_profile(SAMPLE_RESUME_TEXT)

        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "careeriq_test.sqlite"
            candidate_id = save_candidate_profile(
                database_path=database_path,
                schema_path=PROJECT_ROOT / "database" / "schema.sql",
                resume_file_name="jane_candidate.pdf",
                raw_resume_text=SAMPLE_RESUME_TEXT,
                target_role="Data Analyst",
                profile=profile,
            )

            connection = sqlite3.connect(database_path)
            try:
                profile_count = connection.execute("SELECT COUNT(*) FROM candidate_profiles;").fetchone()[0]
                skill_count = connection.execute(
                    "SELECT COUNT(*) FROM candidate_skills WHERE candidate_id = ?;",
                    (candidate_id,),
                ).fetchone()[0]
                certification_count = connection.execute(
                    "SELECT COUNT(*) FROM candidate_certifications WHERE candidate_id = ?;",
                    (candidate_id,),
                ).fetchone()[0]
            finally:
                connection.close()

            self.assertEqual(profile_count, 1)
            self.assertGreaterEqual(skill_count, 5)
            self.assertGreaterEqual(certification_count, 2)

    def test_save_candidate_profile_accepts_minimal_profile(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "careeriq_test.sqlite"
            candidate_id = save_candidate_profile(
                database_path=database_path,
                schema_path=PROJECT_ROOT / "database" / "schema.sql",
                resume_file_name="minimal.pdf",
                raw_resume_text="SQL analyst",
                target_role="Data Analyst",
                profile=parse_resume_profile("SQL analyst"),
            )

            self.assertIsInstance(candidate_id, int)


if __name__ == "__main__":
    unittest.main()
