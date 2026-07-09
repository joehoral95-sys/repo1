"""The deckstudio CLI — the only interface the agent (or Joe) needs.

    deckstudio new <name>            start a deck project with a starter spec
    deckstudio validate <deck>       schema + design lint
    deckstudio build <deck>          compile spec.yaml -> output/<name>_vN.pptx
    deckstudio ingest <files> --deck <name>   source docs -> markdown digests
    deckstudio extract <file.pptx> --deck <name>  old deck -> draft spec + report
    deckstudio doctor                environment & font check
    deckstudio types                 list slide types the engine supports
"""

from __future__ import annotations

import sys
from pathlib import Path

import typer
from rich.console import Console

from . import __version__
from .tokens import REPO_ROOT, load_tokens

app = typer.Typer(add_completion=False, no_args_is_help=True,
                  help="SOA Deck Studio — spec in, stunning editable deck out.")
console = Console()


def _stdout_can_encode(text: str) -> bool:
    enc = getattr(sys.stdout, "encoding", None) or "ascii"
    try:
        text.encode(enc)
        return True
    except (LookupError, UnicodeEncodeError):
        return False


# Legacy Windows consoles (cp1252) can't encode ✓/✗ — fall back to ASCII
# so the CLI never crashes over a status glyph.
OK, BAD = ("✓", "✗") if _stdout_can_encode("✓✗") else ("OK", "X")

DECKS_DIR = REPO_ROOT / "decks"
OUTPUT_DIR = REPO_ROOT / "output"


def _deck_dir(deck: str) -> Path:
    p = Path(deck)
    if p.is_dir():
        return p
    candidate = DECKS_DIR / deck
    if candidate.is_dir():
        return candidate
    console.print(f"[red]No deck found at '{deck}' or decks/{deck}.[/red] "
                  f"Existing decks: {[d.name for d in DECKS_DIR.iterdir() if d.is_dir()]}")
    raise typer.Exit(2)


def _load(deck_dir: Path):
    from .spec.loader import SpecError, load_spec

    try:
        return load_spec(deck_dir)
    except SpecError as e:
        console.print(f"[red]Spec error:[/red]\n{e}")
        raise typer.Exit(1) from None


@app.command()
def new(name: str = typer.Argument(help="Deck name, e.g. 'q3-board-update'")):
    """Create decks/<name>/ with a starter spec and brief."""
    deck_dir = DECKS_DIR / name
    if deck_dir.exists():
        console.print(f"[yellow]decks/{name} already exists — not touching it.[/yellow]")
        raise typer.Exit(1)
    (deck_dir / "sources").mkdir(parents=True)
    starter = """\
deck:
  title: "TODO — deck title"
  audience: "TODO — who will see this?"
  intent: "TODO — what must it achieve?"

slides:
  - id: cover
    type: title
    title: "TODO — an assertion, not a topic"
    subtitle: ""
"""
    (deck_dir / "spec.yaml").write_text(starter, encoding="utf-8")
    (deck_dir / "brief.md").write_text(
        f"# Brief: {name}\n\n- Audience:\n- Intent:\n- Date / occasion:\n"
        "- Candidate insights (fill during the insight pass):\n", encoding="utf-8")
    console.print(f"[green]Created decks/{name}/[/green] — edit spec.yaml, then "
                  f"`deckstudio build {name}`.")


@app.command()
def validate(deck: str = typer.Argument(help="Deck name or path")):
    """Schema validation + design lint. Exit code 1 on schema errors."""
    deck_dir = _deck_dir(deck)
    loaded = _load(deck_dir)
    console.print(f"[green]{OK} spec is valid[/green] — {len(loaded.spec.slides)} slides")

    from .validate.spec_lint import lint

    warnings = lint(loaded.spec)
    if warnings:
        console.print(f"[yellow]{len(warnings)} design suggestion(s):[/yellow]")
        for w in warnings:
            console.print(f"  [yellow]•[/yellow] {w}")
    else:
        console.print(f"[green]{OK} no design suggestions[/green]")


@app.command()
def build(
    deck: str = typer.Argument(help="Deck name or path"),
    no_animations: bool = typer.Option(False, "--no-animations",
                                       help="Skip animation injection entirely"),
    preview: bool = typer.Option(False, "--preview",
                                 help="Also render PNG previews (needs LibreOffice)"),
):
    """Compile spec.yaml into a versioned .pptx (never overwrites old versions)."""
    from .engine.builder import build_deck
    from .validate.build_check import check_build

    deck_dir = _deck_dir(deck)
    loaded = _load(deck_dir)
    deck_name = deck_dir.name.lstrip("_")

    result = build_deck(
        loaded.spec,
        output_dir=OUTPUT_DIR,
        deck_name=deck_name,
        enable_animations=not no_animations,
    )
    for w in result.warnings:
        console.print(f"  [yellow]warning:[/yellow] {w}")

    problems = check_build(result.output_path, loaded.spec)
    if problems:
        console.print("[red]Build smoke-check FAILED (engine bug — do not edit the "
                      "spec to work around this):[/red]")
        for p in problems:
            console.print(f"  [red]{BAD}[/red] {p}")
        raise typer.Exit(1)

    _log_build(deck_dir, result)
    console.print(f"[green]{OK} built[/green] {result.output_path.relative_to(REPO_ROOT)} "
                  f"({result.slide_count} slides, v{result.version})")

    if preview:
        from .validate.render import render_previews

        images = render_previews(result.output_path)
        if images is None:
            console.print("[yellow]LibreOffice not found — previews skipped "
                          "(the deck itself is fine).[/yellow]")
        elif not images:
            console.print("[yellow]LibreOffice could not convert the deck — "
                          "previews skipped (the deck itself is fine).[/yellow]")
        else:
            console.print(f"[green]{OK} previews:[/green] {images[0].parent}")


@app.command()
def ingest(
    files: list[Path] = typer.Argument(help="Source files (.pdf .docx .xlsx .md .txt)"),
    deck: str = typer.Option(..., "--deck", help="Deck to attach the digests to"),
):
    """Turn source documents into markdown digests under decks/<name>/sources/."""
    from .ingest.digest import ingest_file

    deck_dir = _deck_dir(deck)
    sources = deck_dir / "sources"
    for f in files:
        if not f.exists():
            console.print(f"[red]{f} does not exist[/red]")
            raise typer.Exit(2)
        out = ingest_file(f, sources)
        console.print(f"[green]{OK}[/green] {f.name} -> {out.relative_to(REPO_ROOT)}")


@app.command()
def extract(
    pptx_file: Path = typer.Argument(help="Existing .pptx to beautify"),
    deck: str = typer.Option(..., "--deck", help="Deck project to extract into"),
):
    """Extract an existing deck into a draft spec (extracted.yaml) + gap report."""
    from .ingest.pptx_extract import extract_pptx

    deck_dir = _deck_dir(deck)
    if not pptx_file.exists():
        console.print(f"[red]{pptx_file} does not exist[/red]")
        raise typer.Exit(2)
    yaml_path, report_path = extract_pptx(pptx_file, deck_dir)
    console.print(f"[green]{OK} extracted[/green] {yaml_path.relative_to(REPO_ROOT)}")
    console.print(f"[green]{OK} gap report[/green] {report_path.relative_to(REPO_ROOT)}")
    console.print("Next: read the report, re-outline with better slide types, and "
                  "write the real spec.yaml (do NOT just build extracted.yaml as-is).")


@app.command()
def doctor():
    """Check the environment: deps, tokens, template, brand fonts installed."""
    console.print(f"deckstudio {__version__}")
    ok = True

    try:
        tokens = load_tokens()
        console.print(f"[green]{OK} brand/tokens.yaml loads[/green]")
    except Exception as e:
        console.print(f"[red]{BAD} brand/tokens.yaml failed to load: {e}[/red]")
        raise typer.Exit(1) from None

    template = tokens.brand_dir / "template.pptx"
    if template.exists():
        console.print(f"[green]{OK} brand/template.pptx present[/green]")
    else:
        console.print("[yellow]• brand/template.pptx missing — building on a clean "
                      "16:9 base (fine until brand intake).[/yellow]")

    if tokens.logo_default is None:
        console.print("[yellow]• no logo asset yet — slides will simply omit the "
                      "logo (add during brand intake).[/yellow]")
    else:
        console.print(f"[green]{OK} logo assets found[/green]")

    installed = _installed_fonts()
    if installed is None:
        console.print("[yellow]• could not enumerate installed fonts on this OS — "
                      "verify brand fonts manually.[/yellow]")
    else:
        for role, spec in (("heading", tokens.heading_font), ("body", tokens.body_font)):
            if spec.name in installed:
                console.print(f"[green]{OK} {role} font '{spec.name}' installed[/green]")
            elif spec.fallback in installed:
                console.print(f"[yellow]• {role} font '{spec.name}' NOT installed — "
                              f"PowerPoint will substitute; fallback '{spec.fallback}' "
                              "is available. Ask IT to install the brand font.[/yellow]")
            else:
                ok = False
                console.print(f"[red]{BAD} neither {role} font '{spec.name}' nor fallback "
                              f"'{spec.fallback}' is installed.[/red]")

    from .validate.render import soffice_available

    if soffice_available():
        console.print(f"[green]{OK} LibreOffice found — visual previews available[/green]")
    else:
        console.print("[yellow]• LibreOffice not found — previews unavailable "
                      "(optional; decks build fine without it).[/yellow]")

    raise typer.Exit(0 if ok else 1)


def _installed_fonts() -> set[str] | None:
    """Best-effort set of installed font family names (Windows/mac/linux)."""
    import platform

    system = platform.system()
    names: set[str] = set()
    try:
        if system == "Windows":
            import winreg

            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts")
            for i in range(winreg.QueryInfoKey(key)[1]):
                value_name, _, _ = winreg.EnumValue(key, i)
                names.add(value_name.split(" (")[0].strip())
                names.add(value_name.split(" (")[0].split(" Bold")[0].split(" Italic")[0].strip())
        else:
            import subprocess

            out = subprocess.run(["fc-list", ":", "family"], capture_output=True,
                                 text=True, timeout=20)
            if out.returncode != 0:
                return None
            for line in out.stdout.splitlines():
                for fam in line.split(","):
                    names.add(fam.strip())
    except Exception:
        return None
    return names or None


@app.command()
def types():
    """List the slide types the engine can build (see playbooks/slide-type-catalog.md)."""
    from .engine.registry import registered_types

    for t in registered_types():
        console.print(f"  • {t}")


def _log_build(deck_dir: Path, result) -> None:
    import subprocess

    log = deck_dir / "build_log.md"
    try:
        sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT,
                             capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        sha = "unknown"
    line = f"- v{result.version}: {result.output_path.name} (repo @ {sha})\n"
    header = f"# Build log: {deck_dir.name}\n\n"
    if log.exists():
        log.write_text(log.read_text(encoding="utf-8") + line, encoding="utf-8")
    else:
        log.write_text(header + line, encoding="utf-8")


if __name__ == "__main__":
    app()
