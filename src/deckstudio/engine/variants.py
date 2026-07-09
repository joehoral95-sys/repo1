"""Layout variants: every slide type has multiple named compositions.

Why: decks built from the same slide types shouldn't look like clones of
each other. Each renderer implements the variants listed here; the engine
picks a DETERMINISTIC default per deck (hashed from the deck title), so two
different decks naturally land on different compositions — and any slide
can override with `variant:` in the spec.

The combinatorial space (products of per-type variants across a deck) runs
to hundreds of thousands of distinct deck appearances.
"""

from __future__ import annotations

import hashlib

# First entry = canonical look; order matters only for documentation.
VARIANTS: dict[str, list[str]] = {
    "title": ["band", "band-left", "watermark", "minimal"],
    "section": ["chip", "giant", "band", "minimal"],
    "agenda": ["band", "list", "grid"],
    "big_number": ["cards", "uniform", "dark"],
    "chart": ["exhibit", "panel-left", "strip"],
    "comparison": ["panels", "open"],
    "icon_row": ["centered", "rows"],
    "quote": ["card", "dark", "light"],
    "table": ["banded", "open"],
    "timeline": ["spine", "vertical"],
    "content": ["bullets", "columns", "numbered"],
    "progress": ["rings", "bars"],
    "thanks": ["circle", "band", "minimal"],
}


def resolve_variant(slide_type: str, requested: str | None, deck_title: str,
                    warn=None) -> str:
    """Return the variant to render: the requested one if valid, else a
    deck-deterministic default (same spec always builds the same deck)."""
    options = VARIANTS.get(slide_type)
    if not options:
        return "default"
    if requested:
        if requested in options:
            return requested
        if warn:
            warn(f"unknown variant '{requested}' for {slide_type} "
                 f"(options: {options}) — using a deck default")
    digest = hashlib.md5(f"{deck_title}::{slide_type}".encode()).hexdigest()
    return options[int(digest, 16) % len(options)]
