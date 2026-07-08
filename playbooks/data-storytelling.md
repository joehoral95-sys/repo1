# Data storytelling — choosing the visual form

Distilled from: Cleveland/McGill's perception rankings, Tufte's data-ink
principles, Few's dashboard design, Knaflic's *Storytelling with Data*.

## The chart chooser

Start from what the audience must SEE, not from the data's shape:

| The message is about… | Use | Spec |
|---|---|---|
| One number that matters | big-number stat tile | `big_number`, 1 stat (hero) |
| 2-4 KPIs at a glance | stat tile row | `big_number`, 2-4 stats |
| Comparison across categories | columns | `chart: bar_clustered` |
| Comparison, many (>8) or long-named categories | horizontal bars | `chart: bar_horizontal` |
| Trend over time | line | `chart: line` (needs ≥3 points) |
| Trend of a total + its parts | stacked columns / area | `chart: bar_stacked` / `area` |
| Part-of-whole, ≤4-6 slices | doughnut | `chart: doughnut` |
| Part-of-whole, >6 slices | horizontal bars (not pie!) | `chart: bar_horizontal` |
| Correlation of two measures | scatter | `chart: scatter` |
| Two options / before-after | side-by-side panels | `comparison` |
| Sequence, milestones, rollout | timeline | `timeline` |
| 3-4 parallel reasons/factors | icon columns | `icon_row` |
| Exact values the audience will read | table | `table` + `emphasize_col` |

When a default chart underserves the data (1-4 numbers, a single share, a
"how far along are we"), prefer the composed infographic forms the engine
offers — stat tiles, progress rings, proportional bars — over a sparse chart.
A bar chart with two bars is a big_number slide in disguise.

## Perception rules (why the table says what it says)

- People judge **position and length** accurately; **angle and area** poorly
  — hence bars/lines beat pies; pies are acceptable only for a handful of
  slices where the message is "roughly two-thirds," not exact comparison.
- Time flows left-to-right; categories order by value (largest first) unless
  they have natural order.
- Don't make the audience compute: if the message is the *change*, chart the
  change (or annotate the delta) rather than two levels they must subtract.

## Focus: one chart, one message

- The `insight:` field is mandatory in spirit: a chart without a stated
  takeaway is homework, not communication.
- Use `highlight:` to accent the single data point that proves the title's
  assertion. One accent — highlighting everything highlights nothing.
- 6 series max (schema-enforced); 2-3 reads best. If you need more, the
  message is probably "one of these differs" — gray isn't available in the
  spec, so split the chart or aggregate the rest.
- Data labels appear automatically where they help (single-series bars,
  pie/doughnut percentages); axis gridlines stay minimal. Trust the engine.

## Honesty rules

- Bar charts start at zero (the engine's default; never fake a dramatic
  difference with a truncated axis).
- Keep time intervals even; don't mix quarterly and annual points in one line.
- Label the source (`source:`) for any number the audience may challenge.
- If the honest chart is boring, the story is elsewhere — go back to the
  insight pass rather than dressing up a non-finding.
