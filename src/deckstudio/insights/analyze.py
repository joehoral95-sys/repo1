"""Pattern detectors: the lenses from playbooks/insight-finding.md, run
mechanically. Each finding is a CANDIDATE - true arithmetic on the given
numbers, but only a human can judge whether it's new and material.

Two table shapes:
  wide  label column + period columns (one series per row) -> trend lenses
  long  label column + measure columns (one distribution per column)
        -> outlier / concentration / correlation / target-gap lenses
"""

from __future__ import annotations

import re
import statistics
from dataclasses import dataclass, field

from .tabular import (
    Table,
    label_column_index,
    looks_like_periods,
    numeric_column_indexes,
    parse_number,
)

MIN_STREAK = 3          # periods moving one way before it's a story
OUTLIER_Z = 3.0         # modified z-score threshold (MAD-based)
TOP_SHARE = 0.35        # one item carrying 35%+ of the total
MIX_SHIFT_PTS = 5.0     # share-of-total move in percentage points
STRONG_R = 0.8          # correlation worth reporting
DIVERGE_R = -0.5        # two series moving against each other
TARGET_WORDS = re.compile(r"target|plan|goal|budget|forecast", re.IGNORECASE)


@dataclass
class Finding:
    lens: str            # which hunting-checklist lens fired
    headline: str        # assertion-style candidate slide title
    evidence: str        # the arithmetic, so it can be checked
    so_what: str         # prompt to climb the ladder, not a conclusion
    score: float         # 0-100 ranking weight
    table: str = ""
    source: str = ""
    slide_yaml: str = ""  # optional starter spec snippet
    series: list[str] = field(default_factory=list)


def analyze_table(table: Table) -> list[Finding]:
    numeric = numeric_column_indexes(table)
    label_idx = label_column_index(table, numeric)
    findings: list[Finding] = []
    if len(numeric) >= 3 and looks_like_periods([table.headers[i] for i in numeric]):
        findings.extend(_wide_lenses(table, label_idx, numeric))
        # the latest period is also a distribution: concentration still applies
        findings.extend(_concentration(table, label_idx, numeric[-1:]))
    else:
        findings.extend(_long_lenses(table, label_idx, numeric))
    for f in findings:
        f.table, f.source = table.name, table.source
    return sorted(findings, key=lambda f: -f.score)


# ---------------------------------------------------------------- wide shape

def _row_series(table: Table, label_idx: int | None, numeric: list[int]):
    """(label, [values]) per row, only rows fully numeric across the periods."""
    out = []
    for r, row in enumerate(table.rows):
        label = str(row[label_idx]).strip() if label_idx is not None else f"row {r + 1}"
        values = [parse_number(row[i]) if i < len(row) else None for i in numeric]
        if all(v is not None for v in values):
            out.append((label, values))
    return out


def _wide_lenses(table: Table, label_idx, numeric) -> list[Finding]:
    periods = [str(table.headers[i]) for i in numeric]
    series = _row_series(table, label_idx, numeric)
    findings = []
    for label, values in series:
        findings.extend(_streak_and_reversal(label, values, periods))
        findings.extend(_acceleration(label, values, periods))
    findings.extend(_mix_shift(series, periods))
    findings.extend(_divergence(series, periods))
    findings.extend(_movers(series, periods))
    return findings


def _streak_and_reversal(label, values, periods) -> list[Finding]:
    deltas = [b - a for a, b in zip(values, values[1:], strict=False)]
    if not deltas or all(d == 0 for d in deltas):
        return []
    findings = []
    # streak: consecutive same-direction moves ending at the latest period
    direction = 0
    streak = 0
    for d in reversed(deltas):
        s = (d > 0) - (d < 0)
        if s == 0:
            break
        if direction == 0:
            direction = s
        if s != direction:
            break
        streak += 1
    total_pct = _pct(values[0], values[-1])
    if streak >= MIN_STREAK and streak == len(deltas):
        word = "rose" if direction > 0 else "fell"
        findings.append(Finding(
            lens="streak",
            headline=f"{label} {word} in every period on record ({streak} straight)",
            evidence=f"{label}: {_fmt(values[0])} -> {_fmt(values[-1])} across "
                     f"{periods[0]}-{periods[-1]} ({_fmt_pct(total_pct)})",
            so_what="An unbroken run is a story by itself - is the driver "
                    "durable, and does the audience know it's this consistent?",
            score=60 + min(streak * 5, 25),
            series=[label],
            slide_yaml=_chart_yaml(label, periods, values, point=len(values) - 1),
        ))
    elif streak >= MIN_STREAK:
        word = "rising" if direction > 0 else "falling"
        findings.append(Finding(
            lens="streak",
            headline=f"{label} has been {word} for {streak} straight periods",
            evidence=f"last {streak} moves all {word}; latest {_fmt(values[-1])} "
                     f"({_fmt_pct(_pct(values[-1 - streak], values[-1]))} over the run)",
            so_what="Is the streak accelerating or fading, and what breaks it?",
            score=50 + min(streak * 5, 25),
            series=[label],
            slide_yaml=_chart_yaml(label, periods, values, point=len(values) - 1),
        ))
    # reversal: latest move against an established run
    if len(deltas) >= 3:
        prior = deltas[:-1]
        prior_dir = (sum(1 for d in prior if d > 0) - sum(1 for d in prior if d < 0))
        last = deltas[-1]
        if prior_dir != 0 and last != 0 and ((last > 0) != (prior_dir > 0)):
            run = sum(1 for d in prior if (d > 0) == (prior_dir > 0))
            if run == len(prior):
                word = "drop" if last < 0 else "rise"
                findings.append(Finding(
                    lens="reversal",
                    headline=f"{label}: first {word} after {run} periods the other way",
                    evidence=f"{periods[-2]} {_fmt(values[-2])} -> {periods[-1]} "
                             f"{_fmt(values[-1])} ({_fmt_pct(_pct(values[-2], values[-1]))})",
                    so_what="Reversals are the buried lede - one-off or turning "
                            "point? What changed in this period?",
                    score=80,
                    series=[label],
                    slide_yaml=_chart_yaml(label, periods, values, point=len(values) - 1),
                ))
    return findings


def _acceleration(label, values, periods) -> list[Finding]:
    deltas = [b - a for a, b in zip(values, values[1:], strict=False)]
    if len(deltas) < 4:
        return []
    early = statistics.mean(deltas[:-2])
    late = statistics.mean(deltas[-2:])
    if early == 0 or (early > 0) != (late > 0):
        return []
    ratio = late / early
    if ratio >= 1.8:
        verb = "growth is accelerating" if late > 0 else "the decline is steepening"
        score = 65.0
    elif ratio <= 0.4:
        verb = "growth is stalling" if early > 0 else "the decline is easing"
        score = 55.0
    else:
        return []
    return [Finding(
        lens="rate-vs-level",
        headline=f"{label}: {verb}",
        evidence=f"average move was {_fmt(early)}/period, last two periods "
                 f"average {_fmt(late)}/period",
        so_what="The level looks unchanged period to period - the rate is the "
                "story. Does the audience track the level or the rate?",
        score=score,
        series=[label],
        slide_yaml=_chart_yaml(label, periods, values, point=len(values) - 1),
    )]


def _mix_shift(series, periods) -> list[Finding]:
    if len(series) < 2:
        return []
    first_total = sum(v[0] for _, v in series)
    last_total = sum(v[-1] for _, v in series)
    if first_total <= 0 or last_total <= 0:
        return []
    moves = [(label, (values[-1] / last_total - values[0] / first_total) * 100,
              values) for label, values in series]
    # near-ties favor the gaining side: "shifting toward X" names the story
    label, move, values = max(moves, key=lambda m: (round(abs(m[1]), 4), m[1] > 0))
    if abs(move) < MIX_SHIFT_PTS:
        return []
    direction = "toward" if move > 0 else "away from"
    share_now = values[-1] / last_total * 100
    return [Finding(
        lens="mix-shift",
        headline=f"The mix is shifting {direction} {label}",
        evidence=f"{label} went from {values[0] / first_total:.0%} to "
                 f"{share_now / 100:.0%} of the total between {periods[0]} "
                 f"and {periods[-1]} ({move:+.1f} pts)",
        so_what="Totals can look flat while composition moves - does the "
                "shift change where money or effort should go?",
        score=55 + min(abs(move), 25),
        series=[label],
    )]


def _divergence(series, periods) -> list[Finding]:
    if len(series) < 2 or len(periods) < 5:
        return []
    findings = []
    for i in range(len(series)):
        for j in range(i + 1, len(series)):
            (la, va), (lb, vb) = series[i], series[j]
            r = _pearson(va, vb)
            if r is not None and r <= DIVERGE_R:
                findings.append(Finding(
                    lens="divergence",
                    headline=f"{la} and {lb} are moving in opposite directions",
                    evidence=f"correlation {r:.2f} across {len(periods)} periods; "
                             f"{la} {_fmt_pct(_pct(va[0], va[-1]))}, "
                             f"{lb} {_fmt_pct(_pct(vb[0], vb[-1]))}",
                    so_what="Series that split apart usually mean two different "
                            "causes - naming which is which is the insight.",
                    score=70 + min(abs(r) * 10, 10),
                    series=[la, lb],
                ))
    return findings[:2]


def _movers(series, periods) -> list[Finding]:
    changes = []
    for label, values in series:
        pct = _pct(values[0], values[-1])
        if pct is not None:
            changes.append((label, pct, values))
    if len(changes) < 3:
        return []
    changes.sort(key=lambda t: t[1])
    median_pct = statistics.median(pct for _, pct, _ in changes)
    findings = []
    for label, pct, values in (changes[-1], changes[0]):
        if abs(pct - median_pct) < 10 or abs(pct) < 5:
            continue
        word = "fastest-growing" if pct > median_pct else "the laggard"
        findings.append(Finding(
            lens="outlier",
            headline=f"{label} is {word} of the group "
                     f"({_fmt_pct(pct)} vs {_fmt_pct(median_pct)} median)",
            evidence=f"{label}: {_fmt(values[0])} ({periods[0]}) -> "
                     f"{_fmt(values[-1])} ({periods[-1]})",
            so_what="Heroes and problems both hide in group totals - is this "
                    "one a cause to copy or a fire to put out?",
            score=50 + min(abs(pct - median_pct) / 2, 30),
            series=[label],
        ))
    return findings


# ---------------------------------------------------------------- long shape

def _long_lenses(table: Table, label_idx, numeric) -> list[Finding]:
    findings = []
    findings.extend(_concentration(table, label_idx, numeric))
    findings.extend(_outliers(table, label_idx, numeric))
    findings.extend(_correlations(table, numeric))
    findings.extend(_target_gaps(table, label_idx, numeric))
    return findings


def _labeled_values(table, label_idx, col):
    out = []
    for r, row in enumerate(table.rows):
        v = parse_number(row[col]) if col < len(row) else None
        if v is None:
            continue
        label = str(row[label_idx]).strip() if label_idx is not None else f"row {r + 1}"
        out.append((label, v))
    return out


def _concentration(table, label_idx, numeric) -> list[Finding]:
    findings = []
    for col in numeric:
        header = str(table.headers[col])
        if "%" in header or TARGET_WORDS.search(header):
            continue
        pairs = _labeled_values(table, label_idx, col)
        if len(pairs) < 4:
            continue
        total = sum(v for _, v in pairs)
        if total <= 0:
            continue
        pairs.sort(key=lambda t: -t[1])
        top_label, top_v = pairs[0]
        top_share = top_v / total
        two_share = (top_v + pairs[1][1]) / total
        if top_share >= TOP_SHARE:
            findings.append(Finding(
                lens="concentration",
                headline=f"{top_label} alone carries {top_share:.0%} of {header}",
                evidence=f"{_fmt(top_v)} of {_fmt(total)} total across "
                         f"{len(pairs)} items",
                so_what="Concentration cuts both ways - focus the win, or "
                        "flag the dependency risk?",
                score=55 + min(top_share * 40, 30),
                series=[top_label],
                slide_yaml=_stat_yaml(f"{top_share:.0%}",
                                      f"{top_label} share of {header}"),
            ))
        elif two_share >= 0.6:
            findings.append(Finding(
                lens="concentration",
                headline=f"{top_label} and {pairs[1][0]} carry {two_share:.0%} "
                         f"of {header}",
                evidence=f"top 2 of {len(pairs)} items = {_fmt(top_v + pairs[1][1])} "
                         f"of {_fmt(total)}",
                so_what="The long tail may cost more than it returns - or the "
                        "top two may deserve the investment.",
                score=50,
                series=[top_label, pairs[1][0]],
            ))
    return findings


def _outliers(table, label_idx, numeric) -> list[Finding]:
    findings = []
    for col in numeric:
        pairs = _labeled_values(table, label_idx, col)
        if len(pairs) < 5:
            continue
        values = [v for _, v in pairs]
        med = statistics.median(values)
        mad = statistics.median(abs(v - med) for v in values)
        if mad == 0:
            continue
        header = str(table.headers[col])
        for label, v in pairs:
            z = 0.6745 * (v - med) / mad
            if abs(z) >= OUTLIER_Z:
                side = "far above" if z > 0 else "far below"
                findings.append(Finding(
                    lens="outlier",
                    headline=f"{label} is {side} the pack on {header}",
                    evidence=f"{label} = {_fmt(v)} vs median {_fmt(med)} "
                             f"(modified z = {z:.1f})",
                    so_what="Outliers are heroes or problems - which, and is "
                            "the measurement itself trustworthy?",
                    score=60 + min(abs(z) * 3, 25),
                    series=[label],
                ))
    return findings[:3]


def _correlations(table, numeric) -> list[Finding]:
    if len(numeric) < 2:
        return []
    findings = []
    for a in range(len(numeric)):
        for b in range(a + 1, len(numeric)):
            ca, cb = numeric[a], numeric[b]
            va = [parse_number(row[ca]) if ca < len(row) else None for row in table.rows]
            vb = [parse_number(row[cb]) if cb < len(row) else None for row in table.rows]
            pairs = [(x, y) for x, y in zip(va, vb, strict=True)
                     if x is not None and y is not None]
            if len(pairs) < 6:
                continue
            r = _pearson([p[0] for p in pairs], [p[1] for p in pairs])
            if r is None or abs(r) < STRONG_R:
                continue
            ha, hb = str(table.headers[ca]), str(table.headers[cb])
            word = "tracks" if r > 0 else "moves against"
            findings.append(Finding(
                lens="divergence",
                headline=f"{ha} {word} {hb} (r = {r:.2f})",
                evidence=f"{len(pairs)} paired observations",
                so_what="Correlation isn't a lever - but if one is cheap to "
                        "move and they're linked, that's worth a slide. Check "
                        "for a shared cause first.",
                score=45 + min(abs(r) * 20, 20),
                series=[ha, hb],
            ))
    return findings[:2]


def _target_gaps(table, label_idx, numeric) -> list[Finding]:
    target_cols = [i for i in numeric if TARGET_WORDS.search(str(table.headers[i]))]
    actual_cols = [i for i in numeric if i not in target_cols]
    if not target_cols or not actual_cols:
        return []
    tcol, acol = target_cols[0], actual_cols[0]
    gaps = []
    for r, row in enumerate(table.rows):
        t = parse_number(row[tcol]) if tcol < len(row) else None
        a = parse_number(row[acol]) if acol < len(row) else None
        if t in (None, 0) or a is None:
            continue
        label = str(row[label_idx]).strip() if label_idx is not None else f"row {r + 1}"
        gaps.append((label, (a - t) / abs(t) * 100, a, t))
    if not gaps:
        return []
    findings = []
    gaps.sort(key=lambda g: g[1])
    worst, best = gaps[0], gaps[-1]
    if worst[1] <= -5:
        findings.append(Finding(
            lens="benchmark",
            headline=f"{worst[0]} is {abs(worst[1]):.0f}% behind "
                     f"{table.headers[tcol]}",
            evidence=f"actual {_fmt(worst[2])} vs {_fmt(worst[3])}",
            so_what="Misses against a stated target demand either a recovery "
                    "plan or a re-based target - which will the audience ask for?",
            score=70 + min(abs(worst[1]) / 2, 20),
            series=[worst[0]],
            slide_yaml=_stat_yaml(f"{worst[1]:+.0f}%",
                                  f"{worst[0]} vs {table.headers[tcol]}",
                                  sentiment="bad"),
        ))
    if best[1] >= 5 and best is not worst:
        findings.append(Finding(
            lens="benchmark",
            headline=f"{best[0]} is beating {table.headers[tcol]} "
                     f"by {best[1]:.0f}%",
            evidence=f"actual {_fmt(best[2])} vs {_fmt(best[3])}",
            so_what="Beats are underused - they buy credibility for the asks "
                    "elsewhere in the deck.",
            score=55 + min(best[1] / 2, 15),
            series=[best[0]],
            slide_yaml=_stat_yaml(f"{best[1]:+.0f}%",
                                  f"{best[0]} vs {table.headers[tcol]}",
                                  sentiment="good"),
        ))
    return findings


# ---------------------------------------------------------------- utilities

def _pearson(xs, ys) -> float | None:
    if len(xs) < 3:
        return None
    try:
        return statistics.correlation(xs, ys)
    except statistics.StatisticsError:
        return None


def _pct(a, b) -> float | None:
    if a in (None, 0) or b is None:
        return None
    return (b - a) / abs(a) * 100


def _fmt(v: float) -> str:
    if abs(v) >= 1000:
        return f"{v:,.0f}"
    if v == int(v):
        return str(int(v))
    return f"{v:,.1f}"


def _fmt_pct(p: float | None) -> str:
    return "n/a" if p is None else f"{p:+.1f}%"


def _chart_yaml(label, periods, values, point=None) -> str:
    vals = ", ".join(_fmt(v).replace(",", "") for v in values)
    cats = ", ".join(f'"{p}"' for p in periods)
    lines = [
        "- id: TODO",
        "  type: chart",
        "  title: \"TODO - the assertion this trend proves\"",
        "  chart:",
        f"    kind: {'line' if len(values) >= 5 else 'bar_clustered'}",
        f"    categories: [{cats}]",
        "    series:",
        f"      - {{name: \"{label}\", values: [{vals}]}}",
    ]
    if point is not None:
        lines.append(f"    highlight: {{series: \"{label}\", point: {point}}}")
    lines.append("  insight: \"TODO - the so-what for this audience\"")
    return "\n".join(lines)


def _stat_yaml(value, label, sentiment="neutral") -> str:
    return "\n".join([
        "- id: TODO",
        "  type: big_number",
        "  title: \"TODO - the assertion\"",
        "  stats:",
        f"    - {{value: \"{value}\", label: \"{label}\", sentiment: {sentiment}}}",
    ])
