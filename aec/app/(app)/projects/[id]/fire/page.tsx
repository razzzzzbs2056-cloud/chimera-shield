import { AreaViz } from "@/components/charts";
import { NoRun } from "@/components/no-run";
import { KV, SectionTitle } from "@/components/page";
import { Card, Stat, StatusBadge, Table } from "@/components/ui";
import { fmt } from "@/lib/format";
import { loadProject } from "@/lib/project-page";

export default async function Fire({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const { run } = await loadProject(id);
  if (!run) return <NoRun id={id} />;
  const f = run.fire, p = run.params;
  return (
    <>
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <Stat label="Occupant load" value={fmt.n(f.occupantLoadFloor)} unit="/ floor" hint={`${fmt.n(f.occupantLoadTotal)} total · ${run.derived.occupancyGroup}`} />
        <Stat label="Exit stairs" value={`${f.exitsProvided} × ${p.stairWidth} m`} hint={`${f.exitsRequired} required · ${f.stairWidthRequired} m capacity needed`} tone={f.exitsProvided >= f.exitsRequired && f.stairWidthProvided >= f.stairWidthRequired ? "good" : "bad"} />
        <Stat label="Travel distance" value={f.travelDistance} unit="m" hint={`Limit ${f.travelLimit} m · common path ${f.commonPath} m`} tone={f.travelDistance <= f.travelLimit ? "good" : "bad"} />
        <Stat label="RSET / ASET" value={`${Math.round(f.evacuation.rset / 60)} / ${Math.round(f.evacuation.aset / 60)}`} unit="min" hint={f.evacuation.strategy} tone={f.evacuation.aset >= 1.5 * f.evacuation.rset ? "good" : f.evacuation.aset >= f.evacuation.rset ? "warn" : "bad"} />
      </div>
      <div className="grid gap-4 lg:grid-cols-3">
        <Card title="Evacuation model" subtitle="SFPE hydraulic model — simultaneous full-building evacuation curve" className="lg:col-span-2">
          <AreaViz data={f.evacuation.curve.map((c) => ({ "time (s)": c.t, "Occupants remaining": c.remaining }))} x="time (s)" series={[{ key: "Occupants remaining" }]} height={240} />
          <KV cols={3} rows={[["Detection & alarm", `${f.evacuation.detection} s`], ["Pre-movement", `${f.evacuation.preMovement} s`], ["Flow-limited time", `${f.evacuation.flowLimited} s`], ["Full evacuation", `${Math.round(f.evacuation.full / 60)} min`], ["Phased (fire floor ±1)", `${Math.round(f.evacuation.phased / 60)} min`], ["Smoke layer ASET", `${Math.round(f.evacuation.aset / 60)} min`]]} />
        </Card>
        <Card title="Fire protection systems">
          <KV cols={1} rows={[["Construction type", `IBC Type ${f.constructionType}`], ["Height limit", f.maxHeight ? `${f.maxHeight} m` : "Unlimited"], ["Sprinklers", f.sprinklers.provided ? `Yes — ${f.sprinklers.hazard}` : f.sprinklers.required ? "REQUIRED — not provided" : "Not required"], ["Design density", `${f.sprinklers.designDensity} mm/min`], ["Heads (approx.)", fmt.n(f.sprinklers.heads)], ["Fire pump", `${f.sprinklers.pumpFlow} L/s`], ["Standpipes", f.standpipes ? "Class I in every stair" : "Not required"], ["Fire-service lifts", f.fireServiceLift ? "2 required" : "Not required"], ["Smoke control", f.smokeControl], ["Compartment", `${fmt.n(f.compartmentArea)} m² per floor`]]} />
        </Card>
      </div>
      <Card title="Fire-resistance ratings" pad={false}>
        <Table head={["Building element", "Required FRR", "Basis"]}>{f.frr.map((r) => <tr key={r.element}><td className="td">{r.element}</td><td className="td num">{r.hours} h</td><td className="td text-xs text-slate-500">IBC Table 601 / §713 — Type {f.constructionType}</td></tr>)}</Table>
      </Card>
      <SectionTitle sub="Accessible routes, lifts, gradients and facilities">Accessibility checker</SectionTitle>
      <Card pad={false}>
        <Table head={["Item", "Required", "Provided", "Clause", "Status"]}>
          {run.accessibility.map((a) => <tr key={a.item}><td className="td font-medium">{a.item}</td><td className="td">{a.required}</td><td className="td">{a.provided}</td><td className="td text-xs">{a.clause}</td><td className="td"><StatusBadge status={a.ok ? "PASS" : "FAIL"} /></td></tr>)}
        </Table>
      </Card>
    </>
  );
}
