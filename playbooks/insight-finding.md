# Insight finding

The mandatory pass between reading the sources and outlining the deck. The
sender usually transmits *data*; the deck's job is to transmit *meaning*.
An insight = a true, supported statement that changes what the audience
thinks or does, which they didn't already know.

**Start mechanical:** for CSV/XLSX sources, `deckstudio insights <file>
--deck <name>` runs lenses 1-8 below arithmetically and writes ranked
candidates (with starter slide snippets) to `insights.md`. That pass
catches what a reader skimming a table misses – a steepening rate inside a
flat-looking level, two series quietly splitting apart. It cannot judge
newness, materiality, or data quality: lenses 9-10 and the quality gates
are always on you.

## The hunting checklist

Run each lens over the digests; note anything that fires with its supporting
numbers:

1. **Deltas** – what changed vs. last period / plan / same period last year?
   Which direction, how big, is it accelerating?
2. **Streaks & reversals** – "6th straight quarter of growth" and "first
   decline since 2019" are stories; a single number isn't.
3. **Outliers** – which category/region/product is way off the others? Both
   heroes and problems.
4. **Mix shifts** – totals can hide it: flat overall, but the composition
   moved ("two-thirds of candidates now come via universities").
5. **Concentration** – does one segment carry most of the total? ("P and FM
   carry the dip.")
6. **Divergence** – two series that used to move together and no longer do
   (prelim vs. fellowship exams). Often the buried lede.
7. **Rate vs. level** – a level can look fine while its rate of change is
   alarming, and vice versa.
8. **Benchmarks** – vs. peers, targets, history. "8-15% below comparable
   bodies" kills an objection by itself.
9. **The denominator check** – percentages of small bases, totals that
   changed definition, cherry-picked windows. Finding a *flaw* in the data's
   apparent story is also an insight (and saves Joe embarrassment).
10. **The absence** – what would you expect in this data that isn't there?

## The "so what" ladder

Raw observation → so what → so what for THIS audience. Climb until it would
make the audience act or feel differently, then put THAT on the slide.

> Prelim sittings fell 7% → the entry pipeline is softening → *for the Board*:
> revenue risk in 2028+, but retention is intact, so the fix is marketing to
> universities, not program surgery.

If you can't climb past the observation, it's a fact for the appendix, not an
insight for a slide.

## Quality gates (all must pass)

- **True**: traceable to a source digest, arithmetic checked. Never
  extrapolate beyond the data to make a better story.
- **New**: would the audience already know this? (Quarterly numbers they see
  monthly are not insights; the pattern across them may be.)
- **Material**: does it touch money, risk, members, or a decision on the table?
- **Honest**: reframing bad news ("dip is concentrated in prelims") is good;
  hiding it is not. Present the negative and the response.

## Where insights go in the deck

- The best one shapes the deck's title and first section.
- Chart slides: the insight is the `insight:` callout AND drives the
  `highlight:` choice – accent the exact data point that proves it.
- List candidate insights in `brief.md` with sources, even ones that didn't
  make the deck – Joe may know context you don't; let him choose.
