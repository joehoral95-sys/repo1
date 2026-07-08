from lxml import etree
from pptx import Presentation

P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"


def _timing_elements(pptx_path):
    prs = Presentation(str(pptx_path))
    return [sl._element.find(f"{{{P_NS}}}timing") for sl in prs.slides]


def test_animated_slides_have_timing(built_example, example_spec):
    timings = _timing_elements(built_example.output_path)
    for i, model in enumerate(example_spec.slides):
        if model.animate != "none":
            assert timings[i] is not None, f"slide '{model.id}' should have timing XML"
        else:
            assert timings[i] is None, f"slide '{model.id}' should NOT have timing XML"


def test_timing_xml_is_wellformed_and_targets_real_shapes(built_example):
    prs = Presentation(str(built_example.output_path))
    for slide in prs.slides:
        timing = slide._element.find(f"{{{P_NS}}}timing")
        if timing is None:
            continue
        # re-parse to prove well-formedness
        etree.fromstring(etree.tostring(timing))
        shape_ids = {str(sh.shape_id) for sh in slide.shapes}
        spids = {el.get("spid") for el in timing.iter(f"{{{P_NS}}}spTgt")}
        assert spids, "timing tree has no shape targets"
        assert spids <= shape_ids, f"timing targets unknown shapes: {spids - shape_ids}"


def test_no_animations_flag(example_spec, tmp_path):
    from deckstudio.engine.builder import build_deck

    result = build_deck(example_spec, output_dir=tmp_path, deck_name="noanim",
                        enable_animations=False)
    assert all(t is None for t in _timing_elements(result.output_path))


def test_deck_level_off_switch(example_spec, tmp_path):
    from deckstudio.engine.builder import build_deck

    spec = example_spec.model_copy(deep=True)
    spec.deck.animations = "off"
    result = build_deck(spec, output_dir=tmp_path, deck_name="off")
    assert all(t is None for t in _timing_elements(result.output_path))
