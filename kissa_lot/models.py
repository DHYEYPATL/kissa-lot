from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SourceHit(BaseModel):
    title: str
    url: str
    publish_date: str | None = None
    excerpts: list[str] = Field(default_factory=list)
    query_bucket: str = "general"


class SceneBeat(BaseModel):
    index: int
    heading: str
    int_ext: str | None = None
    day_night: str | None = None
    location: str | None = None
    summary: str = ""
    characters: list[str] = Field(default_factory=list)
    props: list[str] = Field(default_factory=list)
    vfx_hint: bool = False


class ScriptBreakdown(BaseModel):
    title: str
    logline: str
    genre_guess: list[str] = Field(default_factory=list)
    themes: list[str] = Field(default_factory=list)
    characters: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    props: list[str] = Field(default_factory=list)
    scenes: list[SceneBeat] = Field(default_factory=list)
    night_scenes: int = 0
    int_count: int = 0
    ext_count: int = 0
    vfx_flags: list[str] = Field(default_factory=list)
    page_estimate: int = 1
    raw_excerpt: str = ""


class ComplexityReport(BaseModel):
    score: int = Field(ge=0, le=100)
    verdict: str
    drivers: list[str] = Field(default_factory=list)
    cuts: list[str] = Field(default_factory=list)
    shooting_groups: list[dict[str, Any]] = Field(default_factory=list)


class ResearchBundle(BaseModel):
    audience: list[SourceHit] = Field(default_factory=list)
    market: list[SourceHit] = Field(default_factory=list)
    authenticity: list[SourceHit] = Field(default_factory=list)
    production: list[SourceHit] = Field(default_factory=list)

    def all_hits(self) -> list[SourceHit]:
        return self.audience + self.market + self.authenticity + self.production


class GreenlightPacket(BaseModel):
    working_title: str
    polished_logline: str
    audience_desire: str
    why_now: str
    comps: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    authenticity_notes: list[str] = Field(default_factory=list)
    clip_moments: list[str] = Field(default_factory=list)
    greenlight_verdict: str
    confidence: str
    citations: list[SourceHit] = Field(default_factory=list)


class RunResult(BaseModel):
    breakdown: ScriptBreakdown
    complexity: ComplexityReport
    research: ResearchBundle
    packet: GreenlightPacket
    engines: dict[str, str] = Field(default_factory=dict)
    steps: list[str] = Field(default_factory=list)
