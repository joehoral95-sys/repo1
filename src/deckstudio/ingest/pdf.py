"""PDF -> markdown digest via pypdf. Flags low-text pages (likely scans)."""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from .digest import Digest


def digest_pdf(path: Path) -> Digest:
    digest = Digest(source_name=path.name, kind="pdf")
    reader = PdfReader(str(path))
    thin_pages = []
    for i, page in enumerate(reader.pages, start=1):
        try:
            text = (page.extract_text() or "").strip()
        except Exception as e:
            digest.warn(f"page {i}: extraction failed ({e})")
            continue
        if len(text) < 40:
            thin_pages.append(i)
            continue
        digest.add(f"## Page {i}\n\n{text}\n")
    if thin_pages:
        digest.warn(
            f"pages {thin_pages} had little or no extractable text - they may be "
            "scans or images. Ask Joe for the source Word/Excel file if numbers "
            "are missing.")
    if not digest.sections:
        digest.warn("no text could be extracted from this PDF at all.")
    return digest
