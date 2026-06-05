"""Rule-based resume profile parser for CareerIQ Version 1."""

from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Optional


DEFAULT_SKILLS = [
    "A/B Testing",
    "Active Directory",
    "Agile",
    "API Development",
    "Attention to Detail",
    "ATS",
    "Benefits Administration",
    "Budgeting",
    "C#",
    "Change Management",
    "Communication",
    "Conflict Resolution",
    "CRM",
    "CSS",
    "Customer Service",
    "DAX",
    "Data Cleaning",
    "Data Modeling",
    "Data Quality",
    "Data Visualization",
    "Django",
    "Documentation",
    "Employee Relations",
    "Excel",
    "FastAPI",
    "Flask",
    "Git",
    "Google Analytics",
    "Hardware Support",
    "HTML",
    "Interviewing",
    "Java",
    "JavaScript",
    "Jira",
    "KPI Reporting",
    "Knowledge Base",
    "Leadership",
    "Market Research",
    "Microsoft 365",
    "Networking",
    "Node.js",
    "Onboarding",
    "Power BI",
    "Payroll",
    "Performance Management",
    "Process Mapping",
    "Product Analytics",
    "Project Management",
    "Python",
    "React",
    "Recruiting",
    "Requirements Gathering",
    "Risk Management",
    "Scrum",
    "SEO",
    "Stakeholder Communication",
    "SQL",
    "Stakeholder Management",
    "Statistics",
    "Talent Acquisition",
    "Tableau",
    "Test Automation",
    "Ticketing Systems",
    "Troubleshooting",
    "TypeScript",
    "User Stories",
    "Vendor Management",
    "Windows",
]

SECTION_HEADERS = {
    "summary",
    "profile",
    "skills",
    "technical skills",
    "core skills",
    "education",
    "certifications",
    "certification",
    "work experience",
    "experience",
    "professional experience",
    "employment history",
    "projects",
    "project experience",
}

EDUCATION_KEYWORDS = [
    "bachelor",
    "master",
    "diploma",
    "degree",
    "college",
    "university",
    "institute",
    "bootcamp",
    "b.sc",
    "bsc",
    "ba",
    "certificate in",
]

CERTIFICATION_KEYWORDS = [
    "certified",
    "certification",
    "certificate",
    "comptia",
    "google data analytics",
    "microsoft certified",
    "azure fundamentals",
    "aws cloud practitioner",
    "power bi data analyst",
    "tableau desktop specialist",
    "itil",
    "ccna",
]

EXPERIENCE_HEADERS = ["work experience", "professional experience", "employment history", "experience"]
PROJECT_HEADERS = ["projects", "project experience"]
EDUCATION_HEADERS = ["education"]
CERTIFICATION_HEADERS = ["certifications", "certification"]


@dataclass(frozen=True)
class ParsedSkill:
    """A skill detected in resume text."""

    name: str
    confidence_score: float = 1.0
    extraction_method: str = "rule_based"


@dataclass(frozen=True)
class CandidateProfile:
    """Structured resume profile used by later CareerIQ analysis modules."""

    candidate_name: Optional[str] = None
    skills: list[ParsedSkill] = field(default_factory=list)
    education: list[str] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    experience: list[str] = field(default_factory=list)
    projects: list[str] = field(default_factory=list)


def normalize_lines(text: Optional[str]) -> list[str]:
    """Return non-empty resume lines with repeated spacing removed."""

    if not text:
        return []

    lines = []
    for line in text.splitlines():
        normalized = re.sub(r"\s+", " ", line).strip(" -|")
        if normalized:
            lines.append(normalized)
    return lines


def is_section_header(line: str) -> bool:
    """Return True when a line looks like a resume section header."""

    cleaned = re.sub(r"[^a-zA-Z ]", "", line).strip().lower()
    return cleaned in SECTION_HEADERS


def unique_preserve_order(values: list[str]) -> list[str]:
    """Remove duplicates without changing display order."""

    results = []
    seen = set()
    for value in values:
        key = value.lower()
        if key not in seen:
            results.append(value)
            seen.add(key)
    return results


def extract_candidate_name(lines: list[str]) -> Optional[str]:
    """Extract a likely candidate name from the top of the resume."""

    blocked_terms = {
        "resume",
        "curriculum vitae",
        "cv",
        "summary",
        "profile",
        "skills",
        "education",
        "experience",
    }
    role_terms = {
        "analyst",
        "developer",
        "engineer",
        "manager",
        "coordinator",
        "specialist",
        "technician",
        "support",
        "recruiter",
        "representative",
    }

    for line in lines[:8]:
        lower_line = line.lower()
        if lower_line in blocked_terms:
            continue
        if any(term in lower_line for term in role_terms):
            continue
        if "@" in line or re.search(r"\d{3}", line):
            continue
        words = re.findall(r"[A-Za-z][A-Za-z'.-]*", line)
        if 2 <= len(words) <= 4 and len(line) <= 60:
            return " ".join(word[:1].upper() + word[1:] for word in words)
    return None


def extract_skills(text: Optional[str], known_skills: Optional[list[str]] = None) -> list[ParsedSkill]:
    """Find known skills in resume text using phrase-aware matching."""

    if not text:
        return []

    skill_names = known_skills or DEFAULT_SKILLS
    detected = []
    seen = set()

    for skill in sorted(skill_names, key=len, reverse=True):
        escaped = re.escape(skill)
        pattern = rf"(?<![A-Za-z0-9+#]){escaped}(?![A-Za-z0-9+#])"
        if re.search(pattern, text, flags=re.IGNORECASE):
            key = skill.lower()
            if key not in seen:
                detected.append(ParsedSkill(name=skill))
                seen.add(key)

    return sorted(detected, key=lambda item: item.name.lower())


def extract_section_lines(lines: list[str], header_names: list[str], max_lines: int = 12) -> list[str]:
    """Extract lines after a section header until the next known header."""

    header_set = {header.lower() for header in header_names}
    collecting = False
    section_lines = []

    for line in lines:
        cleaned = re.sub(r"[^a-zA-Z ]", "", line).strip().lower()
        if cleaned in header_set:
            collecting = True
            continue
        if collecting and is_section_header(line):
            break
        if collecting:
            section_lines.append(line)
        if len(section_lines) >= max_lines:
            break

    return unique_preserve_order(section_lines)


def extract_keyword_lines(lines: list[str], keywords: list[str], max_lines: int = 8) -> list[str]:
    """Extract lines that contain any keyword from a keyword list."""

    matches = []
    for line in lines:
        lower_line = line.lower()
        if any(keyword in lower_line for keyword in keywords):
            matches.append(line)
    return unique_preserve_order(matches)[:max_lines]


def extract_education(lines: list[str]) -> list[str]:
    """Extract education lines from a resume."""

    section_lines = extract_section_lines(lines, EDUCATION_HEADERS, max_lines=8)
    keyword_lines = extract_keyword_lines(lines, EDUCATION_KEYWORDS, max_lines=8)
    return unique_preserve_order(section_lines + keyword_lines)[:8]


def extract_certifications(lines: list[str]) -> list[str]:
    """Extract certification lines from a resume."""

    section_lines = extract_section_lines(lines, CERTIFICATION_HEADERS, max_lines=8)
    keyword_lines = extract_keyword_lines(lines, CERTIFICATION_KEYWORDS, max_lines=8)
    return unique_preserve_order(section_lines + keyword_lines)[:8]


def extract_experience(lines: list[str]) -> list[str]:
    """Extract a compact work experience preview."""

    section_lines = extract_section_lines(lines, EXPERIENCE_HEADERS, max_lines=12)
    if section_lines:
        return section_lines

    date_pattern = re.compile(r"\b(20\d{2}|19\d{2}|present|current)\b", flags=re.IGNORECASE)
    return unique_preserve_order([line for line in lines if date_pattern.search(line)])[:8]


def extract_projects(lines: list[str]) -> list[str]:
    """Extract project lines from a resume."""

    section_lines = extract_section_lines(lines, PROJECT_HEADERS, max_lines=10)
    if section_lines:
        return section_lines

    project_lines = [line for line in lines if "project" in line.lower()]
    return unique_preserve_order(project_lines)[:8]


def parse_resume_profile(text: Optional[str], known_skills: Optional[list[str]] = None) -> CandidateProfile:
    """Parse cleaned resume text into a structured candidate profile."""

    lines = normalize_lines(text)
    return CandidateProfile(
        candidate_name=extract_candidate_name(lines),
        skills=extract_skills(text, known_skills=known_skills),
        education=extract_education(lines),
        certifications=extract_certifications(lines),
        experience=extract_experience(lines),
        projects=extract_projects(lines),
    )
