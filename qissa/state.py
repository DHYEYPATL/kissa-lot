from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

Status = Literal[
    "draft",
    "twin",
    "review",
    "canary",
    "iterate",
    "graduate",
    "archive",
]


class TrendBrief(BaseModel):
    tropes_rising: list[str] = Field(default_factory=list)
    tropes_saturated: list[str] = Field(default_factory=list)
    archetypes: list[str] = Field(default_factory=list)
    regional_moments: list[str] = Field(default_factory=list)
    listener_pains: list[str] = Field(default_factory=list)
    tone: str = ""
    citations: list[dict[str, Any]] = Field(default_factory=list)
    engine: str = "offline"


class Character(BaseModel):
    name: str
    goal: str = ""
    wound: str = ""
    speech: str = ""
    voice: str = "medium"
    secrets: list[str] = Field(default_factory=list)


class Beat(BaseModel):
    minute: float
    label: str
    text: str
    emotion: str = ""
    ad_safe: bool = False


class Episode(BaseModel):
    number: int
    title: str
    minutes: float = 12.0
    logline: str = ""
    script: str = ""
    beats: list[Beat] = Field(default_factory=list)
    cliffhanger: str = ""
    branch_id: str | None = None
    first_turn_minute: float = 8.0
    exposition_minutes: float = 4.0


class TwinScore(BaseModel):
    persona_id: str
    persona_name: str
    cohort: Literal["high_retention", "low_retention"]
    drop_minute: float
    would_finish: bool
    would_start_next: bool
    would_spend_coin: bool = False
    reasons: list[str] = Field(default_factory=list)
    score: int = 0


class Diagnosis(BaseModel):
    issue: str
    evidence: str
    edit_op: str
    severity: Literal["high", "medium", "low"] = "medium"


class OriginalityFlag(BaseModel):
    title: str
    reason: str
    severity: Literal["block", "warn", "note"] = "warn"
    source: str = ""


class MonetizationTag(BaseModel):
    minute: float
    kind: Literal["midroll", "premium_cliff", "spinoff"]
    note: str


class HumanDecision(BaseModel):
    action: Literal["approve", "reject", "direct"]
    note: str = ""
    cycle: int = 0


class SeriesMemory(BaseModel):
    events: list[str] = Field(default_factory=list)
    secrets_unrevealed: list[str] = Field(default_factory=list)
    growth: list[str] = Field(default_factory=list)
    relationships: list[str] = Field(default_factory=list)
    tone_rules: list[str] = Field(default_factory=list)
    open_threads: list[str] = Field(default_factory=list)


class PayoffLedger(BaseModel):
    promises: list[str] = Field(default_factory=list)
    paid: list[str] = Field(default_factory=list)
    still_open: list[str] = Field(default_factory=list)
    ratio: float = 0.0
    rule: str = "Pay one. Leave one. Never 174 episodes of the same wound."


class CanaryReport(BaseModel):
    cohort_pct: float = 3.0
    opted_in: bool = True
    disclosed_ai: bool = True
    ran: bool = False
    blocked_reason: str = "waiting on human greenlight"
    completion: float = 0.0
    next_start: float = 0.0
    skip_rate: float = 0.0
    coin_conversion: float = 0.0
    drop_timestamps: list[float] = Field(default_factory=list)
    vs_catalog: str = ""
    catalog_bar: float = 0.0
    session_fit: str = ""


class BranchScore(BaseModel):
    branch_id: str
    title: str
    twin_mean: float = 0.0
    preferred_by: list[str] = Field(default_factory=list)
    note: str = ""


class SeriesState(BaseModel):
    title: str
    genre: str = "regional family drama"
    logline: str = ""
    seed: str = ""
    bible: str = ""
    characters: list[Character] = Field(default_factory=list)
    spine: list[str] = Field(default_factory=list)
    episodes: list[Episode] = Field(default_factory=list)
    branches: dict[str, Episode] = Field(default_factory=dict)
    branch_scores: list[BranchScore] = Field(default_factory=list)
    trend: TrendBrief = Field(default_factory=TrendBrief)
    twin_scores: list[TwinScore] = Field(default_factory=list)
    diagnoses: list[Diagnosis] = Field(default_factory=list)
    originality: list[OriginalityFlag] = Field(default_factory=list)
    monetization: list[MonetizationTag] = Field(default_factory=list)
    memory: SeriesMemory = Field(default_factory=SeriesMemory)
    ledger: PayoffLedger = Field(default_factory=PayoffLedger)
    human_decisions: list[HumanDecision] = Field(default_factory=list)
    canary: CanaryReport = Field(default_factory=CanaryReport)
    revisions: list[str] = Field(default_factory=list)
    before_after: list[dict[str, str]] = Field(default_factory=list)
    cycle: int = 0
    max_cycles: int = 4
    status: Status = "draft"
    engines: dict[str, str] = Field(default_factory=dict)
    steps: list[str] = Field(default_factory=list)
    verdict: str = ""
    rework_brief: str = ""
    rescue_of: str = ""
    owned_fact: str = ""
    refused_instinct: str = ""
    dialect_score: float = 0.85
    dialect_verdict: str = "High Authenticity"
    dark_pattern_risk: str = "Low / Safe"
    slop_flags: list[str] = Field(default_factory=list)
    booth: dict[str, Any] = Field(default_factory=dict)
    provenance: dict[str, str] = Field(default_factory=dict)
    extras: dict[str, Any] = Field(default_factory=dict)
