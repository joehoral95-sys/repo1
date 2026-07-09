# Presentation design

Slide craft: what makes a slide read as designed rather than assembled. The
engine enforces most of this mechanically (grid, tokens, type scale); this
playbook governs the choices the spec still leaves to you.

## One idea per slide

- A slide is a billboard, not a page. If the title needs "and," split it.
- The ~40-word ceiling exists because the audience reads or listens, never
  both. Speaker notes exist precisely so slides can stay sparse.
- Empty space is a feature. A `big_number` slide with one hero stat
  communicates more than the same number inside six bullets.

## Visual hierarchy

Every slide should answer in half a second: where do I look first, second,
third?
1. First: the title (the assertion).
2. Second: the evidence (chart/tiles/panels).
3. Third: the qualifier (insight strip, source, footer).
If a slide has two competing "look here" elements, demote one (or split).
That's why the engine allows one `highlight:` per chart and one `emphasize`
per comparison/table.

## Rhythm across the deck

- Vary slide types: three near-identical bullet slides in a row reads as one
  long slide (the linter flags this). Break runs with a `section`,
  `big_number`, or `chart`.
- `section` dividers every 3-6 slides give the audience a mental table of
  contents; number them for decks longer than ~10 slides.
- Open strong (title → agenda → the headline) and close with the ask or the
  takeaway — never trail off into an appendix.

## Animation discipline

**Animations are OFF by default and opt-in per deck** (`animations: subtle`).
Hard compatibility fact: renderers other than desktop PowerPoint — iOS
Quick Look, phone previews, some web viewers — mis-composite animated
slides (ghosted shapes, hidden panels). Only enable animations for a deck
that will be PRESENTED from desktop PowerPoint, never for anything that
will be emailed, previewed on a phone, or read as a document.

When they are enabled:
- `build` when the *sequence* is the point — options revealed one at a time,
  KPIs landing one by one, a list where each item deserves its beat.
- `fade` for gentle polish on a slide whose content arrives as one thought.
- `none` is the correct per-slide default. Never animate section dividers,
  tables, or anything the audience should study.

## Brand application (liberal but compliant)

- All colors/fonts/spacing come from `brand/tokens.yaml` via the engine —
  a spec can't go off-brand, so be *bold* with the forms: hero stats, full-bleed
  section slides, accent highlights. Restraint should be editorial, not visual
  timidity.
- Accent (gold/blue) means "look here" — the moment it's everywhere it means
  nothing. The engine already rations it; don't fight that with markup abuse
  (`[accent]` on whole sentences).
- **SOA-specific rules** (from the official 2026 SOA PowerPoint template):
  - Logo sits **bottom-left** on every slide; page number bottom-right in
    brand blue. The engine does this automatically — never add extra logos.
  - On navy backgrounds use the sky-blue shield mark alone (the navy wordmark
    would vanish); on white use the full-color logo. Never stretch, recolor,
    or add effects to either.
  - Slide titles render in SOA bright blue (#0051B8) — the template's own
    convention.
  - Brand red (#FF383C) is reserved for negative values and alerts; lime
    (#B3CE36) is an energy accent, used sparingly.
  - Brand fonts are Tenorite Bold / Tenorite Regular (Microsoft 365 cloud
    fonts). Machines without them substitute Segoe UI / Calibri —
    `deckstudio doctor` warns when that will happen.
  - SOA's hand-drawn accent marks (`brand/assets/patterns/`): the sky
    **swash** underlines divider titles; the sky **circle** wraps the
    thank-you words. The engine places both automatically. Use them ONLY on
    dark full-bleed slides, never behind or over content.
  - The template's geometric background pattern (WMF, on layouts like
    '1_Blank') is decorative page art — it must NEVER sit behind slide
    content. The engine refuses decorated layouts; don't fight that.

## Editability (why the engine works the way it does)

- Charts are native with embedded data → Joe can Edit Data in PowerPoint.
- Text is real text boxes → anyone can retype a word.
- Rebuilds never overwrite old versions → hand edits are safe.
- Therefore: never suggest screenshots/images of data, never flatten a table
  into a picture, and always update the spec when numbers change so the next
  rebuild agrees with reality.
