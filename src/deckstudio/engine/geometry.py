"""Slide grid math. All positions flow through here so layout stays consistent.

Slide canvas: 16:9 widescreen, 13.333in x 7.5in.
"""

from __future__ import annotations

from dataclasses import dataclass

from pptx.util import Emu, Inches

SLIDE_W_IN = 13.333
SLIDE_H_IN = 7.5
SLIDE_W = Emu(12192000)
SLIDE_H = Emu(6858000)


@dataclass(frozen=True)
class Box:
    left_in: float
    top_in: float
    width_in: float
    height_in: float

    @property
    def left(self):
        return Inches(self.left_in)

    @property
    def top(self):
        return Inches(self.top_in)

    @property
    def width(self):
        return Inches(self.width_in)

    @property
    def height(self):
        return Inches(self.height_in)

    @property
    def right_in(self) -> float:
        return self.left_in + self.width_in

    @property
    def bottom_in(self) -> float:
        return self.top_in + self.height_in


def content_area(margin_in: float, top_in: float, bottom_in: float = 0.75) -> Box:
    """The area below the title band and above the footer."""
    return Box(
        left_in=margin_in,
        top_in=top_in,
        width_in=SLIDE_W_IN - 2 * margin_in,
        height_in=SLIDE_H_IN - top_in - bottom_in,
    )


def columns(area: Box, n: int, gutter_in: float) -> list[Box]:
    """Split an area into n equal columns."""
    col_w = (area.width_in - gutter_in * (n - 1)) / n
    return [
        Box(area.left_in + i * (col_w + gutter_in), area.top_in, col_w, area.height_in)
        for i in range(n)
    ]


def rows(area: Box, n: int, gutter_in: float) -> list[Box]:
    row_h = (area.height_in - gutter_in * (n - 1)) / n
    return [
        Box(area.left_in, area.top_in + i * (row_h + gutter_in), area.width_in, row_h)
        for i in range(n)
    ]


def inset(box: Box, all_in: float = 0.0, *, x_in: float | None = None,
          y_in: float | None = None) -> Box:
    dx = all_in if x_in is None else x_in
    dy = all_in if y_in is None else y_in
    return Box(box.left_in + dx, box.top_in + dy,
               box.width_in - 2 * dx, box.height_in - 2 * dy)


def vcenter(box: Box, height_in: float) -> Box:
    """A box of the given height vertically centered inside `box`."""
    top = box.top_in + max(0.0, (box.height_in - height_in) / 2)
    return Box(box.left_in, top, box.width_in, min(height_in, box.height_in))
