"""Content slide — variants:

  bullets   classic single-column bullets
  columns   bullets split across two columns
  numbered  numbered rows with accent numerals
"""

from __future__ import annotations

from pptx.enum.text import MSO_ANCHOR, PP_ALIGN

from ...spec.schema import Bullet, ContentSlide
from ..geometry import Box
from ..geometry import columns as grid_columns
from ..geometry import rows as grid_rows
from ..registry import renderer
from ..shapes import add_rect
from ..text import add_bullets, add_text
from ._common import add_title_band


@renderer("content")
def render(slide, model: ContentSlide, ctx) -> None:
    tokens = ctx.tokens
    variant = ctx.variant(model)
    area = add_title_band(slide, tokens, model.title, kicker=model.kicker)
    items: list = []
    for b in model.bullets:
        if isinstance(b, Bullet):
            items.append((b.text, b.sub) if b.sub else b.text)
        else:
            items.append(b)

    if variant == "columns" and len(items) >= 4:
        half = (len(items) + 1) // 2
        left, right = grid_columns(area, 2, 0.6)
        add_bullets(slide, left, items[:half], tokens)
        add_bullets(slide, right, items[half:], tokens)
        return

    if variant == "numbered":
        flat = [(i[0] if isinstance(i, tuple) else i) for i in items]
        for n, (text, row) in enumerate(
                zip(flat, grid_rows(area, max(len(flat), 3), 0.12), strict=False),
                start=1):
            sq = 0.55
            sq_top = row.top_in + (row.height_in - sq) / 2
            add_rect(slide, Box(row.left_in, sq_top, sq, sq), tokens,
                     fill="accent_tint", rounded=True, corner=0.25)
            add_text(slide, Box(row.left_in, sq_top + 0.02, sq, sq - 0.04),
                     str(n), tokens, scale="stat_label", role="heading",
                     color="accent", bold=True, align=PP_ALIGN.CENTER,
                     anchor=MSO_ANCHOR.MIDDLE)
            add_text(slide, Box(row.left_in + sq + 0.35, row.top_in,
                                row.width_in - sq - 0.35, row.height_in),
                     text, tokens, scale="body", color="neutral_dark",
                     anchor=MSO_ANCHOR.MIDDLE, shrink_to_fit=True)
        return

    add_bullets(slide, area, items, tokens)
