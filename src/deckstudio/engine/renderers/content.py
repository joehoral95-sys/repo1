"""Content slide: title + bullets. The escape hatch — the playbooks push
authors toward more visual types when one fits."""

from __future__ import annotations

from ...spec.schema import Bullet, ContentSlide
from ..registry import renderer
from ..text import add_bullets
from ._common import add_title_band


@renderer("content")
def render(slide, model: ContentSlide, ctx) -> None:
    tokens = ctx.tokens
    area = add_title_band(slide, tokens, model.title, kicker=model.kicker)
    items: list = []
    for b in model.bullets:
        if isinstance(b, Bullet):
            items.append((b.text, b.sub) if b.sub else b.text)
        else:
            items.append(b)
    add_bullets(slide, area, items, tokens)
