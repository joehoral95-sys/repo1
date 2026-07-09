"""Title slide: two-tone composition — navy gradient field carrying the
title, a bright-blue vertical band on the right with the white shield mark
bleeding off the edge."""

from __future__ import annotations

from pptx.enum.text import MSO_ANCHOR

from ...spec.schema import TitleSlide
from ..geometry import SLIDE_H_IN, SLIDE_W_IN, Box
from ..registry import renderer
from ..shapes import add_accent_bar, add_brand_art, add_logo, add_rect, fill_background
from ..text import add_text

BAND_LEFT = 9.7


@renderer("title")
def render(slide, model: TitleSlide, ctx) -> None:
    tokens = ctx.tokens
    fill_background(slide, tokens, "primary")
    m = tokens.margin_in + 0.4

    # Bright-blue band, white shield mark half off-canvas.
    add_rect(slide, Box(BAND_LEFT, 0, SLIDE_W_IN - BAND_LEFT, SLIDE_H_IN), tokens,
             fill="accent", rounded=False)
    add_brand_art(slide, tokens, "shield_white", Box(BAND_LEFT + 0.55, 2.05, 3.4, 3.4))

    text_w = BAND_LEFT - m - 0.5
    add_accent_bar(slide, m, 2.55, 1.1, tokens, color="accent_warm", height_in=0.07)
    add_text(slide, Box(m, 2.8, text_w, 1.9), model.title, tokens,
             scale="section_title", role="heading", color="white", bold=True,
             anchor=MSO_ANCHOR.TOP, shrink_to_fit=True)
    if model.subtitle:
        add_text(slide, Box(m, 4.7, text_w, 0.7), model.subtitle, tokens,
                 scale="subtitle", color="white", shrink_to_fit=True)

    meta_bits = [b for b in (model.presenter, ctx.deck.date) if b]
    if meta_bits:
        add_text(slide, Box(m, SLIDE_H_IN - 1.75, text_w, 0.6),
                 "  ·  ".join(meta_bits), tokens, scale="stat_label", color="white")
    add_logo(slide, tokens, dark_bg=True, center_at_in=BAND_LEFT / 2,
             bottom_in=7.0, height_in=0.5)
