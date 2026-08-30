from __future__ import annotations

import re

from kissa_lot.models import SceneBeat, ScriptBreakdown

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
    """Deterministic production-format parser. No AI. Used as an ADK tool."""
    text = raw.strip()
    if not text:
        raise ValueError("Empty screenplay or logline.")

    lines = [ln.rstrip() for ln in text.splitlines()]
    first = next((ln.strip() for ln in lines if ln.strip()), "Untitled")
    title = title_hint.strip() or (first.title() if len(first) < 80 else "Untitled Kissa")

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
