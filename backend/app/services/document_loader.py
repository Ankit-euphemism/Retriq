import pdfplumber
import io
import zipfile
from docx import Document

# Document loader service for extracting text from various document formats.
def load_document_from_url(url: str) -> str:
    import requests
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    raw = response.content

    # Prefer URL/content-type hints, then fall back to byte sniffing.
    url_lower = url.lower()
    content_type = response.headers.get("content-type", "").lower()

    if url_lower.endswith(".docx") or "application/vnd.openxmlformats-officedocument.wordprocessingml.document" in content_type:
        return _parse_docx_bytes(raw)
    if url_lower.endswith(".pdf") or "application/pdf" in content_type:
        return _parse_pdf_bytes(raw)

    return _parse_by_bytes(raw)

# load document from bytes (for file upload)
def load_document_from_bytes(file_bytes: bytes) -> str:  # NEW
    return _parse_by_bytes(file_bytes)

# Parse document from bytes (for file upload)
def _parse_by_bytes(raw: bytes) -> str:
    if _looks_like_pdf(raw):
        return _parse_pdf_bytes(raw)
    if _looks_like_docx(raw):
        return _parse_docx_bytes(raw)
    raise ValueError("Unsupported document format. Please upload a PDF or DOCX file.")

# check if the raw bytes look like a PDF or DOCX file
def _looks_like_pdf(raw: bytes) -> bool:
    return raw.startswith(b"%PDF")

# check if the raw bytes look like a DOCX file
def _looks_like_docx(raw: bytes) -> bool:
    # DOCX is a ZIP package containing word/document.xml
    if not raw.startswith(b"PK"):
        return False

    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            return "word/document.xml" in zf.namelist()
    except zipfile.BadZipFile:
        return False

# Parse PDF bytes into text
def _parse_pdf_bytes(raw: bytes) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

# Parse DOCX bytes into text
def _parse_docx_bytes(raw: bytes) -> str:
    document = Document(io.BytesIO(raw))
    lines = [paragraph.text for paragraph in document.paragraphs if paragraph.text and paragraph.text.strip()]
    return "\n".join(lines)