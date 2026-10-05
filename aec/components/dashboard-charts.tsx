"use client";

import { BarViz } from "./charts";
import { fmt } from "./ui";

export function ComplianceChart({ data }: { data: { name: string; Pass: number; Warn: number; Fail: number }[] }) {
  return <BarViz data={data} x="name" horizontal stacked height={Math.max(180, data.length * 44)} series={[{ key: "Pass", color: "#15803d" }, { key: "Warn", color: "#d97706" }, { key: "Fail", color: "#b91c1c" }]} />;
}

export function CostChart({ data }: { data: { name: string; Estimate: number; Budget: number }[] }) {
  return <BarViz data={data} x="name" height={240} valueFormatter={(v) => fmt.money(v)} series={[{ key: "Estimate" }, { key: "Budget", color: "#94a3b8" }]} />;
}

export function CarbonChart({ data }: { data: { name: string; Embodied: number; Target: number }[] }) {
  return <BarViz data={data} x="name" height={240} series={[{ key: "Embodied", name: "Embodied A1–A5" }, { key: "Target", color: "#94a3b8" }]} />;
}
