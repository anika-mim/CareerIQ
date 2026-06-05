from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from careeriq.analysis.repository import save_analysis_result
from careeriq.analysis.scoring import (
    calculate_profile_depth_score,
    score_candidate_profile,
    target_role_to_category,
)
from careeriq.jobs.load_job_postings import load_job_postings
from careeriq.resume.profile_parser import parse_resume_profile
from careeriq.resume.profile_repository import save_candidate_profile


SAMPLE_ANALYST_RESUME = """
Data Analyst

Skills
SQL, Excel, Power BI, Python, Data Cleaning, Communication

Education
Diploma in Business Analytics

Certifications
Google Data Analytics Certificate

Work Experience
Data Analyst Intern, 2025
Built KPI reports and cleaned operational data.

Projects
Power BI Sales Dashboard Project
"""


class CandidateScoringTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "careeriq_scoring_test.sqlite"
        load_job_postings(
            csv_path=PROJECT_ROOT / "data" / "raw" / "sample_canadian_job_postings.csv",
            database_path=self.database_path,
            schema_path=PROJECT_ROOT / "database" / "schema.sql",
            replace=True,
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_target_role_maps_to_market_category(self):
        self.assertEqual(target_role_to_category("Data Analyst"), "Data and BI")
        self.assertEqual(target_role_to_category("Business Analyst"), "Business Analysis")
        self.assertEqual(target_role_to_category("Software Engineer"), "Software Engineering")
        self.assertEqual(target_role_to_category("HR Specialist"), "Human Resources")
        self.assertEqual(target_role_to_category("Unknown Role"), "All")

    def test_profile_depth_score_rewards_complete_profiles(self):
        profile = parse_resume_profile(SAMPLE_ANALYST_RESUME)

        self.assertGreaterEqual(calculate_profile_depth_score(profile), 80)

    def test_score_candidate_profile_returns_scores_and_gaps(self):
        profile = parse_resume_profile(SAMPLE_ANALYST_RESUME)
        result = score_candidate_profile(profile, "Data Analyst", self.database_path)

        self.assertGreater(result.market_competitiveness_score, 40)
        self.assertGreater(result.employability_score, 50)
        self.assertGreater(result.best_job_match_score, 50)
        self.assertGreater(len(result.top_job_matches), 0)
        self.assertGreater(len(result.missing_skills), 0)
        self.assertIn("SQL", result.matched_market_skills)

    def test_save_analysis_result_persists_scores_matches_and_gaps(self):
        profile = parse_resume_profile(SAMPLE_ANALYST_RESUME)
        score_result = score_candidate_profile(profile, "Data Analyst", self.database_path)
        candidate_id = save_candidate_profile(
            database_path=self.database_path,
            schema_path=PROJECT_ROOT / "database" / "schema.sql",
            resume_file_name="analyst.pdf",
            raw_resume_text=SAMPLE_ANALYST_RESUME,
            target_role="Data Analyst",
            profile=profile,
        )
        analysis_id = save_analysis_result(
            database_path=self.database_path,
            schema_path=PROJECT_ROOT / "database" / "schema.sql",
            candidate_id=candidate_id,
            result=score_result,
        )

        connection = sqlite3.connect(self.database_path)
        try:
            analysis_count = connection.execute(
                "SELECT COUNT(*) FROM analysis_runs WHERE analysis_id = ?;",
                (analysis_id,),
            ).fetchone()[0]
            match_count = connection.execute(
                "SELECT COUNT(*) FROM job_match_results WHERE analysis_id = ?;",
                (analysis_id,),
            ).fetchone()[0]
            gap_count = connection.execute(
                "SELECT COUNT(*) FROM skill_gap_results WHERE analysis_id = ?;",
                (analysis_id,),
            ).fetchone()[0]
        finally:
            connection.close()

        self.assertEqual(analysis_count, 1)
        self.assertGreater(match_count, 0)
        self.assertGreater(gap_count, 0)


if __name__ == "__main__":
    unittest.main()
