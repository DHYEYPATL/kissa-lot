"""Tiny eval so judges see the system catch a bad story, not only generate one."""

from __future__ import annotations

from qissa.agents import criticize, originality_scan
from qissa.catalog import CATALOG
from qissa.state import Episode, SeriesState


GOOD = """MEENA: Not for camera.
ARJUN: Then what is it.
MEENA: Heat as a feeling.
SFX: tape.
ANJALI (memory): They will forget the smell.
"""

BAD = """NARRATOR: Welcome to our kitchen where we shall now describe the coffee at length.
CHEF: Would you like some coffee?
FRIEND: Yes please let us talk while I make the coffee for us.
CHEF: Wow this coffee took forever. Here is your mug. It smells delicious.
FRIEND: I agree this coffee is so good.
NARRATOR: Meanwhile a new mystery appears, and another, and another, never paid.
"""


def run_eval() -> dict:
    good = SeriesState(title="Night Kitchen", genre="regional family drama", episodes=[
        Episode(number=1, title="Pour", script=GOOD, cliffhanger="forget the smell", first_turn_minute=5, exposition_minutes=1.5)
    ])
    bad = SeriesState(title="His Secret Howl", genre="campus dark romance", logline="werewolf billionaire CEO", bible="werewolf billionaire", episodes=[
        Episode(number=1, title="Coffee", script=BAD, cliffhanger="", first_turn_minute=11, exposition_minutes=8)
    ])
    good_issues = {d.issue for d in criticize(good)}
    bad_issues = {d.issue for d in criticize(bad)}
    flags = originality_scan(bad)
    clone_caught = any(f.severity in {"block", "warn"} for f in flags)
    result = {
        "good_not_flagged_soft_cliff": "soft cliff" not in good_issues,
        "bad_flagged_exposition": any(
            "exposition" in i or "late" in i or "soft" in i or "generated" in i for i in bad_issues
        ),
        "clone_caught": clone_caught,
        "catalog_size": len(CATALOG),
    }
    result["pass"] = bool(result["bad_flagged_exposition"] and result["clone_caught"])
    return result
