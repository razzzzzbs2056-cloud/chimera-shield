import { Activity, AlertTriangle, ArrowRight, Building2, CheckCircle2, Leaf, Plus, Ruler, Wallet } from "lucide-react";
import Link from "next/link";
import { CarbonChart, ComplianceChart, CostChart } from "@/components/dashboard-charts";
import { Container, PageHeader } from "@/components/page";
import { Badge, Card, EmptyState, Stat } from "@/components/ui";
import { fmt } from "@/lib/format";
import { requireUser } from "@/lib/auth";
import { listActivity, portfolioStats } from "@/lib/repo";

export const metadata = { title: "Dashboard" };

export default async function Dashboard() {
  const user = await requireUser();
  const s = portfolioStats(user.id);
  const activity = listActivity(user.id, 10);
  const withK = s.projects.filter((p) => p.kpis);
  const total = s.pass + s.fail + s.warn;
  const short = (n: string) => (n.length > 16 ? n.slice(0, 15) + "…" : n);
  return (
    <Container>
      <PageHeader eyebrow={new Date().toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" })} title={`Good to see you, ${user.name.split(" ")[0]}`} subtitle="Portfolio health across design, compliance, cost, carbon and operations."
        actions={<Link href="/projects/new" className="inline-flex items-center gap-1.5 rounded-lg bg-brand-600 px-3.5 py-2 text-sm font-medium text-white shadow-sm hover:bg-brand-700"><Plus className="h-4 w-4" /> New project</Link>} />
      {s.count === 0 ? (
        <EmptyState icon={Building2} title="Your portfolio is empty" body="Create a project from a site brief, or load a sample tower to see the agents, solvers and BIM at work." action={<Link href="/projects?welcome=1" className="text-sm font-medium text-brand-700 hover:underline">Go to projects →</Link>} />
      ) : (
        <>
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            <Stat label="Active projects" value={s.count} hint={`${fmt.n(s.gfa)} m² gross floor area`} />
            <Stat label="Portfolio construction value" value={fmt.money(s.cost)} hint={`${withK.filter((p) => p.kpis!.budgetVariance > 0).length} over budget`} tone={withK.some((p) => p.kpis!.budgetVariance > 0) ? "warn" : "good"} />
            <Stat label="Clause-level checks passing" value={total ? fmt.pct((s.pass / total) * 100, 0) : "—"} hint={`${s.fail} failing · ${s.warn} warnings`} tone={s.fail ? "bad" : "good"} />
            <Stat label="Embodied carbon (GFA-weighted)" value={fmt.n(s.carbon)} unit="kgCO₂e/m²" hint={`${s.openIssues} open coordination issues`} tone={s.critical ? "warn" : undefined} />
          </div>
          <div className="grid gap-4 lg:grid-cols-3">
            <Card title="Compliance by project" subtitle="PASS / WARN / FAIL across all automated clause checks" className="lg:col-span-2">
              <ComplianceChart data={withK.map((p) => ({ name: short(p.name), Pass: p.kpis!.pass, Warn: p.kpis!.warn, Fail: p.kpis!.fail }))} />
            </Card>
            <Card title="Recent activity" pad={false}>
              <ul className="divide-y divide-slate-100">
                {activity.length === 0 && <li className="px-4 py-6 text-center text-sm text-slate-500">No activity yet</li>}
                {activity.map((a) => (
                  <li key={a.id} className="flex gap-3 px-4 py-2.5">
                    <Activity className="mt-0.5 h-4 w-4 shrink-0 text-slate-400" />
                    <div className="min-w-0 text-sm">
                      <span className="text-slate-700">{a.action}</span>{a.project_name && <> · <Link className="font-medium text-slate-900 hover:underline" href={`/projects/${a.project_id}`}>{a.project_name}</Link></>}
                      {a.detail && <div className="truncate text-xs text-slate-500">{a.detail}</div>}
                      <div className="text-[11px] text-slate-400">{fmt.date(a.created_at)}</div>
                    </div>
                  </li>
                ))}
              </ul>
            </Card>
          </div>
          <div className="grid gap-4 lg:grid-cols-2">
            <Card title="Estimate vs budget" subtitle="Construction cost incl. preliminaries, contingency, fees and escalation"><CostChart data={withK.map((p) => ({ name: short(p.name), Estimate: p.kpis!.cost, Budget: p.intake.budget }))} /></Card>
            <Card title="Embodied carbon vs target" subtitle="kgCO₂e per m² GFA, modules A1–A5"><CarbonChart data={withK.map((p) => ({ name: short(p.name), Embodied: p.kpis!.embodiedCarbon, Target: p.intake.targetCarbon }))} /></Card>
          </div>
          <Card title="Projects" pad={false} action={<Link href="/projects" className="text-xs font-medium text-brand-700 hover:underline">View all</Link>}>
            <ul className="divide-y divide-slate-100">
              {s.projects.slice(0, 6).map((p) => (
                <li key={p.id}>
                  <Link href={`/projects/${p.id}`} className="flex flex-wrap items-center gap-x-6 gap-y-2 px-4 py-3 hover:bg-slate-50">
                    <div className="min-w-[200px] flex-1">
                      <div className="flex items-center gap-2"><span className="font-medium text-slate-900">{p.name}</span><Badge>{p.code}</Badge></div>
                      <div className="text-xs text-slate-500">{p.intake.city} · {p.intake.buildingType} · {p.params.floors} storeys · {p.stage}</div>
                    </div>
                    {p.kpis ? (
                      <div className="flex flex-wrap gap-5 text-xs text-slate-600">
                        <span className="flex items-center gap-1"><Ruler className="h-3.5 w-3.5" />{fmt.n(p.kpis.gfa)} m²</span>
                        <span className="flex items-center gap-1"><Wallet className="h-3.5 w-3.5" />{fmt.money(p.kpis.cost)}</span>
                        <span className="flex items-center gap-1"><Leaf className="h-3.5 w-3.5" />{p.kpis.embodiedCarbon} kg/m²</span>
                        <span className={`flex items-center gap-1 ${p.kpis.fail ? "text-red-700" : "text-emerald-700"}`}>{p.kpis.fail ? <AlertTriangle className="h-3.5 w-3.5" /> : <CheckCircle2 className="h-3.5 w-3.5" />}{p.kpis.fail ? `${p.kpis.fail} failing` : "All passing"}</span>
                      </div>
                    ) : <Badge tone="amber">Not analysed</Badge>}
                    <ArrowRight className="h-4 w-4 text-slate-300" />
                  </Link>
                </li>
              ))}
            </ul>
          </Card>
        </>
      )}
    </Container>
  );
}
