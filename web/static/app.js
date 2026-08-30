const openForm = document.getElementById("open");
const board = document.getElementById("board");
const ticker = document.getElementById("ticker");

openForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  ticker.hidden = false;
  ticker.innerHTML = "<li>Trend scout → twins → critic → gate. Canary waits.</li>";
  const res = await fetch("/api/open", { method: "POST", body: new FormData(openForm) });
  paint(await res.json());
});

document.querySelectorAll("[data-act]").forEach((btn) => {
  btn.addEventListener("click", async () => {
    const data = new FormData();
    data.set("action", btn.dataset.act);
    data.set("note", document.getElementById("note").value);
    const res = await fetch("/api/gate", { method: "POST", body: data });
    paint(await res.json());
  });
});

function paint(s) {
  if (s.error) { ticker.innerHTML += `<li>${s.error}</li>`; return; }
  board.hidden = false;
  ticker.innerHTML = (s.steps || []).map((x) => `<li>${x}</li>`).join("");
  document.getElementById("status").textContent =
    `${s.status} · ${s.verdict || "HOLD FOR HUMAN"} · cycle ${s.cycle}/${s.max_cycles} · ${s.engines?.gemini || "offline"} · ${s.engines?.parallel || "offline"}`;
  const t = s.trend || {};
  document.getElementById("trend").innerHTML =
    `<p>Rising: ${(t.tropes_rising || []).join(", ")}</p>
     <p>Saturated: ${(t.tropes_saturated || []).join(", ")}</p>
     <p>Pains: ${(t.listener_pains || []).join(" · ")}</p>
     <p>${t.tone || ""}</p>`;
  document.getElementById("bible").textContent = (s.bible || s.logline || "");
  const led = s.ledger || {};
  document.getElementById("ledger").textContent =
    `paid/open ratio ${led.ratio ?? 0} — ${led.rule || ""}`;
  document.getElementById("memory").innerHTML = [
    ...(s.memory?.events || []).map((x) => `<li>paid: ${x}</li>`),
    ...(s.memory?.open_threads || []).map((x) => `<li>open: ${x}</li>`),
  ].join("");
  document.getElementById("twins").innerHTML = (s.twin_scores || []).map((p) =>
    `<div class="chip">${p.persona_name.split(",")[0]} · ${p.score} · drop ${p.drop_minute}m · coin ${p.would_spend_coin ? "yes" : "no"}</div>`
  ).join("");
  const c = s.canary || {};
  document.getElementById("canary").textContent = c.ran
    ? `RAN 3% opt-in · completion ${c.completion} · next ${c.next_start} · coin ${c.coin_conversion} · ${c.vs_catalog} · ${c.session_fit}`
    : (c.blocked_reason || "Canary waiting on human.");
  document.getElementById("heat").innerHTML = (c.drop_timestamps || []).map((m) =>
    `<div class="chip">drop ${m}m</div>`
  ).join("");
  document.getElementById("dx").innerHTML = (s.diagnoses || []).map((d) =>
    `<li><strong>${d.issue}</strong> — ${d.edit_op}</li>`
  ).join("");
  document.getElementById("script").textContent = s.episodes?.[0]?.script || "";
  const ba = (s.before_after || [])[(s.before_after || []).length - 1];
  document.getElementById("ba").textContent = ba
    ? `NOTE: ${ba.note}\n\nBEFORE\n${ba.before}\n\nAFTER\n${ba.after}`
    : "Direct a rewrite to see the patch.";
  document.getElementById("branches").innerHTML = (s.branch_scores || []).map((b) =>
    `<div class="chip">${b.branch_id}: ${b.title} · twins ${b.twin_mean}</div>`
  ).join("");
  document.getElementById("orig").innerHTML = (s.originality || []).map((o) =>
    `<li>${o.severity}: ${o.title} — ${o.reason}</li>`
  ).join("");
  document.getElementById("ads").innerHTML = (s.monetization || []).map((m) =>
    `<li>${m.kind} @ ${m.minute}m — ${m.note}</li>`
  ).join("");
  document.getElementById("cites").innerHTML = (t.citations || []).map((h) =>
    `<li><a href="${h.url}" target="_blank" rel="noreferrer">${h.title}</a></li>`
  ).join("") || "<li>Offline fallback — add PARALLEL_API_KEY for live URLs.</li>";
}
