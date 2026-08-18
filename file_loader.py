"""
docchat/file_loader.py - turn an uploaded file into plain text.

One job: given a filename and its raw bytes, return the text inside. The rest of
the app never has to know whether the upload was a PDF, a DOCX or a TXT - it just
calls load_text() and gets a string. (This is exactly the "hide messy details
behind one clean function" idea from lesson 03.)

Concepts reused from lessons 01 and 02:
    .txt  -> decode the bytes         (lesson 01)
    .pdf  -> pypdf                     (lesson 02)
    .docx -> python-docx              (lesson 02)
"""

# BytesIO wraps raw bytes so libraries that expect a "file" can read from memory
# instead of from disk. An upload lives in memory, so this is exactly what we need.
from io import BytesIO

from docx import Document       # python-docx: read .docx
from pypdf import PdfReader     # pypdf: read .pdf


def _read_txt(data: bytes) -> str:
    # Try UTF-8 first; fall back to latin-1 so odd encodings don't crash the app.
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1", errors="ignore")


def _read_pdf(data: bytes) -> str:
    # PdfReader can read straight from a BytesIO - no temp file needed.
    reader = PdfReader(BytesIO(data))
    # extract_text() may return None on an image-only (scanned) page; use "".
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def _read_docx(data: bytes) -> str:
    doc = Document(BytesIO(data))
    return "\n".join(paragraph.text for paragraph in doc.paragraphs)


def load_text(filename: str, data: bytes) -> str:
    """Dispatch on the file extension and return the extracted text.

    Raises ValueError for unsupported types so the UI can show a clear message.
    """
    # Lower-case the name so ".PDF" and ".pdf" both match.
    name = filename.lower()

    if name.endswith(".txt"):
        text = _read_txt(data)
    elif name.endswith(".pdf"):
        text = _read_pdf(data)
    elif name.endswith(".docx"):
        text = _read_docx(data)
    else:
        raise ValueError(f"Unsupported file type: {filename}")

    # A scanned PDF (or empty file) yields no text - tell the caller clearly.
    if not text.strip():
        raise ValueError(
            f"No readable text found in {filename}. "
            "If it's a scanned PDF, it has no selectable text to extract."
        )
    return text


# Quick self-test with a plain-text payload (no external files needed).
if __name__ == "__main__":
    demo = load_text("demo.txt", b"Chroma stores vectors. RAG retrieves them.")
    print("load_text() returned:", repr(demo))