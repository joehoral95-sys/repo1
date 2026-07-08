"""Template handling: open brand/template.pptx (or a clean 16:9 base) and
resolve slide layouts BY NAME so template edits can't silently break builds.

v1 renderers draw brand elements themselves from tokens, so they only need a
blank layout. When brand intake replaces template.pptx with SOA's official
masters, renderers can opt into named layouts (e.g. "Title Slide") and the
lookup below fails loudly if a named layout disappears.
"""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation

from .geometry import SLIDE_H, SLIDE_W


class TemplateError(Exception):
    pass


BLANK_CANDIDATES = ("Blank", "blank")


def open_template(template_path: Path | None):
    """Return a Presentation sized 16:9, from the brand template if present."""
    if template_path and template_path.exists():
        prs = Presentation(str(template_path))
    else:
        prs = Presentation()  # python-pptx built-in default
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    return prs


def layout_by_name(prs, name: str):
    """Find a layout by exact name across all masters; loud failure lists options."""
    available = []
    for master in prs.slide_masters:
        for layout in master.slide_layouts:
            if layout.name == name:
                return layout
            available.append(layout.name)
    raise TemplateError(
        f"Slide layout '{name}' not found in template. Available layouts: {available}. "
        "Someone may have renamed or deleted it in brand/template.pptx.")


def blank_layout(prs):
    """The layout renderers draw on. Prefer one literally named Blank, else the
    layout with the fewest placeholders."""
    for name in BLANK_CANDIDATES:
        try:
            return layout_by_name(prs, name)
        except TemplateError:
            pass
    best = None
    best_count = 10 ** 9
    for master in prs.slide_masters:
        for layout in master.slide_layouts:
            n = len(layout.placeholders)
            if n < best_count:
                best, best_count = layout, n
    if best is None:
        raise TemplateError("Template has no slide layouts at all.")
    return best


def add_blank_slide(prs):
    """Add a slide on the blank layout and remove any inherited placeholders."""
    slide = prs.slides.add_slide(blank_layout(prs))
    for ph in list(slide.placeholders):
        ph._element.getparent().remove(ph._element)
    return slide
