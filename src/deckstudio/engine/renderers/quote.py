"""Quote / big-statement slide: full-bleed primary, oversized gold quote mark."""

from __future__ import annotations

from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Pt

from ...spec.schema import QuoteSlide
from ..geometry import SLIDE_W_IN, Box
from ..registry import renderer
from ..shapes import fill_background
from ..text import add_text


@renderer("quote")
def render(slide, model: QuoteSlide, ctx) -> None:
    tokens = ctx.tokens
    fill_background(slide, tokens, "primary")
    m = tokens.margin_in + 1.0

    mark = add_text(slide, Box(m - 0.5, 0.9, 2.0, 1.6), "“", tokens,
                    scale="big_number", role="heading", color="accent_warm", bold=True)
    for para in mark.text_frame.paragraphs:
        for run in para.runs:
            run.font.size = Pt(120)

    add_text(slide, Box(m, 2.35, SLIDE_W_IN - 2 * m, 2.6), model.text, tokens,
             scale="quote", role="heading", color="white",
             anchor=MSO_ANCHOR.MIDDLE, align=PP_ALIGN.LEFT, line_spacing=1.15,
             shrink_to_fit=True)
    if model.attribution:
        add_text(slide, Box(m, 5.3, SLIDE_W_IN - 2 * m, 0.6),
                 f"—  {model.attribution}", tokens, scale="subtitle",
                 color="accent_warm", bold=True)
