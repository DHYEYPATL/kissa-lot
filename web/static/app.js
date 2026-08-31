// Qissa Studio — Minimal Serialized Audio Greenlight Desk Controller

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

// 2. TOGGLE DIRECT DRAWER
const btnToggleDirect = document.getElementById("btn-toggle-direct");
const btnCloseDirect = document.getElementById("btn-close-direct");
if (btnToggleDirect) {
  btnToggleDirect.addEventListener("click", () => {
    directDrawer.hidden = !directDrawer.hidden;
    if (!directDrawer.hidden) document.getElementById("note").focus();
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

// 4. CLEAN TABS SWITCHER (3 TABS)
document.querySelectorAll(".tab-clean-btn").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab-clean-btn").forEach((t) => t.classList.remove("active"));
    document.querySelectorAll(".tab-clean-panel").forEach((p) => p.classList.remove("active"));
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
    btnToggleDx.textContent = showAllDx ? "Collapse" : "Show all";
  });
}

// 7. SUBMIT STORY FORM
openForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  setLoading(true);
  tickerWrap.hidden = false;
  ticker.innerHTML = `
    <li>• Synthesizing audience pains & audio structure...</li>
    <li>• Pre-scoring drop timestamps against 7 listener twins...</li>
    <li>• Holding at Human Gate. Canary testing blocked.</li>
  `;

  try {
    const formData = new FormData(openForm);
    if (currentSessionId) formData.set("session_id", currentSessionId);
    const res = await fetch("/api/open", { method: "POST", body: formData });
    const data = await res.json();
    paint(data);
    window.scrollTo({ top: 0, behavior: "smooth" });
  } catch (err) {
    ticker.innerHTML += `<li style="color:var(--rose);">Error: ${err.message}</li>`;
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
      alert("Gate error: " + err.message);
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
        label.textContent = "Packet";
      }, 2000);
    } catch (e) {
      alert("Copy failed: " + e.message);
    }
  });
}

function setLoading(isLoading) {
  btnRun.disabled = isLoading;
  if (btnSpin) btnSpin.hidden = !isLoading;
  btnText.textContent = isLoading ? "Analyzing Structure..." : "Run Retention Diagnostics";
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
  }

  // Display active story board
  pitchDesk.hidden = true;
  board.hidden = false;

  // 1. HERO COMMAND CENTER
  document.getElementById("story-title").textContent = s.title || "Untitled Lot";
  document.getElementById("story-genre").textContent = s.genre || "Regional Family Drama";
  document.getElementById("story-logline").textContent = s.logline || s.seed || "";
  
  const factBox = document.getElementById("owned-fact-display");
  const factEl = document.getElementById("story-fact");
  if (s.owned_fact) {
    factBox.hidden = false;
    factEl.textContent = s.owned_fact;
  } else {
    factBox.hidden = true;
  }

  // Status Badge
  const verdictPill = document.getElementById("verdict-pill");
  const verdictLabel = document.getElementById("verdict-label");
  const verdictDot = document.getElementById("verdict-dot");

  if (s.status === "graduate") {
    verdictPill.style.borderColor = "var(--emerald-border)";
    verdictPill.style.background = "var(--emerald-soft)";
    verdictPill.style.color = "var(--emerald-light)";
    verdictDot.style.background = "var(--emerald)";
    verdictDot.style.boxShadow = "0 0 6px var(--emerald)";
    verdictLabel.textContent = "GRADUATED TO AUDIO";
  } else if (s.status === "archive") {
    verdictPill.style.borderColor = "var(--slate-soft)";
    verdictPill.style.background = "var(--slate-soft)";
    verdictPill.style.color = "#cbd5e1";
    verdictDot.style.background = "var(--slate)";
    verdictDot.style.boxShadow = "none";
    verdictLabel.textContent = "ARCHIVED";
  } else {
    verdictPill.style.borderColor = "var(--amber-border)";
    verdictPill.style.background = "var(--amber-soft)";
    verdictPill.style.color = "var(--amber-light)";
    verdictDot.style.background = "var(--amber)";
    verdictDot.style.boxShadow = "0 0 6px var(--amber)";
    verdictLabel.textContent = "HOLD FOR HUMAN GATE";
  }

  // 2. HERO METRICS STRIP (Twin 76 · Turn 4.5m · Payoff 50% · Dialect High · Dark Low)
  const twins = s.twin_scores || [];
  const avgTwinScore = twins.length 
    ? Math.round(twins.reduce((acc, t) => acc + (t.score || 0), 0) / twins.length)
    : "--";
  document.getElementById("m-twin").textContent = avgTwinScore;

  const ep1 = s.episodes?.[0] || {};
  const turnMin = ep1.first_turn_minute || 5.0;
  document.getElementById("m-turn").textContent = `${turnMin}m`;

  const canary = s.canary || {};
  const canaryEl = document.getElementById("m-canary");
  if (canary.ran) {
    canaryEl.textContent = `${(canary.completion * 100).toFixed(0)}% (${canary.vs_catalog?.includes("beats") ? "Pass" : "Below"})`;
  } else {
    canaryEl.textContent = "Blocked";
  }

  const ledger = s.ledger || {};
  document.getElementById("m-payoff").textContent = `${Math.round((ledger.ratio || 0.5) * 100)}%`;

  const dialectPct = Math.round((s.dialect_score || 0.85) * 100);
  document.getElementById("m-dialect").textContent = dialectPct >= 75 ? "High" : "Low";

  document.getElementById("m-dark").textContent = (s.dark_pattern_risk || "Low").includes("High") ? "High" : "Low";

  // Rework brief banner
  const reworkBox = document.getElementById("rework-brief-card");
  const reworkText = document.getElementById("rework-brief-text");
  if (s.rework_brief && s.status === "archive") {
    reworkBox.hidden = false;
    reworkText.textContent = s.rework_brief;
  } else {
    reworkBox.hidden = true;
  }

  // 3. TOP DIAGNOSES (SILENT & COMPACT)
  currentDiagnoses = s.diagnoses || [];
  renderDiagnoses(currentDiagnoses);

  // 4. TAB 1: TWINS TABLE & RETENTION CURVE
  renderRetentionCurve(twins, s.genre || "regional family drama");
  renderTwinsTable(twins);

  // 5. TAB 2: SCRIPT & DIFF
  document.getElementById("ep1-title").textContent = `Episode 1: ${ep1.title || 'The Turn'} (${ep1.minutes || 12} mins)`;
  document.getElementById("script-formatted").innerHTML = formatScreenplay(ep1.script || "");

  const baList = s.before_after || [];
  const lastBA = baList[baList.length - 1];
  const baContainer = document.getElementById("ba-diff");
  const diffTag = document.getElementById("diff-cycle-tag");
  if (lastBA) {
    diffTag.textContent = `Cycle ${lastBA.cycle || s.cycle}`;
    baContainer.innerHTML = `
      <div style="margin-bottom:4px;font-weight:700;color:var(--amber);">Note: "${lastBA.note}"</div>
      <pre style="background:var(--rose-soft);padding:6px;border-radius:3px;margin-bottom:4px;font-size:11px;font-family:var(--font-mono);white-space:pre-wrap;">${lastBA.before}</pre>
      <pre style="background:var(--emerald-soft);padding:6px;border-radius:3px;font-size:11px;font-family:var(--font-mono);white-space:pre-wrap;">${lastBA.after}</pre>
    `;
  } else {
    diffTag.textContent = "No Patch";
    baContainer.innerHTML = `<p class="empty-state">No rewrite applied yet. Use <strong>Direct</strong> to patch script.</p>`;
  }

  // 6. TAB 3: PRODUCTION (LEDGER, BRANCHES, BOOTH)
  const paid = ledger.paid || [];
  const openThreads = ledger.still_open || (s.memory?.open_threads || []);
  document.getElementById("ledger-ratio-line").textContent = `Ratio: ${Math.round((ledger.ratio || 0.5) * 100)}% · ${paid.length} Paid / ${openThreads.length} Open`;
  
  const ledgerThreads = document.getElementById("ledger-threads");
  ledgerThreads.innerHTML = `
    ${paid.map(p => `<div><span class="badge-tag" style="background:var(--emerald-soft);color:var(--emerald-light);">PAID</span> ${p}</div>`).join("")}
    ${openThreads.map(o => `<div><span class="badge-tag" style="background:var(--amber-soft);color:var(--amber);">OPEN</span> ${o}</div>`).join("")}
  `;

  const branchesContainer = document.getElementById("branches-list");
  branchesContainer.innerHTML = (s.branch_scores || []).map((b) => `
    <div class="branch-mini">
      <div style="display:flex;justify-content:space-between;">
        <strong>${b.title}</strong>
        <span style="color:var(--amber);font-weight:700;">Score: ${b.twin_mean}</span>
      </div>
      <p style="font-size:11px;color:var(--text-sub);">${b.note || 'Scored against 7 twins.'}</p>
    </div>
  `).join("");

  const charsList = document.getElementById("characters-list");
  charsList.innerHTML = (s.characters || []).map((c) => `
    <div><strong>${c.name}</strong> <span style="color:var(--cyan);font-family:var(--font-mono);">[${c.voice}]</span></div>
  `).join("");

  const boothDetails = document.getElementById("booth-details");
  const booth = s.booth || {};
  boothDetails.innerHTML = `
    <p>Fit: ${booth.session_fit || 'commute'} · Night Safe: ${booth.night_safe ? 'Yes' : 'No'}</p>
    <p>Atmo: ${booth.atmo || 'Recorded dry.'}</p>
  `;
}

// RENDER DIAGNOSES (SILENT & BULLETED)
function renderDiagnoses(dxs) {
  const dxContainer = document.getElementById("dx-list");
  
  if (!dxs || !dxs.length) {
    dxContainer.innerHTML = `<li class="dx-pass-line">✓ No structural pacing stalls detected.</li>`;
    return;
  }

  const displayList = showAllDx ? dxs : dxs.slice(0, 3);
  dxContainer.innerHTML = displayList.map((d) => `
    <li>
      <strong>• ${d.issue}:</strong> ${d.edit_op}
    </li>
  `).join("");
}

// RENDER RETENTION CURVE STRIP
function renderRetentionCurve(twins, genre) {
  const container = document.getElementById("curve-visual-strip");
  const hitTag = document.getElementById("curve-hit-bar-tag");
  if (!container) return;

  const hitBars = {
    "regional family drama": 0.59,
    "mythic thriller": 0.58,
    "campus dark romance": 0.67,
    "investigative noir": 0.56,
  };
  const barTarget = hitBars[genre] || 0.59;
  if (hitTag) hitTag.textContent = `Hit Bar: ${Math.round(barTarget * 100)}%`;

  const checkpoints = [
    { min: 1, label: "1m" },
    { min: 3, label: "3m" },
    { min: 5, label: "5m [Turn]" },
    { min: 7, label: "7m" },
    { min: 9, label: "9m" },
    { min: 11, label: "11m" },
    { min: 12, label: "12m [Cliff]" },
  ];

  const totalTwins = Math.max(1, twins.length);

  container.innerHTML = checkpoints.map((cp) => {
    // Twin is still listening if they finished OR if their drop minute > checkpoint minute
    const listeningCount = twins.filter((t) => t.would_finish || t.drop_minute >= cp.min).length;
    const pct = Math.round((listeningCount / totalTwins) * 100);
    const isAboveBar = (pct / 100) >= barTarget;
    const barColor = isAboveBar ? "var(--emerald)" : "var(--rose)";

    return `
      <div class="curve-col" title="${pct}% listeners active at minute ${cp.min}">
        <span class="curve-val">${pct}%</span>
        <div class="curve-bar" style="height:${pct}%;background:${barColor};"></div>
        <span class="curve-lbl">${cp.label}</span>
      </div>
    `;
  }).join("");
}

// RENDER COMPACT TWINS TABLE
function renderTwinsTable(twins) {
  const tbody = document.getElementById("twins-table-body");
  if (!tbody) return;

  tbody.innerHTML = twins.map((t) => {
    const isPass = t.would_start_next || t.score >= 60;
    const scoreColor = isPass ? "var(--emerald-light)" : "var(--rose-light)";
    const finishBadge = t.would_finish ? "Yes" : `Drops @ ${t.drop_minute}m`;
    const coinBadge = t.would_spend_coin ? "🪙 Yes" : "No";

    return `
      <tr title="${(t.reasons || []).join(' · ')}">
        <td><strong>${t.persona_name}</strong></td>
        <td><strong style="color:${scoreColor};">${t.score}</strong></td>
        <td>${t.drop_minute}m</td>
        <td>${finishBadge}</td>
        <td>${coinBadge}</td>
        <td style="color:var(--text-muted);">${(t.reasons || [])[0] || 'Evaluates dialogue.'}</td>
      </tr>
    `;
  }).join("");
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

// SPEECH DICTATION
const btnVoiceDictate = document.getElementById("btn-voice-dictate");
const voiceLabel = document.getElementById("voice-dictate-label");
if (btnVoiceDictate) {
  let recognition = null;
  let isRecording = false;
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  btnVoiceDictate.addEventListener("click", () => {
    if (!SpeechRecognition) {
      alert("Microphone speech recognition is not supported in this browser.");
      return;
    }

    const noteArea = document.getElementById("note");
    if (isRecording) {
      if (recognition) recognition.stop();
      isRecording = false;
      voiceLabel.textContent = "🎤 Speak";
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
        voiceLabel.textContent = "🎤 Speak";
        isRecording = false;
      };
      recognition.onend = () => {
        voiceLabel.textContent = "🎤 Speak";
        isRecording = false;
      };
      recognition.start();
    }
  });
}

// RESTORE SESSION ON LOAD
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
