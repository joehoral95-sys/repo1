#!/usr/bin/env bash
# SOA Deck Studio — one-time setup for macOS/Linux/CI.
set -euo pipefail

if command -v uv >/dev/null 2>&1; then
  uv venv .venv --quiet 2>/dev/null || true
  uv pip install --quiet -e ".[dev]" --python .venv/bin/python
else
  python3 -m venv .venv
  .venv/bin/python -m pip install --quiet --upgrade pip
  .venv/bin/python -m pip install --quiet -e ".[dev]"
fi

.venv/bin/deckstudio doctor || true
echo
echo "Done. Open this folder in Cursor and ask for a deck (see README.md)."
