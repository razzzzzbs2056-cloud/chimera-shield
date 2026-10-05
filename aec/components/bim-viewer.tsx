"use client";

import { Download, Loader2, RotateCw } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import type { BimModel } from "@/lib/engine/bim";
import type { BimElement } from "@/lib/engine/types";
import { api, Button, Skeleton } from "./ui";

const DISC: Record<string, { label: string; color: string }> = {
  STR: { label: "Structure", color: "#94a3b8" }, ARC: { label: "Architecture", color: "#2a78d6" }, MEC: { label: "Mechanical", color: "#eb6834" },
  ELE: { label: "Electrical", color: "#eda100" }, PLB: { label: "Plumbing", color: "#1baf7a" }, FIR: { label: "Fire", color: "#e34948" },
};

function shade(hex: string, f: number) {
  const n = parseInt(hex.slice(1), 16);
  const c = (s: number) => Math.max(0, Math.min(255, Math.round(((n >> s) & 255) * f)));
  return `rgb(${c(16)},${c(8)},${c(0)})`;
}

/** Canvas isometric renderer for the IFC element model (painter's algorithm, 4 view directions). */
export function BimViewer({ projectId, ifcHref, mode = "disciplines", progressLevel, phaseColor, height = 520 }: { projectId: string; ifcHref?: string; mode?: "disciplines" | "4d"; progressLevel?: number; phaseColor?: (e: BimElement) => string | null; height?: number }) {
  const [model, setModel] = useState<BimModel | null>(null);
  const [error, setError] = useState("");
  const [view, setView] = useState(0);
  const [on, setOn] = useState<Record<string, boolean>>({ STR: true, ARC: false, MEC: true, ELE: true, PLB: true, FIR: true });
  const [cut, setCut] = useState<number | null>(null);
  const [hover, setHover] = useState<BimElement | null>(null);
  const canvas = useRef<HTMLCanvasElement>(null);
  const hits = useRef<{ e: BimElement; poly: [number, number][] }[]>([]);

  useEffect(() => {
    api<BimModel>(`/api/projects/${projectId}/model`).then(setModel).catch((e) => setError((e as Error).message));
  }, [projectId]);

  const maxLevel = model ? Math.max(...model.elements.map((e) => e.level)) : 0;
  const level = mode === "4d" ? progressLevel ?? maxLevel : cut ?? maxLevel;

  const visible = useMemo(() => {
    if (!model) return [];
    return model.elements.filter((e) => (mode === "4d" ? e.level <= level + 1 && phaseColor?.(e) !== null : on[e.discipline] && e.level <= level));
  }, [model, on, level, mode, phaseColor]);

  useEffect(() => {
    const cv = canvas.current;
    if (!cv || !model) return;
    const dpr = window.devicePixelRatio || 1;
    const W = cv.clientWidth, H = cv.clientHeight;
    cv.width = W * dpr; cv.height = H * dpr;
    const ctx = cv.getContext("2d")!;
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, W, H);
    const B = model.bounds;
    const Lx = B.dx, Ly = B.dy;
    const rot = (x: number, y: number): [number, number] => {
      switch (view) { case 1: return [y, Lx - x]; case 2: return [Lx - x, Ly - y]; case 3: return [Ly - y, x]; default: return [x, y]; }
    };
    const c = Math.cos(Math.PI / 6), s = 0.5;
    const proj = (x: number, y: number, z: number): [number, number] => { const [a, b] = rot(x, y); return [(a - b) * c, (a + b) * s - z]; };
    const corners = [proj(B.x, B.y, 0), proj(B.x + Lx, B.y, 0), proj(B.x + Lx, B.y + Ly, 0), proj(B.x, B.y + Ly, 0), proj(B.x, B.y, B.dz), proj(B.x + Lx, B.y + Ly, B.dz)];
    const minX = Math.min(...corners.map((p) => p[0])), maxX = Math.max(...corners.map((p) => p[0]));
    const minY = Math.min(...corners.map((p) => p[1])), maxY = Math.max(...corners.map((p) => p[1]));
    const k = Math.min((W - 30) / (maxX - minX), (H - 30) / (maxY - minY));
    const ox = (W - (maxX - minX) * k) / 2 - minX * k, oy = (H - (maxY - minY) * k) / 2 - minY * k;
    const P = (x: number, y: number, z: number): [number, number] => { const [u, v] = proj(x, y, z); return [ox + u * k, oy + v * k]; };
    // ground
    ctx.fillStyle = "#f1f5f9";
    ctx.beginPath(); [P(0, 0, 0), P(Lx - 2, 0, 0), P(Lx - 2, Ly - 2, 0), P(0, Ly - 2, 0)].forEach(([x, y], i) => (i ? ctx.lineTo(x, y) : ctx.moveTo(x, y))); ctx.closePath(); ctx.fill();
    const depth = (e: BimElement) => { const [a, b] = rot(e.box.x + e.box.dx / 2, e.box.y + e.box.dy / 2); return a + b + (e.box.z + e.box.dz / 2) * 0.8; };
    const list = [...visible].sort((a, b) => depth(a) - depth(b));
    hits.current = [];
    for (const e of list) {
      const { x, y, z, dx, dy, dz } = e.box;
      // in rotated space find which original x/y faces are "front"
      const pts = (xs: number[], ys: number[], zs: number[]) => xs.map((_, i) => P(xs[i], ys[i], zs[i]));
      const xr = rot(x + dx, y)[0] + rot(x + dx, y)[1] > rot(x, y)[0] + rot(x, y)[1] ? x + dx : x; // face of x facing viewer
      const yr = rot(x, y + dy)[0] + rot(x, y + dy)[1] > rot(x, y)[0] + rot(x, y)[1] ? y + dy : y;
      const base = mode === "4d" ? phaseColor?.(e) ?? "#cbd5e1" : DISC[e.discipline].color;
      const alpha = e.discipline === "ARC" && e.ifc === "IfcPlate" ? 0.35 : e.ifc === "IfcSlab" ? 0.55 : 0.95;
      ctx.globalAlpha = alpha;
      const faces: [[number, number][], number][] = [
        [pts([xr, xr, xr, xr], [y, y + dy, y + dy, y], [z, z, z + dz, z + dz]), 0.8],
        [pts([x, x + dx, x + dx, x], [yr, yr, yr, yr], [z, z, z + dz, z + dz]), 0.65],
        [pts([x, x + dx, x + dx, x], [y, y, y + dy, y + dy], [z + dz, z + dz, z + dz, z + dz]), 1.0],
      ];
      for (const [poly, f] of faces) {
        ctx.fillStyle = shade(base, f);
        ctx.beginPath(); poly.forEach(([px, py], i) => (i ? ctx.lineTo(px, py) : ctx.moveTo(px, py))); ctx.closePath(); ctx.fill();
        if (hover?.id === e.id) { ctx.globalAlpha = 1; ctx.strokeStyle = "#0f172a"; ctx.lineWidth = 1.5; ctx.stroke(); ctx.globalAlpha = alpha; }
      }
      hits.current.push({ e, poly: faces[2][0].concat(faces[0][0]) });
    }
    ctx.globalAlpha = 1;
  }, [model, visible, view, hover, mode, phaseColor]);

  function onMove(ev: React.MouseEvent<HTMLCanvasElement>) {
    const r = ev.currentTarget.getBoundingClientRect();
    const mx = ev.clientX - r.left, my = ev.clientY - r.top;
    for (let i = hits.current.length - 1; i >= 0; i--) {
      const ps = hits.current[i].poly;
      const xs = ps.map((p) => p[0]), ys = ps.map((p) => p[1]);
      if (mx >= Math.min(...xs) && mx <= Math.max(...xs) && my >= Math.min(...ys) && my <= Math.max(...ys)) { setHover(hits.current[i].e); return; }
    }
    setHover(null);
  }

  if (error) return <div className="flex items-center justify-center rounded-xl border border-dashed border-slate-300 text-sm text-slate-500" style={{ height }}>{error}</div>;
  if (!model) return <div className="relative" style={{ height }}><Skeleton className="h-full w-full" /><Loader2 className="absolute left-1/2 top-1/2 h-5 w-5 -translate-x-1/2 animate-spin text-slate-400" /></div>;

  return (
    <div>
      <div className="mb-3 flex flex-wrap items-center gap-2">
        {mode === "disciplines" && Object.entries(DISC).map(([k, d]) => (
          <button key={k} onClick={() => setOn({ ...on, [k]: !on[k] })} aria-pressed={on[k]} className={`flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium transition ${on[k] ? "border-slate-300 bg-white text-slate-800" : "border-slate-200 bg-slate-50 text-slate-400"}`}>
            <span className="h-2.5 w-2.5 rounded-sm" style={{ background: on[k] ? d.color : "#cbd5e1" }} />{d.label}
          </button>
        ))}
        <div className="ml-auto flex items-center gap-2">
          <Button size="sm" variant="secondary" onClick={() => setView((v) => (v + 1) % 4)}><RotateCw className="h-3.5 w-3.5" />View {["SE", "SW", "NW", "NE"][view]}</Button>
          {ifcHref && <a href={ifcHref} className="inline-flex items-center gap-1.5 rounded-lg bg-brand-600 px-2.5 py-1.5 text-xs font-medium text-white hover:bg-brand-700"><Download className="h-3.5 w-3.5" />IFC4</a>}
        </div>
      </div>
      <div className="relative overflow-hidden rounded-xl bg-gradient-to-b from-slate-50 to-white ring-1 ring-slate-100">
        <canvas ref={canvas} style={{ width: "100%", height }} onMouseMove={onMove} onMouseLeave={() => setHover(null)} aria-label="3D isometric BIM model" role="img" />
        {hover && (
          <div className="pointer-events-none absolute left-3 top-3 max-w-xs rounded-lg border border-slate-200 bg-white/95 px-3 py-2 text-xs shadow">
            <div className="font-semibold text-slate-900">{hover.name}</div>
            <div className="text-slate-500">{hover.ifc} · {DISC[hover.discipline].label} · level {hover.level + 1}</div>
            <div className="num text-slate-500">{hover.box.dx.toFixed(2)} × {hover.box.dy.toFixed(2)} × {hover.box.dz.toFixed(2)} m</div>
            <div className="font-mono text-[10px] text-slate-400">{hover.id}</div>
          </div>
        )}
        <div className="absolute bottom-2 right-3 text-[11px] text-slate-400">{visible.length.toLocaleString()} of {model.elements.length.toLocaleString()} elements</div>
      </div>
      {mode === "disciplines" && (
        <label className="mt-3 block">
          <span className="label flex justify-between"><span>Section cut — show up to level</span><span className="num">{level + 1} / {maxLevel + 1}</span></span>
          <input type="range" className="w-full accent-brand-600" min={0} max={maxLevel} value={level} onChange={(e) => setCut(Number(e.target.value))} />
        </label>
      )}
    </div>
  );
}
