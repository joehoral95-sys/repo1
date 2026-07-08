"""Semantic lint beyond the schema: catches slides that would be VALID but BAD.

Messages are advisory (warnings, not errors) and written so an LLM or Joe can
act on them directly.
"""

from __future__ import annotations

from ..engine.text import strip_markup
from ..spec.schema import ChartSlide, ContentSlide, DeckSpec


def lint(spec: DeckSpec) -> list[str]:
    warnings: list[str] = []
    warnings.extend(_deck_shape(spec))
    for slide in spec.slides:
        if isinstance(slide, ContentSlide):
            warnings.extend(_content_density(slide))
        if isinstance(slide, ChartSlide):
            warnings.extend(_chart_choices(slide))
        warnings.extend(_title_style(slide))
    return warnings


def _deck_shape(spec: DeckSpec) -> list[str]:
    w = []
    types = [s.type for s in spec.slides]
    if types[0] != "title":
        w.append("deck: first slide isn't a 'title' slide — decks should open with one.")
    if not spec.deck.audience or not spec.deck.intent:
        w.append("deck: audience/intent missing — fill them in; they should drive "
                 "every content choice (see playbooks/audience-adaptation.md).")
    content_run = 0
    for s in spec.slides:
        content_run = content_run + 1 if s.type == "content" else 0
        if content_run == 3:
            w.append(f"deck: 3+ consecutive bullet slides ending at '{s.id}' — "
                     "vary the visual rhythm (big_number, chart, icon_row, quote…).")
            break
    return w


def _content_density(slide: ContentSlide) -> list[str]:
    w = []
    total_words = 0
    for b in slide.bullets:
        text = b if isinstance(b, str) else b.text
        total_words += len(strip_markup(text).split())
    if total_words > 60:
        w.append(f"slide '{slide.id}': ~{total_words} words of bullets — slides aren't "
                 "documents. Cut to <40 words or split the slide; detail goes to notes.")
    if len(slide.bullets) > 5:
        w.append(f"slide '{slide.id}': {len(slide.bullets)} bullets — 3-5 reads best.")
    return w


def _chart_choices(slide: ChartSlide) -> list[str]:
    w = []
    c = slide.chart
    if c.kind == "line" and len(c.categories) < 3:
        w.append(f"slide '{slide.id}': a line chart with {len(c.categories)} points "
                 "shows no trend — use bar_clustered or big_number instead.")
    if c.kind in ("bar_clustered", "bar_stacked") and len(c.categories) > 12:
        w.append(f"slide '{slide.id}': {len(c.categories)} categories is crowded for "
                 "columns — consider bar_horizontal or aggregating.")
    if not slide.insight:
        w.append(f"slide '{slide.id}': chart has no `insight:` — every chart should "
                 "state its 'so what' (see playbooks/data-storytelling.md).")
    if len(c.series) == 1 and len(c.categories) <= 2 and c.kind not in ("pie", "doughnut"):
        w.append(f"slide '{slide.id}': {len(c.categories)} value(s) in one series — "
                 "a big_number slide would land harder than a chart.")
    return w


_TOPIC_TITLES = {
    "update", "overview", "background", "status", "results", "data", "numbers",
    "agenda", "next steps", "summary", "introduction", "discussion",
}


def _title_style(slide) -> list[str]:
    title = getattr(slide, "title", None)
    if not title or slide.type in ("title", "agenda", "thanks", "section"):
        return []
    plain = strip_markup(title).strip().lower()
    if plain in _TOPIC_TITLES or (len(plain.split()) <= 2 and not any(ch.isdigit() for ch in plain)):
        return [f"slide '{slide.id}': title '{title}' is a topic label, not an assertion. "
                "Say what the audience should take away, e.g. "
                "'Membership grew for the 6th straight quarter'."]
    return []
