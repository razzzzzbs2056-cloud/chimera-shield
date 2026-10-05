import { LineViz } from "@/components/charts";
import { NoRun } from "@/components/no-run";
import { AssetRegister } from "@/components/operations";
import { Card, Stat } from "@/components/ui";
import { assetHealth, twinState } from "@/lib/engine/operations";
import { fmt } from "@/lib/format";
import { loadProject } from "@/lib/project-page";
import { listAssets } from "@/lib/repo";

export default async function Operations({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const { user, project, run } = await loadProject(id);
  if (!run) return <NoRun id={id} />;
  const assets = (listAssets(user.id, id) ?? []).map((a) => ({ ...assetHealth({ id: a.id, name: a.name, system: a.system, type: a.type, installDate: a.install_date, condition: a.condition, runtimeHours: a.runtime_hours, criticality: a.criticality, location: a.location ?? "" }), install_date: a.install_date, runtime_hours: a.runtime_hours, criticality: a.criticality }));
  const twin = twinState(id, run.params.floors, run.energy.eui, run.derived.gfaAbove);
  const levels = [...new Set(twin.zones.map((z) => z.level))].sort((a, b) => b - a);
  const zones = ["N", "E", "S", "W", "Core"];
  const tColor = (t: number) => (t > 24.5 ? "#e34948" : t > 23.6 ? "#eda100" : t < 21.5 ? "#2a78d6" : "#1baf7a");
  const operating = project.stage === "Operations" || project.status === "completed";
  return (
    <>
      {!operating && <p className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">This project is in <b>{project.stage}</b>. The digital twin below runs on simulated sensor feeds derived from the design model; connect BMS/IoT data at handover.</p>}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <Stat label="Measured EUI (rolling)" value={twin.kpis.eui} unit="kWh/m²·yr" hint={`Design ${run.energy.eui}`} tone={twin.kpis.eui > run.energy.eui * 1.05 ? "warn" : "good"} />
        <Stat label="Comfort compliance" value={`${twin.kpis.comfort}%`} hint="Zones within 21–24 °C" tone={twin.kpis.comfort >= 85 ? "good" : "warn"} />
        <Stat label="Energy anomalies (48 h)" value={twin.kpis.anomalies} hint="> 25 % above baseline" tone={twin.kpis.anomalies ? "warn" : "good"} />
        <Stat label="Savings potential" value={fmt.money(twin.kpis.savingsPotential)} unit="/ yr" hint={`${assets.filter((a) => a.status === "action").length} assets need action`} />
      </div>
      <div className="grid gap-4 lg:grid-cols-3">
        <Card title="Live energy vs baseline" subtitle="Last 48 hours, kW" className="lg:col-span-2">
          <LineViz data={twin.energy.map((e) => ({ hour: e.hour, Actual: e.actual, Baseline: e.baseline }))} x="hour" series={[{ key: "Actual" }, { key: "Baseline", color: "#94a3b8" }]} height={240} xLabel="Hour" />
        </Card>
        <Card title="Zone temperatures" subtitle="Sampled floors × orientation (°C)">
          <div className="overflow-x-auto">
            <table className="w-full text-[11px]">
              <thead><tr><th className="th">Level</th>{zones.map((z) => <th key={z} className="th text-center">{z}</th>)}</tr></thead>
              <tbody>{levels.map((l) => <tr key={l}><td className="td num">L{l}</td>{zones.map((z) => { const v = twin.zones.find((q) => q.level === l && q.zone === z)!; return <td key={z} className="p-0.5"><div className="num rounded py-1 text-center font-semibold text-white" style={{ background: tColor(v.temp) }} title={`CO₂ ${v.co2} ppm · occupancy ${v.occupancy}%`}>{v.temp}</div></td>; })}</tr>)}</tbody>
            </table>
          </div>
        </Card>
      </div>
      <AssetRegister projectId={id} initial={assets} />
      <Card title="Operational optimisation" subtitle="Recommendations generated from anomalies, comfort and IAQ data" pad={false}>
        <ul className="divide-y divide-slate-100">{twin.recommendations.map((r) => <li key={r.title} className="flex flex-wrap items-start justify-between gap-2 px-4 py-3"><div><div className="text-sm font-medium">{r.title}</div><div className="text-xs text-slate-600">{r.detail}</div></div><span className="num text-sm font-semibold text-emerald-700">{fmt.money(r.saving)}/yr</span></li>)}</ul>
      </Card>
    </>
  );
}
