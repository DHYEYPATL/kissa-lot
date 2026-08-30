# Devpost form — paste this

**Name:** Qissa Studio

**Tagline:** Human-in-the-loop pipeline for retention-optimized serialized stories

**Track:** Parallel

**Repo:** https://github.com/DHYEYPATL/Qissa-Studio

**License:** MIT (file at repo root)

**Hosted project URL:** *(paste Cloud Run URL after `gcloud run deploy`)*

**Demo video URL:** *(YouTube/Vimeo, ≤3 min, English, app on camera — follow docs/DEMO_SCRIPT.md)*

## Built with

google-genai, google-adk, google-cloud-aiplatform, parallel-web, FastAPI, Cloud Run, Pydantic

## Description

Qissa Studio is a greenlight valve for serialized audio. A flop is weeks of bible work; most drop-off is structural.

Parallel Search grounds a trend brief (rising vs saturated tropes, regional moments, listener pains) and a near-duplicate sweep. Gemini drafts the bible, characters, episode 1, and the keep/tell branches. Seven digital-twin personas pre-score the draft against minute-level behaviors — skip after 90 seconds of exposition, stay if a costly choice lands before minute 8, refuse a coin if the last 170 episodes never paid a wound. A human must approve, reject, or direct in natural language. Only approve starts a simulated 3% opt-in canary, scored against the *hit* bar in the same genre bucket. Failures leave an archive and a rework brief. Generation is the easy part. The product is what we refuse to publish.

Not used (rules-banned): OpenAI, Anthropic, LangGraph, CrewAI, any non-Google model.

Runtime proof:

- `qissa/search.py` calls `parallel.Parallel(...).search(...)`
- `qissa/llm.py` calls `google.genai.Client`
- `adk_agent/agent.py` exposes `root_agent` with those tools

## What we learned

One research query is mush; four jobs are a brief. Averaging flops into a "catalog bar" makes weak drafts look fine — we switched to a hit-bar. Twins without minute-level behaviors smell like theater. Canary before a human is a political error. Never mid-sentence ads. Never a magic 60%.

## How it maps to judging

- Implementation: required packages imported and called; eval harness catches a planted clone and a bad-pacing script offline.
- Design: studio floor UI — trend, ledger, twins, heatmap, diagnosis, before/after, human box — not a chat window.
- Impact: named buyer (serialized-audio editor), named cost (weeks before you know if anyone stays), salvage path for stalled catalog titles.
- Idea: Parallel is the living ear of the week, not a citation sticker.
