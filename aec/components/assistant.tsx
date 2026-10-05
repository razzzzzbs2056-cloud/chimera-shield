"use client";

import { Bot, Send, User } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { api, Button } from "./ui";

type Msg = { role: "user" | "assistant"; content: string; note?: string; source?: string };
const SUGGESTIONS = ["Summarise the main design risks and failing checks", "Why did the agents change the structure?", "How can we cut embodied carbon by 15% without breaking drift?", "Is the egress design adequate for a high-rise?", "Which value-engineering options should we take to the client?", "Explain the foundation choice"];

function render(text: string) {
  return text.split(/\n{2,}/).map((para, i) => (
    <p key={i} className="mb-2 last:mb-0">
      {para.split(/(\*\*[^*]+\*\*)/g).map((seg, j) => (seg.startsWith("**") ? <strong key={j}>{seg.slice(2, -2)}</strong> : seg.split("\n").map((l, k, a) => <span key={k}>{l}{k < a.length - 1 && <br />}</span>)))}
    </p>
  ));
}

export function Assistant({ projectId, projectName }: { projectId: string; projectName: string }) {
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const end = useRef<HTMLDivElement>(null);
  useEffect(() => end.current?.scrollIntoView({ behavior: "smooth", block: "end" }), [msgs, busy]);

  async function ask(q: string) {
    if (!q.trim() || busy) return;
    const history = msgs.map(({ role, content }) => ({ role, content }));
    setMsgs((m) => [...m, { role: "user", content: q }]);
    setInput("");
    setBusy(true);
    try {
      const r = await api<{ answer: string; source: string; note?: string; model?: string }>(`/api/projects/${projectId}/ask`, { body: { question: q, history } });
      setMsgs((m) => [...m, { role: "assistant", content: r.answer, note: r.note, source: r.source === "claude" ? `Claude · ${r.model}` : "Solver summary" }]);
    } catch (e) {
      setMsgs((m) => [...m, { role: "assistant", content: (e as Error).message, note: "Request failed" }]);
    }
    setBusy(false);
  }

  return (
    <div className="card flex h-[calc(100vh-260px)] min-h-[480px] flex-col">
      <div className="scrollbar-thin flex-1 space-y-4 overflow-y-auto p-4">
        {msgs.length === 0 && (
          <div className="mx-auto max-w-xl py-8 text-center">
            <div className="mx-auto flex h-11 w-11 items-center justify-center rounded-full bg-brand-50 text-brand-600"><Bot className="h-5 w-5" /></div>
            <h3 className="mt-3 font-semibold">Ask the consultancy about {projectName}</h3>
            <p className="mt-1 text-sm text-slate-500">Answers are grounded in the latest solver run — Claude explains and recommends, the engines produce the numbers.</p>
            <div className="mt-5 flex flex-wrap justify-center gap-2">{SUGGESTIONS.map((s) => <button key={s} onClick={() => ask(s)} className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-700 hover:border-brand-300 hover:bg-brand-50">{s}</button>)}</div>
          </div>
        )}
        {msgs.map((m, i) => (
          <div key={i} className={`flex gap-3 ${m.role === "user" ? "justify-end" : ""}`}>
            {m.role === "assistant" && <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-brand-600 text-white"><Bot className="h-4 w-4" /></div>}
            <div className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm ${m.role === "user" ? "bg-brand-600 text-white" : "bg-slate-100 text-slate-800"}`}>
              {render(m.content)}
              {(m.source || m.note) && <div className="mt-2 text-[11px] text-slate-500">{[m.source, m.note].filter(Boolean).join(" · ")}</div>}
            </div>
            {m.role === "user" && <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-slate-200 text-slate-600"><User className="h-4 w-4" /></div>}
          </div>
        ))}
        {busy && <div className="flex gap-3"><div className="flex h-7 w-7 items-center justify-center rounded-full bg-brand-600 text-white"><Bot className="h-4 w-4" /></div><div className="flex items-center gap-1 rounded-2xl bg-slate-100 px-4 py-3">{[0, 1, 2].map((d) => <span key={d} className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-400" style={{ animationDelay: `${d * 120}ms` }} />)}</div></div>}
        <div ref={end} />
      </div>
      <form onSubmit={(e) => { e.preventDefault(); ask(input); }} className="flex gap-2 border-t border-slate-100 p-3">
        <input className="input" value={input} onChange={(e) => setInput(e.target.value)} placeholder="Ask about drift, egress, cost, carbon, clashes…" aria-label="Question" />
        <Button type="submit" disabled={!input.trim()} loading={busy}>{!busy && <Send className="h-4 w-4" />}Ask</Button>
      </form>
    </div>
  );
}
