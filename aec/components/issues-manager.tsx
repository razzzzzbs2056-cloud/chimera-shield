"use client";

import { CheckCircle2, MessageSquarePlus, Trash2 } from "lucide-react";
import { useState } from "react";
import { api, Badge, Button, EmptyState, Field, fmt, Modal, Segmented, severityTone, useToast } from "./ui";

export interface Issue { id: string; key: string | null; type: string; severity: string; title: string; detail: string | null; discipline: string | null; location: string | null; status: string; assignee: string | null; updated_at: string }

const STATUSES = ["open", "in-review", "resolved"];

export function IssuesManager({ projectId, initial }: { projectId: string; initial: Issue[] }) {
  const [items, setItems] = useState(initial);
  const [filter, setFilter] = useState<"active" | "physical" | "semantic" | "rfi" | "resolved">("active");
  const [create, setCreate] = useState(false);
  const [draft, setDraft] = useState({ title: "", detail: "", severity: "minor", discipline: "Structural", location: "", assignee: "" });
  const [saving, setSaving] = useState(false);
  const toast = useToast();

  const shown = items.filter((i) => (filter === "active" ? i.status !== "resolved" : filter === "resolved" ? i.status === "resolved" : i.type === filter && i.status !== "resolved"));

  async function patch(i: Issue, p: Partial<Issue>) {
    const prev = items;
    setItems((x) => x.map((y) => (y.id === i.id ? { ...y, ...p } : y)));
    try { await api(`/api/issues/${i.id}`, { method: "PATCH", body: p }); }
    catch (e) { setItems(prev); toast({ tone: "error", text: (e as Error).message }); }
  }
  async function remove(i: Issue) {
    const prev = items;
    setItems((x) => x.filter((y) => y.id !== i.id));
    try { await api(`/api/issues/${i.id}`, { method: "DELETE" }); }
    catch (e) { setItems(prev); toast({ tone: "error", text: (e as Error).message }); }
  }
  async function submit() {
    if (!draft.title.trim()) return;
    setSaving(true);
    const tmp: Issue = { id: `tmp-${Date.now()}`, key: null, type: "rfi", status: "open", updated_at: new Date().toISOString(), ...draft };
    setItems((x) => [tmp, ...x]);
    setCreate(false);
    try {
      const { id } = await api<{ id: string }>(`/api/projects/${projectId}/issues`, { body: draft });
      setItems((x) => x.map((y) => (y.id === tmp.id ? { ...y, id } : y)));
      setDraft({ title: "", detail: "", severity: "minor", discipline: "Structural", location: "", assignee: "" });
      toast({ tone: "success", text: "RFI raised" });
    } catch (e) {
      setItems((x) => x.filter((y) => y.id !== tmp.id));
      toast({ tone: "error", text: (e as Error).message });
    }
    setSaving(false);
  }

  const count = (f: typeof filter) => items.filter((i) => (f === "active" ? i.status !== "resolved" : f === "resolved" ? i.status === "resolved" : i.type === f && i.status !== "resolved")).length;

  return (
    <div className="card">
      <div className="flex flex-wrap items-center gap-2 border-b border-slate-100 p-3">
        <Segmented value={filter} onChange={setFilter} options={[{ value: "active", label: `Active ${count("active")}` }, { value: "physical", label: `Physical ${count("physical")}` }, { value: "semantic", label: `Semantic ${count("semantic")}` }, { value: "rfi", label: `RFIs ${count("rfi")}` }, { value: "resolved", label: `Resolved ${count("resolved")}` }]} />
        <Button size="sm" className="ml-auto" onClick={() => setCreate(true)}><MessageSquarePlus className="h-3.5 w-3.5" />Raise RFI</Button>
      </div>
      {shown.length === 0 ? <div className="p-4"><EmptyState icon={CheckCircle2} title="Nothing here" body={filter === "resolved" ? "Resolved issues will appear here." : "No open issues in this category — coordination is clean."} /></div> : (
        <ul className="divide-y divide-slate-100">
          {shown.map((i) => (
            <li key={i.id} className="px-4 py-3">
              <div className="flex flex-wrap items-start gap-2">
                <Badge tone={severityTone(i.severity)}>{i.severity}</Badge>
                <Badge tone={i.type === "semantic" ? "violet" : i.type === "rfi" ? "blue" : "slate"}>{i.type === "rfi" ? "RFI" : i.type}</Badge>
                <div className="min-w-0 flex-1">
                  <div className="text-sm font-medium text-slate-900">{i.title}</div>
                  {i.detail && <p className="mt-0.5 text-xs text-slate-600">{i.detail}</p>}
                  <div className="mt-1 text-[11px] text-slate-400">{[i.discipline, i.location, i.assignee && i.assignee !== "auto" ? `@${i.assignee}` : i.assignee === "auto" ? "auto-resolved by re-run" : null, fmt.date(i.updated_at)].filter(Boolean).join(" · ")}</div>
                </div>
                <select className="input w-32 py-1 text-xs" value={i.status} onChange={(e) => patch(i, { status: e.target.value })} aria-label="Issue status">{STATUSES.map((s) => <option key={s}>{s}</option>)}</select>
                <input className="input w-28 py-1 text-xs" placeholder="Assignee" defaultValue={i.assignee && i.assignee !== "auto" ? i.assignee : ""} onBlur={(e) => e.target.value !== (i.assignee ?? "") && patch(i, { assignee: e.target.value })} aria-label="Assignee" />
                <button onClick={() => remove(i)} className="rounded p-1 text-slate-400 hover:text-red-600" aria-label="Delete issue"><Trash2 className="h-4 w-4" /></button>
              </div>
            </li>
          ))}
        </ul>
      )}
      <Modal open={create} onClose={() => setCreate(false)} title="Raise an RFI / coordination issue" footer={<><Button variant="secondary" onClick={() => setCreate(false)}>Cancel</Button><Button onClick={submit} loading={saving} disabled={!draft.title.trim()}>Create</Button></>}>
        <div className="space-y-3">
          <Field label="Title"><input className="input" value={draft.title} onChange={(e) => setDraft({ ...draft, title: e.target.value })} autoFocus /></Field>
          <Field label="Detail"><textarea className="input min-h-[90px]" value={draft.detail} onChange={(e) => setDraft({ ...draft, detail: e.target.value })} /></Field>
          <div className="grid grid-cols-2 gap-3">
            <Field label="Severity"><select className="input" value={draft.severity} onChange={(e) => setDraft({ ...draft, severity: e.target.value })}>{["critical", "major", "minor"].map((s) => <option key={s}>{s}</option>)}</select></Field>
            <Field label="Discipline"><select className="input" value={draft.discipline} onChange={(e) => setDraft({ ...draft, discipline: e.target.value })}>{["Architecture", "Structural", "Mechanical", "Electrical", "Hydraulics", "Fire", "Façade", "Civil", "Coordination"].map((s) => <option key={s}>{s}</option>)}</select></Field>
            <Field label="Location"><input className="input" value={draft.location} onChange={(e) => setDraft({ ...draft, location: e.target.value })} placeholder="e.g. L12 grid C/4" /></Field>
            <Field label="Assignee"><input className="input" value={draft.assignee} onChange={(e) => setDraft({ ...draft, assignee: e.target.value })} /></Field>
          </div>
        </div>
      </Modal>
    </div>
  );
}
