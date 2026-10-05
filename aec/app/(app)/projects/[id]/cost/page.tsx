import { BarViz } from "@/components/charts";
import { BoqTable } from "@/components/boq-table";
import { NoRun } from "@/components/no-run";
import { Badge, Card, Stat, StatusBadge, Table } from "@/components/ui";
import { fmt } from "@/lib/format";
import { loadProject } from "@/lib/project-page";

export default async function Cost({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const { run } = await loadProject(id);
  if (!run) return <NoRun id={id} />;
  const c = run.cost;
  return (
    <>
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <Stat label="Total construction cost" value={fmt.money(c.total)} hint={`$${fmt.n(c.perM2)}/m² GFA`} />
        <Stat label="Budget" value={fmt.money(c.budget)} hint={`${c.variance > 0 ? "Over" : "Under"} by ${fmt.money(Math.abs(c.variance))} (${((c.variance / c.budget) * 100).toFixed(1)}%)`} tone={c.variance > 0 ? "bad" : "good"} />
        <Stat label="Direct works" value={fmt.money(c.subtotal)} hint={`Prelims ${fmt.money(c.preliminaries)} · contingency ${fmt.money(c.contingency)}`} />
        <Stat label="Best VE saving" value={fmt.money(Math.max(0, ...run.ve.filter((v) => v.ok).map((v) => v.saving)))} hint={`${run.ve.filter((v) => v.ok).length} options pass performance checks`} tone="good" />
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Cost by discipline"><BarViz data={c.byDiscipline.map((d) => ({ name: d.name, USD: d.value }))} x="name" series={[{ key: "USD" }]} horizontal height={300} /></Card>
        <Card title="Cost by floor" subtitle="Superstructure, envelope, services and fit-out distributed per level"><BarViz data={c.byFloor.map((d) => ({ level: d.level, USD: d.value }))} x="level" series={[{ key: "USD" }]} height={300} /></Card>
      </div>
      <Card title="Quantity take-off" subtitle="Measured from the parametric model and sized engineering systems">
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
          {Object.entries(c.quantities).map(([k, v]) => <div key={k} className="rounded-lg border border-slate-200 px-3 py-2"><div className="text-[11px] text-slate-500">{k}</div><div className="num text-sm font-semibold">{fmt.n(v.qty)} <span className="text-xs font-normal text-slate-500">{v.unit}</span></div></div>)}
        </div>
      </Card>
      <BoqTable rows={c.boq} href={`/api/projects/${id}/export?type=boq`} totals={[{ label: "Direct works subtotal", value: c.subtotal }, { label: "Preliminaries (11%)", value: c.preliminaries }, { label: "Design contingency (8%)", value: c.contingency }, { label: "Professional fees (9%)", value: c.fees }, { label: "Escalation (2 yrs @ 3.5%)", value: c.escalation }, { label: "Total construction cost", value: c.total }]} />
      <Card title="Value engineering" subtitle="Each alternative re-run through the full engine — savings are only recommended if performance still passes" pad={false}>
        <Table head={["Option", "Saving", "Carbon", "EUI", "Drift %", "Programme", "Performance consequences", "Verdict"]}>
          {run.ve.map((v) => (
            <tr key={v.id}>
              <td className="td font-medium">{v.title}</td>
              <td className={`td num ${v.saving > 0 ? "text-emerald-700" : "text-red-700"}`}>{v.saving > 0 ? "−" : "+"}{fmt.money(Math.abs(v.saving))}</td>
              <td className="td num">{v.carbon}</td><td className="td num">{v.eui}</td><td className="td num">{v.drift}</td><td className="td num">{v.months} mo</td>
              <td className="td text-xs">{v.consequences.length ? v.consequences.map((x) => <Badge key={x} tone={x.includes("exceeds") || x.includes("failure") ? "red" : "amber"} className="mb-1 mr-1">{x}</Badge>) : <span className="text-slate-400">none</span>}</td>
              <td className="td"><StatusBadge status={v.ok ? "PASS" : "FAIL"} label={v.ok ? "recommend" : "reject"} /></td>
            </tr>
          ))}
        </Table>
      </Card>
    </>
  );
}
