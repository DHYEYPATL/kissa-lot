"""Google ADK root agent for Qissa Studio. No LangGraph. No OpenAI."""

from __future__ import annotations

from qissa.catalog import bucket_bar, stalled_shows
from qissa.eval_harness import run_eval
from qissa.pipeline import human_gate, run_desk
from qissa.search import parallel_search
from qissa.state import SeriesState

SESSIONS: dict[str, SeriesState] = {}


def open_qissa(seed: str, genre: str = "regional family drama") -> dict:
    """Run Trend Scout → Showrunner → Twin Bench → Critic → Originality.
    Stops at the human gate. Does not publish. Does not canary."""
    state = run_desk(seed, genre=genre)
    SESSIONS["current"] = state
    return state.model_dump()


def human_decide(action: str, note: str = "") -> dict:
    """action is approve | reject | direct. approve is what starts the 3% canary."""
    state = SESSIONS.get("current")
    if state is None:
        return {"error": "no series on the lot"}
    state = human_gate(state, action, note)
    SESSIONS["current"] = state
    return state.model_dump()


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
        description="Human-in-the-loop greenlight loop for serialized audio.",
        instruction=(
            "You are Qissa Studio. A qissa is a story. You do not replace writers. "
            "Call open_qissa on a seed. Then wait. Call human_decide only when the "
            "user accepts, rejects, or gives a note. Approve is what starts canary. "
            "Never invent Parallel URLs. If asked to prove the desk works, call eval_desk."
        ),
        tools=[open_qissa, human_decide, search_live_web, catalog_bars, eval_desk],
    )
except Exception:
    root_agent = None
