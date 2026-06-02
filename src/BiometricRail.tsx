import { useEffect, useRef, useState } from "react";

const C = "#06EAF8";
const V = "#7B61FF";
const G = "#00FF94";

type ChipProps = {
  label: string;
  value: number;
  unit: string;
  delta: string;
  deltaGood?: boolean;
  color?: string;
};

function SparkLine({ values, color }: { values: number[]; color: string }) {
  const max = Math.max(...values);
  const min = Math.min(...values);
  const range = max - min || 1;
  const W = 64, H = 18;
  const pts = values
    .map((v, i) => {
      const x = (i / (values.length - 1)) * W;
      const y = H - ((v - min) / range) * (H - 2) - 1;
      return `${x},${y}`;
    })
    .join(" ");
  return (
    <svg width={W} height={H} className="overflow-visible">
      <defs>
        <linearGradient id={`sg-${color.replace("#", "")}`} x1="0" x2="1" y1="0" y2="0">
          <stop offset="0%" stopColor={color} stopOpacity="0.3" />
          <stop offset="100%" stopColor={color} stopOpacity="1" />
        </linearGradient>
      </defs>
      <polyline
        points={pts}
        fill="none"
        stroke={`url(#sg-${color.replace("#", "")})`}
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      {(() => {
        const last = values[values.length - 1];
        const x = W;
        const y = H - ((last - min) / range) * (H - 2) - 1;
        return <circle cx={x} cy={y} r="2" fill={color} style={{ filter: `drop-shadow(0 0 3px ${color})` }} />;
      })()}
    </svg>
  );
}

function RadialChip({ label, value, unit, delta, deltaGood = true, color = C }: ChipProps) {
  const r = 22;
  const circ = 2 * Math.PI * r;
  const spark = [60, 65, 58, 72, 70, 68, value - 5, value + 2, value - 3, value];
  return (
    <div className="flex flex-col items-center gap-1">
      <div className="relative h-14 w-14">
        <svg viewBox="0 0 52 52" className="absolute inset-0 -rotate-90">
          <circle cx="26" cy="26" r={r} fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="2.5" />
          <circle
            cx="26" cy="26" r={r} fill="none"
            stroke={color} strokeWidth="2.5" strokeLinecap="round"
            strokeDasharray={circ}
            strokeDashoffset={circ * (1 - value / 100)}
            style={{ filter: `drop-shadow(0 0 5px ${color})`, transition: "stroke-dashoffset 0.8s ease" }}
          />
          <circle cx="26" cy="4" r="1.5" fill={color} opacity="0.5" />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="font-mono text-[11px] font-bold leading-none" style={{ color, textShadow: `0 0 8px ${color}` }}>
            {value}
          </span>
        </div>
      </div>
      <div className="font-mono text-[6.5px] tracking-[0.25em] text-white/30 text-center leading-tight">
        {label.toUpperCase()}
      </div>
      <SparkLine values={spark} color={color} />
      <div className="flex items-center gap-1">
        <span
          className="rounded px-1 py-0.5 font-mono text-[6.5px] tracking-widest border"
          style={{
            borderColor: `${deltaGood ? color : "#FF2D78"}30`,
            color: deltaGood ? color : "#FF2D78",
            background: `${deltaGood ? color : "#FF2D78"}08`,
          }}
        >
          {delta}
        </span>
        <span className="font-mono text-[6px] text-white/20">{unit}</span>
      </div>
    </div>
  );
}

function BrandMark() {
  return (
    <div className="relative flex h-11 w-11 items-center justify-center">
      <svg viewBox="0 0 44 44" className="absolute inset-0 spin-slow" style={{ opacity: 0.5 }}>
        <circle cx="22" cy="22" r="20" fill="none" stroke={C} strokeWidth="0.5" strokeDasharray="4 3" />
      </svg>
      <svg viewBox="0 0 44 44" className="absolute inset-0 spin-slow-rev" style={{ opacity: 0.3 }}>
        <circle cx="22" cy="22" r="14" fill="none" stroke={V} strokeWidth="0.5" strokeDasharray="2 4" />
      </svg>
      <div
        className="relative flex h-8 w-8 items-center justify-center rounded-xl"
        style={{
          background: "linear-gradient(135deg, #0D1220 0%, #0B1428 100%)",
          boxShadow: `0 0 0 1px rgba(6,234,248,0.2), 0 0 20px rgba(6,234,248,0.15), inset 0 1px 0 rgba(255,255,255,0.08)`,
        }}
      >
        <svg viewBox="0 0 24 24" className="h-4 w-4">
          <circle cx="12" cy="4" r="1.8" fill={C} style={{ filter: `drop-shadow(0 0 3px ${C})` }} />
          <circle cx="5" cy="14" r="1.5" fill="#3DB8FF" />
          <circle cx="19" cy="14" r="1.5" fill={V} />
          <circle cx="12" cy="20.5" r="1.3" fill={G} />
          <line x1="12" y1="4" x2="5" y2="14" stroke={C} strokeWidth="0.7" opacity="0.7" />
          <line x1="5" y1="14" x2="12" y2="20.5" stroke="#3DB8FF" strokeWidth="0.7" opacity="0.7" />
          <line x1="12" y1="20.5" x2="19" y2="14" stroke={G} strokeWidth="0.7" opacity="0.7" />
          <line x1="19" y1="14" x2="12" y2="4" stroke={V} strokeWidth="0.7" opacity="0.7" />
          <line x1="5" y1="14" x2="19" y2="14" stroke="rgba(255,255,255,0.15)" strokeWidth="0.5" />
          <line x1="12" y1="4" x2="12" y2="20.5" stroke="rgba(255,255,255,0.1)" strokeWidth="0.5" />
        </svg>
      </div>
    </div>
  );
}

function Divider() {
  return (
    <div className="relative mx-3 my-1">
      <div className="h-px bg-gradient-to-r from-transparent via-white/8 to-transparent" />
      <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
        <div className="h-1 w-1 rotate-45 bg-white/10" />
      </div>
    </div>
  );
}

export function BiometricRail({ fireTick }: { fireTick: number }) {
  const [now, setNow] = useState(new Date());
  const [paused, setPaused] = useState(false);
  const [secs, setSecs] = useState(54 * 60 + 12);
  const [health, setHealth] = useState(87);
  const ULTRADIAN = 90 * 60;

  useEffect(() => {
    const t = setInterval(() => {
      setNow(new Date());
      setHealth((h) => Math.max(75, Math.min(99, h + (Math.random() - 0.48) * 0.5)));
    }, 1000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    if (paused) return;
    const t = setInterval(() => setSecs((s) => (s + 1) % ULTRADIAN), 1000);
    return () => clearInterval(t);
  }, [paused]);

  const m = Math.floor(secs / 60);
  const s = secs % 60;
  const pct = (secs / ULTRADIAN) * 100;
  const phase = pct < 25 ? "WARMUP" : pct < 75 ? "DEEP·FLOW" : pct < 90 ? "PEAK" : "RECOVER";
  const phaseColor = pct < 25 ? C : pct < 75 ? G : pct < 90 ? "#FFB300" : V;

  const hR = 24;
  const hCirc = 2 * Math.PI * hR;

  return (
    <aside className="relative z-20 flex h-screen w-[96px] shrink-0 flex-col border-r border-white/5 glass-panel">
      {/* Scan line effect */}
      <div
        className="scan-line pointer-events-none absolute inset-x-0 top-0 z-50 h-16"
        style={{
          background: "linear-gradient(180deg, transparent 0%, rgba(6,234,248,0.03) 50%, transparent 100%)",
        }}
      />

      {/* Brand */}
      <div className="flex flex-col items-center gap-2 px-2 pt-5 pb-3">
        <BrandMark />
        <div className="flex flex-col items-center gap-0.5">
          <div className="font-mono text-[8px] font-bold tracking-[0.35em] flicker" style={{ color: C }}>
            R·OS
          </div>
          <div className="font-mono text-[6px] tracking-widest text-white/20">v3.1.0</div>
        </div>
        <div
          className="flex items-center gap-1 rounded-full border px-1.5 py-0.5"
          style={{ borderColor: `${G}30`, background: `${G}08` }}
        >
          <span className="h-1 w-1 rounded-full pulse-soft" style={{ background: G, boxShadow: `0 0 4px ${G}` }} />
          <span className="font-mono text-[6px] tracking-widest" style={{ color: G }}>LIVE</span>
        </div>
      </div>

      <Divider />

      {/* System Health Ring */}
      <div className="flex flex-col items-center gap-1.5 px-2 py-3">
        <div className="font-mono text-[6.5px] tracking-[0.3em] text-white/25">HEALTH</div>
        <div className="relative h-16 w-16">
          <svg viewBox="0 0 56 56" className="absolute inset-0 -rotate-90">
            <circle cx="28" cy="28" r={hR} fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="3" />
            <circle
              cx="28" cy="28" r={hR} fill="none"
              stroke={`url(#health-grad)`} strokeWidth="3" strokeLinecap="round"
              strokeDasharray={hCirc}
              strokeDashoffset={hCirc * (1 - health / 100)}
              style={{ filter: `drop-shadow(0 0 6px ${G})`, transition: "stroke-dashoffset 1s ease" }}
            />
            <defs>
              <linearGradient id="health-grad" x1="0" x2="1" y1="0" y2="0">
                <stop offset="0%" stopColor={G} />
                <stop offset="100%" stopColor={C} />
              </linearGradient>
            </defs>
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="font-mono text-[13px] font-bold leading-none" style={{ color: G, textShadow: `0 0 10px ${G}` }}>
              {Math.round(health)}
            </span>
            <span className="font-mono text-[6px] text-white/30 mt-0.5">/ 100</span>
          </div>
        </div>
      </div>

      <Divider />

      {/* Clock */}
      <div className="flex flex-col items-center gap-1 px-2 py-3">
        <div className="font-mono text-[6px] tracking-widest text-white/25">SYS·CLOCK</div>
        <div
          className="font-mono text-[12px] font-bold tracking-wider tabular-nums"
          style={{ color: C, textShadow: `0 0 10px ${C}60` }}
        >
          {now.toLocaleTimeString("en-US", { hour12: false, hour: "2-digit", minute: "2-digit" })}
        </div>
        <div className="font-mono text-[8px] font-semibold tabular-nums" style={{ color: C, opacity: 0.5 }}>
          {now.toLocaleTimeString("en-US", { hour12: false, second: "2-digit" }).split(":")[2]}<span className="blink">_</span>
        </div>
        <div className="font-mono text-[6px] tracking-widest text-white/20">
          {now.toLocaleDateString("en-US", { month: "short", day: "2-digit" }).toUpperCase()}
        </div>
      </div>

      <Divider />

      {/* Biometrics */}
      <div className="flex flex-1 flex-col gap-4 overflow-y-auto px-2 py-3">
        <div className="text-center font-mono text-[6.5px] tracking-[0.3em] text-white/25 uppercase">
          Biometrics
        </div>
        <RadialChip label="Cortex Load" value={38} unit="cu" delta="−12%" deltaGood={true} color={C} />
        <RadialChip label="HRV" value={72} unit="ms" delta="+8%" deltaGood={true} color={G} />
        <RadialChip label="SpO₂" value={98} unit="%" delta="STABLE" deltaGood={true} color={C} />
        <RadialChip label="Breath" value={64} unit="rpm" delta="−2%" deltaGood={true} color={V} />
        <RadialChip label="Readiness" value={84} unit="pts" delta="+5%" deltaGood={true} color={G} />
      </div>

      <Divider />

      {/* Ultradian */}
      <div className="flex flex-col items-center gap-1.5 px-2 py-3">
        <div className="font-mono text-[6.5px] tracking-[0.3em] text-white/25">ULTRADIAN</div>
        <div className="relative h-16 w-16">
          <svg viewBox="0 0 64 64" className="h-full w-full -rotate-90">
            <circle cx="32" cy="32" r="26" fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth="3.5" />
            <circle
              cx="32" cy="32" r="26" fill="none"
              stroke="url(#ultra)" strokeWidth="3.5" strokeLinecap="round"
              strokeDasharray={2 * Math.PI * 26}
              strokeDashoffset={2 * Math.PI * 26 * (1 - pct / 100)}
              style={{ filter: `drop-shadow(0 0 8px ${phaseColor})` }}
            />
            <defs>
              <linearGradient id="ultra" x1="0" x2="1" y1="0" y2="1">
                <stop offset="0%" stopColor={phaseColor} />
                <stop offset="100%" stopColor={V} />
              </linearGradient>
            </defs>
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-0.5">
            <div className="font-mono text-[10px] font-bold tracking-wider" style={{ color: phaseColor }}>
              {m}:{s.toString().padStart(2, "0")}
            </div>
            <div className="font-mono text-[5.5px] text-white/30">{Math.round(pct)}%</div>
          </div>
        </div>
        <div
          className="rounded border px-1.5 py-0.5 font-mono text-[6.5px] tracking-widest"
          style={{ borderColor: `${phaseColor}35`, color: phaseColor, background: `${phaseColor}08` }}
        >
          {phase}
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setPaused((p) => !p)}
            className="font-mono text-[9px] text-white/30 transition-colors hover:text-white"
          >
            {paused ? "▶" : "⏸"}
          </button>
          <button
            onClick={() => setSecs(0)}
            className="font-mono text-[9px] text-white/20 transition-colors hover:text-white/50"
          >
            ↺
          </button>
        </div>
      </div>

      <Divider />

      {/* Fire counter */}
      <div className="flex flex-col items-center gap-1 px-2 py-4">
        <div className="font-mono text-[6px] tracking-widest text-white/25">FIRES·TODAY</div>
        <div
          className="font-mono text-2xl font-black tabular-nums"
          style={{ color: C, textShadow: `0 0 16px ${C}80, 0 0 32px ${C}30` }}
        >
          {fireTick}
        </div>
        <div className="flex items-center gap-1">
          <div className="h-px w-8 bg-gradient-to-r from-transparent" style={{ backgroundImage: `linear-gradient(90deg, transparent, ${C}40)` }} />
          <div className="h-1 w-1 rotate-45" style={{ background: C, boxShadow: `0 0 4px ${C}` }} />
          <div className="h-px w-8" style={{ backgroundImage: `linear-gradient(90deg, ${C}40, transparent)` }} />
        </div>
      </div>
    </aside>
  );
}
