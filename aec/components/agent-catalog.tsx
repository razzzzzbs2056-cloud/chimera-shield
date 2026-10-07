"use client";

import { ArrowRight, Bot, CheckCircle2, Search, X } from "lucide-react";
import { useMemo, useState } from "react";
import type { AgentSpec, Tier } from "@/lib/agent-catalog";
import { Badge, Segmented } from "./ui";

const TIER_TONE: Record<Tier, "slate" | "blue" | "violet"> = { Starter: "slate", Professional: "blue", Enterprise: "violet" };

function List({ title, items }: { title: string; items: string[] }) {
  return (
    <div>
      <h4 className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">{title}</h4>
      <ul className="mt-1.5 space-y-1">{items.map((x) => <li key={x} className="flex gap-1.5 text-sm text-slate-700"><CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-brand-600" />{x}</li>)}</ul>
    </div>
  );
}

export function AgentCatalog({ agents, origin }: { agents: AgentSpec[]; origin: string }) {
  const [tier, setTier] = useState<"all" | Tier>("all");
  const [q, setQ] = useState("");
  const [open, setOpen] = useState<AgentSpec | null>(null);
  const name = (id: string) => (id === "all" ? "All agents" : agents.find((a) => a.id === id)?.name ?? id);
  const shown = useMemo(() => agents.filter((a) => (tier === "all" || a.tier === tier) && `${a.name} ${a.discipline} ${a.tagline} ${a.skills.join(" ")} ${a.buyers.join(" ")}`.toLowerCase().includes(q.toLowerCase())), [agents, tier, q]);

  return (
    <>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative flex-1"><Search className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-slate-400" /><input className="input pl-9" placeholder="Search agents, skills, standards, buyers…" value={q} onChange={(e) => setQ(e.target.value)} aria-label="Search agents" /></div>
        <Segmented value={tier} onChange={setTier} options={[{ value: "all", label: `All ${agents.length}` }, { value: "Starter", label: "Starter" }, { value: "Professional", label: "Professional" }, { value: "Enterprise", label: "Enterprise" }]} />
      </div>
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {shown.map((a) => (
          <button key={a.id} onClick={() => setOpen(a)} className="card group flex flex-col p-4 text-left transition hover:border-brand-300 hover:shadow-md">
            <div className="flex items-start gap-3">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-brand-50 text-brand-600"><Bot className="h-4 w-4" /></div>
              <div className="min-w-0 flex-1">
                <div className="font-semibold text-slate-900">{a.name}</div>
                <div className="mt-0.5 flex flex-wrap gap-1"><Badge>{a.discipline}</Badge><Badge tone={TIER_TONE[a.tier]}>{a.tier}+</Badge></div>
              </div>
            </div>
            <p className="mt-3 text-sm text-slate-600">{a.tagline}</p>
            <div className="mt-3 flex flex-wrap gap-1">{a.skills.slice(0, 3).map((s) => <span key={s} className="rounded bg-slate-100 px-1.5 py-0.5 text-[11px] text-slate-600">{s.length > 42 ? s.slice(0, 41) + "…" : s}</span>)}{a.skills.length > 3 && <span className="text-[11px] text-slate-400">+{a.skills.length - 3} skills</span>}</div>
            <div className="mt-auto flex items-center justify-between pt-4 text-xs"><span className="text-slate-500">Sold to: {a.buyers[0]}</span><ArrowRight className="h-4 w-4 text-slate-300 group-hover:text-brand-600" /></div>
          </button>
        ))}
      </div>
      {shown.length === 0 && <p className="py-10 text-center text-sm text-slate-500">No agents match.</p>}

      {open && (
        <div className="fixed inset-0 !mt-0 z-50 flex justify-end bg-slate-900/40 backdrop-blur-sm" onMouseDown={() => setOpen(null)} role="dialog" aria-modal aria-label={open.name}>
          <aside className="h-full w-full max-w-2xl overflow-y-auto bg-white shadow-xl" onMouseDown={(e) => e.stopPropagation()}>
            <div className="sticky top-0 flex items-start justify-between gap-3 border-b border-slate-100 bg-white px-6 py-4">
              <div>
                <div className="flex items-center gap-2"><h2 className="text-lg font-semibold">{open.name}</h2><Badge tone={TIER_TONE[open.tier]}>{open.tier}+</Badge></div>
                <p className="text-sm text-slate-500">{open.tagline}</p>
              </div>
              <button onClick={() => setOpen(null)} className="rounded-md p-1 text-slate-400 hover:bg-slate-100" aria-label="Close"><X className="h-5 w-5" /></button>
            </div>
            <div className="space-y-5 px-6 py-5">
              <p className="text-sm text-slate-700">{open.description}</p>
              <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-900"><b>Business value:</b> {open.valueProp}</div>
              <List title="Skills & methods" items={open.skills} />
              <div className="grid gap-5 sm:grid-cols-2"><List title="Inputs" items={open.inputs} /><List title="Outputs" items={open.outputs} /></div>
              <List title="Standards" items={open.standards} />
              <div>
                <h4 className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Collaborates with</h4>
                <ul className="mt-1.5 space-y-1">{open.handoffs.map((h) => <li key={h.to + h.what} className="text-sm text-slate-700"><b>{name(h.to)}</b> — {h.what}</li>)}</ul>
              </div>
              <div><h4 className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Who buys it</h4><div className="mt-1.5 flex flex-wrap gap-1.5">{open.buyers.map((b) => <Badge key={b} tone="blue">{b}</Badge>)}</div></div>
              <div className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-900"><b>Scope & limits:</b> {open.limits}</div>
              <div>
                <h4 className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">Call it via the API</h4>
                <pre className="mt-1.5 overflow-x-auto rounded-lg bg-slate-950 p-3 text-[11px] leading-relaxed text-slate-100">{`curl -X POST ${origin}/api/v1/analyze \\
  -H "Authorization: Bearer $AEC_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"buildingType":"office","city":"Seattle","floors":20,"agents":["${open.id}"]}'`}</pre>
              </div>
            </div>
          </aside>
        </div>
      )}
    </>
  );
}
