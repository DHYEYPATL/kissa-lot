"""Google ADK root agent for Qissa Studio. No LangGraph. No OpenAI."""

from __future__ import annotations

from qissa.pipeline import human_gate, run_desk
from qissa.search import parallel_search
from qissa.state import SeriesState

SESSIONS: dict[str, SeriesState] = {}


def open_qissa(seed: str, genre: str = "regional family drama") -> dict:
    """Run Trend Scout to Canary. Stops at the human gate."""
    state = run_desk(seed, genre=genre)
    SESSIONS["current"] = state
    return state.model_dump()


def human_decide(action: str, note: str = "") -> dict:
    """action is approve | reject | direct."""
    state = SESSIONS.get("current")
    if state is None:
        return {"error": "no series on the lot"}
    state = human_gate(state, action, note)
    SESSIONS["current"] = state
    return state.model_dump()


def search_live_web(objective: str, query_one: str, query_two: str = "") -> list[dict]:
    """Parallel Search API. Required partner runtime call."""
    return parallel_search(objective, [q for q in (query_one, query_two) if q])


try:
    from google.adk import Agent

    root_agent = Agent(
        name="qissa_studio",
        model="gemini-2.5-flash",
        description="Human-in-the-loop greenlight loop for serialized audio.",
        instruction=(
            "You are Qissa Studio. A qissa is a story. You do not replace writers. "
            "Call open_qissa on a seed. Then wait. Call human_decide only when the "
            "user accepts, rejects, or gives a note. Never invent Parallel URLs."
        ),
        tools=[open_qissa, human_decide, search_live_web],
    )
except Exception:
    root_agent = None
