"use client";

import { Activity, Plus, Trash2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import type { AssetHealth } from "@/lib/engine/operations";
import { LineViz } from "./charts";
import { api, Badge, Button, EmptyState, Field, Modal, useToast } from "./ui";

type Row = AssetHealth & { install_date: string; runtime_hours: number; criticality: number };
const TYPES = ["chiller", "ahu", "pump", "lift", "boiler", "transformer", "facade", "structure", "generator"];
const tone = (s: string) => (s === "action" ? "red" : s === "watch" ? "amber" : "green") as "red" | "amber" | "green";

export function AssetRegister({ projectId, initial }: { projectId: string; initial: Row[] }) {
  const [items, setItems] = useState(initial);
  const [sel, setSel] = useState<Row | null>([...initial].sort((a, b) => b.risk - a.risk)[0] ?? null);
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState({ name: "", system: "HVAC", type: "pump", install_date: new Date().toISOString().slice(0, 10), condition: 4, runtime_hours: 0, criticality: 0.6, location: "" });
  const [saving, setSaving] = useState(false);
  const toast = useToast();
  const router = useRouter();

  async function add() {
    setSaving(true);
    try {
      const { id, health } = await api<{ id: string; health: AssetHealth }>(`/api/projects/${projectId}/assets`, { body: draft });
      const row: Row = { ...health, install_date: draft.install_date, runtime_hours: draft.runtime_hours, criticality: draft.criticality, id };
      setItems((x) => [...x, row]);
      setSel(row);
      setOpen(false);
      toast({ tone: "success", text: `${draft.name} registered in the digital twin` });
      router.refresh();
    } catch (e) { toast({ tone: "error", text: (e as Error).message }); }
    setSaving(false);
  }
  async function setCondition(a: Row, condition: number) {
    const prev = items;
    setItems((x) => x.map((y) => (y.id === a.id ? { ...y, condition } : y)));
    try { await api(`/api/assets/${a.id}`, { method: "PATCH", body: { condition } }); router.refresh(); }
    catch (e) { setItems(prev); toast({ tone: "error", text: (e as Error).message }); }
  }
  async function remove(a: Row) {
    const prev = items;
    setItems((x) => x.filter((y) => y.id !== a.id));
    if (sel?.id === a.id) setSel(null);
    try { await api(`/api/assets/${a.id}`, { method: "DELETE" }); router.refresh(); }
    catch (e) { setItems(prev); toast({ tone: "error", text: (e as Error).message }); }
  }

  return (
    <div className="grid gap-4 xl:grid-cols-5">
      <div className="card xl:col-span-3">
        <div className="flex items-center justify-between border-b border-slate-100 px-4 py-3">
          <div><h3 className="text-sm font-semibold">Asset register & predictive maintenance</h3><p className="text-xs text-slate-500">Weibull reliability adjusted by condition and runtime</p></div>
          <Button size="sm" onClick={() => setOpen(true)}><Plus className="h-3.5 w-3.5" />Add asset</Button>
        </div>
        {items.length === 0 ? <div className="p-4"><EmptyState icon={Activity} title="No assets registered" body="Register plant and systems to start condition monitoring and maintenance forecasting." action={<Button onClick={() => setOpen(true)}>Add first asset</Button>} /></div> : (
          <div className="scrollbar-thin overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50/70"><tr>{["Asset", "Health", "P(fail) 90 d", "RUL", "Next service", "Condition", ""].map((h) => <th key={h} className="th">{h}</th>)}</tr></thead>
              <tbody className="divide-y divide-slate-100">
                {[...items].sort((a, b) => b.risk - a.risk).map((a) => (
                  <tr key={a.id} onClick={() => setSel(a)} className={`cursor-pointer hover:bg-slate-50 ${sel?.id === a.id ? "bg-brand-50/50" : ""}`}>
                    <td className="td"><div className="font-medium text-slate-900">{a.name}</div><div className="text-[11px] text-slate-500">{a.system} · {a.location}</div></td>
                    <td className="td"><Badge tone={tone(a.status)}>{a.health} · {a.status}</Badge></td>
                    <td className="td num">{a.pf90}%</td><td className="td num">{a.rul > 3650 ? "> 10 yr" : `${a.rul} d`}</td><td className="td num">{a.nextService}</td>
                    <td className="td" onClick={(e) => e.stopPropagation()}>
                      <select className="input w-20 py-1 text-xs" value={a.condition} onChange={(e) => setCondition(a, +e.target.value)} aria-label="Condition score">{[1, 2, 3, 4, 5].map((c) => <option key={c} value={c}>{c} / 5</option>)}</select>
                    </td>
                    <td className="td" onClick={(e) => e.stopPropagation()}><button onClick={() => remove(a)} className="rounded p-1 text-slate-400 hover:text-red-600" aria-label={`Delete ${a.name}`}><Trash2 className="h-4 w-4" /></button></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
      <div className="card xl:col-span-2">
        <div className="border-b border-slate-100 px-4 py-3"><h3 className="text-sm font-semibold">{sel ? sel.name : "Select an asset"}</h3><p className="text-xs text-slate-500">{sel ? `${sel.metric} — last 60 days, ${sel.anomalies} anomalies` : "Sensor trend & anomaly detection"}</p></div>
        <div className="p-4">
          {sel ? <LineViz data={sel.series.map((s) => ({ day: s.t, [sel.metric]: s.v, Alarm: s.limit }))} x="day" series={[{ key: sel.metric }, { key: "Alarm", color: "#b91c1c" }]} height={240} /> : <p className="py-10 text-center text-sm text-slate-500">Click an asset to view its sensor history.</p>}
          {sel && <p className="mt-2 text-xs text-slate-600">Risk index {sel.risk} (P(fail) × criticality). Recommended service by <b>{sel.nextService}</b>.</p>}
        </div>
      </div>
      <Modal open={open} onClose={() => setOpen(false)} title="Register asset" footer={<><Button variant="secondary" onClick={() => setOpen(false)}>Cancel</Button><Button onClick={add} loading={saving} disabled={!draft.name.trim()}>Register</Button></>}>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Name" className="col-span-2"><input className="input" value={draft.name} onChange={(e) => setDraft({ ...draft, name: e.target.value })} autoFocus /></Field>
          <Field label="Type"><select className="input" value={draft.type} onChange={(e) => setDraft({ ...draft, type: e.target.value })}>{TYPES.map((t) => <option key={t}>{t}</option>)}</select></Field>
          <Field label="System"><input className="input" value={draft.system} onChange={(e) => setDraft({ ...draft, system: e.target.value })} /></Field>
          <Field label="Install date"><input className="input" type="date" value={draft.install_date} onChange={(e) => setDraft({ ...draft, install_date: e.target.value })} /></Field>
          <Field label="Runtime hours"><input className="input num" type="number" value={draft.runtime_hours} onChange={(e) => setDraft({ ...draft, runtime_hours: +e.target.value })} /></Field>
          <Field label="Condition (1–5)"><input className="input num" type="number" min={1} max={5} value={draft.condition} onChange={(e) => setDraft({ ...draft, condition: +e.target.value })} /></Field>
          <Field label="Criticality (0–1)"><input className="input num" type="number" step={0.1} min={0} max={1} value={draft.criticality} onChange={(e) => setDraft({ ...draft, criticality: +e.target.value })} /></Field>
          <Field label="Location" className="col-span-2"><input className="input" value={draft.location} onChange={(e) => setDraft({ ...draft, location: e.target.value })} /></Field>
        </div>
      </Modal>
    </div>
  );
}
