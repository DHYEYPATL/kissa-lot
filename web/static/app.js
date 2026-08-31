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

let currentSessionId = "";
let showAllDx = false;
let currentDiagnoses = [];

const pitchDesk = document.getElementById("pitch-desk");
const openForm = document.getElementById("open");
const board = document.getElementById("board");
const tickerWrap = document.getElementById("ticker-wrap");
const ticker = document.getElementById("ticker");
const btnRun = document.getElementById("run");
const btnText = document.getElementById("btn-text");
const btnSpin = document.getElementById("btn-spin");
const directDrawer = document.getElementById("direct-drawer");

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

// 2. TOGGLE DIRECT REWRITE DRAWER
const btnToggleDirect = document.getElementById("btn-toggle-direct");
const btnCloseDirect = document.getElementById("btn-close-direct");
if (btnToggleDirect) {
  btnToggleDirect.addEventListener("click", () => {
    directDrawer.hidden = !directDrawer.hidden;
    if (!directDrawer.hidden) {
      document.getElementById("note").focus();
    }
  });
}
if (btnCloseDirect) {
  btnCloseDirect.addEventListener("click", () => {
    directDrawer.hidden = true;
  });
}

// 3. QUICK NOTE CHIPS
document.querySelectorAll(".chip-btn").forEach((chip) => {
  chip.addEventListener("click", () => {
    const noteArea = document.getElementById("note");
    noteArea.value = chip.dataset.note;
    noteArea.focus();
  });
});

// 4. DESK TABS SWITCHER
document.querySelectorAll(".tab-nav-btn").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab-nav-btn").forEach((t) => t.classList.remove("active"));
    document.querySelectorAll(".tab-content-panel").forEach((p) => p.classList.remove("active"));
    tab.classList.add("active");
    const panelId = `tab-${tab.dataset.tab}`;
    const panel = document.getElementById(panelId);
    if (panel) panel.classList.add("active");
  });
});

// 5. NEW STORY LOT BUTTON
const btnNewLot = document.getElementById("btn-new-lot");
if (btnNewLot) {
  btnNewLot.addEventListener("click", () => {
    currentSessionId = "";
    localStorage.removeItem("qissa_session_id");
    const url = new URL(window.location);
    url.searchParams.delete("session");
    window.history.replaceState({}, "", url);
    
    board.hidden = true;
    pitchDesk.hidden = false;
    document.getElementById("header-session-tag").hidden = true;
    openForm.reset();
    document.getElementById("seed-input").focus();
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
}

// 6. TOGGLE ALL DIAGNOSES EXPANDER
const btnToggleDx = document.getElementById("btn-toggle-all-dx");
if (btnToggleDx) {
  btnToggleDx.addEventListener("click", () => {
    showAllDx = !showAllDx;
    renderDiagnoses(currentDiagnoses);
    btnToggleDx.textContent = showAllDx ? "Collapse Diagnoses ▴" : "Show All Diagnoses ▾";
  });
}

// 7. SUBMIT STORY FORM
openForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  setLoading(true);
  tickerWrap.hidden = false;
  ticker.innerHTML = `
    <li>📡 <strong>Step 1: Trend Scout:</strong> Querying Parallel Search API for weekly listener pains...</li>
    <li>✍️ <strong>Step 2: Showrunner:</strong> Gemini 2.5 generating audio bible, characters & Episode 1...</li>
    <li>🎧 <strong>Step 3: Twin Bench:</strong> Simulating drop timers against 7 digital personas...</li>
    <li>🔒 <strong>Step 4: Human Gate:</strong> Pausing at Human Gate. Canary testing is blocked.</li>
  `;

  try {
    const formData = new FormData(openForm);
    if (currentSessionId) formData.set("session_id", currentSessionId);
    const res = await fetch("/api/open", { method: "POST", body: formData });
    const data = await res.json();
    paint(data);
    window.scrollTo({ top: 0, behavior: "smooth" });
  } catch (err) {
    ticker.innerHTML += `<li style="color:var(--rose);">Error running desk: ${err.message}</li>`;
  } finally {
    setLoading(false);
  }
});

// 8. HUMAN GATE ACTIONS (Approve / Direct / Reject)
document.querySelectorAll("[data-act]").forEach((btn) => {
  btn.addEventListener("click", async () => {
    const action = btn.dataset.act;
    const noteArea = document.getElementById("note");
    const note = noteArea ? noteArea.value : "";
    btn.disabled = true;
    
    try {
      const data = new FormData();
      data.set("action", action);
      data.set("note", note);
      if (currentSessionId) data.set("session_id", currentSessionId);
      const res = await fetch("/api/gate", { method: "POST", body: data });
      const state = await res.json();
      paint(state);
      if (action === "direct") {
        directDrawer.hidden = true;
        if (noteArea) noteArea.value = "";
      }
    } catch (err) {
      alert("Error processing gate decision: " + err.message);
    } finally {
      btn.disabled = false;
    }
  });
});

// 9. COPY DECISION PACKET TO CLIPBOARD
const btnCopyPacket = document.getElementById("btn-copy-packet");
if (btnCopyPacket) {
  btnCopyPacket.addEventListener("click", async () => {
    if (!currentSessionId) return;
    try {
      const res = await fetch(`/api/packet?session_id=${encodeURIComponent(currentSessionId)}`);
      const text = await res.text();
      await navigator.clipboard.writeText(text);
      const label = document.getElementById("copy-packet-label");
      label.textContent = "✓ Copied!";
      setTimeout(() => {
        label.textContent = "Copy Decision Packet";
      }, 2500);
    } catch (e) {
      alert("Failed to copy packet: " + e.message);
    }
  });
}

function setLoading(isLoading) {
  btnRun.disabled = isLoading;
  if (btnSpin) btnSpin.hidden = !isLoading;
  btnText.textContent = isLoading ? "Analyzing Structure & Retention..." : "Run Retention Diagnostics & Intubate Lot";
}

// 10. MAIN RENDER FUNCTION
function paint(s) {
  if (s.error) {
    ticker.innerHTML += `<li style="color:var(--rose);">${s.error}</li>`;
    return;
  }

  if (s.session_id) {
    currentSessionId = s.session_id;
    localStorage.setItem("qissa_session_id", currentSessionId);
    const url = new URL(window.location);
    url.searchParams.set("session", currentSessionId);
    window.history.replaceState({}, "", url);
    
    const sessTag = document.getElementById("header-session-tag");
    const sessId = document.getElementById("header-session-id");
    if (sessTag && sessId) {
      sessTag.hidden = false;
      sessId.textContent = currentSessionId.substring(0, 10);
    }
  }

  // Switch views: Hide intake form, display full production desk!
  pitchDesk.hidden = true;
  board.hidden = false;
  
  if (s.steps && s.steps.length) {
    ticker.innerHTML = s.steps.map((x) => `<li>✓ ${x}</li>`).join("");
  }

  // Story Details
  document.getElementById("story-title").textContent = s.title || "Untitled Lot";
  document.getElementById("story-logline").textContent = s.logline || s.seed || "";
  document.getElementById("story-genre").textContent = s.genre || "Regional Family Drama";
  document.getElementById("story-cycle").textContent = `Cycle ${s.cycle || 0}/${s.max_cycles || 4}`;
  
  const factEl = document.getElementById("story-fact");
  const factBox = document.getElementById("owned-fact-display");
  if (s.owned_fact) {
    factBox.hidden = false;
    factEl.textContent = `Owned Fact: "${s.owned_fact}"`;
  } else {
    factBox.hidden = true;
  }

  // Dialect and Monetization indicators
  const dialectEl = document.getElementById("story-dialect");
  if (dialectEl) {
    dialectEl.textContent = `Dialect: ${s.dialect_verdict || 'High Texture'}`;
  }
  const monEl = document.getElementById("story-monetization");
  if (monEl) {
    monEl.textContent = `Monetization: ${s.dark_pattern_risk || 'Low / Safe'}`;
  }

  // Engine status
  const provEl = document.getElementById("story-provenance");
  const isGeminiLive = s.engines?.gemini === "google-genai" || s.engines?.gemini === "google-genai-rewrite";
  const isParallelLive = s.engines?.parallel === "parallel-web.search";
  provEl.textContent = `${isGeminiLive ? 'Gemini 2.5: Live' : 'Deterministic Script'} · ${isParallelLive ? 'Parallel: Live' : 'Offline Trends'}`;

  // STATUS & VERDICT PILL
  const verdictPill = document.getElementById("verdict-pill");
  const verdictLabel = document.getElementById("verdict-label");
  const verdictDot = document.getElementById("verdict-dot");
  const verdictSubtext = document.getElementById("verdict-subtext");

  if (s.status === "graduate") {
    verdictPill.style.borderColor = "var(--emerald-border)";
    verdictPill.style.background = "var(--emerald-soft)";
    verdictPill.style.boxShadow = "0 0 16px var(--emerald-glow)";
    verdictDot.style.background = "var(--emerald)";
    verdictDot.style.boxShadow = "0 0 8px var(--emerald)";
    verdictLabel.style.color = "var(--emerald-light)";
    verdictLabel.textContent = "GRADUATE TO AUDIO PRODUCTION";
    verdictSubtext.textContent = s.verdict || "Canary cleared hit bar. Approved for full audio production.";
  } else if (s.status === "archive") {
    verdictPill.style.borderColor = "var(--slate-border)";
    verdictPill.style.background = "var(--slate-soft)";
    verdictPill.style.boxShadow = "none";
    verdictDot.style.background = "var(--slate)";
    verdictDot.style.boxShadow = "none";
    verdictLabel.style.color = "#cbd5e1";
    verdictLabel.textContent = "ARCHIVED — REWORK BRIEF GENERATED";
    verdictSubtext.textContent = s.verdict || "Story archived. Salvageable assets documented for writer room.";
  } else {
    verdictPill.style.borderColor = "var(--amber-border)";
    verdictPill.style.background = "var(--amber-soft)";
    verdictPill.style.boxShadow = "0 0 16px var(--amber-glow)";
    verdictDot.style.background = "var(--amber)";
    verdictDot.style.boxShadow = "0 0 8px var(--amber)";
    verdictLabel.style.color = "var(--amber-light)";
    verdictLabel.textContent = "HOLD FOR HUMAN GATE";
    verdictSubtext.textContent = s.verdict || "Twins pre-scored. 3% Canary test is strictly blocked until you click Approve.";
  }

  // REWORK BRIEF BOX
  const reworkBox = document.getElementById("rework-brief-card");
  const reworkText = document.getElementById("rework-brief-text");
  if (s.rework_brief && s.status === "archive") {
    reworkBox.hidden = false;
    reworkText.textContent = s.rework_brief;
  } else {
    reworkBox.hidden = true;
  }

  // 4 METRIC TILES
  const twins = s.twin_scores || [];
  const avgTwinScore = twins.length 
    ? Math.round(twins.reduce((acc, t) => acc + (t.score || 0), 0) / twins.length)
    : "--";
  document.getElementById("metric-twin-score").textContent = `${avgTwinScore}/100`;
  const twinTag = document.getElementById("twin-pass-tag");
  twinTag.textContent = avgTwinScore >= 60 ? "PASS" : "RISK";
  twinTag.style.color = avgTwinScore >= 60 ? "var(--emerald-light)" : "var(--rose-light)";

  const ep1 = s.episodes?.[0] || {};
  const turnMin = ep1.first_turn_minute || 5.0;
  document.getElementById("metric-first-turn").textContent = `${turnMin}m`;
  document.getElementById("expo-subtext").textContent = `Exposition: ${ep1.exposition_minutes || 1.2}m`;
  const turnTag = document.getElementById("turn-pass-tag");
  turnTag.textContent = turnMin <= 5.0 ? "ON TIME" : "LATE";
  turnTag.style.color = turnMin <= 5.0 ? "var(--emerald-light)" : "var(--rose-light)";

  const canary = s.canary || {};
  const canaryComp = document.getElementById("metric-canary-comp");
  const canaryTag = document.getElementById("canary-tag");
  const canarySub = document.getElementById("canary-bar-sub");
  const canaryWidgetDesc = document.getElementById("canary-widget-desc");
  const canaryStatsGrid = document.getElementById("canary-stats-grid");

  if (canary.ran) {
    canaryComp.textContent = `${(canary.completion * 100).toFixed(0)}%`;
    canaryTag.textContent = canary.vs_catalog?.includes("beats") ? "PASS" : "FAIL";
    canaryTag.style.color = canary.vs_catalog?.includes("beats") ? "var(--emerald-light)" : "var(--rose-light)";
    canarySub.textContent = `Hit Bar: ${(canary.catalog_bar * 100).toFixed(0)}% (${canary.vs_catalog})`;
    
    canaryWidgetDesc.textContent = `Canary test simulated on 3% opt-in cohort. Result: ${canary.vs_catalog}.`;
    canaryStatsGrid.hidden = false;
    document.getElementById("c-comp").textContent = `${(canary.completion * 100).toFixed(0)}%`;
    document.getElementById("c-next").textContent = `${(canary.next_start * 100).toFixed(0)}%`;
    document.getElementById("c-skip").textContent = `${(canary.skip_rate * 100).toFixed(0)}%`;
    document.getElementById("c-vs").textContent = canary.vs_catalog?.includes("beats") ? "Pass" : "Below";
  } else {
    canaryComp.textContent = "BLOCKED";
    canaryTag.textContent = "GATED";
    canaryTag.style.color = "var(--amber)";
    canarySub.textContent = `Hit Bar: ${(canary.catalog_bar * 100).toFixed(0)}% required`;
    canaryWidgetDesc.textContent = canary.blocked_reason || "Canary simulation is gated until human director clicks 'Approve'.";
    canaryStatsGrid.hidden = true;
  }

  const ledger = s.ledger || {};
  document.getElementById("metric-payoff").textContent = `${Math.round((ledger.ratio || 0.5) * 100)}%`;
  document.getElementById("ledger-counts").textContent = `${(ledger.paid || []).length} paid / ${(ledger.still_open || []).length} open`;
  document.getElementById("ledger-ratio").textContent = `${Math.round((ledger.ratio || 0.5) * 100)}%`;
  document.getElementById("ledger-rule").textContent = ledger.rule || "Pay one mystery. Leave one open.";

  // Dialect Metric Tile
  const dialectPct = Math.round((s.dialect_score || 0.85) * 100);
  const diaScoreEl = document.getElementById("metric-dialect-score");
  if (diaScoreEl) diaScoreEl.textContent = `${dialectPct}%`;
  const diaTag = document.getElementById("dialect-pass-tag");
  if (diaTag) {
    diaTag.textContent = dialectPct >= 75 ? "AUTHENTIC" : "FLATTENED";
    diaTag.style.color = dialectPct >= 75 ? "var(--emerald-light)" : "var(--rose-light)";
  }
  const diaSub = document.getElementById("dialect-subtext");
  if (diaSub) diaSub.textContent = s.owned_fact ? "Owned Fact Grounded" : "General Idiom";

  // DIAGNOSES LIST
  currentDiagnoses = s.diagnoses || [];
  renderDiagnoses(currentDiagnoses);

  // TWINS TABLE (TAB 1)
  renderTwinsTable(twins);

  // SCRIPT & DIFF (TAB 2)
  document.getElementById("ep1-title").textContent = `Episode 1: ${ep1.title || 'The Turn'} (${ep1.minutes || 12} mins)`;
  document.getElementById("script-formatted").innerHTML = formatScreenplay(ep1.script || "");

  const baList = s.before_after || [];
  const lastBA = baList[baList.length - 1];
  const baContainer = document.getElementById("ba-diff");
  const diffTag = document.getElementById("diff-cycle-tag");
  if (lastBA) {
    diffTag.textContent = `Cycle ${lastBA.cycle || s.cycle}`;
    baContainer.innerHTML = `
      <div style="margin-bottom:6px;font-weight:700;color:var(--amber);">DIRECTOR NOTE: "${lastBA.note}"</div>
      <div style="background:var(--rose-soft);padding:8px 10px;border-radius:4px;margin-bottom:6px;border-left:3px solid var(--rose);">
        <strong style="color:var(--rose-light);font-size:10.5px;text-transform:uppercase;">Before:</strong>
        <pre style="margin:2px 0;white-space:pre-wrap;font-size:11.5px;font-family:var(--font-mono);">${lastBA.before}</pre>
      </div>
      <div style="background:var(--emerald-soft);padding:8px 10px;border-radius:4px;border-left:3px solid var(--emerald);">
        <strong style="color:var(--emerald-light);font-size:10.5px;text-transform:uppercase;">After (Doctor Patch):</strong>
        <pre style="margin:2px 0;white-space:pre-wrap;font-size:11.5px;font-family:var(--font-mono);">${lastBA.after}</pre>
      </div>
    `;
  } else {
    diffTag.textContent = "No Patch";
    baContainer.innerHTML = `<p class="empty-state">No rewrite applied yet. Use <strong>Direct Rewrite</strong> above to patch script.</p>`;
  }

  // MONETIZATION TAGS
  const adsContainer = document.getElementById("ads-list");
  adsContainer.innerHTML = (s.monetization || []).map((m) => `
    <li>
      <strong style="color:var(--cyan);">${m.kind.toUpperCase()} @ Minute ${m.minute}m</strong>
      <div style="font-size:11.5px;color:var(--text-muted);">${m.note}</div>
    </li>
  `).join("");

  // BRANCHES (TAB 3)
  const branchesContainer = document.getElementById("branches-list");
  branchesContainer.innerHTML = (s.branch_scores || []).map((b) => `
    <div class="branch-item">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
        <strong style="font-size:13px;color:#fff;">Branch: ${b.title}</strong>
        <span class="badge-tag" style="background:var(--amber-soft);color:var(--amber);font-weight:700;">Twin Score: ${b.twin_mean}</span>
      </div>
      <p style="font-size:12px;color:var(--text-muted);">${b.note || 'Scored against 7 twins.'}</p>
    </div>
  `).join("");

  // PAYOFF LEDGER (TAB 4)
  const ledgerThreads = document.getElementById("ledger-threads");
  const paid = ledger.paid || [];
  const openThreads = ledger.still_open || (s.memory?.open_threads || []);
  ledgerThreads.innerHTML = `
    <ul class="clean-tags-list">
      ${paid.map(p => `<li><span class="badge-tag" style="background:var(--emerald-soft);color:var(--emerald-light);">PAID</span> ${p}</li>`).join("")}
      ${openThreads.map(o => `<li><span class="badge-tag" style="background:var(--amber-soft);color:var(--amber);">OPEN</span> ${o}</li>`).join("")}
    </ul>
  `;

  const origContainer = document.getElementById("orig-list");
  origContainer.innerHTML = (s.originality || []).map((o) => `
    <li>
      <div style="display:flex;justify-content:space-between;">
        <strong style="color:${o.severity === 'block' ? 'var(--rose-light)' : '#fff'};">${o.title}</strong>
        <span class="badge-tag" style="font-size:9px;">${o.severity.toUpperCase()}</span>
      </div>
      <div style="font-size:11.5px;color:var(--text-muted);margin-top:1px;">${o.reason}</div>
    </li>
  `).join("") || "<li>No catalog near-duplicates flagged.</li>";

  // TRENDS (RIGHT SIDEBAR)
  const trend = s.trend || {};
  renderMiniList("tropes-rising", trend.tropes_rising || []);
  renderMiniList("listener-pains", trend.listener_pains || []);
  document.getElementById("trend-tone-text").textContent = trend.tone || "Dialect stays in the room. Contained suspense.";

  // BOOTH & CHARACTERS (RIGHT SIDEBAR)
  const charsList = document.getElementById("characters-list");
  charsList.innerHTML = (s.characters || []).map((c) => `
    <div class="char-card-mini">
      <div style="font-weight:700;color:#fff;">${c.name} <span style="font-size:10.5px;color:var(--cyan);font-family:var(--font-mono);">[${c.voice}]</span></div>
      <div style="font-size:11px;color:var(--text-muted);margin-top:1px;"><strong>Wound:</strong> ${c.wound || 'none'}</div>
    </div>
  `).join("");

  const boothDetails = document.getElementById("booth-details");
  const booth = s.booth || {};
  boothDetails.innerHTML = `
    <p><strong>Session Fit:</strong> ${booth.session_fit || 'commute'} · <strong>Night Safe:</strong> ${booth.night_safe ? 'Yes' : 'No'}</p>
    <p><strong>Sound Design:</strong> ${booth.atmo || 'One room. Recorded dry.'}</p>
  `;

  // EXPORT PACKET URL
  const exportBtn = document.getElementById("btn-export-packet");
  if (exportBtn) exportBtn.href = `/api/packet?session_id=${encodeURIComponent(currentSessionId)}`;
}

// 11. RENDER DIAGNOSES LIST
function renderDiagnoses(dxs) {
  const dxContainer = document.getElementById("dx-list");
  const badgeCount = document.getElementById("dx-count-badge");
  
  if (!dxs || !dxs.length) {
    badgeCount.textContent = "0 Issues";
    badgeCount.style.background = "var(--emerald-soft)";
    badgeCount.style.borderColor = "var(--emerald-border)";
    badgeCount.style.color = "var(--emerald-light)";
    dxContainer.innerHTML = `<div class="dx-row dx-pass">✓ <strong>Clean Structure:</strong> No pacing stalls or late agency detected in Episode 1.</div>`;
    return;
  }

  badgeCount.textContent = `${dxs.length} Issues`;
  badgeCount.style.background = "var(--rose-soft)";
  badgeCount.style.borderColor = "var(--rose-border)";
  badgeCount.style.color = "var(--rose-light)";

  const displayList = showAllDx ? dxs : dxs.slice(0, 3);
  dxContainer.innerHTML = displayList.map((d) => `
    <div class="dx-row">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <strong style="color:var(--rose-light);">⚠️ ${d.issue.toUpperCase()}</strong>
        <span style="font-size:10px;font-family:var(--font-mono);color:var(--text-sub);">${d.evidence}</span>
      </div>
      <div style="margin-top:2px;color:#e2e8f0;font-size:11.5px;"><strong>Fix:</strong> ${d.edit_op}</div>
    </div>
  `).join("");
}

// 12. RENDER COMPACT TWINS TABLE
function renderTwinsTable(twins) {
  const tbody = document.getElementById("twins-table-body");
  if (!tbody) return;

  tbody.innerHTML = twins.map((t) => {
    const isPass = t.would_start_next || t.score >= 60;
    const barColor = isPass ? "var(--emerald)" : "var(--rose)";
    const finishBadge = t.would_finish 
      ? `<span class="badge-tag" style="background:var(--emerald-soft);color:var(--emerald-light);">Yes</span>`
      : `<span class="badge-tag" style="background:var(--rose-soft);color:var(--rose-light);">Drops @ ${t.drop_minute}m</span>`;
    const coinBadge = t.would_spend_coin 
      ? `<span style="color:var(--amber);font-weight:600;">🪙 Yes</span>`
      : `<span style="color:var(--text-sub);">🚫 No</span>`;

    return `
      <tr title="${(t.reasons || []).join(' · ')}">
        <td>
          <div style="font-weight:700;color:#fff;">${t.persona_name}</div>
          <div style="font-size:10.5px;color:var(--text-sub);">${t.cohort === 'high_retention' ? 'High Retention' : 'Skeptic / Low Retention'}</div>
        </td>
        <td>
          <div class="score-bar-wrap">
            <div class="score-bar-bg">
              <div class="score-bar-fill" style="width:${t.score}%;background:${barColor};"></div>
            </div>
            <strong style="font-family:var(--font-mono);font-size:11.5px;">${t.score}</strong>
          </div>
        </td>
        <td style="font-family:var(--font-mono);font-size:11.5px;">${t.drop_minute}m</td>
        <td>${finishBadge}</td>
        <td>${coinBadge}</td>
        <td style="font-size:11.5px;color:var(--text-muted);max-width:240px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
          "${(t.reasons || [])[0] || 'Evaluates dialogue pacing.'}"
        </td>
      </tr>
    `;
  }).join("");
}

function renderMiniList(elementId, items) {
  const el = document.getElementById(elementId);
  if (!el) return;
  el.innerHTML = items.map((x) => `<li>• ${x}</li>`).join("");
}

function formatScreenplay(scriptText) {
  if (!scriptText) return "<p class='empty-state'>No script generated yet.</p>";
  
  const lines = scriptText.split("\n");
  return lines.map((line) => {
    const trimmed = line.trim();
    if (!trimmed) return "<div style='height:6px;'></div>";
    
    if (trimmed.startsWith("SFX:")) {
      return `<div style="margin-bottom:4px;"><span class="speaker-tag speaker-sfx">SFX</span> <em>${trimmed.replace("SFX:", "").trim()}</em></div>`;
    }
    const colonIdx = trimmed.indexOf(":");
    if (colonIdx > 0 && colonIdx < 15 && !trimmed.startsWith("http")) {
      const name = trimmed.substring(0, colonIdx).trim();
      const speech = trimmed.substring(colonIdx + 1).trim();
      return `<div style="margin-bottom:4px;"><span class="speaker-tag speaker-char">${name}</span> ${speech}</div>`;
    }
    if (trimmed.includes("(memory)") || trimmed.includes("(private)")) {
      return `<div style="margin-bottom:4px;color:var(--amber);font-style:italic;">${trimmed}</div>`;
    }
    return `<div style="margin-bottom:4px;">${trimmed}</div>`;
  }).join("");
}

// 13. SPEECH DICTATION
const btnVoiceDictate = document.getElementById("btn-voice-dictate");
const voiceLabel = document.getElementById("voice-dictate-label");
if (btnVoiceDictate) {
  let recognition = null;
  let isRecording = false;
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  btnVoiceDictate.addEventListener("click", () => {
    if (!SpeechRecognition) {
      alert("Microphone speech recognition is not supported in this browser. Please type your note.");
      return;
    }

    const noteArea = document.getElementById("note");
    if (isRecording) {
      if (recognition) recognition.stop();
      isRecording = false;
      voiceLabel.textContent = "Speak Note";
    } else {
      recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.onstart = () => {
        isRecording = true;
        voiceLabel.textContent = "Listening...";
      };
      recognition.onresult = (event) => {
        let text = "";
        for (let i = 0; i < event.results.length; i++) {
          text += event.results[i][0].transcript;
        }
        noteArea.value = text;
      };
      recognition.onerror = () => {
        voiceLabel.textContent = "Speak Note";
        isRecording = false;
      };
      recognition.onend = () => {
        voiceLabel.textContent = "Speak Note";
        isRecording = false;
      };
      recognition.start();
    }
  });
}

// 14. AUTO RESTORE SESSION ON PAGE LOAD
window.addEventListener("DOMContentLoaded", () => {
  const params = new URLSearchParams(window.location.search);
  const sid = params.get("session") || localStorage.getItem("qissa_session_id");
  if (sid) {
    fetch(`/api/session?session_id=${encodeURIComponent(sid)}`)
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => {
        if (data && !data.error) {
          paint(data);
        }
      })
      .catch((e) => console.log("Session restore skipped:", e));
  }
});
