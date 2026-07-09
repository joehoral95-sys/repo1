"""Agenda — variants:

  band  navy band left with swash title, numbered items right
  list  white: blue title left, numbered rows full width
  grid  white: items as tinted number cards in a grid

Agenda owns its full canvas (no standard footer); each variant draws the
page number itself.
"""

from __future__ import annotations

from pptx.enum.text import MSO_ANCHOR, PP_ALIGN

from ...spec.schema import AgendaSlide
from ..geometry import SLIDE_H_IN, SLIDE_W_IN, Box, columns, inset, rows
from ..registry import renderer
from ..shapes import add_accent_bar, add_brand_art, add_logo, add_rect
from ..text import add_text

BAND_W = 4.3


@renderer("agenda")
def render(slide, model: AgendaSlide, ctx) -> None:
    variant = ctx.variant(model)
    if variant == "list":
        _list(slide, model, ctx)
    elif variant == "grid":
        _grid(slide, model, ctx)
    else:
        _band(slide, model, ctx)
    _page_number(slide, ctx)


def _band(slide, model: AgendaSlide, ctx) -> None:
    tokens = ctx.tokens
    m = tokens.margin_in
    add_rect(slide, Box(0, 0, BAND_W, SLIDE_H_IN), tokens, fill="primary",
             rounded=False)
    add_text(slide, Box(m, 2.55, BAND_W - m - 0.3, 1.1), model.title or "Agenda",
             tokens, scale="section_title", role="heading", color="white",
             bold=True, shrink_to_fit=True)
    if add_brand_art(slide, tokens, "swash_sky", Box(m, 3.6, 2.4, 0.33)) is None:
        add_accent_bar(slide, m, 3.65, 0.9, tokens, color="accent_warm", height_in=0.06)
    add_logo(slide, tokens, dark_bg=True, center_at_in=BAND_W / 2,
             bottom_in=7.0, height_in=0.4)

    items_area = Box(BAND_W + 0.55, 0.9, SLIDE_W_IN - BAND_W - 0.55 - m,
                     SLIDE_H_IN - 1.8)
    for i, (item, row) in enumerate(
            zip(model.items, rows(items_area, max(len(model.items), 3), 0.12),
                strict=False), start=1):
        _numbered_row(slide, tokens, i, item, row)


def _list(slide, model: AgendaSlide, ctx) -> None:
    tokens = ctx.tokens
    m = tokens.margin_in
    add_text(slide, Box(m, tokens.title_top_in, 6.0, 0.85),
             model.title or "Agenda", tokens, scale="slide_title",
             role="heading", color="accent", bold=True)
    add_accent_bar(slide, m, tokens.title_top_in + 0.92, 0.9, tokens)
    items_area = Box(m, 1.85, SLIDE_W_IN - 2 * m, SLIDE_H_IN - 2.6)
    for i, (item, row) in enumerate(
            zip(model.items, rows(items_area, max(len(model.items), 3), 0.1),
                strict=False), start=1):
        _numbered_row(slide, tokens, i, item, row)
    add_logo(slide, tokens, left_in=m, bottom_in=7.18, height_in=0.32)


def _grid(slide, model: AgendaSlide, ctx) -> None:
    tokens = ctx.tokens
    m = tokens.margin_in
    add_text(slide, Box(m, tokens.title_top_in, SLIDE_W_IN - 2 * m, 0.85),
             model.title or "Agenda", tokens, scale="slide_title",
             role="heading", color="accent", bold=True, align=PP_ALIGN.CENTER)
    add_accent_bar(slide, (SLIDE_W_IN - 0.9) / 2, tokens.title_top_in + 0.92,
                   0.9, tokens)
    area = Box(m + 0.4, 2.0, SLIDE_W_IN - 2 * m - 0.8, 4.4)
    n = len(model.items)
    ncols = 2 if n <= 4 else 3
    nrows = (n + ncols - 1) // ncols
    grid_rows = rows(area, nrows, 0.3)
    idx = 0
    for r in range(nrows):
        for col in columns(grid_rows[r], ncols, 0.3):
            if idx >= n:
                break
            card = col
            add_rect(slide, card, tokens, fill="neutral_light", rounded=True,
                     corner=0.08, outline="border")
            pad = inset(card, x_in=0.3, y_in=0.2)
            add_text(slide, Box(pad.left_in, pad.top_in, 1.0, 0.5), f"{idx + 1:02d}",
                     tokens, scale="slide_title", role="heading", color="accent",
                     bold=True)
            add_text(slide, Box(pad.left_in, pad.top_in + 0.55, pad.width_in,
                                pad.height_in - 0.55),
                     model.items[idx], tokens, scale="stat_label",
                     color="neutral_dark", shrink_to_fit=True)
            idx += 1
    add_logo(slide, tokens, left_in=m, bottom_in=7.18, height_in=0.32)


def _numbered_row(slide, tokens, i: int, item: str, row: Box) -> None:
    sq = 0.62
    sq_top = row.top_in + (row.height_in - sq) / 2
    add_rect(slide, Box(row.left_in, sq_top, sq, sq), tokens,
             fill="accent_tint", rounded=True, corner=0.25)
    add_text(slide, Box(row.left_in, sq_top + 0.02, sq, sq - 0.04), f"{i:02d}",
             tokens, scale="subtitle", role="heading", color="accent",
             bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    add_text(slide, Box(row.left_in + sq + 0.4, row.top_in,
                        row.width_in - sq - 0.4, row.height_in), item, tokens,
             scale="subtitle", color="neutral_dark", anchor=MSO_ANCHOR.MIDDLE,
             shrink_to_fit=True)


def _page_number(slide, ctx) -> None:
    tokens = ctx.tokens
    if tokens.show_page_numbers:
        add_text(slide, Box(SLIDE_W_IN - tokens.margin_in - 0.5, SLIDE_H_IN - 0.42,
                            0.5, 0.3),
                 str(ctx.slide_index + 1), tokens, scale="footer", color="accent",
                 align=PP_ALIGN.RIGHT)
