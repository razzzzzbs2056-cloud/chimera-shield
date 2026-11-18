const $ = (s, el = document) => el.querySelector(s);
const esc = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const money = (n) => "$" + Number(n || 0).toLocaleString(undefined, { maximumFractionDigits: 0 });
const time = (ts) => new Date(ts * 1000).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
const date = (ts) => ts ? new Date(ts * 1000).toLocaleDateString([], { month: "short", day: "numeric" }) : "";
const secs = (s) => `${Math.floor(s / 60)}:${String(Math.round(s % 60)).padStart(2, "0")}`;

const DEPTS = [
  ["Growth", ["research", "sales"]],
  ["Production", ["intake", "strategist", "clipper"]],
  ["Editing", ["pacing", "motion", "audio", "captioner"]],
  ["FilmCraft", ["assembler", "colorist", "finisher"]],
  ["Quality & distribution", ["quality", "publisher"]],
  ["Business", ["business"]],
];
const STAGES = [
  ["Planned", ["planned"]], ["Cutting", ["cutting", "cut"]],
  ["Editing", ["trimming", "paced", "zooming", "zoomed", "mixing", "edited"]], ["Captions", ["captioning", "captioned"]],
  ["FilmCraft", ["fc_assembling", "assembled", "grading", "graded", "fc_rendering", "finished"]],
  ["QC", ["qc"]], ["Fixing", ["needs_recut", "needs_recaption"]], ["Your approval", ["awaiting_approval"]],
  ["Publishing", ["approved", "publishing"]], ["Scheduled", ["scheduled"]], ["Stopped", ["rejected", "qc_failed"]],
];

const EDITORS = new Set(["pacing", "motion", "audio", "assembler", "colorist", "finisher"]);
const FILMCRAFT = new Set(["assembler", "colorist", "finisher"]);
let state = null;
let musicCount = 0;
let queueKey = "";

function toast(msg) {
  const t = $("#toast"); t.textContent = msg; t.classList.add("show");
  clearTimeout(toast._t); toast._t = setTimeout(() => t.classList.remove("show"), 2500);
}

async function api(path, opts = {}) {
  const init = { method: "POST", ...opts };
  if (opts.json) { init.body = JSON.stringify(opts.json); init.headers = { "Content-Type": "application/json" }; }
  const r = await fetch(path, init);
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.detail || r.statusText);
  return data;
}

function renderKpis(k) {
  const items = [
    ["Revenue collected", money(k.revenue_paid)], ["Outstanding", money(k.revenue_outstanding)],
    ["Billed (30 days)", money(k.billed_30d)], ["Active clients", k.clients], ["Orders in progress", k.orders_active],
    ["Awaiting approval", k.awaiting_approval, k.awaiting_approval > 0], ["Clips delivered", k.clips_delivered],
    ["QC first-pass", k.qc_first_pass_rate == null ? "–" : k.qc_first_pass_rate + "%"], ["Leads in pipeline", k.leads_pipeline],
  ];
  $("#kpis").innerHTML = items.map(([l, v, hot]) =>
    `<div class="kpi"><div class="label">${l}</div><div class="value ${hot ? "hot" : ""}">${esc(v)}</div></div>`).join("");
}

function renderAgents(agents) {
  const by = Object.fromEntries(agents.map((a) => [a.name, a]));
  $("#agents").innerHTML = DEPTS.map(([dept, names]) => `
    <div class="dept"><div class="dept-name">${dept}</div>
    ${names.filter((n) => by[n]).map((n) => { const a = by[n]; return `
      <div class="agent ${a.status}">
        <div class="agent-top"><span class="dot ${a.status}"></span><b>${esc(a.name)}</b><span class="hint">${a.status}</span></div>
        <div class="role">${esc(a.role)}</div>
        <div class="task" title="${esc(a.current_task)}">${esc(a.current_task || (FILMCRAFT.has(a.name) && !state.filmcraft ? "FilmCraft not installed: set FILMCRAFT_CLI" : ({ paused: "Paused by you", bypassed: "Bypassed: clips pass through unedited" }[a.status] || "Waiting for work")))}</div>
        <div class="stats"><span>${a.processed} done</span>${a.errors ? `<span style="color:var(--err)">${a.errors} errors</span>` : ""}
          <button class="btn sm" data-toggle="${esc(a.name)}">${a.enabled ? (EDITORS.has(a.name) ? "Bypass" : "Pause") : (EDITORS.has(a.name) ? "Enable" : "Resume")}</button></div>
        ${a.name === "audio" ? `<div class="stats"><span>Music library: ${musicCount} track${musicCount === 1 ? "" : "s"}</span></div>` : ""}
      </div>`; }).join("")}
    </div>`).join("");
}

function checkChips(report) {
  return (report || []).map((c) => `<span class="chk ${c.ok ? "" : c.severity === "warn" ? "warn" : "bad"}" title="${esc(c.detail)}">${c.ok ? "✓" : "✕"} ${esc(c.check.replace(/_/g, " "))}</span>`).join("");
}

function renderQueue(queue) {
  const key = queue.map((c) => c.id + ":" + c.updated_at).join(",");
  $("#queue-hint").textContent = queue.length ? `${queue.length} clip${queue.length > 1 ? "s" : ""} passed QC` : "";
  if (key === queueKey) return; // don't reset videos that are playing
  queueKey = key;
  $("#queue").innerHTML = queue.length ? queue.map((c) => `
    <div class="clip-card">
      <video src="${esc(c.video_url)}" poster="${esc(c.thumb_url)}" controls preload="none" playsinline></video>
      <div class="clip-body">
        <div class="hook">${esc(c.hook)}</div>
        <div class="meta">${esc(c.client_name || "")} · ${esc(c.order_title)} · ${secs(c.end - c.start)} · moment ${c.score}/100 · QC ${c.qc_score}/100</div>
        <div class="meta">${esc(c.reason)}</div>
        ${c.grade_url ? `<img class="grade" src="${esc(c.grade_url)}" alt="Before and after the FilmCraft colour grade" title="Before / after grade">` : ""}
        ${(c.edit_log || []).length ? `<ul class="edits">${c.edit_log.map((l) => `<li>${esc(l)}</li>`).join("")}</ul>` : ""}
        <div class="checks">${checkChips(c.qc_report)}</div>
      </div>
      <div class="clip-actions">
        <input placeholder="Note (optional)" data-note="${c.id}">
        <button class="btn ok sm" data-review="approve" data-id="${c.id}">Approve</button>
        <button class="btn sm" data-review="revise" data-id="${c.id}">New hook</button>
        <button class="btn danger sm" data-review="reject" data-id="${c.id}">Reject</button>
        <a class="btn sm" href="${esc(c.srt_url)}" download>SRT</a>
        ${c.fcproj_url ? `<a class="btn sm" href="${esc(c.fcproj_url)}" download title="The full FilmCraft project: cuts, keyframes, grade, captions and mix, all editable">FilmCraft project</a>` : ""}
        ${c.otio_url ? `<a class="btn sm" href="${esc(c.otio_url)}" download title="Timeline for FilmCraft (File ▸ Import), Resolve or any OTIO-capable editor">${c.fcproj_url ? "Timeline (.otio)" : "Edit in FilmCraft (.otio)"}</a>` : ""}
      </div>
    </div>`).join("") : `<div class="empty">Nothing to review. Clips appear here once they pass QC.</div>`;
}

function renderBoard(clips) {
  $("#board").innerHTML = STAGES.map(([label, sts]) => {
    const items = clips.filter((c) => sts.includes(c.status));
    return `<div class="col"><div class="col-head"><b>${label}</b><span>${items.length}</span></div>
      ${items.slice(0, 12).map((c) => `<div class="mini">${c.thumb_url ? `<img src="${esc(c.thumb_url)}" alt="">` : ""}
        <div><div class="t">#${c.id} ${esc(c.hook || c.title)}</div><div class="s">${esc(c.order_title)} · ${secs(c.end - c.start)}</div></div></div>`).join("")}
      ${items.length > 12 ? `<div class="hint">+${items.length - 12} more</div>` : ""}</div>`;
  }).join("");
}

function table(head, rows) {
  return `<div class="table-wrap"><table><thead><tr>${head.map((h) => `<th>${h}</th>`).join("")}</tr></thead><tbody>${rows.join("") || `<tr><td colspan="${head.length}" class="hint">Nothing yet</td></tr>`}</tbody></table></div>`;
}

function renderTabs(s) {
  $("#tab-orders").innerHTML = table(["#", "Client", "Title", "Length", "Status", "Clips", "Price", "Received"], s.orders.map((o) => `
    <tr><td>${o.id}</td><td>${esc(o.client_name)}</td><td>${esc(o.title)}${o.error ? `<div class="hint" style="color:var(--err)">${esc(o.error)}</div>` : ""}</td>
    <td>${o.duration ? secs(o.duration) : ""}</td><td><span class="status ${o.status}">${esc(o.status.replace(/_/g, " "))}</span></td>
    <td><div class="bar"><i style="width:${o.clip_total ? (100 * o.clip_done) / o.clip_total : 0}%"></i></div><span class="hint">${o.clip_done}/${o.clip_total || o.clips_requested}</span></td>
    <td>${money(o.price_cents / 100)}</td><td>${date(o.created_at)}</td></tr>`));

  $("#outreach").innerHTML = s.outreach.length ? s.outreach.map((o) => `
    <div class="email" data-oid="${o.id}">
      <div class="to">To ${esc(o.lead_name)}${o.lead_email ? ` &lt;${esc(o.lead_email)}&gt;` : ""} · ${esc(o.kind)}</div>
      <input value="${esc(o.subject)}" data-f="subject">
      <textarea rows="7" data-f="body">${esc(o.body)}</textarea>
      <div class="row-actions">
        <button class="btn sm" data-copy="${o.id}">Copy</button>
        <button class="btn ok sm" data-out="sent" data-id="${o.id}">I sent it</button>
        <button class="btn sm" data-out="save" data-id="${o.id}">Save edits</button>
        <button class="btn danger sm" data-out="discard" data-id="${o.id}">Discard</button>
      </div>
    </div>`).join("") : `<div class="hint">No drafts. The sales agent writes them for qualified leads.</div>`;

  $("#leads").innerHTML = table(["Lead", "Niche", "Followers", "Fit", "Stage", "Why", ""], s.leads.map((l) => {
    const why = l.fit_reasons ? JSON.parse(l.fit_reasons).join("; ") : "";
    return `<tr><td>${l.channel_url ? `<a href="${esc(l.channel_url)}" target="_blank" rel="noopener" style="color:inherit">${esc(l.name)}</a>` : esc(l.name)}</td>
      <td>${esc(l.niche)}</td><td>${Number(l.followers).toLocaleString()}</td><td class="score">${l.fit_score ?? "…"}</td>
      <td><span class="status ${l.stage}">${esc(l.stage.replace(/_/g, " "))}</span></td><td class="hint">${esc(why)}</td>
      <td>${["won", "lost"].includes(l.stage) ? "" : `<button class="btn ok sm" data-stage="won" data-id="${l.id}">Won</button><button class="btn sm" data-stage="lost" data-id="${l.id}">Lost</button>`}</td></tr>`;
  }));

  $("#tab-clients").innerHTML = `<h3>Clients</h3>` + table(["Name", "Email", "Package", "Orders", "Paid"], s.clients.map((c) => `
    <tr><td>${esc(c.name)}</td><td>${esc(c.email)}</td><td>${esc(c.package)}</td><td>${c.orders}</td><td>${money(c.paid_cents / 100)}</td></tr>`))
    + `<h3>Invoices</h3>` + table(["#", "Client", "Order", "Amount", "Status", "Issued", ""], s.invoices.map((i) => `
    <tr><td>${i.id}</td><td>${esc(i.client_name)}</td><td>#${i.order_id}</td><td>${money(i.amount_cents / 100)}</td>
    <td><span class="status ${i.status}">${i.status}</span></td><td>${date(i.created_at)}</td>
    <td>${i.status !== "paid" ? `<button class="btn sm" data-paid="${i.id}">Mark paid</button>` : date(i.paid_at)}</td></tr>`));

  $("#feed").innerHTML = s.events.map((e) => `<li class="${e.level}"><span class="ts">${time(e.ts)}</span><span class="who">${esc(e.agent)}</span><span class="msg">${esc(e.message)}</span></li>`).join("");
}

function fillSelects(s) {
  const sel = $("#order-client"), cur = sel.value;
  sel.innerHTML = s.clients.map((c) => `<option value="${c.id}">${esc(c.name)} (${esc(c.package)})</option>`).join("");
  if (cur) sel.value = cur;
  const lk = $("#client-look");
  if (lk.options.length <= 1) lk.innerHTML = `<option value="">Let the colorist choose</option>` + Object.entries(s.looks || {}).map(([k, v]) => `<option value="${esc(k)}">${esc(k)}: ${esc(v)}</option>`).join("");
  const pk = $("#client-package");
  if (!pk.options.length) pk.innerHTML = Object.entries(s.packages).map(([k, v]) => `<option value="${k}">${k}: ${v.clips} clips · ${money(v.price)}/video</option>`).join("");
}

async function refresh() {
  try {
    const r = await fetch("/api/dashboard");
    state = await r.json();
    const ai = $("#ai-mode");
    ai.textContent = state.ai_mode === "claude" ? `AI: ${state.model}` : "AI: heuristic mode (no API key)";
    ai.className = "pill " + (state.ai_mode === "claude" ? "claude" : "");
    musicCount = (state.music || []).length;
    renderKpis(state.kpis); renderAgents(state.agents); renderQueue(state.approval_queue);
    renderBoard(state.clips); fillSelects(state);
    // don't clobber an email draft that's being edited
    if (!document.activeElement || !document.activeElement.closest("#tab-leads, #tab-clients")) renderTabs(state);
  } catch (e) { console.error(e); }
}

document.addEventListener("click", async (ev) => {
  const t = ev.target.closest("button, [data-open]");
  if (!t) return;
  try {
    if (t.dataset.open) return $("#" + t.dataset.open).showModal();
    if (t.hasAttribute("data-close")) return t.closest("dialog").close();
    if (t.dataset.tab) {
      document.querySelectorAll("#tabs button").forEach((b) => b.classList.toggle("active", b === t));
      document.querySelectorAll(".tab").forEach((x) => x.classList.toggle("hidden", x.id !== "tab-" + t.dataset.tab));
      return;
    }
    if (t.dataset.toggle) { await api(`/api/agents/${t.dataset.toggle}/toggle`); return refresh(); }
    if (t.dataset.review) {
      const note = $(`[data-note="${t.dataset.id}"]`)?.value || "";
      await api(`/api/clips/${t.dataset.id}/review`, { json: { action: t.dataset.review, note } });
      toast({ approve: "Approved: sent to publishing", revise: "Sent back for a new hook", reject: "Rejected" }[t.dataset.review]);
      queueKey = ""; return refresh();
    }
    if (t.dataset.out) {
      const box = t.closest(".email");
      await api(`/api/outreach/${t.dataset.id}`, { json: { action: t.dataset.out, subject: $("[data-f=subject]", box).value, body: $("[data-f=body]", box).value } });
      document.activeElement.blur(); toast("Saved"); return refresh();
    }
    if (t.dataset.copy) {
      const box = t.closest(".email");
      await navigator.clipboard.writeText(`Subject: ${$("[data-f=subject]", box).value}\n\n${$("[data-f=body]", box).value}`);
      return toast("Copied to clipboard");
    }
    if (t.dataset.stage) { await api(`/api/leads/${t.dataset.id}/stage`, { json: { stage: t.dataset.stage } }); return refresh(); }
    if (t.dataset.paid) { await api(`/api/invoices/${t.dataset.paid}/paid`); toast("Invoice marked paid"); return refresh(); }
  } catch (e) { toast(e.message); }
});

$("#order-form").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const f = ev.target, fd = new FormData(f), btn = $("#order-submit");
  if (!fd.get("clips_requested")) fd.delete("clips_requested");
  if (!fd.get("transcript")?.size) fd.delete("transcript");
  btn.disabled = true; btn.textContent = "Uploading…"; $("#order-err").textContent = "";
  try { await api("/api/orders", { body: fd }); f.reset(); f.closest("dialog").close(); toast("Order received: intake agent is on it"); refresh(); }
  catch (e) { $("#order-err").textContent = e.message; }
  finally { btn.disabled = false; btn.textContent = "Upload"; }
});

$("#client-form").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const d = Object.fromEntries(new FormData(ev.target)); if (!d.look) delete d.look;
  try { await api("/api/clients", { json: d }); ev.target.reset(); ev.target.closest("dialog").close(); toast("Client added"); refresh(); }
  catch (e) { toast(e.message); }
});

$("#lead-form").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const d = Object.fromEntries(new FormData(ev.target));
  d.has_shorts = !!d.has_shorts; d.followers = +d.followers || 0; d.avg_views = +d.avg_views || 0; d.uploads_per_week = +d.uploads_per_week || 0;
  try { await api("/api/leads", { json: d }); ev.target.reset(); ev.target.closest("dialog").close(); toast("Lead added: research agent will score it"); refresh(); }
  catch (e) { toast(e.message); }
});

$("#lead-csv").addEventListener("change", async (ev) => {
  const fd = new FormData(); fd.append("file", ev.target.files[0]);
  try { const r = await api("/api/leads/import", { body: fd }); toast(`Imported ${r.imported} leads`); refresh(); }
  catch (e) { toast(e.message); }
  ev.target.value = "";
});

$("#discover").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  try { const r = await api("/api/leads/discover", { json: { query: ev.target.query.value } }); toast(`Found ${r.created} new channels`); refresh(); }
  catch (e) { toast(e.message); }
});

document.addEventListener("change", async (ev) => {
  if (ev.target.id !== "music-file" || !ev.target.files[0]) return;
  const fd = new FormData(); fd.append("file", ev.target.files[0]);
  try { const r = await api("/api/music", { body: fd }); toast(`Added ${r.name} to the music library`); refresh(); }
  catch (e) { toast(e.message); }
});

refresh();
setInterval(refresh, 2000);
