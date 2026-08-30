"""Tiny eval so judges see the system catch a bad story, not only generate one."""

from __future__ import annotations

from qissa.agents import criticize, originality_scan, score_twins
from qissa.catalog import CATALOG
from qissa.state import Episode, SeriesState


GOOD = """MEENA: Not for camera.
ARJUN: Then what is it.
MEENA: Heat as a feeling.
SFX: tape.
ANJALI (memory): They will forget the smell.
MEENA (private): I will keep the book.
"""

BAD = """NARRATOR: Welcome to our kitchen where we shall now describe the coffee at length.
CHEF: Would you like some coffee?
FRIEND: Yes please let us talk while I make the coffee for us.
CHEF: Wow this coffee took forever. Here is your mug. It smells delicious.
FRIEND: I agree this coffee is so good.
NARRATOR: Meanwhile a new mystery appears, and another, and another, never paid.
"""


def run_eval() -> dict:
    good = SeriesState(
        title="Night Kitchen",
        genre="regional family drama",
        episodes=[
            Episode(
                number=1,
                title="Pour",
                script=GOOD,
                cliffhanger="forget the smell — last page is not a recipe",
                first_turn_minute=5,
                exposition_minutes=1.5,
            )
        ],
    )
    bad = SeriesState(
        title="His Secret Howl",
        genre="campus dark romance",
        logline="werewolf billionaire CEO",
        bible="werewolf billionaire",
        episodes=[
            Episode(
                number=1,
                title="Coffee",
                script=BAD,
                cliffhanger="",
                first_turn_minute=11,
                exposition_minutes=8,
            )
        ],
    )
    good_issues = {d.issue for d in criticize(good)}
    bad_issues = {d.issue for d in criticize(bad)}
    flags = originality_scan(bad)
    clone_caught = any(f.severity in {"block", "warn"} for f in flags)
    good_twins = score_twins(good)
    bad_twins = score_twins(bad)
    good_mean = sum(t.score for t in good_twins) / len(good_twins)
    bad_mean = sum(t.score for t in bad_twins) / len(bad_twins)
    result = {
        "good_not_flagged_soft_cliff": "soft cliff" not in good_issues,
        "bad_flagged_exposition": any(
            "exposition" in i or "late" in i or "soft" in i or "generated" in i for i in bad_issues
        ),
        "clone_caught": clone_caught,
        "twins_rank_good_above_bad": good_mean > bad_mean,
        "good_mean": round(good_mean, 1),
        "bad_mean": round(bad_mean, 1),
        "catalog_size": len(CATALOG),
        "persona_count": len(good_twins),
    }
    result["pass"] = bool(
        result["bad_flagged_exposition"]
        and result["clone_caught"]
        and result["twins_rank_good_above_bad"]
    )
    return result
