"""Shared chrome for standard (light-background) content slides."""

from __future__ import annotations

from pptx.enum.text import PP_ALIGN

from ...tokens import Tokens
from ..geometry import SLIDE_W_IN, Box, content_area
from ..shapes import add_accent_bar, add_logo
from ..text import add_text


def add_title_band(slide, tokens: Tokens, title: str, *, kicker: str | None = None) -> Box:
    """Kicker + assertion title + accent rule + logo. Returns the content area below."""
    m = tokens.margin_in
    top = tokens.title_top_in
    if kicker:
        add_text(slide, Box(m, top - 0.05, SLIDE_W_IN - 2 * m, 0.28), kicker.upper(),
                 tokens, scale="kicker", color="accent", bold=True)
        top += 0.3
    add_text(slide, Box(m, top, SLIDE_W_IN - 2 * m - 1.2, 0.85), title, tokens,
             scale="slide_title", role="heading", color="primary", bold=True,
             shrink_to_fit=True)
    bar_top = top + 0.92
    add_accent_bar(slide, m, bar_top, 0.9, tokens)
    add_logo(slide, tokens, right_in=SLIDE_W_IN - tokens.margin_in)
    return content_area(m, bar_top + 0.28)


def add_insight_strip(slide, area: Box, text: str, tokens: Tokens) -> None:
    """The 'so what' callout: gold rule + bold takeaway line, anchored at the
    bottom of the given area."""
    strip = Box(area.left_in, area.bottom_in - 0.5, area.width_in, 0.5)
    add_accent_bar(slide, strip.left_in, strip.top_in, 0.45, tokens,
                   color="accent_warm", height_in=0.05)
    add_text(slide, Box(strip.left_in, strip.top_in + 0.1, strip.width_in, 0.4),
             text, tokens, scale="body", color="primary", bold=True,
             align=PP_ALIGN.LEFT, shrink_to_fit=True)
