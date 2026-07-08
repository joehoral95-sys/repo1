"""Comparison: two panels; the emphasized option gets the primary treatment."""

from __future__ import annotations

from ...spec.schema import ComparisonSide, ComparisonSlide
from ..geometry import Box, columns, inset
from ..registry import renderer
from ..shapes import add_rect
from ..text import add_bullets, add_text
from ._common import add_title_band


@renderer("comparison")
def render(slide, model: ComparisonSlide, ctx) -> None:
    tokens = ctx.tokens
    area = add_title_band(slide, tokens, model.title)
    left_col, right_col = columns(area, 2, tokens.gutter_in + 0.1)
    _panel(slide, left_col, model.left, tokens, emphasized=model.emphasize == "left")
    _panel(slide, right_col, model.right, tokens, emphasized=model.emphasize == "right")


def _panel(slide, box: Box, side: ComparisonSide, tokens, *, emphasized: bool) -> None:
    fill = "primary" if emphasized else "neutral_light"
    heading_color = "accent_warm" if emphasized else "primary"
    body_color = "white" if emphasized else "neutral_dark"
    add_rect(slide, box, tokens, fill=fill, rounded=True, corner=0.05)
    pad = inset(box, x_in=0.35, y_in=0.3)
    add_text(slide, Box(pad.left_in, pad.top_in, pad.width_in, 0.5), side.heading,
             tokens, scale="subtitle", role="heading", color=heading_color,
             bold=True, shrink_to_fit=True)
    bullets_box = Box(pad.left_in, pad.top_in + 0.65, pad.width_in,
                      pad.height_in - 0.65)
    add_bullets(slide, bullets_box, list(side.bullets), tokens, color=body_color,
                space_after_pt=8)
