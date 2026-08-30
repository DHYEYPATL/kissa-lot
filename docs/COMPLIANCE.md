# Stage One / Stage Two map — official rules, not marketing

Hackathon: Agentic Cinema: The Blockbuster Hackathon  
Track we enter: **Parallel**  
Official rules: https://agentic-cinema.devpost.com/rules  
Deadline: 9 Sep 2026, 2:00 PM PT

This file exists so a judge can fail us in thirty seconds if we cheated,
and pass us in thirty seconds if we did not.

## Stage One — pass / fail

| Official requirement | Status | Proof |
|---|---|---|
| Functional agent, not a slide | PASS (code) | `qissa/pipeline.py` `run_desk` + `human_gate`; UI `web/` |
| Powered by Gemini | PASS (code) | `qissa/llm.py` → `from google import genai` → `client.models.generate_content` |
| Google Cloud Agent Builder / ADK | PASS (code) | `adk_agent/agent.py` `from google.adk import Agent` + `root_agent` |
| Accepted GCP packages | PASS | `requirements.txt`: `google-adk`, `google-genai`, `google-cloud-aiplatform` |
| Partner product at runtime | PASS (code) | `qissa/search.py` `from parallel import Parallel` + `client.search(...)` |
| Parallel Search API, not README sticker | PASS | Official `parallel-web` SDK. Fallback only if key missing. |
| Media / entertainment workflow | PASS | Serialized-audio greenlight for writers + studio desks |
| Audience: filmmakers, screenwriters, studio crews, or fans | PASS | Screenwriters / audio editors / development desks |
| Public repo | PASS | https://github.com/DHYEYPATL/kissa-lot |
| Complete OSS license at repo root | PASS | `LICENSE` MIT |
| Instructions to run | PASS | README |
| No banned AI (OpenAI, Anthropic, other agent frameworks) | PASS | Grep-clean. No LangGraph / CrewAI / LangChain agent loop |
| Runs on web | PASS | FastAPI + static UI |
| Hosted URL | **USER** | Cloud Run. Until this is live, Stage One can fail. |
| ≤3 min demo video, English, app on camera, not a trailer | **USER** | `docs/DEMO_SCRIPT.md` |
| Devpost form + Parallel track selected | **USER** | `docs/SUBMISSION.md` |
| New work in contest window | PASS (intent) | Built for this hackathon |

## Stage Two — four equal criteria

### Technological Implementation
Deterministic multi-step graph: Parallel trend + near-dupe → Gemini bible/episode → critic → seven twins → human gate → optional 3% canary → graduate or archive. Same graph exposed as ADK tools. Offline eval harness proves the critic without keys.

### Design
Studio floor, not a chat toy. Human is a required step. Before/after of a directed rewrite. Canary valve visible as blocked until approve.

### Potential Impact
Named job: serialized-audio editor. Named cost: weeks of bible before you know if a commuter stays. Named refusal: do not publish the structurally dead draft. Catalog rescue for stalled titles. Not a Pocket FM contract. Not a live user experiment.

### Quality of the Idea
Parallel is the living ear of the week (tropes + listener pain + near-duplicates), not a citation footer. Gemini writes. The invention is the gate.

## What this is not
- Not a film generator.
- Not a Pocket FM scrape or partnership.
- Not a trained recommender.
- Not a live 3% experiment on real listeners.
- Not commercially launched software. It is a working desk prototype.
