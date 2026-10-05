import { BarViz } from "@/components/charts";
import { NoRun } from "@/components/no-run";
import { SectionTitle } from "@/components/page";
import { Badge, Card, Stat, StatusBadge, Table } from "@/components/ui";
import { fmt } from "@/lib/format";
import { loadProject } from "@/lib/project-page";

export default async function Sustainability({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const { project, run } = await loadProject(id);
  if (!run) return <NoRun id={id} />;
  const c = run.cost.carbon, r = run.resilience;
  const greenVE = run.ve.filter((v) => v.carbon < c.perM2);
  const sel = run.selection.filter((s) => s.feasible);
  const tone = (x: number) => (x >= 12 ? "red" : x >= 6 ? "amber" : "green") as "red" | "amber" | "green";
  return (
    <>
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <Stat label="Embodied carbon A1–A5" value={c.perM2} unit="kgCO₂e/m²" hint={`Target ${project.intake.targetCarbon}`} tone={c.perM2 <= project.intake.targetCarbon ? "good" : "bad"} />
        <Stat label="Total embodied" value={fmt.n(c.total)} unit="tCO₂e" hint={`A1–A3 ${fmt.n(c.a1a3)} t · A4–A5 ${fmt.n(c.a4a5)} t`} />
        <Stat label="Operational (annual)" value={run.energy.operationalCarbon} unit="kg/m²·yr" hint={`Payback vs embodied: ${Math.round(c.perM2 / Math.max(run.energy.operationalCarbon, 0.1))} yrs of operation`} />
        <Stat label="Resilience score" value={r.score} unit="/ 100" hint={`Chiller margin at ${r.heat2050} °C: ${r.chillerMargin}%`} tone={r.score >= 70 ? "good" : "warn"} />
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Embodied carbon by element group" subtitle="tCO₂e, A1–A3 (ICE-style generic factors)"><BarViz data={c.byCategory.map((x) => ({ name: x.name, tCO2e: x.value }))} x="name" series={[{ key: "tCO2e" }]} horizontal height={300} /></Card>
        <Card title="Carbon by structural system" subtitle="Structure-only A1–A3 for each feasible lateral system">
          {sel.length ? <BarViz data={sel.map((s) => ({ name: s.label.replace(/\(.*\)/, "").trim(), tCO2e: s.carbon }))} x="name" series={[{ key: "tCO2e" }]} horizontal height={300} /> : <p className="text-sm text-slate-500">No comparison available.</p>}
        </Card>
      </div>
      <Card title="Lower-carbon options" subtitle="Value-engineering alternatives that reduce embodied carbon, re-evaluated by the full engine" pad={false}>
        {greenVE.length === 0 ? <p className="px-4 py-6 text-sm text-slate-500">No lower-carbon alternative found among the VE options.</p> : (
          <Table head={["Option", "Carbon (kg/m²)", "Δ carbon", "Cost impact", "Consequences"]}>
            {greenVE.map((v) => <tr key={v.id}><td className="td font-medium">{v.title}</td><td className="td num">{v.carbon}</td><td className="td num text-emerald-700">−{(c.perM2 - v.carbon).toFixed(0)}</td><td className={`td num ${v.saving >= 0 ? "text-emerald-700" : "text-red-700"}`}>{v.saving >= 0 ? "saves " : "adds "}{fmt.money(Math.abs(v.saving))}</td><td className="td text-xs">{v.consequences.join("; ") || "None"}</td></tr>)}
          </Table>
        )}
      </Card>
      <SectionTitle sub="Exposure × vulnerability (1–4 each); risk ≥ 12 is high">Climate-resilience analysis</SectionTitle>
      <div className="grid gap-4 lg:grid-cols-3">
        <Card title="Hazard register" className="lg:col-span-2" pad={false}>
          <Table head={["Hazard", "Exposure", "Vulnerability", "Risk", "Mitigation"]}>
            {r.hazards.map((h) => <tr key={h.hazard}><td className="td font-medium">{h.hazard}</td><td className="td num">{h.exposure}</td><td className="td num">{h.vulnerability}</td><td className="td"><Badge tone={tone(h.risk)}>{h.risk}</Badge></td><td className="td text-xs">{h.mitigation}</td></tr>)}
          </Table>
        </Card>
        <Card title="System redundancy" pad={false}>
          <ul className="divide-y divide-slate-100">{r.redundancy.map((x) => <li key={x.system} className="flex items-center justify-between gap-2 px-4 py-2.5 text-sm"><span><span className="font-medium">{x.system}</span><div className="text-xs text-slate-500">{x.config}</div></span><StatusBadge status={x.ok ? "PASS" : "WARN"} label={x.ok ? "redundant" : "single point"} /></li>)}</ul>
        </Card>
      </div>
    </>
  );
}
