# Qissa Studio

**Submission product for Agentic Cinema (Parallel track).**  
`qissa/` + `web/` + `adk_agent/` is the full production greenlight desk.

**Title line:** Qissa Studio: Human-in-the-Loop Pipeline for Retention-Optimized Serialized Stories  
**Hackathon:** Agentic Cinema: The Blockbuster Hackathon  
**Track:** Parallel  
**Repo:** https://github.com/DHYEYPATL/Qissa-Studio  
**License:** MIT (file at repo root — confirm it shows in GitHub About)

### Stage One checklist
- [x] Public repo + MIT + run instructions
- [x] Gemini via `google-genai` (`qissa/llm.py`)
- [x] ADK `root_agent` (`adk_agent/agent.py`)
- [x] Parallel Search API via `parallel-web` (`qissa/search.py`)
- [x] Web app (FastAPI) for the hosted URL
- [x] Web app hosted: https://qissa-studio-d7lrfpwafq-uc.a.run.app
- [ ] **You** record the ≤3 min screencast (`docs/DEMO_SCRIPT.md`)
- [ ] **You** submit on Devpost, track = Parallel (`docs/SUBMISSION.md`)

Rules map: `docs/COMPLIANCE.md`.

A qissa is a story. Qissa Studio does not replace writers. It de-risks greenlight for serialized audio.

```
Trends (Parallel Search) → bible + episodes (Gemini)
→ Twin pre-score → HUMAN GATE
→ opt-in 3% canary (only after approve; scored on the hit bar)
→ diagnosis → 3–4 directed rewrites
→ graduate to audio  OR  archive + rework brief
→ same loop rescues stalled catalog titles
```

Generation is the easy part. The product is what we refuse to publish, and how fast the next draft gets better.

## Why this, not another writer bot

Serialized-audio desks already know acquisition is not the problem. Long-term retention is. Episodes live at 11–15 minutes. Listeners binge. They also drop when structure fails: late agency, unpaid mystery piles, mid-sentence ads, generated coffee talk, coin walls after the hook, 174 episodes of the same wound. Regional and niche shows die in committee because a flop is expensive.

If we only ship "Gemini writes episode 1," we lose this hackathon. The loop is the invention.

## Honest about twins and canary

- Twins are seven persona cards with concrete behaviors. Not a trained causal model of a platform.
- Canary is simulated, opt-in 3%, **blocked until a human approves**. We do not pretend we dumped experiments on a live base.
- Graduation is catalog-relative against *hit* titles in the same bucket. No magic 60%. Flops do not lower the bar.
- Originality is overlap + a planted clone (`His Secret Howl`) + Parallel near-duplicate search. Not a courtroom engine.
- Monetization tags sit after an emotional beat. They are not the pitch.

## Stack (rules-legal)

Official rules ban OpenAI, Anthropic, and other agent frameworks. LangGraph / CrewAI / GPT are not used.

| Job | Tool | File |
|---|---|---|
| Trend Scout + near-dupe sweep | Parallel Search API (`parallel-web`) | `qissa/search.py` |
| Showrunner / writer / rewrite | Gemini via `google-genai` | `qissa/llm.py` |
| Multi-agent surface | Google ADK `root_agent` | `adk_agent/agent.py` |
| Graph + state | Python `SeriesState` | `qissa/state.py` |
| Hosting | FastAPI + Cloud Run | `web/app.py`, `Dockerfile` |

## Agents we actually built

Trend Scout · Showrunner · Episode Writer · Canon Guard · Twin Bench · Retention Critic · Originality Guard · Human Gate · Payoff Ledger · Catalog Rescue

Stubbed on purpose: merch marketplace, live user canary, Databricks, full TTS mix, multi-language adapter.

Interactive PS: episode 2 has two pre-written branches (`keep` vs `tell`), scored against the same twins.

## Run

```bash
pip install -r requirements.txt
cp .env.example .env
python -m qissa eval
python -m qissa
uvicorn web.app:app --port 8080
```

ADK: `adk web` (entrypoint `adk_agent/agent.py`).

Tests: `python -m unittest tests.test_qissa tests.test_parser -v`

## Rubric map

- Technological implementation: Parallel in `qissa/search.py`. Gemini in `qissa/llm.py`. ADK tools wrap the same graph. `/health` prints the eval harness.
- Design: studio floor — trend, ledger, twins with coin-willingness, heatmap, diagnosis, before/after, human box, branches.
- Impact: greenlight and salvage for serialized-audio desks. Failed series become briefs.
- Idea quality: test structure before production cost. Partner used as live trend grounding *and* near-duplicate search.

## Demo

`docs/DEMO_SCRIPT.md`. Show the gate. Show a structural diagnosis. Show archive-instead-of-delete. Click a Parallel URL.

GCP credit form closes 31 Aug 2026 23:59 PST. Parallel keys: https://platform.parallel.ai
