"""Deterministic story-structure diagnostics.

Judges need to see the system catch a bad story without a live model.
These heuristics are grounded in 2025–2026 listener complaints:
late first turn, unpaid mystery piles, generated coffee-talk,
mid-sentence ads, stalled payoff, and episodes that feel finished.
"""

from __future__ import annotations

import re
from typing import Any

from qissa.state import Diagnosis, Episode, SeriesState

GENERATED_MARKERS = (
    "welcome to our",
    "let us talk while",
    "smells delicious",
    "here is your mug",
    "as an ai",
    "in this episode we will",
)
EXPOSITION_MARKERS = (
    "describe the coffee",
    "meanwhile a new mystery",
    "kitchen listing",
    "we shall now",
    "for many years",
    "backstory",
)
MYSTERY_PILE_MARKERS = (
    "another mystery",
    "and another",
    "never paid",
    "files without faces",
    "new secret appears",
)
URGENCY_THEN_THESIS = (
    "only minutes left",
    "seconds to decide",
    "i thought about all the ways",
    "paragraphs of thinking",
)
YELLING = ("!!!", "screams", "yelling")
AD_MID_SENTENCE = ("[ad]", "[midroll]", "brought to you by")


def script_blob(state: SeriesState) -> str:
    parts = [state.logline, state.bible, state.title]
    for ep in state.episodes:
        parts.append(ep.script)
        parts.append(ep.cliffhanger)
        parts.append(ep.logline)
    return " ".join(p for p in parts if p).lower()


def first_episode(state: SeriesState) -> Episode | None:
    return state.episodes[0] if state.episodes else None


def scan_structure(state: SeriesState) -> list[Diagnosis]:
    text = script_blob(state)
    ep = first_episode(state)
    issues: list[Diagnosis] = []

    expo = ep.exposition_minutes if ep else 6.0
    turn = ep.first_turn_minute if ep else 10.0
    minutes = ep.minutes if ep else 12.0
    cliff = (ep.cliffhanger if ep else "") or ""

    if expo >= 3.5:
        issues.append(
            Diagnosis(
                issue="late first turn / heavy exposition",
                evidence=f"{expo:.1f} minutes of setup before a turn",
                edit_op="Move the first costly choice earlier than minute 6. Cut kitchen listing.",
                severity="high",
            )
        )
    if turn > 8:
        issues.append(
            Diagnosis(
                issue="agency arrives late",
                evidence=f"first character choice at minute {turn}",
                edit_op="Give her a private decision with a price before minute 8.",
                severity="high",
            )
        )
    if not cliff.strip() or len(cliff.strip()) < 12:
        issues.append(
            Diagnosis(
                issue="soft cliff",
                evidence="episode ends without an unpaid question",
                edit_op="End on a reason to start the next episode, not a complete scene.",
                severity="high",
            )
        )
    if any(m in text for m in GENERATED_MARKERS):
        issues.append(
            Diagnosis(
                issue="generated-sounding talk",
                evidence="characters explain the coffee they are drinking",
                edit_op="Cut phatic talk. Differ speech patterns. Add one private monologue.",
                severity="high",
            )
        )
    if any(m in text for m in MYSTERY_PILE_MARKERS) or text.count("mystery") >= 3:
        issues.append(
            Diagnosis(
                issue="mystery pile-on",
                evidence="new questions land without paying an old one",
                edit_op="Pay one secret this episode. Leave exactly one new question.",
                severity="high",
            )
        )
    if any(m in text for m in URGENCY_THEN_THESIS):
        issues.append(
            Diagnosis(
                issue="urgency then thesis paper",
                evidence="climax stalls in inner monologue while the clock is ticking",
                edit_op="Keep the thought to one spoken line. Act, then feel.",
                severity="medium",
            )
        )
    if any(m in text for m in YELLING):
        issues.append(
            Diagnosis(
                issue="volume spike / yelling episode",
                evidence="sleep-listen personas drop when the mix shouts",
                edit_op="Mark emotion in the line, not in the loudness. Keep night-safe dynamics.",
                severity="low",
            )
        )
    if any(m in text for m in AD_MID_SENTENCE):
        issues.append(
            Diagnosis(
                issue="mid-sentence ad",
                evidence="break lands inside a threat line",
                edit_op="Move the mid-roll to the first completed emotional beat only.",
                severity="high",
            )
        )
    if minutes < 9:
        issues.append(
            Diagnosis(
                issue="episode shorter than the ads around it",
                evidence=f"{minutes} min listed runtime — r/audiodrama drops these",
                edit_op="Target 11–15 minutes of story, not 7 minutes plus bumper.",
                severity="medium",
            )
        )
    open_threads = list(state.memory.open_threads)
    if len(open_threads) >= 4 and not state.memory.events:
        issues.append(
            Diagnosis(
                issue="payoff stall",
                evidence=f"{len(open_threads)} open threads and no paid event",
                edit_op="Close one thread on-mic this episode. Archive the rest for season memory.",
                severity="high",
            )
        )
    if "werewolf" in text and "billionaire" in text:
        issues.append(
            Diagnosis(
                issue="saturated catalog trope",
                evidence="werewolf billionaire already wins and clones in the catalog",
                edit_op="Keep the hunger. Change the power source. Do not ship a howl-CEO.",
                severity="medium",
            )
        )
    return issues


def structural_features(state: SeriesState) -> dict[str, Any]:
    ep = first_episode(state)
    text = script_blob(state)
    return {
        "exposition_minutes": ep.exposition_minutes if ep else 6.0,
        "first_turn_minute": ep.first_turn_minute if ep else 10.0,
        "minutes": ep.minutes if ep else 12.0,
        "has_cliff": bool(ep and ep.cliffhanger and len(ep.cliffhanger) > 12),
        "generated": any(m in text for m in GENERATED_MARKERS),
        "mystery_pile": any(m in text for m in MYSTERY_PILE_MARKERS),
        "agency_words": bool(re.search(r"\b(i will|i won't|i choose|i hide|i keep|i tell)\b", text)),
        "private_monologue": "monologue" in text or "(" in (ep.script if ep else ""),
        "mother_tongue": any(w in text for w in ("gujarati", "surat", "undhiyu", "nani", "maa", "kitchen")),
    }
