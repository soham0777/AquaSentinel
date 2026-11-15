/* AquaSentinel live dashboard - no libraries, works offline on the booth screen. */
"use strict";
const $ = (id) => document.getElementById(id);
const WINDOW = 600;                 // seconds kept on screen
let hist = [];                      // readings (newest last)
let S = null;                       // latest snapshot

const ICON = { LEARNING: "◌", NORMAL: "✓", ACIDIC: "⚗", INDUSTRIAL: "⚠", RUNOFF: "≋", SOLVENT: "☁", "SENSOR FAULT": "⚡" };
const WATER = {                     // river colour per state  [top, bottom]
  LEARNING: ["#1c8aa0", "#0a3c52"], NORMAL: ["#1c9aa8", "#0a4256"], INDUSTRIAL: ["#6f8796", "#2d3c47"],
  ACIDIC: ["#a7b04a", "#4b5220"], RUNOFF: ["#8a6235", "#3f2a14"], SOLVENT: ["#6f7fb0", "#2b2f55"], "SENSOR FAULT": ["#2a5a72", "#0a2a3a"] };
const BEACON = { G: "#3dff8f", R: "#ff3b4e", B: "#4aa3ff", W: "#ffffff", F: "#c17bff", Y: "#ffd34d", O: "#334", "?": "#888" };
const BEACON_NAME = { G: "GREEN", R: "RED", B: "BLUE", W: "WHITE", F: "FAULT (blinking)", Y: "YELLOW", O: "OFF", "?": "-" };

/* ---------- sensor tiles ---------- */
const TILES = [
  { k: "ph", lab: "pH", ic: "⚗", unit: "", fmt: v => v.toFixed(2),
    sub: r => `${fx(r.ph_v, 3)} V`,
    check: (r, s) => r.ph == null ? "" : (!s.ph_calibrated ? (s.state === "ACIDIC" ? "bad" : "ok") : (r.ph < 6 || r.ph > 9 ? "bad" : "ok")),
    chip: s => s.ph_calibrated ? ["calibrated", "ok"] : ["calibrate", "warn"] },
  { k: "tds", lab: "Dissolved solids", ic: "◇", unit: "ppm", fmt: v => Math.round(v),
    sub: (r, s) => s.baseline && s.baseline.tds ? `normal ≈ ${Math.round(s.baseline.tds)} ppm` : `${fx(r.tds_v, 3)} V`,
    check: r => r.tds == null ? "" : (r.tds > 1400 ? "bad" : "ok") },
  { k: "turb_v", lab: "Turbidity", ic: "≋", unit: "", fmt: (v, r) => r.turbid ? "Cloudy" : "Clear",
    sub: r => `${fx(r.turb_v, 2)} V`, check: r => r.turbid == null ? "" : (r.turbid ? "bad" : "ok") },
  { k: "t_water", lab: "Water temp", ic: "🌡", unit: "°C", fmt: v => v.toFixed(1),
    sub: () => "DS18B20 in the cage", check: r => r.t_water == null ? "bad" : "ok" },
  { k: "mq3_v", lab: "Vapour (MQ-3)", ic: "☁", unit: "", fmt: (v, r) => r.vapour ? "Detected" : "None",
    sub: r => `${fx(r.mq3_v, 2)} V`, check: r => r.vapour ? "bad" : "ok" },
  { k: "t_air", lab: "Air temp", ic: "☀", unit: "°C", fmt: v => v.toFixed(1),
    sub: () => "DHT11 on the met head", check: r => r.t_air == null ? "warn" : "ok" },
  { k: "rh", lab: "Humidity", ic: "💧", unit: "%", fmt: v => Math.round(v),
    sub: () => "relative humidity", check: r => r.rh == null ? "warn" : "ok" },
  { k: "dark", lab: "Light", ic: "◐", unit: "", fmt: (v, r) => r.dark ? "Night" : "Day",
    sub: r => r.pump ? "pump running" : "LDR on the met head", check: () => "ok" },
];
function fx(v, d) { return v == null ? "-" : Number(v).toFixed(d); }

function buildTiles() {
  $("tiles").innerHTML = TILES.map((t, i) => `
    <div class="tile" id="tile${i}">
      <div class="lab"><span>${t.lab}</span><span class="ic">${t.ic}</span></div>
      <div class="val" id="v${i}">-</div>
      <div class="sub" id="s${i}"></div>
      <canvas id="c${i}"></canvas>
    </div>`).join("");
}

/* ---------- drawing helpers ---------- */
function prep(cv) {
  const dpr = window.devicePixelRatio || 1, w = cv.clientWidth, h = cv.clientHeight;
  if (cv.width !== Math.round(w * dpr)) { cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr); }
  const c = cv.getContext("2d"); c.setTransform(dpr, 0, 0, dpr, 0, 0); c.clearRect(0, 0, w, h); return [c, w, h];
}
function spark(cv, vals, colour) {
  const [c, w, h] = prep(cv); const v = vals.filter(x => x != null);
  if (v.length < 2) return;
  let lo = Math.min(...v), hi = Math.max(...v); if (hi - lo < 1e-6) { hi += 1; lo -= 1; }
  const step = w / (vals.length - 1);
  const grad = c.createLinearGradient(0, 0, 0, h); grad.addColorStop(0, colour + "66"); grad.addColorStop(1, colour + "00");
  c.beginPath(); let started = false, lastX = 0;
  vals.forEach((x, i) => { if (x == null) return; const X = i * step, Y = h - 3 - (x - lo) / (hi - lo) * (h - 6);
    started ? c.lineTo(X, Y) : (c.moveTo(X, Y), started = true); lastX = X; });
  c.strokeStyle = colour; c.lineWidth = 2; c.stroke();
  c.lineTo(lastX, h); c.lineTo(0, h); c.closePath(); c.fillStyle = grad; c.fill();
}
function bigChart() {
  const [c, w, h] = prep($("chart")); const now = Date.now() / 1000;
  const pts = hist.filter(p => p.t > now - WINDOW); const L = 46, R = 54, T = 10, B = 24;
  c.font = "11px Segoe UI, DejaVu Sans, sans-serif"; c.fillStyle = "#7f99ad";
  // event bands
  let band = null;
  pts.forEach(p => { const x = L + (p.t - (now - WINDOW)) / WINDOW * (w - L - R); const bad = !["NORMAL", "LEARNING"].includes(p.state);
    if (bad && band == null) band = x; if (!bad && band != null) { c.fillStyle = "#ff4d5e22"; c.fillRect(band, T, x - band, h - T - B); band = null; } });
  if (band != null) { c.fillStyle = "#ff4d5e22"; c.fillRect(band, T, w - R - band, h - T - B); }
  // grid + axes
  c.strokeStyle = "#1d3a52"; c.lineWidth = 1; c.fillStyle = "#7f99ad";
  for (let i = 0; i <= 4; i++) { const y = T + i * (h - T - B) / 4; c.beginPath(); c.moveTo(L, y); c.lineTo(w - R, y); c.stroke();
    c.textAlign = "right"; c.fillText((14 - i * 3.5).toFixed(1), L - 6, y + 4); }
  const tv = pts.map(p => p.tds).filter(v => v != null); const tmax = Math.max(500, ...(tv.length ? tv : [0])) * 1.15;
  c.textAlign = "left"; for (let i = 0; i <= 4; i++) { const y = T + i * (h - T - B) / 4; c.fillText(Math.round(tmax - i * tmax / 4), w - R + 6, y + 4); }
  for (let m = 0; m <= 10; m += 2) { const x = L + (1 - m / 10) * (w - L - R); c.textAlign = "center"; c.fillText(m ? `-${m} min` : "now", x, h - 6); }
  const line = (key, scale, colour) => { c.beginPath(); let s = false;
    pts.forEach(p => { if (p[key] == null) { s = false; return; } const x = L + (p.t - (now - WINDOW)) / WINDOW * (w - L - R);
      const y = T + (1 - scale(p[key])) * (h - T - B); s ? c.lineTo(x, y) : (c.moveTo(x, y), s = true); });
    c.strokeStyle = colour; c.lineWidth = 2.2; c.stroke(); };
  line("ph", v => v / 14, "#2fd6c8"); line("tds", v => v / tmax, "#ffb547");
}

/* ---------- river scene ---------- */
const stars = $("stars"); for (let i = 0; i < 40; i++) { const s = document.createElementNS("http://www.w3.org/2000/svg", "circle");
  s.setAttribute("cx", Math.random() * 800); s.setAttribute("cy", Math.random() * 120); s.setAttribute("r", Math.random() * 1.3 + .3);
  s.setAttribute("fill", "#fff"); s.setAttribute("opacity", Math.random() * .7 + .2); stars.appendChild(s); }
const parts = $("particles"); for (let i = 0; i < 26; i++) { const p = document.createElementNS("http://www.w3.org/2000/svg", "circle");
  p.setAttribute("r", Math.random() * 2.2 + .8); p.dataset.x = Math.random() * 800; p.dataset.y = 250 + Math.random() * 100;
  p.dataset.v = Math.random() * .6 + .2; parts.appendChild(p); }
function wavePath(t, amp, base, k, phase) { let d = `M0 ${base}`;
  for (let x = 0; x <= 800; x += 20) d += ` L${x} ${base + Math.sin(x * k + t + phase) * amp + Math.sin(x * k * 2.3 + t * 1.7) * amp * .35}`;
  return d + " L800 360 L0 360 Z"; }
let riverLevel = 0;
function animate(ts) {
  const t = ts / 900, st = S ? S.state : "LEARNING", bad = !["NORMAL", "LEARNING"].includes(st);
  const lvl = 214 - riverLevel; $("wave1").setAttribute("d", wavePath(t, 5, lvl, .018, 0)); $("wave2").setAttribute("d", wavePath(t * .8, 7, lvl - 8, .013, 2));
  const bob = Math.sin(t) * 3 - riverLevel; $("float").setAttribute("transform", `translate(0 ${bob}) rotate(${Math.sin(t * .9) * 1.2} 352 200)`);
  const col = BEACON[(S && S.beacon) || "B"] || "#4aa3ff", blink = bad || (S && S.beacon === "F");
  const on = !blink || Math.floor(ts / 450) % 2 === 0;
  $("beacon").setAttribute("fill", on ? col : "#2a3440"); $("g1").setAttribute("stop-color", col); $("g2").setAttribute("stop-color", col);
  $("beacon-glow").setAttribute("opacity", on ? (bad ? 1 : .7) : .1);
  const pc = st === "RUNOFF" ? "#6b4a22" : st === "INDUSTRIAL" ? "#c9d3dc" : st === "SOLVENT" ? "#a98bff" : st === "ACIDIC" ? "#d7e86b" : "#9fe8ff";
  [...parts.children].forEach(p => { let x = +p.dataset.x + +p.dataset.v; if (x > 800) x = 0; p.dataset.x = x;
    p.setAttribute("cx", x); p.setAttribute("cy", +p.dataset.y - riverLevel + Math.sin(t + x / 60) * 3);
    p.setAttribute("fill", pc); p.setAttribute("opacity", bad ? .85 : .25); });
  requestAnimationFrame(animate);
}

/* ---------- render ---------- */
function render() {
  if (!S) return;
  document.body.dataset.state = S.state;
  $("site").textContent = S.site; $("state").textContent = S.state; $("title").textContent = S.title;
  $("explain").textContent = S.state === "LEARNING" && S.learn_left ? `${S.text} ${S.learn_left} s left.` : S.text;
  $("reasons").innerHTML = (S.reasons || []).map(r => `<li>${r}</li>`).join("");
  $("hero-icon").textContent = ICON[S.state] || "•";
  const since = new Date(S.since * 1000); $("since").textContent = "since " + since.toLocaleTimeString([], { hour12: false });
  $("beacon-label").textContent = "beacon " + (BEACON_NAME[S.beacon] || "-");
  $("samples").textContent = `${S.samples} sample${S.samples === 1 ? "" : "s"} bottled`;
  const [w1, w2] = WATER[S.state] || WATER.NORMAL; $("w1").setAttribute("stop-color", w1); $("w2").setAttribute("stop-color", w2);
  document.querySelector(".hero-ring").style.setProperty("--p", S.state === "LEARNING" ? `${100 - S.learn_left * 5}%` : "100%");

  const L = S.link; const pn = $("pill-nano"), ps = $("pill-sim");
  pn.className = "pill " + (L.nano ? "on" : "off"); pn.querySelector("span").textContent = L.simulate ? "Simulator" : (L.nano ? `Sensor hub · ${L.port}` : "Sensor hub offline");
  ps.className = "pill " + (L.sim === "ready" ? "on" : L.sim === "off" ? "" : "mid");
  ps.querySelector("span").textContent = L.sim === "ready" ? (L.operator || "SIM800L ready") : `SIM800L · ${L.sim}`;
  const bars = L.signal == null || L.signal === 99 ? 0 : Math.min(4, Math.ceil(L.signal / 8));
  [...$("bars").children].forEach((b, i) => b.classList.toggle("lit", i < bars));

  const r = S.latest || {}; const recent = hist.slice(-120);
  TILES.forEach((t, i) => {
    const v = r[t.k]; const valEl = $("v" + i);
    const shown = (v == null && !["turb_v", "mq3_v", "dark"].includes(t.k)) ? "-" : t.fmt(v ?? 0, r);
    valEl.innerHTML = `${shown}${t.unit && shown !== "-" ? `<small>${t.unit}</small>` : ""}`;
    let sub = t.sub(r, S); if (t.chip) { const [txt, cls] = t.chip(S); sub += ` <span class="chip ${cls}">${txt}</span>`; }
    $("s" + i).innerHTML = sub;
    const chk = t.check(r, S); const tile = $("tile" + i); tile.classList.toggle("alert", chk === "bad"); tile.classList.toggle("warn", chk === "warn");
    const key = t.k === "dark" ? "dark" : t.k; spark($("c" + i), recent.map(p => p[key] == null ? null : +p[key]), chk === "bad" ? "#ff4d5e" : "#2fd6c8");
  });

  const ev = S.events || [];
  $("ev-count").textContent = ev.length ? `${ev.length} today` : "none yet";
  $("events").innerHTML = ev.length ? ev.map(e => `
    <li class="${e.open ? "open" : ""}"><div class="e1"><span>${e.title}</span><span>${e.time}</span></div>
    <div class="e2">${(e.reasons || []).join(" · ")}</div>
    <div class="tags">${e.open ? '<span class="chip bad">active</span>' : `<span class="chip ok">cleared ${e.cleared || ""}</span>`}
      ${e.sample ? '<span class="chip">sample bottled</span>' : ""}<span class="chip">SMS: ${e.sms || "-"}</span></div></li>`).join("")
    : `<div class="empty">No events. The river is calm.</div>`;
  $("ticker").textContent = (S.logs || [])[0] || "";
  const u = S.uptime; $("foot-up").textContent = `up ${u > 3600 ? Math.floor(u / 3600) + " h " : ""}${Math.floor(u % 3600 / 60)} min · ${S.link.age != null ? "last reading " + S.link.age + " s ago" : ""}`;
  $("foot-team").textContent = `${S.team} · AAKRUTI 2026`;
  bigChart();
}

/* ---------- data ---------- */
async function boot() {
  buildTiles();
  try { const s = await (await fetch("/api/state")).json(); S = s; hist = s.history || []; render(); } catch (e) {}
  connect();
  requestAnimationFrame(animate);
  setInterval(() => { $("clock").textContent = new Date().toLocaleTimeString([], { hour12: false }); }, 250);
  window.addEventListener("resize", render);
}
function connect() {
  const es = new EventSource("/api/stream");
  es.onmessage = (m) => { const s = JSON.parse(m.data); const p = (s.history || [])[0];
    if (p && (!hist.length || p.t > hist[hist.length - 1].t)) hist.push(p);
    const cut = Date.now() / 1000 - WINDOW; while (hist.length && hist[0].t < cut) hist.shift();
    S = s; render(); };
  es.onerror = () => { $("pill-nano").className = "pill off"; $("pill-nano").querySelector("span").textContent = "Reconnecting…"; };
}
function toast(text) { const t = $("toast"); t.textContent = text; t.classList.add("show"); clearTimeout(toast.h); toast.h = setTimeout(() => t.classList.remove("show"), 2600); }
document.addEventListener("click", async (e) => {
  const b = e.target.closest("button[data-cmd]"); if (!b) return;
  const action = b.dataset.cmd;
  if (action === "sms_test" && !confirm("Send a test SMS to the numbers in config.json?")) return;
  const res = await (await fetch("/api/cmd", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ action }) })).json();
  toast(`${b.textContent.trim()}: ${res.result}`); $("cmd-result").textContent = res.result;
});
boot();
