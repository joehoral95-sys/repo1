"""Big-number slide: 1-4 KPI stat tiles. One stat = hero treatment."""

from __future__ import annotations

from ...spec.schema import BigNumberSlide
from ..geometry import Box, columns, vcenter
from ..infographics import add_stat_tile
from ..registry import renderer
from ._common import add_title_band


@renderer("big_number")
def render(slide, model: BigNumberSlide, ctx) -> None:
    tokens = ctx.tokens
    area = add_title_band(slide, tokens, model.title)
    n = len(model.stats)
    if n == 1:
        tile_w = min(5.4, area.width_in)
        tile = Box(area.left_in + (area.width_in - tile_w) / 2,
                   area.top_in + 0.2, tile_w, min(3.4, area.height_in - 0.4))
        add_stat_tile(slide, tile, model.stats[0], tokens, hero=True)
        return
    tile_h = min(3.2, area.height_in - 0.3)
    for stat, col in zip(model.stats, columns(area, n, tokens.gutter_in), strict=True):
        add_stat_tile(slide, vcenter(col, tile_h), stat, tokens)
