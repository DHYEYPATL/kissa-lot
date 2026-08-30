from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from qissa.catalog import CATALOG, bucket_bar, stalled_shows
from qissa.eval_harness import run_eval
from qissa.pipeline import human_gate, run_desk
from qissa.state import SeriesState

load_dotenv()

ROOT = Path(__file__).resolve().parent
SESSIONS: dict[str, SeriesState] = {}

app = FastAPI(title="Qissa Studio", version="2.1.0")
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")


@app.get("/health")
def health() -> dict:
    return {
        "ok": True,
        "product": "Qissa Studio",
        "track": "Parallel",
        "gemini": bool(
            os.environ.get("GEMINI_API_KEY")
            or os.environ.get("GOOGLE_GENAI_USE_VERTEXAI") == "true"
        ),
        "parallel": bool(os.environ.get("PARALLEL_API_KEY")),
        "eval": run_eval(),
        "runtime": {
            "google_genai": "qissa/llm.py",
            "google_adk": "adk_agent/agent.py",
            "parallel_web": "qissa/search.py",
        },
    }


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return (ROOT / "static" / "index.html").read_text(encoding="utf-8")


@app.get("/api/catalog")
def catalog() -> dict:
    return {"catalog": CATALOG, "bars": {
        g: bucket_bar(g) for g in sorted({r["genre"] for r in CATALOG})
    }, "stalled": stalled_shows()}


@app.post("/api/open")
def open_lot(
    seed: str = Form(...),
    genre: str = Form("regional family drama"),
    title: str = Form(""),
    owned_fact: str = Form(""),
) -> JSONResponse:
    state = run_desk(seed, genre=genre, title=title, owned_fact=owned_fact)
    SESSIONS["current"] = state
    return JSONResponse(state.model_dump())


@app.post("/api/gate")
def gate(action: str = Form(...), note: str = Form("")) -> JSONResponse:
    state = SESSIONS.get("current")
    if state is None:
        return JSONResponse({"error": "no series on the lot"}, status_code=400)
    state = human_gate(state, action, note)
    SESSIONS["current"] = state
    return JSONResponse(state.model_dump())


@app.get("/api/packet")
def packet() -> PlainTextResponse:
    """One-page GO / NO-GO a producer can paste into Slack."""
    state = SESSIONS.get("current")
    if state is None:
        return PlainTextResponse("No series on the lot.", status_code=400)
    lines = [
        f"QISSA STUDIO — {state.title}",
        f"STATUS: {state.status}",
        f"VERDICT: {state.verdict or 'HOLD FOR HUMAN'}",
        f"OWNED FACT: {state.owned_fact or '(none)'}",
        f"REFUSED: {state.refused_instinct}",
        "",
        "WHY PEOPLE MIGHT DROP",
    ]
    for d in state.diagnoses[:5]:
        lines.append(f"- {d.issue}: {d.edit_op}")
    lines += ["", "CAST (voices must differ)"]
    for v in (state.booth or {}).get("voices") or []:
        lines.append(f"- {v.get('name')}: {v.get('tag')}")
    lines += ["", "WEB SOURCES (Parallel — do not invent)"]
    for c in (state.trend.citations or [])[:6]:
        lines.append(f"- {c.get('title')} {c.get('url')}")
    if not state.trend.citations:
        lines.append("- none this run (offline fallback)")
    lines += ["", "AUDIO ONLY. No picture track."]
    return PlainTextResponse("\n".join(lines))
