# Kissa Lot

**Hackathon:** Agentic Cinema: The Blockbuster Hackathon  
**Track:** Parallel  
**Deadline:** 9 September 2026, 2:00 PM PT  
**Repo:** https://github.com/DHYEYPATL/kissa-lot  
**License:** MIT (see `LICENSE`)

A kissa is a story. Kissa Lot is the development desk that runs before a writer locks pages or a producer locks a schedule.

Paste a logline or a screenplay. The agent does five deterministic jobs:

1. Parse production format (INT/EXT, day/night, cast, locations, VFX flags).
2. Score whether the script is shootable on an indie calendar.
3. Call **Parallel Search API four times** for audience desire, market comps, cultural facts, and location/production reality.
4. Ask **Gemini** (`google-genai`) to write a greenlight packet that may only cite URLs Parallel actually returned.
5. Return shooting groups and a cut list.

This is not a chatbot that "talks about film." It is a multi-step media workflow: research → risk → package.

## Why this exists

Last-six-month audience and practitioner research (see `docs/RESEARCH.md`):

- People still leave the house for story, not franchise habit.
- Younger crowds want original, culturally specific work they can talk about — and clip.
- Horror is up. Mid-budget "pretty but unmemetic" drama is invisible.
- Regional-language and tactile films are taking share from polished generic IP.
- Indie films die in prep: unlocked scripts, verbal locations, night work treated as mood.

Kissa Lot is built for that desk, not for a two-hundred-person studio lot. It also works for a development assistant drowning in spec piles.

## Track compliance

| Requirement | Where it lives |
|---|---|
| Gemini + Google Cloud AI packages | `kissa_lot/gemini_client.py` imports `google.genai`; `adk_agent/agent.py` builds an ADK `Agent` |
| Accepted packages | `google-genai`, `google-adk`, `google-cloud-aiplatform` in `requirements.txt` |
| Partner runtime use | `kissa_lot/tools/parallel_search.py` does `from parallel import Parallel` and `client.search(...)` |
| Functional media workflow | Development / pre-production packaging |
| Public repo + OSI license | This repository, MIT |
| Hosted project | FastAPI app in `web/app.py` (Cloud Run / any container) |
| No third-party AI models | Only Gemini + Parallel's own retrieval |

IBM Bob, Grafana MCP, ClickHouse MCP, and Replit Agent are **not** used. Submit under the **Parallel** track only.

## Architecture

```
filmmaker pages
    → parse_screenplay          (deterministic)
    → score_complexity          (deterministic)
    → Parallel Search × 4       (live web, cited)
    → Gemini generate_content   (packet JSON)
    → greenlight packet + UI
```

ADK entrypoint: `adk_agent/agent.py` exposes `root_agent` with tools
`develop_kissa`, `breakdown_pages`, and `search_production_web`.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# GEMINI_API_KEY from https://aistudio.google.com/app/apikey
# PARALLEL_API_KEY from https://platform.parallel.ai  (hackathon signup grants credits)

python -m kissa_lot examples/night_kitchen.fountain --json
python -m unittest discover -s tests
uvicorn web.app:app --reload --port 8080
```

Open `http://127.0.0.1:8080`.

### ADK

```bash
adk web
# or
adk run adk_agent
```

### Cloud Run

```bash
gcloud run deploy kissa-lot \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=...,PARALLEL_API_KEY=...
```

Prefer Secret Manager in a real submission rather than raw flags.

## Demo without keys

The parser and complexity engine always run. If a key is missing, the orchestrator records the exception, fills a research fixture taken from the design brief, and still returns a packet so you can walk the UI. Judges should see live Parallel + Gemini in the demo video — set the keys first.

## What to submit on Devpost

Copy `docs/SUBMISSION.md`. Record the trailer with `docs/DEMO_SCRIPT.md` (under three minutes, English, project running — not a cinematic teaser).

## Credits

Built by Dhyey Patel for Agentic Cinema. Research notes in `docs/RESEARCH.md`. Sample pages in `examples/night_kitchen.fountain` are original.
