"use client";

import { AlertTriangle, Building2, CheckCircle2, Loader2, MoreHorizontal, Plus, Search, Sparkles, Trash2 } from "lucide-react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useMemo, useState } from "react";
import { api, Badge, Button, EmptyState, fmt, Modal, useToast } from "./ui";

export interface ProjectCard {
  id: string; name: string; code: string; client: string | null; stage: string; status: string; city: string; type: string; floors: number;
  kpis: { gfa: number; cost: number; embodiedCarbon: number; fail: number; pass: number; warn: number; criticalClashes: number; budgetVariance: number; eui: number } | null;
  openIssues: number; updated: string;
}

const STAGES = ["Feasibility", "Concept", "Scheme Design", "Design Development", "Construction Documents", "Construction", "Operations"];
const SAMPLES = ["Harbourview Tower (32-storey office, SF)", "Riverside Medical Pavilion (hospital, Seattle)", "Elm Street Timber Residences (mass timber, Austin)", "Canary Wharf Life Sciences (labs, London)", "Southbank Residences (45-storey, Melbourne)", "Lakeside Primary School (in operation, Chicago)"];

export function ProjectsList({ initial }: { initial: ProjectCard[] }) {
  const [items, setItems] = useState(initial);
  const [q, setQ] = useState("");
  const [stage, setStage] = useState("all");
  const [confirm, setConfirm] = useState<ProjectCard | null>(null);
  const [menu, setMenu] = useState<string | null>(null);
  const [sampleOpen, setSampleOpen] = useState(useSearchParams().get("welcome") === "1" && initial.length === 0);
  const [loadingSample, setLoadingSample] = useState<number | null>(null);
  const toast = useToast();
  const router = useRouter();

  const shown = useMemo(() => items.filter((p) => (stage === "all" || p.stage === stage) && `${p.name} ${p.code} ${p.client} ${p.city}`.toLowerCase().includes(q.toLowerCase())), [items, q, stage]);

  async function remove(p: ProjectCard) {
    setConfirm(null);
    const prev = items;
    setItems((x) => x.filter((y) => y.id !== p.id)); // optimistic
    try {
      await api(`/api/projects/${p.id}`, { method: "DELETE" });
      toast({ tone: "success", text: `Deleted ${p.name}` });
      router.refresh();
    } catch (e) {
      setItems(prev);
      toast({ tone: "error", text: (e as Error).message });
    }
  }

  async function setStageOf(p: ProjectCard, s: string) {
    setMenu(null);
    const prev = items;
    setItems((x) => x.map((y) => (y.id === p.id ? { ...y, stage: s } : y)));
    try { await api(`/api/projects/${p.id}`, { method: "PATCH", body: { stage: s } }); }
    catch (e) { setItems(prev); toast({ tone: "error", text: (e as Error).message }); }
  }

  async function loadSample(i: number) {
    setLoadingSample(i);
    try {
      const { id } = await api<{ id: string }>("/api/sample", { body: { index: i } });
      toast({ tone: "success", text: "Sample project created and analysed" });
      router.push(`/projects/${id}`);
      router.refresh();
    } catch (e) {
      toast({ tone: "error", text: (e as Error).message });
      setLoadingSample(null);
    }
  }

  return (
    <>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input className="input pl-9" placeholder="Search projects, clients, cities…" value={q} onChange={(e) => setQ(e.target.value)} aria-label="Search projects" />
        </div>
        <select className="input sm:w-56" value={stage} onChange={(e) => setStage(e.target.value)} aria-label="Filter by stage">
          <option value="all">All stages</option>
          {STAGES.map((s) => <option key={s}>{s}</option>)}
        </select>
        <Button variant="secondary" onClick={() => setSampleOpen(true)}><Sparkles className="h-4 w-4" /> Sample project</Button>
      </div>

      {items.length === 0 ? (
        <EmptyState icon={Building2} title="No projects yet" body="Start from a site brief — the intake engine sizes a parametric scheme and routes it to the right specialist agents."
          action={<div className="flex flex-wrap justify-center gap-2"><Link href="/projects/new" className="inline-flex items-center gap-1.5 rounded-lg bg-brand-600 px-3.5 py-2 text-sm font-medium text-white hover:bg-brand-700"><Plus className="h-4 w-4" />New project</Link><Button variant="secondary" onClick={() => setSampleOpen(true)}>Load a sample</Button></div>} />
      ) : shown.length === 0 ? (
        <EmptyState icon={Search} title="No matching projects" body="Try a different search term or stage filter." action={<Button variant="secondary" onClick={() => { setQ(""); setStage("all"); }}>Clear filters</Button>} />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {shown.map((p) => (
            <div key={p.id} className="card group relative flex flex-col transition hover:border-brand-300 hover:shadow-md">
              <Link href={`/projects/${p.id}`} className="flex-1 p-4">
                <div className="flex items-start justify-between gap-2 pr-6">
                  <div className="min-w-0">
                    <div className="truncate font-semibold text-slate-900">{p.name}</div>
                    <div className="truncate text-xs text-slate-500">{p.client ?? "—"} · {p.city}</div>
                  </div>
                </div>
                <div className="mt-3 flex flex-wrap gap-1.5">
                  <Badge tone="blue">{p.stage}</Badge><Badge>{p.code}</Badge><Badge className="capitalize">{p.type}</Badge><Badge>{p.floors} storeys</Badge>
                </div>
                {p.kpis ? (
                  <dl className="mt-4 grid grid-cols-3 gap-2 text-xs">
                    <div><dt className="text-slate-500">GFA</dt><dd className="num font-semibold text-slate-900">{fmt.n(p.kpis.gfa)} m²</dd></div>
                    <div><dt className="text-slate-500">Estimate</dt><dd className={`num font-semibold ${p.kpis.budgetVariance > 0 ? "text-amber-700" : "text-slate-900"}`}>{fmt.money(p.kpis.cost)}</dd></div>
                    <div><dt className="text-slate-500">Carbon</dt><dd className="num font-semibold text-slate-900">{p.kpis.embodiedCarbon} kg/m²</dd></div>
                  </dl>
                ) : <p className="mt-4 text-xs text-slate-500">Not analysed yet</p>}
              </Link>
              <div className="flex items-center justify-between border-t border-slate-100 px-4 py-2 text-xs">
                {p.kpis ? (
                  <span className={`flex items-center gap-1 font-medium ${p.kpis.fail ? "text-red-700" : "text-emerald-700"}`}>
                    {p.kpis.fail ? <AlertTriangle className="h-3.5 w-3.5" /> : <CheckCircle2 className="h-3.5 w-3.5" />}
                    {p.kpis.fail ? `${p.kpis.fail} failing checks` : `${p.kpis.pass} checks passing`}
                  </span>
                ) : <span />}
                <span className="text-slate-500">{p.openIssues} open issues</span>
              </div>
              <button onClick={() => setMenu(menu === p.id ? null : p.id)} className="absolute right-2 top-3 rounded-md p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-700" aria-label={`Actions for ${p.name}`}><MoreHorizontal className="h-4 w-4" /></button>
              {menu === p.id && (
                <div className="absolute right-2 top-10 z-10 w-56 rounded-lg border border-slate-200 bg-white py-1 text-sm shadow-lg" onMouseLeave={() => setMenu(null)}>
                  <div className="px-3 py-1 text-[11px] font-semibold uppercase text-slate-400">Move to stage</div>
                  {STAGES.map((s) => <button key={s} onClick={() => setStageOf(p, s)} className={`block w-full px-3 py-1.5 text-left hover:bg-slate-50 ${s === p.stage ? "font-semibold text-brand-700" : ""}`}>{s}</button>)}
                  <div className="my-1 border-t border-slate-100" />
                  <button onClick={() => { setMenu(null); setConfirm(p); }} className="flex w-full items-center gap-2 px-3 py-1.5 text-left text-red-700 hover:bg-red-50"><Trash2 className="h-3.5 w-3.5" /> Delete project</button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <Modal open={!!confirm} onClose={() => setConfirm(null)} title="Delete project?" footer={<><Button variant="secondary" onClick={() => setConfirm(null)}>Cancel</Button><Button variant="danger" onClick={() => confirm && remove(confirm)}>Delete</Button></>}>
        <p className="text-sm text-slate-600">This permanently deletes <b>{confirm?.name}</b>, its analysis runs, boreholes, design options, issues and assets.</p>
      </Modal>
      <Modal open={sampleOpen} onClose={() => setSampleOpen(false)} title="Load a sample project">
        <p className="mb-3 text-sm text-slate-600">Each sample comes with borehole logs, a full multi-agent engineering run, clashes and RFIs.</p>
        <ul className="space-y-2">
          {SAMPLES.map((s, i) => (
            <li key={s}><button disabled={loadingSample !== null} onClick={() => loadSample(i)} className="flex w-full items-center justify-between rounded-lg border border-slate-200 px-3 py-2.5 text-left text-sm hover:border-brand-300 hover:bg-brand-50/40 disabled:opacity-60">
              {s}{loadingSample === i ? <Loader2 className="h-4 w-4 animate-spin text-brand-600" /> : <Plus className="h-4 w-4 text-slate-400" />}
            </button></li>
          ))}
        </ul>
      </Modal>
    </>
  );
}
