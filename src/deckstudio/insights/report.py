"""Render findings as a markdown report the agent (or Joe) works FROM.

The report is deliberately framed as candidates: the machine did the
arithmetic pass; judgment - is it new, is it material, is the data itself
sound - still belongs to the reader (see playbooks/insight-finding.md).
"""

from __future__ import annotations

from .analyze import Finding

MAX_FINDINGS_PER_TABLE = 8

LENS_LABEL = {
    "streak": "Streaks & reversals",
    "reversal": "Streaks & reversals",
    "rate-vs-level": "Rate vs. level",
    "mix-shift": "Mix shift",
    "divergence": "Divergence",
    "outlier": "Outliers",
    "concentration": "Concentration",
    "benchmark": "Benchmarks & targets",
}


def findings_to_markdown(findings_by_table: dict[str, list[Finding]]) -> str:
    lines = [
        "# Data insights - candidate pass",
        "",
        "Machine arithmetic over the uploaded data, ranked by likely interest.",
        "Every item is a CANDIDATE: verify the numbers against the source,",
        "then climb the so-what ladder (playbooks/insight-finding.md) before",
        "anything goes on a slide. If a finding is something the audience",
        "already knows, drop it.",
        "",
    ]
    any_findings = False
    for table_name, findings in findings_by_table.items():
        lines.append(f"## {table_name}")
        lines.append("")
        if not findings:
            lines.append("No strong patterns fired. Either the data is steady "
                         "(which can itself be the story) or it's too small "
                         "for mechanical lenses - read it manually.")
            lines.append("")
            continue
        any_findings = True
        for i, f in enumerate(findings[:MAX_FINDINGS_PER_TABLE], start=1):
            lens = LENS_LABEL.get(f.lens, f.lens)
            lines.append(f"### {i}. {f.headline}")
            lines.append(f"*Lens: {lens} · source: {f.source}*")
            lines.append("")
            lines.append(f"- Evidence: {f.evidence}")
            lines.append(f"- So what: {f.so_what}")
            if f.slide_yaml:
                lines.append("- Starter slide (edit the TODOs):")
                lines.append("")
                lines.append("  ```yaml")
                lines.extend("  " + line for line in f.slide_yaml.splitlines())
                lines.append("  ```")
            lines.append("")
        dropped = len(findings) - MAX_FINDINGS_PER_TABLE
        if dropped > 0:
            lines.append(f"({dropped} lower-scoring findings not shown - "
                         "rerun with the data trimmed to the area of interest "
                         "to dig deeper.)")
            lines.append("")
    if not any_findings:
        lines.append("_Nothing fired anywhere. Say so honestly rather than "
                     "inventing an insight._")
        lines.append("")
    return "\n".join(lines)
