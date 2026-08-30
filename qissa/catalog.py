"""Tiny synthetic catalog. Honest: not Pocket FM's warehouse."""

from __future__ import annotations

CATALOG = [
    {"id": "undhiyu-letters", "title": "The Undhiyu Letters", "genre": "regional family drama", "minutes": 12, "completion": 0.61, "next_start": 0.48, "note": "Payoff arrives episode 2.", "trope": "mother's secret recipe", "good": True},
    {"id": "night-shift-surat", "title": "Night Shift Surat", "genre": "regional family drama", "minutes": 13, "completion": 0.44, "next_start": 0.29, "note": "Six minutes of kitchen listing.", "trope": "kitchen monologue", "good": False},
    {"id": "cabin-knows", "title": "The Cabin Knows", "genre": "mythic thriller", "minutes": 11, "completion": 0.58, "next_start": 0.51, "note": "Letter at minute 9.", "trope": "I know what you did", "good": True},
    {"id": "mystery-pile", "title": "Files Without Faces", "genre": "mythic thriller", "minutes": 14, "completion": 0.31, "next_start": 0.18, "note": "Adds mysteries, never pays one.", "trope": "mystery pile-on", "good": False},
    {"id": "werewolf-boss", "title": "My CEO Is A Wolf", "genre": "campus dark romance", "minutes": 10, "completion": 0.67, "next_start": 0.62, "note": "Saturated trope.", "trope": "werewolf billionaire", "good": True},
    {"id": "werewolf-clone", "title": "His Secret Howl", "genre": "campus dark romance", "minutes": 10, "completion": 0.22, "next_start": 0.11, "note": "Planted clone.", "trope": "werewolf billionaire", "good": False, "clone_of": "werewolf-boss"},
]


def bucket_bar(genre: str, minutes: float = 12) -> dict:
    rows = [r for r in CATALOG if r["genre"] == genre] or CATALOG
    completion = sum(r["completion"] for r in rows) / len(rows)
    next_start = sum(r["next_start"] for r in rows) / len(rows)
    return {"genre": genre, "n": len(rows), "completion_bar": round(completion, 3), "next_start_bar": round(next_start, 3), "minutes": minutes}


def titles() -> list[str]:
    return [r["title"] for r in CATALOG]
