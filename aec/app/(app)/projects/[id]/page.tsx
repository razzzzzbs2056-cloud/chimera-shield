import { ArrowRight, Bot, GitBranch } from "lucide-react";
import Link from "next/link";
import { NoRun } from "@/components/no-run";
import { Badge, Card, Stat, StatusBadge } from "@/components/ui";
import { fmt } from "@/lib/format";
import { loadProject } from "@/lib/project-page";

export default async function Overview({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const { project, run } = await loadProject(id);
  if (!run) return <NoRun id={id} />;
  const k = run.kpis;
  const fails = run.findings.filter((f) => f.status === "FAIL");
  const base = `/projects/${id}`;
  return (
    <>
      {project.description && <p className="max-w-4xl text-sm text-slate-600">{project.description}</p>}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <Stat label="Gross floor area" value={fmt.n(k.gfa)} unit="m²" hint={`NLA ${fmt.n(k.nla)} m² · efficiency ${fmt.pct(k.efficiency * 100, 0)}`} />
        <Stat label="Construction estimate" value={fmt.money(k.cost)} hint={`${k.budgetVariance > 0 ? "+" : ""}${fmt.money(k.budgetVariance)} vs budget · $${fmt.n(k.costPerM2)}/m²`} tone={k.budgetVariance > 0 ? "bad" : "good"} />
        <Stat label="Embodied carbon" value={k.embodiedCarbon} unit="kgCO₂e/m²" hint={`Target ${project.intake.targetCarbon}`} tone={k.embodiedCarbon > project.intake.targetCarbon ? "warn" : "good"} />
        <Stat label="Energy use intensity" value={k.eui} unit="kWh/m²·yr" hint={`Target ${project.intake.targetEUI}`} tone={k.eui > project.intake.targetEUI ? "warn" : "good"} />
        <Stat label="Height / period" value={`${k.height} m`} hint={`T₁ ${k.T1} s · ${run.structure.system.label}`} />
        <Stat label="Max story drift" value={fmt.pct(k.maxDrift, 2)} hint={`Limit ${k.driftLimit}% · ${run.structure.pushover.level}`} tone={k.maxDrift > k.driftLimit ? "bad" : "good"} />
        <Stat label="Compliance" value={`${k.pass}/${k.pass + k.fail + k.warn}`} hint={`${k.fail} fail · ${k.warn} warn`} tone={k.fail ? "bad" : "good"} />
        <Stat label="Programme" value={run.construction.durationMonths} unit="months" hint={`${run.construction.floorCycle}-day floor cycle · ${k.clashes} clash groups`} />
      </div>
      <div className="grid gap-4 lg:grid-cols-3">
        <Card title="Failing checks" subtitle="Clause-level findings that need design action" className="lg:col-span-2" pad={false} action={<Link href={`${base}/compliance`} className="text-xs font-medium text-brand-700 hover:underline">All findings</Link>}>
          {fails.length === 0 ? <p className="px-4 py-8 text-center text-sm text-emerald-700">All automated checks pass. Review warnings and verification before issue.</p> : (
            <ul className="divide-y divide-slate-100">
              {fails.slice(0, 8).map((f) => (
                <li key={f.id} className="flex items-start gap-3 px-4 py-2.5">
                  <StatusBadge status={f.status} />
                  <div className="min-w-0 text-sm">
                    <div className="font-medium text-slate-900">{f.check}</div>
                    <div className="text-xs text-slate-500">{f.standard} {f.clause} — {f.evidence}</div>
                  </div>
                  <Badge className="ml-auto shrink-0">{f.discipline}</Badge>
                </li>
              ))}
            </ul>
          )}
        </Card>
        <Card title="Agent design changes" subtitle="Changes negotiated between agents during this run" pad={false} action={<GitBranch className="h-4 w-4 text-slate-400" />}>
          {run.changes.length === 0 ? <p className="px-4 py-8 text-center text-sm text-slate-500">The brief converged without changes.</p> : (
            <ul className="divide-y divide-slate-100">
              {run.changes.map((c, i) => (
                <li key={i} className="px-4 py-2.5 text-sm">
                  <div><span className="font-mono text-xs text-slate-500">{c.param}</span> <span className="num">{String(c.from)} → <b>{String(c.to)}</b></span></div>
                  <div className="text-xs text-slate-500">{c.by} agent · {c.reason}</div>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
      <Card title="Specialist agents" subtitle={`${run.agents.filter((a) => a.required).length} engaged by automatic routing`} action={<Link href={`${base}/agents`} className="inline-flex items-center gap-1 text-xs font-medium text-brand-700 hover:underline">Collaboration log <ArrowRight className="h-3 w-3" /></Link>}>
        <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
          {run.agents.map((a) => (
            <div key={a.id} className={`flex items-start gap-2 rounded-lg border px-3 py-2 ${a.status === "skipped" ? "border-dashed border-slate-200 opacity-60" : "border-slate-200"}`}>
              <Bot className={`mt-0.5 h-4 w-4 shrink-0 ${a.status === "warning" ? "text-amber-600" : a.status === "skipped" ? "text-slate-300" : "text-emerald-600"}`} />
              <div className="min-w-0"><div className="truncate text-sm font-medium">{a.name}</div><div className="truncate text-[11px] text-slate-500">{a.status === "warning" ? "Has failing checks" : a.status === "skipped" ? "Not required" : a.discipline}</div></div>
            </div>
          ))}
        </div>
      </Card>
    </>
  );
}
