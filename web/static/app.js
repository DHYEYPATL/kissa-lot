// Qissa Studio — Audio Production Desk Client Controller & WebGL Voice Orb

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

let currentSessionId = "";

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
  
  if (s.steps && s.steps.length) {
    ticker.innerHTML = s.steps.map((x) => `<li>✓ ${x}</li>`).join("");
  }

  document.getElementById("story-title").textContent = s.title || "Untitled Lot";
  document.getElementById("story-logline").textContent = s.logline || s.seed || "";
  
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

  const ledgerThreads = document.getElementById("ledger-threads");
  const paid = ledger.paid || [];
  const openThreads = ledger.still_open || (s.memory?.open_threads || []);
  ledgerThreads.innerHTML = `
    <ul class="clean-list">
      ${paid.map(p => `<li><span class="badge-tag" style="background:var(--jade-soft);color:var(--jade-green);">PAID</span> ${p}</li>`).join("")}
      ${openThreads.map(o => `<li><span class="badge-tag" style="background:var(--gold-soft);color:var(--gold-dark);">OPEN</span> ${o}</li>`).join("")}
    </ul>
  `;

  const dxContainer = document.getElementById("dx-list");
  const dxs = s.diagnoses || [];
  dxContainer.innerHTML = dxs.length ? dxs.map((d) => `
    <div class="dx-item">
      <strong>⚠️ ${d.issue}</strong>
      <div style="margin-top:2px;color:var(--paper-ink);">${d.edit_op}</div>
    </div>
  `).join("") : `<div class="dx-item" style="background:var(--jade-soft);border-color:var(--jade-border);color:var(--jade-green);"><strong>✓ Clean Structure:</strong> No pacing stalls or late agency detected in Episode 1.</div>`;

  const origContainer = document.getElementById("orig-list");
  origContainer.innerHTML = (s.originality || []).map((o) => `
    <li>
      <strong>${o.title}</strong>
      <div style="font-size:12px;color:var(--paper-sub);">${o.reason}</div>
      ${o.source ? `<a href="${o.source}" target="_blank" style="font-size:11px;color:var(--terracotta);">View Source ↗</a>` : ''}
    </li>
  `).join("") || "<li>No near-duplicates found in catalog.</li>";

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

  document.getElementById("ep1-title").textContent = `Episode 1: ${ep1.title || 'The Turn'} (${ep1.minutes || 12} mins)`;
  const scriptReader = document.getElementById("script-formatted");
  scriptReader.innerHTML = formatScreenplay(ep1.script || "");

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

  const adsContainer = document.getElementById("ads-list");
  adsContainer.innerHTML = (s.monetization || []).map((m) => `
    <li>
      <strong>${m.kind.toUpperCase()} @ Minute ${m.minute}m</strong>
      <div style="font-size:12px;color:var(--paper-sub);">${m.note}</div>
    </li>
  `).join("");

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

  const bibleContent = document.getElementById("bible-content");
  bibleContent.innerHTML = `
    <div style="background:#fff;border:1px solid var(--paper-border);padding:14px;border-radius:var(--radius-sm);margin-bottom:12px;font-family:'Newsreader',serif;font-size:15px;">
      ${s.bible || s.logline || ''}
    </div>
  `;

  const charsList = document.getElementById("characters-list");
  charsList.innerHTML = (s.characters || []).map((c) => `
    <div style="background:#fff;border:1px solid var(--paper-border);padding:10px 14px;border-radius:var(--radius-sm);margin-bottom:8px;">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <div style="font-weight:700;color:var(--paper-ink);">${c.name} <span style="font-size:11px;color:var(--gold-dark);font-family:'JetBrains Mono';">(${c.voice})</span></div>
        <button type="button" class="char-audition-btn" onclick="auditionVoice('${c.name}', '${c.voice}')">
          ▶ Audition Voice
        </button>
      </div>
      <div style="font-size:12px;color:var(--paper-sub);margin-top:4px;"><strong>Wound:</strong> ${c.wound}</div>
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
    
    if (trimmed.startsWith("SFX:")) {
      return `<div class="script-dialogue-line"><span class="speaker-tag speaker-sfx">SFX</span> <em>${trimmed.replace("SFX:", "").trim()}</em></div>`;
    }
    const colonIdx = trimmed.indexOf(":");
    if (colonIdx > 0 && colonIdx < 15 && !trimmed.startsWith("http")) {
      const name = trimmed.substring(0, colonIdx).trim();
      const speech = trimmed.substring(colonIdx + 1).trim();
      return `<div class="script-dialogue-line"><span class="speaker-tag speaker-char">${name}</span> ${speech}</div>`;
    }
    if (trimmed.includes("(memory)") || trimmed.includes("(private)")) {
      return `<div class="script-dialogue-line" style="color:var(--gold-dark);font-style:italic;">${trimmed}</div>`;
    }
    return `<div class="script-dialogue-line">${trimmed}</div>`;
  }).join("");
}

// 7. VOICE AUDITION USING BROWSER SPEECH SYNTHESIS
window.auditionVoice = function(name, voiceTag) {
  if (!window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  
  const sample = `${name} speaking. The scene starts before the camera is ready.`;
  const utterance = new SpeechSynthesisUtterance(sample);
  
  if (voiceTag.includes("low") || voiceTag.includes("dry")) {
    utterance.pitch = 0.8;
    utterance.rate = 0.9;
  } else if (voiceTag.includes("bright")) {
    utterance.pitch = 1.25;
    utterance.rate = 1.1;
  } else if (voiceTag.includes("whisper")) {
    utterance.pitch = 1.0;
    utterance.rate = 0.85;
    utterance.volume = 0.6;
  } else {
    utterance.pitch = 1.0;
    utterance.rate = 1.0;
  }
  
  window.speechSynthesis.speak(utterance);
};

// 8. WEBGL VOICE POWERED ORB SHADER IMPLEMENTATION
class VoiceOrbRenderer {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.gl = this.canvas.getContext("webgl") || this.canvas.getContext("experimental-webgl");
    if (!this.gl) return;
    
    this.hue = 30.0;
    this.sensitivity = 1.8;
    this.audioLevel = 0.0;
    this.rot = 0.0;
    this.lastTime = 0;
    this.isRecording = false;

    this.initShaders();
    this.initBuffers();
    this.animate = this.animate.bind(this);
    requestAnimationFrame(this.animate);
  }

  initShaders() {
    const vsSource = `
      attribute vec2 position;
      varying vec2 vUv;
      void main() {
        vUv = (position + 1.0) * 0.5;
        gl_Position = vec4(position, 0.0, 1.0);
      }
    `;

    const fsSource = `
      precision highp float;
      uniform float iTime;
      uniform vec2 iResolution;
      uniform float hue;
      uniform float hover;
      uniform float rot;
      uniform float hoverIntensity;
      varying vec2 vUv;

      vec3 rgb2yiq(vec3 c) {
        float y = dot(c, vec3(0.299, 0.587, 0.114));
        float i = dot(c, vec3(0.596, -0.274, -0.322));
        float q = dot(c, vec3(0.211, -0.523, 0.312));
        return vec3(y, i, q);
      }

      vec3 yiq2rgb(vec3 c) {
        float r = c.x + 0.956 * c.y + 0.621 * c.z;
        float g = c.x - 0.272 * c.y - 0.647 * c.z;
        float b = c.x - 1.106 * c.y + 1.703 * c.z;
        return vec3(r, g, b);
      }

      vec3 adjustHue(vec3 color, float hueDeg) {
        float hueRad = hueDeg * 3.14159265 / 180.0;
        vec3 yiq = rgb2yiq(color);
        float cosA = cos(hueRad);
        float sinA = sin(hueRad);
        float i = yiq.y * cosA - yiq.z * sinA;
        float q = yiq.y * sinA + yiq.z * cosA;
        yiq.y = i;
        yiq.z = q;
        return yiq2rgb(yiq);
      }

      vec3 hash33(vec3 p3) {
        p3 = fract(p3 * vec3(0.1031, 0.11369, 0.13787));
        p3 += dot(p3, p3.yxz + 19.19);
        return -1.0 + 2.0 * fract(vec3(p3.x + p3.y, p3.x + p3.z, p3.y + p3.z) * p3.zyx);
      }

      float snoise3(vec3 p) {
        const float K1 = 0.333333333;
        const float K2 = 0.166666667;
        vec3 i = floor(p + (p.x + p.y + p.z) * K1);
        vec3 d0 = p - (i - (i.x + i.y + i.z) * K2);
        vec3 e = step(vec3(0.0), d0 - d0.yzx);
        vec3 i1 = e * (1.0 - e.zxy);
        vec3 i2 = 1.0 - e.zxy * (1.0 - e);
        vec3 d1 = d0 - (i1 - K2);
        vec3 d2 = d0 - (i2 - K1);
        vec3 d3 = d0 - 0.5;
        vec4 h = max(0.6 - vec4(dot(d0, d0), dot(d1, d1), dot(d2, d2), dot(d3, d3)), 0.0);
        vec4 n = h * h * h * h * vec4(dot(d0, hash33(i)), dot(d1, hash33(i + i1)), dot(d2, hash33(i + i2)), dot(d3, hash33(i + 1.0)));
        return dot(vec4(31.316), n);
      }

      const vec3 baseColor1 = vec3(0.83, 0.60, 0.22);
      const vec3 baseColor2 = vec3(0.15, 0.42, 0.27);
      const vec3 baseColor3 = vec3(0.72, 0.24, 0.16);

      void main() {
        vec2 uv = (vUv - 0.5) * 2.0;
        float angle = rot;
        float s = sin(angle);
        float c = cos(angle);
        uv = vec2(c * uv.x - s * uv.y, s * uv.x + c * uv.y);
        uv.x += hover * hoverIntensity * 0.15 * sin(uv.y * 10.0 + iTime);
        uv.y += hover * hoverIntensity * 0.15 * sin(uv.x * 10.0 + iTime);

        float len = length(uv);
        float ang = atan(uv.y, uv.x);
        float n0 = snoise3(vec3(uv * 0.65, iTime * 0.5)) * 0.5 + 0.5;
        float r0 = mix(0.6, 1.0, n0);
        float v0 = 1.0 / (1.0 + distance(uv, (r0 / max(0.01, len)) * uv) * 10.0);

        vec3 col1 = adjustHue(baseColor1, hue);
        vec3 col2 = adjustHue(baseColor2, hue);
        vec3 col3 = adjustHue(baseColor3, hue);
        vec3 col = mix(col1, col2, cos(ang + iTime * 2.0) * 0.5 + 0.5);
        col = mix(col3, col, v0);

        float v2 = smoothstep(1.0, 0.4, len);
        col *= v2;
        gl_FragColor = vec4(col, v2);
      }
    `;

    const gl = this.gl;
    const vs = gl.createShader(gl.VERTEX_SHADER);
    gl.shaderSource(vs, vsSource);
    gl.compileShader(vs);

    const fs = gl.createShader(gl.FRAGMENT_SHADER);
    gl.shaderSource(fs, fsSource);
    gl.compileShader(fs);

    this.program = gl.createProgram();
    gl.attachShader(this.program, vs);
    gl.attachShader(this.program, fs);
    gl.linkProgram(this.program);
  }

  initBuffers() {
    const gl = this.gl;
    const vertices = new Float32Array([-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1]);
    const buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);

    const posLoc = gl.getAttribLocation(this.program, "position");
    gl.enableVertexAttribArray(posLoc);
    gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0);

    this.uTime = gl.getUniformLocation(this.program, "iTime");
    this.uRes = gl.getUniformLocation(this.program, "iResolution");
    this.uHue = gl.getUniformLocation(this.program, "hue");
    this.uHover = gl.getUniformLocation(this.program, "hover");
    this.uRot = gl.getUniformLocation(this.program, "rot");
    this.uHoverInt = gl.getUniformLocation(this.program, "hoverIntensity");
  }

  animate(now) {
    if (!this.gl || !this.program) return;
    const gl = this.gl;
    const t = now * 0.001;
    const dt = t - this.lastTime;
    this.lastTime = t;

    const baseRot = 0.35;
    const speed = baseRot + this.audioLevel * this.sensitivity * 2.5;
    this.rot += dt * speed;

    gl.viewport(0, 0, this.canvas.width, this.canvas.height);
    gl.useProgram(this.program);

    gl.uniform1f(this.uTime, t);
    gl.uniform2f(this.uRes, this.canvas.width, this.canvas.height);
    gl.uniform1f(this.uHue, this.hue);
    gl.uniform1f(this.uHover, Math.min(this.audioLevel * 2.0, 1.0));
    gl.uniform1f(this.uRot, this.rot);
    gl.uniform1f(this.uHoverInt, Math.min(this.audioLevel * 0.8, 0.8));

    gl.drawArrays(gl.TRIANGLES, 0, 6);
    requestAnimationFrame(this.animate);
  }
}

// 9. AUDIO & SPEECH RECOGNITION CONTROLLER
let audioCtx = null;
let analyser = null;
let micStream = null;
let voiceOrbBooth = null;
let voiceOrbGate = null;
let recognition = null;
let isRecording = false;

function initAudioOrbEngines() {
  voiceOrbBooth = new VoiceOrbRenderer("booth-voice-orb");
  voiceOrbGate = new VoiceOrbRenderer("gate-voice-orb");

  const hueInput = document.getElementById("orb-hue");
  if (hueInput) {
    hueInput.addEventListener("input", (e) => {
      const val = parseFloat(e.target.value);
      if (voiceOrbBooth) voiceOrbBooth.hue = val;
      if (voiceOrbGate) voiceOrbGate.hue = val;
    });
  }

  const sensInput = document.getElementById("orb-sens");
  if (sensInput) {
    sensInput.addEventListener("input", (e) => {
      const val = parseFloat(e.target.value);
      if (voiceOrbBooth) voiceOrbBooth.sensitivity = val;
      if (voiceOrbGate) voiceOrbGate.sensitivity = val;
    });
  }
}

async function startMicrophone() {
  try {
    micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    analyser = audioCtx.createAnalyser();
    analyser.fftSize = 256;
    analyser.smoothingTimeConstant = 0.3;

    const source = audioCtx.createMediaStreamSource(micStream);
    source.connect(analyser);

    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    function updateAudio() {
      if (!analyser) return;
      analyser.getByteFrequencyData(dataArray);
      let sum = 0;
      for (let i = 0; i < dataArray.length; i++) {
        const norm = dataArray[i] / 255.0;
        sum += norm * norm;
      }
      const rms = Math.sqrt(sum / dataArray.length);
      const level = Math.min(rms * 2.5, 1.0);
      
      if (voiceOrbBooth) voiceOrbBooth.audioLevel = level;
      if (voiceOrbGate) voiceOrbGate.audioLevel = level;

      if (micStream) {
        requestAnimationFrame(updateAudio);
      }
    }
    updateAudio();
    return true;
  } catch (err) {
    console.warn("Microphone access denied or error:", err);
    return false;
  }
}

function stopMicrophone() {
  if (micStream) {
    micStream.getTracks().forEach((t) => t.stop());
    micStream = null;
  }
  if (audioCtx) {
    audioCtx.close();
    audioCtx = null;
  }
  if (voiceOrbBooth) voiceOrbBooth.audioLevel = 0;
  if (voiceOrbGate) voiceOrbGate.audioLevel = 0;
}

// 10. VOICE DICTATION FOR HUMAN GATE NOTE
const btnVoiceDictate = document.getElementById("btn-voice-dictate");
const dictateLabel = document.getElementById("voice-dictate-label");
const noteArea = document.getElementById("note");

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (btnVoiceDictate) {
  btnVoiceDictate.addEventListener("click", async () => {
    if (isRecording) {
      // Stop
      isRecording = false;
      btnVoiceDictate.classList.remove("recording");
      dictateLabel.textContent = "Speak Note";
      stopMicrophone();
      if (recognition) recognition.stop();
    } else {
      // Start
      const ok = await startMicrophone();
      if (!ok) {
        alert("Please enable microphone permissions in your browser to dictate notes.");
        return;
      }
      isRecording = true;
      btnVoiceDictate.classList.add("recording");
      dictateLabel.textContent = "Listening...";

      if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.onresult = (event) => {
          let text = "";
          for (let i = 0; i < event.results.length; i++) {
            text += event.results[i][0].transcript;
          }
          noteArea.value = text;
        };
        recognition.onerror = (e) => console.warn("Speech recognition error:", e);
        recognition.start();
      }
    }
  });
}

// Booth test mic button
const btnBoothMic = document.getElementById("btn-booth-mic");
const boothMicLabel = document.getElementById("booth-mic-label");
if (btnBoothMic) {
  btnBoothMic.addEventListener("click", async () => {
    if (micStream) {
      stopMicrophone();
      btnBoothMic.classList.remove("btn-danger");
      btnBoothMic.classList.add("btn-primary");
      boothMicLabel.textContent = "Test Mic Voice Pulse";
    } else {
      const ok = await startMicrophone();
      if (ok) {
        btnBoothMic.classList.remove("btn-primary");
        btnBoothMic.classList.add("btn-danger");
        boothMicLabel.textContent = "Stop Mic Stream";
      }
    }
  });
}

// Initialize WebGL Shaders on window load
window.addEventListener("DOMContentLoaded", () => {
  initAudioOrbEngines();
});
