"use client";

import { Check, Loader2, Save, Sparkles, Star, Trash2, Wand2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useRef, useState } from "react";
import type { Objective } from "@/lib/engine/alternatives";
import type { Borehole, DesignParams, Intake, StandardRef } from "@/lib/engine/types";
import { evaluate, type Evaluation } from "@/lib/engine/workflow";
import { ScatterViz } from "./charts";
import { AgentProgress } from "./agent-progress";
import { api, Badge, Button, Card, EmptyState, fmt, Modal, Segmented, useToast } from "./ui";

interface Ctx { id: string; name: string; code: string; intake: Intake; boreholes: Borehole[]; standards: StandardRef[]; pins: Record<string, string> }
type Option = { id: string; name: string; objective: string; params: DesignParams; metrics: Record<string, number>; score: number; notes: string | null; starred: number };
type Alt = { name: string; params: DesignParams; metrics: Record<string, number>; score: number; pareto: boolean; scores: Record<string, number> };

const SLIDERS: { key: keyof DesignParams; label: string; min: number; max: number; step: number; unit?: string }[] = [
  { key: "floors", label: "Storeys", min: 1, max: 80, step: 1 },
  { key: "floorHeight", label: "Floor-to-floor", min: 3.0, max: 5.5, step: 0.05, unit: "m" },
  { key: "baysX", label: "Bays (X)", min: 2, max: 12, step: 1 },
  { key: "baysY", label: "Bays (Y)", min: 2, max: 8, step: 1 },
  { key: "spanX", label: "Column spacing X", min: 6, max: 12, step: 0.3, unit: "m" },
  { key: "spanY", label: "Column spacing Y", min: 6, max: 12, step: 0.3, unit: "m" },
  { key: "coreWidth", label: "Core width", min: 6, max: 30, step: 0.5, unit: "m" },
  { key: "coreDepth", label: "Core depth", min: 5, max: 20, step: 0.5, unit: "m" },
  { key: "coreWallThickness", label: "Core wall", min: 0.2, max: 0.9, step: 0.05, unit: "m" },
  { key: "columnSize", label: "Column size", min: 0.3, max: 1.4, step: 0.05, unit: "m" },
  { key: "slabThickness", label: "Slab depth", min: 0.12, max: 0.4, step: 0.01, unit: "m" },
  { key: "wwr", label: "Façade glazing ratio", min: 0.2, max: 0.8, step: 0.05 },
];
const SELECTS: { key: keyof DesignParams; label: string; options: string[] }[] = [
  { key: "material", label: "Structural material", options: ["concrete", "steel", "composite", "timber"] },
  { key: "lateralSystem", label: "Lateral system", options: ["auto", "core", "core-outrigger", "shear-wall", "moment-frame", "braced-frame", "dual", "diagrid", "clt-wall"] },
  { key: "slabSystem", label: "Slab system", options: ["flat-plate", "post-tensioned", "beam-slab", "composite-deck", "clt"] },
  { key: "facadeType", label: "Façade", options: ["unitised", "curtain-wall", "punched", "rainscreen"] },
  { key: "heating", label: "Heating", options: ["heat-pump", "gas-boiler", "district"] },
];

export function Massing({ p, highlight }: { p: DesignParams; highlight?: boolean }) {
  const Lx = p.baysX * p.spanX, Ly = p.baysY * p.spanY;
  const H = p.groundFloorHeight + (p.floors - 1) * p.floorHeight;
  const c = Math.cos(Math.PI / 6), s = 0.5;
  const pt = (x: number, y: number, z: number) => [(x - y) * c, (x + y) * s - z] as const;
  const corners = [pt(0, 0, 0), pt(Lx, 0, 0), pt(Lx, Ly, 0), pt(0, Ly, 0), pt(0, 0, H), pt(Lx, 0, H), pt(Lx, Ly, H), pt(0, Ly, H)];
  const xs = corners.map((q) => q[0]), ys = corners.map((q) => q[1]);
  const [minX, maxX, minY, maxY] = [Math.min(...xs), Math.max(...xs), Math.min(...ys), Math.max(...ys)];
  const poly = (pts: (readonly [number, number])[]) => pts.map((q) => q.join(",")).join(" ");
  const step = Math.max(1, Math.ceil(p.floors / 40));
  const cx0 = (Lx - p.coreWidth) / 2, cy0 = (Ly - p.coreDepth) / 2;
  return (
    <svg viewBox={`${minX - 4} ${minY - 4} ${maxX - minX + 8} ${maxY - minY + 8}`} className="h-full w-full" role="img" aria-label={`Massing: ${p.floors} storeys, ${Math.round(Lx)}×${Math.round(Ly)} m plate`}>
      <polygon points={poly([pt(Lx, 0, 0), pt(Lx, Ly, 0), pt(Lx, Ly, H), pt(Lx, 0, H)])} fill={highlight ? "#bcdaff" : "#dbe3ee"} stroke="#64748b" strokeWidth={0.3} />
      <polygon points={poly([pt(0, Ly, 0), pt(Lx, Ly, 0), pt(Lx, Ly, H), pt(0, Ly, H)])} fill={highlight ? "#8ec3ff" : "#c3cfdd"} stroke="#64748b" strokeWidth={0.3} />
      {Array.from({ length: Math.floor(p.floors / step) }, (_, k) => {
        const z = p.groundFloorHeight + k * step * p.floorHeight;
        return <polyline key={k} points={poly([pt(Lx, 0, z), pt(Lx, Ly, z), pt(0, Ly, z)])} fill="none" stroke="#94a3b8" strokeWidth={0.2} />;
      })}
      <polygon points={poly([corners[4], corners[5], corners[6], corners[7]])} fill="#f8fafc" stroke="#64748b" strokeWidth={0.3} />
      <polygon points={poly([pt(cx0, cy0, H), pt(cx0 + p.coreWidth, cy0, H), pt(cx0 + p.coreWidth, cy0 + p.coreDepth, H), pt(cx0, cy0 + p.coreDepth, H)])} fill="#1b5ef5" fillOpacity={0.25} stroke="#1b5ef5" strokeWidth={0.3} />
    </svg>
  );
}

function MetricDelta({ label, a, b, unit, better = "lower", d = 0 }: { label: string; a: number; b?: number; unit?: string; better?: "lower" | "higher"; d?: number }) {
  const delta = b === undefined ? 0 : a - b;
  const good = better === "lower" ? delta < 0 : delta > 0;
  return (
    <div className="rounded-lg border border-slate-200 px-3 py-2">
      <div className="text-[11px] text-slate-500">{label}</div>
      <div className="num text-base font-semibold">{label.includes("Cost") ? fmt.money(a) : fmt.n(a, d)}{unit && <span className="ml-0.5 text-xs font-normal text-slate-500">{unit}</span>}</div>
      {b !== undefined && Math.abs(delta) > 1e-9 && <div className={`num text-[11px] ${good ? "text-emerald-700" : "text-red-700"}`}>{delta > 0 ? "+" : "−"}{label.includes("Cost") ? fmt.money(Math.abs(delta)) : fmt.n(Math.abs(delta), d)} vs current</div>}
    </div>
  );
}

export function DesignStudio({ ctx, params, baseline, initialOptions }: { ctx: Ctx; params: DesignParams; baseline: Evaluation | null; initialOptions: Option[] }) {
  const router = useRouter();
  const toast = useToast();
  const [p, setP] = useState(params);
  const [live, setLive] = useState<Evaluation | null>(baseline);
  const [computing, setComputing] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [options, setOptions] = useState(initialOptions);
  const [objective, setObjective] = useState<Objective>("balanced");
  const [alts, setAlts] = useState<Alt[] | null>(null);
  const [genBusy, setGenBusy] = useState(false);
  const [saveOpen, setSaveOpen] = useState<{ name: string; params: DesignParams; metrics: Record<string, number>; score: number } | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout>>(undefined);
  const dirty = JSON.stringify(p) !== JSON.stringify(params);

  useEffect(() => {
    if (!dirty) { setLive(baseline); setError(""); return; }
    setComputing(true);
    clearTimeout(timer.current);
    timer.current = setTimeout(() => {
      try {
        setLive(evaluate({ projectId: ctx.id, name: ctx.name, code: ctx.code, intake: ctx.intake, params: p, boreholes: ctx.boreholes, standards: ctx.standards, pins: ctx.pins }, p));
        setError("");
      } catch (e) { setError((e as Error).message); }
      setComputing(false);
    }, 250);
    return () => clearTimeout(timer.current);
  }, [p, dirty, baseline, ctx]);

  const metrics = (e: Evaluation) => ({ cost: e.cost, carbon: e.carbon, nla: e.nla, efficiency: e.efficiency, daylight: e.daylight, drift: e.drift, driftLimit: e.driftLimit, eui: e.eui, months: e.months, fails: e.fails, T1: e.T1, clashes: e.clashes });

  async function applyAndRun() {
    setBusy(true);
    try {
      await api(`/api/projects/${ctx.id}`, { method: "PATCH", body: { params: p } });
      await api(`/api/projects/${ctx.id}/run`, { method: "POST" });
      toast({ tone: "success", text: "Scheme regenerated and re-analysed" });
      router.refresh();
    } catch (e) { toast({ tone: "error", text: (e as Error).message }); }
    setBusy(false);
  }

  async function generate() {
    setGenBusy(true);
    try { setAlts(await api<Alt[]>(`/api/projects/${ctx.id}/alternatives`, { body: { objective } })); }
    catch (e) { toast({ tone: "error", text: (e as Error).message }); }
    setGenBusy(false);
  }

  async function saveOption() {
    if (!saveOpen) return;
    const tmp: Option = { id: `tmp-${Date.now()}`, name: saveOpen.name, objective, params: saveOpen.params, metrics: saveOpen.metrics, score: saveOpen.score, notes: null, starred: 0 };
    setOptions((o) => [tmp, ...o]);
    setSaveOpen(null);
    try {
      const { id } = await api<{ id: string }>(`/api/projects/${ctx.id}/options`, { body: { ...tmp } });
      setOptions((o) => o.map((x) => (x.id === tmp.id ? { ...x, id } : x)));
      toast({ tone: "success", text: "Design option saved" });
    } catch (e) {
      setOptions((o) => o.filter((x) => x.id !== tmp.id));
      toast({ tone: "error", text: (e as Error).message });
    }
  }

  async function patchOption(o: Option, patch: Partial<Option>) {
    const prev = options;
    setOptions((x) => x.map((y) => (y.id === o.id ? { ...y, ...patch } : y)));
    try { await api(`/api/options/${o.id}`, { method: "PATCH", body: { ...patch, starred: patch.starred === undefined ? undefined : !!patch.starred } }); }
    catch (e) { setOptions(prev); toast({ tone: "error", text: (e as Error).message }); }
  }
  async function deleteOption(o: Option) {
    const prev = options;
    setOptions((x) => x.filter((y) => y.id !== o.id));
    try { await api(`/api/options/${o.id}`, { method: "DELETE" }); }
    catch (e) { setOptions(prev); toast({ tone: "error", text: (e as Error).message }); }
  }
  async function applyOption(o: Option) {
    setBusy(true);
    try {
      await api(`/api/options/${o.id}/apply`, { method: "POST" });
      toast({ tone: "success", text: `Applied “${o.name}” and re-ran the workflow` });
      setP(o.params);
      router.refresh();
    } catch (e) { toast({ tone: "error", text: (e as Error).message }); }
    setBusy(false);
  }

  const scatter = useMemo(() => (alts ?? []).map((a) => ({ name: a.name, "Cost ($M)": Math.round(a.metrics.cost / 1e5) / 10, "Carbon (kg/m²)": a.metrics.carbon, NLA: a.metrics.nla, pareto: a.pareto ? 1 : 0 })), [alts]);

  return (
    <>
      {busy && <AgentProgress />}
      <div className="grid gap-5 xl:grid-cols-3">
        <Card title="Parametric building generator" subtitle="Drag a parameter — the engine re-solves structure, MEP, cost and carbon in your browser" className="xl:col-span-2"
          action={<div className="flex gap-2">{dirty && <Button size="sm" variant="ghost" onClick={() => setP(params)}>Reset</Button>}<Button size="sm" variant="secondary" disabled={!live} onClick={() => live && setSaveOpen({ name: `Variant ${options.length + 1}`, params: p, metrics: metrics(live), score: 0 })}><Save className="h-3.5 w-3.5" />Save option</Button><Button size="sm" disabled={!dirty} onClick={applyAndRun}><Wand2 className="h-3.5 w-3.5" />Apply & re-run</Button></div>}>
          <div className="grid gap-6 lg:grid-cols-2">
            <div className="space-y-3">
              {SLIDERS.map((s) => (
                <label key={s.key} className="block">
                  <span className="label flex justify-between"><span>{s.label}</span><span className="num text-slate-900">{(p[s.key] as number).toFixed(s.step < 1 ? (s.step < 0.05 ? 2 : 2) : 0)}{s.unit ? ` ${s.unit}` : ""}</span></span>
                  <input type="range" className="w-full accent-brand-600" min={s.min} max={s.max} step={s.step} value={p[s.key] as number} onChange={(e) => setP({ ...p, [s.key]: Number(e.target.value) })} aria-label={s.label} />
                </label>
              ))}
              <div className="grid grid-cols-2 gap-3 pt-1">
                {SELECTS.map((s) => (
                  <label key={s.key} className="block"><span className="label">{s.label}</span>
                    <select className="input py-1.5" value={p[s.key] as string} onChange={(e) => setP({ ...p, [s.key]: e.target.value })}>{s.options.map((o) => <option key={o}>{o}</option>)}</select>
                  </label>
                ))}
              </div>
            </div>
            <div className="space-y-3">
              <div className="relative h-64 rounded-xl bg-gradient-to-b from-slate-50 to-white p-2 ring-1 ring-slate-100">
                <Massing p={p} highlight={dirty} />
                {computing && <div className="absolute right-3 top-3 flex items-center gap-1 rounded-full bg-white px-2 py-1 text-[11px] text-slate-500 shadow"><Loader2 className="h-3 w-3 animate-spin" />solving</div>}
              </div>
              {error && <p className="rounded-lg bg-red-50 px-3 py-2 text-xs text-red-700">{error}</p>}
              {live && (
                <div className="grid grid-cols-2 gap-2">
                  <MetricDelta label="Cost" a={live.cost} b={dirty ? baseline?.cost : undefined} />
                  <MetricDelta label="Embodied carbon" a={live.carbon} b={dirty ? baseline?.carbon : undefined} unit="kg/m²" />
                  <MetricDelta label="Net lettable area" a={live.nla} b={dirty ? baseline?.nla : undefined} unit="m²" better="higher" />
                  <MetricDelta label="Max drift" a={live.drift} b={dirty ? baseline?.drift : undefined} unit={`% (≤ ${live.driftLimit})`} d={2} />
                  <MetricDelta label="EUI" a={live.eui} b={dirty ? baseline?.eui : undefined} unit="kWh/m²" d={1} />
                  <MetricDelta label="Programme" a={live.months} b={dirty ? baseline?.months : undefined} unit="months" />
                  <MetricDelta label="Daylit area" a={live.daylight} b={dirty ? baseline?.daylight : undefined} unit="%" better="higher" />
                  <MetricDelta label="Failing checks" a={live.fails} b={dirty ? baseline?.fails : undefined} />
                </div>
              )}
              {live && <p className="text-[11px] text-slate-500">Resolved system: <b>{live.system}</b> · T₁ {live.T1} s · {live.clashes} clash groups. Agents may resize members to converge.</p>}
            </div>
          </div>
        </Card>

        <Card title="Saved design options" subtitle="Compare, star and apply" pad={false}>
          {options.length === 0 ? <div className="p-4"><EmptyState icon={Sparkles} title="No saved options" body="Save a variant from the generator or the alternatives explorer." /></div> : (
            <ul className="divide-y divide-slate-100">
              {options.map((o) => (
                <li key={o.id} className="px-4 py-3">
                  <div className="flex items-start gap-2">
                    <button onClick={() => patchOption(o, { starred: o.starred ? 0 : 1 })} aria-label={o.starred ? "Unstar" : "Star"} className="mt-0.5"><Star className={`h-4 w-4 ${o.starred ? "fill-amber-400 text-amber-500" : "text-slate-300 hover:text-slate-500"}`} /></button>
                    <div className="min-w-0 flex-1">
                      <input className="w-full truncate bg-transparent text-sm font-medium outline-none focus:ring-1 focus:ring-brand-300" defaultValue={o.name} onBlur={(e) => e.target.value !== o.name && patchOption(o, { name: e.target.value })} aria-label="Option name" />
                      <div className="mt-1 flex flex-wrap gap-1"><Badge>{o.params.material}</Badge><Badge>{o.params.lateralSystem}</Badge><Badge>{o.params.slabSystem}</Badge></div>
                      <div className="num mt-1.5 grid grid-cols-3 gap-1 text-[11px] text-slate-600">
                        <span>{fmt.money(o.metrics.cost ?? 0)}</span><span>{o.metrics.carbon ?? "—"} kg/m²</span><span>{fmt.n(o.metrics.nla ?? 0)} m²</span>
                      </div>
                      {o.notes && <div className="mt-1 text-[11px] text-slate-500">{o.notes}</div>}
                    </div>
                  </div>
                  <div className="mt-2 flex justify-end gap-1">
                    <Button size="sm" variant="ghost" onClick={() => setP(o.params)}>Preview</Button>
                    <Button size="sm" variant="secondary" disabled={o.id.startsWith("tmp")} onClick={() => applyOption(o)}><Check className="h-3.5 w-3.5" />Apply</Button>
                    <Button size="sm" variant="ghost" onClick={() => deleteOption(o)} aria-label="Delete option"><Trash2 className="h-3.5 w-3.5 text-red-600" /></Button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>

      <Card title="Design alternatives generator" subtitle="Eight structural/façade concepts solved with the full engine and ranked by your objective"
        action={<div className="flex flex-wrap items-center gap-2"><Segmented value={objective} onChange={setObjective} options={(["balanced", "cost", "carbon", "area", "daylight", "structure", "speed"] as Objective[]).map((v) => ({ value: v, label: v[0].toUpperCase() + v.slice(1) }))} /><Button size="sm" onClick={generate} loading={genBusy}>{!genBusy && <Sparkles className="h-3.5 w-3.5" />}Generate</Button></div>}>
        {!alts ? (
          genBusy ? <div className="flex h-40 items-center justify-center text-sm text-slate-500"><Loader2 className="mr-2 h-4 w-4 animate-spin" />Solving eight concepts…</div>
            : <EmptyState icon={Sparkles} title="Explore alternatives" body="Pick an objective and generate: each concept is analysed for structure, compliance, cost, carbon, daylight and programme." />
        ) : (
          <div className="grid gap-5 lg:grid-cols-5">
            <div className="lg:col-span-2">
              <ScatterViz data={scatter} x="Cost ($M)" y="Carbon (kg/m²)" z="NLA" xLabel="Cost ($M)" yLabel="Embodied carbon (kg/m²)" highlight={(r) => r.pareto === 1} />
              <p className="text-[11px] text-slate-500"><span className="mr-1 inline-block h-2 w-2 rounded-full bg-[#2a78d6]" />Pareto-optimal (no other concept is both cheaper and lower-carbon) · bubble size = NLA</p>
            </div>
            <div className="space-y-2 lg:col-span-3">
              {alts.map((a, i) => (
                <div key={a.name} className={`flex flex-wrap items-center gap-3 rounded-lg border px-3 py-2 ${i === 0 ? "border-brand-300 bg-brand-50/40" : "border-slate-200"}`}>
                  <div className="num w-10 text-center text-lg font-semibold text-slate-900">{a.score}</div>
                  <div className="min-w-[160px] flex-1">
                    <div className="flex items-center gap-1.5 text-sm font-medium">{a.name}{a.pareto && <Badge tone="blue">Pareto</Badge>}{a.metrics.drift > a.metrics.driftLimit && <Badge tone="red">drift fails</Badge>}</div>
                    <div className="num text-[11px] text-slate-500">{fmt.money(a.metrics.cost)} · {a.metrics.carbon} kg/m² · NLA {fmt.n(a.metrics.nla)} m² · drift {a.metrics.drift}% · {a.metrics.months} mo · {a.metrics.fails} fails</div>
                  </div>
                  <Button size="sm" variant="ghost" onClick={() => setP(a.params)}>Preview</Button>
                  <Button size="sm" variant="secondary" onClick={() => setSaveOpen({ name: a.name, params: a.params, metrics: a.metrics, score: a.score })}><Save className="h-3.5 w-3.5" />Save</Button>
                </div>
              ))}
            </div>
          </div>
        )}
      </Card>

      <Modal open={!!saveOpen} onClose={() => setSaveOpen(null)} title="Save design option" footer={<><Button variant="secondary" onClick={() => setSaveOpen(null)}>Cancel</Button><Button onClick={saveOption}>Save</Button></>}>
        <label className="block"><span className="label">Option name</span><input className="input" autoFocus value={saveOpen?.name ?? ""} onChange={(e) => saveOpen && setSaveOpen({ ...saveOpen, name: e.target.value })} /></label>
      </Modal>
    </>
  );
}
