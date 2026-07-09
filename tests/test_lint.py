from deckstudio.spec.schema import DeckSpec
from deckstudio.validate.spec_lint import lint


def make(slides, audience="Board", intent="Approve X"):
    return DeckSpec.model_validate({
        "deck": {"title": "T", "audience": audience, "intent": intent},
        "slides": [{"id": "cover", "type": "title", "title": "Assertion here"}] + slides,
    })


def test_clean_example_deck_has_no_warnings(example_spec):
    assert lint(example_spec) == []


def test_topic_title_flagged():
    spec = make([{"id": "u", "type": "content", "title": "Update",
                  "bullets": ["a point"]}])
    assert any("topic label, not an assertion" in w for w in lint(spec))


def test_missing_audience_flagged():
    spec = make([], audience=None)
    assert any("audience/intent missing" in w for w in lint(spec))


def test_chart_without_insight_flagged():
    spec = make([{
        "id": "c", "type": "chart", "title": "Prelims dipped 7% in Q2",
        "chart": {"kind": "bar_clustered", "categories": ["Q1", "Q2", "Q3"],
                  "series": [{"name": "s", "values": [1, 2, 3]},
                             {"name": "t", "values": [2, 3, 4]}]},
    }])
    assert any("no `insight:`" in w for w in lint(spec))


def test_two_point_line_chart_flagged():
    spec = make([{
        "id": "c", "type": "chart", "title": "Membership rose again this quarter",
        "chart": {"kind": "line", "categories": ["Q1", "Q2"],
                  "series": [{"name": "s", "values": [1, 2]},
                             {"name": "t", "values": [2, 3]}]},
        "insight": "so what",
    }])
    assert any("shows no trend" in w for w in lint(spec))


def test_wall_of_bullets_flagged():
    long_bullet = "word " * 25
    spec = make([{"id": "w", "type": "content", "title": "We must invest in universities",
                  "bullets": [long_bullet.strip()] * 3}])
    assert any("slides aren't documents" in w.lower() for w in lint(spec))


def test_em_dash_flagged():
    spec = make([{"id": "d", "type": "content", "title": "Costs rose 12% since 2024",
                  "bullets": ["Vendor costs — the largest line — rose again"]}])
    assert any("em dash" in w for w in lint(spec))


def test_ai_boilerplate_flagged():
    spec = make([{"id": "a", "type": "content", "title": "We must leverage synergies",
                  "bullets": ["Seamlessly unlock game-changing value"]}])
    warns = [w for w in lint(spec) if "AI boilerplate" in w]
    assert len(warns) >= 2  # title and bullet each get one nudge


def test_plain_business_copy_not_flagged():
    spec = make([{"id": "ok", "type": "content", "title": "Fees sit 8% below peers",
                  "bullets": ["Raising 4% covers proctoring costs",
                              "Members told us price is not the barrier"]}])
    assert not any("AI boilerplate" in w or "em dash" in w for w in lint(spec))


def test_bullet_slide_run_flagged():
    slides = [
        {"id": f"b{i}", "type": "content", "title": f"Assertion number {i} here",
         "bullets": ["a point"]}
        for i in range(3)
    ]
    assert any("visual rhythm" in w for w in lint(make(slides)))
