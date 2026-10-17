"""Stage 1 — extract text (+basic layout) from an uploaded file."""

import io

LAYOUT_KEYS = ("pages", "has_text", "blocks")


def extract_text(data: bytes, filename: str) -> tuple[str, dict]:
    name = filename.lower()
    if name.endswith(".pdf"):
        return _extract_pdf(data)
    if name.endswith(".docx"):
        return _extract_docx(data)
    return data.decode("utf-8", errors="ignore"), {"pages": 1, "has_text": True, "blocks": []}


def _extract_pdf(data: bytes) -> tuple[str, dict]:
    import fitz  # PyMuPDF

    doc = fitz.open(stream=data, filetype="pdf")
    parts: list[str] = []
    blocks: list[dict] = []
    for page in doc:
        parts.append(page.get_text("text"))
        for b in page.get_text("blocks"):
            blocks.append({"page": page.number, "bbox": list(b[:4]), "text": b[4]})
    text = "\n".join(parts)
    layout = {"pages": doc.page_count, "has_text": bool(text.strip()), "blocks": blocks}
    doc.close()
    return text, layout


def _extract_docx(data: bytes) -> tuple[str, dict]:
    import docx

    document = docx.Document(io.BytesIO(data))
    text = "\n".join(p.text for p in document.paragraphs)
    return text, {"pages": 1, "has_text": bool(text.strip()), "blocks": []}
