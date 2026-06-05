from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from careeriq.resume.text_extraction import clean_resume_text, count_words, validate_pdf_file_name


class ResumeTextExtractionTests(unittest.TestCase):
    def test_clean_resume_text_removes_extra_spacing(self):
        messy_text = "  Data Analyst  \r\n\r\n\r\n Skills:   SQL,   Excel  \n\n Experience  "

        cleaned = clean_resume_text(messy_text)

        self.assertEqual(cleaned, "Data Analyst\n\nSkills: SQL, Excel\n\nExperience")

    def test_count_words_handles_common_resume_tokens(self):
        text = "Python SQL Power BI C# Help-desk Microsoft 365"

        self.assertEqual(count_words(text), 8)

    def test_validate_pdf_file_name_rejects_non_pdf(self):
        with self.assertRaises(ValueError):
            validate_pdf_file_name("resume.docx")

    def test_validate_pdf_file_name_accepts_pdf(self):
        validate_pdf_file_name("resume.PDF")


if __name__ == "__main__":
    unittest.main()

