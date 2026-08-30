from __future__ import annotations

import os
from typing import Any

from kissa_lot.models import ResearchBundle, SourceHit


def _parallel_client(api_key: str):
    # Official Parallel Python SDK. Imported and called at runtime for the
    # Agentic Cinema Parallel track — not a README-only mention.
    from parallel import Parallel

    return Parallel(api_key=api_key)


def _hits_from_search(search: Any, bucket: str) -> list[SourceHit]:
    hits: list[SourceHit] = []
    results = getattr(search, "results", None) or []
    for item in results:
        excerpts = list(getattr(item, "excerpts", None) or [])
        hits.append(
            SourceHit(
                title=getattr(item, "title", "") or "Untitled source",
                url=getattr(item, "url", "") or "",
                publish_date=str(getattr(item, "publish_date", "") or "") or None,
                excerpts=excerpts[:4],
                query_bucket=bucket,
            )
        )
    return hits


def parallel_web_search(
    objective: str,
    search_queries: list[str],
    mode: str | None = None,
) -> list[SourceHit]:
    """Call Parallel Search API at runtime.

    This function is both an orchestrator primitive and an ADK FunctionTool.
    """
    api_key = os.environ.get("PARALLEL_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "PARALLEL_API_KEY is missing. Get a free key at https://platform.parallel.ai"
        )

    client = _parallel_client(api_key)
    chosen_mode = mode or os.environ.get("PARALLEL_SEARCH_MODE", "fast")
    search = client.search(
        objective=objective,
        search_queries=search_queries[:5],
        mode=chosen_mode,
    )
    return _hits_from_search(search, bucket="ad-hoc")


def research_story(
    title: str,
    logline: str,
    genres: list[str],
    locations: list[str],
    themes: list[str],
) -> ResearchBundle:
    """Four Parallel searches that match how development actually works.

    1. Audience desire / raw reviews (Reddit, Letterboxd, forums)
    2. Market comps and 2025–2026 theatrical/streaming trends
    3. Cultural / factual authenticity for the story world
    4. Production feasibility for named locations
    """
    genre_blob = ", ".join(genres) or "drama"
    theme_blob = ", ".join(themes) or "family"
    loc_blob = ", ".join(locations[:3]) or "unspecified city"

    audience_obj = (
        "Find what real movie audiences and indie film communities said in the last "
        "six months about what they want from cinema: authenticity, horror, regional "
        f"stories, clip-worthy moments, comfort vs novelty. Story context: {title}. {logline}"
    )
    market_obj = (
        "Find 2025-2026 film market research and box-office / streaming trend reports "
        f"relevant to {genre_blob} and culturally specific or regional cinema. "
        "Prefer last six months. Include what mid-budget films are failing at."
    )
    auth_obj = (
        f"Fact-check and culturally ground this story world. Title: {title}. "
        f"Logline: {logline}. Themes: {theme_blob}. Locations: {loc_blob}. "
        "Find primary-source or recent reporting that a writer should not invent."
    )
    prod_obj = (
        f"Find production, permitting, or filming-in facts for these locations: {loc_blob}. "
        "Also find recent guidance on low-budget night shoots, company moves, and "
        "why indie films stall in pre-production."
    )

    return ResearchBundle(
        audience=parallel_web_search(
            audience_obj,
            [
                "movie audience trends 2026 authenticity",
                "reddit what audiences want cinema",
                f"{genre_blob} film audience reviews 2026",
            ],
        ),
        market=parallel_web_search(
            market_obj,
            [
                "2026 film industry trends regional cinema",
                "box office midbudget drama decline 2026",
                f"{genre_blob} streaming commission trends",
            ],
        ),
        authenticity=parallel_web_search(
            auth_obj,
            [
                f"{loc_blob} culture recent news",
                f"{theme_blob} oral storytelling cinema",
                f"{title} comparable true stories",
            ],
        ),
        production=parallel_web_search(
            prod_obj,
            [
                f"filming in {loc_blob} permits",
                "indie film pre-production bottlenecks 2026",
                "low budget night shoot cost",
            ],
        ),
    )
