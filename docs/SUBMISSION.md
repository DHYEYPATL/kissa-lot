# Devpost submission draft — Kissa Lot

**Project name:** Kissa Lot  
**Tagline:** The development desk that listens to the crowd before you lock the script.  
**Track:** Parallel  
**Built with:** Google Gemini (`google-genai`), Google ADK, Parallel Search API (`parallel-web`), FastAPI, Cloud Run  
**Repo:** https://github.com/DHYEYPATL/kissa-lot  
**License:** MIT  

## Elevator

Kissa Lot is a production-ready agent for filmmakers and development execs. It turns a logline or screenplay into a cited greenlight packet: who the 2026 audience is, whether the pages are shootable, what to cut, and which live sources say so.

## The problem

Most films die before day one. Scripts do not lock. Locations are a handshake. Night work is treated as atmosphere. Meanwhile audiences — Reddit threads, CivicScience, regional box office — are loud about what they will leave the house for: story, cultural specificity, one image they can clip. Development still guesses.

## What it does

1. Parses production format without a model.
2. Scores schedule risk (locations, nights, VFX, cast).
3. Runs four Parallel Search calls: audience desire, market comps, authenticity, production facts.
4. Gemini writes the packet and may only cite URLs Parallel returned.
5. Shows shooting groups and a cut list in a desk UI.

## How it uses the required stack

- **Gemini / ADK:** `adk_agent/agent.py` defines `root_agent` with function tools. `kissa_lot/gemini_client.py` calls `google.genai` `client.models.generate_content`.
- **Parallel:** `kissa_lot/tools/parallel_search.py` constructs `Parallel(api_key=...)` and calls `client.search(objective=..., search_queries=..., mode=...)`.
- No OpenAI, Anthropic, or other agent frameworks.

## Data sources

Live web via Parallel. Design research (last six months) documented in `docs/RESEARCH.md`. Sample screenplay is original.

## Learnings

Retrieval has to be split by job. One "research this movie" query produces mush. Four narrow objectives — crowd, market, fact, lot — give Gemini something it cannot hallucinate past. The complexity score should stay deterministic so a missing API key cannot invent a green light.

## Next

Vertex Agent Engine deploy, Parallel Extract on the top three URLs, and a rights/clearance pass for any real names the search surfaces.
