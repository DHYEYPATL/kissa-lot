"""How we refuse the average sentence.

Models converge on the most likely story. Reddit's working fixes are
not "write better." They are constraints that sit *before* the draft:

- Contrastive priming: notice the first instinct, set it aside.
- An owned fact the model cannot invent (a wage, a street, a smell).
- A banned-slop list (copper, ozone, not-X-but-Y).
- Voice prints that may not collide.
- Audio-only: if it cannot be heard, it is not in the script.
"""

from __future__ import annotations

import re
from typing import Any

SLOP = (
    "copper",
    "ozone",
    "pennies on the tongue",
    "tapestry",
    "symphony of",
    "labyrinth",
    "gossamer",
    "ethereal",
    "iridescent",
    "luminous",
    "something shifts behind",
    "the silence stretches",
    "a weight settled",
    "breath hitch",
    "jaw tighten",
    "not a hero",
    "just a man with",
    "and for now, that was enough",
    "surgical precision",
    "welcome to our",
    "in this episode we will",
)

FIRST_INSTINCT = {
    "regional family drama": "A secret recipe heals the family. The camera weeps.",
    "mythic thriller": "A file with no name. Another file. Another file.",
    "campus dark romance": "The powerful one is a monster. She is the only one who sees it.",
}


def contrastive_rule() -> str:
    return (
        "Before writing: notice the first instinct for premise, structure, "
        "voice, and scene. Set it aside. Choose an option that shares no "
        "obvious pattern with it. Do not moralize the ending. Do not "
        "explain the theme. Audio only — if it cannot be heard, cut it."
    )


def refused_instinct(genre: str) -> str:
    return FIRST_INSTINCT.get(genre, "The most filmed version of this premise.")


def scan_slop(text: str) -> list[str]:
    low = (text or "").lower()
    hits = [w for w in SLOP if w in low]
    if re.search(r"\bnot [^.]+, but\b", low):
        hits.append("not-X-but-Y construction")
    if low.count("something") >= 3:
        hits.append("vague 'something' interiority")
    return hits


def voice_collision(speeches: list[str]) -> str:
    cleaned = [re.sub(r"\W+", " ", s).lower().strip() for s in speeches if s]
    if len(cleaned) < 2:
        return ""
    tokens = [set(s.split()) for s in cleaned]
    shared = tokens[0]
    for t in tokens[1:]:
        shared &= t
    shared -= {"the", "a", "and", "to", "of", "in", "she", "he", "i"}
    if len(shared) >= 4:
        return "voices share too many words — listeners will lose who is speaking"
    return ""


def booth_packet(title: str, characters: list[Any], script: str, minutes: float) -> dict:
    voices = []
    used = set()
    palette = ["low dry", "bright mid", "private whisper", "gravel night", "thin bright"]
    for i, c in enumerate(characters or []):
        tag = getattr(c, "voice", None) or palette[i % len(palette)]
        if tag in used:
            tag = palette[(i + 2) % len(palette)]
        used.add(tag)
        name = getattr(c, "name", f"V{i+1}")
        voices.append({"name": name, "tag": tag, "must_differ": True})
    sfx = []
    for i, line in enumerate((script or "").splitlines()):
        if line.strip().upper().startswith("SFX"):
            sfx.append(
                {
                    "cue": i + 1,
                    "line": line.strip(),
                    "rule": "Name material and manner. Not 'door.' 'Steel latch, dry hands.'",
                }
            )
    if not sfx:
        sfx.append(
            {
                "cue": 1,
                "line": "SFX: one object the listener can hold",
                "rule": "One specific object. Reuse the room. Do not invent a second city.",
            }
        )
    return {
        "title": title,
        "runtime_min": minutes,
        "session_fit": "commute" if 11 <= minutes <= 16 else "adjust to 11–15",
        "night_safe": True,
        "audio_only": True,
        "atmo": "One room. Reuse it. Footsteps only if you can record them well.",
        "voices": voices,
        "sfx": sfx[:8],
        "rule": "Number cues. Record narration separate. No picture track.",
    }


def provenance(parallel_on: bool, gemini_on: bool, owned_fact: str) -> dict:
    return {
        "live_web": "Parallel Search" if parallel_on else "offline research brief",
        "draft": "Gemini" if gemini_on else "deterministic kitchen packet",
        "owned_fact": owned_fact or "(none — draft is more average)",
        "human_gate": "required before canary",
        "picture_track": "none — audio only",
    }
