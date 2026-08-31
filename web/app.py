from __future__ import annotations

import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Form, Query
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from qissa.catalog import CATALOG, bucket_bar, stalled_shows
from qissa.eval_harness import run_eval
from qissa.llm import is_live_gemini
from qissa.pipeline import human_gate, run_desk
from qissa.search import is_live_parallel
from qissa.sessions import get_session, list_sessions, save_session

load_dotenv()

ROOT = Path(__file__).resolve().parent

app = FastAPI(title="Qissa Studio", version="2.3.0")
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")


@app.get("/health")
def health() -> dict:
    eval_res = run_eval()
    return {
        "ok": True,
        "product": "Qissa Studio",
        "version": "2.3.0",
        "track": "Parallel",
        "gemini": is_live_gemini(),
        "parallel": is_live_parallel(),
        "session_store": "sqlite+memory",
        "eval": eval_res,
        "eval_pass": eval_res.get("pass", False),
        "runtime": {
            "google_genai": "qissa/llm.py",
            "google_adk": "adk_agent/agent.py",
            "parallel_web": "qissa/search.py",
            "sessions": "qissa/sessions.py",
        },
    }


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return (ROOT / "static" / "index.html").read_text(encoding="utf-8")


@app.get("/api/catalog")
def catalog() -> dict:
    return {
        "catalog": CATALOG,
        "bars": {g: bucket_bar(g) for g in sorted({r["genre"] for r in CATALOG})},
        "stalled": stalled_shows(),
    }


@app.get("/api/sessions")
def sessions() -> dict:
    return {"sessions": list_sessions(limit=15)}


@app.get("/api/session")
def get_single_session(session_id: str = Query(...)) -> JSONResponse:
    sid = session_id.strip()
    state = get_session(sid)
    if not state:
        return JSONResponse(
            {"error": "Session not found or expired. Please open a new story lot."},
            status_code=404,
        )
    data = state.model_dump()
    data["session_id"] = sid
    return JSONResponse(data)


@app.post("/api/open")
def open_lot(
    seed: str = Form(...),
    genre: str = Form("regional family drama"),
    title: str = Form(""),
    owned_fact: str = Form(""),
    session_id: str = Form(""),
) -> JSONResponse:
    sid = session_id.strip() or f"qissa-{uuid.uuid4().hex[:10]}"
    state = run_desk(seed, genre=genre, title=title, owned_fact=owned_fact)
    save_session(sid, state)
    
    data = state.model_dump()
    data["session_id"] = sid
    return JSONResponse(data)


@app.post("/api/gate")
def gate(
    action: str = Form(...),
    note: str = Form(""),
    session_id: str = Form(...),
) -> JSONResponse:
    sid = session_id.strip()
    if not sid:
        return JSONResponse({"error": "session_id is required."}, status_code=400)
    
    state = get_session(sid)
    if not state:
        return JSONResponse(
            {"error": "Session not found or expired. Please open a new story lot."},
            status_code=404,
        )
    
    state = human_gate(state, action, note)
    save_session(sid, state)
    
    data = state.model_dump()
    data["session_id"] = sid
    return JSONResponse(data)


@app.get("/api/packet")
def packet(session_id: str = Query("")) -> PlainTextResponse:
    """One-page GO / NO-GO executive summary for production greenlight."""
    sid = session_id.strip()
    if not sid:
        return PlainTextResponse("Error: session_id query parameter missing.", status_code=400)
    
    state = get_session(sid)
    if not state:
        return PlainTextResponse("Session not found or expired. Please open a story lot.", status_code=404)
    
    twin_mean = round(sum(t.score for t in state.twin_scores) / max(1, len(state.twin_scores)), 1)
    bar = bucket_bar(state.genre)
    
    lines = [
        "=======================================================================",
        f"QISSA STUDIO DECISION: {state.title.upper()} ({state.genre.upper()})",
        f"VERDICT:        {state.verdict or 'HOLD FOR HUMAN GATE'}",
        f"RETENTION:      Twin Mean {twin_mean}/100 | Hit Bar {bar['completion_bar']:.0%} | Canary: {'RAN (' + str(round(state.canary.completion * 100)) + '%)' if state.canary.ran else 'BLOCKED (Waits on Human Approve)'}",
        f"INTEGRITY:      Payoff Ledger {state.ledger.ratio:.0%} Paid | Dialect: {state.dialect_verdict} ({state.dialect_score:.0%}) | Dark Pattern Risk: {state.dark_pattern_risk}",
        f"FIRST TURN:     Minute {state.episodes[0].first_turn_minute if state.episodes else 5.0}m (Target: <5m) | Exposition: {state.episodes[0].exposition_minutes if state.episodes else 1.2}m",
        "=======================================================================",
        f"OWNED FACT:     {state.owned_fact or '(none locked)'}",
        f"REFUSED CLICHE: {state.refused_instinct}",
        f"CYCLE:          Cycle {state.cycle}/{state.max_cycles}",
        "",
        "-----------------------------------------------------------------------",
        "TOP STRUCTURAL DIAGNOSES & DIRECTED FIXES",
        "-----------------------------------------------------------------------",
    ]
    if state.diagnoses:
        for i, d in enumerate(state.diagnoses[:4], 1):
            lines.append(f"[{i}] {d.issue.upper()} ({d.severity})")
            lines.append(f"    Evidence: {d.evidence}")
            lines.append(f"    Fix:      {d.edit_op}")
    else:
        lines.append("- No critical structural pacing flaws detected.")

    lines += [
        "",
        "-----------------------------------------------------------------------",
        "CAST & VOICE BOOTH SPECIFICATION",
        "-----------------------------------------------------------------------",
    ]
    for v in (state.booth or {}).get("voices") or []:
        lines.append(f"• {v.get('name')}: Voice Texture [{v.get('tag')}] (Must differ)")

    lines += [
        "",
        "-----------------------------------------------------------------------",
        "AUDIENCE TREND GROUNDING & LISTENER PAIN SUMMARY",
        "-----------------------------------------------------------------------",
        f"• Rising Tropes:    {', '.join(state.trend.tropes_rising[:3]) if state.trend.tropes_rising else 'Local trade, contained suspense'}",
        f"• Listener Pains:   {', '.join(state.trend.listener_pains[:3]) if state.trend.listener_pains else 'Coin walls, mid-sentence ads, flat delivery'}",
        f"• Tone Grounding:   {state.trend.tone or 'Dialect stays in the room. Contained suspense.'}",
    ]

    if state.rework_brief:
        lines += [
            "",
            "-----------------------------------------------------------------------",
            "SALVAGEABLE ASSETS & REWORK BRIEF (IF ARCHIVED)",
            "-----------------------------------------------------------------------",
            state.rework_brief,
        ]

    lines += [
        "",
        "=======================================================================",
        "AUDIO ONLY SPECIFICATION. NO PICTURE TRACK.",
        "=======================================================================",
    ]
    return PlainTextResponse("\n".join(lines))
