"""Agenda: asymmetric split — navy band on the left carrying the title with
SOA's swash, numbered items on the white right. Deliberately unlike the
standard content chrome so the deck opens with visual range."""

from __future__ import annotations

from pptx.enum.text import MSO_ANCHOR, PP_ALIGN

from ...spec.schema import AgendaSlide
from ..geometry import SLIDE_H_IN, SLIDE_W_IN, Box, rows
from ..registry import renderer
from ..shapes import add_accent_bar, add_brand_art, add_logo, add_rect
from ..text import add_text

BAND_W = 4.3


@renderer("agenda")
def render(slide, model: AgendaSlide, ctx) -> None:
    tokens = ctx.tokens
    m = tokens.margin_in

    # Full-height navy band, square edges (full bleed to three slide edges).
    add_rect(slide, Box(0, 0, BAND_W, SLIDE_H_IN), tokens, fill="primary",
             rounded=False)
    add_text(slide, Box(m, 2.55, BAND_W - m - 0.3, 1.1), model.title or "Agenda",
             tokens, scale="section_title", role="heading", color="white",
             bold=True, shrink_to_fit=True)
    if add_brand_art(slide, tokens, "swash_sky", Box(m, 3.6, 2.4, 0.33)) is None:
        add_accent_bar(slide, m, 3.65, 0.9, tokens, color="accent_warm", height_in=0.06)
    add_logo(slide, tokens, dark_bg=True, center_at_in=BAND_W / 2,
             bottom_in=7.0, height_in=0.4)

    # Numbered items on the white side.
    items_area = Box(BAND_W + 0.55, 0.9, SLIDE_W_IN - BAND_W - 0.55 - m, SLIDE_H_IN - 1.8)
    item_rows = rows(items_area, max(len(model.items), 3), 0.12)
    for i, (item, row) in enumerate(zip(model.items, item_rows, strict=False), start=1):
        # numbered sky squares, app-icon style
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

    # This slide draws its own chrome (it's in FULL_BLEED_TYPES): just the
    # page number, kept in the template's spot.
    if tokens.show_page_numbers:
        add_text(slide, Box(SLIDE_W_IN - m - 0.5, SLIDE_H_IN - 0.42, 0.5, 0.3),
                 str(ctx.slide_index + 1), tokens, scale="footer", color="accent",
                 align=PP_ALIGN.RIGHT)
