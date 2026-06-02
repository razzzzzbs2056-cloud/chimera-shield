import { useEffect, useState } from "react";
import { Connectome } from "./Connectome";
import { BiometricRail } from "./BiometricRail";
import { TelemetryPanel } from "./TelemetryPanel";

const C = "#06EAF8";
const V = "#7B61FF";

export default function App() {
  const [fire, setFire] = useState(0);
  const [uptime, setUptime] = useState(0);

  useEffect(() => {
    const t = setInterval(() => setFire((f) => f + 1), 6000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    const t = setInterval(() => setUptime((u) => u + 1), 1000);
    return () => clearInterval(t);
  }, []);

  const uptimeStr = `${String(Math.floor(uptime / 3600)).padStart(2, "0")}:${String(Math.floor((uptime % 3600) / 60)).padStart(2, "0")}:${String(uptime % 60).padStart(2, "0")}`;

  return (
    <div className="flex h-screen w-screen overflow-hidden text-white" style={{ background: "#020408" }}>
      {/* LEFT — biometric rail */}
      <BiometricRail fireTick={fire} />

      {/* CENTRE */}
      <main className="relative flex-1 overflow-hidden grid-bg">
        <Connectome />

        {/* Vignette overlay */}
        <div
          className="pointer-events-none absolute inset-0"
          style={{
            background: "radial-gradient(ellipse at center, transparent 30%, rgba(2,4,8,0.7) 100%)",
          }}
        />

        {/* Top strip */}
        <div className="pointer-events-none absolute inset-x-0 top-0 flex items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <div
              className="flex items-center gap-2 rounded-full border px-3 py-1.5"
              style={{ borderColor: `${C}30`, background: `${C}08`, backdropFilter: "blur(8px)" }}
            >
              <div className="h-1 w-1 rounded-full pulse-soft" style={{ background: C, boxShadow: `0 0 6px ${C}` }} />
              <span className="font-mono text-[9px] tracking-[0.35em]" style={{ color: C }}>THE CONNECTOME</span>
            </div>
            <div className="hidden sm:flex items-center gap-1.5 rounded-full border border-white/8 bg-white/[0.02] px-3 py-1.5" style={{ backdropFilter: "blur(8px)" }}>
              <span className="font-mono text-[8.5px] tracking-widest text-white/35">800 NODES</span>
              <span className="h-3 w-px bg-white/15" />
              <span className="font-mono text-[8.5px] tracking-widest text-white/35">4-OPT PROXIMITY</span>
              <span className="h-3 w-px bg-white/15" />
              <span className="font-mono text-[8.5px] tracking-widest text-white/35">BLOOM v1.4</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* Uptime */}
            <div
              className="rounded-full border px-3 py-1.5"
              style={{ borderColor: `${V}25`, background: `${V}06`, backdropFilter: "blur(8px)" }}
            >
              <span className="font-mono text-[8.5px] tracking-widest" style={{ color: V }}>
                ↑ {uptimeStr}
              </span>
            </div>
            <div
              className="rounded-full border border-white/8 bg-white/[0.02] px-3 py-1.5"
              style={{ backdropFilter: "blur(8px)" }}
            >
              <span className="font-mono text-[8.5px] tracking-widest text-white/35">DRAG · ZOOM · PAN</span>
            </div>
          </div>
        </div>

        {/* Center title */}
        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center px-6 text-center">
          <div className="max-w-3xl">
            <div className="flex items-center justify-center gap-3 mb-6">
              <div className="h-px w-16" style={{ background: `linear-gradient(90deg, transparent, ${C}60)` }} />
              <div
                className="font-mono text-[9px] tracking-[0.6em] uppercase"
                style={{ color: C, textShadow: `0 0 12px ${C}60` }}
              >
                Neural Command Interface
              </div>
              <div className="h-px w-16" style={{ background: `linear-gradient(90deg, ${C}60, transparent)` }} />
            </div>
            <h1
              className="text-[clamp(2rem,5vw,5rem)] font-semibold leading-[0.92] tracking-tight"
              style={{ fontFamily: "Space Grotesk, Inter, sans-serif" }}
            >
              Your attention,
              <br />
              <span
                style={{
                  background: `linear-gradient(90deg, ${C} 0%, #ffffff 45%, ${V} 100%)`,
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                  backgroundClip: "text",
                  filter: "drop-shadow(0 0 20px rgba(6,234,248,0.3))",
                }}
              >
                as a network
              </span>
              .
            </h1>
            <p className="mx-auto mt-6 max-w-lg text-sm leading-relaxed" style={{ color: "rgba(232,237,248,0.45)" }}>
              800 nodes. Proximity synapses. Bloom-glow rendering.
              <br />A spatial instrument for a deliberate mind.
            </p>

            {/* Status pills */}
            <div className="mt-8 flex items-center justify-center gap-3">
              {[
                { label: "WebGL2", color: C },
                { label: "Bloom 1.4", color: V },
                { label: "60fps", color: "#00FF94" },
                { label: "2 draw calls", color: "rgba(255,255,255,0.4)" },
              ].map((p) => (
                <div
                  key={p.label}
                  className="rounded-full border px-2.5 py-1"
                  style={{ borderColor: `${p.color}25`, background: `${p.color}08`, backdropFilter: "blur(4px)" }}
                >
                  <span className="font-mono text-[8px] tracking-widest" style={{ color: p.color }}>{p.label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Bottom strip */}
        <div className="pointer-events-none absolute inset-x-0 bottom-0 flex items-end justify-between gap-4 p-6">
          <div
            className="rounded-2xl border px-4 py-3"
            style={{ borderColor: `${C}20`, background: "rgba(0,0,0,0.55)", backdropFilter: "blur(12px)" }}
          >
            <div className="font-mono text-[8px] tracking-[0.4em] mb-2" style={{ color: C }}>/ CONTROLS</div>
            <div className="flex flex-col gap-0.5 font-mono text-[9px] tracking-wider text-white/60">
              <span><span style={{ color: C }}>◐</span> DRAG · rotate cluster</span>
              <span><span style={{ color: C }}>◐</span> SCROLL · zoom in / out</span>
              <span><span style={{ color: C }}>◐</span> RIGHT-DRAG · pan view</span>
              <span className="text-white/25 mt-0.5">auto-rotation · 0.12 rad/s</span>
            </div>
          </div>
          <div
            className="rounded-2xl border px-4 py-3"
            style={{ borderColor: "rgba(255,255,255,0.08)", background: "rgba(0,0,0,0.55)", backdropFilter: "blur(12px)" }}
          >
            <div className="font-mono text-[8px] tracking-[0.4em] text-white/35 mb-2">/ RENDERER</div>
            <div className="flex flex-col gap-0.5 font-mono text-[9px] tracking-wider text-white/55">
              <span>engine: <span style={{ color: C }}>WebGL2</span></span>
              <span>post-fx: <span style={{ color: V }}>Bloom 1.4</span></span>
              <span>nodes: <span style={{ color: "#00FF94" }}>800</span></span>
              <span className="text-white/25 mt-0.5">draw calls · 2</span>
            </div>
          </div>
        </div>
      </main>

      {/* RIGHT — telemetry */}
      <TelemetryPanel fires={fire} />
    </div>
  );
}
