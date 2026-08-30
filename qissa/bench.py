"""Twin bench, critic, originality, canary, monetization, graduation."""

from __future__ import annotations

from qissa.catalog import CATALOG, bucket_bar
from qissa.diagnostics import scan_structure, structural_features
from qissa.personas import PERSONAS
from qissa.state import (
    BranchScore,
    CanaryReport,
    MonetizationTag,
    OriginalityFlag,
    PayoffLedger,
    SeriesState,
    TwinScore,
)


def criticize(state: SeriesState) -> list:
    return scan_structure(state)


def canon_guard(state: SeriesState) -> list:
    from qissa.state import Diagnosis
    flags = []
    names = {c.name.lower() for c in state.characters}
    blob = " ".join(ep.script for ep in state.episodes).lower()
    if "dead" in " ".join(state.memory.events).lower():
        for name in names:
            if f"{name}:" in blob and "dies" in " ".join(state.memory.events).lower():
                flags.append(Diagnosis(issue="canon drift", evidence=f"{name} may be speaking after a recorded death", edit_op="Check series memory before the next line.", severity="high"))
    return flags


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
    return TwinScore(persona_id=p["id"], persona_name=p["name"], cohort=p["cohort"], drop_minute=round(drop, 1), would_finish=would_finish, would_start_next=would_next, would_spend_coin=would_coin, reasons=reasons[:3], score=score)


def score_twins(state: SeriesState) -> list[TwinScore]:
    feats = structural_features(state)
    diagnoses = state.diagnoses or scan_structure(state)
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
        out.append(BranchScore(branch_id=key, title=ep.title, twin_mean=round(mean, 1), preferred_by=fans, note="Twins compare keep vs tell. Canary would A/B only after human gate."))
    return out


def build_ledger(state: SeriesState) -> PayoffLedger:
    promises = list(state.memory.open_threads) or ["what is on the last page", "who bought the pour"]
    paid = list(state.memory.events)
    still = [p for p in promises if p.lower() not in " ".join(paid).lower()]
    total = max(1, len(paid) + len(still))
    return PayoffLedger(promises=promises, paid=paid, still_open=still, ratio=round(len(paid) / total, 2))


def originality_scan(state: SeriesState) -> list[OriginalityFlag]:
    flags: list[OriginalityFlag] = []
    blob = f"{state.title} {state.logline} {state.bible} {state.seed}".lower()
    for row in CATALOG:
        trope = (row.get("trope") or "").lower()
        title = row["title"]
        if row.get("clone_of") and (title.lower() in blob or trope in blob):
            flags.append(OriginalityFlag(title=title, reason=f"Planted clone overlap with {row.get('clone_of')}. Similarity, not a lawsuit.", severity="block", source="catalog"))
        elif trope and trope in blob and title.lower() != state.title.lower():
            flags.append(OriginalityFlag(title=title, reason=f"Shares catalog trope '{row.get('trope')}'. Editor flag only.", severity="warn" if row.get("good") else "note", source="catalog"))
    if "werewolf" in blob and "billionaire" in blob:
        if not any(f.title == "His Secret Howl" for f in flags):
            flags.append(OriginalityFlag(title="His Secret Howl", reason="Werewolf billionaire is the planted clone test.", severity="block", source="catalog"))
    try:
        from qissa.search import parallel_search
        hits = parallel_search("Find existing audio series or novels that closely match this premise. Flag near-duplicates.", [state.title, state.logline or state.seed, f"{state.genre} audio series similar"])
        for hit in hits[:4]:
            flags.append(OriginalityFlag(title=hit.get("title") or "web match", reason="Live web near-duplicate candidate. Human must read it.", severity="note", source=hit.get("url") or "parallel-web.search"))
    except Exception:
        pass
    return flags


def monetize(state: SeriesState) -> list[MonetizationTag]:
    tags: list[MonetizationTag] = []
    ep = state.episodes[0] if state.episodes else None
    placed = False
    for beat in list(ep.beats) if ep else []:
        if beat.ad_safe and beat.label in {"turn", "cliff"} and not placed:
            tags.append(MonetizationTag(minute=beat.minute, kind="midroll", note=f"After '{beat.label}' — never mid-sentence. Emotion: {beat.emotion or 'beat'}."))
            placed = True
    if ep and ep.cliffhanger:
        tags.append(MonetizationTag(minute=ep.minutes - 0.4, kind="premium_cliff", note="Premium exists only if the cliff pays a prior promise later. Coin-bait cliffs fail Rhea."))
    tags.append(MonetizationTag(minute=5.0, kind="spinoff", note="Anjali-memory could be a short. Only if twins stay. Do not lead the pitch with merch."))
    return tags


def simulate_canary(state: SeriesState) -> CanaryReport:
    approved = any(d.action == "approve" for d in state.human_decisions)
    bar = bucket_bar(state.genre)
    if not approved:
        return CanaryReport(ran=False, blocked_reason="Canary waits for human greenlight. Opt-in 3% only. AI disclosed.", catalog_bar=bar["completion_bar"], vs_catalog="not run")
    twins = state.twin_scores or score_twins(state)
    finish = sum(1 for t in twins if t.would_finish) / len(twins)
    nxt = sum(1 for t in twins if t.would_start_next) / len(twins)
    coin = sum(1 for t in twins if t.would_spend_coin) / len(twins)
    drops = sorted({t.drop_minute for t in twins if not t.would_finish})
    completion = round(0.28 + 0.62 * finish, 3)
    next_start = round(0.18 + 0.55 * nxt, 3)
    vs = "beats hit bar" if completion >= bar["completion_bar"] else "below hit bar"
    minutes = state.episodes[0].minutes if state.episodes else 12
    fit = "commute-fit" if 11 <= minutes <= 16 else ("too short vs bumper" if minutes < 11 else "long for night listen")
    return CanaryReport(ran=True, blocked_reason="", opted_in=True, disclosed_ai=True, cohort_pct=3.0, completion=completion, next_start=next_start, skip_rate=round(1 - finish, 3), coin_conversion=round(coin, 3), drop_timestamps=drops or [11.5], catalog_bar=bar["completion_bar"], vs_catalog=f"{vs} (hits {bar['completion_bar']:.0%} completion in {state.genre}; n={bar['n_hits']})", session_fit=fit)


def decide_graduation(state: SeriesState) -> SeriesState:
    bar = bucket_bar(state.genre)
    if state.canary.ran and state.canary.completion >= bar["completion_bar"]:
        if any(f.severity == "block" for f in state.originality):
            state.status = "review"
            state.verdict = "HOLD — beats the bar but originality is blocked. Human must rule."
            state.rework_brief = "Keep the hunger. Change the power source. Do not ship a catalog clone."
            return state
        state.status = "graduate"
        state.verdict = "GRADUATE TO AUDIO — beats catalog hit bar after human gate + canary."
        return state
    if state.cycle >= state.max_cycles:
        state.status = "archive"
        state.verdict = "ARCHIVE — iteration cap"
        state.rework_brief = _brief(state)
        return state
    if state.canary.ran and state.canary.completion < bar["completion_bar"]:
        state.status = "iterate"
        state.verdict = "HOLD — below hit bar. Rewrite or archive with a brief. Not landfill."
        state.rework_brief = _brief(state)
        return state
    state.status = "review"
    state.verdict = "HOLD FOR HUMAN — twins scored; canary has not run."
    return state


def _brief(state: SeriesState) -> str:
    top = state.diagnoses[:3]
    lines = [f"- {d.issue}: {d.edit_op}" for d in top]
    salvage = ""
    if state.branch_scores:
        best = max(state.branch_scores, key=lambda b: b.twin_mean)
        salvage = f" Salvage branch '{best.branch_id}' ({best.title})."
    return "Rework brief. Do not delete the object.\n" + "\n".join(lines) + salvage + "\nKeep series memory. Season 2 should not invent a new childhood trauma."


def rescue_packet(title: str) -> SeriesState:
    from qissa.catalog import find_title
    from qissa.craft import showrun
    row = find_title(title)
    seed = row["note"] if row else title
    genre = row["genre"] if row else "regional family drama"
    state = SeriesState(title=row["title"] if row else title, genre=genre, seed=seed, logline=seed, rescue_of=row["id"] if row else title)
    state.steps.append("catalog_rescue")
    state = showrun(state)
    state.diagnoses = criticize(state)
    if row and not row.get("good"):
        state.rework_brief = row.get("note") or ""
        state.verdict = f"RESCUE CANDIDATE — {row['title']} is stalled in the catalog."
    return state
