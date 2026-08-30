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
from qissa.catalog import find_title
from qissa.state import HumanDecision, SeriesState


def run_desk(seed: str, genre: str = "regional family drama", title: str = "") -> SeriesState:
    """Trend → bible → critic → twins → originality → HUMAN GATE.

    Canary does *not* run here. That was a v1 fallacy. Real users (even 3%)
    wait for a human. Rescue mode fires if the seed matches a stalled title.
    """
    rescued = find_title(seed) or find_title(title)
    state = SeriesState(
        title=title or (rescued["title"] if rescued else "Untitled Qissa"),
        genre=(rescued["genre"] if rescued else genre),
        seed=seed,
        logline=seed,
        rescue_of=rescued["id"] if rescued else "",
    )
    state.steps.append("open_lot")
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

    state.canary = simulate_canary(state)
    state.status = "review"
    state = decide_graduation(state)
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
        state.rework_brief = note or state.rework_brief or (
            "Human rejected the packet. Keep the object, cut the spectacle."
        )
        state.steps.append("human_reject_archive")
        return state
    if state.cycle >= state.max_cycles:
        state.status = "archive"
        state.verdict = "ARCHIVE — iteration cap"
        state.rework_brief = "Four cycles used. Hand the bible to a human writer."
        state.steps.append("iteration_cap")
        return state
    state = apply_direction(state, note or "Tighten agency in scene 3.")
    state.diagnoses = criticize(state)
    state.twin_scores = score_twins(state)
    state.branch_scores = score_branches(state)
    state.ledger = build_ledger(state)
    state.originality = originality_scan(state)
    state.monetization = monetize(state)
    state = decide_graduation(state)
    state.steps.append(f"human_direct_cycle_{state.cycle}")
    return state
