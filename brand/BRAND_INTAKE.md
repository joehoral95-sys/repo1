# Brand intake – one-time setup with the real SOA brand assets

> **Status: COMPLETED (2026-07)** from the official SOA PowerPoint template
> (`2026.06.02__SOA_PPT_Template.pptx`): theme colors and fonts extracted into
> `tokens.yaml`, logo assets filed under `assets/logos/`, and the template
> (slides stripped, all 31 layouts kept) installed as `template.pptx`.
> Still welcome if they surface later: the formal brand-guidelines PDF
> (clear-space and usage rules), a white/reversed full logo for dark
> backgrounds, and any approved icon set → drop them in `inbox/` and rerun
> the relevant steps below.

Deck Studio ships with brand values extracted from the official template.
This checklist documents how to (re)run the intake if assets change. It's a
conversation between Joe (who has the assets) and the agent (who does the
editing) – run it once, then every deck is on-brand automatically.

## What Joe drops into `inbox/`

1. **Brand guidelines** (PDF or PPT) – the official document with colors,
   fonts, and logo rules.
2. **Logo files** – ideally PNG with transparent background, in at least two
   variants: full-color (for white slides) and white/reversed (for dark
   slides). SVG or EPS also fine (note: convert to PNG for PowerPoint use).
3. **The current SOA PowerPoint template** (.potx or .pptx), if one exists.
4. Optionally: an approved icon set, photography, background textures.

## What the agent does with them

1. **Extract design tokens** from the guidelines into `brand/tokens.yaml`:
   - `colors:` – exact hex values for primary, accent(s), and neutrals.
     Map SOA's palette onto the token roles; keep `positive`/`negative`
     readable against white (WCAG AA for text-sized uses).
   - `colors.chart_series:` – 4-6 brand-compatible series colors, highest
     contrast pair first (first color = hero series).
   - `fonts:` – the brand heading and body font NAMES exactly as they appear
     in Windows (plus the guideline's documented substitute as `fallback`).
     Never embed fonts; PowerPoint substitutes by name.
2. **File the logos** under `brand/assets/logos/` and point
   `logo.default` / `logo.dark_bg` in tokens.yaml at them.
3. **Adopt the official template** (if provided): save it as
   `brand/template.pptx`. The engine picks it up automatically. Keep layout
   names stable – the engine resolves layouts by name and fails loudly if
   they disappear.
4. **Verify**: run `deckstudio doctor` (checks fonts are installed on this
   machine, logo paths resolve, template loads), then
   `deckstudio build _example-quarterly --preview` and eyeball the sample
   deck against the guidelines with Joe.
   **Important**: LibreOffice previews do NOT render EMF/WMF graphics that
   corporate templates often use for background art – after any template
   change, open a built deck once in real PowerPoint before calling it done.
5. **Record rules the engine can't encode** (logo clear space, photo style,
   "never put the logo on gold", ...) in `playbooks/presentation-design.md`
   under "SOA-specific rules" so the agent respects them when speccing.

## After intake

- Commit `tokens.yaml`, assets, and template to git – the brand travels with
  the repo.
- Delete nothing from `inbox/` until Joe confirms the sample deck looks right.
