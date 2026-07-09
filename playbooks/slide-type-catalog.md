# Slide-type catalog

Every type the engine builds, when to use it, and a minimal spec snippet.
Full worked example: `decks/_example-quarterly/spec.yaml`.

## title — deck opener
Every deck starts with one. Title = the deck's core assertion when possible.
```yaml
- id: cover
  type: title
  title: "Membership Momentum, Exam Headwinds"
  subtitle: "Q2 2026 Update for the Board"
  presenter: "Prepared by the CEO's Office"
```

## agenda — the roadmap
Decks ≥6 slides. 2-6 items, a few words each.
```yaml
- id: agenda
  type: agenda
  items: ["Membership trend", "Exam volumes", "Fee proposal", "Decision needed"]
```

## section — chapter divider
Every 3-6 slides in longer decks; `number` gives a progress cue.
```yaml
- id: sec-membership
  type: section
  title: "Membership"
  number: 1
  subtitle: "The longest growth streak since 2019"
```

## big_number — KPIs / the hero stat
1 stat = hero tile (the star of the deck); 2-4 = tile row where the FIRST
stat gets the navy hero tile — order stats by importance. `arrow` is the
direction drawn; `sentiment` picks the color (falling lapse rate =
`arrow: down, sentiment: good`).
```yaml
- id: kpis
  type: big_number
  title: "Membership grew for the 6th straight quarter"
  stats:
    - {value: "33,412", label: "Total members", delta: "+2.1% vs Q1", arrow: up, sentiment: good}
```

## chart — evidence
Native, Edit-Data-able. Always give `insight:` — it renders as a navy
"SO WHAT" takeaway panel beside the chart (the exhibit layout); without it
the chart runs full-width. `highlight:` accents the point that proves the
title. Kinds: bar_clustered, bar_stacked, bar_horizontal, line, area, pie,
doughnut, scatter. Chooser: `data-storytelling.md`.
```yaml
- id: exam-trend
  type: chart
  title: "Exam sittings dipped — but only in prelims"
  chart:
    kind: bar_clustered
    categories: ["Q3 25", "Q4 25", "Q1 26", "Q2 26"]
    series:
      - {name: "Preliminary exams", values: [8120, 8340, 7980, 7410]}
      - {name: "Fellowship exams", values: [2210, 2190, 2260, 2300]}
    highlight: {series: "Preliminary exams", point: 3}
    number_format: "#,##0"
  insight: "Fellowship demand is stable — it's a pipeline issue, not retention."
  source: "SOA exam registration system"
```

## comparison — two options / before-after
The decision slide. `emphasize:` marks the recommendation.
```yaml
- id: fee-paths
  type: comparison
  title: "Two paths on exam fees"
  left:  {heading: "Hold fees flat", bullets: ["No friction", "**-$1.2M** vs plan"]}
  right: {heading: "Raise 4% (recommended)", bullets: ["Covers costs", "**+$0.9M** to plan"]}
  emphasize: right
```

## timeline — sequence / rollout
2-6 milestones; `done: true` fills completed nodes.
```yaml
- id: rollout
  type: timeline
  title: "Approval today puts new fees in place by spring"
  milestones:
    - {label: "Board approval", date: "Jul 2026"}
    - {label: "New fees effective", date: "Jan 2027"}
```

## icon_row — 2-4 parallel factors
Reasons, pillars, pressures. Icon files from `brand/assets/icons/`
(falls back to a branded initial disc — fine).
```yaml
- id: why-now
  type: icon_row
  title: "Three pressures make this the right moment"
  items:
    - {heading: "Proctoring costs", text: "Vendor costs up 12% since 2024."}
    - {heading: "Peer benchmark", text: "Fees sit 8-15% below peer bodies."}
```

## table — exact values
When the audience will *read* numbers (committees, appendices).
`emphasize_col` highlights the column that carries the story.
```yaml
- id: detail
  type: table
  title: "P and FM carry the dip"
  columns: ["Exam", "Q1 26", "Q2 26", "Change"]
  rows: [["Exam P", "2,410", "2,180", "-9.5%"]]
  emphasize_col: 3
```

## quote — the big statement / the ask
Full-bleed drama for one sentence: the formal ask, a member quote, a rallying
line. ≤280 chars.
```yaml
- id: ask
  type: quote
  text: "We ask the Board to approve the 4% exam-fee adjustment effective January 2027."
  attribution: "Decision requested today"
```

## content — plain bullets (escape hatch)
When nothing above fits. 1-6 bullets, optional `sub`, optional `kicker`
eyebrow. If you're using it three slides in a row, redesign.
```yaml
- id: context
  type: content
  title: "The dip traces to the university calendar shift"
  kicker: "Background"
  bullets:
    - "Spring sitting moved past most graduation dates"
    - {text: "Two cohorts affected", sub: ["Class of '25", "Class of '26"]}
```

## thanks — closer
```yaml
- id: close
  type: thanks
  message: "Full model in the appendix pack."
  contact: "questions@soa.org"
```

## progress — how far along are we
1-4 donut gauges. Use for execution status, plan completion, adoption.
```yaml
- id: readiness
  type: progress
  title: "Rollout workstreams are already moving"
  items:
    - {label: "Fee model & pricing", percent: 90}
    - {label: "Member comms plan", percent: 65}
  caption: "Percent complete as of July 2026"
```

## Universal fields
Every slide: `id` (unique kebab-case, stable), optional `kicker:` (small
letter-spaced eyebrow, e.g. "AT A GLANCE" or "KPI METRICS · 1 OF 2"),
optional `notes:` (speaker notes — put the detail here), optional
`animate: none|fade|build`.

## Status & context extras
- `big_number` stats take `target:` ("FY target 34.0K") and
  `status: on_track|watch|pending` (colored dot in the card corner).
- `section` slides take `preview:` — up to 6 `{label, value, status}` rows
  rendered as a right-side teaser panel of the section's metrics.
- `chart.highlight` renders the data point in SOA yellow AND pins an
  auto-computed delta chip to the chart.
- `comparison.emphasize` adds the navy panel, a RECOMMENDED chip, and a
  "vs" badge on the seam.
- `icon_row` icons by name: growth, people, cost, clock, target, shield,
  idea, alert, doc, globe.
