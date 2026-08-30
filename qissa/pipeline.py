from __future__ import annotations

from qissa.agents import (
    apply_direction,
    criticize,
    decide_graduation,
    monetize,
    originality_scan,
    scout_trends,
    score_twins,
    showrun,
    simulate_canary,
    _fallback_trend,
)
from qissa.state import HumanDecision, SeriesState


def run_desk(seed: str, genre: str = "regional family drama", title: str = "") -> SeriesState:
    state = SeriesState(title=title or "Untitled Qissa", genre=genre, seed=seed, logline=seed)
    state.steps.append("open_lot")

    try:
        state.trend = scout_trends(seed, genre)
        state.engines["parallel"] = "parallel-web.search"
        state.steps.append("trend_scout:parallel")
    except Exception as exc:
        state.trend = _fallback_trend()
        state.engines["parallel"] = f"fallback:{exc}"
        state.steps.append(f"trend_scout:fallback:{exc}")

    state.status = "draft"
    state = showrun(state)
    state.steps.append("showrunner+writer")

    state.diagnoses = criticize(state)
    state.steps.append("canon_guard+retention_critic")

    state.twin_scores = score_twins(state)
    state.status = "twin"
    state.steps.append("twin_bench")

    state.originality = originality_scan(state)
    state.steps.append("originality_guard")

    state.monetization = monetize(state)
    state.steps.append("monetization_tags")

    state.canary = simulate_canary(state)
    state.status = "canary"
    state.steps.append("canary_opt_in_3pct")

    state.status = "review"
    state = decide_graduation(state)
    state.steps.append("human_gate_wait")
    return state


def human_gate(state: SeriesState, action: str, note: str = "") -> SeriesState:
    if action == "approve":
        state.human_decisions.append(HumanDecision(action="approve", note=note, cycle=state.cycle))
        state = decide_graduation(state)
        if state.status != "graduate":
            state.status = "graduate"
            state.verdict = "GRADUATE TO AUDIO (human override after review)"
        state.steps.append("human_approve")
        return state
    if action == "reject":
        state.human_decisions.append(HumanDecision(action="reject", note=note, cycle=state.cycle))
        state.status = "archive"
        state.verdict = "ARCHIVE + REWORK BRIEF"
        state.rework_brief = note or state.rework_brief or "Human rejected the packet. Keep the object, cut the spectacle."
        state.steps.append("human_reject_archive")
        return state
    if state.cycle >= state.max_cycles:
        state.status = "archive"
        state.verdict = "ARCHIVE — iteration cap"
        state.rework_brief = "Four cycles used. Hand the bible to a human writer."
        return state
    state = apply_direction(state, note or "Tighten agency in scene 3.")
    state.diagnoses = criticize(state)
    state.twin_scores = score_twins(state)
    state.canary = simulate_canary(state)
    state = decide_graduation(state)
    state.steps.append(f"human_direct_cycle_{state.cycle}")
    return state
