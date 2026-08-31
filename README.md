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

## The Real Industry Crisis: Why Qissa Exists

> *"User acquisition isn't the challenge... long-term retention is."*  
> — **Rohan Nayak, Co-Founder & CEO, Pocket FM** (June 2026)

Serialized audio platforms (Pocket FM, Kuku FM, ReelShort Audio) produce hundreds of 11–15 minute daily episodes. While top hits generate millions in revenue, platforms face **massive listener drop-off and trust erosion** driven by upstream structural failures:

1. **Coin Walls & Dark Pattern Backlash**: Hooking listeners then locking episodes behind aggressive coin walls or cliffhangers engineered purely for payment.
2. **174 Episodes of Unpaid Wounds**: Stalling narrative progress and looping the same trauma without payoff.
3. **Mid-Sentence Commercials**: Placing programmatic audio ads directly inside dramatic lines (causing up to 40% first-time listener churn).
4. **Flattened AI "Coffee Talk"**: AI generation collapsing authentic regional dialect into generic English exposition.
5. **Slow Agency**: Protagonist taking >8 minutes to make a costly choice in a 12-minute episode.

### The Missing Layer: Pre-Production Greenlight
Existing platforms run post-publishing analytics: they discover a story has failed **after spending $5,000–$15,000 on studio voice actors and sound engineering**.

**Qissa Studio is the pre-production retention desk**:
- **Pre-scores retention drop-off at Episode 1** using 7 digital listener twins.
- **Enforces the "Pay One, Leave One" Ledger** so mysteries resolve on mic.
- **Audits Dark Pattern Risk & Dialect Texture** before recording budgets are committed.
- **Strict Human Gate**: Pauses before production; canary simulation runs strictly upon human greenlight.
- **Slack-Ready Decision Packet**: 1-click GO / NO-GO executive export.

## Honest about Twins and Canary

- **Twins**: Seven persona cards with concrete listener behaviors (commute binge, skeptic, dialect-first, sleep-listen).
- **Canary**: Simulated 3% opt-in cohort model, **strictly blocked until a human approves**.
- **Graduation Bar**: Catalog-relative against *hit* titles in the genre bucket (e.g. 59% for Regional Family Drama). Flops never lower the bar.
- **Originality Guard**: Token overlap similarity + planted clone detection + Parallel near-duplicate search.
- **Monetization Safety**: Tags sit strictly after resolved emotional beats—never mid-sentence or within 60s of a cliffhanger.

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
