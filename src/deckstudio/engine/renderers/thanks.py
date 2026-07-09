"""Closing slide: primary background, thank-you message, contact line."""

from __future__ import annotations

from pptx.enum.text import MSO_ANCHOR

from ...spec.schema import ThanksSlide
from ..geometry import SLIDE_W_IN, Box
from ..registry import renderer
from ..shapes import add_accent_bar, add_brand_art, add_logo, fill_background
from ..text import add_text


@renderer("thanks")
def render(slide, model: ThanksSlide, ctx) -> None:
    tokens = ctx.tokens
    fill_background(slide, tokens, "primary")
    m = tokens.margin_in + 0.4

    title = model.title or "Thank you"
    add_text(slide, Box(m, 2.95, SLIDE_W_IN - 2 * m, 1.2),
             title, tokens, scale="section_title",
             role="heading", color="white", bold=True, anchor=MSO_ANCHOR.TOP)
    # SOA's own Thank You layout hand-circles the words — replicate that.
    # The ring is STRETCHED around the text block (as in the template) and
    # extends above/below the title line, so the message sits lower.
    circle_w = max(3.0, min(0.36 * len(title) + 0.9, 7.0))
    if add_brand_art(slide, tokens, "circle_sky",
                     Box(m - 0.5, 2.35, circle_w, 1.8), stretch=True) is None:
        add_accent_bar(slide, m, 2.7, 1.1, tokens, color="accent_warm", height_in=0.07)
    if model.message:
        add_text(slide, Box(m, 4.55, SLIDE_W_IN - 2 * m, 0.9), model.message,
                 tokens, scale="subtitle", color="white", shrink_to_fit=True)
    if model.contact:
        add_text(slide, Box(m, 5.6, SLIDE_W_IN - 2 * m, 0.5), model.contact,
                 tokens, scale="stat_label", color="accent_warm", bold=True)
    add_logo(slide, tokens, dark_bg=True, left_in=m, bottom_in=7.0, height_in=0.5)
