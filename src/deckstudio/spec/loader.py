"""Load and validate a spec.yaml, producing friendly, line-anchored errors.

Error messages are written for an LLM (or Joe) to self-correct from:
they name the slide id, the field, and what to do about it.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError
from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError

from .schema import DeckSpec


class SpecError(Exception):
    """A spec problem with a human/LLM-friendly message."""


@dataclass
class LoadedSpec:
    spec: DeckSpec
    path: Path
    raw: dict


def _loc_to_message(err: dict, raw: dict) -> str:
    loc = err["loc"]
    msg = err["msg"]
    # Anchor errors to the slide id instead of a list index where possible.
    if len(loc) >= 2 and loc[0] == "slides" and isinstance(loc[1], int):
        idx = loc[1]
        slide_id = None
        slides = raw.get("slides")
        if isinstance(slides, list) and idx < len(slides) and isinstance(slides[idx], dict):
            slide_id = slides[idx].get("id")
        where = f"slide '{slide_id}'" if slide_id else f"slide #{idx + 1}"
        rest = ".".join(str(p) for p in loc[2:])
        field = f" field '{rest}'" if rest else ""
        return f"{where}{field}: {msg}"
    return f"{'.'.join(str(p) for p in loc)}: {msg}"


def load_spec(path: Path | str) -> LoadedSpec:
    path = Path(path)
    if path.is_dir():
        path = path / "spec.yaml"
    if not path.exists():
        raise SpecError(f"No spec found at {path}. Create it with `deckstudio new <name>`.")

    yaml = YAML(typ="safe")
    try:
        with path.open("r", encoding="utf-8") as f:
            raw = yaml.load(f)
    except YAMLError as e:
        raise SpecError(f"{path} is not valid YAML:\n{e}") from e

    if not isinstance(raw, dict):
        raise SpecError(f"{path} must be a YAML mapping with top-level keys 'deck' and 'slides'.")

    try:
        spec = DeckSpec.model_validate(raw)
    except ValidationError as e:
        lines = [_loc_to_message(err, raw) for err in e.errors()]
        bullet = "\n  - ".join(lines)
        raise SpecError(
            f"{path} failed validation ({len(lines)} problem{'s' if len(lines) != 1 else ''}):\n"
            f"  - {bullet}"
        ) from e

    return LoadedSpec(spec=spec, path=path, raw=raw)
