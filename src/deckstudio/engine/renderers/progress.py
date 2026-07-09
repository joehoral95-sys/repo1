"""Progress rings: 'how far along are we' rendered as donut gauges."""

from __future__ import annotations

from pptx.enum.text import PP_ALIGN

from ...spec.schema import ProgressSlide
from ..geometry import Box, columns, vcenter
from ..infographics import add_progress_ring
from ..registry import renderer
from ..text import add_text
from ._common import add_title_band


@renderer("progress")
def render(slide, model: ProgressSlide, ctx) -> None:
    tokens = ctx.tokens
    area = add_title_band(slide, tokens, model.title, kicker=model.kicker)
    n = len(model.items)
    caption_pad = 0.55 if model.caption else 0.0
    ring_area = Box(area.left_in, area.top_in, area.width_in,
                    area.height_in - caption_pad)
    ring_h = min(3.1, ring_area.height_in - 0.2)
    for item, col in zip(model.items, columns(ring_area, n, 0.5), strict=True):
        add_progress_ring(slide, vcenter(col, ring_h), item.percent / 100.0,
                          item.label, tokens)
    if model.caption:
        add_text(slide, Box(area.left_in, area.bottom_in - 0.4, area.width_in, 0.4),
                 model.caption, tokens, scale="stat_label", color="neutral_mid",
                 align=PP_ALIGN.CENTER, shrink_to_fit=True)
