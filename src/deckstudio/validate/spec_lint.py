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
        warnings.extend(_human_voice(slide))
    return warnings


def _deck_shape(spec: DeckSpec) -> list[str]:
    w = []
    types = [s.type for s in spec.slides]
    if types[0] != "title":
        w.append("deck: first slide isn't a 'title' slide - decks should open with one.")
    if not spec.deck.audience or not spec.deck.intent:
        w.append("deck: audience/intent missing - fill them in; they should drive "
                 "every content choice (see playbooks/audience-adaptation.md).")
    content_run = 0
    for s in spec.slides:
        content_run = content_run + 1 if s.type == "content" else 0
        if content_run == 3:
            w.append(f"deck: 3+ consecutive bullet slides ending at '{s.id}' - "
                     "vary the visual rhythm (big_number, chart, icon_row, quote...).")
            break
    return w


def _content_density(slide: ContentSlide) -> list[str]:
    w = []
    total_words = 0
    for b in slide.bullets:
        text = b if isinstance(b, str) else b.text
        total_words += len(strip_markup(text).split())
    if total_words > 60:
        w.append(f"slide '{slide.id}': ~{total_words} words of bullets - slides aren't "
                 "documents. Cut to <40 words or split the slide; detail goes to notes.")
    if len(slide.bullets) > 5:
        w.append(f"slide '{slide.id}': {len(slide.bullets)} bullets - 3-5 reads best.")
    return w


def _chart_choices(slide: ChartSlide) -> list[str]:
    w = []
    c = slide.chart
    if c.kind == "line" and len(c.categories) < 3:
        w.append(f"slide '{slide.id}': a line chart with {len(c.categories)} points "
                 "shows no trend - use bar_clustered or big_number instead.")
    if c.kind in ("bar_clustered", "bar_stacked") and len(c.categories) > 12:
        w.append(f"slide '{slide.id}': {len(c.categories)} categories is crowded for "
                 "columns - consider bar_horizontal or aggregating.")
    if not slide.insight:
        w.append(f"slide '{slide.id}': chart has no `insight:` - every chart should "
                 "state its 'so what' (see playbooks/data-storytelling.md).")
    if len(c.series) == 1 and len(c.categories) <= 2 and c.kind not in ("pie", "doughnut"):
        w.append(f"slide '{slide.id}': {len(c.categories)} value(s) in one series - "
                 "a big_number slide would land harder than a chart.")
    return w


_TOPIC_TITLES = {
    "update", "overview", "background", "status", "results", "data", "numbers",
    "agenda", "next steps", "summary", "introduction", "discussion",
}


# Phrases that make copy read machine-written. Each entry: (needle, advice).
# Kept short and high-confidence; these are warnings, not bans.
_AI_TELLS = [
    ("delve", "say 'look at' or just cut it"),
    ("seamless", "claim something concrete instead"),
    ("leverage", "say 'use'"),
    ("unlock", "say what actually becomes possible"),
    ("unleash", "tone it down"),
    ("empower", "name the specific new ability"),
    ("supercharge", "tone it down"),
    ("game-chang", "show the change with a number instead"),
    ("game chang", "show the change with a number instead"),
    ("cutting-edge", "date or benchmark the claim instead"),
    ("state-of-the-art", "date or benchmark the claim instead"),
    ("transformative", "describe the before/after instead"),
    ("revolutioniz", "describe the before/after instead"),
    ("holistic", "say which parts are covered"),
    ("synerg", "say who saves what"),
    ("paradigm", "plain words win"),
    ("embark", "say 'start'"),
    ("elevate ", "say 'improve' or name the metric"),
    ("harness the", "say 'use'"),
    ("ever-evolving", "cut the filler"),
    ("fast-paced world", "cut the filler"),
    ("in today's", "cut the filler opener"),
    ("it's not just", "make the positive claim directly"),
    ("isn't just", "make the positive claim directly"),
    ("not just about", "make the positive claim directly"),
]

# Slide fields that carry structural values, not prose.
_NON_PROSE_KEYS = {
    "id", "type", "variant", "icon", "kind", "number_format", "arrow",
    "sentiment", "status", "emphasize", "animate", "emphasize_col", "series",
    "point", "percent", "number", "done",
}


def _prose_strings(value, key: str = "") -> list[str]:
    if key in _NON_PROSE_KEYS:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [s for k, v in value.items() for s in _prose_strings(v, k)]
    if isinstance(value, list):
        return [s for v in value for s in _prose_strings(v, key)]
    return []


def _human_voice(slide) -> list[str]:
    w = []
    texts = _prose_strings(slide.model_dump(exclude_none=True))
    for text in texts:
        plain = strip_markup(text)
        if "—" in plain:
            w.append(f"slide '{slide.id}': em dash in \"{plain[:50]}\" - use a "
                     "spaced en dash (word – word) instead; em dashes read "
                     "as machine-written.")
        low = plain.lower()
        for needle, advice in _AI_TELLS:
            if needle in low:
                w.append(f"slide '{slide.id}': '{needle.strip()}' in "
                         f"\"{plain[:50]}\" reads like AI boilerplate - {advice}.")
                break  # one nudge per string is enough
    return w


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
