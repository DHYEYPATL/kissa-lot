"""Google ADK root agent for Kissa Lot.

Run with:
    adk web
or import root_agent from this module when deploying to Vertex AI Agent Engine.
"""

from __future__ import annotations

from kissa_lot.orchestrator import run_development
from kissa_lot.tools.parallel_search import parallel_web_search
from kissa_lot.tools.script_parse import parse_screenplay


def develop_kissa(screenplay_or_logline: str, title: str = "") -> dict:
    """Run the full Kissa Lot development desk on a logline or screenplay.

    Use this when a filmmaker pastes pages or a one-line kissa and needs a
    greenlight packet grounded in live web research.
    """
    result = run_development(screenplay_or_logline, title_hint=title)
    return result.model_dump()


def breakdown_pages(screenplay_or_logline: str, title: str = "") -> dict:
    """Parse production format without calling the network."""
    return parse_screenplay(screenplay_or_logline, title_hint=title).model_dump()


def search_production_web(objective: str, query_one: str, query_two: str = "", query_three: str = "") -> list[dict]:
    """Search the live web with Parallel so the agent never invents a citation."""
    queries = [q for q in (query_one, query_two, query_three) if q.strip()]
    hits = parallel_web_search(objective, queries)
    return [h.model_dump() for h in hits]


try:
    from google.adk import Agent

    root_agent = Agent(
        name="kissa_lot_agent",
        model="gemini-2.5-flash",
        description=(
            "Development desk for filmmakers. Turns a logline or screenplay into "
            "an audience-grounded greenlight packet using Parallel Search and a "
            "deterministic complexity score."
        ),
        instruction=(
            "You are Kissa Lot, a studio development agent. A kissa is a story. "
            "When the user pastes a logline or pages, call develop_kissa. "
            "When they ask a narrow research question, call search_production_web "
            "with a clear objective and 2-3 short keyword queries. "
            "Never invent URLs. Prefer the tool output over your prior. "
            "Be blunt about schedule risk. Speak like a producer who still loves movies."
        ),
        tools=[develop_kissa, breakdown_pages, search_production_web],
    )
except Exception:  # pragma: no cover - environments without ADK still run the API
    root_agent = None
