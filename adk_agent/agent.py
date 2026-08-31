"""Google ADK root agent for Qissa Studio. No LangGraph. No OpenAI."""

from __future__ import annotations

import uuid
from qissa.catalog import bucket_bar, stalled_shows
from qissa.eval_harness import run_eval
from qissa.pipeline import human_gate, run_desk
from qissa.search import parallel_search
from qissa.sessions import get_session, save_session
from qissa.state import SeriesState


def open_qissa(
    seed: str,
    genre: str = "regional family drama",
    owned_fact: str = "",
    session_id: str = "",
) -> dict:
    """Run Trend Scout → Showrunner → Twin Bench → Critic → Originality.
    Stops at the human gate. Does not publish. Does not canary.
    owned_fact is a lived detail the model must not invent."""
    sid = session_id.strip() or f"adk-{uuid.uuid4().hex[:8]}"
    state = run_desk(seed, genre=genre, owned_fact=owned_fact)
    save_session(sid, state)
    save_session("current", state)
    data = state.model_dump()
    data["session_id"] = sid
    return data


def human_decide(action: str, note: str = "", session_id: str = "") -> dict:
    """action is approve | reject | direct. approve is what starts the 3% canary."""
    sid = session_id.strip() or "current"
    state = get_session(sid) or get_session("current")
    if state is None:
        return {"error": "no series on the lot. Call open_qissa first."}
    state = human_gate(state, action, note)
    save_session(sid, state)
    save_session("current", state)
    data = state.model_dump()
    data["session_id"] = sid
    return data


def search_live_web(objective: str, query_one: str, query_two: str = "") -> list[dict]:
    """Parallel Search API. Required partner runtime call."""
    return parallel_search(objective, [q for q in (query_one, query_two) if q])


def catalog_bars(genre: str = "regional family drama") -> dict:
    """Hit-bar for a genre bucket plus stalled titles that can be rescued."""
    return {"bar": bucket_bar(genre), "stalled": stalled_shows(genre)}


def eval_desk() -> dict:
    """Prove the critic catches a bad story and the planted clone."""
    return run_eval()


try:
    from google.adk import Agent

    root_agent = Agent(
        name="qissa_studio",
        model="gemini-2.5-flash",
        description="Human-in-the-loop greenlight loop for serialized audio fiction.",
        instruction=(
            "You are Qissa Studio. A qissa is a story. You do not replace writers. "
            "Call open_qissa on a seed and an owned_fact. Then wait. Call human_decide "
            "only when the user approves, rejects, or gives a direction note. Approve starts the 3% canary. "
            "Never invent Parallel URLs. If asked to prove the desk works, call eval_desk."
        ),
        tools=[open_qissa, human_decide, search_live_web, catalog_bars, eval_desk],
    )
except Exception:
    root_agent = None
