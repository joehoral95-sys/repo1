"""Optional visual previews via LibreOffice headless. Never required.

If soffice is on PATH, `deckstudio build --preview` (and the agent's
self-review step) can turn the deck into PNG thumbnails for a visual check.
Absence of LibreOffice degrades to a one-line note.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def soffice_available() -> bool:
    return shutil.which("soffice") is not None


def render_previews(pptx_path: Path, out_dir: Path | None = None) -> list[Path] | None:
    """Convert the deck to PNGs (one per slide via PDF). Returns image paths,
    or None if LibreOffice isn't installed."""
    if not soffice_available():
        return None
    out_dir = out_dir or pptx_path.with_name(f"{pptx_path.stem}_preview")
    out_dir.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        ["soffice", "--headless", "--convert-to", "pdf",
         "--outdir", str(out_dir), str(pptx_path)],
        check=True, capture_output=True, timeout=180)
    pdf_path = out_dir / f"{pptx_path.stem}.pdf"
    if not pdf_path.exists():
        return []

    if shutil.which("pdftoppm"):
        subprocess.run(
            ["pdftoppm", "-png", "-r", "80", str(pdf_path), str(out_dir / "slide")],
            check=True, capture_output=True, timeout=180)
        return sorted(out_dir.glob("slide*.png")) or [pdf_path]
    return [pdf_path]
