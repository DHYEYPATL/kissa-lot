const form = document.getElementById("desk");
const ticker = document.getElementById("ticker");
const packetEl = document.getElementById("packet");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = document.getElementById("run");
  button.disabled = true;
  ticker.hidden = false;
  ticker.innerHTML = "<li>Opening the lot…</li>";
  packetEl.hidden = true;

  const data = new FormData(form);
  try {
    const response = await fetch("/api/develop", { method: "POST", body: data });
    if (!response.ok) throw new Error("Desk failed: " + response.status);
    const result = await response.json();
    render(result);
  } catch (err) {
    ticker.innerHTML += `<li>${err.message}</li>`;
  } finally {
    button.disabled = false;
  }
});

function render(result) {
  ticker.innerHTML = (result.steps || []).map((s) => `<li>${s}</li>`).join("");
  packetEl.hidden = false;
  const p = result.packet;
  const c = result.complexity;
  const tone = c.score >= 70 ? "tone-red" : c.score >= 40 ? "tone-amber" : "tone-green";
  document.getElementById("verdict").innerHTML = `
    <p class="meta">${result.engines.gemini} · ${result.engines.parallel} · complexity ${c.score}/100</p>
    <h2 class="${tone}">${p.greenlight_verdict}</h2>
    <p><em>${p.working_title}</em> — ${p.polished_logline}</p>
    <p class="meta">${c.verdict}</p>
  `;
  document.getElementById("desire").textContent = p.audience_desire;
  document.getElementById("whynow").textContent = p.why_now;
  fillList("clips", p.clip_moments);
  document.getElementById("complexity").textContent = (c.drivers || []).join(" ");
  fillList("cuts", c.cuts);
  document.getElementById("groups").innerHTML = (c.shooting_groups || [])
    .map((g) => `<div class="chip">${g.location} · ${g.time_of_day} · sc. ${(g.scenes || []).join(", ")}</div>`)
    .join("");
  document.getElementById("cites").innerHTML = (p.citations || result.research?.audience || [])
    .map((h) => `<li><a href="${h.url}" target="_blank" rel="noreferrer">${h.title}</a></li>`)
    .join("");
}

function fillList(id, items) {
  document.getElementById(id).innerHTML = (items || []).map((item) => `<li>${item}</li>`).join("");
}
