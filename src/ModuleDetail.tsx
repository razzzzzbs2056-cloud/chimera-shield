import { useEffect } from "react";
import { BLUEPRINTS } from "./blueprint";

// ============================================
// MODULE DETAIL — full-screen overlay that
// renders the 0.01% Blueprint behind each
// Module Cluster node. Opens on module click.
// ============================================

const C = "#06EAF8";
const V = "#7B61FF";

export function ModuleDetail({
  id,
  color,
  onClose,
}: {
  id: string | null;
  color?: string;
  onClose: () => void;
}) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  if (!id) return null;
  const bp = BLUEPRINTS[id];
  if (!bp) return null;
  const accent = color || C;

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center p-6"
      onClick={onClose}
      style={{ background: "rgba(2,4,8,0.78)", backdropFilter: "blur(8px)" }}
    >
      <div
        className="relative flex max-h-[82vh] w-full max-w-2xl flex-col overflow-hidden rounded-3xl border"
        onClick={(e) => e.stopPropagation()}
        style={{
          borderColor: `${accent}30`,
          background: "linear-gradient(160deg, #0D1220 0%, #080C16 100%)",
          boxShadow: `0 0 0 1px ${accent}15, 0 30px 80px rgba(0,0,0,0.7), 0 0 60px ${accent}15`,
        }}
      >
        {/* Scan line */}
        <div
          className="scan-line pointer-events-none absolute inset-x-0 top-0 z-10 h-24"
          style={{ background: `linear-gradient(180deg, ${accent}10, transparent)` }}
        />

        {/* Header */}
        <div
          className="relative flex items-start justify-between gap-4 border-b px-7 py-5"
          style={{ borderColor: "rgba(255,255,255,0.06)" }}
        >
          <div className="flex items-start gap-4">
            <div
              className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl border font-mono text-sm font-bold"
              style={{
                borderColor: `${accent}40`,
                color: accent,
                background: `${accent}0C`,
                textShadow: `0 0 10px ${accent}`,
              }}
            >
              {bp.id}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-[8px] tracking-[0.4em] text-white/30 uppercase">
                  Module · Blueprint
                </span>
                <span
                  className="h-1 w-1 rounded-full pulse-soft"
                  style={{ background: accent, boxShadow: `0 0 4px ${accent}` }}
                />
              </div>
              <h2
                className="mt-1 text-xl font-semibold tracking-tight text-white"
                style={{ fontFamily: "Space Grotesk, Inter, sans-serif" }}
              >
                {bp.title}
              </h2>
              <p className="mt-0.5 text-[12px]" style={{ color: "rgba(232,237,248,0.45)" }}>
                {bp.tagline}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-white/10 font-mono text-sm text-white/40 transition-colors hover:border-white/30 hover:text-white"
          >
            ✕
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 space-y-5 overflow-y-auto px-7 py-6">
          {bp.sections.map((s, i) => (
            <div key={i}>
              <div className="mb-2 flex items-center gap-2">
                <span
                  className="h-3 w-0.5 rounded-full"
                  style={{ background: accent, boxShadow: `0 0 6px ${accent}` }}
                />
                <h3 className="font-mono text-[11px] font-semibold tracking-[0.15em] text-white/85 uppercase">
                  {s.heading}
                </h3>
              </div>
              {s.body && (
                <p
                  className="pl-3.5 text-[13px] leading-relaxed"
                  style={{ color: "rgba(232,237,248,0.6)" }}
                >
                  {s.body}
                </p>
              )}
              {s.bullets && (
                <ul className="space-y-1.5 pl-3.5">
                  {s.bullets.map((b, j) => (
                    <li key={j} className="flex gap-2.5 text-[13px] leading-snug">
                      <span
                        className="mt-1.5 h-1 w-1 shrink-0 rotate-45"
                        style={{ background: accent, boxShadow: `0 0 4px ${accent}` }}
                      />
                      <span style={{ color: "rgba(232,237,248,0.62)" }}>{b}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </div>

        {/* Footer */}
        <div
          className="flex items-center justify-between border-t px-7 py-3"
          style={{ borderColor: "rgba(255,255,255,0.06)", background: "rgba(0,0,0,0.3)" }}
        >
          <span className="font-mono text-[8px] tracking-[0.3em] text-white/25">
            THE 0.01% OPERATING SYSTEM
          </span>
          <span className="font-mono text-[8px] tracking-[0.3em]" style={{ color: V }}>
            ESC TO CLOSE
          </span>
        </div>
      </div>
    </div>
  );
}
