import { Drawings } from "@/components/drawings";
import { NoRun } from "@/components/no-run";
import { Badge, Card, Table } from "@/components/ui";
import { fmt } from "@/lib/format";
import { loadProject } from "@/lib/project-page";

export default async function DrawingsPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const { project, run } = await loadProject(id);
  if (!run) return <NoRun id={id} />;
  const p = run.params;
  const tiers = [0, 1, 2].map((t) => {
    const from = Math.floor((t * p.floors) / 3) + 1, to = Math.floor(((t + 1) * p.floors) / 3);
    const size = Math.max(0.3, p.columnSize * [1, 0.85, 0.7][t]);
    return { mark: `C${t + 1}`, levels: `L${from}–L${to}`, size: `${Math.round(size * 1000)} × ${Math.round(size * 1000)}`, material: p.material === "concrete" ? `C${p.concreteGrade}, ρ ≈ 2%` : p.material === "timber" ? "GL28h glulam" : "Heavy W-shape, A992" };
  }).filter((t) => t.levels !== `L${p.floors + 1}–L${p.floors}`);
  return (
    <>
      <Card title="Drawing generator" subtitle="Plans, services plans, sections and elevations derived live from the IFC model"><Drawings projectId={id} code={project.code} /></Card>
      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Column schedule" pad={false}>
          <Table head={["Mark", "Levels", "Size (mm)", "Material", "Count / floor"]}>
            {tiers.map((t) => <tr key={t.mark}><td className="td font-medium">{t.mark}</td><td className="td">{t.levels}</td><td className="td num">{t.size}</td><td className="td">{t.material}</td><td className="td num">{(p.baysX + 1) * (p.baysY + 1)}</td></tr>)}
          </Table>
        </Card>
        <Card title="Plant & equipment schedule" pad={false}>
          <Table head={["Tag", "Description", "Qty", "Capacity"]}>
            <tr><td className="td font-medium">CH</td><td className="td">Water-cooled chiller</td><td className="td num">{run.hvac.plant.chillers}</td><td className="td num">{run.hvac.plant.chillerSize} kW</td></tr>
            <tr><td className="td font-medium">AHU</td><td className="td">Air-handling unit w/ heat recovery</td><td className="td num">{run.hvac.plant.ahus}</td><td className="td num">{run.hvac.plant.ahuSize} m³/s</td></tr>
            <tr><td className="td font-medium">TX</td><td className="td">Cast-resin transformer</td><td className="td num">{run.electrical.transformers.count}</td><td className="td num">{run.electrical.transformers.size} kVA</td></tr>
            <tr><td className="td font-medium">GEN</td><td className="td">Standby diesel generator</td><td className="td num">1</td><td className="td num">{run.electrical.generator.kVA} kVA</td></tr>
            <tr><td className="td font-medium">L</td><td className="td">Traction passenger lift</td><td className="td num">{p.liftCount}</td><td className="td num">{p.floors > 30 ? "4.0" : "2.5"} m/s</td></tr>
            <tr><td className="td font-medium">PV</td><td className="td">Rooftop photovoltaic array</td><td className="td num">1</td><td className="td num">{fmt.n(run.electrical.pv.kWp)} kWp</td></tr>
          </Table>
        </Card>
      </div>
      <Card title="Specification generator" subtitle="CSI MasterFormat sections drafted from engineering results and linked to IFC object types">
        <div className="grid gap-3 lg:grid-cols-2">
          {run.specs.map((s) => (
            <section key={s.section} className="rounded-lg border border-slate-200 p-3">
              <div className="flex flex-wrap items-center gap-2"><span className="font-mono text-xs text-slate-500">{s.section}</span><h4 className="text-sm font-semibold">{s.title}</h4><Badge tone="blue" className="ml-auto">{fmt.n(s.elements)} linked elements</Badge></div>
              <ol className="mt-2 list-decimal space-y-1 pl-5 text-xs text-slate-700">{s.clauses.map((c, i) => <li key={i}>{c}</li>)}</ol>
              {s.ifc.length > 0 && <div className="mt-2 flex flex-wrap gap-1">{s.ifc.map((t) => <Badge key={t}>{t}</Badge>)}</div>}
            </section>
          ))}
        </div>
      </Card>
    </>
  );
}
