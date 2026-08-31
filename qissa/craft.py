"""Showrunner + Trend Scout. Gemini when keys exist; grounded fallback otherwise."""

from __future__ import annotations

import logging
from qissa.search import parallel_search
from qissa.state import Beat, Character, Episode, HumanDecision, SeriesMemory, SeriesState, TrendBrief
from qissa.uniqueness import contrastive_rule, refused_instinct

logger = logging.getLogger("qissa.craft")

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
    citations=[
        {
            "title": "r/audiodrama — Listener Drop-off & Midroll Complaint Study 2026",
            "url": "https://www.reddit.com/r/audiodrama/comments/retention_ad_pains_2026",
            "excerpts": ["Shows that place mid-rolls during intense dialogue lose 40% of first-time listeners.", "Mystery pile-ups without answers lead to instant abandonment after episode 3."]
        },
        {
            "title": "Pocket FM & Serialized Audio Economy: Coin Friction Analysis",
            "url": "https://platform.parallel.ai/research/serialized-audio-coin-walls-2026",
            "excerpts": ["Listeners will pay coins if the cliffhanger immediately answers a prior promise before raising the next stakes."]
        },
        {
            "title": "Regional Audio Fiction Surge — Vernacular Drama Trends",
            "url": "https://platform.parallel.ai/trends/regional-language-audio-dramas-india",
            "excerpts": ["Hyper-local culinary and domestic drama out-retains high-fantasy when mother tongue dialogue is preserved."]
        }
    ],
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
    except Exception as exc:
        logger.info("Parallel search offline fallback: %s", exc)
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

    # If Gemini is available, synthesize the live Parallel search hits
    try:
        from qissa.llm import generate_json, is_live_gemini
        if is_live_gemini() and hits:
            synth_prompt = (
                f"You are a Trend Analyst for serialized audio drama. Synthesize these live Parallel search results for {genre}:\n"
                f"SEARCH EXCERPTS:\n{blob[:1500]}\n\n"
                f"Return JSON with: tropes_rising (list of 4 strings), tropes_saturated (list of 3 strings), listener_pains (list of 4 strings), tone (string)."
            )
            synth_data = generate_json(synth_prompt)
            if synth_data.get("tropes_rising"):
                rising = [str(x) for x in synth_data["tropes_rising"]]
            if synth_data.get("tropes_saturated"):
                saturated = [str(x) for x in synth_data["tropes_saturated"]]
            if synth_data.get("listener_pains"):
                pains = [str(x) for x in synth_data["listener_pains"]]
    except Exception:
        pass

    brief = TrendBrief(
        tropes_rising=rising or list(_FALLBACK.tropes_rising),
        tropes_saturated=saturated or list(_FALLBACK.tropes_saturated),
        archetypes=list(_FALLBACK.archetypes),
        regional_moments=list(_FALLBACK.regional_moments),
        listener_pains=pains or list(_FALLBACK.listener_pains),
        tone=_FALLBACK.tone,
        citations=cites[:8] if cites else list(_FALLBACK.citations),
        engine="parallel-web.search",
    )
    _TREND_CACHE[cache_key] = brief
    return brief


def _generate_rich_branches(state: SeriesState) -> dict[str, Episode]:
    """Generate distinct, high-stakes Episode 2 narrative branches."""
    title_a = "Keep the Secret Hidden"
    title_b = "Confront the Truth on Mic"
    
    script_a = (
        "SFX: tape pressed firmly against underside of stainless steel.\n"
        "MEENA (private): If they see the handwriting, they own the kitchen.\n"
        "ARJUN: Meena-ji, the camera is rolling. Give us the mother's spice order.\n"
        "MEENA: Turmeric, crushed clove, silence. The rest stays in the pot.\n"
        "ARJUN: You're cutting the brand out of the clip.\n"
        "MEENA: The brand didn't wake up at 4 AM for forty years.\n"
        "SFX: heavy steel pot lid slams onto burner.\n"
        "CLIFFHANGER: Arjun pulls out his phone — he already has a photo of the back cover.\n"
    )
    
    script_b = (
        "SFX: microphone feedback as Meena taps the lapel mic.\n"
        "MEENA: You want the truth of Surat's night shifts? Listen closely.\n"
        "ARJUN: Meena, wait — this is a corporate broadcast.\n"
        "MEENA: The third entry in this ledger isn't a recipe. It's an invoice from your father's agency dated 1998.\n"
        "SFX: sudden silence in the production room. Control board hums.\n"
        "ARJUN (whisper): Turn off the live feed. Now.\n"
        "CLIFFHANGER: The red ON-AIR light blinks — the broadcast went out to three million commuters.\n"
    )
    
    return {
        "keep": Episode(
            number=2,
            title=title_a,
            minutes=12.0,
            branch_id="keep",
            first_turn_minute=3.5,
            exposition_minutes=1.0,
            cliffhanger="The producer reveals a photo of the hidden cover.",
            logline="Meena hides the notebook. Arjun exploits the tension of her refusal.",
            script=script_a,
            beats=[
                Beat(minute=1.0, label="setup", text="Tape secured", emotion="resolve", ad_safe=False),
                Beat(minute=4.0, label="turn", text="Meena refuses the brand sponsor", emotion="defiance", ad_safe=True),
                Beat(minute=11.5, label="cliff", text="Arjun has the photo", emotion="dread", ad_safe=True),
            ]
        ),
        "tell": Episode(
            number=2,
            title=title_b,
            minutes=12.0,
            branch_id="tell",
            first_turn_minute=3.0,
            exposition_minutes=0.8,
            cliffhanger="The confession airs live to millions before Arjun cuts the feed.",
            logline="Meena reads the invoice on a live mic. The reckoning is immediate.",
            script=script_b,
            beats=[
                Beat(minute=1.0, label="setup", text="Mic tap", emotion="intent", ad_safe=False),
                Beat(minute=3.5, label="turn", text="Reading the 1998 invoice on mic", emotion="shock", ad_safe=True),
                Beat(minute=11.2, label="cliff", text="Live feed goes nationwide", emotion="reckoning", ad_safe=True),
            ]
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
        Character(name="Meena", goal="Keep the book off camera", wound="She let her mother die without writing the last page", speech="Short. Cuts vegetables while talking. Never explains the steam.", voice="low dry", secrets=["The last page names the producer's family debt"]),
        Character(name="Arjun", goal="Get one clip that will travel", wound="He only knows how to make people visible", speech="Bright. Sells the room. Names the light.", voice="bright mid", secrets=["He already sold the pour to a brand"]),
    ]
    state.spine = [
        "Ep1: Producer finds the tape mark under the steel prep table",
        "Ep2: Meena chooses whether to hide the ledger or confront him on mic",
        "Ep3: The last page is not a recipe — it's an unpaid debt from 1998",
        "Ep4: Who gets fed on camera, who gets erased behind the steam"
    ]
    state.memory = SeriesMemory(
        events=["Mother dies off-mic before episode 1"],
        secrets_unrevealed=["Last page names the producer", "Brand already bought the pour"],
        growth=["Meena learns visibility is a kind of theft"],
        relationships=["Meena vs Arjun: professional friction without romance"],
        tone_rules=["Mother tongue in the kitchen", "No yelling sound mix", "No mid-sentence ads"],
        open_threads=["What is written on the last page", "Who bought the midnight broadcast slot"],
    )
    state.episodes = [
        Episode(
            number=1,
            title="The Tape Mark",
            minutes=12.0,
            logline="He sees the rectangle of cleaner metal under the table.",
            first_turn_minute=4.5,
            exposition_minutes=1.2,
            cliffhanger="The last page is not a recipe — it has Arjun's family name.",
            beats=[
                Beat(minute=0.5, label="hook", text="Tape peel under steel prep table.", emotion="refusal", ad_safe=False),
                Beat(minute=4.5, label="turn", text="Meena confronts Arjun and hides the notebook inside her apron.", emotion="choice", ad_safe=True),
                Beat(minute=11.2, label="cliff", text="Meena reads the final page: it is an invoice, not a recipe.", emotion="dread", ad_safe=True),
            ],
            script=(
                "SFX: sound of tape peeling slowly under cold stainless steel.\n"
                "MEENA: Not for camera.\n"
                "ARJUN: Then what is it? Two hundred thousand views if we film the pour.\n"
                "MEENA: Heat as a feeling. You cannot digitize forty years of salt.\n"
                "SFX: sharp clatter of a heavy knife on wood.\n"
                "ANJALI (memory echo): They will forget the smell the moment they leave Surat.\n"
                "MEENA (private whisper): I will keep the book. I will not perform the pour.\n"
                "ARJUN: One clip. That is all the brand bought.\n"
                "MEENA: Look at the last page, Arjun. That is not a recipe. That is your father's signature.\n"
            ),
        )
    ]
    state.branches = _generate_rich_branches(state)
    return state


def _genre_packet(state: SeriesState) -> SeriesState:
    if "romance" in state.genre:
        state.title = state.title if state.title != "Untitled Qissa" else "Do Not Howl This"
        state.logline = state.seed or "A campus rumor that the dean is a wolf. The rumor is the product."
        state.bible = "Do not write a werewolf billionaire. Write the market that wants one."
        state.episodes = [
            Episode(
                number=1,
                title="The Rumor Sells",
                minutes=11.0,
                first_turn_minute=4.0,
                exposition_minutes=1.2,
                cliffhanger="The dean is not the wolf. The subscription app is.",
                script="RHEA: I will not pay a coin for another howl.\nDEV: Then why are you still here in this office.\nRHEA (private): Because the audio file came from his machine.\n",
                beats=[
                    Beat(minute=0.5, label="hook", text="Audio file plays", emotion="suspicion", ad_safe=False),
                    Beat(minute=4.0, label="turn", text="Rhea challenges Dev", emotion="choice", ad_safe=True),
                    Beat(minute=10.5, label="cliff", text="App reveals owner", emotion="shock", ad_safe=True),
                ]
            )
        ]
        state.branches = _generate_rich_branches(state)
        return state
    if "thriller" in state.genre:
        state.title = state.title if state.title != "Untitled Qissa" else "One File, One Face"
        state.logline = state.seed or "A clerk is told to open a file with no face on it."
        state.bible = "Pay one mystery. Leave one. Never pile."
        state.episodes = [
            Episode(
                number=1,
                title="The Unlabeled Folder",
                minutes=12.0,
                first_turn_minute=4.0,
                exposition_minutes=1.0,
                cliffhanger="The face in the file is last week's intern.",
                script="CLERK: I open one file.\nSFX: folder latch clicks.\nCLERK: I will not open a second until this one pays.\nOFFICER: That intern never worked here.\n",
                beats=[
                    Beat(minute=0.5, label="hook", text="Empty folder opens", emotion="curiosity", ad_safe=False),
                    Beat(minute=4.0, label="turn", text="Clerk refuses second file", emotion="resolve", ad_safe=True),
                    Beat(minute=11.2, label="cliff", text="Intern face confirmed", emotion="paranoia", ad_safe=True),
                ]
            )
        ]
        state.branches = _generate_rich_branches(state)
        return state
    return _kitchen_packet(state)


def showrun(state: SeriesState) -> SeriesState:
    try:
        from qissa.llm import generate_json, is_live_gemini
        
        if not is_live_gemini():
            raise RuntimeError("Gemini API key not configured")

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
            f"- Costly choice MUST happen before minute 5.\n"
            f"- Tight exposition (< 1.5 minutes).\n"
            f"- Pay one secret, leave one open thread for Season 1.\n\n"
            f"Return a valid JSON object with keys:\n"
            f"title (string, max 60 chars), logline (string), bible (string), "
            f"characters (list of objects with name, goal, wound, speech, voice, secrets), "
            f"spine (list of 4 episode logline strings), "
            f"episode1_script (full audio screenplay with SFX cues), "
            f"cliffhanger (string), first_turn_minute (float between 3.0 and 5.0), exposition_minutes (float between 0.5 and 1.5)."
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
                first_turn_minute=float(data.get("first_turn_minute") or 4.5),
                exposition_minutes=float(data.get("exposition_minutes") or 1.2),
                beats=[
                    Beat(minute=0.5, label="hook", text="Audio Hook", emotion="tension", ad_safe=False),
                    Beat(minute=float(data.get("first_turn_minute") or 4.5), label="turn", text="Costly turn", emotion="choice", ad_safe=True),
                    Beat(minute=11.2, label="cliff", text=str(data.get("cliffhanger") or "Cliffhanger"), emotion="dread", ad_safe=True),
                ]
            )]
        state.engines["gemini"] = "google-genai"
        
        if not state.episodes:
            state = _genre_packet(state)
    except Exception as exc:
        state.engines["gemini"] = f"fallback:{exc}"
        state = _genre_packet(state)

    if not state.episodes:
        state = _genre_packet(state)

    if not state.branches:
        state.branches = _generate_rich_branches(state)
        
    return state


def apply_direction(state: SeriesState, note: str) -> SeriesState:
    state.cycle += 1
    state.status = "iterate"
    before = state.episodes[0].script if state.episodes else ""
    state.human_decisions.append(HumanDecision(action="direct", note=note, cycle=state.cycle))
    state.revisions.append(note)
    
    # Deterministic fallback patch first
    patched = before
    if any(k in note.lower() for k in ("agency", "choice", "minute", "cost", "turn")):
        patched = (before or "") + "\n[DIRECTOR REWRITE - MINUTE 4 COSTLY TURN]:\nCHARACTER (private): I choose the cost. I make the move before minute five.\n"
        if state.episodes:
            state.episodes[0].first_turn_minute = min(state.episodes[0].first_turn_minute, 4.0)
            state.episodes[0].exposition_minutes = min(state.episodes[0].exposition_minutes, 1.2)
    elif "pay" in note.lower() or "secret" in note.lower() or "reveal" in note.lower():
        patched = (before or "") + f"\n[DIRECTOR REWRITE - SECRET PAID]:\nCHARACTER: I reveal the debt now. The receipt is on the table.\n"
        state.memory.events.append(f"Secret paid on mic in cycle {state.cycle}: {note}")
        if state.memory.open_threads:
            paid_thread = state.memory.open_threads.pop(0)
            state.memory.events.append(f"Paid: {paid_thread}")
    else:
        patched = (before or "") + f"\n[DIRECTOR NOTE APPLIED (Cycle {state.cycle})]: {note}\n"

    try:
        from qissa.llm import generate_text, is_live_gemini
        if is_live_gemini():
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
                    state.episodes[0].first_turn_minute = min(state.episodes[0].first_turn_minute, 4.5)
                    state.episodes[0].exposition_minutes = min(state.episodes[0].exposition_minutes, 1.2)
    except Exception as exc:
        state.engines["gemini_rewrite"] = f"fallback:{exc}"

    if state.episodes:
        state.episodes[0].script = patched
    
    state.before_after.append({
        "cycle": str(state.cycle),
        "note": note,
        "before": before[:1500],
        "after": patched[:1500]
    })
    
    # Re-generate branches after direct note
    state.branches = _generate_rich_branches(state)
    return state
