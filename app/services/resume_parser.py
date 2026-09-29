from io import BytesIO
from zipfile import BadZipFile

from docx import Document
from pypdf import PdfReader
from pypdf.errors import PdfReadError


MAX_RESUME_SIZE_BYTES = 10 * 1024 * 1024
SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


def extract_resume_text(content: bytes, filename: str) -> str:
    extension = filename.rsplit(".", maxsplit=1)[-1].lower() if "." in filename else ""
    extension = f".{extension}"
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError("Only PDF and DOCX resumes are supported.")
    if not content:
        raise ValueError("The uploaded file is empty.")
    if len(content) > MAX_RESUME_SIZE_BYTES:
        raise ValueError("Resume file exceeds the 10 MB limit.")

    try:
        if extension == ".pdf":
            if b"%PDF-" not in content[:1024]:
                raise ValueError("The uploaded file is not a valid PDF.")
            reader = PdfReader(BytesIO(content))
            if reader.is_encrypted:
                raise ValueError("Password-protected PDFs are not supported.")
            text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
        else:
            if not content.startswith(b"PK"):
                raise ValueError("The uploaded file is not a valid DOCX document.")
            document = Document(BytesIO(content))
            text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    except (PdfReadError, BadZipFile, KeyError) as error:
        raise ValueError("The uploaded document is corrupted or unreadable.") from error

    cleaned_text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    if not cleaned_text:
        raise ValueError("No readable text was found in the resume.")
    return cleaned_text
