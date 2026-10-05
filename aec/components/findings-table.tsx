"use client";

import { Download, Search } from "lucide-react";
import { useMemo, useState } from "react";
import type { Finding } from "@/lib/engine/types";
import { Badge, Segmented, StatusBadge } from "./ui";

export function FindingsTable({ findings, csvHref }: { findings: Finding[]; csvHref: string }) {
  const [status, setStatus] = useState<"all" | "FAIL" | "WARN" | "PASS">("all");
  const [disc, setDisc] = useState("all");
  const [q, setQ] = useState("");
  const discs = useMemo(() => [...new Set(findings.map((f) => f.discipline))].sort(), [findings]);
  const shown = findings.filter((f) => (status === "all" || f.status === status) && (disc === "all" || f.discipline === disc) && `${f.check} ${f.standard} ${f.clause} ${f.evidence}`.toLowerCase().includes(q.toLowerCase()));
  const count = (s: string) => findings.filter((f) => f.status === s).length;
  return (
    <div className="card">
      <div className="flex flex-col gap-3 border-b border-slate-100 p-3 lg:flex-row lg:items-center">
        <Segmented value={status} onChange={setStatus} options={[{ value: "all", label: `All ${findings.length}` }, { value: "FAIL", label: `Fail ${count("FAIL")}` }, { value: "WARN", label: `Warn ${count("WARN")}` }, { value: "PASS", label: `Pass ${count("PASS")}` }]} />
        <select className="input py-1.5 lg:w-48" value={disc} onChange={(e) => setDisc(e.target.value)} aria-label="Discipline"><option value="all">All disciplines</option>{discs.map((d) => <option key={d}>{d}</option>)}</select>
        <div className="relative flex-1"><Search className="pointer-events-none absolute left-2.5 top-2 h-4 w-4 text-slate-400" /><input className="input py-1.5 pl-8" placeholder="Search checks, clauses, evidence…" value={q} onChange={(e) => setQ(e.target.value)} aria-label="Search findings" /></div>
        <a href={csvHref} className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"><Download className="h-4 w-4" />CSV</a>
      </div>
      <div className="scrollbar-thin overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-100">
          <thead className="bg-slate-50/70"><tr>{["Status", "Check", "Standard & clause", "Requirement", "Calculation / evidence", "Value / limit"].map((h) => <th key={h} className="th whitespace-nowrap">{h}</th>)}</tr></thead>
          <tbody className="divide-y divide-slate-100">
            {shown.map((f) => (
              <tr key={f.id} className={f.status === "FAIL" ? "bg-red-50/30" : undefined}>
                <td className="td"><StatusBadge status={f.status} /></td>
                <td className="td"><div className="font-medium text-slate-900">{f.check}</div><div className="text-[11px] text-slate-500">{f.discipline}</div></td>
                <td className="td whitespace-nowrap"><div className="font-medium">{f.standard}</div><div className="text-[11px] text-slate-500">{f.clause}</div>{f.proxy && <Badge tone="amber" className="mt-1">proxy method</Badge>}</td>
                <td className="td text-xs">{f.requirement}</td>
                <td className="td text-xs">{f.evidence}</td>
                <td className="td num whitespace-nowrap text-xs">{f.value ?? "—"}{f.limit !== null && f.limit !== undefined ? <span className="text-slate-400"> / {f.limit}</span> : null}{f.unit ? ` ${f.unit}` : ""}</td>
              </tr>
            ))}
            {shown.length === 0 && <tr><td colSpan={6} className="px-4 py-10 text-center text-sm text-slate-500">No findings match these filters.</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}
