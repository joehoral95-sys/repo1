"""The deck spec schema — the contract between the agent and the engine.

Design rules encoded here on purpose:
- No colors, fonts, or positions. Only semantic hints (emphasize, sentiment,
  highlight, animate) that the engine maps to brand styling.
- Per-type content limits (max stats, max agenda items, bullet length caps)
  so validation errors teach spec authors to write BETTER slides, not just
  valid ones. Keep limit error messages actionable.
- Every slide has a stable `id` so feedback like "make slide `exam-trend`
  punchier" survives slide insertion/reordering.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

MAX_BULLET_CHARS = 160
MAX_TITLE_CHARS = 90

Animate = Literal["none", "fade", "build"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


# --------------------------------------------------------------------
# Deck-level metadata
# --------------------------------------------------------------------
class DeckMeta(StrictModel):
    title: str
    subtitle: str | None = None
    audience: str | None = Field(None, description="Who will see this deck")
    intent: str | None = Field(None, description="What the deck must achieve")
    tone: str | None = None
    date: str | None = None
    footer: str | None = Field(None, description="Overrides brand default footer")
    animations: Literal["off", "subtle"] = Field(
        "off", description="Animations are OPT-IN: some renderers (iOS Quick "
        "Look, web previews) mis-composite animated slides. Enable 'subtle' "
        "only for decks presented from desktop PowerPoint.")


# --------------------------------------------------------------------
# Shared slide fields
# --------------------------------------------------------------------
class SlideBase(StrictModel):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9\-]*$",
                    description="Stable handle, e.g. 'exam-trend'")
    title: str | None = None
    kicker: str | None = Field(
        None, description="Small letter-spaced eyebrow above the title, "
        "e.g. 'AT A GLANCE' or 'KPI METRICS · 2 OF 2'")
    notes: str | None = Field(None, description="Speaker notes")
    animate: Animate = "none"

    @field_validator("title")
    @classmethod
    def title_length(cls, v: str | None) -> str | None:
        if v and len(v) > MAX_TITLE_CHARS:
            raise ValueError(
                f"title is {len(v)} chars (max {MAX_TITLE_CHARS}). "
                "Titles should be one crisp assertion — trim it."
            )
        return v


def _check_bullets(bullets: list[str], where: str) -> list[str]:
    for i, b in enumerate(bullets):
        if len(b) > MAX_BULLET_CHARS:
            raise ValueError(
                f"{where} bullet {i + 1} is {len(b)} chars (max {MAX_BULLET_CHARS}). "
                "Slides aren't documents — move detail to speaker notes."
            )
    return bullets


# --------------------------------------------------------------------
# Slide types
# --------------------------------------------------------------------
class TitleSlide(SlideBase):
    type: Literal["title"]
    title: str
    subtitle: str | None = None
    presenter: str | None = None


class PreviewMetric(StrictModel):
    label: str
    value: str
    status: Literal["on_track", "watch", "pending"] | None = None


class SectionSlide(SlideBase):
    type: Literal["section"]
    title: str
    subtitle: str | None = None
    number: int | None = Field(None, ge=1, le=20, description="Optional big section number")
    preview: list[PreviewMetric] = Field(
        default_factory=list, max_length=6,
        description="Optional right-side teaser of the metrics this section covers")


class AgendaSlide(SlideBase):
    type: Literal["agenda"]
    items: list[str] = Field(min_length=2, max_length=6)

    @field_validator("items")
    @classmethod
    def items_short(cls, v: list[str]) -> list[str]:
        return _check_bullets(v, "agenda")


class Bullet(StrictModel):
    text: str
    sub: list[str] = Field(default_factory=list, max_length=4)

    @field_validator("text")
    @classmethod
    def text_short(cls, v: str) -> str:
        _check_bullets([v], "content")
        return v

    @field_validator("sub")
    @classmethod
    def sub_short(cls, v: list[str]) -> list[str]:
        return _check_bullets(v, "sub-")


class ContentSlide(SlideBase):
    """Title + bullets. The escape hatch — prefer a more visual type when one fits."""

    type: Literal["content"]
    title: str
    bullets: list[str | Bullet] = Field(min_length=1, max_length=6)

    @field_validator("bullets")
    @classmethod
    def bullets_short(cls, v: list[str | Bullet]) -> list[str | Bullet]:
        _check_bullets([b for b in v if isinstance(b, str)], "content")
        return v


class Stat(StrictModel):
    value: str = Field(description="Display value, e.g. '33,412' or '4.3%'")
    label: str
    delta: str | None = Field(None, description="e.g. '+2.1% vs Q1'")
    arrow: Literal["up", "down", "flat", "none"] = "none"
    sentiment: Literal["good", "bad", "neutral"] = Field(
        "neutral", description="Colors the delta: good=green, bad=red. "
        "A falling lapse rate is arrow=down, sentiment=good.")
    target: str | None = Field(
        None, description="Context line under the value, e.g. 'YTD target 34.0K · FY 81.0K'")
    status: Literal["on_track", "watch", "pending"] | None = Field(
        None, description="Status dot in the card corner: green/amber/gray")


class BigNumberSlide(SlideBase):
    type: Literal["big_number"]
    title: str
    stats: list[Stat] = Field(min_length=1, max_length=4)


class ComparisonSide(StrictModel):
    heading: str
    bullets: list[str] = Field(min_length=1, max_length=5)

    @field_validator("bullets")
    @classmethod
    def bullets_short(cls, v: list[str]) -> list[str]:
        return _check_bullets(v, "comparison")


class ComparisonSlide(SlideBase):
    type: Literal["comparison"]
    title: str
    left: ComparisonSide
    right: ComparisonSide
    emphasize: Literal["left", "right", "none"] = "none"
    badge: str | None = Field(
        None, max_length=24,
        description="Chip on the emphasized panel, e.g. 'Recommended' — omit for no chip")


class Milestone(StrictModel):
    label: str
    date: str | None = None
    done: bool = False


class TimelineSlide(SlideBase):
    type: Literal["timeline"]
    title: str
    milestones: list[Milestone] = Field(min_length=2, max_length=6)


class IconItem(StrictModel):
    icon: str | None = Field(
        None, description="Icon name from brand/assets/icons/: growth, people, "
        "cost, clock, target, shield, idea, alert, doc, globe (or a filename)")
    heading: str
    text: str = Field(max_length=MAX_BULLET_CHARS)


class IconRowSlide(SlideBase):
    type: Literal["icon_row"]
    title: str
    items: list[IconItem] = Field(min_length=2, max_length=4)


class QuoteSlide(SlideBase):
    type: Literal["quote"]
    text: str = Field(max_length=280)
    attribution: str | None = None


class ProgressItem(StrictModel):
    label: str
    percent: float = Field(ge=0, le=100)


class ProgressSlide(SlideBase):
    """Progress rings — 'how far along are we' as a visual, not a number list."""

    type: Literal["progress"]
    title: str
    items: list[ProgressItem] = Field(min_length=1, max_length=4)
    caption: str | None = Field(None, max_length=160)


class TableSlide(SlideBase):
    type: Literal["table"]
    title: str
    columns: list[str] = Field(min_length=2, max_length=6)
    rows: list[list[str]] = Field(min_length=1, max_length=8)
    emphasize_col: int | None = Field(
        None, ge=0, description="0-based column index to highlight")

    @model_validator(mode="after")
    def rows_match_columns(self) -> TableSlide:
        ncols = len(self.columns)
        for i, row in enumerate(self.rows):
            if len(row) != ncols:
                raise ValueError(
                    f"row {i + 1} has {len(row)} cells but there are {ncols} columns")
        if self.emphasize_col is not None and self.emphasize_col >= ncols:
            raise ValueError(f"emphasize_col {self.emphasize_col} out of range (0..{ncols - 1})")
        return self


ChartKind = Literal[
    "bar_clustered",   # vertical columns
    "bar_stacked",
    "bar_horizontal",
    "line",
    "area",
    "pie",
    "doughnut",
    "scatter",
]


class ChartSeries(StrictModel):
    name: str
    values: list[float | None]


class Highlight(StrictModel):
    series: str
    point: int = Field(ge=0, description="0-based category index to accent")


class ChartSpec(StrictModel):
    kind: ChartKind
    categories: list[str] = Field(min_length=1, max_length=24)
    series: list[ChartSeries] = Field(min_length=1, max_length=6)
    highlight: Highlight | None = None
    number_format: str | None = Field(None, description="e.g. '#,##0' or '0.0%'")
    y_title: str | None = None

    @model_validator(mode="after")
    def series_lengths(self) -> ChartSpec:
        ncats = len(self.categories)
        for s in self.series:
            if len(s.values) != ncats:
                raise ValueError(
                    f"series '{s.name}' has {len(s.values)} values but there are "
                    f"{ncats} categories — they must match")
        if self.kind in ("pie", "doughnut"):
            if len(self.series) != 1:
                raise ValueError(f"{self.kind} charts take exactly 1 series")
            if ncats > 6:
                raise ValueError(
                    f"{self.kind} with {ncats} slices is unreadable (max 6) — "
                    "use bar_horizontal for many categories")
        if self.highlight is not None:
            names = [s.name for s in self.series]
            if self.highlight.series not in names:
                raise ValueError(
                    f"highlight.series '{self.highlight.series}' not found; "
                    f"series are: {names}")
            if self.highlight.point >= ncats:
                raise ValueError(
                    f"highlight.point {self.highlight.point} out of range (0..{ncats - 1})")
        return self


class ChartSlide(SlideBase):
    type: Literal["chart"]
    title: str
    chart: ChartSpec
    insight: str | None = Field(
        None, max_length=200,
        description="The 'so what' — rendered as an accent callout under the chart")
    source: str | None = Field(None, description="Data source, rendered as a caption")


class ThanksSlide(SlideBase):
    type: Literal["thanks"]
    message: str | None = None
    contact: str | None = None


Slide = Annotated[
    TitleSlide | SectionSlide | AgendaSlide | ContentSlide | BigNumberSlide | ComparisonSlide | TimelineSlide | IconRowSlide | QuoteSlide | TableSlide | ChartSlide | ProgressSlide | ThanksSlide,
    Field(discriminator="type"),
]

SLIDE_TYPES = [
    "title", "section", "agenda", "content", "big_number", "comparison",
    "timeline", "icon_row", "quote", "table", "chart", "progress", "thanks",
]


class DeckSpec(StrictModel):
    deck: DeckMeta
    slides: list[Slide] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_ids(self) -> DeckSpec:
        seen: dict[str, int] = {}
        for i, s in enumerate(self.slides):
            if s.id in seen:
                raise ValueError(
                    f"duplicate slide id '{s.id}' (slides {seen[s.id] + 1} and {i + 1}) — "
                    "ids must be unique")
            seen[s.id] = i
        return self
