"""Icon row: 2-4 columns of icon + heading + text. Falls back to an accent
initial disc when no icon asset is given."""

from __future__ import annotations

from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches

from ...spec.schema import IconRowSlide
from ..geometry import SLIDE_W_IN, Box, columns, content_area
from ..registry import renderer
from ..shapes import add_accent_bar, add_picture_fitted
from ..text import add_text


@renderer("icon_row")
def render(slide, model: IconRowSlide, ctx) -> None:
    """Variants: centered (icon columns) | rows (stacked icon+text rows)."""
    tokens = ctx.tokens
    if ctx.variant(model) == "rows":
        _rows(slide, model, ctx)
        return
    m = tokens.margin_in
    add_text(slide, Box(m, tokens.title_top_in + 0.15, SLIDE_W_IN - 2 * m, 0.85),
             model.title, tokens, scale="slide_title", role="heading",
             color="accent", bold=True, align=PP_ALIGN.CENTER, shrink_to_fit=True)
    add_accent_bar(slide, (SLIDE_W_IN - 0.9) / 2, tokens.title_top_in + 1.1, 0.9, tokens)
    area = content_area(m, tokens.title_top_in + 1.55)
    icon_d = 1.0
    # disc color cycles through brand blues so the row reads designed
    disc_styles = [("accent", "white"), ("primary", "white"), ("accent_warm", "primary")]
    for i, (item, col) in enumerate(
            zip(model.items, columns(area, len(model.items), 0.4), strict=True)):
        cx = col.left_in + (col.width_in - icon_d) / 2
        icon_top = col.top_in + 0.25
        icon_path = None
        if item.icon:
            icons_dir = tokens.brand_dir / "assets" / "icons"
            for candidate in (icons_dir / item.icon, icons_dir / f"{item.icon}.png"):
                if candidate.exists():
                    icon_path = candidate
                    break
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


def _rows(slide, model: IconRowSlide, ctx) -> None:
    from ..geometry import rows as grid_rows
    from ._common import add_title_band

    tokens = ctx.tokens
    area = add_title_band(slide, tokens, model.title, kicker=model.kicker)
    disc_styles = [("accent", "white"), ("primary", "white"), ("accent_warm", "primary")]
    icon_d = 0.85
    for i, (item, row) in enumerate(
            zip(model.items, grid_rows(area, max(len(model.items), 2), 0.2),
                strict=False)):
        icon_top = row.top_in + (row.height_in - icon_d) / 2
        icon_path = None
        if item.icon:
            icons_dir = tokens.brand_dir / "assets" / "icons"
            for candidate in (icons_dir / item.icon, icons_dir / f"{item.icon}.png"):
                if candidate.exists():
                    icon_path = candidate
                    break
        if icon_path:
            add_picture_fitted(slide, str(icon_path),
                               Box(row.left_in, icon_top, icon_d, icon_d))
        else:
            fill, initial = disc_styles[i % len(disc_styles)]
            disc = slide.shapes.add_shape(
                MSO_SHAPE.OVAL, Inches(row.left_in), Inches(icon_top),
                Inches(icon_d), Inches(icon_d))
            disc.fill.solid()
            disc.fill.fore_color.rgb = tokens.color(fill)
            disc.line.fill.background()
            disc.shadow.inherit = False
            add_text(slide, Box(row.left_in, icon_top + 0.16, icon_d, 0.55),
                     item.heading[:1].upper(), tokens, scale="subtitle",
                     role="heading", color=initial, bold=True,
                     align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        text_left = row.left_in + icon_d + 0.45
        add_text(slide, Box(text_left, row.top_in + row.height_in * 0.14,
                            row.width_in - icon_d - 0.45, 0.45),
                 item.heading, tokens, scale="subtitle", role="heading",
                 color="primary", bold=True, shrink_to_fit=True)
        add_text(slide, Box(text_left, row.top_in + row.height_in * 0.14 + 0.5,
                            row.width_in - icon_d - 0.45,
                            row.height_in * 0.72 - 0.5),
                 item.text, tokens, scale="stat_label", color="neutral_dark",
                 line_spacing=1.1, shrink_to_fit=True)
