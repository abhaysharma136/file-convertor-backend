from docx import Document
from pathlib import Path
import re
from pypdf import PdfReader




SECTION_HEADERS = {
    "summary": ["summary", "professional summary"],
    "skills": ["skills", "technical skills"],
    "experience": ["experience", "work experience", "full-time jobs", "employment"],
    "projects": ["projects", "project works"],
    "education": ["education", "academic details"],
    "certifications": ["certifications", "certification"],
    "achievements": ["achievements", "awards"]
}
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


def normalize_line(text: str) -> str:
    text = text.lower()

    # Remove junk characters
    text = re.sub(r"[^\x00-\x7F]+", " ", text)  # non-ascii
    text = text.replace("•", " ")
    text = text.replace("|", " ")

    return text.strip()


def normalize_text(text: str) -> str:
    text = text.lower()

    # Remove junk characters
    text = re.sub(r"[^\x00-\x7F]+", " ", text)  # non-ascii
    text = text.replace("•", " ")
    text = text.replace("|", " ")

    return text.strip()
def extract_resume_text(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported resume format")
    
def split_into_sections(raw_text: str) -> dict:
    sections = {}
    current_section = "other"
    sections[current_section] = []

    lines = raw_text.split("\n")

    for line in lines:
        clean_line = normalize_line(line)
        if not clean_line:
            continue

        matched_section = None

        for section, keywords in SECTION_HEADERS.items():
            for keyword in keywords:
                if clean_line.startswith(keyword):
                    matched_section = section
                    break
            if matched_section:
                break

        if matched_section:
            current_section = matched_section
            sections[current_section] = []
        else:
            sections.setdefault(current_section, []).append(clean_line)

    for key in sections:
        sections[key] = " ".join(sections[key])

    return sections

def normalize_jd_text(jd_text: str) -> str:
    return normalize_text(jd_text)

