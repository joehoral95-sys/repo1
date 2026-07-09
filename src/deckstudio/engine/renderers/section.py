"""Section divider: navy background, oversized number, hand-drawn sky swash
under the title (the official SOA divider layouts use exactly this mark)."""

from __future__ import annotations

from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Pt

from ...spec.schema import SectionSlide
from ..geometry import SLIDE_W_IN, Box
from ..registry import renderer
from ..shapes import add_accent_bar, add_brand_art, add_logo, add_rect, fill_background
from ..text import add_text


@renderer("section")
def render(slide, model: SectionSlide, ctx) -> None:
    tokens = ctx.tokens
    fill_background(slide, tokens, "primary")
    m = tokens.margin_in + 0.4

    add_brand_art(slide, tokens, "shield_watermark", Box(9.6, 3.2, 5.2, 5.2))

    if model.number is not None:
        # app-icon style chip: sky rounded square, navy number
        chip = Box(m, 1.15, 1.7, 1.7)
        add_rect(slide, chip, tokens, fill="accent_warm", rounded=True, corner=0.18)
        shape = add_text(slide, Box(chip.left_in, chip.top_in + 0.28, chip.width_in, 1.2),
                         f"{model.number:02d}", tokens, scale="big_number",
                         role="heading", color="primary", bold=True,
                         align=PP_ALIGN.CENTER)
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                run.font.size = Pt(64)

    text_w = (6.4 if model.preview else SLIDE_W_IN - 2 * m)
    kicker = model.kicker or (f"SECTION {model.number:02d}" if model.number else None)
    if kicker:
        add_text(slide, Box(m, 3.32, text_w, 0.32), kicker.upper(), tokens,
                 scale="kicker", color="accent_warm", bold=True,
                 letter_spacing_pt=1.6)
    add_text(slide, Box(m, 3.7, text_w, 1.1), model.title, tokens,
             scale="section_title", role="heading", color="white", bold=True,
             anchor=MSO_ANCHOR.TOP, shrink_to_fit=True)
    # SOA's brush-stroke underline; falls back to a straight rule if the
    # asset is missing.
    if add_brand_art(slide, tokens, "swash_sky", Box(m, 4.75, 3.0, 0.41)) is None:
        add_accent_bar(slide, m, 4.85, 1.1, tokens, color="accent_warm", height_in=0.07)

    if model.subtitle:
        add_text(slide, Box(m, 5.35, text_w, 0.9),
                 model.subtitle, tokens, scale="subtitle", color="white",
                 line_spacing=1.15, shrink_to_fit=True)
    if model.preview:
        _preview_panel(slide, model.preview, tokens)
    add_logo(slide, tokens, dark_bg=True, left_in=m, bottom_in=7.0, height_in=0.4)


PREVIEW_STATUS = {"on_track": "positive", "watch": "warning", "pending": "neutral_mid"}


def _preview_panel(slide, metrics, tokens) -> None:
    """Right-side teaser: what this section will show, with status dots and
    sky values — the inspiration decks' divider pattern."""
    from pptx.enum.shapes import MSO_SHAPE
    from pptx.util import Inches

    panel = Box(7.6, 1.5, 4.9, 4.6)
    n = len(metrics)
    row_h = min(0.75, panel.height_in / n)
    for i, metric in enumerate(metrics):
        y = panel.top_in + i * row_h
        if i > 0:
            rule = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE, Inches(panel.left_in), Inches(y),
                Inches(panel.width_in), Inches(0.011))
            rule.fill.solid()
            rule.fill.fore_color.rgb = RGBColor.from_string("2A4A6B")
            rule.line.fill.background()
            rule.shadow.inherit = False
        if metric.status:
            d = 0.11
            dot = slide.shapes.add_shape(
                MSO_SHAPE.OVAL, Inches(panel.left_in),
                Inches(y + (row_h - d) / 2), Inches(d), Inches(d))
            dot.fill.solid()
            dot.fill.fore_color.rgb = tokens.color(PREVIEW_STATUS[metric.status])
            dot.line.fill.background()
            dot.shadow.inherit = False
        add_text(slide, Box(panel.left_in + 0.3, y, panel.width_in - 1.7, row_h),
                 metric.label, tokens, scale="stat_label", color="white",
                 anchor=MSO_ANCHOR.MIDDLE, shrink_to_fit=True)
        add_text(slide, Box(panel.right_in - 1.35, y, 1.35, row_h), metric.value,
                 tokens, scale="stat_label", color="accent_warm", bold=True,
                 align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)
