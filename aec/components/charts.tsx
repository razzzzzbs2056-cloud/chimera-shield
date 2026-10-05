"use client";

// Thin wrappers around Recharts using the validated categorical palette
// (fixed slot order), 2px lines, recessive grid and a hover tooltip.

import {
  Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Legend, Line, LineChart, ReferenceLine, ResponsiveContainer,
  Scatter, ScatterChart, Tooltip, XAxis, YAxis, ZAxis,
} from "recharts";

export const SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7", "#e34948"];
const axis = { stroke: "#94a3b8", fontSize: 11, tickLine: false, axisLine: { stroke: "#e2e8f0" } } as const;
const tip = { contentStyle: { borderRadius: 8, border: "1px solid #e2e8f0", fontSize: 12, boxShadow: "0 4px 12px rgba(15,23,42,.08)" }, labelStyle: { color: "#0f172a", fontWeight: 600 } };

type Row = Record<string, string | number | null | undefined>;
interface SeriesDef { key: string; name?: string; color?: string }

export function LineViz({ data, x, series, height = 240, xLabel, yLabel, refY, refLabel, xType = "category", layout }: { data: Row[]; x: string; series: SeriesDef[]; height?: number; xLabel?: string; yLabel?: string; refY?: number; refLabel?: string; xType?: "number" | "category"; layout?: "vertical" }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} layout={layout} margin={{ top: 8, right: 16, bottom: xLabel ? 18 : 4, left: 4 }}>
        <CartesianGrid stroke="#f1f5f9" vertical={false} />
        {layout === "vertical" ? (
          <>
            <XAxis type="number" {...axis} label={xLabel ? { value: xLabel, position: "insideBottom", offset: -10, fontSize: 11, fill: "#64748b" } : undefined} />
            <YAxis dataKey={x} type="number" {...axis} width={44} label={yLabel ? { value: yLabel, angle: -90, position: "insideLeft", fontSize: 11, fill: "#64748b" } : undefined} />
          </>
        ) : (
          <>
            <XAxis dataKey={x} type={xType} {...axis} domain={xType === "number" ? ["dataMin", "dataMax"] : undefined} label={xLabel ? { value: xLabel, position: "insideBottom", offset: -10, fontSize: 11, fill: "#64748b" } : undefined} />
            <YAxis {...axis} width={52} label={yLabel ? { value: yLabel, angle: -90, position: "insideLeft", fontSize: 11, fill: "#64748b" } : undefined} />
          </>
        )}
        <Tooltip {...tip} />
        {series.length > 1 && <Legend wrapperStyle={{ fontSize: 12 }} iconType="plainline" />}
        {refY !== undefined && <ReferenceLine {...(layout === "vertical" ? { x: refY } : { y: refY })} stroke="#b91c1c" strokeDasharray="4 4" label={{ value: refLabel, fontSize: 10, fill: "#b91c1c", position: "insideTopRight" }} />}
        {series.map((s, i) => <Line key={s.key} type="monotone" dataKey={s.key} name={s.name ?? s.key} stroke={s.color ?? SERIES[i]} strokeWidth={2} dot={false} activeDot={{ r: 4 }} isAnimationActive={false} />)}
      </LineChart>
    </ResponsiveContainer>
  );
}

export function AreaViz({ data, x, series, height = 240, stacked }: { data: Row[]; x: string; series: SeriesDef[]; height?: number; stacked?: boolean }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 8, right: 16, bottom: 4, left: 4 }}>
        <CartesianGrid stroke="#f1f5f9" vertical={false} />
        <XAxis dataKey={x} {...axis} />
        <YAxis {...axis} width={52} />
        <Tooltip {...tip} />
        {series.length > 1 && <Legend wrapperStyle={{ fontSize: 12 }} />}
        {series.map((s, i) => <Area key={s.key} type="monotone" dataKey={s.key} name={s.name ?? s.key} stackId={stacked ? "a" : undefined} stroke={s.color ?? SERIES[i]} fill={s.color ?? SERIES[i]} fillOpacity={0.22} strokeWidth={2} isAnimationActive={false} />)}
      </AreaChart>
    </ResponsiveContainer>
  );
}

export function BarViz({ data, x, series, height = 240, horizontal, stacked, colorBy, valueFormatter }: { data: Row[]; x: string; series: SeriesDef[]; height?: number; horizontal?: boolean; stacked?: boolean; colorBy?: (row: Row, i: number) => string; valueFormatter?: (v: number) => string }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} layout={horizontal ? "vertical" : "horizontal"} margin={{ top: 8, right: 16, bottom: 4, left: 4 }} barCategoryGap="22%">
        <CartesianGrid stroke="#f1f5f9" vertical={horizontal} horizontal={!horizontal} />
        {horizontal ? (
          <>
            <XAxis type="number" {...axis} tickFormatter={valueFormatter} />
            <YAxis type="category" dataKey={x} {...axis} width={130} />
          </>
        ) : (
          <>
            <XAxis dataKey={x} {...axis} interval="preserveStartEnd" />
            <YAxis {...axis} width={56} tickFormatter={valueFormatter} />
          </>
        )}
        <Tooltip {...tip} cursor={{ fill: "#f8fafc" }} formatter={valueFormatter ? (v) => valueFormatter(Number(v)) : undefined} />
        {series.length > 1 && <Legend wrapperStyle={{ fontSize: 12 }} />}
        {series.map((s, i) => (
          <Bar key={s.key} dataKey={s.key} name={s.name ?? s.key} stackId={stacked ? "a" : undefined} fill={s.color ?? SERIES[i]} radius={stacked ? 0 : horizontal ? [0, 4, 4, 0] : [4, 4, 0, 0]} stroke="#fff" strokeWidth={stacked ? 1 : 0} isAnimationActive={false}>
            {colorBy && data.map((row, j) => <Cell key={j} fill={colorBy(row, j)} />)}
          </Bar>
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}

export function ScatterViz({ data, x, y, z, xLabel, yLabel, height = 280, highlight }: { data: Row[]; x: string; y: string; z?: string; xLabel: string; yLabel: string; height?: number; highlight?: (r: Row) => boolean }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <ScatterChart margin={{ top: 8, right: 16, bottom: 18, left: 4 }}>
        <CartesianGrid stroke="#f1f5f9" />
        <XAxis type="number" dataKey={x} name={xLabel} {...axis} domain={["auto", "auto"]} label={{ value: xLabel, position: "insideBottom", offset: -10, fontSize: 11, fill: "#64748b" }} />
        <YAxis type="number" dataKey={y} name={yLabel} {...axis} width={56} domain={["auto", "auto"]} label={{ value: yLabel, angle: -90, position: "insideLeft", fontSize: 11, fill: "#64748b" }} />
        {z && <ZAxis type="number" dataKey={z} range={[60, 260]} />}
        <Tooltip {...tip} cursor={{ strokeDasharray: "3 3" }} />
        <Scatter data={data} isAnimationActive={false}>
          {data.map((r, i) => <Cell key={i} fill={highlight?.(r) ? SERIES[0] : "#94a3b8"} stroke="#fff" strokeWidth={2} />)}
        </Scatter>
      </ScatterChart>
    </ResponsiveContainer>
  );
}
