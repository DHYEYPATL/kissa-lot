"""Tiny synthetic catalog. Honest: not Pocket FM's warehouse.

Graduation uses the *hit* bar in the same genre + length bucket,
not the mean of flops. Averaging failures into the bar was a
logical fallacy in v1 — it made weak drafts look competitive.
"""

from __future__ import annotations

CATALOG = [
    {
        "id": "undhiyu-letters",
        "title": "The Undhiyu Letters",
        "genre": "regional family drama",
        "minutes": 12,
        "completion": 0.61,
        "next_start": 0.48,
        "coin": 0.41,
        "note": "Payoff of the recipe book arrives episode 2. High retention.",
        "trope": "mother's secret recipe",
        "good": True,
        "status": "hit",
    },
    {
        "id": "night-shift-surat",
        "title": "Night Shift Surat",
        "genre": "regional family drama",
        "minutes": 13,
        "completion": 0.44,
        "next_start": 0.29,
        "coin": 0.18,
        "note": "Six minutes of kitchen listing before a turn. Classic drop.",
        "trope": "kitchen monologue",
        "good": False,
        "status": "stalled",
    },
    {
        "id": "cabin-knows",
        "title": "The Cabin Knows",
        "genre": "mythic thriller",
        "minutes": 11,
        "completion": 0.58,
        "next_start": 0.51,
        "coin": 0.39,
        "note": "Anonymous letter at minute 9. Soft but early hook.",
        "trope": "I know what you did",
        "good": True,
        "status": "hit",
    },
    {
        "id": "mystery-pile",
        "title": "Files Without Faces",
        "genre": "mythic thriller",
        "minutes": 14,
        "completion": 0.31,
        "next_start": 0.18,
        "coin": 0.09,
        "note": "Adds mysteries, never pays one. r/audiodrama graveyard.",
        "trope": "mystery pile-on",
        "good": False,
        "status": "stalled",
    },
    {
        "id": "werewolf-boss",
        "title": "My CEO Is A Wolf",
        "genre": "campus dark romance",
        "minutes": 10,
        "completion": 0.67,
        "next_start": 0.62,
        "coin": 0.55,
        "note": "Saturated trope, high completion, originality risk.",
        "trope": "werewolf billionaire",
        "good": True,
        "status": "hit",
    },
    {
        "id": "werewolf-clone",
        "title": "His Secret Howl",
        "genre": "campus dark romance",
        "minutes": 10,
        "completion": 0.22,
        "next_start": 0.11,
        "coin": 0.07,
        "note": "Planted clone of My CEO Is A Wolf. Originality Guard must flag.",
        "trope": "werewolf billionaire",
        "good": False,
        "clone_of": "werewolf-boss",
        "status": "killed",
    },
    {
        "id": "amelia-stall",
        "title": "The Long Recital",
        "genre": "mythic thriller",
        "minutes": 38,
        "completion": 0.36,
        "next_start": 0.21,
        "coin": 0.12,
        "note": "Loved early. Then monthly releases with no story motion.",
        "trope": "reverse-history stall",
        "good": False,
        "status": "stalled",
    },
    {
        "id": "clip-kitchen",
        "title": "Pour on Camera",
        "genre": "regional family drama",
        "minutes": 12,
        "completion": 0.57,
        "next_start": 0.46,
        "coin": 0.33,
        "note": "One clip-able pour. Mother tongue stays in the kitchen.",
        "trope": "food-show extract",
        "good": True,
        "status": "hit",
    },
]


def bucket_bar(genre: str, minutes: float = 12) -> dict:
    """Hit bar only. Flops inform diagnosis, they do not lower the hurdle."""
    same = [r for r in CATALOG if r["genre"] == genre]
    hits = [r for r in same if r.get("good")] or [r for r in CATALOG if r.get("good")]
    stalled = [r for r in same if not r.get("good")]
    completion = sum(r["completion"] for r in hits) / len(hits)
    next_start = sum(r["next_start"] for r in hits) / len(hits)
    coin = sum(r.get("coin", 0.3) for r in hits) / len(hits)
    return {
        "genre": genre,
        "n_hits": len(hits),
        "n_stalled": len(stalled),
        "completion_bar": round(completion, 3),
        "next_start_bar": round(next_start, 3),
        "coin_bar": round(coin, 3),
        "minutes": minutes,
        "hit_titles": [r["title"] for r in hits],
        "stalled_titles": [r["title"] for r in stalled],
    }


def titles() -> list[str]:
    return [r["title"] for r in CATALOG]


def find_title(name: str) -> dict | None:
    key = name.lower().strip()
    for row in CATALOG:
        if row["title"].lower() == key or row["id"] == key:
            return row
    return None


def stalled_shows(genre: str | None = None) -> list[dict]:
    rows = [r for r in CATALOG if not r.get("good")]
    if genre:
        rows = [r for r in rows if r["genre"] == genre]
    return rows
