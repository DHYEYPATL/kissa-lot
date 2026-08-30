from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from kissa_lot.orchestrator import run_development

load_dotenv()

ROOT = Path(__file__).resolve().parent
SAMPLE = (ROOT.parent / "examples" / "night_kitchen.fountain").read_text(encoding="utf-8")

app = FastAPI(title="Kissa Lot", version="1.0.0")
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")


@app.get("/health")
def health() -> dict:
    return {
        "ok": True,
        "gemini": bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_GENAI_USE_VERTEXAI") == "true"),
        "parallel": bool(os.environ.get("PARALLEL_API_KEY")),
        "track": "Parallel",
    }


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    page = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
    return page.replace("%%SAMPLE%%", SAMPLE.replace("</", "<\\/"))


@app.post("/api/develop")
def develop(
    pages: str = Form(...),
    title: str = Form(""),
) -> JSONResponse:
    result = run_development(pages, title_hint=title)
    return JSONResponse(result.model_dump())
