import { AreaViz, BarViz } from "@/components/charts";
import { NoRun } from "@/components/no-run";
import { KV, SectionTitle } from "@/components/page";
import { Card, Stat, StatusBadge, Table } from "@/components/ui";
import { fmt } from "@/lib/format";
import { loadProject } from "@/lib/project-page";

export default async function Envelope({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const { project, run } = await loadProject(id);
  if (!run) return <NoRun id={id} />;
  const f = run.facade, ph = run.physics, en = run.energy;
  return (
    <>
      <SectionTitle sub={`${run.params.facadeType} · WWR ${Math.round(run.params.wwr * 100)}% · ${fmt.n(f.panels)} panels, ${f.panelTypes} types`}>Façade engineering</SectionTitle>
      <div className="grid gap-4 lg:grid-cols-3">
        <Card title="Structural">
          <KV cols={1} rows={[["Design pressure (field)", `±${f.designPressure} kPa`], ["Corner pressure", `${f.cornerPressure} kPa`], ["Mullion", f.mullion.selected], ["Mullion deflection", <StatusBadge key="m" status={f.mullion.deflection <= f.mullion.limit ? "PASS" : "FAIL"} label={`${f.mullion.deflection} / ${f.mullion.limit} mm`} />], ["Mullion stress ratio", f.mullion.stressRatio], ["Glass make-up", f.glass.make], ["Glass stress", `${f.glass.stress} / ${f.glass.allowable} MPa`], ["Anchor loads", `${f.anchor.dead} kN dead, ${f.anchor.wind} kN wind`]]} />
        </Card>
        <Card title="Thermal & moisture">
          <KV cols={1} rows={[["Glazing U", `${f.thermal.uGlazing} W/m²K`], ["Opaque U", `${f.thermal.uWall} W/m²K`], ["Ψ slab edge / window", `${f.thermal.psiSlab} / ${f.thermal.psiWindow} W/mK`], ["Effective façade U", `${f.thermal.uEffective} W/m²K`], ["Worst surface temp", `${f.thermal.surfaceTemp} °C`], ["fRsi vs required", <StatusBadge key="f" status={f.thermal.condensation ? "FAIL" : "PASS"} label={`${f.thermal.fRsi} / ${f.thermal.fRsiMin}`} />], ["Water test pressure", `${f.waterTest} kPa (AAMA 501.1)`]]} />
        </Card>
        <Card title="Façade fire risk">
          <div className="flex items-start gap-2 text-sm"><StatusBadge status={f.fire.combustible && run.derived.height > 18 ? "FAIL" : "PASS"} label={f.fire.combustible ? "combustible" : "non-combustible"} /><p className="text-slate-600">{f.fire.note}</p></div>
          <div className="mt-3"><KV cols={1} rows={[["NFPA 285 testing", f.fire.nfpa285 ? "Required for combustible components" : "Not triggered"], ["Building height", `${run.derived.height.toFixed(1)} m`]]} /></div>
        </Card>
      </div>
      <SectionTitle sub="Daylight, glare, natural ventilation, acoustics and comfort">Building physics</SectionTitle>
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <Stat label="Average daylight factor" value={`${ph.daylightFactor}%`} hint={`${ph.daylitArea}% of NLA daylit`} />
        <Stat label="Glare risk" value={ph.glareRisk.split(" ")[0]} hint={ph.glareRisk} tone={ph.glareRisk.startsWith("High") ? "warn" : "good"} />
        <Stat label="Façade sound insulation" value={`Rw ${ph.acoustics.providedRw}`} hint={`Required Rw ${ph.acoustics.requiredRw} for ${ph.acoustics.indoorTarget} dB(A) inside`} tone={ph.acoustics.providedRw >= ph.acoustics.requiredRw ? "good" : "bad"} />
        <Stat label="Natural ventilation" value={ph.natVentFeasible ? "Feasible" : "Mixed-mode"} hint={`Effective depth ≤ ${ph.natVentDepth} m (5 × floor height)`} />
      </div>
      <SectionTitle sub={`${fmt.n(en.totalMWh)} MWh/yr · grid factor ${en.gridFactor} kgCO₂e/kWh`}>Energy simulation</SectionTitle>
      <div className="grid gap-4 lg:grid-cols-3">
        <Card title="Monthly energy balance" subtitle="MWh — heating, cooling, other end-uses and PV generation" className="lg:col-span-2">
          <AreaViz data={en.monthly.map((m) => ({ month: m.month, Heating: m.heating, Cooling: m.cooling, Other: m.other }))} x="month" series={[{ key: "Heating" }, { key: "Cooling" }, { key: "Other" }]} stacked height={260} />
        </Card>
        <Card title="Annual performance">
          <KV cols={1} rows={[["EUI", `${en.eui} kWh/m²·yr`], ["Net EUI (after PV)", `${en.netEui} kWh/m²·yr`], ["Target", `${project.intake.targetEUI} kWh/m²·yr`], ["PV offset", `${en.pvOffset}%`], ["Operational carbon", `${en.operationalCarbon} kgCO₂e/m²·yr`]]} />
          <div className="mt-3"><BarViz data={en.breakdown.map((b) => ({ name: b.end, MWh: Math.round(b.kWh / 1000) }))} x="name" series={[{ key: "MWh" }]} horizontal height={240} /></div>
        </Card>
      </div>
      <Card title="Operating-energy scenarios" subtitle="Each scenario re-simulated with the same weather and schedules" pad={false}>
        <Table head={["Scenario", "EUI (kWh/m²·yr)", "Operational carbon (kg/m²·yr)", "vs proposed"]}>
          {en.scenarios.map((s) => <tr key={s.name}><td className="td font-medium">{s.name}</td><td className="td num">{s.eui}</td><td className="td num">{s.carbon}</td><td className={`td num ${s.eui < en.scenarios[0].eui ? "text-emerald-700" : s.eui > en.scenarios[0].eui ? "text-red-700" : ""}`}>{s.name === "Proposed" ? "—" : `${s.eui > en.scenarios[0].eui ? "+" : ""}${(s.eui - en.scenarios[0].eui).toFixed(1)}`}</td></tr>)}
        </Table>
      </Card>
    </>
  );
}
