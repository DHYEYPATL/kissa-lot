from __future__ import annotations

import os
from typing import Callable

from kissa_lot.gemini_client import synthesize_packet
from kissa_lot.models import GreenlightPacket, ResearchBundle, RunResult, SourceHit
from kissa_lot.tools.complexity import score_complexity
from kissa_lot.tools.parallel_search import research_story
from kissa_lot.tools.script_parse import parse_screenplay


ProgressCb = Callable[[str], None]


def _fallback_research(title: str, logline: str) -> ResearchBundle:
    """Used only when PARALLEL_API_KEY is absent so the UI still teaches the workflow.
    Live submissions must set the key — the Parallel client is still imported and
    called on the happy path.
    """
    note = (
        "Demo fixture. Replace by exporting PARALLEL_API_KEY. "
        "These notes summarize last-six-month public research used to design Kissa Lot."
    )
    fixtures = [
        SourceHit(
            title="CivicScience — What Americans want from movies (2026)",
            url="https://civicscience.com/what-americans-want-from-movies-right-now-as-moviegoing-rebounds/",
            publish_date="2026-06",
            excerpts=[
                "Story/plot, ticket cost, and cast drive the ticket. Franchise connection is last.",
                "Younger audiences want original or culturally relevant work; older audiences want comfort.",
            ],
            query_bucket="audience",
        ),
        SourceHit(
            title="Reddit r/Cinema — theaters as viral events",
            url="https://www.reddit.com/r/Cinema/",
            publish_date="2026-07",
            excerpts=[
                "Young viewers still go out. They go out for films that fragment into 20-second clips.",
                "Mid-budget dramas without a shareable moment are ignored, not hated.",
            ],
            query_bucket="audience",
        ),
        SourceHit(
            title="Storytella — why indie films stall before day one",
            url="https://storytella.ai/blog/indie-film-pre-production",
            publish_date="2026-05",
            excerpts=[
                "Script lock, informal locations, and casting without a schedule kill more films than cameras do.",
            ],
            query_bucket="production",
        ),
        SourceHit(
            title="Regional and tactile cinema, 2026",
            url="https://www.shop.bottegadelsarto.com/feed/2026-film-industry-trends-the-shift-no-one-saw-coming-920000",
            publish_date="2026-05",
            excerpts=[
                "Regional-language films drive a majority of Indian admissions. Authenticity beats polish.",
            ],
            query_bucket="market",
        ),
    ]
    return ResearchBundle(
        audience=fixtures[:2],
        market=[fixtures[3]],
        authenticity=[
            SourceHit(
                title=f"Authenticity brief for {title}",
                url="https://docs.parallel.ai/search/search-quickstart",
                excerpts=[note, logline[:180]],
                query_bucket="authenticity",
            )
        ],
        production=[fixtures[2]],
    )


def _fallback_packet(title: str, logline: str, verdict: str) -> GreenlightPacket:
    return GreenlightPacket(
        working_title=title,
        polished_logline=logline,
        audience_desire=(
            "Younger crowds will leave the house for a story that feels locally true and "
            "contains one image they can clip. Older crowds want comfort. Do not try to be both."
        ),
        why_now=(
            "2026 research shows franchise habit is weak, horror is rising, and culturally "
            "specific emotion travels. A contained kissa with one unforgettable object can ride that."
        ),
        comps=["Regional family dramas with one genre spike", "Low-location horror with analog texture"],
        risks=["Overscoped locations", "Night work without a cover set", "Generic 'universal' rewriting that sands off the accent"],
        authenticity_notes=["Keep the mother tongue in the kitchen scenes. Subtitle. Do not flatten."],
        clip_moments=["A single practical image the trailer can live on — an object, a look, a sound."],
        greenlight_verdict="CONTAIN THEN SHOOT" if "GREEN" not in verdict else "PACKAGE AND PITCH",
        confidence="medium",
    )


def run_development(raw_text: str, title_hint: str = "", progress: ProgressCb | None = None) -> RunResult:
    def emit(msg: str) -> None:
        if progress:
            progress(msg)

    steps: list[str] = []
    engines = {"gemini": "offline", "parallel": "offline"}

    emit("1/5 Parsing screenplay or treatment…")
    breakdown = parse_screenplay(raw_text, title_hint=title_hint)
    steps.append("parse_screenplay")

    emit("2/5 Scoring production complexity…")
    complexity = score_complexity(breakdown)
    steps.append("score_complexity")

    emit("3/5 Researching live web via Parallel Search API…")
    try:
        research = research_story(
            title=breakdown.title,
            logline=breakdown.logline,
            genres=breakdown.genre_guess,
            locations=breakdown.locations,
            themes=breakdown.themes,
        )
        engines["parallel"] = "parallel-web.search"
        steps.append("parallel_web_search x4")
    except Exception as exc:
        emit(f"Parallel unavailable ({exc}). Using design-research fixtures.")
        research = _fallback_research(breakdown.title, breakdown.logline)
        steps.append(f"parallel_fallback: {exc}")

    emit("4/5 Asking Gemini to write the greenlight packet…")
    try:
        packet = synthesize_packet(breakdown, complexity, research)
        model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        engines["gemini"] = model
        steps.append("gemini.generate_content")
    except Exception as exc:
        emit(f"Gemini unavailable ({exc}). Using structured fallback packet.")
        packet = _fallback_packet(breakdown.title, breakdown.logline, complexity.verdict)
        packet.citations = research.all_hits()[:6]
        steps.append(f"gemini_fallback: {exc}")

    emit("5/5 Packet locked.")
    steps.append("assemble_packet")
    return RunResult(
        breakdown=breakdown,
        complexity=complexity,
        research=research,
        packet=packet,
        engines=engines,
        steps=steps,
    )
