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
from ..text import adaptive_pt, add_bullets, add_text
from ._common import add_title_band


@renderer("content")
def render(slide, model: ContentSlide, ctx) -> None:
    tokens = ctx.tokens
    variant, chrome = ctx.variant_parts(model)
    area = add_title_band(slide, tokens, model.title, kicker=model.kicker,
                          style=chrome)
    items: list = []
    for b in model.bullets:
        if isinstance(b, Bullet):
            items.append((b.text, b.sub) if b.sub else b.text)
        else:
            items.append(b)
    top_texts = [(i[0] if isinstance(i, tuple) else i) for i in items]
    has_subs = any(isinstance(i, tuple) for i in items)
    # Few short bullets in a big canvas → bigger type (subs keep their scale,
    # so skip the bump when sub-bullets would end up disproportionately small).
    bullet_pt = None
    if not has_subs and len(items) <= 5:
        bullet_pt = adaptive_pt(int(tokens.pt("body").pt), top_texts,
                                [(35, 20), (65, 18)])

    if variant == "columns" and len(items) >= 4:
        half = (len(items) + 1) // 2
        left, right = grid_columns(area, 2, 0.6)
        add_bullets(slide, left, items[:half], tokens, size_pt=bullet_pt)
        add_bullets(slide, right, items[half:], tokens, size_pt=bullet_pt)
        return

    if variant == "numbered":
        flat = top_texts
        row_pt = adaptive_pt(int(tokens.pt("body").pt), flat,
                             [(28, 20), (55, 18)])
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
                     anchor=MSO_ANCHOR.MIDDLE, shrink_to_fit=True,
                     size_pt=row_pt)
        return

    if variant == "cards":
        flat = top_texts
        card_pt = adaptive_pt(int(tokens.pt("body").pt), flat, [(40, 18)])
        ncols = 2
        nrows = (len(flat) + ncols - 1) // ncols
        idx = 0
        for r in grid_rows(Box(area.left_in, area.top_in + 0.1, area.width_in,
                               area.height_in - 0.2), max(nrows, 2), 0.25):
            for col in grid_columns(r, ncols, 0.25):
                if idx >= len(flat):
                    break
                add_rect(slide, col, tokens, fill="neutral_light", rounded=True,
                         corner=0.08, outline="border")
                add_text(slide, Box(col.left_in + 0.3, col.top_in + 0.15,
                                    col.width_in - 0.6, col.height_in - 0.3),
                         flat[idx], tokens, scale="body", color="neutral_dark",
                         anchor=MSO_ANCHOR.MIDDLE, shrink_to_fit=True,
                         size_pt=card_pt)
                idx += 1
        return

    add_bullets(slide, area, items, tokens, size_pt=bullet_pt)
