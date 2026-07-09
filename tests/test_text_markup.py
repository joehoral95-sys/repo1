from deckstudio.engine.text import adaptive_pt, parse_markup, strip_markup


def test_plain():
    segs = parse_markup("hello world")
    assert len(segs) == 1 and not segs[0].bold and not segs[0].accent


def test_bold():
    segs = parse_markup("save **$0.9M** next year")
    assert [s.text for s in segs] == ["save ", "$0.9M", " next year"]
    assert [s.bold for s in segs] == [False, True, False]


def test_accent():
    segs = parse_markup("[accent]66%[/accent] of candidates")
    assert segs[0].accent and segs[0].text == "66%"


def test_mixed():
    segs = parse_markup("**bold** and [accent]blue[/accent]")
    assert [(s.text, s.bold, s.accent) for s in segs] == [
        ("bold", True, False), (" and ", False, False), ("blue", False, True)]


def test_strip():
    assert strip_markup("**a** [accent]b[/accent] c") == "a b c"


TIERS = [(12, 18), (20, 16)]


def test_adaptive_short_labels_scale_up():
    assert adaptive_pt(14, ["Kickoff", "Launch"], TIERS) == 18


def test_adaptive_medium_labels_scale_a_little():
    assert adaptive_pt(14, ["Kickoff", "Board approval day"], TIERS) == 16


def test_adaptive_long_labels_stay_at_base():
    assert adaptive_pt(14, ["A milestone label well past twenty chars"], TIERS) == 14


def test_adaptive_never_below_base():
    # a tier smaller than the base is clamped up, never down
    assert adaptive_pt(14, ["hi"], [(10, 12)]) == 14


def test_adaptive_counts_stripped_markup():
    # "**Launch day**" is 14 raw chars but 10 stripped -> shortest tier
    assert adaptive_pt(14, ["**Launch day**"], TIERS) == 18


def test_adaptive_accepts_single_string():
    assert adaptive_pt(14, "Go", TIERS) == 18
