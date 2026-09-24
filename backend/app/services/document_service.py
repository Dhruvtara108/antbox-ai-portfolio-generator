from io import BytesIO
from pathlib import Path

from docx import Document
from fastapi import UploadFile
from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


class DocumentExtractionError(ValueError):
    """Raised when an uploaded document cannot be extracted safely."""


async def extract_text(upload: UploadFile) -> str:
    filename = upload.filename or ""
    extension = Path(filename).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise DocumentExtractionError("Only PDF and DOCX files are supported.")

    contents = await upload.read()
    if not contents:
        raise DocumentExtractionError(f"{filename} is empty.")

    try:
        if extension == ".pdf":
            reader = PdfReader(BytesIO(contents))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        else:
            document = Document(BytesIO(contents))
            text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    except Exception as exc:
        raise DocumentExtractionError(f"Could not read {filename}.") from exc

    text = text.strip()
    if not text:
        raise DocumentExtractionError(f"No readable text was found in {filename}.")
    return text
