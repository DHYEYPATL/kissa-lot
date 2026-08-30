"""Deterministic production-format parser and complexity scoring.

Pure deterministic logic without external LLM dependencies.
"""

from __future__ import annotations

import re
from collections import defaultdict
from pydantic import BaseModel, Field


class SceneBeat(BaseModel):
    index: int = 1
    heading: str = ""
    int_ext: str = "INT"
    day_night: str | None = None
    location: str = ""
    summary: str = ""
    characters: list[str] = Field(default_factory=list)
    props: list[str] = Field(default_factory=list)
    vfx_hint: bool = False


class ScriptBreakdown(BaseModel):
    title: str = ""
    logline: str = ""
    genre_guess: list[str] = Field(default_factory=list)
    themes: list[str] = Field(default_factory=list)
    characters: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    props: list[str] = Field(default_factory=list)
    scenes: list[SceneBeat] = Field(default_factory=list)
    night_scenes: int = 0
    int_count: int = 0
    ext_count: int = 0
    vfx_flags: list[str] = Field(default_factory=list)
    page_estimate: int = 1
    raw_excerpt: str = ""


class ComplexityReport(BaseModel):
    score: int = 10
    verdict: str = "GREEN"
    drivers: list[str] = Field(default_factory=list)
    cuts: list[str] = Field(default_factory=list)
    shooting_groups: list[dict] = Field(default_factory=list)


HEADING_RE = re.compile(
    r"^(INT\.|EXT\.|INT/EXT\.|I/E\.)\s+(.+?)(?:\s+[-\u2013\u2014]\s+|\s+)(DAY|NIGHT|DAWN|DUSK|MORNING|EVENING|CONTINUOUS|LATER)?\s*$",
    re.IGNORECASE,
)
CHARACTER_RE = re.compile(r"^[A-Z][A-Z0-9 '\-]{1,30}$")
VFX_WORDS = (
    "explode",
    "explosion",
    "cgi",
    "vfx",
    "spaceship",
    "dragon",
    "magic",
    "transform",
    "superpower",
    "blood spray",
    "crowd of thousands",
    "destroy the city",
    "alien",
    "ghost appears",
    "morph",
)


def _guess_genres(text: str) -> list[str]:
    lowered = text.lower()
    mapping = {
        "horror": ("haunt", "blood", "scream", "possess", "demon", "ghost", "slash"),
        "thriller": ("surveil", "chase", "gun", "secret", "kidnap", "threat"),
        "romance": ("kiss", "love", "heart", "wedding", "affair"),
        "comedy": ("joke", "laugh", "awkward", "sitcom", "prank"),
        "drama": ("mother", "father", "grief", "family", "guilt", "memory"),
        "crime": ("police", "detective", "heist", "mafia", "court"),
        "sci-fi": ("spaceship", "android", "colony", "quantum", "future"),
        "regional drama": ("village", "mother tongue", "temple", "mohalla", "nani", "aji"),
    }
    hits = [genre for genre, keys in mapping.items() if any(k in lowered for k in keys)]
    return hits[:3] or ["drama"]


def _guess_themes(text: str) -> list[str]:
    lowered = text.lower()
    mapping = {
        "belonging": ("home", "belong", "exile", "return"),
        "family duty": ("mother", "father", "daughter", "son", "duty"),
        "class": ("rent", "factory", "rich", "slum", "boss"),
        "faith vs science": ("temple", "priest", "lab", "doctor"),
        "first love": ("first love", "crush", "college"),
        "grief": ("funeral", "death", "gone", "widow"),
        "coming of age": ("school", "exam", "seventeen", "hostel"),
        "cultural memory": ("grandmother", "folktale", "kissa", "oral", "partition"),
    }
    return [theme for theme, keys in mapping.items() if any(k in lowered for k in keys)][:4]


def parse_screenplay(raw: str, title_hint: str = "") -> ScriptBreakdown:
    """Deterministic screenplay parser."""
    text = raw.strip()
    if not text:
        raise ValueError("Empty screenplay or logline.")

    lines = [ln.rstrip() for ln in text.splitlines()]
    first = next((ln.strip() for ln in lines if ln.strip()), "Untitled")
    title = title_hint.strip() or (first.title() if len(first) < 80 else "Untitled Qissa")

    scenes: list[SceneBeat] = []
    characters: list[str] = []
    locations: list[str] = []
    props: list[str] = []
    vfx_flags: list[str] = []
    current: SceneBeat | None = None
    body: list[str] = []

    def flush() -> None:
        nonlocal current, body
        if current is None:
            return
        current.summary = " ".join(body)[:400]
        scenes.append(current)
        current, body = None, []

    for ln in lines:
        stripped = ln.strip()
        heading = HEADING_RE.match(stripped)
        if heading:
            flush()
            int_ext = heading.group(1).upper().replace("I/E.", "INT/EXT.")
            loc = heading.group(2).strip(" -\u2013\u2014").title()
            tod = (heading.group(3) or "").upper() or None
            current = SceneBeat(
                index=len(scenes) + 1,
                heading=stripped,
                int_ext=int_ext,
                day_night=tod,
                location=loc,
            )
            if loc and loc not in locations:
                locations.append(loc)
            continue
        if current is None:
            continue
        if CHARACTER_RE.match(stripped) and stripped not in {"INT", "EXT", "FADE OUT", "FADE IN", "CUT TO"}:
            name = stripped.title() if stripped.isupper() else stripped
            if name not in current.characters:
                current.characters.append(name)
            if name not in characters and len(name) > 1:
                characters.append(name)
            continue
        lowered = stripped.lower()
        if any(w in lowered for w in VFX_WORDS):
            current.vfx_hint = True
            vfx_flags.append(stripped[:120])
        if re.search(r"\b(phone|letter|knife|gun|photograph|id card|key|notebook)\b", lowered):
            prop = re.search(r"\b(phone|letter|knife|gun|photograph|id card|key|notebook)\b", lowered)
            if prop:
                token = prop.group(1)
                if token not in props:
                    props.append(token)
                if token not in current.props:
                    current.props.append(token)
        body.append(stripped)

    flush()

    if not scenes:
        scenes = [
            SceneBeat(
                index=1,
                heading="TREATMENT",
                summary=text[:500],
            )
        ]

    night_scenes = sum(1 for s in scenes if (s.day_night or "").find("NIGHT") >= 0)
    int_count = sum(1 for s in scenes if (s.int_ext or "").startswith("INT"))
    ext_count = sum(1 for s in scenes if (s.int_ext or "").startswith("EXT"))
    words = len(text.split())
    page_estimate = max(1, words // 90)

    logline = text.split("\n\n")[0].strip()
    if len(logline) > 280:
        logline = logline[:277] + "..."

    return ScriptBreakdown(
        title=title,
        logline=logline,
        genre_guess=_guess_genres(text),
        themes=_guess_themes(text),
        characters=characters[:20],
        locations=locations[:20],
        props=props[:20],
        scenes=scenes[:80],
        night_scenes=night_scenes,
        int_count=int_count,
        ext_count=ext_count,
        vfx_flags=vfx_flags[:12],
        page_estimate=page_estimate,
        raw_excerpt=text[:1500],
    )


def score_complexity(breakdown: ScriptBreakdown) -> ComplexityReport:
    """Score schedule and budget risk for screenplay structures."""
    location_count = len(breakdown.locations) or 1
    night = breakdown.night_scenes
    vfx = len(breakdown.vfx_flags)
    cast = len(breakdown.characters)
    pages = breakdown.page_estimate
    ext = breakdown.ext_count

    score = 12
    drivers: list[str] = []
    cuts: list[str] = []

    if location_count >= 8:
        score += 28
        drivers.append(f"{location_count} distinct locations — each move burns coverage.")
        cuts.append("Collapse satellite locations into two hero interiors + one exterior block.")
    elif location_count >= 4:
        score += 16
        drivers.append(f"{location_count} locations. Fine if they cluster; fatal if they scatter.")
        cuts.append("Shoot same-block locations as one company day.")
    else:
        score += 4
        drivers.append(f"{location_count} location(s) — contained, which audiences of tactile drama reward.")

    if night >= 5:
        score += 22
        drivers.append(f"{night} night scenes. Night is a budget multiplier, not a mood.")
        cuts.append("Convert exposition nights to practical-interior night.")
    elif night >= 2:
        score += 10
        drivers.append(f"{night} night scenes. Budget the night shifts carefully.")

    if vfx:
        score += min(24, 6 * vfx)
        drivers.append(f"{vfx} VFX-leaning beats. Unplanned comps are the most expensive shots.")
        cuts.append("Decide the VFX approach in prep: locked plate vs. in-camera sound gag.")

    if cast >= 10:
        score += 14
        drivers.append(f"{cast} speaking characters. Availability slips the schedule.")
        cuts.append("Merge one-scene characters into existing roles.")
    elif cast >= 6:
        score += 6

    if ext >= 6:
        score += 8
        drivers.append("Exterior-heavy. Weather is an uncredited producer.")
        cuts.append("Build a cover-set interior for every exterior day.")

    if pages > 30 and location_count + night > 8:
        score += 10
        drivers.append("Page count plus logistics look like an overscoped schedule.")

    score = min(100, score)

    if score >= 70:
        verdict = "RED — lock fewer moving parts before you raise or schedule."
    elif score >= 40:
        verdict = "AMBER — shootable if you cut two locations or two nights."
    else:
        verdict = "GREEN — contained enough that taste, not logistics, is the risk."

    groups_map: dict[tuple[str, str], list[int]] = defaultdict(list)
    for scene in breakdown.scenes:
        key = (scene.location or "UNSPECIFIED", scene.day_night or "ANY")
        groups_map[key].append(scene.index)

    shooting_groups = [
        {
            "location": loc,
            "time_of_day": tod,
            "scenes": idxs,
            "note": "Keep this block together. Do not interleave another company move.",
        }
        for (loc, tod), idxs in groups_map.items()
    ]
    shooting_groups.sort(key=lambda g: g["scenes"][0] if g["scenes"] else 0)

    if not cuts:
        cuts.append("Protect the must-have emotional scene first. Coverage second.")

    return ComplexityReport(
        score=score,
        verdict=verdict,
        drivers=drivers,
        cuts=cuts,
        shooting_groups=shooting_groups[:12],
    )
