"""Chart slide: assertion title + native chart + optional insight callout."""

from __future__ import annotations

from pptx.enum.text import PP_ALIGN

from ...spec.schema import ChartSlide
from ..charts import add_chart
from ..geometry import Box
from ..registry import renderer
from ..text import add_text
from ._common import add_insight_strip, add_title_band


@renderer("chart")
def render(slide, model: ChartSlide, ctx) -> None:
    tokens = ctx.tokens
    area = add_title_band(slide, tokens, model.title)

    chart_bottom_pad = 0.0
    if model.insight:
        chart_bottom_pad += 0.6
    if model.source:
        chart_bottom_pad += 0.25

    chart_box = Box(area.left_in, area.top_in,
                    area.width_in, area.height_in - chart_bottom_pad)
    add_chart(slide, model.chart, chart_box, tokens)

    if model.insight:
        add_insight_strip(slide, area, model.insight, tokens)
    if model.source:
        add_text(slide, Box(area.left_in, area.bottom_in + 0.05, area.width_in, 0.22),
                 f"Source: {model.source}", tokens, scale="caption",
                 color="neutral_mid", align=PP_ALIGN.RIGHT)
