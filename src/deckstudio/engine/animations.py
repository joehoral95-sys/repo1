"""Tasteful, contained PowerPoint animations via p:timing OOXML injection.

Exactly two recipes, both entrance fades (presetID 10 — PowerPoint's "Fade"):

  fade  — all content shapes fade in automatically when the slide appears,
          with a subtle 120ms cascade.
  build — content shapes appear one per click, in z-order (the order
          renderers created them), so the presenter reveals the story.

Rules that keep this safe:
- Only shapes BELOW the title band (top >= 1.3in) animate; titles and the
  footer never do.
- Any failure raises to the builder, which logs a warning and ships the
  deck without animation. Animation can never break a build.
- `--no-animations` at the CLI (or `deck.animations: off` in the spec)
  bypasses this module entirely.
"""

from __future__ import annotations

from lxml import etree
from pptx.util import Emu

NSMAP_P = "http://schemas.openxmlformats.org/presentationml/2006/main"
P = f"{{{NSMAP_P}}}"

CONTENT_TOP_EMU = Emu(int(1.3 * 914400))
FADE_MS = 400
CASCADE_MS = 120
MAX_CLICKS = 3  # a build slide never needs more than 3 clicks to show everything


def _chunk(shape_ids: list[int], n_groups: int) -> list[list[int]]:
    """Split shapes into at most n_groups contiguous chunks. Shape ids are in
    creation (z) order, which renderers emit column-by-column / card-by-card,
    so contiguous chunks correspond to visual groups."""
    n = min(n_groups, len(shape_ids))
    base, extra = divmod(len(shape_ids), n)
    chunks, start = [], 0
    for i in range(n):
        size = base + (1 if i < extra else 0)
        chunks.append(shape_ids[start:start + size])
        start += size
    return chunks


def apply(slide, mode: str) -> None:
    """Inject a p:timing tree animating the slide's content shapes."""
    shape_ids = _content_shape_ids(slide)
    if not shape_ids:
        return
    _remove_existing_timing(slide)
    timing = _build_timing(shape_ids, mode)
    slide._element.append(timing)


def _content_shape_ids(slide) -> list[int]:
    ids = []
    for shape in slide.shapes:
        try:
            if shape.top is not None and shape.top >= CONTENT_TOP_EMU:
                ids.append(shape.shape_id)
        except (AttributeError, TypeError):
            continue
    return ids


def _remove_existing_timing(slide) -> None:
    for el in slide._element.findall(f"{P}timing"):
        slide._element.remove(el)


class _Ids:
    def __init__(self):
        self._n = 0

    def next(self) -> str:
        self._n += 1
        return str(self._n)


def _build_timing(shape_ids: list[int], mode: str) -> etree._Element:
    ids = _Ids()
    timing = etree.SubElement(etree.Element(f"{P}_root"), f"{P}timing")
    tnLst = etree.SubElement(timing, f"{P}tnLst")
    root_par = etree.SubElement(tnLst, f"{P}par")
    root_ctn = etree.SubElement(root_par, f"{P}cTn")
    root_ctn.set("id", ids.next())
    root_ctn.set("dur", "indefinite")
    root_ctn.set("restart", "never")
    root_ctn.set("nodeType", "tmRoot")
    root_children = etree.SubElement(root_ctn, f"{P}childTnLst")

    seq = etree.SubElement(root_children, f"{P}seq")
    seq.set("concurrent", "1")
    seq.set("nextAc", "seek")
    main_ctn = etree.SubElement(seq, f"{P}cTn")
    main_id = ids.next()
    main_ctn.set("id", main_id)
    main_ctn.set("dur", "indefinite")
    main_ctn.set("nodeType", "mainSeq")
    main_children = etree.SubElement(main_ctn, f"{P}childTnLst")

    if mode == "fade":
        # One group, auto-started when the slide appears; shapes cascade.
        effects = [
            (spid, "withEffect" if i else "afterEffect", i * CASCADE_MS)
            for i, spid in enumerate(shape_ids)
        ]
        main_children.append(_group(ids, effects, auto_start=True, main_seq_id=main_id))
    elif mode == "build":
        # AT MOST 3 clicks per slide: shapes are chunked into up to 3 click
        # groups (a whole card/column per click), cascading within each group.
        for chunk in _chunk(shape_ids, MAX_CLICKS):
            effects = [
                (spid, "clickEffect" if i == 0 else "withEffect", i * CASCADE_MS)
                for i, spid in enumerate(chunk)
            ]
            main_children.append(
                _group(ids, effects, auto_start=False, main_seq_id=main_id))
    else:
        raise ValueError(f"unknown animation mode '{mode}'")

    _seq_conditions(seq)
    return timing


def _group(ids: _Ids, effects: list[tuple[int, str, int]], *,
           auto_start: bool, main_seq_id: str) -> etree._Element:
    """A top-level animation group (one click, or one automatic burst)."""
    outer_par = etree.Element(f"{P}par")
    outer_ctn = etree.SubElement(outer_par, f"{P}cTn")
    outer_ctn.set("id", ids.next())
    outer_ctn.set("fill", "hold")
    st = etree.SubElement(outer_ctn, f"{P}stCondLst")
    cond = etree.SubElement(st, f"{P}cond")
    cond.set("delay", "indefinite")
    if auto_start:
        # Also start when the main sequence begins (i.e., on slide entry).
        cond2 = etree.SubElement(st, f"{P}cond")
        cond2.set("evt", "onBegin")
        cond2.set("delay", "0")
        tn = etree.SubElement(cond2, f"{P}tn")
        tn.set("val", main_seq_id)
    outer_children = etree.SubElement(outer_ctn, f"{P}childTnLst")

    mid_par = etree.SubElement(outer_children, f"{P}par")
    mid_ctn = etree.SubElement(mid_par, f"{P}cTn")
    mid_ctn.set("id", ids.next())
    mid_ctn.set("fill", "hold")
    mid_st = etree.SubElement(mid_ctn, f"{P}stCondLst")
    mid_cond = etree.SubElement(mid_st, f"{P}cond")
    mid_cond.set("delay", "0")
    mid_children = etree.SubElement(mid_ctn, f"{P}childTnLst")

    for spid, node_type, delay_ms in effects:
        mid_children.append(_fade_effect(ids, spid, node_type, delay_ms))
    return outer_par


def _fade_effect(ids: _Ids, spid: int, node_type: str, delay_ms: int) -> etree._Element:
    par = etree.Element(f"{P}par")
    ctn = etree.SubElement(par, f"{P}cTn")
    ctn.set("id", ids.next())
    ctn.set("presetID", "10")           # Fade
    ctn.set("presetClass", "entr")
    ctn.set("presetSubtype", "0")
    ctn.set("fill", "hold")
    ctn.set("grpId", "0")
    ctn.set("nodeType", node_type)
    st = etree.SubElement(ctn, f"{P}stCondLst")
    cond = etree.SubElement(st, f"{P}cond")
    cond.set("delay", str(delay_ms))
    children = etree.SubElement(ctn, f"{P}childTnLst")

    # 1) set visibility -> visible
    set_el = etree.SubElement(children, f"{P}set")
    set_bhvr = etree.SubElement(set_el, f"{P}cBhvr")
    set_ctn = etree.SubElement(set_bhvr, f"{P}cTn")
    set_ctn.set("id", ids.next())
    set_ctn.set("dur", "1")
    set_ctn.set("fill", "hold")
    set_st = etree.SubElement(set_ctn, f"{P}stCondLst")
    set_cond = etree.SubElement(set_st, f"{P}cond")
    set_cond.set("delay", "0")
    _target(set_bhvr, spid)
    attrs = etree.SubElement(set_bhvr, f"{P}attrNameLst")
    attr = etree.SubElement(attrs, f"{P}attrName")
    attr.text = "style.visibility"
    to = etree.SubElement(set_el, f"{P}to")
    val = etree.SubElement(to, f"{P}strVal")
    val.set("val", "visible")

    # 2) the fade itself
    anim = etree.SubElement(children, f"{P}animEffect")
    anim.set("transition", "in")
    anim.set("filter", "fade")
    anim_bhvr = etree.SubElement(anim, f"{P}cBhvr")
    anim_ctn = etree.SubElement(anim_bhvr, f"{P}cTn")
    anim_ctn.set("id", ids.next())
    anim_ctn.set("dur", str(FADE_MS))
    _target(anim_bhvr, spid)
    return par


def _target(bhvr: etree._Element, spid: int) -> None:
    tgt = etree.SubElement(bhvr, f"{P}tgtEl")
    sp = etree.SubElement(tgt, f"{P}spTgt")
    sp.set("spid", str(spid))


def _seq_conditions(seq: etree._Element) -> None:
    prev = etree.SubElement(seq, f"{P}prevCondLst")
    pcond = etree.SubElement(prev, f"{P}cond")
    pcond.set("evt", "onPrev")
    pcond.set("delay", "0")
    ptgt = etree.SubElement(pcond, f"{P}tgtEl")
    etree.SubElement(ptgt, f"{P}sldTgt")
    nxt = etree.SubElement(seq, f"{P}nextCondLst")
    ncond = etree.SubElement(nxt, f"{P}cond")
    ncond.set("evt", "onNext")
    ncond.set("delay", "0")
    ntgt = etree.SubElement(ncond, f"{P}tgtEl")
    etree.SubElement(ntgt, f"{P}sldTgt")
