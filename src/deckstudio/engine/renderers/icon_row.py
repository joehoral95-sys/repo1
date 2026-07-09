"""Icon row: 2-4 columns of icon + heading + text. Falls back to an accent
initial disc when no icon asset is given."""

from __future__ import annotations

from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches

from ...spec.schema import IconRowSlide
from ..geometry import Box, columns
from ..registry import renderer
from ..shapes import add_picture_fitted
from ..text import add_text
from ._common import add_title_band


@renderer("icon_row")
def render(slide, model: IconRowSlide, ctx) -> None:
    tokens = ctx.tokens
    area = add_title_band(slide, tokens, model.title)
    icon_d = 1.0
    # disc color cycles through brand blues so the row reads designed
    disc_styles = [("accent", "white"), ("primary", "white"), ("accent_warm", "primary")]
    for i, (item, col) in enumerate(
            zip(model.items, columns(area, len(model.items), 0.4), strict=True)):
        cx = col.left_in + (col.width_in - icon_d) / 2
        icon_top = col.top_in + 0.25
        icon_path = None
        if item.icon:
            candidate = tokens.brand_dir / "assets" / "icons" / item.icon
            if candidate.exists():
                icon_path = candidate
            else:
                ctx.warn(f"icon '{item.icon}' not found in brand/assets/icons — using fallback disc")
        if icon_path:
            add_picture_fitted(slide, str(icon_path), Box(cx, icon_top, icon_d, icon_d))
        else:
            disc_fill, initial_color = disc_styles[i % len(disc_styles)]
            disc = slide.shapes.add_shape(
                MSO_SHAPE.OVAL, Inches(cx), Inches(icon_top), Inches(icon_d), Inches(icon_d))
            disc.fill.solid()
            disc.fill.fore_color.rgb = tokens.color(disc_fill)
            disc.line.fill.background()
            disc.shadow.inherit = False
            add_text(slide, Box(cx, icon_top + 0.22, icon_d, 0.6),
                     item.heading[:1].upper(), tokens, scale="slide_title",
                     role="heading", color=initial_color, bold=True, align=PP_ALIGN.CENTER,
                     anchor=MSO_ANCHOR.MIDDLE)

        add_text(slide, Box(col.left_in, icon_top + icon_d + 0.2, col.width_in, 0.55),
                 item.heading, tokens, scale="subtitle", role="heading",
                 color="primary", bold=True, align=PP_ALIGN.CENTER, shrink_to_fit=True)
        add_text(slide, Box(col.left_in + 0.1, icon_top + icon_d + 0.8,
                            col.width_in - 0.2, col.height_in - icon_d - 1.1),
                 item.text, tokens, scale="stat_label", color="neutral_dark",
                 align=PP_ALIGN.CENTER, line_spacing=1.15, shrink_to_fit=True)
