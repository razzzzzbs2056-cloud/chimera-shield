"use client";

import { Download, Search } from "lucide-react";
import { Fragment, useState } from "react";
import { fmt } from "./ui";

type Row = { code: string; section: string; item: string; unit: string; qty: number; rate: number; amount: number; carbon: number; discipline: string };

export function BoqTable({ rows, href, totals }: { rows: Row[]; href: string; totals: { label: string; value: number }[] }) {
  const [q, setQ] = useState("");
  const shown = rows.filter((r) => `${r.code} ${r.item} ${r.section}`.toLowerCase().includes(q.toLowerCase()));
  const sections = [...new Set(shown.map((r) => r.section))];
  return (
    <div className="card">
      <div className="flex flex-wrap items-center gap-2 border-b border-slate-100 p-3">
        <h3 className="text-sm font-semibold">Bill of quantities</h3>
        <div className="relative ml-auto w-full sm:w-64"><Search className="pointer-events-none absolute left-2.5 top-2 h-4 w-4 text-slate-400" /><input className="input py-1.5 pl-8" placeholder="Filter items…" value={q} onChange={(e) => setQ(e.target.value)} aria-label="Filter BOQ" /></div>
        <a href={href} className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"><Download className="h-4 w-4" />CSV</a>
      </div>
      <div className="scrollbar-thin overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-50/70"><tr>{["Code", "Item", "Unit", "Qty", "Rate", "Amount", "tCO₂e"].map((h, i) => <th key={h} className={`th ${i >= 3 ? "text-right" : ""}`}>{h}</th>)}</tr></thead>
          <tbody>
            {sections.map((s) => (
              <Fragment key={s}>
                <tr className="bg-slate-50"><td colSpan={5} className="px-3 py-1.5 text-xs font-semibold uppercase tracking-wide text-slate-600">{s}</td><td className="num px-3 py-1.5 text-right text-xs font-semibold">{fmt.money(shown.filter((r) => r.section === s).reduce((a, r) => a + r.amount, 0))}</td><td /></tr>
                {shown.filter((r) => r.section === s).map((r) => (
                  <tr key={r.code + r.item} className="border-t border-slate-100">
                    <td className="td font-mono text-xs text-slate-500">{r.code}</td><td className="td">{r.item}</td><td className="td">{r.unit}</td>
                    <td className="td num text-right">{fmt.n(r.qty, r.qty < 100 ? 1 : 0)}</td><td className="td num text-right">{fmt.n(r.rate, 2)}</td><td className="td num text-right font-medium">{fmt.n(r.amount)}</td><td className="td num text-right">{fmt.n(r.carbon, 1)}</td>
                  </tr>
                ))}
              </Fragment>
            ))}
          </tbody>
          <tfoot>
            {totals.map((t, i) => <tr key={t.label} className={i === totals.length - 1 ? "border-t-2 border-slate-300 font-semibold" : "border-t border-slate-100"}><td colSpan={5} className="px-3 py-1.5 text-right text-sm">{t.label}</td><td className="num px-3 py-1.5 text-right text-sm">{fmt.n(t.value)}</td><td /></tr>)}
          </tfoot>
        </table>
      </div>
    </div>
  );
}
