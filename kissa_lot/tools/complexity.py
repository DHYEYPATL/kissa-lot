from __future__ import annotations

from collections import defaultdict

from kissa_lot.models import ComplexityReport, ScriptBreakdown


def score_complexity(breakdown: ScriptBreakdown) -> ComplexityReport:
    """Score schedule risk the way indie producers actually bleed money.

    Grounded in 2025–2026 practitioner research: most indie films die in
    pre-production from overscoped scripts, fragile locations, and night work.
    """
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
        drivers.append(f"{location_count} distinct locations — each company move burns coverage.")
        cuts.append("Collapse satellite locations into two hero interiors + one exterior block.")
    elif location_count >= 4:
        score += 16
        drivers.append(f"{location_count} locations. Fine if they cluster; fatal if they scatter.")
        cuts.append("Shoot same-block locations as one company day.")
    else:
        score += 4
        drivers.append(f"{location_count} location(s) — contained, which audiences of tactile cinema reward.")

    if night >= 5:
        score += 22
        drivers.append(f"{night} night scenes. Night is a budget multiplier, not a mood.")
        cuts.append("Convert exposition nights to magic-hour or practical-interior night.")
    elif night >= 2:
        score += 10
        drivers.append(f"{night} night scenes. Budget the generator and the wrap meal now.")

    if vfx:
        score += min(24, 6 * vfx)
        drivers.append(f"{vfx} VFX-leaning beats. Unplanned comps are the most expensive shots on low-budget sets.")
        cuts.append("Decide the VFX approach in prep: locked plate vs. in-camera gag vs. cutaway.")

    if cast >= 10:
        score += 14
        drivers.append(f"{cast} speaking characters. Availability, not talent, will slip the schedule.")
        cuts.append("Merge one-scene characters into existing roles.")
    elif cast >= 6:
        score += 6

    if ext >= 6:
        score += 8
        drivers.append("Exterior-heavy. Weather is an uncredited producer.")
        cuts.append("Build a cover-set interior for every exterior day.")

    if pages > 30 and location_count + night > 8:
        score += 10
        drivers.append("Page count plus logistics look like a feature schedule on a short-film budget.")

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
