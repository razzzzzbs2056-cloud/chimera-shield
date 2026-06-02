import { useEffect, useRef, useState } from "react";
import { ModuleDetail } from "./ModuleDetail";

const C = "#06EAF8";
const V = "#7B61FF";
const G = "#00FF94";
const A = "#FFB300";
const P = "#FF2D78";

const STREAM_EVENTS = [
  { t: "FIRE", n: "node-2417", c: C, m: "+12ms", icon: "◉" },
  { t: "MYELIN", n: "path-44", c: V, m: "peak", icon: "◈" },
  { t: "FIRE", n: "node-0182", c: C, m: "+8ms", icon: "◉" },
  { t: "PHASE", n: "α→β", c: A, m: "shift", icon: "◆" },
  { t: "FIRE", n: "node-1109", c: C, m: "+11ms", icon: "◉" },
  { t: "CLUSTER", n: "vmPFC", c: V, m: "coh+", icon: "◈" },
  { t: "FIRE", n: "node-0711", c: C, m: "+5ms", icon: "◉" },
  { t: "MYELIN", n: "path-22", c: A, m: "forming", icon: "◆" },
  { t: "FIRE", n: "node-3344", c: C, m: "+9ms", icon: "◉" },
  { t: "PHASE", n: "β→γ", c: V, m: "lock", icon: "◈" },
  { t: "ALERT", n: "cluster-7", c: P, m: "delta↑", icon: "◈" },
  { t: "FIRE", n: "node-0022", c: C, m: "+14ms", icon: "◉" },
];

const MODULES = [
  { id: "01", t: "Mental Matrix", n: 1247, c: P, pct: 78, status: "active" },
  { id: "02", t: "Syllabus", n: 892, c: C, pct: 65, status: "active" },
  { id: "03", t: "Resource Vault", n: 612, c: A, pct: 42, status: "idle" },
  { id: "04", t: "Optimized Routine", n: 2104, c: C, pct: 91, status: "active" },
  { id: "05", t: "Playbook", n: 318, c: P, pct: 55, status: "active" },
  { id: "06", t: "UX Data Matrix", n: 988, c: A, pct: 67, status: "active" },
  { id: "07", t: "Cocoa Studio", n: 142, c: P, pct: 28, status: "idle" },
  { id: "08", t: "Schedule", n: 1567, c: A, pct: 83, status: "active" },
  { id: "09", t: "Psych Framework", n: 76, c: G, pct: 19, status: "standby" },
];

const HIST = [22, 38, 28, 64, 72, 58, 46, 32, 48, 76, 88, 92, 86, 78, 64, 52, 40, 36, 28, 22, 30, 44, 58, 64];

const KPI = [
  { l: "Throughput", v: "1.2M", u: "ev/s", d: "+8.4%", good: true, pct: 72, color: C },
  { l: "Coherence", v: "0.94", u: "γ", d: "+0.06", good: true, pct: 94, color: G },
  { l: "Phase Lock", v: "78", u: "%", d: "STABLE", good: true, pct: 78, color: V },
  { l: "Cortical", v: "36.7", u: "°C", d: "+0.1°", good: false, pct: 62, color: A },
];

function PanelBlock({ title, badge, accent = C, children }: { title: string; badge?: string; accent?: string; children: React.ReactNode }) {
  return (
    <div className="rounded-2xl border overflow-hidden" style={{ borderColor: "rgba(255,255,255,0.07)", background: "rgba(13,18,32,0.7)" }}>
      <div className="flex items-center justify-between px-4 py-2.5 border-b" style={{ borderColor: "rgba(255,255,255,0.05)" }}>
        <div className="flex items-center gap-2">
          <div className="h-1 w-1 rounded-full" style={{ background: accent, boxShadow: `0 0 4px ${accent}` }} />
          <span className="font-mono text-[9px] tracking-[0.3em] text-white/60 uppercase">{title}</span>
        </div>
        {badge && (
          <span className="font-mono text-[8px] tracking-widest rounded-full border px-2 py-0.5"
            style={{ color: accent, borderColor: `${accent}30`, background: `${accent}08` }}>
            {badge}
          </span>
        )}
      </div>
      <div>{children}</div>
    </div>
  );
}

function EEGCanvas() {
  useEffect(() => {
    let raf = 0;
    const host = document.getElementById("eeg-host");
    if (!host) return;
    const c = document.createElement("canvas");
    host.appendChild(c);
    const ctx = c.getContext("2d")!;
    let offset = 0;

    const resize = () => {
      const r = host.getBoundingClientRect();
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      c.width = r.width * dpr;
      c.height = r.height * dpr;
      c.style.width = `${r.width}px`;
      c.style.height = `${r.height}px`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    resize();
    window.addEventListener("resize", resize);

    const draw = (now: number) => {
      const t = now / 1000;
      const r = host.getBoundingClientRect();
      const W = r.width, H = r.height;
      ctx.clearRect(0, 0, W, H);

      // Grid
      ctx.strokeStyle = "rgba(255,255,255,0.03)";
      ctx.lineWidth = 1;
      for (let y = 0; y < H; y += 16) {
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke();
      }
      for (let x = 0; x < W; x += 24) {
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
      }

      // Center line
      ctx.strokeStyle = "rgba(6,234,248,0.06)";
      ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(0, H / 2); ctx.lineTo(W, H / 2); ctx.stroke();

      // Main EEG wave
      const grad = ctx.createLinearGradient(0, 0, W, 0);
      grad.addColorStop(0, "rgba(6,234,248,0.3)");
      grad.addColorStop(0.5, C);
      grad.addColorStop(1, "rgba(123,97,255,0.8)");
      ctx.strokeStyle = grad;
      ctx.lineWidth = 1.8;
      ctx.shadowColor = C;
      ctx.shadowBlur = 8;
      ctx.beginPath();
      for (let x = 0; x <= W; x += 2) {
        const u = (x + offset) / 40;
        const y =
          H / 2 +
          Math.sin(u * 1.1 + t * 1.2) * 20 +
          Math.sin(u * 2.7 + t * 2.0) * 13 +
          Math.sin(u * 5.3 + t * 0.7) * 7 +
          Math.sin(u * 11 + t * 4) * 2.5;
        if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }
      ctx.stroke();
      ctx.shadowBlur = 0;

      // Secondary (violet) wave faint
      ctx.strokeStyle = "rgba(123,97,255,0.25)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      for (let x = 0; x <= W; x += 3) {
        const u = (x + offset * 0.7) / 50;
        const y =
          H / 2 +
          Math.sin(u * 1.5 + t * 0.9) * 12 +
          Math.sin(u * 3.1 + t * 1.5) * 8;
        if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }
      ctx.stroke();

      offset += 1.6;
      raf = requestAnimationFrame(draw);
    };
    raf = requestAnimationFrame(draw);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
      c.remove();
    };
  }, []);
  return <div id="eeg-host" className="h-28 w-full" />;
}

export function TelemetryPanel({ fires }: { fires: number }) {
  const [active, setActive] = useState("04");
  const [openId, setOpenId] = useState<string | null>(null);
  const [streamIdx, setStreamIdx] = useState(0);
  const [coherence, setCoherence] = useState(94);

  useEffect(() => {
    const t = setInterval(() => {
      setStreamIdx((i) => (i + 1) % STREAM_EVENTS.length);
      setCoherence((c) => Math.max(80, Math.min(99, c + (Math.random() - 0.48))));
    }, 1800);
    return () => clearInterval(t);
  }, []);

  const sortedEvents = [
    ...STREAM_EVENTS.slice(streamIdx),
    ...STREAM_EVENTS.slice(0, streamIdx),
  ];

  const openModule = MODULES.find((m) => m.id === openId);

  return (
    <>
    <aside className="relative z-20 flex h-screen w-[340px] shrink-0 flex-col border-l border-white/5 glass-panel">
      {/* Top header */}
      <div className="border-b border-white/5 px-5 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex flex-col gap-0.5">
              <div className="font-mono text-[10px] font-bold tracking-[0.3em] text-white/80 uppercase">
                Cortex · Live
              </div>
              <div className="font-mono text-[8px] tracking-widest text-white/35">
                SESSION 0x7F3A · 9 MODULES
              </div>
            </div>
          </div>
          <div className="flex flex-col items-end gap-1.5">
            <div className="flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full pulse-soft" style={{ background: G, boxShadow: `0 0 8px ${G}` }} />
              <span className="font-mono text-[9px] font-semibold tracking-widest" style={{ color: G }}>
                COHERENT {Math.round(coherence)}%
              </span>
            </div>
            <div className="flex h-1.5 w-28 overflow-hidden rounded-full" style={{ background: "rgba(255,255,255,0.04)" }}>
              <div
                className="h-full rounded-full transition-all duration-1000"
                style={{
                  width: `${coherence}%`,
                  background: `linear-gradient(90deg, ${G}, ${C})`,
                  boxShadow: `0 0 8px ${G}60`,
                }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Scrollable */}
      <div className="flex-1 space-y-3 overflow-y-auto px-4 py-4">

        {/* KPI grid */}
        <div className="grid grid-cols-2 gap-2">
          {KPI.map((k) => (
            <div
              key={k.l}
              className="rounded-xl border p-3 transition-colors"
              style={{ borderColor: `${k.color}20`, background: `${k.color}06` }}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="font-mono text-[7.5px] tracking-widest text-white/40 uppercase">{k.l}</span>
                <span
                  className="rounded px-1 py-0.5 font-mono text-[7px] tracking-widest"
                  style={{ background: `${k.color}15`, color: k.color }}
                >
                  {k.d}
                </span>
              </div>
              <div className="flex items-baseline gap-1 mb-2">
                <span className="font-mono text-lg font-bold text-white" style={{ textShadow: `0 0 16px ${k.color}40` }}>
                  {k.v}
                </span>
                <span className="font-mono text-[8px] text-white/30">{k.u}</span>
              </div>
              <div className="flex h-1 overflow-hidden rounded-full" style={{ background: "rgba(255,255,255,0.04)" }}>
                <div
                  className="h-full rounded-full"
                  style={{
                    width: `${k.pct}%`,
                    background: `linear-gradient(90deg, ${k.color}80, ${k.color})`,
                    boxShadow: `0 0 6px ${k.color}60`,
                  }}
                />
              </div>
            </div>
          ))}
        </div>

        {/* EEG */}
        <PanelBlock title="EEG · Fpz-Cz · 256 Hz" badge="LIVE" accent={C}>
          <EEGCanvas />
        </PanelBlock>

        {/* Histogram */}
        <PanelBlock title="Firing Rate · 24H" badge="Hz" accent={V}>
          <div className="flex h-20 items-end gap-0.5 p-3">
            {HIST.map((b, i) => (
              <div
                key={i}
                className="flex-1 rounded-sm cursor-pointer transition-all duration-200 hover:opacity-100"
                style={{
                  height: `${b}%`,
                  background: `linear-gradient(180deg, ${C} 0%, ${V} 100%)`,
                  boxShadow: b > 70 ? `0 0 6px ${C}60` : "none",
                  opacity: 0.35 + (b / 100) * 0.65,
                }}
              />
            ))}
          </div>
        </PanelBlock>

        {/* Event stream */}
        <PanelBlock title="Neural Event Stream" badge={`⚡ ${fires}`} accent={C}>
          <div className="max-h-44 divide-y overflow-y-auto" style={{ borderColor: "rgba(255,255,255,0.04)" }}>
            {sortedEvents.map((e, i) => (
              <div
                key={i}
                className="flex items-center gap-2.5 px-3 py-1.5 transition-colors hover:bg-white/[0.02]"
                style={{ opacity: i === 0 ? 1 : 0.5 + (1 - i / 12) * 0.5 }}
              >
                <span className="text-[8px]" style={{ color: e.c, filter: `drop-shadow(0 0 3px ${e.c})` }}>{e.icon}</span>
                <span className="w-12 font-mono text-[7.5px] tracking-widest font-semibold" style={{ color: e.c }}>{e.t}</span>
                <span className="flex-1 font-mono text-[8.5px] text-white/65">{e.n}</span>
                <span className="font-mono text-[7.5px] tracking-widest text-white/35">{e.m}</span>
              </div>
            ))}
          </div>
        </PanelBlock>

        {/* Modules */}
        <PanelBlock title="Module Cluster" badge="TAP TO OPEN" accent={V}>
          <div className="space-y-1 p-3">
            {MODULES.map((m) => {
              const isActive = active === m.id;
              const statusColor = m.status === "active" ? G : m.status === "idle" ? A : V;
              return (
                <button
                  key={m.id}
                  onClick={() => {
                    setActive(m.id);
                    setOpenId(m.id);
                  }}
                  className="group flex w-full flex-col gap-1.5 rounded-lg border p-2.5 text-left transition-all hover:border-white/20"
                  style={{
                    borderColor: isActive ? `${m.c}50` : "rgba(255,255,255,0.05)",
                    background: isActive ? `${m.c}0A` : "rgba(255,255,255,0.01)",
                  }}
                >
                  <div className="flex items-center gap-2">
                    <div className="flex items-center gap-1.5">
                      <div className="h-1 w-1 rounded-full" style={{ background: statusColor, boxShadow: `0 0 4px ${statusColor}` }} />
                      <span className="font-mono text-[8px] tracking-widest font-semibold" style={{ color: m.c }}>{m.id}</span>
                    </div>
                    <span className="flex-1 text-[10px] text-white/75 font-medium">{m.t}</span>
                    <span className="font-mono text-[7.5px] tracking-widest text-white/30 group-hover:hidden">{m.n.toLocaleString()}</span>
                    <span className="hidden font-mono text-[7.5px] tracking-widest group-hover:inline" style={{ color: m.c }}>OPEN ›</span>
                  </div>
                  <div className="flex h-0.5 overflow-hidden rounded-full w-full" style={{ background: "rgba(255,255,255,0.04)" }}>
                    <div
                      className="h-full rounded-full transition-all duration-500"
                      style={{
                        width: `${m.pct}%`,
                        background: `linear-gradient(90deg, ${m.c}60, ${m.c})`,
                        boxShadow: isActive ? `0 0 4px ${m.c}80` : "none",
                      }}
                    />
                  </div>
                </button>
              );
            })}
          </div>
        </PanelBlock>
      </div>

      {/* Bottom marquee */}
      <div className="relative overflow-hidden border-t border-white/5 py-2" style={{ background: "rgba(0,0,0,0.5)" }}>
        <div className="pointer-events-none absolute inset-y-0 left-0 w-8 z-10" style={{ background: "linear-gradient(90deg, rgba(2,4,8,0.9), transparent)" }} />
        <div className="pointer-events-none absolute inset-y-0 right-0 w-8 z-10" style={{ background: "linear-gradient(270deg, rgba(2,4,8,0.9), transparent)" }} />
        <div className="marquee-x flex w-max items-center gap-6 whitespace-nowrap font-mono text-[9px] tracking-[0.3em] text-white/40">
          {Array.from({ length: 2 }).map((_, k) => (
            <div key={k} className="flex items-center gap-6">
              {[
                "ATTENTION IS THE ONLY CURRENCY",
                "COMPOUND DAILY",
                "SHIP FAST · THINK DEEP",
                "ENERGY FIRST",
                "DESIGN THE LIFE",
                "EXECUTE WITHOUT MERCY",
                "SIGNAL OVER NOISE",
              ].map((txt) => (
                <span key={txt} className="flex items-center gap-6">
                  {txt}
                  <span className="h-1.5 w-1.5 rotate-45 inline-block" style={{ background: C, boxShadow: `0 0 6px ${C}` }} />
                </span>
              ))}
            </div>
          ))}
        </div>
      </div>
    </aside>
    <ModuleDetail id={openId} color={openModule?.c} onClose={() => setOpenId(null)} />
    </>
  );
}
