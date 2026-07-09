"""Every (slide type, variant) combination must build cleanly."""

import pytest

from deckstudio.engine.builder import build_deck
from deckstudio.engine.variants import VARIANTS, resolve_variant
from deckstudio.spec.schema import DeckSpec

SAMPLE_SLIDES = {
    "title": {"title": "A Title That Asserts", "subtitle": "sub", "presenter": "p"},
    "section": {"title": "Chapter", "number": 2, "subtitle": "sub",
                "preview": [{"label": "Metric", "value": "1", "status": "on_track"},
                            {"label": "Other", "value": "2", "status": "watch"}]},
    "agenda": {"items": ["First topic", "Second topic", "Third topic",
                         "Fourth topic", "Fifth topic"]},
    "big_number": {"title": "Numbers rose again", "stats": [
        {"value": "1", "label": "one", "status": "on_track", "target": "t"},
        {"value": "2", "label": "two", "delta": "+1", "arrow": "up",
         "sentiment": "good"},
        {"value": "3", "label": "three"}]},
    "chart": {"title": "The trend held through Q4", "insight": "so what",
              "source": "somewhere",
              "chart": {"kind": "bar_clustered", "categories": ["a", "b", "c"],
                        "series": [{"name": "s", "values": [1, 2, 3]}],
                        "highlight": {"series": "s", "point": 2}}},
    "comparison": {"title": "Two ways forward", "emphasize": "right",
                   "badge": "Recommended",
                   "left": {"heading": "A", "bullets": ["one", "two"]},
                   "right": {"heading": "B", "bullets": ["three", "four"]}},
    "icon_row": {"title": "Three reasons now", "items": [
        {"icon": "growth", "heading": "One", "text": "text one"},
        {"heading": "Two", "text": "text two"},
        {"icon": "people", "heading": "Three", "text": "text three"}]},
    "quote": {"text": "A statement worth a whole slide.", "attribution": "who"},
    "table": {"title": "Values compared cleanly",
              "columns": ["A", "B"], "rows": [["1", "2"], ["3", "4"], ["5", "6"]],
              "emphasize_col": 1},
    "timeline": {"title": "Milestones through the year", "milestones": [
        {"label": "A milestone with a fairly long label", "date": "Jan", "done": True},
        {"label": "Next", "date": "Jun"},
        {"label": "Later", "date": "Dec"}]},
    "content": {"title": "Points made plainly", "bullets": [
        "first point", "second point", "third point", "fourth point"]},
    "progress": {"title": "How far along we are", "caption": "as of now",
                 "items": [{"label": "One", "percent": 80},
                           {"label": "Two", "percent": 35}]},
    "thanks": {"message": "msg", "contact": "who@where"},
}

CASES = [(t, v) for t, vs in VARIANTS.items() for v in vs]


@pytest.mark.parametrize("slide_type,variant", CASES)
def test_variant_builds(slide_type, variant, tmp_path):
    body = dict(SAMPLE_SLIDES[slide_type])
    body.update({"id": "s1", "type": slide_type, "variant": variant})
    spec = DeckSpec.model_validate({
        "deck": {"title": "Variant Matrix", "audience": "a", "intent": "i",
                 "animations": "off"},
        "slides": [body],
    })
    result = build_deck(spec, output_dir=tmp_path, deck_name=f"{slide_type}-{variant}")
    assert result.output_path.exists()
    assert result.warnings == [], result.warnings


def test_unknown_variant_falls_back_with_warning():
    warnings = []
    v = resolve_variant("quote", "sideways", "Some Deck", warn=warnings.append)
    assert v in VARIANTS["quote"]
    assert warnings and "unknown variant" in warnings[0]


def test_defaults_differ_across_decks():
    """Different deck titles should not all land on identical variant picks."""
    picks_a = tuple(resolve_variant(t, None, "Deck Alpha") for t in VARIANTS)
    picks_b = tuple(resolve_variant(t, None, "Deck Bravo") for t in VARIANTS)
    picks_c = tuple(resolve_variant(t, None, "Deck Charlie") for t in VARIANTS)
    assert len({picks_a, picks_b, picks_c}) >= 2
