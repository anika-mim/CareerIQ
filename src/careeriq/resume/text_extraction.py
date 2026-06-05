"""PDF resume text extraction and cleaning utilities."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import BinaryIO, Optional, Union


@dataclass(frozen=True)
class ResumeTextResult:
    """Structured result returned after extracting resume text."""

    file_name: str
    raw_text: str
    cleaned_text: str
    page_count: int
    word_count: int
    embedded_image_count: int = 0


def clean_resume_text(text: Optional[str]) -> str:
    """Normalize resume text while preserving readable section breaks."""

    if not text:
        return ""

    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r" *\n *", "\n", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()


def count_words(text: Optional[str]) -> int:
    """Count word-like tokens in cleaned resume text."""

    if not text:
        return 0
    return len(re.findall(r"\b[\w+#.-]+\b", text))


def validate_pdf_file_name(file_name: str) -> None:
    """Raise a clear error when the uploaded file is not a PDF."""

    if Path(file_name).suffix.lower() != ".pdf":
        raise ValueError("Please upload a PDF resume.")


def extract_text_from_pdf(pdf_file: Union[str, Path, BinaryIO], file_name: Optional[str] = None) -> ResumeTextResult:
    """Extract raw and cleaned text from a PDF resume."""

    try:
        import pdfplumber
    except ImportError as exc:
        raise ImportError(
            "pdfplumber is required for PDF extraction. Install it with: pip install pdfplumber"
        ) from exc

    display_name = file_name or getattr(pdf_file, "name", "uploaded_resume.pdf")
    validate_pdf_file_name(display_name)

    raw_pages: list[str] = []
    embedded_image_count = 0
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            raw_pages.append(page.extract_text() or "")
            embedded_image_count += len(getattr(page, "images", []) or [])
        page_count = len(pdf.pages)

    raw_text = "\n\n".join(raw_pages)
    cleaned_text = clean_resume_text(raw_text)

    return ResumeTextResult(
        file_name=Path(display_name).name,
        raw_text=raw_text,
        cleaned_text=cleaned_text,
        page_count=page_count,
        word_count=count_words(cleaned_text),
        embedded_image_count=embedded_image_count,
    )
