"""Load brand/tokens.yaml into a typed object every renderer consumes.

Design rule: renderers never hard-code colors, fonts, or sizes - they ask
the Tokens object. Rebranding the studio = editing brand/tokens.yaml.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt
from ruamel.yaml import YAML

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TOKENS_PATH = REPO_ROOT / "brand" / "tokens.yaml"


def _rgb(hexstr: str) -> RGBColor:
    return RGBColor.from_string(hexstr.lstrip("#"))


@dataclass
class FontSpec:
    name: str
    fallback: str

    def resolved(self, installed: set[str] | None = None) -> str:
        """Return the font to use; fall back when we know it's missing."""
        if installed is not None and self.name not in installed:
            return self.fallback
        return self.name


@dataclass
class Tokens:
    colors: dict[str, RGBColor]
    chart_series: list[RGBColor]
    heading_font: FontSpec
    body_font: FontSpec
    type_scale: dict[str, int]
    margin_in: float
    gutter_in: float
    title_top_in: float
    content_top_in: float
    chart_font_size: int
    logo_default: Path | None
    logo_dark_bg: Path | None
    footer_text: str
    show_page_numbers: bool
    brand_dir: Path = field(default_factory=lambda: REPO_ROOT / "brand")

    # ---- convenience accessors -------------------------------------
    def color(self, name: str) -> RGBColor:
        return self.colors[name]

    def pt(self, scale_key: str) -> Pt:
        return Pt(self.type_scale[scale_key])

    @property
    def margin(self):
        return Inches(self.margin_in)

    @property
    def gutter(self):
        return Inches(self.gutter_in)


def load_tokens(path: Path | str | None = None) -> Tokens:
    path = Path(path) if path else DEFAULT_TOKENS_PATH
    yaml = YAML(typ="safe")
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.load(f)

    colors_raw = raw["colors"]
    colors = {k: _rgb(v) for k, v in colors_raw.items() if k != "chart_series"}
    chart_series = [_rgb(v) for v in colors_raw["chart_series"]]

    brand_dir = path.parent

    def _asset(rel: str | None) -> Path | None:
        if not rel:
            return None
        p = brand_dir / rel
        return p if p.exists() else None

    logo_cfg = raw.get("logo", {})
    footer_cfg = raw.get("footer", {})
    layout = raw["layout"]

    return Tokens(
        colors=colors,
        chart_series=chart_series,
        heading_font=FontSpec(**raw["fonts"]["heading"]),
        body_font=FontSpec(**raw["fonts"]["body"]),
        type_scale=dict(raw["type_scale"]),
        margin_in=float(layout["margin_in"]),
        gutter_in=float(layout["gutter_in"]),
        title_top_in=float(layout.get("title_top_in", 0.45)),
        content_top_in=float(layout.get("content_top_in", 1.5)),
        chart_font_size=int(raw.get("charts", {}).get("font_size", 12)),
        logo_default=_asset(logo_cfg.get("default")),
        logo_dark_bg=_asset(logo_cfg.get("dark_bg")),
        footer_text=footer_cfg.get("text", ""),
        show_page_numbers=bool(footer_cfg.get("show_page_numbers", True)),
        brand_dir=brand_dir,
    )
