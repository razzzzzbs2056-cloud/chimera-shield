"use client";

// Engineering-specific charts that need multiple data sets on a numeric axis.

import { CartesianGrid, Legend, Line, LineChart, ReferenceDot, ReferenceLine, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis, ZAxis } from "recharts";
import { SERIES } from "./charts";

const axis = { stroke: "#94a3b8", fontSize: 11, tickLine: false, axisLine: { stroke: "#e2e8f0" } } as const;
const tip = { contentStyle: { borderRadius: 8, border: "1px solid #e2e8f0", fontSize: 12 } };
type Pt = Record<string, number>;

export function MultiLine({ sets, x, y, xLabel, yLabel, height = 260, refX, refY, dot }: { sets: { name: string; data: Pt[]; color?: string; dashed?: boolean }[]; x: string; y: string; xLabel: string; yLabel: string; height?: number; refX?: { v: number; label: string }; refY?: { v: number; label: string }; dot?: { x: number; y: number; label: string } }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart margin={{ top: 8, right: 16, bottom: 18, left: 4 }}>
        <CartesianGrid stroke="#f1f5f9" />
        <XAxis type="number" dataKey={x} {...axis} domain={["dataMin", "dataMax"]} allowDuplicatedCategory={false} label={{ value: xLabel, position: "insideBottom", offset: -10, fontSize: 11, fill: "#64748b" }} tickFormatter={(v) => (Math.abs(v) < 10 ? (+v).toFixed(2) : Math.round(v).toString())} />
        <YAxis type="number" {...axis} width={56} label={{ value: yLabel, angle: -90, position: "insideLeft", fontSize: 11, fill: "#64748b" }} tickFormatter={(v) => (Math.abs(v) < 10 ? (+v).toFixed(2) : Math.round(v).toString())} />
        <Tooltip {...tip} />
        {sets.length > 1 && <Legend wrapperStyle={{ fontSize: 12 }} iconType="plainline" />}
        {refX && <ReferenceLine x={refX.v} stroke="#64748b" strokeDasharray="4 4" label={{ value: refX.label, fontSize: 10, fill: "#64748b", position: "top" }} />}
        {refY && <ReferenceLine y={refY.v} stroke="#b91c1c" strokeDasharray="4 4" label={{ value: refY.label, fontSize: 10, fill: "#b91c1c", position: "insideTopRight" }} />}
        {sets.map((s, i) => <Line key={s.name} data={s.data} dataKey={y} name={s.name} stroke={s.color ?? SERIES[i]} strokeWidth={2} strokeDasharray={s.dashed ? "5 4" : undefined} dot={false} isAnimationActive={false} type="linear" />)}
        {dot && <ReferenceDot x={dot.x} y={dot.y} r={5} fill="#b91c1c" stroke="#fff" strokeWidth={2} label={{ value: dot.label, fontSize: 10, position: "right", fill: "#0f172a" }} />}
      </LineChart>
    </ResponsiveContainer>
  );
}

export function PointCloud({ data, x, y, xLabel, yLabel, height = 260, flag, reversedY, refX }: { data: Pt[]; x: string; y: string; xLabel: string; yLabel: string; height?: number; flag?: string; reversedY?: boolean; refX?: number }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <ScatterChart margin={{ top: 8, right: 16, bottom: 18, left: 4 }}>
        <CartesianGrid stroke="#f1f5f9" />
        <XAxis type="number" dataKey={x} {...axis} name={xLabel} label={{ value: xLabel, position: "insideBottom", offset: -10, fontSize: 11, fill: "#64748b" }} />
        <YAxis type="number" dataKey={y} {...axis} width={48} reversed={reversedY} name={yLabel} label={{ value: yLabel, angle: -90, position: "insideLeft", fontSize: 11, fill: "#64748b" }} />
        <ZAxis range={[50, 50]} />
        <Tooltip {...tip} cursor={{ strokeDasharray: "3 3" }} />
        {refX !== undefined && <ReferenceLine x={refX} stroke="#b91c1c" strokeDasharray="4 4" label={{ value: "FS = 1.0", fontSize: 10, fill: "#b91c1c", position: "top" }} />}
        <Scatter name="OK" data={data.filter((d) => !flag || !d[flag])} fill={SERIES[0]} isAnimationActive={false} />
        {flag && <Scatter name="Liquefiable" data={data.filter((d) => d[flag])} fill="#b91c1c" isAnimationActive={false} />}
        {flag && <Legend wrapperStyle={{ fontSize: 12 }} />}
      </ScatterChart>
    </ResponsiveContainer>
  );
}

const SOIL_COLORS: Record<string, string> = { fill: "#a8a29e", clay: "#b45309", silt: "#d6a85a", sand: "#eab308", gravel: "#78716c", rock: "#475569" };
export function SoilColumns({ holes, foundingDepth }: { holes: { name: string; gwl: number; layers: { top: number; bottom: number; soil: string; spt: number }[] }[]; foundingDepth: number }) {
  const maxD = Math.max(...holes.flatMap((h) => h.layers.map((l) => l.bottom)), foundingDepth + 5);
  const H = 320, top = 18, scale = (H - top - 8) / maxD;
  const w = 64, gap = 46;
  const width = 50 + holes.length * (w + gap);
  return (
    <div className="overflow-x-auto">
      <svg viewBox={`0 0 ${width} ${H}`} className="h-[320px] min-w-full" style={{ width: Math.max(width, 300) }} role="img" aria-label="Borehole soil columns">
        {Array.from({ length: Math.floor(maxD / 5) + 1 }, (_, i) => i * 5).map((d) => (
          <g key={d}><line x1={40} x2={width} y1={top + d * scale} y2={top + d * scale} stroke="#f1f5f9" /><text x={34} y={top + d * scale + 3} fontSize={10} textAnchor="end" fill="#94a3b8">{d} m</text></g>
        ))}
        <line x1={40} x2={width} y1={top + foundingDepth * scale} y2={top + foundingDepth * scale} stroke="#1b5ef5" strokeDasharray="4 3" />
        <text x={width - 4} y={top + foundingDepth * scale - 4} fontSize={10} textAnchor="end" fill="#1b5ef5">founding level</text>
        {holes.map((h, i) => {
          const x = 56 + i * (w + gap);
          return (
            <g key={h.name}>
              <text x={x + w / 2} y={12} fontSize={11} fontWeight={600} textAnchor="middle" fill="#0f172a">{h.name}</text>
              {h.layers.map((l, k) => (
                <g key={k}>
                  <rect x={x} y={top + l.top * scale} width={w} height={Math.max(1, (l.bottom - l.top) * scale)} fill={SOIL_COLORS[l.soil] ?? "#cbd5e1"} stroke="#fff" strokeWidth={2} rx={2} />
                  {(l.bottom - l.top) * scale > 14 && <text x={x + w / 2} y={top + ((l.top + l.bottom) / 2) * scale + 3} fontSize={9.5} textAnchor="middle" fill="#fff" fontWeight={600}>{l.soil} N{l.spt}</text>}
                </g>
              ))}
              <path d={`M${x - 8} ${top + h.gwl * scale} l6 -5 h-12 z`} fill="#2a78d6" />
              <text x={x - 10} y={top + h.gwl * scale + 12} fontSize={9} textAnchor="middle" fill="#2a78d6">GWL</text>
            </g>
          );
        })}
      </svg>
      <div className="mt-1 flex flex-wrap gap-3 text-[11px] text-slate-600">{Object.entries(SOIL_COLORS).map(([k, c]) => <span key={k} className="flex items-center gap-1"><span className="h-2.5 w-2.5 rounded-sm" style={{ background: c }} />{k}</span>)}</div>
    </div>
  );
}

export function Gantt({ acts, total, critical, today }: { acts: { id: string; name: string; phase: string; es: number; ef: number; critical: boolean; float: number }[]; total: number; critical: boolean; today?: number }) {
  const rows = critical ? acts.filter((a) => a.critical || ["MOB", "EXC", "FND", "BSM", "RFP", "COM"].includes(a.id)) : acts;
  const rowH = 18, W = 900, left = 190;
  const sx = (d: number) => left + (d / total) * (W - left - 10);
  const months = Math.ceil(total / 21.7);
  const PH: Record<string, string> = { Preliminaries: "#64748b", Substructure: SERIES[6], Superstructure: SERIES[0], Envelope: SERIES[2], Services: SERIES[1], "Fit-out": SERIES[4], Commissioning: SERIES[5] };
  return (
    <div className="scrollbar-thin max-h-[520px] overflow-auto">
      <svg viewBox={`0 0 ${W} ${rows.length * rowH + 28}`} style={{ minWidth: 720, width: "100%" }} role="img" aria-label="Construction programme Gantt chart">
        {Array.from({ length: months + 1 }, (_, m) => (
          <g key={m}><line x1={sx(m * 21.7)} x2={sx(m * 21.7)} y1={16} y2={rows.length * rowH + 22} stroke="#f1f5f9" />{m % Math.max(1, Math.round(months / 12)) === 0 && <text x={sx(m * 21.7)} y={11} fontSize={9} fill="#94a3b8" textAnchor="middle">M{m}</text>}</g>
        ))}
        {today !== undefined && <line x1={sx(today)} x2={sx(today)} y1={14} y2={rows.length * rowH + 22} stroke="#b91c1c" strokeDasharray="3 3" />}
        {rows.map((a, i) => (
          <g key={a.id} transform={`translate(0 ${20 + i * rowH})`}>
            <text x={4} y={12} fontSize={10} fill="#334155">{a.name.length > 30 ? a.name.slice(0, 29) + "…" : a.name}</text>
            <rect x={sx(a.es)} y={3} width={Math.max(2, sx(a.ef) - sx(a.es))} height={rowH - 7} rx={3} fill={PH[a.phase] ?? "#94a3b8"} stroke={a.critical ? "#0f172a" : "none"} strokeWidth={a.critical ? 1.2 : 0}>
              <title>{`${a.name}: day ${a.es}–${a.ef}${a.critical ? " (critical)" : `, float ${a.float} d`}`}</title>
            </rect>
          </g>
        ))}
      </svg>
      <div className="sticky bottom-0 flex flex-wrap gap-3 bg-white pt-2 text-[11px] text-slate-600">{Object.entries(PH).map(([k, c]) => <span key={k} className="flex items-center gap-1"><span className="h-2.5 w-2.5 rounded-sm" style={{ background: c }} />{k}</span>)}<span className="flex items-center gap-1"><span className="h-2.5 w-2.5 rounded-sm border border-slate-900" />critical path</span></div>
    </div>
  );
}
