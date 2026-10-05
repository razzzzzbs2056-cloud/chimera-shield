"use client";

import { BookOpen, Pencil, Plus, Search, Trash2 } from "lucide-react";
import { useMemo, useState } from "react";
import type { StandardRef } from "@/lib/engine/types";
import { api, Badge, Button, EmptyState, Field, Modal, useToast } from "./ui";

type Std = StandardRef & { id: string };
const blank: Std = { id: "", code: "", title: "", jurisdiction: "US", discipline: "Structural", edition: "", year: new Date().getFullYear(), status: "current", supersededBy: null };

export function StandardsManager({ initial }: { initial: Std[] }) {
  const [items, setItems] = useState(initial);
  const [j, setJ] = useState("all");
  const [q, setQ] = useState("");
  const [edit, setEdit] = useState<Std | null>(null);
  const [confirm, setConfirm] = useState<Std | null>(null);
  const toast = useToast();
  const jur = useMemo(() => [...new Set(items.map((s) => s.jurisdiction))].sort(), [items]);
  const shown = items.filter((s) => (j === "all" || s.jurisdiction === j) && `${s.code} ${s.title} ${s.edition}`.toLowerCase().includes(q.toLowerCase()));
  const families = [...new Set(shown.map((s) => `${s.jurisdiction}|${s.code}`))];

  async function save() {
    if (!edit) return;
    const isNew = !edit.id;
    const prev = items;
    const tmpId = `tmp-${Date.now()}`;
    let next = isNew ? [...items, { ...edit, id: tmpId }] : items.map((s) => (s.id === edit.id ? edit : s));
    // version control: marking a new edition current supersedes the previous current edition of the same family
    if (edit.status === "current") next = next.map((s) => (s.code === edit.code && s.jurisdiction === edit.jurisdiction && s.id !== (isNew ? tmpId : edit.id) && s.status === "current" ? { ...s, status: "superseded", supersededBy: edit.edition } : s));
    setItems(next);
    const draft = edit;
    setEdit(null);
    try {
      if (isNew) {
        const { id } = await api<{ id: string }>("/api/standards", { body: draft });
        setItems((x) => x.map((s) => (s.id === tmpId ? { ...s, id } : s)));
      } else await api(`/api/standards/${draft.id}`, { method: "PATCH", body: draft });
      const superseded = next.filter((s) => prev.find((p) => p.id === s.id && p.status !== s.status));
      for (const s of superseded) await api(`/api/standards/${s.id}`, { method: "PATCH", body: { status: "superseded", supersededBy: draft.edition } });
      toast({ tone: "success", text: superseded.length ? `Saved — ${superseded.length} older edition(s) marked superseded` : "Standard saved" });
    } catch (e) { setItems(prev); toast({ tone: "error", text: (e as Error).message }); }
  }
  async function remove(s: Std) {
    setConfirm(null);
    const prev = items;
    setItems((x) => x.filter((y) => y.id !== s.id));
    try { await api(`/api/standards/${s.id}`, { method: "DELETE" }); }
    catch (e) { setItems(prev); toast({ tone: "error", text: (e as Error).message }); }
  }

  return (
    <>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative flex-1"><Search className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-slate-400" /><input className="input pl-9" placeholder="Search standards…" value={q} onChange={(e) => setQ(e.target.value)} aria-label="Search standards" /></div>
        <select className="input sm:w-44" value={j} onChange={(e) => setJ(e.target.value)} aria-label="Jurisdiction"><option value="all">All jurisdictions</option>{jur.map((x) => <option key={x}>{x}</option>)}</select>
        <Button onClick={() => setEdit({ ...blank })}><Plus className="h-4 w-4" />Add edition</Button>
      </div>
      {shown.length === 0 ? <EmptyState icon={BookOpen} title="No standards found" body="Add a code edition, or clear the filters." /> : (
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {families.map((f) => {
            const [jj, code] = f.split("|");
            const eds = shown.filter((s) => s.jurisdiction === jj && s.code === code).sort((a, b) => b.year - a.year);
            return (
              <div key={f} className="card p-4">
                <div className="flex items-start justify-between gap-2"><div><div className="font-semibold">{code}</div><div className="text-xs text-slate-500">{eds[0].title}</div></div><Badge>{jj}</Badge></div>
                <ul className="mt-3 space-y-1.5">
                  {eds.map((s) => (
                    <li key={s.id} className="group flex items-center gap-2 text-sm">
                      <span className="num font-medium">{s.edition}</span>
                      <Badge tone={s.status === "current" ? "green" : s.status === "superseded" ? "red" : "amber"}>{s.status === "draft" ? "pending" : s.status}</Badge>
                      {s.supersededBy && <span className="text-[11px] text-slate-400">→ {s.supersededBy}</span>}
                      <span className="ml-auto flex gap-1 opacity-60 group-hover:opacity-100">
                        <button onClick={() => setEdit({ ...s })} className="rounded p-1 hover:bg-slate-100" aria-label={`Edit ${s.code} ${s.edition}`}><Pencil className="h-3.5 w-3.5" /></button>
                        <button onClick={() => setConfirm(s)} className="rounded p-1 text-red-600 hover:bg-red-50" aria-label={`Delete ${s.code} ${s.edition}`}><Trash2 className="h-3.5 w-3.5" /></button>
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </div>
      )}
      <Modal open={!!edit} onClose={() => setEdit(null)} title={edit?.id ? "Edit edition" : "Add code edition"} footer={<><Button variant="secondary" onClick={() => setEdit(null)}>Cancel</Button><Button onClick={save} disabled={!edit?.code || !edit?.edition}>Save</Button></>}>
        {edit && (
          <div className="grid grid-cols-2 gap-3">
            <Field label="Code family"><input className="input" value={edit.code} onChange={(e) => setEdit({ ...edit, code: e.target.value })} placeholder="ASCE 7" /></Field>
            <Field label="Edition"><input className="input" value={edit.edition} onChange={(e) => setEdit({ ...edit, edition: e.target.value })} placeholder="7-22" /></Field>
            <Field label="Title" className="col-span-2"><input className="input" value={edit.title} onChange={(e) => setEdit({ ...edit, title: e.target.value })} /></Field>
            <Field label="Jurisdiction"><select className="input" value={edit.jurisdiction} onChange={(e) => setEdit({ ...edit, jurisdiction: e.target.value })}>{["US", "UK", "AU", "NZ", "SG", "CA", "INT"].map((x) => <option key={x}>{x}</option>)}</select></Field>
            <Field label="Discipline"><select className="input" value={edit.discipline} onChange={(e) => setEdit({ ...edit, discipline: e.target.value })}>{["General", "Structural", "Geotechnical", "Fire", "Mechanical", "Electrical", "Hydraulics", "Energy", "Accessibility"].map((x) => <option key={x}>{x}</option>)}</select></Field>
            <Field label="Year"><input className="input num" type="number" value={edit.year} onChange={(e) => setEdit({ ...edit, year: +e.target.value })} /></Field>
            <Field label="Status" hint="Setting “current” supersedes the previous current edition"><select className="input" value={edit.status} onChange={(e) => setEdit({ ...edit, status: e.target.value as Std["status"] })}><option value="current">current (adopted)</option><option value="superseded">superseded</option><option value="draft">pending adoption</option></select></Field>
          </div>
        )}
      </Modal>
      <Modal open={!!confirm} onClose={() => setConfirm(null)} title="Delete edition?" footer={<><Button variant="secondary" onClick={() => setConfirm(null)}>Cancel</Button><Button variant="danger" onClick={() => confirm && remove(confirm)}>Delete</Button></>}>
        <p className="text-sm text-slate-600">Remove <b>{confirm?.code} {confirm?.edition}</b> from the library? Projects using it will fall back to the current edition on their next run.</p>
      </Modal>
    </>
  );
}
