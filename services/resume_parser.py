from docx import Document
from pathlib import Path
import re
from pypdf import PdfReader


# ---------------------------------------------------------
# SECTION HEADERS
# ---------------------------------------------------------

SECTION_HEADERS = {
    "summary": [
        "summary",
        "professional summary",
        "profile",
        "professional profile",
        "objective",
        "career objective",
    ],

    "skills": [
        "skills",
        "technical skills",
        "core skills",
        "key skills",
        "technical expertise",
        "technologies",
        "technology stack",
        "tech stack",
    ],

    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment",
        "employment history",
        "work history",
        "full-time jobs",
    ],

    "projects": [
        "projects",
        "project works",
        "personal projects",
        "academic projects",
        "key projects",
    ],

    "education": [
        "education",
        "academic details",
        "academic background",
        "educational background",
        "qualifications",
    ],

    "certifications": [
        "certifications",
        "certification",
        "licenses",
        "licenses & certifications",
    ],

    "achievements": [
        "achievements",
        "awards",
        "honors",
        "accomplishments",
    ],
}


# ---------------------------------------------------------
# DOCUMENT EXTRACTION
# ---------------------------------------------------------

def extract_text_from_docx(file_path: str) -> str:
    doc = Document(file_path)

    paragraphs = []

    for para in doc.paragraphs:
        text = para.text.strip()

        if text:
            paragraphs.append(text)

    return "\n".join(paragraphs)


def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)

    pages_text = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages_text.append(text)

    return "\n".join(pages_text)


def extract_resume_text(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)

    if ext == ".docx":
        return extract_text_from_docx(file_path)

    raise ValueError("Unsupported resume format")


# ---------------------------------------------------------
# NORMALIZATION
# ---------------------------------------------------------

def normalize_line(text: str) -> str:
    """
    Normalize a single resume line while preserving useful
    technical characters such as +, #, ., / and -.
    """

    if not text:
        return ""

    text = text.replace("\u00a0", " ")

    # Common bullet characters
    text = re.sub(
        r"^[\s]*[•●▪◦‣⁃]\s*",
        "",
        text
    )

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip().lower()


def normalize_text(text: str) -> str:
    """
    Normalize the complete resume text.

    We intentionally do NOT remove all non-ASCII characters.
    Technical resume terms such as C++, C#, etc. need to survive.
    """

    if not text:
        return ""

    text = text.replace("\u00a0", " ")

    # Normalize common bullets into spaces
    text = re.sub(
        r"[•●▪◦‣⁃]",
        " ",
        text
    )

    # Normalize tabs/newlines
    text = re.sub(r"\s+", " ", text)

    return text.strip().lower()


# ---------------------------------------------------------
# SECTION HEADER DETECTION
# ---------------------------------------------------------

def _clean_header_candidate(line: str) -> str:
    """
    Prepare a line for section-header comparison.
    """

    text = line.strip().lower()

    # Remove common trailing separators
    text = re.sub(r"[:\-–—]+$", "", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def _match_section_header(line: str):
    """
    Detect a resume section header even when PDF extraction
    places the first piece of section content on the same line.

    Examples:

        Experience
        Experience: Full Stack Developer
        Experience  Full Stack Developer

    All should identify "experience".
    """

    candidate = _clean_header_candidate(line)

    if not candidate:
        return None, ""

    for section, keywords in SECTION_HEADERS.items():

        for keyword in keywords:

            keyword = keyword.lower().strip()

            # Exact header
            if candidate == keyword:
                return section, ""

            # Header followed by separator
            pattern = rf"^{re.escape(keyword)}\s*[:\-–—]\s*(.+)$"

            match = re.match(
                pattern,
                candidate,
                flags=re.IGNORECASE
            )

            if match:
                return section, match.group(1).strip()

            # Header followed by multiple spaces.
            #
            # This is particularly useful for PDF extraction:
            #
            # Experience  Full Stack Developer - Company
            #
            pattern = rf"^{re.escape(keyword)}\s{{2,}}(.+)$"

            match = re.match(
                pattern,
                line.strip(),
                flags=re.IGNORECASE
            )

            if match:
                return section, match.group(1).strip().lower()

    return None, ""

# ---------------------------------------------------------
# BULLET DETECTION
# ---------------------------------------------------------

BULLET_PATTERN = re.compile(
    r"^\s*(?:[•●▪◦‣⁃]|[-*+])\s+"
)


def is_bullet_line(line: str) -> bool:
    """
    Detect common resume bullet formats.
    """

    if not line:
        return False

    return bool(BULLET_PATTERN.match(line))


def clean_bullet(line: str) -> str:
    """
    Remove the bullet marker but preserve the bullet content.
    """

    return BULLET_PATTERN.sub("", line).strip()


# ---------------------------------------------------------
# SECTION SPLITTING
# ---------------------------------------------------------

def split_into_sections(raw_text: str) -> dict:
    """
    Split resume into logical sections.

    Handles PDF extraction where a section heading and the
    first piece of content may appear on the same line.
    """

    sections = {
        "other": []
    }

    current_section = "other"

    lines = raw_text.splitlines()

    for line in lines:

        if not line.strip():
            continue

        matched_section, remainder = _match_section_header(line)

        if matched_section:

            current_section = matched_section

            sections.setdefault(
                current_section,
                []
            )

            # If PDF extraction placed content on the same
            # line as the section heading, preserve it.
            if remainder:
                clean_remainder = normalize_line(
                    remainder
                )

                if clean_remainder:
                    sections[current_section].append(
                        clean_remainder
                    )

            continue

        clean_line = normalize_line(line)

        if not clean_line:
            continue

        sections.setdefault(
            current_section,
            []
        ).append(clean_line)

    return {
        key: " ".join(value).strip()
        for key, value in sections.items()
    }

# ---------------------------------------------------------
# RESUME METADATA
# ---------------------------------------------------------

def extract_resume_metadata(raw_text: str) -> dict:
    """
    Extract simple deterministic metadata from the resume.

    This is intentionally rule-based.
    """

    normalized = normalize_text(raw_text)

    email_matches = re.findall(
        r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
        raw_text,
        flags=re.IGNORECASE
    )

    phone_matches = re.findall(
        r"(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)",
        raw_text
    )

    linkedin_present = bool(
        re.search(r"linkedin\.com", normalized)
    )

    github_present = bool(
        re.search(r"github\.com", normalized)
    )

    website_present = bool(
        re.search(
            r"(https?://|www\.)",
            normalized
        )
    )

    return {
        "email_present": len(email_matches) > 0,
        "phone_present": len(phone_matches) > 0,
        "linkedin_present": linkedin_present,
        "github_present": github_present,
        "website_present": website_present,
    }


# ---------------------------------------------------------
# BULLET EXTRACTION
# ---------------------------------------------------------

def extract_bullets(raw_text: str) -> list[str]:
    """
    Extract bullet-style lines from the original resume.
    """

    bullets = []

    for line in raw_text.splitlines():

        if is_bullet_line(line):
            bullet = clean_bullet(line)

            if bullet:
                bullets.append(bullet)

    return bullets


# ---------------------------------------------------------
# JD NORMALIZATION
# ---------------------------------------------------------

def normalize_jd_text(jd_text: str) -> str:
    return normalize_text(jd_text)


# ---------------------------------------------------------
# JD SECTION HEADERS
# ---------------------------------------------------------

JD_SECTION_HEADERS = {
    "responsibilities": [
        "responsibilities",
        "what you will do",
        "the role",
        "primary responsibilities",
        "role responsibilities",
    ],

    "requirements": [
        "requirements",
        "qualifications",
        "what you need",
        "required qualifications",
        "skills",
        "required skills",
    ],

    "education_req": [
        "education",
        "academic",
        "ug:",
        "pg:",
    ],

    "boilerplate": [
        "comply with",
        "equal opportunity",
        "about us",
        "employment contract",
    ],
}


def split_jd_into_sections(jd_text: str) -> dict:
    sections = {
        "other": []
    }

    current_section = "other"

    lines = jd_text.splitlines()

    for line in lines:

        clean_line = normalize_line(line)

        if not clean_line:
            continue

        matched_section = None

        for section, keywords in JD_SECTION_HEADERS.items():

            for keyword in keywords:

                if clean_line == keyword.lower():
                    matched_section = section
                    break

            if matched_section:
                break

        if matched_section:
            current_section = matched_section
            sections.setdefault(current_section, [])
        else:
            sections.setdefault(
                current_section,
                []
            ).append(clean_line)

    return {
        key: " ".join(value).strip()
        for key, value in sections.items()
    }