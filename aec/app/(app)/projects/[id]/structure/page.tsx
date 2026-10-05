import { LineViz } from "@/components/charts";
import { NoRun } from "@/components/no-run";
import { KV, Note } from "@/components/page";
import { Card, StatusBadge, Table } from "@/components/ui";
import { fmt } from "@/lib/format";
import { loadProject } from "@/lib/project-page";

export default async function Structure({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const { run } = await loadProject(id);
  if (!run) return <NoRun id={id} />;
  const s = run.structure, d = run.derived, p = run.params;
  const g = s.gravity;
  const profile = s.stories.map((st) => ({ level: st.level, "Story shear (kN)": Math.round(st.V), "ELF force (kN)": Math.round(st.F), "Seismic drift (%)": +(st.driftRatio * 100).toFixed(3), "Wind drift (%)": +((st.windDriftRatio ?? 0) * 100).toFixed(3) }));
  return (
    <>
      <div className="grid gap-4 lg:grid-cols-3">
        <Card title="Structural system" subtitle={s.system.row}>
          <KV cols={1} rows={[
            ["Lateral system", s.system.label], ["Material", p.material], ["Slab", `${p.slabSystem} ${Math.round(p.slabThickness * 1000)} mm`],
            ["Grid", `${p.baysX} × ${p.baysY} bays @ ${p.spanX} × ${p.spanY} m`], ["Core", `${p.coreWidth} × ${p.coreDepth} m, ${Math.round(p.coreWallThickness * 1000)} mm walls`],
            ["Columns (base)", `${Math.round(p.columnSize * 1000)} mm, f'c ${p.concreteGrade} MPa`], ["R / Cd / Ω₀", `${s.system.R} / ${s.system.Cd} / ${s.system.Omega0}`],
            ["Code path", s.prescriptive ? "Prescriptive (Table 12.2-1)" : "Performance-based design required"],
          ]} />
        </Card>
        <Card title="Load summary" subtitle="ASCE 7-22 Ch. 4, 7, 12, 26–27">
          <KV cols={1} rows={[
            ["Live load", `${d.liveLoad} kPa (+ partitions ${d.partition})`], ["Superimposed dead", `${d.sdl} kPa`], ["Roof snow pf", `${run.snow.pf} kPa`],
            ["Seismic weight W", `${fmt.n(s.W)} kN`], ["Seismic base shear V", `${fmt.n(s.Vbase)} kN (Cs ${s.Cs.toFixed(4)})`],
            ["Wind base shear", `${fmt.n(run.wind.baseShear)} kN`], ["Governing lateral", s.Vbase > run.wind.baseShear ? "Seismic" : "Wind"],
            ["Core share of base shear", s.coreShare ? fmt.pct(s.coreShare * 100, 0) : "—"],
          ]} />
        </Card>
        <Card title="Gravity design checks" subtitle="Hand checks run alongside the FE model">
          <ul className="space-y-2 text-sm">
            <li className="flex items-center justify-between gap-2"><span>Column axial (base, interior)<div className="text-[11px] text-slate-500">Pu {fmt.n(g.colAxialHand)} kN / φPn {fmt.n(g.colCapacity)} kN</div></span><StatusBadge status={g.colUtil <= 1 ? "PASS" : "FAIL"} label={g.colUtil.toFixed(2)} /></li>
            {g.punching && <li className="flex items-center justify-between gap-2"><span>Punching shear<div className="text-[11px] text-slate-500">vu {g.punching.vu} MPa / φvc {g.punching.phiVc} MPa</div></span><StatusBadge status={g.punching.util <= 1 ? "PASS" : "FAIL"} label={g.punching.util.toFixed(2)} /></li>}
            <li className="flex items-center justify-between gap-2"><span>Slab thickness (deflection)<div className="text-[11px] text-slate-500">min {Math.round(g.slabMin * 1000)} mm</div></span><StatusBadge status={p.slabThickness >= g.slabMin - 0.001 ? "PASS" : "WARN"} label={`${Math.round(p.slabThickness * 1000)} mm`} /></li>
            <li className="flex items-center justify-between gap-2"><span>Global equilibrium (ΣRy)<div className="text-[11px] text-slate-500">{fmt.n(g.sumRy)} vs {fmt.n(g.appliedGravity)} kN</div></span><StatusBadge status={Math.abs(g.sumRy - g.appliedGravity) / g.appliedGravity < 0.005 ? "PASS" : "FAIL"} label="balanced" /></li>
          </ul>
        </Card>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Story shear & ELF forces" subtitle={`Vertical distribution Cvx = w·hᵏ/Σw·hᵏ, k = ${s.k.toFixed(2)}; RSA scaled ×${s.rsaScale.toFixed(2)}`}>
          <LineViz data={profile} x="level" layout="vertical" series={[{ key: "Story shear (kN)" }, { key: "ELF force (kN)" }]} height={320} xLabel="kN" yLabel="Level" />
        </Card>
        <Card title="Inter-story drift ratio" subtitle={`Seismic (CQC × Cd/Ie) and wind; limit ${s.driftLimitRatio * 100}%`}>
          <LineViz data={profile} x="level" layout="vertical" series={[{ key: "Seismic drift (%)" }, { key: "Wind drift (%)" }]} height={320} xLabel="% of story height" yLabel="Level" refY={s.driftLimitRatio * 100} refLabel="limit" />
        </Card>
      </div>
      <Card title="Finite-element model" subtitle="Planar equivalent frame: lumped frame lines + core cantilever + rigid links / outriggers, 3 DOF per node, banded LDLᵀ solver">
        <KV cols={3} rows={[
          ["Nodes", fmt.n((p.floors + 1) * (p.baysX + 2))], ["Load cases", "D, L, ELF, wind, unit-load flexibility (×" + p.floors + ")"], ["Roof displacement (ELF)", `${(s.roofDispELF * 1000).toFixed(1)} mm`],
          ["Lateral stiffness", "Condensed via flexibility inversion"], ["Modal solver", "Jacobi eigen (M⁻¹ᐟ² K M⁻¹ᐟ²)"], ["Base moment in core", s.baseMomentCore ? `${fmt.n(s.baseMomentCore)} kN·m` : "—"],
        ]} />
      </Card>
      <Card title="Story results" subtitle="ELF forces, RSA-scaled shears, design drifts and stability coefficient" pad={false}>
        <Table head={["Level", "z (m)", "W (kN)", "Fx (kN)", "Vx (kN)", "δ (mm)", "Δ/h (%)", "θ", "Wind Δ/h (%)"]}>
          {[...s.stories].reverse().map((st) => (
            <tr key={st.level}>
              <td className="td num">L{st.level}</td><td className="td num">{st.z.toFixed(1)}</td><td className="td num">{fmt.n(st.W)}</td><td className="td num">{fmt.n(st.F)}</td><td className="td num">{fmt.n(st.V)}</td>
              <td className="td num">{(st.disp * 1000).toFixed(1)}</td><td className={`td num ${st.driftRatio > s.driftLimitRatio ? "font-semibold text-red-700" : ""}`}>{(st.driftRatio * 100).toFixed(3)}</td>
              <td className="td num">{st.theta.toFixed(3)}</td><td className="td num">{((st.windDriftRatio ?? 0) * 100).toFixed(3)}</td>
            </tr>
          ))}
        </Table>
      </Card>
      <Note>Simplified planar analysis for scheme design. Final design requires a 3D model with diaphragm flexibility, cracked-section calibration and member design by the engineer of record.</Note>
    </>
  );
}
