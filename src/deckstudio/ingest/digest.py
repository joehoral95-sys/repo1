"""Common digest format: every ingested source becomes a markdown file in
decks/<name>/sources/ that the agent reads instead of the binary.

Digests preserve provenance (file name, sheet/page) so every number the agent
puts in a spec can be traced to its source.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Digest:
    source_name: str
    kind: str                       # pdf | docx | xlsx | pptx
    sections: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add(self, text: str) -> None:
        self.sections.append(text)

    def warn(self, text: str) -> None:
        self.warnings.append(text)

    def to_markdown(self) -> str:
        parts = [f"# Digest: {self.source_name}", f"_Type: {self.kind}_", ""]
        if self.warnings:
            parts.append("> **Extraction warnings:**")
            for w in self.warnings:
                parts.append(f"> - {w}")
            parts.append("")
        parts.extend(self.sections)
        return "\n".join(parts) + "\n"

    def write(self, sources_dir: Path) -> Path:
        sources_dir.mkdir(parents=True, exist_ok=True)
        out = sources_dir / f"{Path(self.source_name).stem}.md"
        out.write_text(self.to_markdown(), encoding="utf-8")
        return out


def table_to_markdown(rows: list[list[str]], header: bool = True) -> str:
    if not rows:
        return ""
    widths = [max(len(str(r[i])) if i < len(r) else 0 for r in rows)
              for i in range(max(len(r) for r in rows))]

    def fmt(row: list[str]) -> str:
        cells = [str(c) if c is not None else "" for c in row]
        cells += [""] * (len(widths) - len(cells))
        return "| " + " | ".join(c.ljust(w) for c, w in zip(cells, widths, strict=True)) + " |"

    lines = [fmt(rows[0])]
    if header:
        lines.append("|" + "|".join("-" * (w + 2) for w in widths) + "|")
        body = rows[1:]
    else:
        body = rows[1:]
    lines.extend(fmt(r) for r in body)
    return "\n".join(lines)


def ingest_file(path: Path, sources_dir: Path) -> Path:
    """Dispatch on extension; returns the digest path."""
    from . import docx as docx_mod
    from . import pdf as pdf_mod
    from . import xlsx as xlsx_mod

    suffix = path.suffix.lower()
    if suffix == ".pdf":
        digest = pdf_mod.digest_pdf(path)
    elif suffix == ".docx":
        digest = docx_mod.digest_docx(path)
    elif suffix in (".xlsx", ".xlsm"):
        digest = xlsx_mod.digest_xlsx(path)
    elif suffix in (".md", ".txt"):
        digest = Digest(source_name=path.name, kind="text")
        digest.add(path.read_text(encoding="utf-8", errors="replace"))
    else:
        raise ValueError(
            f"Don't know how to ingest '{path.name}' ({suffix}). "
            "Supported: .pdf .docx .xlsx .xlsm .md .txt — and .pptx via `deckstudio extract`.")
    return digest.write(sources_dir)
