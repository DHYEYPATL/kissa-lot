// Qissa Studio — Audio Production Desk Client Controller

const PRESETS = {
  surat: {
    genre: "regional family drama",
    seed: "A night-shift cook in Surat keeps her late mother's recipe book taped under a prep table. A food-show producer wants the pour as a clip.",
    fact: "The tape under the table still smells like asafetida from last Undhiyu season."
  },
  pune: {
    genre: "regional family drama",
    seed: "An elderly radio repairman in Pune finds an unposted 1947 Partition letter soldered inside an antique valve set brought in by a corporate land buyer.",
    fact: "The solder flux smells like pine resin and the valve is a 1947 Philips Miniwatt."
  },
  kodaikanal: {
    genre: "mythic thriller",
    seed: "A night-bus driver on the Kodaikanal ghat road hears a passenger in seat 14 whisper family secrets that only his dead brother knew.",
    fact: "The ticket was punched at the Batlagundu toll booth with a brass star clipper."
  },
  whitefield: {
    genre: "campus dark romance",
    seed: "A junior audio annotator in Bangalore cleans late-night server room recordings, only to hear her own voice from a college night she cannot remember.",
    fact: "The security lanyard is frayed at the clip from a 2019 Bellandur flood."
  }
};

const openForm = document.getElementById("open");
const board = document.getElementById("board");
const tickerWrap = document.getElementById("ticker-wrap");
const ticker = document.getElementById("ticker");
const btnRun = document.getElementById("run");
const btnText = document.getElementById("btn-text");
const btnSpin = document.getElementById("btn-spin");

// 1. PRESET BUTTONS
document.querySelectorAll(".preset-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".preset-btn").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    const p = PRESETS[btn.dataset.preset];
    if (p) {
      document.getElementById("genre-select").value = p.genre;
      document.getElementById("seed-input").value = p.seed;
      document.getElementById("fact-input").value = p.fact;
    }
  });
});

// 2. QUICK NOTES IN GATE DOCK
document.querySelectorAll(".quick-note-chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    const noteArea = document.getElementById("note");
    noteArea.value = chip.dataset.note;
    noteArea.focus();
  });
});

// 3. DESK TABS SWITCHER
document.querySelectorAll(".desk-tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".desk-tab").forEach((t) => t.classList.remove("active"));
    document.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("active"));
    tab.classList.add("active");
    const panelId = `tab-${tab.dataset.tab}`;
    const panel = document.getElementById(panelId);
    if (panel) panel.classList.add("active");
  });
});

let currentSessionId = "";

// 4. SUBMIT STORY FORM
openForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  setLoading(true);
  tickerWrap.hidden = false;
  ticker.innerHTML = `
    <li>📡 <strong>Trend Scout:</strong> Querying Parallel Search for weekly tropes & complaints...</li>
    <li>✍️ <strong>Showrunner:</strong> Drafting audio bible, character wounds & 12-min Episode 1...</li>
    <li>🎧 <strong>Twin Bench:</strong> Pre-scoring retention against 7 picky listener personas...</li>
    <li>🔒 <strong>Human Gate:</strong> Holding draft for director review (Canary blocked)...</li>
  `;

  try {
    const formData = new FormData(openForm);
    if (currentSessionId) formData.set("session_id", currentSessionId);
    const res = await fetch("/api/open", { method: "POST", body: formData });
    const data = await res.json();
    if (data.session_id) currentSessionId = data.session_id;
    paint(data);
    updateStepper(2);
    // Update packet download URL with session_id
    const exportBtn = document.getElementById("btn-export-packet");
    if (exportBtn) exportBtn.href = `/api/packet?session_id=${encodeURIComponent(currentSessionId)}`;
    board.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (err) {
    ticker.innerHTML += `<li style="color:var(--terracotta);">Error running desk: ${err.message}</li>`;
  } finally {
    setLoading(false);
  }
});

// 5. HUMAN GATE ACTIONS (Direct / Approve / Reject)
document.querySelectorAll("[data-act]").forEach((btn) => {
  btn.addEventListener("click", async () => {
    const action = btn.dataset.act;
    const note = document.getElementById("note").value;
    btn.disabled = true;
    
    try {
      const data = new FormData();
      data.set("action", action);
      data.set("note", note);
      if (currentSessionId) data.set("session_id", currentSessionId);
      const res = await fetch("/api/gate", { method: "POST", body: data });
      const state = await res.json();
      if (state.session_id) currentSessionId = state.session_id;
      paint(state);
      if (action === "approve") {
        updateStepper(3);
      }
    } catch (err) {
      alert("Error processing gate decision: " + err.message);
    } finally {
      btn.disabled = false;
    }
  });
});

function setLoading(isLoading) {
  btnRun.disabled = isLoading;
  if (btnSpin) btnSpin.hidden = !isLoading;
  btnText.textContent = isLoading ? "Analyzing Structure & Pacing..." : "Test Story Structure & Retention";
}

function updateStepper(stepNum) {
  document.getElementById("step-pill-1").classList.toggle("active", stepNum >= 1);
  document.getElementById("step-pill-2").classList.toggle("active", stepNum >= 2);
  document.getElementById("step-pill-3").classList.toggle("active", stepNum >= 3);
}

// 6. MAIN RENDER / PAINT FUNCTION
function paint(s) {
  if (s.error) {
    ticker.innerHTML += `<li style="color:var(--terracotta);">${s.error}</li>`;
    return;
  }

  board.hidden = false;
  
  // Pipeline Ticker Steps
  if (s.steps && s.steps.length) {
    ticker.innerHTML = s.steps.map((x) => `<li>✓ ${x}</li>`).join("");
  }

  // Header Story Meta
  document.getElementById("story-title").textContent = s.title || "Untitled Lot";
  document.getElementById("story-logline").textContent = s.logline || s.seed || "";
  
  // Verdict Pill
  const verdictPill = document.getElementById("verdict-pill");
  const verdictLabel = document.getElementById("verdict-label");
  if (s.status === "canary" || s.canary?.ran) {
    verdictPill.style.borderColor = "var(--jade-green)";
    verdictPill.style.background = "var(--jade-soft)";
    verdictLabel.style.color = "var(--jade-green)";
    verdictLabel.textContent = "🟢 APPROVED — 3% CANARY SIMULATION ACTIVE";
  } else if (s.status === "archive") {
    verdictPill.style.borderColor = "var(--terracotta)";
    verdictPill.style.background = "var(--terracotta-soft)";
    verdictLabel.style.color = "var(--terracotta)";
    verdictLabel.textContent = "📁 ARCHIVED — REWORK BRIEF LOGGED";
  } else {
    verdictPill.style.borderColor = "var(--gold-primary)";
    verdictPill.style.background = "var(--gold-soft)";
    verdictLabel.style.color = "var(--gold-dark)";
    verdictLabel.textContent = "🟡 " + (s.verdict || "HOLD FOR HUMAN GREENLIGHT");
  }

  // Summary Metrics
  const twins = s.twin_scores || [];
  const avgTwinScore = twins.length 
    ? Math.round(twins.reduce((acc, t) => acc + (t.score || 0), 0) / twins.length)
    : "--";
  document.getElementById("metric-twin-score").textContent = avgTwinScore + " / 100";

  const ep1 = s.episodes?.[0] || {};
  document.getElementById("metric-first-turn").textContent = (ep1.first_turn_minute || 5.0) + "m";
  document.getElementById("turn-badge").textContent = `Costly Turn: Minute ${ep1.first_turn_minute || 5.0}`;
  
  const ledger = s.ledger || {};
  document.getElementById("metric-payoff").textContent = (ledger.ratio ?? 0.5);
  document.getElementById("ledger-ratio").textContent = (ledger.ratio ?? 0.5);
  document.getElementById("ledger-rule").textContent = ledger.rule || "Pay one secret. Leave one open.";

  // Render 7 Twin Persona Cards
  const twinsContainer = document.getElementById("twins-cards");
  twinsContainer.innerHTML = twins.map((t) => {
    const isPass = t.would_start_next || t.score >= 70;
    const scoreClass = isPass ? "twin-score-pass" : "twin-score-fail";
    const statusText = t.would_finish ? "Will Finish Ep 1" : `Drops @ ${t.drop_minute}m`;
    const coinIcon = t.would_spend_coin ? "🪙 Will spend coin" : "🚫 Refuses coin";
    const coinClass = t.would_spend_coin ? "twin-coin-yes" : "twin-coin-no";
    const cohortLabel = t.cohort === "high_retention" ? "High Retention" : "Skeptic / Low Retention";

    return `
      <div class="twin-card">
        <div class="twin-head">
          <div>
            <div class="twin-name">${t.persona_name}</div>
            <div class="twin-cohort">${cohortLabel}</div>
          </div>
          <span class="twin-score-badge ${scoreClass}">${t.score} / 100</span>
        </div>
        <div class="twin-behavior">
          "${(t.reasons || [])[0] || 'Evaluates dialogue pacing and character agency.'}"
        </div>
        <div class="twin-footer">
          <span class="${isPass ? 'tone-green' : 'tone-red'}">${statusText}</span>
          <span class="${coinClass}">${coinIcon}</span>
        </div>
      </div>
    `;
  }).join("");

  // Render Payoff Ledger & Memory Threads
  const ledgerThreads = document.getElementById("ledger-threads");
  const promises = ledger.promises || [];
  const paid = ledger.paid || [];
  const openThreads = ledger.still_open || (s.memory?.open_threads || []);
  ledgerThreads.innerHTML = `
    <ul class="clean-list">
      ${paid.map(p => `<li><span class="badge-tag" style="background:var(--jade-soft);color:var(--jade-green);">PAID</span> ${p}</li>`).join("")}
      ${openThreads.map(o => `<li><span class="badge-tag" style="background:var(--gold-soft);color:var(--gold-dark);">OPEN</span> ${o}</li>`).join("")}
    </ul>
  `;

  // Render Structural Diagnoses
  const dxContainer = document.getElementById("dx-list");
  const dxs = s.diagnoses || [];
  dxContainer.innerHTML = dxs.length ? dxs.map((d) => `
    <div class="dx-item">
      <strong>⚠️ ${d.issue}</strong>
      <div style="margin-top:2px;color:var(--paper-ink);">${d.edit_op}</div>
    </div>
  `).join("") : `<div class="dx-item" style="background:var(--jade-soft);border-color:var(--jade-border);color:var(--jade-green);"><strong>✓ Clean Structure:</strong> No pacing stalls or late agency detected in Episode 1.</div>`;

  // Render Originality Near-Duplicates
  const origContainer = document.getElementById("orig-list");
  origContainer.innerHTML = (s.originality || []).map((o) => `
    <li>
      <strong>${o.title}</strong>
      <div style="font-size:12px;color:var(--paper-sub);">${o.reason}</div>
      ${o.source ? `<a href="${o.source}" target="_blank" style="font-size:11px;color:var(--terracotta);">View Source ↗</a>` : ''}
    </li>
  `).join("") || "<li>No near-duplicates found in catalog.</li>";

  // Render Canary Valve
  const canary = s.canary || {};
  const canaryPill = document.getElementById("canary-status-pill");
  const canaryDesc = document.getElementById("canary-desc");
  const canaryStats = document.getElementById("canary-stats");
  
  if (canary.ran) {
    canaryPill.textContent = "🟢 Simulated 3% Canary: Active";
    canaryPill.style.background = "var(--jade-soft)";
    canaryPill.style.color = "var(--jade-green)";
    canaryDesc.textContent = `Canary test run against ${canary.vs_catalog || "hit catalog benchmark"}. Session fit: ${canary.session_fit || "commute"}.`;
    canaryStats.hidden = false;
    document.getElementById("c-comp").textContent = (canary.completion * 100).toFixed(0) + "%";
    document.getElementById("c-next").textContent = (canary.next_start * 100).toFixed(0) + "%";
    document.getElementById("c-skip").textContent = (canary.skip_rate * 100).toFixed(0) + "%";
    document.getElementById("c-vs").textContent = canary.vs_catalog || "Pass";
  } else {
    canaryPill.textContent = "🔒 Blocked: Waiting on Human Gate";
    canaryDesc.textContent = canary.blocked_reason || "Canary simulation is gated until human director clicks 'Approve'.";
    canaryStats.hidden = true;
  }

  // Render Formatted Screenplay
  document.getElementById("ep1-title").textContent = `Episode 1: ${ep1.title || 'The Turn'} (${ep1.minutes || 12} mins)`;
  const scriptReader = document.getElementById("script-formatted");
  scriptReader.innerHTML = formatScreenplay(ep1.script || "");

  // Render Before vs After Rewrite Diff
  const baList = s.before_after || [];
  const lastBA = baList[baList.length - 1];
  const baContainer = document.getElementById("ba-diff");
  if (lastBA) {
    baContainer.innerHTML = `
      <div style="margin-bottom:8px;font-weight:700;color:var(--gold-dark);">DIRECTOR NOTE: "${lastBA.note}"</div>
      <div style="background:var(--terracotta-soft);padding:8px;border-radius:4px;margin-bottom:6px;border-left:3px solid var(--terracotta);">
        <strong style="color:var(--terracotta);">BEFORE:</strong>
        <pre style="margin:4px 0;white-space:pre-wrap;font-size:11px;">${lastBA.before}</pre>
      </div>
      <div style="background:var(--jade-soft);padding:8px;border-radius:4px;border-left:3px solid var(--jade-green);">
        <strong style="color:var(--jade-green);">AFTER:</strong>
        <pre style="margin:4px 0;white-space:pre-wrap;font-size:11px;">${lastBA.after}</pre>
      </div>
    `;
  }

  // Render Interactive Branches
  const branchesContainer = document.getElementById("branches-list");
  branchesContainer.innerHTML = (s.branch_scores || []).map((b) => `
    <div class="branch-card">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <strong>Branch: ${b.title}</strong>
        <span class="badge-tag" style="background:var(--gold-soft);color:var(--gold-dark);font-weight:700;">Twin Mean: ${b.twin_mean}</span>
      </div>
      <p>${b.note || 'Tested against twins.'}</p>
    </div>
  `).join("");

  // Render Monetization Tags
  const adsContainer = document.getElementById("ads-list");
  adsContainer.innerHTML = (s.monetization || []).map((m) => `
    <li>
      <strong>${m.kind.toUpperCase()} @ Minute ${m.minute}m</strong>
      <div style="font-size:12px;color:var(--paper-sub);">${m.note}</div>
    </li>
  `).join("");

  // Render Parallel Trends & Citations
  const trend = s.trend || {};
  renderTagList("tropes-rising", trend.tropes_rising || []);
  renderTagList("tropes-saturated", trend.tropes_saturated || []);
  renderTagList("listener-pains", trend.listener_pains || []);
  document.getElementById("trend-tone-text").textContent = trend.tone || "Mother tongue stays in the room. Contained suspense.";

  const citesGrid = document.getElementById("citations-grid");
  const citations = trend.citations || [];
  citesGrid.innerHTML = citations.length ? citations.map((c) => `
    <div class="citation-card">
      <a href="${c.url}" target="_blank" rel="noreferrer">${c.title || c.url} ↗</a>
      ${c.excerpts ? `<div style="font-size:11.5px;color:var(--paper-sub);margin-top:4px;">${c.excerpts[0] || ''}</div>` : ''}
    </div>
  `).join("") : `<div class="citation-card">Offline fallback or no citations available.</div>`;

  // Render Booth & Bible Details
  const bibleContent = document.getElementById("bible-content");
  bibleContent.innerHTML = `
    <div style="background:#fff;border:1px solid var(--paper-border);padding:14px;border-radius:var(--radius-sm);margin-bottom:12px;font-family:'Newsreader',serif;font-size:15px;">
      ${s.bible || s.logline || ''}
    </div>
  `;

  const charsList = document.getElementById("characters-list");
  charsList.innerHTML = (s.characters || []).map((c) => `
    <div style="background:#fff;border:1px solid var(--paper-border);padding:10px 14px;border-radius:var(--radius-sm);margin-bottom:8px;">
      <div style="font-weight:700;color:var(--paper-ink);">${c.name} <span style="font-size:11px;color:var(--gold-dark);font-family:'JetBrains Mono';">(${c.voice})</span></div>
      <div style="font-size:12px;color:var(--paper-sub);margin-top:2px;"><strong>Wound:</strong> ${c.wound}</div>
      <div style="font-size:12px;color:var(--paper-sub);"><strong>Goal:</strong> ${c.goal}</div>
    </div>
  `).join("");

  const boothDetails = document.getElementById("booth-details");
  const booth = s.booth || {};
  boothDetails.innerHTML = `
    <div style="background:#fff;border:1px solid var(--paper-border);padding:14px;border-radius:var(--radius-sm);font-size:13px;">
      <p><strong>Session Fit:</strong> ${booth.session_fit || 'commute'} · <strong>Night Safe:</strong> ${booth.night_safe ? 'Yes' : 'No'}</p>
      <p><strong>Atmosphere / Sound Design:</strong> ${booth.atmo || 'One room. Recorded dry.'}</p>
      <p><strong>Director Rule:</strong> ${booth.rule || 'Record narration separate. Audio only.'}</p>
    </div>
  `;
}

function renderTagList(elementId, items) {
  const el = document.getElementById(elementId);
  if (!el) return;
  el.innerHTML = items.map((x) => `<li>${x}</li>`).join("");
}

function formatScreenplay(scriptText) {
  if (!scriptText) return "<p class='empty-state'>No script content generated yet.</p>";
  
  const lines = scriptText.split("\n");
  return lines.map((line) => {
    const trimmed = line.trim();
    if (!trimmed) return "<div style='height:8px;'></div>";
    
    if (trimmed.startsWith("MEENA:")) {
      return `<div class="script-dialogue-line"><span class="speaker-tag speaker-meena">MEENA</span> ${trimmed.replace("MEENA:", "").trim()}</div>`;
    }
    if (trimmed.startsWith("ARJUN:")) {
      return `<div class="script-dialogue-line"><span class="speaker-tag speaker-arjun">ARJUN</span> ${trimmed.replace("ARJUN:", "").trim()}</div>`;
    }
    if (trimmed.startsWith("SFX:")) {
      return `<div class="script-dialogue-line"><span class="speaker-tag speaker-sfx">SFX</span> <em>${trimmed.replace("SFX:", "").trim()}</em></div>`;
    }
    if (trimmed.includes("(memory)") || trimmed.includes("(private)")) {
      return `<div class="script-dialogue-line" style="color:var(--gold-dark);font-style:italic;">${trimmed}</div>`;
    }
    return `<div class="script-dialogue-line">${trimmed}</div>`;
  }).join("");
}
