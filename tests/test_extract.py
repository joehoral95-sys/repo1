"""Beautify path: extracting a deck the engine built recovers its content."""

from deckstudio.ingest.pptx_extract import extract_pptx


def test_extract_round_trip(built_example, example_spec, tmp_path):
    deck_dir = tmp_path / "beautify"
    yaml_path, report_path = extract_pptx(built_example.output_path, deck_dir)
    assert yaml_path.exists() and report_path.exists()

    from ruamel.yaml import YAML

    raw = YAML(typ="safe").load(yaml_path.read_text(encoding="utf-8"))
    assert len(raw["slides"]) == len(example_spec.slides)

    # Native charts port losslessly: find the extracted bar chart
    chart_slides = [s for s in raw["slides"] if s.get("type") == "chart"]
    assert len(chart_slides) == 2
    bar = next(s for s in chart_slides if s["chart"]["kind"] == "bar_clustered")
    assert bar["chart"]["categories"] == ["Q3 25", "Q4 25", "Q1 26", "Q2 26"]
    prelim = next(se for se in bar["chart"]["series"] if "Prelim" in se["name"])
    assert prelim["values"] == [8120.0, 8340.0, 7980.0, 7410.0]

    # Table content ports
    table_slides = [s for s in raw["slides"] if s.get("type") == "table"]
    assert len(table_slides) == 1
    assert table_slides[0]["columns"][0] == "Exam"

    # Speaker notes survive
    noted = [s for s in raw["slides"] if s.get("notes")]
    assert noted, "speaker notes should be extracted"


def test_extracted_yaml_is_structurally_sound(built_example, tmp_path):
    """The draft spec is a starting point the agent must redesign, not build
    as-is — dense slides may exceed design limits (e.g. >6 bullets), and that's
    fine. But it must be parseable YAML with ids/types, and any validation
    errors must be design-limit errors, never structural ones."""
    from pydantic import ValidationError

    from deckstudio.spec.schema import DeckSpec

    deck_dir = tmp_path / "beautify2"
    yaml_path, _ = extract_pptx(built_example.output_path, deck_dir)

    from ruamel.yaml import YAML

    raw = YAML(typ="safe").load(yaml_path.read_text(encoding="utf-8"))
    raw["deck"]["audience"] = raw["deck"]["intent"] = "someone"
    assert all("id" in s and "type" in s for s in raw["slides"])
    try:
        DeckSpec.model_validate(raw)
    except ValidationError as e:
        for err in e.errors():
            assert "at most" in err["msg"] or "at least" in err["msg"], (
                f"unexpected structural error in extracted draft: {err}")
