from __future__ import annotations

from qissa.agents import (
    apply_direction,
    build_ledger,
    criticize,
    decide_graduation,
    monetize,
    originality_scan,
    score_branches,
    score_twins,
    scout_trends,
    showrun,
    simulate_canary,
    _fallback_trend,
)
from qissa.catalog import find_title, bucket_bar
from qissa.state import CanaryReport, HumanDecision, SeriesState
from qissa.uniqueness import booth_packet, provenance, refused_instinct, scan_slop


def run_desk(
    seed: str,
    genre: str = "regional family drama",
    title: str = "",
    owned_fact: str = "",
) -> SeriesState:
    rescued = find_title(seed) or find_title(title)
    state = SeriesState(
        title=title or (rescued["title"] if rescued else "Untitled Qissa"),
        genre=(rescued["genre"] if rescued else genre),
        seed=seed,
        logline=seed,
        rescue_of=rescued["id"] if rescued else "",
        owned_fact=owned_fact.strip(),
    )
    state.steps.append("open_lot")
    if state.owned_fact:
        state.steps.append("owned_fact_locked")
    if rescued:
        state.steps.append(f"catalog_rescue:{rescued['id']}")

    try:
        state.trend = scout_trends(seed, state.genre)
        state.engines["parallel"] = "parallel-web.search"
        state.steps.append("trend_scout:parallel")
    except Exception as exc:
        state.trend = _fallback_trend()
        state.engines["parallel"] = f"fallback:{type(exc).__name__}"
        state.steps.append("trend_scout:fallback")

    state.status = "draft"
    state = showrun(state)
    state.steps.append("showrunner+writer")

    state.diagnoses = criticize(state)
    state.steps.append("canon_guard+retention_critic")

    state.twin_scores = score_twins(state)
    state.status = "twin"
    state.steps.append("twin_bench")

    state.branch_scores = score_branches(state)
    state.steps.append("interactive_branch_compare")

    state.ledger = build_ledger(state)
    state.steps.append("payoff_ledger")

    state.originality = originality_scan(state)
    state.steps.append("originality_guard")

    state.monetization = monetize(state)
    state.steps.append("ad_safe_tags")

    script = state.episodes[0].script if state.episodes else ""
    state.refused_instinct = refused_instinct(state.genre)
    state.slop_flags = scan_slop(" ".join([state.bible, script, state.logline]))
    state.booth = booth_packet(
        state.title,
        state.characters,
        script,
        state.episodes[0].minutes if state.episodes else 12,
    )
    state.provenance = provenance(
        "parallel" in (state.engines.get("parallel") or ""),
        "google-genai" in (state.engines.get("gemini") or ""),
        state.owned_fact,
    )
    state.steps.append("uniqueness+booth_packet")

    # Canary is strictly blocked until human approval
    bar = bucket_bar(state.genre)
    state.canary = CanaryReport(
        cohort_pct=3.0,
        opted_in=True,
        disclosed_ai=True,
        ran=False,
        blocked_reason="Canary waits for human greenlight. Opt-in 3% only. AI disclosed.",
        catalog_bar=bar["completion_bar"],
        vs_catalog="blocked",
    )
    state.status = "review"
    state.verdict = "HOLD FOR HUMAN GATE — twin bench scored; canary blocked until human approval."
    state.steps.append("human_gate_wait")
    return state


def human_gate(state: SeriesState, action: str, note: str = "") -> SeriesState:
    if action == "approve":
        state.human_decisions.append(HumanDecision(action="approve", note=note, cycle=state.cycle))
        state.canary = simulate_canary(state)
        state.steps.append("canary_opt_in_3pct")
        state = decide_graduation(state)
        if state.status not in {"graduate", "archive"}:
            if note.lower().startswith("override"):
                state.status = "graduate"
                state.verdict = "GRADUATE TO AUDIO (human override after canary)"
            else:
                state.status = state.status if state.status == "graduate" else "review"
        state.steps.append("human_approve")
        return state

    if action == "reject":
        state.human_decisions.append(HumanDecision(action="reject", note=note, cycle=state.cycle))
        state.status = "archive"
        state.verdict = "ARCHIVE + REWORK BRIEF"
        char_names = ", ".join(c.name for c in state.characters[:2])
        state.rework_brief = note or (
            f"Human producer rejected the packet.\n"
            f"SALVAGEABLE ASSETS: Characters ({char_names}), Owned Fact ('{state.owned_fact or 'none'}').\n"
            f"GUIDANCE: Keep the central personal relationship, rewrite scene 1 with higher stakes before minute 3."
        )
        state.steps.append("human_reject_archive")
        return state

    if state.cycle >= state.max_cycles:
        state.status = "archive"
        state.verdict = "ARCHIVE — iteration cap reached"
        state.rework_brief = (
            f"All {state.max_cycles} human direction cycles used without clearing the hit-bar.\n"
            f"Hand the story bible and characters ({', '.join(c.name for c in state.characters)}) to a human writer room."
        )
        state.steps.append("iteration_cap")
        return state

    # Action is 'direct'
    state = apply_direction(state, note or "Tighten agency in scene 1 before minute 4.")
    state.diagnoses = criticize(state)
    state.twin_scores = score_twins(state)
    state.branch_scores = score_branches(state)
    state.ledger = build_ledger(state)
    state.originality = originality_scan(state)
    state.monetization = monetize(state)
    
    # Keep canary blocked and hold for human gate review
    state.status = "review"
    state.verdict = f"HOLD FOR HUMAN GATE (Cycle {state.cycle}/{state.max_cycles}) — draft updated, twins re-scored."
    state.steps.append(f"human_direct_cycle_{state.cycle}")
    return state
