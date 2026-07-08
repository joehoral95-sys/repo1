"""Closing slide: primary background, thank-you message, contact line."""

from __future__ import annotations

from pptx.enum.text import MSO_ANCHOR

from ...spec.schema import ThanksSlide
from ..geometry import SLIDE_W_IN, Box
from ..registry import renderer
from ..shapes import add_accent_bar, add_logo, fill_background
from ..text import add_text


@renderer("thanks")
def render(slide, model: ThanksSlide, ctx) -> None:
    tokens = ctx.tokens
    fill_background(slide, tokens, "primary")
    m = tokens.margin_in + 0.4

    add_accent_bar(slide, m, 2.7, 1.1, tokens, color="accent_warm", height_in=0.07)
    add_text(slide, Box(m, 2.95, SLIDE_W_IN - 2 * m, 1.2),
             model.title or "Thank you", tokens, scale="section_title",
             role="heading", color="white", bold=True, anchor=MSO_ANCHOR.TOP)
    if model.message:
        add_text(slide, Box(m, 4.25, SLIDE_W_IN - 2 * m, 0.9), model.message,
                 tokens, scale="subtitle", color="white", shrink_to_fit=True)
    if model.contact:
        add_text(slide, Box(m, 5.4, SLIDE_W_IN - 2 * m, 0.5), model.contact,
                 tokens, scale="stat_label", color="accent_warm", bold=True)
    add_logo(slide, tokens, dark_bg=True, right_in=SLIDE_W_IN - tokens.margin_in,
             top_in=6.4, height_in=0.5)
