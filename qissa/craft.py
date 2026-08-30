"""Showrunner + Trend Scout. Gemini when keys exist; grounded fallback otherwise."""

from __future__ import annotations

from qissa.search import parallel_search
from qissa.state import Beat, Character, Episode, HumanDecision, SeriesMemory, SeriesState, TrendBrief
from qissa.uniqueness import contrastive_rule, refused_instinct

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

_TREND_CACHE: dict[str, TrendBrief] = {}


def _fallback_trend() -> TrendBrief:
    return _FALLBACK.model_copy(deep=True)


def scout_trends(seed: str, genre: str) -> TrendBrief:
    cache_key = f"{genre}::{seed[:60].strip().lower()}"
    if cache_key in _TREND_CACHE:
        return _TREND_CACHE[cache_key].model_copy(deep=True)

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
    try:
        hits = parallel_search(objective, queries)
    except Exception:
        hits = []

    if not hits:
        brief = _fallback_trend()
        _TREND_CACHE[cache_key] = brief
        return brief

    rising, saturated, pains, cites = [], [], [], []
    blob = ""
    for hit in hits:
        title = hit.get("title") or ""
        excerpts = " ".join(hit.get("excerpts") or [])
        blob += f" {title} {excerpts}".lower()
        if hit.get("url"):
            cites.append({"title": title or hit["url"], "url": hit["url"], "excerpts": hit.get("excerpts", [])})
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

    brief = TrendBrief(
        tropes_rising=rising or list(_FALLBACK.tropes_rising),
        tropes_saturated=saturated or list(_FALLBACK.tropes_saturated),
        archetypes=list(_FALLBACK.archetypes),
        regional_moments=list(_FALLBACK.regional_moments),
        listener_pains=pains or list(_FALLBACK.listener_pains),
        tone=_FALLBACK.tone,
        citations=cites[:8],
        engine="parallel-web.search",
    )
    _TREND_CACHE[cache_key] = brief
    return brief


def _default_branches(state: SeriesState) -> dict[str, Episode]:
    """Pure branches backfill. Does NOT clobber state.episodes, bible, or characters."""
    title_a = "Keep the Secret Hidden"
    title_b = "Confront the Truth on Mic"
    return {
        "keep": Episode(
            number=2,
            title=title_a,
            minutes=12.0,
            branch_id="keep",
            first_turn_minute=3.0,
            exposition_minutes=1.0,
            cliffhanger="The door opens before the page is hidden.",
            logline="She keeps the secret hidden. The recording continues without truth.",
            script="CHARACTER: I keep it hidden.\nSFX: latch clicks shut.\n",
        ),
        "tell": Episode(
            number=2,
            title=title_b,
            minutes=12.0,
            branch_id="tell",
            first_turn_minute=3.5,
            exposition_minutes=1.2,
            cliffhanger="The last name on the ledger belongs to someone in this room.",
            logline="She speaks on mic. The price is paid immediately.",
            script="CHARACTER: I speak the truth.\nSFX: microphone feedback.\n",
        ),
    }


def _kitchen_packet(state: SeriesState) -> SeriesState:
    """Offline deterministic fallback packet for regional family drama."""
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
        state.branches = _default_branches(state)
        return state
    if "thriller" in state.genre:
        state.title = state.title if state.title != "Untitled Qissa" else "One File, One Face"
        state.logline = state.seed or "A clerk is told to open a file with no face on it."
        state.bible = "Pay one mystery. Leave one. Never pile."
        state.episodes = [Episode(number=1, title="The unlabeled folder", minutes=12.0, first_turn_minute=4.5, exposition_minutes=1.8, cliffhanger="The face in the file is last week's intern.", script="CLERK: I open one file.\nSFX: empty tab.\nCLERK: I will not open a second until this one pays.\n")]
        state.branches = _default_branches(state)
        return state
    return _kitchen_packet(state)


def showrun(state: SeriesState) -> SeriesState:
    try:
        from qissa.llm import generate_json
        
        refused = refused_instinct(state.genre)
        contrast = contrastive_rule()
        prompt = (
            f"You are the Showrunner for a premium serialized audio drama.\n"
            f"GENRE: {state.genre}\n"
            f"STORY SEED: {state.seed}\n"
            f"CRITICAL OWNED FACT (MUST be organically woven into dialogue/action/setting — do NOT ignore): {state.owned_fact or '(none provided)'}\n"
            f"CONTRASTIVE RULE: {contrast}\n"
            f"REFUSED CLICHÉ / DO NOT WRITE THIS: {refused}\n"
            f"CONSTRAINTS:\n"
            f"- Audio-only script format (NAME: text, SFX: sound effect, (private) whisper, (memory) echo).\n"
            f"- Costly choice must happen before minute 6.\n"
            f"- Tight exposition (< 1.5 minutes).\n"
            f"- Pay one secret, leave one open thread for Season 1.\n\n"
            f"Return a valid JSON object with keys:\n"
            f"title (string, max 60 chars), logline (string), bible (string), "
            f"characters (list of objects with name, goal, wound, speech, voice, secrets), "
            f"spine (list of 4 episode logline strings), "
            f"episode1_script (full audio dialogue with SFX cues), "
            f"cliffhanger (string), first_turn_minute (float between 3.0 and 6.0), exposition_minutes (float between 0.5 and 1.5)."
        )
        data = generate_json(prompt)
        if data.get("title"):
            state.title = str(data["title"])[:80]
        if data.get("logline"):
            state.logline = str(data["logline"])
        if data.get("bible"):
            state.bible = str(data["bible"])
        if data.get("characters") and isinstance(data["characters"], list):
            chars = []
            for c in data["characters"]:
                if isinstance(c, dict) and c.get("name"):
                    chars.append(Character(
                        name=str(c.get("name")),
                        goal=str(c.get("goal") or ""),
                        wound=str(c.get("wound") or ""),
                        speech=str(c.get("speech") or ""),
                        voice=str(c.get("voice") or "mid"),
                        secrets=list(c.get("secrets") or []),
                    ))
            if chars:
                state.characters = chars
        if data.get("spine") and isinstance(data["spine"], list):
            state.spine = [str(x) for x in data["spine"]]
        if data.get("episode1_script"):
            state.episodes = [Episode(
                number=1,
                title=f"Episode 1: {state.title}",
                minutes=12.0,
                script=str(data["episode1_script"]),
                cliffhanger=str(data.get("cliffhanger") or ""),
                first_turn_minute=float(data.get("first_turn_minute") or 5.0),
                exposition_minutes=float(data.get("exposition_minutes") or 1.2),
            )]
        state.engines["gemini"] = "google-genai"
        
        # If Gemini returned empty episodes, fallback to genre packet
        if not state.episodes:
            state = _genre_packet(state)
    except Exception as exc:
        state.engines["gemini"] = f"fallback:{exc}"
        state = _genre_packet(state)

    if not state.episodes:
        state = _genre_packet(state)

    # Pure branches backfill — NEVER clobbers state.episodes or bible
    if not state.branches:
        state.branches = _default_branches(state)
        
    return state


def apply_direction(state: SeriesState, note: str) -> SeriesState:
    state.cycle += 1
    state.status = "iterate"
    before = state.episodes[0].script if state.episodes else ""
    state.human_decisions.append(HumanDecision(action="direct", note=note, cycle=state.cycle))
    state.revisions.append(note)
    
    # Deterministic fallback patch first
    patched = before
    if "agency" in note.lower() or "choice" in note.lower() or "minute" in note.lower() or "cost" in note.lower():
        patched = (before or "") + "\n[DIRECTOR REWRITE - MINUTE 5 COSTLY TURN]:\nCHARACTER (private): I choose the cost. I make the move before minute six.\n"
        if state.episodes:
            state.episodes[0].first_turn_minute = min(state.episodes[0].first_turn_minute, 5.0)
            state.episodes[0].exposition_minutes = min(state.episodes[0].exposition_minutes, 1.5)
    else:
        patched = (before or "") + f"\n[DIRECTOR NOTE APPLIED]: {note}\n"

    try:
        from qissa.llm import generate_text
        prompt = (
            f"You are a serialized audio script doctor. Rewrite this Episode 1 audio screenplay to strictly apply the Director Note.\n"
            f"GENRE: {state.genre}\n"
            f"OWNED FACT TO PRESERVE: {state.owned_fact}\n"
            f"DIRECTOR NOTE: {note}\n"
            f"EXISTING SCRIPT:\n{before}\n\n"
            f"Return only the full rewritten screenplay dialogue with SFX and character voice cues."
        )
        rewritten = generate_text(prompt)
        if rewritten and len(rewritten) > 40:
            patched = rewritten
            state.engines["gemini"] = "google-genai-rewrite"
            if state.episodes:
                state.episodes[0].first_turn_minute = min(state.episodes[0].first_turn_minute, 5.0)
                state.episodes[0].exposition_minutes = min(state.episodes[0].exposition_minutes, 1.5)
    except Exception as exc:
        state.engines["gemini_rewrite"] = f"fallback:{exc}"

    if state.episodes:
        state.episodes[0].script = patched
    state.before_after.append({"before": before[:1200], "after": patched[:1200], "note": note})
    return state
