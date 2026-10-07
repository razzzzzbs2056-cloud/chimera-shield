"use client";

import { Copy, KeyRound, Plus, Trash2 } from "lucide-react";
import { useState } from "react";
import { api, Button, Card, EmptyState, fmt, Modal, useToast } from "./ui";

type Key = { id: string; name: string; prefix: string; runs: number; month: string | null; month_runs: number; last_used_at: string | null; created_at: string };

export function ApiKeys({ initial, limit }: { initial: Key[]; limit: number }) {
  const [keys, setKeys] = useState(initial);
  const [name, setName] = useState("");
  const [secret, setSecret] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const toast = useToast();
  const month = new Date().toISOString().slice(0, 7);

  async function create() {
    setBusy(true);
    try {
      const k = await api<{ id: string; secret: string }>("/api/keys", { body: { name: name || "API key" } });
      setKeys((x) => [{ id: k.id, name: name || "API key", prefix: k.secret.slice(0, 14), runs: 0, month: null, month_runs: 0, last_used_at: null, created_at: new Date().toISOString() }, ...x]);
      setSecret(k.secret);
      setName("");
    } catch (e) { toast({ tone: "error", text: (e as Error).message }); }
    setBusy(false);
  }
  async function revoke(k: Key) {
    const prev = keys;
    setKeys((x) => x.filter((y) => y.id !== k.id));
    try { await api(`/api/keys/${k.id}`, { method: "DELETE" }); toast({ tone: "success", text: `Revoked ${k.name}` }); }
    catch (e) { setKeys(prev); toast({ tone: "error", text: (e as Error).message }); }
  }

  return (
    <Card title="API keys" subtitle={`Sell or embed the agents through POST /api/v1/analyze · ${limit.toLocaleString()} runs per key per month`} action={<KeyRound className="h-4 w-4 text-slate-400" />}>
      <form onSubmit={(e) => { e.preventDefault(); create(); }} className="flex gap-2">
        <input className="input" placeholder="Key name, e.g. Procore integration" value={name} onChange={(e) => setName(e.target.value)} aria-label="Key name" />
        <Button type="submit" loading={busy}><Plus className="h-4 w-4" />Create</Button>
      </form>
      <div className="mt-4">
        {keys.length === 0 ? <EmptyState icon={KeyRound} title="No API keys" body="Create a key to call the agents from your own software, a partner platform or the Claude Skill." /> : (
          <ul className="divide-y divide-slate-100 rounded-lg border border-slate-200">
            {keys.map((k) => (
              <li key={k.id} className="flex flex-wrap items-center gap-3 px-3 py-2.5">
                <div className="min-w-0 flex-1">
                  <div className="text-sm font-medium">{k.name}</div>
                  <div className="font-mono text-[11px] text-slate-500">{k.prefix}…</div>
                </div>
                <div className="text-right text-xs text-slate-500"><div className="num">{k.month === month ? k.month_runs : 0} / {limit.toLocaleString()} this month</div><div>{k.last_used_at ? `last used ${fmt.date(k.last_used_at)}` : "never used"}</div></div>
                <button onClick={() => revoke(k)} className="rounded p-1 text-slate-400 hover:text-red-600" aria-label={`Revoke ${k.name}`}><Trash2 className="h-4 w-4" /></button>
              </li>
            ))}
          </ul>
        )}
      </div>
      <Modal open={!!secret} onClose={() => setSecret(null)} title="Copy your API key" footer={<Button onClick={() => setSecret(null)}>Done</Button>}>
        <p className="text-sm text-slate-600">This is the only time the key is shown. Store it in a secrets manager.</p>
        <div className="mt-3 flex items-center gap-2 rounded-lg bg-slate-950 px-3 py-2">
          <code className="flex-1 break-all text-xs text-emerald-300">{secret}</code>
          <button onClick={() => { navigator.clipboard?.writeText(secret ?? ""); toast({ tone: "success", text: "Copied" }); }} className="rounded p-1 text-slate-300 hover:bg-white/10" aria-label="Copy key"><Copy className="h-4 w-4" /></button>
        </div>
      </Modal>
    </Card>
  );
}
