"use client";

import { Drill, Pencil, Plus, Trash2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import type { BoreholeLayer, SoilType } from "@/lib/engine/types";
import { api, Badge, Button, EmptyState, Modal, useToast } from "./ui";

type BH = { id: string; name: string; x: number; y: number; gwl: number; layers: BoreholeLayer[] };
const SOILS: SoilType[] = ["fill", "clay", "silt", "sand", "gravel", "rock"];
const blankLayer = (top: number): BoreholeLayer => ({ top, bottom: top + 5, soil: "sand", spt: 20, gamma: 19, phi: 32, Es: 30 });

export function BoreholeManager({ projectId, initial }: { projectId: string; initial: BH[] }) {
  const [items, setItems] = useState(initial);
  const [edit, setEdit] = useState<BH | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const toast = useToast();
  const router = useRouter();

  function open(b?: BH) {
    setError("");
    setEdit(b ? structuredClone(b) : { id: "", name: `BH-${String(items.length + 1).padStart(2, "0")}`, x: 0, y: 0, gwl: 5, layers: [blankLayer(0)] });
  }

  async function save() {
    if (!edit) return;
    setSaving(true); setError("");
    try {
      if (edit.id) {
        await api(`/api/boreholes/${edit.id}`, { method: "PATCH", body: edit });
        setItems((x) => x.map((y) => (y.id === edit.id ? edit : y)));
      } else {
        const { id } = await api<{ id: string }>(`/api/projects/${projectId}/boreholes`, { body: edit });
        setItems((x) => [...x, { ...edit, id }]);
      }
      setEdit(null);
      toast({ tone: "success", text: "Borehole saved — re-run the workflow to update geotechnical results" });
      router.refresh();
    } catch (e) { setError((e as Error).message); }
    setSaving(false);
  }

  async function remove(b: BH) {
    const prev = items;
    setItems((x) => x.filter((y) => y.id !== b.id));
    try { await api(`/api/boreholes/${b.id}`, { method: "DELETE" }); toast({ tone: "success", text: `Deleted ${b.name}` }); router.refresh(); }
    catch (e) { setItems(prev); toast({ tone: "error", text: (e as Error).message }); }
  }

  const setLayer = (i: number, patch: Partial<BoreholeLayer>) => edit && setEdit({ ...edit, layers: edit.layers.map((l, k) => (k === i ? { ...l, ...patch } : l)) });

  return (
    <>
      {items.length === 0 ? (
        <EmptyState icon={Drill} title="No borehole logs" body="Add borehole or CPT logs — the geotechnical agent derives Vs30, site class, bearing, settlement and liquefaction from them." action={<Button onClick={() => open()}><Plus className="h-4 w-4" />Add borehole</Button>} />
      ) : (
        <div className="space-y-2">
          {items.map((b) => (
            <div key={b.id} className="flex flex-wrap items-center gap-3 rounded-lg border border-slate-200 px-3 py-2">
              <Drill className="h-4 w-4 text-slate-400" />
              <div className="min-w-0 flex-1">
                <div className="text-sm font-medium">{b.name} <span className="text-xs font-normal text-slate-500">({b.x}, {b.y}) · GWL {b.gwl} m · to {Math.max(...b.layers.map((l) => l.bottom))} m</span></div>
                <div className="mt-1 flex flex-wrap gap-1">{b.layers.map((l, i) => <Badge key={i}>{l.top}–{l.bottom} m {l.soil} N{l.spt}</Badge>)}</div>
              </div>
              <Button size="sm" variant="ghost" onClick={() => open(b)} aria-label={`Edit ${b.name}`}><Pencil className="h-3.5 w-3.5" /></Button>
              <Button size="sm" variant="ghost" onClick={() => remove(b)} aria-label={`Delete ${b.name}`}><Trash2 className="h-3.5 w-3.5 text-red-600" /></Button>
            </div>
          ))}
          <Button size="sm" variant="secondary" onClick={() => open()}><Plus className="h-3.5 w-3.5" />Add borehole</Button>
        </div>
      )}
      <Modal open={!!edit} onClose={() => setEdit(null)} title={edit?.id ? `Edit ${edit.name}` : "New borehole log"} wide
        footer={<><Button variant="secondary" onClick={() => setEdit(null)}>Cancel</Button><Button onClick={save} loading={saving}>Save borehole</Button></>}>
        {edit && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              <label><span className="label">Name</span><input className="input" value={edit.name} onChange={(e) => setEdit({ ...edit, name: e.target.value })} /></label>
              <label><span className="label">X (m)</span><input className="input num" type="number" value={edit.x} onChange={(e) => setEdit({ ...edit, x: +e.target.value })} /></label>
              <label><span className="label">Y (m)</span><input className="input num" type="number" value={edit.y} onChange={(e) => setEdit({ ...edit, y: +e.target.value })} /></label>
              <label><span className="label">Groundwater (m bgl)</span><input className="input num" type="number" step={0.1} value={edit.gwl} onChange={(e) => setEdit({ ...edit, gwl: +e.target.value })} /></label>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full text-xs">
                <thead><tr>{["Top", "Bottom", "Soil", "SPT N", "γ kN/m³", "cu kPa", "φ °", "Es MPa", "Cc", "e₀", "Fines %", ""].map((h) => <th key={h} className="th">{h}</th>)}</tr></thead>
                <tbody>
                  {edit.layers.map((l, i) => (
                    <tr key={i}>
                      {(["top", "bottom"] as const).map((k) => <td key={k} className="p-1"><input className="input w-16 px-2 py-1 num" type="number" step={0.5} value={l[k]} onChange={(e) => setLayer(i, { [k]: +e.target.value })} /></td>)}
                      <td className="p-1"><select className="input w-24 px-2 py-1" value={l.soil} onChange={(e) => setLayer(i, { soil: e.target.value as SoilType })}>{SOILS.map((s) => <option key={s}>{s}</option>)}</select></td>
                      {(["spt", "gamma", "cu", "phi", "Es", "cc", "e0", "finesPct"] as const).map((k) => <td key={k} className="p-1"><input className="input w-16 px-2 py-1 num" type="number" step="any" value={l[k] ?? ""} placeholder="—" onChange={(e) => setLayer(i, { [k]: e.target.value === "" ? undefined : +e.target.value })} /></td>)}
                      <td className="p-1"><button className="rounded p-1 text-slate-400 hover:text-red-600" onClick={() => setEdit({ ...edit, layers: edit.layers.filter((_, k) => k !== i) })} aria-label="Remove layer"><Trash2 className="h-3.5 w-3.5" /></button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <Button size="sm" variant="secondary" onClick={() => setEdit({ ...edit, layers: [...edit.layers, blankLayer(Math.max(0, ...edit.layers.map((l) => l.bottom)))] })}><Plus className="h-3.5 w-3.5" />Add layer</Button>
            {error && <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
          </div>
        )}
      </Modal>
    </>
  );
}
