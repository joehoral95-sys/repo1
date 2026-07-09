"""Layout variants: composition × chrome, chosen smartly.

Two axes:
- **composition** — how the slide's content is arranged (per type below).
- **chrome** — how the title band is treated (`left`, `centered`, `banner`,
  `tint`) for the eight standard-chrome types.

A variant string is `composition` for full-bleed types and
`composition/chrome` for chrome types (a bare composition is accepted and
the chrome is auto-picked). 101 variants total.

Selection is SMART, not random: `smart_candidates` filters to compositions
that suit the actual content (long timeline labels need the vertical rail;
four stat cards crowd a hero; wordy icon rows read better stacked...), and
a deck-seeded hash breaks the remaining tie deterministically — so choices
are justified AND different decks still look different.
"""

from __future__ import annotations

import hashlib

CHROMES = ["left", "centered", "banner", "tint"]

COMPOSITIONS: dict[str, list[str]] = {
    # full-bleed types: variant == composition
    "title": ["band", "band-left", "watermark", "minimal"],
    "section": ["chip", "giant", "band", "minimal"],
    "agenda": ["band", "list", "grid"],
    "quote": ["card", "dark", "light"],
    "thanks": ["circle", "band", "minimal"],
    # chrome types: variant == composition/chrome
    "big_number": ["cards", "uniform", "dark"],
    "chart": ["exhibit", "panel-left", "strip"],
    "comparison": ["panels", "open"],
    "icon_row": ["columns", "rows", "cards"],
    "table": ["banded", "open"],
    "timeline": ["spine", "vertical"],
    "content": ["bullets", "columns", "numbered", "cards"],
    "progress": ["rings", "bars"],
}

CHROME_TYPES = {"big_number", "chart", "comparison", "icon_row", "table",
                "timeline", "content", "progress"}

# legacy names from earlier specs
LEGACY = {"icon_row": {"centered": "columns"}}

VARIANTS: dict[str, list[str]] = {
    t: ([f"{c}/{ch}" for c in comps for ch in CHROMES]
        if t in CHROME_TYPES else list(comps))
    for t, comps in COMPOSITIONS.items()
}

TOTAL_VARIANTS = sum(len(v) for v in VARIANTS.values())


def _pick(options: list[str], *keys: str) -> str:
    digest = hashlib.md5("::".join(keys).encode()).hexdigest()
    return options[int(digest, 16) % len(options)]


def split_variant(slide_type: str, variant: str) -> tuple[str, str]:
    """-> (composition, chrome). Chrome is 'left' for full-bleed types."""
    if "/" in variant:
        comp, chrome = variant.split("/", 1)
        return comp, chrome
    return variant, "left"


def resolve_variant(slide_type: str, requested: str | None, deck_title: str,
                    model=None, warn=None) -> str:
    """The variant to render.

    Priority: explicit request (with legacy/bare-composition tolerance) →
    smart content-aware candidates → deck-seeded deterministic pick."""
    comps = COMPOSITIONS.get(slide_type)
    if not comps:
        return "default"
    is_chrome = slide_type in CHROME_TYPES

    if requested:
        comp, _, chrome = requested.partition("/")
        comp = LEGACY.get(slide_type, {}).get(comp, comp)
        if comp in comps:
            if not is_chrome:
                return comp
            if chrome in CHROMES:
                return f"{comp}/{chrome}"
            chrome_opts = smart_chromes(slide_type, comp, model)
            return f"{comp}/{_pick(chrome_opts, deck_title, slide_type, 'chrome')}"
        if warn:
            warn(f"unknown variant '{requested}' for {slide_type} "
                 f"(compositions: {comps}) — using a smart default")

    comp_opts = smart_candidates(slide_type, model) or comps
    slide_id = getattr(model, "id", "") if model is not None else ""
    comp = _pick(comp_opts, deck_title, slide_type, slide_id)
    if not is_chrome:
        return comp
    # chrome is consistent per (deck, type) so e.g. all charts in one deck
    # share a title treatment
    chrome = _pick(smart_chromes(slide_type, comp, model),
                   deck_title, slide_type, "chrome")
    return f"{comp}/{chrome}"


def smart_candidates(slide_type: str, model) -> list[str]:
    """Compositions that SUIT this slide's content. Empty = no opinion."""
    comps = COMPOSITIONS[slide_type]
    if model is None:
        return comps

    if slide_type == "timeline":
        ms = getattr(model, "milestones", [])
        if len(ms) > 4 or any(len(m.label) > 28 for m in ms):
            return ["vertical"]
        return comps

    if slide_type == "big_number":
        stats = getattr(model, "stats", [])
        if len(stats) >= 4:
            return ["uniform", "dark"]   # a hero card crowds a 4-up row
        return comps

    if slide_type == "icon_row":
        items = getattr(model, "items", [])
        if any(len(i.text) > 90 for i in items):
            return ["rows"]              # long text needs the stacked layout
        if len(items) == 4:
            return ["cards", "rows"]     # 4 columns get cramped
        return comps

    if slide_type == "chart":
        chart = getattr(model, "chart", None)
        insight = getattr(model, "insight", None)
        if not insight:
            return comps                 # renderer goes full-width anyway
        if chart is not None and len(chart.categories) >= 6:
            return ["strip"]             # wide data wants the full width
        if len(insight) > 150:
            return ["exhibit", "panel-left"]  # long takeaway needs the panel
        return comps

    if slide_type == "content":
        bullets = getattr(model, "bullets", [])
        has_sub = any(not isinstance(b, str) and getattr(b, "sub", None)
                      for b in bullets)
        if has_sub:
            return ["bullets", "columns"]     # numbered/cards drop sub-points
        texts = [b if isinstance(b, str) else b.text for b in bullets]
        if len(texts) >= 5 and all(len(t) <= 60 for t in texts):
            return ["numbered", "cards", "columns"]
        if len(texts) <= 2:
            return ["bullets", "numbered"]    # grids look empty at 1-2 items
        return comps

    if slide_type == "comparison":
        total = len(model.left.bullets) + len(model.right.bullets)
        if total >= 8:
            return ["panels"]            # fills keep dense content organized
        return comps

    if slide_type == "table":
        if len(getattr(model, "rows", [])) >= 6:
            return ["banded"]            # stripes aid row tracking
        return comps

    if slide_type == "progress":
        n = len(getattr(model, "items", []))
        if n >= 4:
            return ["bars"]              # four rings shrink too far
        if n == 1:
            return ["rings"]
        return comps

    if slide_type == "section":
        if getattr(model, "preview", None):
            return ["chip", "band"]      # compositions built for the preview
        return comps

    if slide_type == "agenda":
        if len(getattr(model, "items", [])) >= 5:
            return ["band", "list"]      # a 5-6 item grid gets cramped
        return comps

    if slide_type == "quote":
        if len(getattr(model, "text", "")) > 180:
            return ["card"]              # the card wraps long quotes best
        return comps

    return comps


def smart_chromes(slide_type: str, composition: str, model) -> list[str]:
    """Chrome styles that suit the composition."""
    if slide_type == "chart" and composition in ("exhibit", "panel-left"):
        # the navy takeaway panel + a navy banner is two heavy blocks
        return ["left", "centered", "tint"]
    if slide_type == "big_number" and composition == "dark":
        return ["left", "centered", "tint"]
    if slide_type == "comparison":
        return ["left", "banner", "tint"]  # centered title over 2 panels drifts
    return list(CHROMES)
