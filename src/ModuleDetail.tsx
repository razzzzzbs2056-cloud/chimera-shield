import { useEffect } from "react";
import { BLUEPRINTS } from "./blueprint";

// ============================================
// MODULE DETAIL — premium full-screen overlay
// rendering the 0.01% Blueprint behind each
// Module Cluster node. Opens on module click.
// ============================================

const C = "#06EAF8";
const V = "#7B61FF";
const G = "#00FF94";

export type ModuleMeta = {
  id: string;
  pct: number;
  n: number;
  status: string;
};

export function ModuleDetail({
  module,
  color,
  onClose,
}: {
  module: ModuleMeta | null;
  color?: string;
  onClose: () => void;
}) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    document.body.style.overflow = module ? "hidden" : "";
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [onClose, module]);

  if (!module) return null;
  const bp = BLUEPRINTS[module.id];
  if (!bp) return null;
  const accent = color || C;

  // Derived header metrics
  const bulletCount = bp.sections.reduce(
    (acc, s) => acc + (s.bullets?.length || (s.body ? 1 : 0)),
    0
  );
  const readMin = Math.max(1, Math.round(bulletCount * 0.4));
  const statusColor =
    module.status === "active" ? G : module.status === "idle" ? "#FFB300" : V;

  return (
    <div
      className="fade-in fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-8"
      onClick={onClose}
      style={{ background: "rgba(2,4,8,0.82)", backdropFilter: "blur(10px)" }}
    >
      <div
        className="modal-in relative flex max-h-[88vh] w-full max-w-3xl flex-col overflow-hidden rounded-[28px] border"
        onClick={(e) => e.stopPropagation()}
        style={{
          borderColor: `${accent}33`,
          background: "linear-gradient(165deg, #0E1424 0%, #070B14 55%, #05080F 100%)",
          boxShadow: `0 0 0 1px ${accent}18, 0 40px 100px rgba(0,0,0,0.75), 0 0 80px ${accent}1A`,
        }}
      >
        {/* Ambient corner glow */}
        <div
          className="pointer-events-none absolute -left-24 -top-24 h-64 w-64 rounded-full"
          style={{ background: `radial-gradient(circle, ${accent}22, transparent 70%)` }}
        />
        <div
          className="pointer-events-none absolute -bottom-24 -right-24 h-64 w-64 rounded-full"
          style={{ background: `radial-gradient(circle, ${V}1A, transparent 70%)` }}
        />

        {/* Scan line */}
        <div
          className="scan-line pointer-events-none absolute inset-x-0 top-0 z-10 h-28"
          style={{ background: `linear-gradient(180deg, ${accent}12, transparent)` }}
        />

        {/* Top accent bar */}
        <div
          className="sweep-bg h-0.5 w-full shrink-0"
          style={{
            backgroundImage: `linear-gradient(90deg, transparent, ${accent}, ${V}, ${accent}, transparent)`,
          }}
        />

        {/* ===== HEADER ===== */}
        <div className="relative px-6 pt-6 sm:px-8">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-4">
              {/* ID glyph */}
              <div className="relative h-14 w-14 shrink-0">
                <svg viewBox="0 0 56 56" className="absolute inset-0 spin-slow" style={{ opacity: 0.4 }}>
                  <circle cx="28" cy="28" r="26" fill="none" stroke={accent} strokeWidth="0.5" strokeDasharray="3 4" />
                </svg>
                <div
                  className="absolute inset-1.5 flex items-center justify-center rounded-2xl font-mono text-base font-bold"
                  style={{
                    borderColor: `${accent}40`,
                    border: `1px solid ${accent}40`,
                    color: accent,
                    background: `${accent}0E`,
                    textShadow: `0 0 12px ${accent}`,
                  }}
                >
                  {bp.id}
                </div>
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-[8px] tracking-[0.45em] text-white/30 uppercase">
                    Module · Blueprint
                  </span>
                  <span
                    className="flex items-center gap-1 rounded-full border px-1.5 py-0.5 font-mono text-[7px] tracking-widest uppercase"
                    style={{ borderColor: `${statusColor}35`, color: statusColor, background: `${statusColor}0C` }}
                  >
                    <span className="h-1 w-1 rounded-full pulse-soft" style={{ background: statusColor, boxShadow: `0 0 4px ${statusColor}` }} />
                    {module.status}
                  </span>
                </div>
                <h2
                  className="mt-1.5 text-2xl font-semibold leading-none tracking-tight"
                  style={{
                    fontFamily: "Space Grotesk, Inter, sans-serif",
                    background: `linear-gradient(90deg, #fff 30%, ${accent})`,
                    WebkitBackgroundClip: "text",
                    WebkitTextFillColor: "transparent",
                    backgroundClip: "text",
                  }}
                >
                  {bp.title}
                </h2>
                <p className="mt-1.5 max-w-md text-[12.5px] leading-snug" style={{ color: "rgba(232,237,248,0.5)" }}>
                  {bp.tagline}
                </p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-white/10 font-mono text-sm text-white/40 transition-all hover:border-white/30 hover:text-white hover:bg-white/5"
            >
              ✕
            </button>
          </div>

          {/* Stat strip */}
          <div className="mt-5 grid grid-cols-4 gap-2">
            {[
              { label: "Mastery", value: `${module.pct}%`, color: accent },
              { label: "Sections", value: String(bp.sections.length), color: V },
              { label: "Data Pts", value: module.n.toLocaleString(), color: G },
              { label: "Read", value: `${readMin}m`, color: "#FFB300" },
            ].map((stat) => (
              <div
                key={stat.label}
                className="rounded-xl border px-3 py-2"
                style={{ borderColor: "rgba(255,255,255,0.06)", background: "rgba(255,255,255,0.015)" }}
              >
                <div className="font-mono text-[7px] tracking-[0.25em] text-white/30 uppercase">{stat.label}</div>
                <div className="mt-0.5 font-mono text-base font-bold" style={{ color: stat.color, textShadow: `0 0 12px ${stat.color}40` }}>
                  {stat.value}
                </div>
              </div>
            ))}
          </div>

          {/* Mastery progress bar */}
          <div className="mt-3 flex items-center gap-3">
            <span className="font-mono text-[8px] tracking-widest text-white/30">PROGRESS</span>
            <div className="flex h-1 flex-1 overflow-hidden rounded-full" style={{ background: "rgba(255,255,255,0.05)" }}>
              <div
                className="h-full rounded-full"
                style={{
                  width: `${module.pct}%`,
                  background: `linear-gradient(90deg, ${accent}70, ${accent})`,
                  boxShadow: `0 0 8px ${accent}80`,
                }}
              />
            </div>
            <span className="font-mono text-[8px] tracking-widest" style={{ color: accent }}>{module.pct}%</span>
          </div>
        </div>

        {/* Divider */}
        <div className="mx-8 mt-5 h-px bg-gradient-to-r from-transparent via-white/8 to-transparent" />

        {/* ===== BODY ===== */}
        <div className="flex-1 space-y-3 overflow-y-auto px-6 py-5 sm:px-8">
          {bp.sections.map((s, i) => (
            <div
              key={i}
              className="reveal-up rounded-2xl border p-4"
              style={{
                borderColor: "rgba(255,255,255,0.06)",
                background: "rgba(255,255,255,0.012)",
                animationDelay: `${0.06 * i}s`,
              }}
            >
              <div className="mb-2.5 flex items-center gap-2.5">
                <span
                  className="flex h-5 w-5 shrink-0 items-center justify-center rounded-md font-mono text-[9px] font-bold"
                  style={{ color: accent, background: `${accent}12`, border: `1px solid ${accent}25` }}
                >
                  {i + 1}
                </span>
                <h3 className="font-mono text-[11px] font-semibold tracking-[0.12em] text-white/85 uppercase">
                  {s.heading}
                </h3>
              </div>
              {s.body && (
                <p className="pl-7.5 text-[13px] leading-relaxed" style={{ color: "rgba(232,237,248,0.62)", paddingLeft: "30px" }}>
                  {s.body}
                </p>
              )}
              {s.bullets && (
                <ul className="space-y-2" style={{ paddingLeft: "30px" }}>
                  {s.bullets.map((b, j) => (
                    <li key={j} className="flex gap-2.5 text-[13px] leading-snug">
                      <span
                        className="mt-[7px] h-1 w-1 shrink-0 rotate-45"
                        style={{ background: accent, boxShadow: `0 0 4px ${accent}` }}
                      />
                      <span style={{ color: "rgba(232,237,248,0.64)" }}>{b}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </div>

        {/* ===== FOOTER ===== */}
        <div
          className="flex items-center justify-between border-t px-8 py-3.5"
          style={{ borderColor: "rgba(255,255,255,0.06)", background: "rgba(0,0,0,0.35)" }}
        >
          <span className="font-mono text-[8px] tracking-[0.3em] text-white/25">
            THE 0.01% OPERATING SYSTEM
          </span>
          <div className="flex items-center gap-3">
            <span className="font-mono text-[8px] tracking-[0.3em] text-white/25">
              {bulletCount} INSIGHTS
            </span>
            <span
              className="rounded border px-2 py-1 font-mono text-[8px] tracking-[0.25em]"
              style={{ borderColor: `${V}30`, color: V, background: `${V}0A` }}
            >
              ESC TO CLOSE
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
