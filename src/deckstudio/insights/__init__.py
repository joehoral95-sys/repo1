"""Data insights engine: a critical machine pass over uploaded data.

Runs the insight-finding lenses (playbooks/insight-finding.md) that a
computer is better at than a reader skimming a table: streaks, reversals,
acceleration, outliers, mix shifts, concentration, divergence, correlations,
target gaps. Output is CANDIDATE insights - every one must be verified and
climbed up the so-what ladder by a human (or the agent) before it goes on
a slide.
"""

from .analyze import Finding, analyze_table
from .report import findings_to_markdown
from .tabular import Table, load_tables

__all__ = ["Finding", "Table", "analyze_table", "findings_to_markdown", "load_tables"]
