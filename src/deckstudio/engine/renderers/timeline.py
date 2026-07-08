"""Timeline: horizontal spine with milestone nodes; done nodes are filled."""

from __future__ import annotations

from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

from ...spec.schema import TimelineSlide
from ..geometry import Box
from ..registry import renderer
from ..text import add_text
from ._common import add_title_band


@renderer("timeline")
def render(slide, model: TimelineSlide, ctx) -> None:
    tokens = ctx.tokens
    area = add_title_band(slide, tokens, model.title)
    n = len(model.milestones)
    spine_y = area.top_in + area.height_in * 0.42
    node_d = 0.34

    spine = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(area.left_in + 0.2), Inches(spine_y - 0.015),
        Inches(area.width_in - 0.4), Inches(0.03))
    spine.fill.solid()
    spine.fill.fore_color.rgb = tokens.color("neutral_mid")
    spine.line.fill.background()
    spine.shadow.inherit = False

    step = (area.width_in - 0.4 - node_d) / max(n - 1, 1)
    for i, ms in enumerate(model.milestones):
        cx = area.left_in + 0.2 + i * step
        node = slide.shapes.add_shape(
            MSO_SHAPE.OVAL, Inches(cx), Inches(spine_y - node_d / 2),
            Inches(node_d), Inches(node_d))
        node.shadow.inherit = False
        if ms.done:
            node.fill.solid()
            node.fill.fore_color.rgb = tokens.color("accent")
            node.line.fill.background()
        else:
            node.fill.solid()
            node.fill.fore_color.rgb = tokens.color("white")
            node.line.color.rgb = tokens.color("accent")
            node.line.width = Pt(2)

        label_w = min(step + node_d, 2.4)
        label_left = cx + node_d / 2 - label_w / 2
        label_left = min(max(label_left, area.left_in), area.right_in - label_w)
        above = i % 2 == 0
        if ms.date:
            date_top = spine_y - 0.75 if above else spine_y + 0.35
            add_text(slide, Box(label_left, date_top, label_w, 0.3), ms.date, tokens,
                     scale="caption", color="accent", bold=True, align=PP_ALIGN.CENTER)
        label_top = spine_y - 1.35 if above else spine_y + 0.68
        add_text(slide, Box(label_left, label_top, label_w, 0.85), ms.label, tokens,
                 scale="stat_label", color="neutral_dark", align=PP_ALIGN.CENTER,
                 shrink_to_fit=True)
