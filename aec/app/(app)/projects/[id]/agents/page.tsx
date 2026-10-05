import { ArrowRight, Bot } from "lucide-react";
import { NoRun } from "@/components/no-run";
import { Badge, Card, Table } from "@/components/ui";
import { AGENT_CATALOG } from "@/lib/engine/agents";
import { loadProject } from "@/lib/project-page";

const KIND: Record<string, "slate" | "blue" | "green" | "amber" | "red" | "violet"> = { handoff: "blue", constraint: "violet", change: "amber", query: "slate", result: "green", warning: "red" };
const name = (id: string) => (id === "all" ? "All agents" : AGENT_CATALOG.find((a) => a.id === id)?.name ?? id);

export default async function Agents({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const { run } = await loadProject(id);
  if (!run) return <NoRun id={id} />;
  return (
    <div className="grid gap-5 xl:grid-cols-5">
      <div className="space-y-5 xl:col-span-2">
        <Card title="Automatic agent routing" subtitle="Which specialists this project needs, and why" pad={false}>
          <ul className="divide-y divide-slate-100">
            {run.agents.map((a) => (
              <li key={a.id} className="flex items-start gap-3 px-4 py-2.5">
                <Bot className={`mt-0.5 h-4 w-4 shrink-0 ${a.required ? "text-brand-600" : "text-slate-300"}`} />
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 text-sm font-medium">{a.name}{!a.required && <Badge>skipped</Badge>}{a.status === "warning" && <Badge tone="amber">attention</Badge>}</div>
                  <div className="text-xs text-slate-500">{a.reason}</div>
                </div>
                <span className="shrink-0 text-[11px] text-slate-400">{a.discipline}</span>
              </li>
            ))}
          </ul>
        </Card>
        <Card title="Design iterations" subtitle="Structural ↔ seismic ↔ architecture convergence loop" pad={false}>
          <Table head={["#", "System", "Drift %", "θ", "Col. util", "Action"]}>
            {run.iterations.map((it) => (
              <tr key={it.n}>
                <td className="td num">{it.n}</td><td className="td">{it.system}</td><td className="td num">{it.drift}</td><td className="td num">{it.theta}</td><td className="td num">{it.colUtil}</td>
                <td className="td text-xs">{it.action}</td>
              </tr>
            ))}
          </Table>
        </Card>
      </div>
      <Card title="Collaboration log" subtitle={`${run.messages.length} messages — models, constraints and design changes passed between agents`} className="xl:col-span-3" pad={false}>
        <ol className="relative space-y-0 px-4 py-3">
          {run.messages.map((m) => (
            <li key={m.seq} className="relative border-l border-slate-200 pb-4 pl-5 last:pb-0">
              <span className="absolute -left-[5px] top-1.5 h-2.5 w-2.5 rounded-full border-2 border-white bg-brand-500" />
              <div className="flex flex-wrap items-center gap-1.5 text-xs">
                <span className="font-semibold text-slate-800">{name(m.from)}</span><ArrowRight className="h-3 w-3 text-slate-400" /><span className="text-slate-600">{name(m.to)}</span>
                <Badge tone={KIND[m.kind]}>{m.kind}</Badge>{m.iteration && <span className="text-slate-400">iteration {m.iteration}</span>}
              </div>
              <p className="mt-0.5 text-sm text-slate-700">{m.content}</p>
            </li>
          ))}
        </ol>
      </Card>
    </div>
  );
}
