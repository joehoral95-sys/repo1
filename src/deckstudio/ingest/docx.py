"""DOCX -> markdown digest preserving heading structure, lists, and tables."""

from __future__ import annotations

from pathlib import Path

import docx

from .digest import Digest, table_to_markdown


def digest_docx(path: Path) -> Digest:
    digest = Digest(source_name=path.name, kind="docx")
    document = docx.Document(str(path))

    lines: list[str] = []
    for block in _iter_blocks(document):
        if isinstance(block, docx.table.Table):
            rows = [[cell.text.strip() for cell in row.cells] for row in block.rows]
            lines.append("")
            lines.append(table_to_markdown(rows))
            lines.append("")
            continue
        para = block
        text = para.text.strip()
        if not text:
            continue
        style = (para.style.name or "").lower()
        if style.startswith("heading"):
            level = _heading_level(style)
            lines.append(f"\n{'#' * (level + 1)} {text}\n")
        elif "list" in style:
            lines.append(f"- {text}")
        else:
            lines.append(text)
    digest.add("\n".join(lines))
    return digest


def _heading_level(style_name: str) -> int:
    for token in style_name.split():
        if token.isdigit():
            return min(int(token), 5)
    return 1


def _iter_blocks(document):
    """Yield paragraphs and tables in document order."""
    from docx.oxml.ns import qn
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    body = document.element.body
    for child in body.iterchildren():
        if child.tag == qn("w:p"):
            yield Paragraph(child, document)
        elif child.tag == qn("w:tbl"):
            yield Table(child, document)
