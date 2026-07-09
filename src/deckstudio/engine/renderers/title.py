"""Title slide — variants:

  band       two-tone: navy field + bright-blue right band, white shield
  band-left  mirror: blue band on the left, text right
  watermark  full navy with the oversized shield watermark
  minimal    white, blue title, swash — the quiet open
"""

from __future__ import annotations

from pptx.enum.text import MSO_ANCHOR

from ...spec.schema import TitleSlide
from ..geometry import SLIDE_H_IN, SLIDE_W_IN, Box
from ..registry import renderer
from ..shapes import add_accent_bar, add_brand_art, add_logo, add_rect, fill_background
from ..text import add_text

BAND_LEFT = 9.7
BAND_W = SLIDE_W_IN - BAND_LEFT


@renderer("title")
def render(slide, model: TitleSlide, ctx) -> None:
    tokens = ctx.tokens
    variant = ctx.variant(model)

    if variant == "minimal":
        _minimal(slide, model, ctx)
        return

    fill_background(slide, tokens, "primary")

    if variant == "band":
        text_left, text_w = tokens.margin_in + 0.4, BAND_LEFT - tokens.margin_in - 0.9
        add_rect(slide, Box(BAND_LEFT, 0, BAND_W, SLIDE_H_IN), tokens,
                 fill="accent", rounded=False)
        add_brand_art(slide, tokens, "shield_white",
                      Box(BAND_LEFT + 0.35, 2.15, BAND_W - 0.7, 3.2))
        logo_center = BAND_LEFT / 2
    elif variant == "band-left":
        text_left, text_w = BAND_W + 1.0, SLIDE_W_IN - BAND_W - 1.6
        add_rect(slide, Box(0, 0, BAND_W, SLIDE_H_IN), tokens,
                 fill="accent", rounded=False)
        add_brand_art(slide, tokens, "shield_white",
                      Box(0.35, 2.15, BAND_W - 0.7, 3.2))
        logo_center = BAND_W + (SLIDE_W_IN - BAND_W) / 2
    else:  # watermark
        text_left, text_w = tokens.margin_in + 0.4, 8.4
        add_brand_art(slide, tokens, "shield_watermark", Box(9.0, 0.9, 6.4, 6.4))
        logo_center = SLIDE_W_IN / 2

    add_accent_bar(slide, text_left, 2.55, 1.1, tokens, color="accent_warm",
                   height_in=0.07)
    add_text(slide, Box(text_left, 2.8, text_w, 1.9), model.title, tokens,
             scale="section_title", role="heading", color="white", bold=True,
             anchor=MSO_ANCHOR.TOP, shrink_to_fit=True)
    if model.subtitle:
        add_text(slide, Box(text_left, 4.7, text_w, 0.7), model.subtitle, tokens,
                 scale="subtitle", color="white", shrink_to_fit=True)
    meta_bits = [b for b in (model.presenter, ctx.deck.date) if b]
    if meta_bits:
        add_text(slide, Box(text_left, SLIDE_H_IN - 1.75, text_w, 0.6),
                 "  ·  ".join(meta_bits), tokens, scale="stat_label", color="white")
    add_logo(slide, tokens, dark_bg=True, center_at_in=logo_center,
             bottom_in=7.0, height_in=0.5)


def _minimal(slide, model: TitleSlide, ctx) -> None:
    tokens = ctx.tokens
    m = tokens.margin_in + 0.4
    add_text(slide, Box(m, 2.3, SLIDE_W_IN - 2 * m, 1.9), model.title, tokens,
             scale="section_title", role="heading", color="accent", bold=True,
             anchor=MSO_ANCHOR.TOP, shrink_to_fit=True)
    add_brand_art(slide, tokens, "swash_sky", Box(m, 4.05, 3.0, 0.41))
    if model.subtitle:
        add_text(slide, Box(m, 4.75, SLIDE_W_IN - 2 * m, 0.7), model.subtitle,
                 tokens, scale="subtitle", color="neutral_dark", shrink_to_fit=True)
    meta_bits = [b for b in (model.presenter, ctx.deck.date) if b]
    if meta_bits:
        add_text(slide, Box(m, SLIDE_H_IN - 1.75, SLIDE_W_IN - 2 * m, 0.6),
                 "  ·  ".join(meta_bits), tokens, scale="stat_label",
                 color="neutral_mid")
    add_logo(slide, tokens, left_in=m, bottom_in=7.05, height_in=0.42)
