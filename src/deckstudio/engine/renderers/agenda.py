"""Agenda: numbered items with accent numerals — scannable, not a wall of text."""

from __future__ import annotations

from pptx.enum.text import MSO_ANCHOR

from ...spec.schema import AgendaSlide
from ..geometry import Box, rows
from ..registry import renderer
from ..text import add_text
from ._common import add_title_band


@renderer("agenda")
def render(slide, model: AgendaSlide, ctx) -> None:
    tokens = ctx.tokens
    area = add_title_band(slide, tokens, model.title or "Agenda")
    item_rows = rows(area, max(len(model.items), 3), 0.12)
    for i, (item, row) in enumerate(zip(model.items, item_rows, strict=False), start=1):
        num_box = Box(row.left_in, row.top_in, 0.7, row.height_in)
        add_text(slide, num_box, f"{i:02d}", tokens, scale="slide_title",
                 role="heading", color="accent", bold=True, anchor=MSO_ANCHOR.MIDDLE)
        text_box = Box(row.left_in + 0.9, row.top_in, row.width_in - 0.9, row.height_in)
        add_text(slide, text_box, item, tokens, scale="subtitle",
                 color="neutral_dark", anchor=MSO_ANCHOR.MIDDLE, shrink_to_fit=True)
