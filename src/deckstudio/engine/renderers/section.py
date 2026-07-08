"""Section divider: primary background, oversized number, gold rule."""

from __future__ import annotations

from pptx.enum.text import MSO_ANCHOR
from pptx.util import Pt

from ...spec.schema import SectionSlide
from ..geometry import SLIDE_H_IN, SLIDE_W_IN, Box
from ..registry import renderer
from ..shapes import add_accent_bar, fill_background
from ..text import add_text


@renderer("section")
def render(slide, model: SectionSlide, ctx) -> None:
    tokens = ctx.tokens
    fill_background(slide, tokens, "primary")
    m = tokens.margin_in + 0.4

    if model.number is not None:
        num_box = Box(m, 1.15, 3.0, 2.2)
        shape = add_text(slide, num_box, f"{model.number:02d}", tokens,
                         scale="big_number", role="heading", color="accent_warm",
                         bold=True)
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                run.font.size = Pt(110)

    add_accent_bar(slide, m, 3.55, 1.1, tokens, color="accent_warm", height_in=0.07)
    add_text(slide, Box(m, 3.8, SLIDE_W_IN - 2 * m, 1.6), model.title, tokens,
             scale="section_title", role="heading", color="white", bold=True,
             anchor=MSO_ANCHOR.TOP, shrink_to_fit=True)
    if model.subtitle:
        add_text(slide, Box(m, SLIDE_H_IN - 2.0, SLIDE_W_IN - 2 * m, 0.9),
                 model.subtitle, tokens, scale="subtitle", color="white",
                 shrink_to_fit=True)
