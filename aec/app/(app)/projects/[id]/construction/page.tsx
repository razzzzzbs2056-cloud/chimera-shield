import { Download } from "lucide-react";
import { LineViz } from "@/components/charts";
import { Construction4D } from "@/components/construction-4d";
import { Gantt } from "@/components/eng-charts";
import { NoRun } from "@/components/no-run";
import { KV } from "@/components/page";
import { Badge, Card, Stat, StatusBadge, Table } from "@/components/ui";
import { fmt } from "@/lib/format";
import { loadProject } from "@/lib/project-page";

export default async function Construction({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const { run } = await loadProject(id);
  if (!run) return <NoRun id={id} />;
  const c = run.construction;
  return (
    <>
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <Stat label="Programme" value={c.durationMonths} unit="months" hint={`${c.durationDays} working days · ${c.criticalPath.length} critical activities`} />
        <Stat label="Floor cycle" value={c.floorCycle} unit="days" hint={`${run.params.slabSystem} slabs`} />
        <Stat label="Tower cranes" value={`${c.cranes.count} × ${c.cranes.type.split(" ")[0]}`} hint={c.cranes.type} tone={c.cranes.ok ? "good" : "bad"} />
        <Stat label="Peak workforce" value={fmt.n(c.peakWorkforce)} hint={`${c.hoists} hoists · ${c.gates} site gate(s)`} />
      </div>
      <Card title="Construction sequence & critical path" subtitle="CPM forward/backward pass — façade follows structure, MEP and fit-out cascade by floor" action={<a href={`/api/projects/${id}/export?type=schedule`} className="inline-flex items-center gap-1 text-xs font-medium text-brand-700 hover:underline"><Download className="h-3.5 w-3.5" />CSV</a>}>
        <Gantt acts={c.activities} total={c.durationDays} critical={c.activities.length > 60} />
        {c.activities.length > 60 && <p className="mt-2 text-[11px] text-slate-500">Showing critical-path activities ({c.activities.length} total in CSV export).</p>}
      </Card>
      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="4D BIM" subtitle="Model elements linked to scheduled activities"><Construction4D projectId={id} acts={c.activities.map((a) => ({ id: a.id, name: a.name, es: a.es, ef: a.ef, levels: a.levels }))} total={c.durationDays} /></Card>
        <Card title="5D — cash flow" subtitle="Cumulative cost (S-curve) and monthly spend from the resource-loaded programme">
          <LineViz data={c.cashflow.map((m) => ({ month: m.month, "Cumulative ($M)": +(m.cumulative / 1e6).toFixed(2), "Monthly ($M)": +(m.monthly / 1e6).toFixed(2) }))} x="month" series={[{ key: "Cumulative ($M)" }, { key: "Monthly ($M)" }]} height={300} xLabel="Month" />
        </Card>
      </div>
      <div className="grid gap-4 lg:grid-cols-3">
        <Card title="Crane & logistics">
          <KV cols={1} rows={[["Crane type", c.cranes.type], ["Required radius", `${c.cranes.radius} m`], ["Critical lift", `${c.cranes.heaviestLift.item} — ${c.cranes.heaviestLift.weight} t @ ${c.cranes.heaviestLift.radius} m`], ["Capacity at radius", <StatusBadge key="c" status={c.cranes.ok ? "PASS" : "FAIL"} label={`${c.cranes.capacityAtRadius} t`} />], ["Hook time", `${c.cranes.hookHoursPerWeek} h/wk (${Math.round(c.cranes.utilisation * 100)}%)`], ["Staging area", `${fmt.n(c.stagingArea)} m²`], ["Hoists", c.hoists]]} />
        </Card>
        <Card title="Temporary works" pad={false}>
          <ul className="divide-y divide-slate-100">{c.temporaryWorks.map((t) => <li key={t.item} className="px-4 py-2.5"><div className="flex items-center justify-between gap-2"><span className="text-sm font-medium">{t.item}</span><StatusBadge status={t.ok ? "PASS" : "FAIL"} /></div><div className="text-xs text-slate-600">{t.solution}</div><div className="text-[11px] text-slate-400">{t.check}</div></li>)}</ul>
        </Card>
        <Card title="Constructability review" subtitle="Valid on paper, hard on site" pad={false}>
          {c.constructability.length === 0 ? <p className="px-4 py-8 text-center text-sm text-emerald-700">No constructability concerns flagged.</p> : (
            <ul className="divide-y divide-slate-100">{c.constructability.map((x, i) => <li key={i} className="px-4 py-2.5"><Badge tone={x.severity === "high" ? "red" : x.severity === "medium" ? "amber" : "slate"}>{x.severity}</Badge><div className="mt-1 text-sm font-medium">{x.issue}</div><div className="text-xs text-slate-600">→ {x.recommendation}</div></li>)}</ul>
          )}
        </Card>
      </div>
      <Card title="Activity register (critical)" pad={false}>
        <Table head={["ID", "Activity", "Phase", "Duration", "Early start", "Early finish", "Float"]}>
          {c.activities.filter((a) => a.critical).slice(0, 40).map((a) => <tr key={a.id}><td className="td font-mono text-xs">{a.id}</td><td className="td">{a.name}</td><td className="td">{a.phase}</td><td className="td num">{a.duration} d</td><td className="td num">{a.es}</td><td className="td num">{a.ef}</td><td className="td num">{a.float}</td></tr>)}
        </Table>
      </Card>
    </>
  );
}
