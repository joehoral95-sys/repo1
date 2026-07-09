"""The insight lenses must fire on data engineered to contain each pattern,
and stay quiet on steady data."""

from deckstudio.insights import Table, analyze_table, findings_to_markdown, load_tables
from deckstudio.insights.tabular import parse_number


def wide(rows, periods=("Q1 25", "Q2 25", "Q3 25", "Q4 25", "Q1 26")):
    return Table(name="t", source="t.csv", headers=["Metric", *periods],
                 rows=[[label, *[str(v) for v in values]] for label, values in rows])


def lenses(findings):
    return {f.lens for f in findings}


def test_parse_number_handles_business_formats():
    assert parse_number("$1,234.50") == 1234.5
    assert parse_number("12%") == 12
    assert parse_number("(340)") == -340
    assert parse_number("n/a") is None
    assert parse_number("") is None


def test_streak_detected():
    f = analyze_table(wide([("Members", [100, 104, 109, 115, 122])]))
    streaks = [x for x in f if x.lens == "streak"]
    assert streaks and "Members" in streaks[0].headline
    assert streaks[0].slide_yaml  # comes with a starter chart snippet


def test_reversal_detected_and_outranks_streak():
    f = analyze_table(wide([("Sittings", [100, 106, 111, 118, 109])]))
    assert f[0].lens == "reversal"
    assert "first drop" in f[0].headline


def test_acceleration_detected():
    f = analyze_table(wide([("Revenue", [100, 102, 104, 112, 124])],
                           periods=("2022", "2023", "2024", "2025", "2026")))
    assert any(x.lens == "rate-vs-level" and "accelerating" in x.headline for x in f)


def test_mix_shift_detected():
    f = analyze_table(wide([
        ("Virtual", [20, 26, 32, 38, 45]),
        ("In-person", [80, 79, 78, 77, 76]),
    ]))
    mix = [x for x in f if x.lens == "mix-shift"]
    assert mix and "Virtual" in mix[0].headline


def test_divergence_detected():
    f = analyze_table(wide([
        ("Prelim exams", [100, 95, 90, 84, 78]),
        ("Fellowship exams", [50, 53, 55, 58, 62]),
    ]))
    div = [x for x in f if x.lens == "divergence"]
    assert div and "opposite directions" in div[0].headline


def test_outlier_detected_in_long_table():
    t = Table(name="regions", source="r.csv", headers=["Region", "Members"],
              rows=[["A", "1000"], ["B", "1100"], ["C", "980"],
                    ["D", "1050"], ["E", "4100"], ["F", "1020"]])
    f = analyze_table(t)
    out = [x for x in f if x.lens == "outlier"]
    assert out and "E" in out[0].headline and "far above" in out[0].headline


def test_concentration_detected():
    t = Table(name="products", source="p.csv", headers=["Product", "Revenue"],
              rows=[["Annual meeting", "500"], ["Webcasts", "120"],
                    ["Seminars", "90"], ["PD Edge", "80"], ["Other", "60"]])
    f = analyze_table(t)
    conc = [x for x in f if x.lens == "concentration"]
    assert conc and "Annual meeting" in conc[0].headline


def test_correlation_detected():
    rows = [[str(i), str(10 * i), str(20 * i + 3)] for i in range(1, 9)]
    t = Table(name="x", source="x.csv", headers=["Week", "Emails", "Signups"],
              rows=rows)
    f = analyze_table(t)
    assert any("tracks" in x.headline for x in f)


def test_target_gap_detected():
    t = Table(name="plan", source="p.csv",
              headers=["Stream", "Actual", "Target"],
              rows=[["Meetings", "90", "100"], ["Webcasts", "118", "100"],
                    ["Seminars", "99", "100"]])
    f = analyze_table(t)
    bench = [x for x in f if x.lens == "benchmark"]
    heads = " | ".join(x.headline for x in bench)
    assert "Meetings" in heads and "behind" in heads
    assert "Webcasts" in heads and "beating" in heads


def test_steady_data_stays_quiet():
    f = analyze_table(wide([("Flat", [100, 100, 100, 100, 100])]))
    assert f == []


def test_csv_roundtrip_and_report(tmp_path):
    p = tmp_path / "members.csv"
    p.write_text("Quarter,Q1 25,Q2 25,Q3 25,Q4 25\n"
                 "Members,\"31,000\",\"31,900\",\"32,600\",\"33,412\"\n",
                 encoding="utf-8")
    tables = load_tables(p)
    assert len(tables) == 1
    findings = analyze_table(tables[0])
    assert findings
    md = findings_to_markdown({"members": findings})
    assert "candidate" in md.lower()
    assert "```yaml" in md          # starter snippet present
    assert "—" not in md            # the report itself follows the style rule


def test_report_honest_when_nothing_fires():
    md = findings_to_markdown({"quiet": []})
    assert "No strong patterns" in md
