from deckstudio.engine.text import parse_markup, strip_markup


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
