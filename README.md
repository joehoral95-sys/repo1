# SOA Deck Studio

Turn whatever you have – a rough PowerPoint, Word docs, spreadsheets, a few
notes – into a polished, on-brand SOA presentation. Built for Joe; driven by
the AI agent in Cursor; no coding required.

## For Joe: how to use it

**One-time setup** (5 minutes):
1. Install [Cursor](https://cursor.com) and open this folder in it.
2. In Cursor's terminal, run: `.\setup.ps1`
   (it installs everything and checks your machine).

**Making a deck:**
1. Drop your files into the `inbox/` folder – an old deck to beautify,
   Word/PDF/Excel source material, anything.
2. Open Cursor's chat and say what you want, for example:
   > "Make a deck from the files in inbox for the July board meeting.
   > Audience is the Board; we need them to approve the exam-fee proposal."
3. The agent will ask a question or two, show you an outline, then build.
   Your deck appears in `output/` (e.g. `q3-board-update_v1.pptx`).
4. Want changes? Just say so: *"Make slide 3 punchier"*, *"the member count
   changed to 33,500"*, *"add a slide about the new study platform."*
   Each rebuild is a new file – your old versions are never touched.

**Editing decks yourself:** everything is real PowerPoint – text is text, and
charts are live: right-click a chart → **Edit Data**, change a number, and
the graph updates. No images of charts, ever.

## What's in the box

| Path | What it is |
|---|---|
| `AGENTS.md` | The step-by-step protocol the AI agent follows |
| `playbooks/` | Distilled best practices: communication, data-viz, insight-finding |
| `brand/tokens.yaml` | The brand: colors, fonts, sizes (single source of truth) |
| `brand/BRAND_INTAKE.md` | Checklist for loading the real SOA brand assets |
| `src/deckstudio/` | The Python engine that compiles specs into .pptx |
| `decks/` | One folder per deck: the editable spec + brief + sources |
| `decks/_example-quarterly/` | A complete worked example |
| `inbox/`, `output/` | Joe's in-tray and the finished decks (not committed) |

## How it works (for the technically curious)

The AI agent never draws slides. It writes a small, human-readable
`spec.yaml` describing each slide's content and intent; the deterministic
Python engine (`deckstudio build`) compiles that spec against the brand
tokens into a .pptx with native, editable objects. Brand compliance and
visual quality are enforced by code; the agent contributes judgment – 
summarizing sources, finding the insights, choosing the story.

```
inbox/ files → agent (reads, thinks, writes spec.yaml) → deckstudio build → output/deck_vN.pptx
```

Engine commands (`deckstudio --help`): `new`, `ingest`, `extract`,
`validate`, `build`, `doctor`, `types`.

## Status

- Brand values are extracted from the **official SOA PowerPoint template**
  (June 2026): real theme colors, Tenorite fonts, logo assets, and all 31
  official slide layouts ship in `brand/` – see `brand/BRAND_INTAKE.md`.
- Animations are tasteful-by-default (`subtle`), and can be disabled per deck
  or per build (`--no-animations`).

## Development

```bash
./setup.sh                 # or setup.ps1 on Windows
.venv/bin/pytest -q        # 38 tests incl. golden-deck build + chart editability
.venv/bin/ruff check src tests
.venv/bin/deckstudio build _example-quarterly --preview
```

CI builds the golden deck on Ubuntu and Windows on every push.
