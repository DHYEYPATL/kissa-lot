# Qissa Studio — Complete System Architecture & Codebase Explanation

> **Qissa Studio** is a **Human-in-the-Loop AI Greenlight Desk for Serialized Audio Fiction** (e.g., Pocket FM / serialized audio drama).  
> It is designed not to replace writers with generic text generators, but to **de-risk story production and optimize listener retention** before investing expensive studio recording and voice acting budgets.

---

## 1. Core Philosophy: The Problem & The Solution

### The Core Problem in Serialized Audio
In serialized audio drama (11–15 minute daily/weekly episodes), acquiring an initial listener is relatively easy, but **long-term retention is where 90% of shows fail**.
Listeners drop off due to concrete structural failures:
1. **Late agency**: The protagonist does not make an active, costly choice until late in the episode.
2. **Exposition dumps**: Long "kitchen listings" or backstory narration before anything happens.
3. **Unpaid mystery piles**: Introducing endless new questions without resolving prior promises.
4. **Mid-sentence ads & coin walls**: Placing monetization right in the middle of dramatic lines or immediately after a cliffhanger.
5. **AI "coffee talk" / slop**: Generic dialogue where characters talk about their feelings or mundane actions without subtext.
6. **Repetitive wound loops**: 170+ episodes of the same unresolved character trauma with no forward motion.

### The Qissa Solution
**"Generation is easy; what we refuse to publish, and how fast the next draft gets better, is the real product."**

Instead of generating unvetted text directly to audio, Qissa Studio runs every story pitch through a multi-agent diagnostic gauntlet:
```
Story Seed / Owned Fact
  │
  ▼
[1. Trend Scout (Parallel Search API)] ──▶ Real-time audience trends & listener complaints
  │
  ▼
[2. Showrunner & Writer (Gemini 2.5)] ──▶ Story bible, characters, & audio screenplay
  │
  ▼
[3. Canon Guard & Retention Critic] ──▶ Deterministic checks for structural flaws & canon drift
  │
  ▼
[4. Twin Bench (7 Digital Personas)] ──▶ Exact drop-minute timestamps & coin-spending willingness
  │
  ▼
[5. Interactive Branch Compare] ──▶ Multi-path evaluation (e.g., "Keep" vs "Tell" the secret)
  │
  ▼
[6. Payoff Ledger & Originality Guard] ──▶ Promise-to-resolution ratio & clone/plagiarism detection
  │
  ▼
[7. Ad-Safe Monetization & Booth Packet] ──▶ Mid-roll placement after completed emotional beats
  │
  ▼
[8. HUMAN GATE (Hold / Approve / Reject / Direct)]
  ├── APPROVE ──▶ [Simulated 3% Canary Test] ──▶ [Hit-Bar Graduation vs Catalog] ──▶ Graduate to Audio / Archive
  ├── REJECT  ──▶ [Archive + Rework Brief]
  └── DIRECT  ──▶ [Script Doctor Iteration Cycle] ──▶ Re-evaluates Twin Bench & Critic (Max 4 Cycles)
```

---

## 2. End-to-End Workflow & Pipeline Execution

The pipeline is triggered either through the **FastAPI Web UI (`web/app.py`)**, the **CLI (`python -m qissa`)**, or the **Google ADK Agent (`adk_agent/agent.py`)**.

### Step 1: Opening the Story Lot (`run_desk` in `qissa/pipeline.py`)
1. **Seed & Owned Fact**: The user inputs a logline/seed and an optional **"Owned Fact"** (a specific lived-experience detail that AI cannot invent, like a specific street, spice, or family debt).
2. **Catalog Rescue Check**: If the seed matches an existing stalled catalog title (e.g., *Night Shift Surat*), the system marks it as a rescue attempt.
3. **Trend Scouting (`qissa/search.py` & `qissa/craft.py`)**: Queries the **Parallel Search API** (`parallel-web`) to identify current listener complaints, rising tropes, and saturated clichés. If Gemini is available, it synthesizes the search results while preserving real citation URLs. (Falls back to offline trend data if no API key is provided).
4. **Showrunning & Scriptwriting (`qissa/llm.py` & `qissa/craft.py`)**: Uses **Gemini 2.5 Flash** (`google-genai`) with strict contrastive prompting to generate a full audio script (with SFX cues and dialogue formatting), characters with wounds/secrets, season spine, and episode cliffhanger.
5. **Structural Diagnostics & Canon Guard (`qissa/diagnostics.py` & `qissa/bench.py`)**: Deterministically scans the script for late agency, heavy exposition, soft cliffhangers, AI clichés, and character consistency violations.
6. **Twin Bench Simulation (`qissa/personas.py` & `qissa/bench.py`)**: Runs the script against 7 distinct listener personas, determining exactly when each listener would drop or if they would pay coins to continue.
7. **Branch Scoring (`qissa/bench.py` & `qissa/craft.py`)**: Generates rich multi-path scripts for Episode 2 (Branch A: "Keep the secret" vs Branch B: "Speak on mic") and compares twin preferences.
8. **Payoff Ledger (`qissa/bench.py`)**: Audits open narrative promises vs paid revelations ("Pay one, leave one. Never pile").
9. **Originality Guard (`qissa/bench.py`)**: Calculates token similarity against the studio catalog and performs live Parallel searches to flag near-duplicates or planted clone tropes (e.g., werewolf billionaire tropes).
10. **Monetization & Booth Packet (`qissa/uniqueness.py` & `qissa/bench.py`)**: Identifies ad-safe timestamps after emotional beats and builds a recording booth spec for voice actors and sound engineers.
11. **State Pauses at Human Gate**: The canary test is **strictly blocked** (`ran=False`, `blocked_reason="Canary waits for human greenlight. Opt-in 3% only. AI disclosed."`) until a human producer reviews and approves the packet.

### Step 2: Human Gate Decision (`human_gate` in `qissa/pipeline.py`)
A human producer has three choices:
* **Approve**: Unlocks the simulated 3% canary release. The canary completion rate is measured against the **Hit Bar** of the genre in the studio catalog. If it beats the hit bar, it **Graduates to Audio**; otherwise, it is **Archived with a Rework Brief**.
* **Reject**: Moves the project directly to **Archive** and generates a comprehensive rework brief preserving salvageable characters and the owned fact.
* **Direct (Rewrite)**: The producer provides natural language feedback (e.g., *"Move the costly turn to minute 4 and make Meena reveal the invoice"*). The system:
  - Increments the iteration cycle (capped at 4 cycles to prevent endless AI churn).
  - Invokes Gemini / Script Doctor to rewrite the screenplay according to the director note.
  - Updates narrative memory events and payoff ledger.
  - Re-evaluates diagnostics, twins, ledger, and originality.
  - Generates a **Before/After Diff** for the producer to inspect.

---

## 3. Deep-Dive into Codebase Modules

```
Qissa-Studio/
├── qissa/                  # Core domain logic, agents, and scoring engine
│   ├── __init__.py         # Package initialization
│   ├── __main__.py         # CLI entry point (python -m qissa [eval])
│   ├── agents.py           # Public agent function exports
│   ├── bench.py            # Twin simulation, canary, payoff ledger, graduation
│   ├── catalog.py          # Synthetic studio catalog & hit-bar calculation
│   ├── craft.py            # Showrunner, trend scout, and director rewrite logic
│   ├── diagnostics.py      # Deterministic story structure scanner
│   ├── eval_harness.py     # Offline benchmark evaluation (good vs bad stories)
│   ├── llm.py              # Google GenAI (Gemini) SDK client & robust JSON extraction
│   ├── parser.py           # Fountain/Screenplay parser & complexity scoring
│   ├── personas.py         # 7 digital twin listener profiles
│   ├── pipeline.py         # Main pipeline flow (run_desk & human_gate)
│   ├── search.py           # Parallel Search API integration (parallel-web)
│   ├── sessions.py         # SQLite + memory thread-safe session persistence store
│   ├── state.py            # Pydantic data schemas for full studio state
│   └── uniqueness.py       # Slop detector, contrastive rules, booth specs
├── adk_agent/              # Google Agent Development Kit (ADK) root agent
│   ├── __init__.py
│   └── agent.py            # ADK Agent definition & tool wrapping (session-isolated)
├── web/                    # FastAPI web application & studio frontend
│   ├── app.py              # REST API endpoints & session management
│   └── static/             # Frontend assets
│       ├── index.html      # Studio floor UI layout
│       ├── styles.css      # Dark-mode aesthetic studio styling
│       └── app.js          # Interactive frontend logic & API communication
├── docs/                   # Documentation & hackathon compliance guides
│   ├── COMPLIANCE.md       # Rule-by-rule hackathon verification
│   ├── DEMO_SCRIPT.md      # Video walkthrough script
│   ├── JUDGING.md          # Scoring rubric breakdown
│   ├── RESEARCH.md         # Industry research & listener retention insights
│   ├── SETUP_KEYS.md       # API key configuration guide
│   └── SUBMISSION.md       # Devpost submission text
├── examples/               # Example screenplay assets (e.g., night_kitchen.fountain)
├── tests/                  # Unit test suite
│   ├── test_parser.py      # Tests for Fountain script parsing
│   └── test_qissa.py       # Tests for pipeline, twins, session store, hit-bar, and gate isolation
├── .env.example            # Environment variable template
├── Dockerfile              # Container deployment spec for GCP Cloud Run
├── deploy_gcp.ps1          # PowerShell deployment script for Cloud Run
├── pyproject.toml          # Build configuration
└── requirements.txt        # Python package dependencies
```

---

## 4. Key Subsystems Explained in Detail

### A. SQLite & Memory Session Store (`qissa/sessions.py`)
Persists all active story lot states across server restarts, worker threads, and multi-user requests. Provides:
- Thread-safe SQLite database (`.qissa_sessions.db`).
- In-memory cache for sub-millisecond retrieval.
- Browser URL query & `localStorage` auto-restoration.

### B. The 7 Digital Twin Personas (`qissa/personas.py`)
Rather than relying on abstract demographics, Qissa uses 7 distinct behavior profiles modeled after real user complaints from Reddit and app stores:

| Persona | Archetype | Drop Triggers | Retention Keys |
|---|---|---|---|
| **Meera (24)** | Commuter (Dual Language) | Mid-sentence ads, uniform voices | Costly choice before min 8 |
| **Arun (31)** | Night-time Sleep Listener | Yelling sound mix, unpaid mysteries | 1 secret paid, 1 new question |
| **Priya (19)** | AI Skeptic | Generated coffee talk / filler | Differentiated voices, private inner thoughts |
| **Dev (27)** | Binge Listener (10 eps/night) | Repeating reveals for 170 eps | Relationship vector progression |
| **Leo (34)** | r/audiodrama Purist | 5-min intro on 11-min show, threat ads | Ad only after finished beat |
| **Nani (58)** | Regional Mother-Tongue Fan | Regional culture flattened to generic English | Mother tongue in the kitchen |
| **Rhea (29)** | Burned Coin Buyer | Cliffhangers that exist only to sell coins | Paid minute actually reveals answers |

### C. Deterministic Retention Diagnostics (`qissa/diagnostics.py`)
Qissa does not rely on an LLM to grade another LLM. It uses deterministic heuristics to identify flaws:
- **Exposition Overload**: Flags if exposition > 3.5 minutes.
- **Late Agency**: Flags if protagonist makes no decision before minute 8.
- **Soft Cliffhanger**: Flags if episode ends without an urgent open question.
- **Coffee Talk**: Flags filler phrases like `"let us talk while"`, `"smells delicious"`, `"here is your mug"`.
- **Mystery Pile-on**: Flags adding questions without resolving prior open threads.
- **Urgency then Thesis**: Flags long inner philosophical monologues during ticking-clock climaxes.
- **Volume Spikes**: Flags screaming / excessive punctuation that disrupts sleep listeners.
- **Mid-sentence Ads**: Flags ad tags placed inside active dialogue.

### D. The Hit-Bar Graduation Logic (`qissa/catalog.py`)
Traditional benchmark systems average all catalog titles (including flops), which lowers the passing bar.  
**Qissa calculates the graduation bar using ONLY hit titles** within the same genre:
$$\text{Graduation Hurdle} = \text{Mean Completion Rate of Hit Shows in Genre}$$
- *Example (Regional Family Drama)*: *The Undhiyu Letters* (61%) and *Pour on Camera* (57%) define the bar at **59%**. Stalled shows like *Night Shift Surat* (44%) are excluded from lowering the bar.

### E. Google ADK & Parallel Search Integration
- **Google ADK (`adk_agent/agent.py`)**: Implements `root_agent = Agent(...)` with session-isolated tools `open_qissa`, `human_decide`, `search_live_web`, `catalog_bars`, and `eval_desk`. Built strictly with `google-genai` and `google-adk` without disallowed frameworks.
- **Parallel Search (`qissa/search.py`)**: Uses the official `parallel-web` SDK to fetch real-time serialized audio trends and sweep the web for near-duplicate premises.

### F. Offline Eval Harness (`qissa/eval_harness.py`)
Allows judges and automated test suites to verify that the diagnostics engine works 100% offline:
- Tests a known **GOOD** script (*Night Kitchen*) vs a known **BAD** script (*His Secret Howl* coffee talk clone).
- Asserts that:
  1. Good script is not flagged with soft cliffhangers.
  2. Bad script is flagged for exposition and coffee talk.
  3. Planted clone is caught by Originality Guard.
  4. Digital Twins rank Good ($72.6$) significantly above Bad ($14.4$).

---

## 5. Web API Endpoints (`web/app.py`)

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | `GET` | Serves the interactive Studio Floor web application (`index.html`). |
| `/health` | `GET` | Returns system health, runtime configuration, and runs the evaluation benchmark. |
| `/api/catalog` | `GET` | Returns catalog titles, stalled shows for rescue, and genre hit bars. |
| `/api/sessions` | `GET` | Lists recent story lot sessions for recovery and multi-session switching. |
| `/api/session` | `GET` | Retrieves state of a specific session by `session_id`. |
| `/api/open` | `POST` | Opens a new story lot (`seed`, `genre`, `owned_fact`), runs agents, and pauses at Human Gate. |
| `/api/gate` | `POST` | Submits human decision (`approve`, `reject`, `direct`) and advances the pipeline. |
| `/api/packet` | `GET` | Exports a plain-text 1-page GO/NO-GO production decision packet for studio execs. |

---

## 6. How to Run & Test

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment (Optional for live Gemini/Parallel calls)
cp .env.example .env

# 3. Run offline evaluation benchmark
python -m qissa eval

# 4. Run automated test suite (12 tests)
python -m unittest discover -s tests -v

# 5. Start the web application
python -m uvicorn web.app:app --host 127.0.0.1 --port 8080
```
Open [http://127.0.0.1:8080](http://127.0.0.1:8080) in any browser to interact with the studio floor.
