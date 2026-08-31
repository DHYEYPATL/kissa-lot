"""Deterministic story-structure diagnostics.

Judges need to see the system catch a bad story without a live model.
These heuristics are grounded in 2025–2026 listener complaints:
late first turn, unpaid mystery piles, generated coffee-talk,
mid-sentence ads, stalled payoff, coin walls, and flattened dialect.
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
AD_MID_SENTENCE = ("[ad]", "[midroll]", "brought to you by", "[ad-midroll]")


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
                edit_op="Move the first costly choice earlier than minute 5. Cut backstory listings.",
                severity="high",
            )
        )
    if turn > 8:
        issues.append(
            Diagnosis(
                issue="agency arrives late",
                evidence=f"first character choice at minute {turn}",
                edit_op="Give protagonist a private decision with a cost before minute 5.",
                severity="high",
            )
        )
    if not cliff.strip() or len(cliff.strip()) < 12:
        issues.append(
            Diagnosis(
                issue="soft cliff",
                evidence="episode ends without an urgent open question",
                edit_op="End on a hook that compels the next episode, not a settled scene.",
                severity="high",
            )
        )
    if any(m in text for m in GENERATED_MARKERS):
        issues.append(
            Diagnosis(
                issue="generated-sounding coffee talk",
                evidence="characters explain mundane feelings/actions with zero subtext",
                edit_op="Cut phatic talk. Differ speech rhythms. Add private subtext.",
                severity="high",
            )
        )
    if any(m in text for m in MYSTERY_PILE_MARKERS) or text.count("mystery") >= 3:
        issues.append(
            Diagnosis(
                issue="mystery pile-on",
                evidence="new questions land without resolving prior open threads",
                edit_op="Pay one secret this episode. Leave exactly one new question ('Pay 1, leave 1').",
                severity="high",
            )
        )
    if any(m in text for m in URGENCY_THEN_THESIS):
        issues.append(
            Diagnosis(
                issue="urgency then thesis paper",
                evidence="climax stalls in inner monologue while the clock is ticking",
                edit_op="Keep thoughts to one spoken line. Action first, contemplation second.",
                severity="medium",
            )
        )
    if any(m in text for m in YELLING):
        issues.append(
            Diagnosis(
                issue="volume spike / yelling mix",
                evidence="excessive exclamation/yelling drops night/sleep listeners",
                edit_op="Mark emotion in the line text, not loudness. Maintain night-safe dynamics.",
                severity="low",
            )
        )
    if any(m in text for m in AD_MID_SENTENCE):
        issues.append(
            Diagnosis(
                issue="mid-sentence ad placement",
                evidence="break lands inside active dialogue line",
                edit_op="Move mid-roll strictly after a completed emotional beat.",
                severity="high",
            )
        )
    if minutes < 9:
        issues.append(
            Diagnosis(
                issue="episode shorter than ads around it",
                evidence=f"{minutes} min listed runtime — r/audiodrama drops shows under 10m",
                edit_op="Target 11–15 minutes of story, avoiding short bumper padding.",
                severity="medium",
            )
        )
    
    # Owned fact preservation check
    if state.owned_fact and len(state.owned_fact.strip()) > 8:
        fact_words = [w for w in re.sub(r"\W+", " ", state.owned_fact.lower()).split() if len(w) > 3 and w not in {"with", "from", "that", "this", "still"}]
        if fact_words and not any(w in text for w in fact_words):
            sample_phrase = state.owned_fact[:50]
            issues.append(
                Diagnosis(
                    issue="owned fact flattened from dialogue",
                    evidence=f"Lived detail ('{sample_phrase}...') has zero presence in scene dialogue",
                    edit_op=f"Ground Scene 1 dialogue in the lived detail (e.g. Add character line mentioning '{sample_phrase}').",
                    severity="high",
                )
            )

    open_threads = list(state.memory.open_threads)
    if len(open_threads) >= 4 and not state.memory.events:
        issues.append(
            Diagnosis(
                issue="payoff stall",
                evidence=f"{len(open_threads)} open threads and zero paid events",
                edit_op="Close one thread on-mic this episode. Never 170 episodes of the same wound.",
                severity="high",
            )
        )
    if "werewolf" in text and "billionaire" in text:
        issues.append(
            Diagnosis(
                issue="saturated catalog trope",
                evidence="werewolf billionaire already saturates the market and clones exist",
                edit_op="Change the power structure. Do not ship a werewolf-CEO clone.",
                severity="medium",
            )
        )
    return issues


def structural_features(state: SeriesState) -> dict[str, Any]:
    ep = first_episode(state)
    text = script_blob(state)
    
    # Vernacular and dialect preservation score
    vernacular_markers = (
        "gujarati", "surat", "undhiyu", "nani", "maa", "bhai", "pune", "kodaikanal",
        "chai", "tiffin", "mohalla", "asafetida", "resin", "morse", "valve", "ghat"
    )
    has_vernacular = any(w in text for w in vernacular_markers)
    has_owned_fact = bool(state.owned_fact and any(w in text for w in state.owned_fact.lower().split() if len(w) > 4))
    
    dialect_val = 0.90 if (has_vernacular or has_owned_fact) else 0.55

    return {
        "exposition_minutes": ep.exposition_minutes if ep else 6.0,
        "first_turn_minute": ep.first_turn_minute if ep else 10.0,
        "minutes": ep.minutes if ep else 12.0,
        "has_cliff": bool(ep and ep.cliffhanger and len(ep.cliffhanger) > 12),
        "generated": any(m in text for m in GENERATED_MARKERS),
        "mystery_pile": any(m in text for m in MYSTERY_PILE_MARKERS),
        "agency_words": bool(re.search(r"\b(i will|i won't|i choose|i hide|i keep|i tell|i reveal)\b", text)),
        "private_monologue": "monologue" in text or "(" in (ep.script if ep else ""),
        "mother_tongue": has_vernacular,
        "dialect_score": dialect_val,
        "dark_pattern_risk": "High Risk" if any(m in text for m in AD_MID_SENTENCE) else "Low / Safe",
    }
