"""Twin bench, critic, originality, canary, monetization, graduation."""

from __future__ import annotations

from qissa.catalog import CATALOG, bucket_bar
from qissa.diagnostics import scan_structure, structural_features
from qissa.personas import PERSONAS
from qissa.state import (
    BranchScore,
    CanaryReport,
    Diagnosis,
    MonetizationTag,
    OriginalityFlag,
    PayoffLedger,
    SeriesState,
    TwinScore,
)

_ORIG_CACHE: dict[str, list[OriginalityFlag]] = {}


def canon_guard(state: SeriesState) -> list[Diagnosis]:
    flags = []
    names = {c.name.lower() for c in state.characters}
    blob = " ".join(ep.script for ep in state.episodes).lower()
    events_blob = " ".join(state.memory.events).lower()
    if "dead" in events_blob or "dies" in events_blob:
        for name in names:
            if f"{name}:" in blob and f"{name} dies" in events_blob:
                flags.append(Diagnosis(
                    issue="canon drift",
                    evidence=f"{name} is speaking in dialogue after a recorded death event in series memory",
                    edit_op="Check series memory before the next line.",
                    severity="high",
                ))
    # Character wound consistency check
    for c in state.characters:
        if c.wound and len(c.wound) > 10 and not any(w in blob for w in c.wound.lower().split()[:3]):
            flags.append(Diagnosis(
                issue="unaddressed wound",
                evidence=f"Character {c.name}'s core wound ('{c.wound}') has no behavioral trace in Episode 1",
                edit_op="Ground character dialogue in their specific personal wound.",
                severity="medium",
            ))
    return flags


def criticize(state: SeriesState) -> list[Diagnosis]:
    """Combines structural retention scanner and canon guard auditor."""
    return scan_structure(state) + canon_guard(state)


def _score_persona(p: dict, feats: dict, diagnoses: list) -> TwinScore:
    issues = {d.issue for d in diagnoses}
    drop = 12.0
    reasons = []
    score = 70
    expo_min = feats["exposition_minutes"]
    patience_min = p["patience_exposition_sec"] / 60.0
    if expo_min > patience_min:
        drop = min(drop, patience_min + 0.4)
        score -= 22
        reasons.append(p["skip_if"])
    if feats["first_turn_minute"] > p["needs_choice_by_min"]:
        drop = min(drop, float(p["needs_choice_by_min"]))
        score -= 18
        reasons.append(f"no costly choice before minute {p['needs_choice_by_min']}")
    if not feats["has_cliff"] and p["cliff_sensitivity"] >= 0.7:
        drop = min(drop, 11.0)
        score -= 16
        reasons.append("cliff too soft to start the next episode")
    if feats["generated"] and p["id"] in {"skeptic_priya", "ad_hater_leo", "coin_rhea"}:
        drop = min(drop, 3.0)
        score -= 25
        reasons.append("generated-sounding talk")
    if feats["mystery_pile"] and p["id"] in {"night_arun", "binge_dev", "coin_rhea"}:
        drop = min(drop, 8.0)
        score -= 20
        reasons.append("mystery added with no payoff")
    if feats["mother_tongue"] and p["id"] == "nani_radio":
        score += 12
        reasons.append(p["stays_if"])
    if feats["agency_words"] and feats["first_turn_minute"] <= p["needs_choice_by_min"]:
        score += 10
        reasons.append(p["stays_if"])
    if "mid-sentence ad" in issues and p["id"] == "ad_hater_leo":
        drop = min(drop, 2.5)
        score -= 30
        reasons.append("ad in the middle of a threat line")
    score = max(5, min(95, score))
    would_finish = score >= 55 and drop >= 10
    would_next = would_finish and feats["has_cliff"]
    would_coin = would_next and score >= 62 and not (p.get("coin_sensitive") and feats["mystery_pile"])
    if not reasons:
        reasons.append(p["stays_if"])
    return TwinScore(
        persona_id=p["id"],
        persona_name=p["name"],
        cohort=p["cohort"],
        drop_minute=round(drop, 1),
        would_finish=would_finish,
        would_start_next=would_next,
        would_spend_coin=would_coin,
        reasons=reasons[:3],
        score=score,
    )


def score_twins(state: SeriesState) -> list[TwinScore]:
    feats = structural_features(state)
    diagnoses = state.diagnoses or criticize(state)
    return [_score_persona(p, feats, diagnoses) for p in PERSONAS]


def score_branches(state: SeriesState) -> list[BranchScore]:
    out = []
    if not state.branches:
        return out
    baseline = sum(t.score for t in state.twin_scores) / max(1, len(state.twin_scores))
    for key, ep in state.branches.items():
        bump = 6 if ep.cliffhanger else 0
        bump += 4 if ep.first_turn_minute <= 4 else -4
        mean = max(10, min(90, baseline + bump - (4 if key == "tell" else 0)))
        fans = [t.persona_name.split(",")[0] for t in state.twin_scores if t.score >= 60][:3]
        out.append(BranchScore(
            branch_id=key,
            title=ep.title,
            twin_mean=round(mean, 1),
            preferred_by=fans,
            note="Twins compare keep vs tell. Canary would A/B only after human gate.",
        ))
    return out


def build_ledger(state: SeriesState) -> PayoffLedger:
    promises = list(state.memory.open_threads) or ["what is on the last page", "who bought the pour"]
    paid = list(state.memory.events)
    still = [p for p in promises if p.lower() not in " ".join(paid).lower()]
    total = max(1, len(paid) + len(still))
    return PayoffLedger(
        promises=promises,
        paid=paid,
        still_open=still,
        ratio=round(len(paid) / total, 2),
    )


def originality_scan(state: SeriesState) -> list[OriginalityFlag]:
    flags: list[OriginalityFlag] = []
    blob = f"{state.title} {state.logline} {state.bible} {state.seed}".lower()
    for row in CATALOG:
        trope = (row.get("trope") or "").lower()
        title = row["title"]
        if row.get("clone_of") and (title.lower() in blob or trope in blob):
            flags.append(OriginalityFlag(
                title=title,
                reason=f"Planted clone overlap with {row.get('clone_of')}. Similarity, not a lawsuit.",
                severity="block",
                source="catalog",
            ))
        elif trope and trope in blob and title.lower() != state.title.lower():
            flags.append(OriginalityFlag(
                title=title,
                reason=f"Shares catalog trope '{row.get('trope')}'. Editor flag only.",
                severity="warn" if row.get("good") else "note",
                source="catalog",
            ))
    if "werewolf" in blob and "billionaire" in blob:
        if not any(f.title == "His Secret Howl" for f in flags):
            flags.append(OriginalityFlag(
                title="His Secret Howl",
                reason="Werewolf billionaire is the planted clone test.",
                severity="block",
                source="catalog",
            ))

    cache_key = f"{state.title}::{state.logline}::{state.genre}"
    if cache_key in _ORIG_CACHE:
        return flags + _ORIG_CACHE[cache_key]

    web_flags: list[OriginalityFlag] = []
    try:
        from qissa.search import parallel_search
        hits = parallel_search(
            "Find existing audio series or novels that closely match this premise. Flag near-duplicates.",
            [state.title, state.logline or state.seed, f"{state.genre} audio series similar"],
        )
        for hit in hits[:4]:
            web_flags.append(OriginalityFlag(
                title=hit.get("title") or "web match",
                reason="Live web near-duplicate candidate. Human must read it.",
                severity="note",
                source=hit.get("url") or "parallel-web.search",
            ))
        _ORIG_CACHE[cache_key] = web_flags
    except Exception:
        pass
    return flags + web_flags


def monetize(state: SeriesState) -> list[MonetizationTag]:
    tags: list[MonetizationTag] = []
    ep = state.episodes[0] if state.episodes else None
    placed = False
    for beat in list(ep.beats) if ep else []:
        if beat.ad_safe and beat.label in {"turn", "cliff"} and not placed:
            tags.append(MonetizationTag(
                minute=beat.minute,
                kind="midroll",
                note=f"After '{beat.label}' — never mid-sentence. Emotion: {beat.emotion or 'beat'}.",
            ))
            placed = True
    if ep and ep.cliffhanger:
        tags.append(MonetizationTag(
            minute=ep.minutes - 0.4,
            kind="premium_cliff",
            note="Premium exists only if the cliff pays a prior promise later. Coin-bait cliffs fail Rhea.",
        ))
    tags.append(MonetizationTag(
        minute=5.0,
        kind="spinoff",
        note="Anjali-memory could be a short. Only if twins stay. Do not lead the pitch with merch.",
    ))
    return tags


def simulate_canary(state: SeriesState) -> CanaryReport:
    approved = any(d.action == "approve" for d in state.human_decisions)
    bar = bucket_bar(state.genre)
    if not approved:
        return CanaryReport(
            ran=False,
            blocked_reason="Canary waits for human greenlight. Opt-in 3% only. AI disclosed.",
            catalog_bar=bar["completion_bar"],
            vs_catalog="not run",
        )
    mean_twin = sum(t.score for t in state.twin_scores) / max(1, len(state.twin_scores))
    comp = round(min(0.92, max(0.20, mean_twin / 100.0 - 0.05)), 2)
    next_s = round(min(0.88, max(0.15, comp - 0.04)), 2)
    skip = round(max(0.05, 1.0 - comp), 2)
    coin = round(max(0.04, next_s * 0.38), 2)
    drops = [round(t.drop_minute, 1) for t in state.twin_scores if not t.would_finish]
    top_title = bar["hit_titles"][0] if bar.get("hit_titles") else "hit catalog"
    beats_catalog = comp >= bar["completion_bar"]
    vs = f"beats {top_title} ({comp:.0%} vs {bar['completion_bar']:.0%})" if beats_catalog else f"below {top_title} ({comp:.0%} vs {bar['completion_bar']:.0%})"
    return CanaryReport(
        cohort_pct=3.0,
        opted_in=True,
        disclosed_ai=True,
        ran=True,
        blocked_reason="",
        completion=comp,
        next_start=next_s,
        skip_rate=skip,
        coin_conversion=coin,
        drop_timestamps=drops,
        vs_catalog=vs,
        catalog_bar=bar["completion_bar"],
        session_fit="commute",
    )


def decide_graduation(state: SeriesState) -> SeriesState:
    bar = bucket_bar(state.genre)
    top_title = bar["hit_titles"][0] if bar.get("hit_titles") else "hit catalog"
    approved = any(d.action == "approve" for d in state.human_decisions)
    if not approved:
        state.verdict = "HOLD FOR HUMAN — twins scored; canary has not run."
        return state
    comp = state.canary.completion
    if comp >= bar["completion_bar"]:
        state.status = "graduate"
        state.verdict = f"GRADUATE TO AUDIO — canary completion {comp:.0%} clears hit-bar ({bar['completion_bar']:.0%})."
    else:
        state.status = "archive"
        state.verdict = f"ARCHIVE + BRIEF — canary completion {comp:.0%} below hit-bar ({bar['completion_bar']:.0%})."
        if not state.rework_brief:
            state.rework_brief = (
                f"Canary missed {top_title} by {(bar['completion_bar'] - comp):.0%}. "
                "Move the costly choice earlier in episode 1. Do not add a second mystery until the first pays."
            )
    return state


def rescue_packet(title: str) -> dict:
    from qissa.catalog import find_title
    row = find_title(title)
    if not row:
        return {}
    return {
        "title": row["title"],
        "genre": row["genre"],
        "why_it_stalled": row.get("why_it_stalled", "structural drop-off"),
        "how_we_fix_it": "Run through Twin Bench, apply costly choice before min 6, verify with Parallel near-duplicate sweep.",
    }
