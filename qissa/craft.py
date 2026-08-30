"""Showrunner + Trend Scout. Gemini when keys exist; grounded fallback otherwise."""

from __future__ import annotations

from qissa.search import parallel_search
from qissa.state import Beat, Character, Episode, HumanDecision, SeriesMemory, SeriesState, TrendBrief

_FALLBACK = TrendBrief(
    tropes_rising=[
        "regional kitchen as crime scene / inheritance",
        "psychological tension over polished prose",
        "pay-one-leave-one secret structure",
        "interactive keep-or-tell beats",
    ],
    tropes_saturated=[
        "werewolf billionaire CEO",
        "mystery pile with no payoff",
        "werewolf campus dark romance clones",
    ],
    archetypes=["night-shift cook who will not perform grief", "producer who wants the pour as a clip"],
    regional_moments=["Surat night kitchens", "Gujarati undhiyu season as family ledger"],
    listener_pains=[
        "coin walls after the hook",
        "mid-sentence ads",
        "174 episodes of the same unresolved wound",
        "AI narration that flattens mother tongue",
        "5 minutes of bumper on an 11 minute show",
    ],
    tone="Contained. Clip-able. Mother tongue stays in the kitchen.",
    citations=[],
    engine="offline-research-2026",
)


def _fallback_trend() -> TrendBrief:
    return _FALLBACK.model_copy(deep=True)


def scout_trends(seed: str, genre: str) -> TrendBrief:
    objective = (
        "Find what serialized audio drama and Pocket-FM-class listeners "
        "wanted or complained about in the last six months: retention, "
        "cliffhangers, coin walls, ads, regional-language series, and "
        f"tropes in {genre}."
    )
    queries = [
        f"{genre} audio drama retention 2026",
        "Pocket FM listener complaints coin episodes Reddit",
        "r/audiodrama drop off ads short episodes cliffhanger",
        f"{seed[:80]} similar audio series existing",
        "serialized fiction payoff stall mystery pile",
    ]
    hits = parallel_search(objective, queries)
    rising, saturated, pains, cites = [], [], [], []
    blob = ""
    for hit in hits:
        title = hit.get("title") or ""
        excerpts = " ".join(hit.get("excerpts") or [])
        blob += f" {title} {excerpts}".lower()
        if hit.get("url"):
            cites.append({"title": title or hit["url"], "url": hit["url"]})
    if any(w in blob for w in ("coin", "paywall", "expensive")):
        pains.append("coin walls after the hook")
    if any(w in blob for w in ("ad", "mid-roll", "midroll")):
        pains.append("ads eating short episodes")
    if "werewolf" in blob or "billionaire" in blob:
        saturated.append("werewolf billionaire")
    if any(w in blob for w in ("retention", "cliff", "hook")):
        rising.append("structure-first serialized episodes")
    if any(w in blob for w in ("regional", "hindi", "gujarati", "bharat")):
        rising.append("regional-language kitchen and family series")
    return TrendBrief(
        tropes_rising=rising or list(_FALLBACK.tropes_rising),
        tropes_saturated=saturated or list(_FALLBACK.tropes_saturated),
        archetypes=list(_FALLBACK.archetypes),
        regional_moments=list(_FALLBACK.regional_moments),
        listener_pains=pains or list(_FALLBACK.listener_pains),
        tone=_FALLBACK.tone,
        citations=cites[:8],
        engine="parallel-web.search",
    )


def _kitchen_packet(state: SeriesState) -> SeriesState:
    state.title = state.title if state.title and state.title != "Untitled Qissa" else "Night Kitchen, Surat"
    state.logline = (
        "A night-shift cook in Surat keeps her late mother's recipe book taped "
        "under a prep table. A food-show producer wants the pour as a clip."
    )
    state.bible = (
        "World: one kitchen, one night shift, one city that still cooks for the living. "
        "Tone: dry heat, no sentimentality performed for a camera. "
        "Rule: Gujarati stays in the kitchen; English is for the producer. "
        "Season spine: the book is not a recipe. It is a ledger of who was fed and who was owed."
    )
    state.characters = [
        Character(name="Meena", goal="Keep the book off camera", wound="She let her mother die without writing the last page", speech="Short. Cuts vegetables while talking. Never explains the steam.", voice="low dry", secrets=["The last page names the producer"]),
        Character(name="Arjun", goal="Get one clip that will travel", wound="He only knows how to make people visible", speech="Bright. Sells the room. Names the light.", voice="bright mid", secrets=["He already sold the pour to a brand"]),
    ]
    state.spine = ["Ep1: producer finds the tape mark under the table", "Ep2: Meena chooses keep or tell", "Ep3: the last page is not a recipe", "Ep4: who gets fed on camera, who gets erased"]
    state.memory = SeriesMemory(
        events=["Mother dies off-mic before episode 1"],
        secrets_unrevealed=["Last page names the producer", "Brand already bought the pour"],
        growth=["Meena learns visibility is a kind of theft"],
        relationships=["Meena vs Arjun: heat without romance"],
        tone_rules=["Mother tongue in the kitchen", "No yelling mix", "No mid-sentence ads"],
        open_threads=["What is written on the last page"],
    )
    state.episodes = [
        Episode(
            number=1, title="The tape", minutes=12.0,
            logline="He sees the rectangle of cleaner metal under the table.",
            first_turn_minute=5.0, exposition_minutes=1.5,
            cliffhanger="The last page is not a recipe.",
            beats=[
                Beat(minute=0.5, label="hook", text="Tape peel. Not for camera.", emotion="refusal", ad_safe=False),
                Beat(minute=5.0, label="turn", text="Meena hides the book in her shirt.", emotion="choice", ad_safe=True),
                Beat(minute=11.2, label="cliff", text="The last page is not a recipe.", emotion="dread", ad_safe=True),
            ],
            script=(
                "SFX: tape peel under steel.\n"
                "MEENA: Not for camera.\n"
                "ARJUN: Then what is it.\n"
                "MEENA: Heat as a feeling.\n"
                "SFX: a page that does not sound like paper.\n"
                "ANJALI (memory): They will forget the smell.\n"
                "MEENA (private): I will keep the book. I will not perform the pour.\n"
                "ARJUN: One clip. That is all the brand bought.\n"
                "MEENA: The last page is not a recipe.\n"
            ),
        )
    ]
    state.branches = {
        "keep": Episode(number=2, title="Keep the page", minutes=12.0, branch_id="keep", first_turn_minute=3.0, exposition_minutes=1.0, cliffhanger="The brand already has a midnight slot.", logline="She tapes the book back. He films the empty hook.", script="MEENA: I keep it.\nARJUN: Then I film the absence.\n"),
        "tell": Episode(number=2, title="Tell the page", minutes=12.0, branch_id="tell", first_turn_minute=3.5, exposition_minutes=1.2, cliffhanger="The last name on the page is his.", logline="She reads one line. It is his name.", script="MEENA: I tell it.\nSFX: paper that is not paper.\nMEENA: Your name is already here.\n"),
    }
    return state


def _genre_packet(state: SeriesState) -> SeriesState:
    if "romance" in state.genre:
        state.title = state.title if state.title != "Untitled Qissa" else "Do Not Howl This"
        state.logline = state.seed or "A campus rumor that the dean is a wolf. The rumor is the product."
        state.bible = "Do not write a werewolf billionaire. Write the market that wants one."
        state.episodes = [Episode(number=1, title="The rumor sells", minutes=11.0, first_turn_minute=4.0, exposition_minutes=2.0, cliffhanger="The dean is not the wolf. The app is.", script="RHEA: I will not pay a coin for another howl.\nDEV: Then why are you still here.\n")]
        return state
    if "thriller" in state.genre:
        state.title = state.title if state.title != "Untitled Qissa" else "One File, One Face"
        state.logline = state.seed or "A clerk is told to open a file with no face on it."
        state.bible = "Pay one mystery. Leave one. Never pile."
        state.episodes = [Episode(number=1, title="The unlabeled folder", minutes=12.0, first_turn_minute=4.5, exposition_minutes=1.8, cliffhanger="The face in the file is last week's intern.", script="CLERK: I open one file.\nSFX: empty tab.\nCLERK: I will not open a second until this one pays.\n")]
        return state
    return _kitchen_packet(state)


def showrun(state: SeriesState) -> SeriesState:
    try:
        from qissa.llm import generate_json
        data = generate_json(
            "Return JSON for a serialized audio bible. Keys: title, logline, bible, "
            "characters (name,goal,wound,speech,voice,secrets), spine (list of 4), "
            "episode1_script, cliffhanger, first_turn_minute, exposition_minutes. Genre: "
            + state.genre + " Seed: " + state.seed
            + " Constraint: mother tongue if regional. Costly choice before minute 8. Pay one secret. Leave one question."
        )
        if data.get("title"):
            state.title = str(data["title"])[:80]
        if data.get("logline"):
            state.logline = str(data["logline"])
        if data.get("bible"):
            state.bible = str(data["bible"])
        if data.get("episode1_script"):
            state.episodes = [Episode(number=1, title="Episode 1", minutes=12.0, script=str(data["episode1_script"]), cliffhanger=str(data.get("cliffhanger") or ""), first_turn_minute=float(data.get("first_turn_minute") or 6), exposition_minutes=float(data.get("exposition_minutes") or 2))]
        state.engines["gemini"] = "google-genai"
        if not state.episodes:
            state = _genre_packet(state)
    except Exception as exc:
        state.engines["gemini"] = f"fallback:{exc}"
        state = _genre_packet(state)
    if not state.episodes:
        state = _genre_packet(state)
    if not state.branches:
        state = _kitchen_packet(state) if "family" in state.genre else state
        if not state.branches:
            state.branches = {
                "keep": Episode(number=2, title="Hold", minutes=12, branch_id="keep", cliffhanger="The other door opens.", first_turn_minute=3, exposition_minutes=1, script="THEY hold."),
                "tell": Episode(number=2, title="Speak", minutes=12, branch_id="tell", cliffhanger="The name is already written.", first_turn_minute=3, exposition_minutes=1, script="THEY speak."),
            }
    return state


def apply_direction(state: SeriesState, note: str) -> SeriesState:
    state.cycle += 1
    state.status = "iterate"
    before = state.episodes[0].script if state.episodes else ""
    state.human_decisions.append(HumanDecision(action="direct", note=note, cycle=state.cycle))
    state.revisions.append(note)
    patched = before
    if "agency" in note.lower() or "choice" in note.lower():
        patched = (before or "") + "\nMEENA (private): I choose the cost. I hide the page before minute six.\n"
        if state.episodes:
            state.episodes[0].first_turn_minute = min(state.episodes[0].first_turn_minute, 5.5)
            state.episodes[0].exposition_minutes = min(state.episodes[0].exposition_minutes, 1.5)
    elif "dark" in note.lower():
        patched = (before or "") + "\nSFX: the tape sounds like skin.\n"
    else:
        patched = (before or "") + f"\n[EDITOR NOTE APPLIED]: {note}\n"
    try:
        from qissa.llm import generate_text
        rewritten = generate_text("Rewrite this audio episode to obey the editor note. Keep character names. Keep mother tongue if present. Return only the script.\nNOTE: " + note + "\nSCRIPT:\n" + before)
        if rewritten and len(rewritten) > 40:
            patched = rewritten
            state.engines["gemini"] = "google-genai-rewrite"
    except Exception as exc:
        state.engines["gemini_rewrite"] = f"fallback:{exc}"
    if state.episodes:
        state.episodes[0].script = patched
    state.before_after.append({"before": before[:800], "after": patched[:800], "note": note})
    return state
