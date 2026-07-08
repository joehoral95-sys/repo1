from pathlib import Path

import pytest

from deckstudio.spec.loader import load_spec
from deckstudio.tokens import load_tokens

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_DECK = REPO_ROOT / "decks" / "_example-quarterly"


@pytest.fixture(scope="session")
def tokens():
    return load_tokens()


@pytest.fixture(scope="session")
def example_spec():
    return load_spec(EXAMPLE_DECK).spec


@pytest.fixture(scope="session")
def built_example(tmp_path_factory, example_spec):
    """Build the golden deck once for the whole session; return its path."""
    from deckstudio.engine.builder import build_deck

    out_dir = tmp_path_factory.mktemp("golden")
    result = build_deck(example_spec, output_dir=out_dir, deck_name="golden")
    return result
