"""Shared chrome for standard (light-background) content slides."""

from __future__ import annotations

from pptx.enum.text import PP_ALIGN

from ...tokens import Tokens
from ..geometry import SLIDE_W_IN, Box, content_area
from ..shapes import add_accent_bar
from ..text import add_text


def add_title_band(slide, tokens: Tokens, title: str, *, kicker: str | None = None,
                   style: str = "left") -> Box:
    """Title chrome in one of four styles; returns the content area below.

    left      blue title left-aligned + short rule (the canonical look)
    centered  the same, centered
    banner    full-width navy band with white title
    tint      full-width pale-sky band with blue title
    """
    from pptx.enum.text import PP_ALIGN

    from ..geometry import SLIDE_H_IN  # noqa: F401  (parity with callers)
    from ..shapes import add_rect

    m = tokens.margin_in
    two_lines = len(title) > 52

    if style in ("banner", "tint"):
        band_h = (1.6 if two_lines else 1.3) + (0.3 if kicker else 0.0)
        add_rect(slide, Box(0, 0, SLIDE_W_IN, band_h), tokens,
                 fill="primary" if style == "banner" else "accent_tint",
                 rounded=False)
        top = 0.3
        kicker_color = "accent_warm" if style == "banner" else "primary"
        title_color = "white" if style == "banner" else "accent"
        if kicker:
            add_text(slide, Box(m, top, SLIDE_W_IN - 2 * m, 0.28), kicker.upper(),
                     tokens, scale="kicker", color=kicker_color, bold=True,
                     letter_spacing_pt=1.6)
            top += 0.32
        add_text(slide, Box(m, top, SLIDE_W_IN - 2 * m, band_h - top - 0.15),
                 title, tokens, scale="slide_title", role="heading",
                 color=title_color, bold=True, shrink_to_fit=True)
        return content_area(m, band_h + 0.3)

    centered = style == "centered"
    align = PP_ALIGN.CENTER if centered else PP_ALIGN.LEFT
    top = tokens.title_top_in
    if kicker:
        add_text(slide, Box(m, top - 0.05, SLIDE_W_IN - 2 * m, 0.28), kicker.upper(),
                 tokens, scale="kicker", color="primary", bold=True,
                 letter_spacing_pt=1.6, align=align)
        top += 0.3
    title_h = 1.35 if two_lines else 0.85
    add_text(slide, Box(m, top, SLIDE_W_IN - 2 * m, title_h), title, tokens,
             scale="slide_title", role="heading", color="accent", bold=True,
             shrink_to_fit=True, align=align)
    bar_top = top + title_h + 0.07
    bar_left = (SLIDE_W_IN - 0.9) / 2 if centered else m
    add_accent_bar(slide, bar_left, bar_top, 0.9, tokens)
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
