from __future__ import annotations

import json
import os
from typing import Any

from kissa_lot.models import (
    ComplexityReport,
    GreenlightPacket,
    ResearchBundle,
    ScriptBreakdown,
    SourceHit,
)


PACKET_SCHEMA_HINT = """
Return ONLY valid JSON with keys:
working_title, polished_logline, audience_desire, why_now,
comps (array of strings), risks (array), authenticity_notes (array),
clip_moments (array of shareable 15-second moments the story already contains or should add),
greenlight_verdict (one of: \"PACKAGE AND PITCH\", \"REWRITE BEFORE PACKAGE\", \"CONTAIN THEN SHOOT\"),
confidence (high/medium/low),
citations (array of {title, url}).
Do not invent URLs. Only cite URLs present in the research brief.
"""


def _client():
    from google import genai

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if os.environ.get("GOOGLE_GENAI_USE_VERTEXAI", "").lower() == "true":
        return genai.Client(
            vertexai=True,
            project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
            location=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1"),
        )
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Create one in Google AI Studio or use Vertex."
        )
    return genai.Client(api_key=api_key)


def _model_name() -> str:
    return os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")


def _pack_hits(hits: list[SourceHit], limit: int = 6) -> str:
    blocks = []
    for hit in hits[:limit]:
        excerpt = " | ".join(hit.excerpts[:2])[:400]
        blocks.append(f"- {hit.title} ({hit.url}) [{hit.publish_date or 'n.d.'}] :: {excerpt}")
    return "\n".join(blocks) or "- none"


def synthesize_packet(
    breakdown: ScriptBreakdown,
    complexity: ComplexityReport,
    research: ResearchBundle,
) -> GreenlightPacket:
    """Gemini writes the development packet. Parallel supplies the ground truth."""
    prompt = f"""You are the development desk at a small but serious studio called Kissa Lot.
Kissa means story. Your job is not to flatter the writer. Your job is to tell them
whether this story earns a crowd in 2026, and what to cut so it can actually shoot.

Writer material
Title: {breakdown.title}
Logline/excerpt: {breakdown.logline}
Genres: {', '.join(breakdown.genre_guess)}
Themes: {', '.join(breakdown.themes)}
Characters: {', '.join(breakdown.characters)}
Locations: {', '.join(breakdown.locations)}
Night scenes: {breakdown.night_scenes}
VFX flags: {'; '.join(breakdown.vfx_flags) or 'none'}
Complexity score {complexity.score}/100 — {complexity.verdict}
Drivers: {' / '.join(complexity.drivers)}
Suggested cuts: {' / '.join(complexity.cuts)}

AUDIENCE RESEARCH (last-six-month web, via Parallel Search):
{_pack_hits(research.audience)}

MARKET / TREND RESEARCH:
{_pack_hits(research.market)}

AUTHENTICITY / FACTUAL GROUNDING:
{_pack_hits(research.authenticity)}

PRODUCTION FEASIBILITY:
{_pack_hits(research.production)}

Write for a filmmaker who has a day job. Be specific. Name the desire you heard
in the research (authenticity, culturally specific emotion, horror, clip-able
moments, comfort vs novelty) and map it onto THIS story. If the story is generic
IP-flavored, say so.

{PACKET_SCHEMA_HINT}
"""
    client = _client()
    response = client.models.generate_content(
        model=_model_name(),
        contents=prompt,
    )
    text = (getattr(response, "text", None) or "").strip()
    data = _extract_json(text)
    citations = []
    allowed = {h.url for h in research.all_hits()}
    for raw in data.get("citations") or []:
        url = raw.get("url") if isinstance(raw, dict) else None
        title = raw.get("title") if isinstance(raw, dict) else ""
        if url and url in allowed:
            citations.append(SourceHit(title=title or url, url=url, query_bucket="cited"))
    if not citations:
        citations = research.all_hits()[:6]

    return GreenlightPacket(
        working_title=str(data.get("working_title") or breakdown.title),
        polished_logline=str(data.get("polished_logline") or breakdown.logline),
        audience_desire=str(data.get("audience_desire") or ""),
        why_now=str(data.get("why_now") or ""),
        comps=list(data.get("comps") or []),
        risks=list(data.get("risks") or complexity.drivers),
        authenticity_notes=list(data.get("authenticity_notes") or []),
        clip_moments=list(data.get("clip_moments") or []),
        greenlight_verdict=str(data.get("greenlight_verdict") or complexity.verdict),
        confidence=str(data.get("confidence") or "medium"),
        citations=citations,
    )


def _extract_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
        if cleaned.endswith("```"):
            cleaned = cleaned[: cleaned.rfind("```")]
        cleaned = cleaned.strip()
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start >= 0 and end > start:
            try:
                parsed = json.loads(cleaned[start : end + 1])
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass
    return {}
