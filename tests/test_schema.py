import pytest
from pydantic import ValidationError

from deckstudio.spec.schema import DeckSpec

BASE = {
    "deck": {"title": "T", "audience": "a", "intent": "i"},
    "slides": [{"id": "cover", "type": "title", "title": "Hello"}],
}


def make(slides):
    return {"deck": BASE["deck"], "slides": slides}


def test_valid_minimal():
    spec = DeckSpec.model_validate(BASE)
    assert spec.slides[0].type == "title"


def test_duplicate_ids_rejected():
    slides = [
        {"id": "a", "type": "title", "title": "x"},
        {"id": "a", "type": "quote", "text": "y"},
    ]
    with pytest.raises(ValidationError, match="duplicate slide id"):
        DeckSpec.model_validate(make(slides))


def test_chart_series_length_mismatch_teaches():
    slides = [{
        "id": "c", "type": "chart", "title": "Numbers went up in Q2",
        "chart": {
            "kind": "line",
            "categories": ["Q1", "Q2", "Q3"],
            "series": [{"name": "Members", "values": [1, 2]}],
        },
    }]
    with pytest.raises(ValidationError, match="2 values but there are 3 categories"):
        DeckSpec.model_validate(make(slides))


def test_pie_max_slices():
    slides = [{
        "id": "p", "type": "chart", "title": "Mix shifted toward universities",
        "chart": {
            "kind": "pie",
            "categories": [f"c{i}" for i in range(7)],
            "series": [{"name": "s", "values": [1] * 7}],
        },
    }]
    with pytest.raises(ValidationError, match="unreadable"):
        DeckSpec.model_validate(make(slides))


def test_highlight_must_reference_existing_series():
    slides = [{
        "id": "c", "type": "chart", "title": "Prelims dipped in Q2",
        "chart": {
            "kind": "bar_clustered",
            "categories": ["Q1", "Q2"],
            "series": [{"name": "Prelims", "values": [1, 2]}],
            "highlight": {"series": "Fellowship", "point": 0},
        },
    }]
    with pytest.raises(ValidationError, match="not found"):
        DeckSpec.model_validate(make(slides))


def test_long_bullet_rejected_with_guidance():
    slides = [{
        "id": "b", "type": "content", "title": "We should cut costs now",
        "bullets": ["x" * 200],
    }]
    with pytest.raises(ValidationError, match="move detail to speaker notes"):
        DeckSpec.model_validate(make(slides))


def test_stats_capped_at_four():
    stat = {"value": "1", "label": "l"}
    slides = [{"id": "s", "type": "big_number", "title": "Growth continued in Q2",
               "stats": [stat] * 5}]
    with pytest.raises(ValidationError):
        DeckSpec.model_validate(make(slides))


def test_table_row_width_checked():
    slides = [{
        "id": "t", "type": "table", "title": "P and FM carry the dip",
        "columns": ["a", "b"],
        "rows": [["1", "2", "3"]],
    }]
    with pytest.raises(ValidationError, match="3 cells but there are 2 columns"):
        DeckSpec.model_validate(make(slides))


def test_unknown_fields_rejected():
    slides = [{"id": "x", "type": "title", "title": "T", "color": "red"}]
    with pytest.raises(ValidationError):
        DeckSpec.model_validate(make(slides))
