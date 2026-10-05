import { LineViz } from "@/components/charts";
import { MultiLine } from "@/components/eng-charts";
import { NoRun } from "@/components/no-run";
import { KV, Note, SectionTitle } from "@/components/page";
import { Badge, Card, StatusBadge, Table } from "@/components/ui";
import { designSa } from "@/lib/engine/site";
import { fmt } from "@/lib/format";
import { loadProject } from "@/lib/project-page";

export default async function SeismicWind({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const { run } = await loadProject(id);
  if (!run) return <NoRun id={id} />;
  const s = run.structure, seis = run.seismic, w = run.wind;
  const spectrum = Array.from({ length: 80 }, (_, i) => { const T = i * 0.075; return { T: +T.toFixed(3), Sa: +designSa(T, seis).toFixed(4) }; });
  const modes = s.modal.periods.slice(0, 8).map((T, i) => ({ T: +T.toFixed(3), Sa: +designSa(T, seis).toFixed(4), mode: i + 1 }));
  const po = s.pushover;
  const sdMax = Math.max(...po.capacity.map((c) => c.Sd)) * 1.6;
  const hist = s.history;
  const windRows = w.stories.filter((_, i, a) => a.length < 25 || i % Math.ceil(a.length / 25) === 0 || i === a.length - 1);
  const faces = ["Windward", "Side", "Leeward", "Corner"];
  const zs = [...new Set(w.heatmap.map((h) => h.z))].sort((a, b) => b - a);
  const maxAbs = Math.max(...w.heatmap.map((h) => Math.abs(h.p)));
  const heat = (v: number) => (v >= 0 ? `rgba(42,120,214,${0.15 + 0.75 * (v / maxAbs)})` : `rgba(227,73,72,${0.15 + 0.75 * (-v / maxAbs)})`);
  return (
    <>
      <SectionTitle sub={`Site Class ${seis.siteClass} · SDC ${seis.sdc} · Risk Category ${run.derived.riskCategory} (Ie ${run.derived.Ie})`}>Earthquake engineering</SectionTitle>
      <div className="grid gap-4 lg:grid-cols-3">
        <Card title="Design response spectrum" subtitle="ASCE 7-22 §11.4.5 with modal periods marked" className="lg:col-span-2">
          <MultiLine sets={[{ name: "Design spectrum Sa", data: spectrum }, { name: "Modal periods", data: modes, color: "#eb6834", points: true }]} x="T" y="Sa" xLabel="Period T (s)" yLabel="Sa (g)" refX={{ v: +s.T1.toFixed(2), label: `T₁ ${s.T1.toFixed(2)} s` }} />
        </Card>
        <Card title="Seismic parameters">
          <KV cols={1} rows={[["Ss / S1", `${(seis.SMS / seis.Fa).toFixed(2)} / ${(seis.SM1 / seis.Fv).toFixed(2)} g`], ["Fa / Fv", `${seis.Fa} / ${seis.Fv}`], ["SDS / SD1", `${seis.SDS} / ${seis.SD1} g`], ["T₀ / Ts", `${seis.T0} / ${seis.Ts} s`], ["Ta / CuTa", `${s.Ta.toFixed(2)} / ${s.CuTa.toFixed(2)} s`], ["T₁ (modal)", `${s.T1.toFixed(2)} s`], ["Cs", s.Cs.toFixed(4)], ["V (ELF) / Vrsa", `${fmt.n(s.Vbase)} / ${fmt.n(s.Vrsa)} kN`], ["Torsion", `${s.torsionRatio.toFixed(2)} — ${s.torsionClass}`], ["Max θ (P-Δ)", `${s.maxTheta.toFixed(3)} ≤ ${s.thetaMax.toFixed(3)}`]]} />
        </Card>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Modal analysis" subtitle="Eigenvalue solution of the condensed lateral stiffness, lumped floor masses" pad={false}>
          <Table head={["Mode", "Period (s)", "Mass ratio", "Cumulative", "|Γ| (roof = 1)"]}>
            {s.modal.periods.slice(0, 8).map((T, i) => (
              <tr key={i}><td className="td num">{i + 1}</td><td className="td num">{T.toFixed(3)}</td><td className="td num">{(s.modal.massRatios[i] * 100).toFixed(1)}%</td><td className="td num">{(s.modal.cumMass[i] * 100).toFixed(1)}%</td><td className="td num">{Math.abs(s.modal.gammas[i]).toFixed(3)}</td></tr>
            ))}
          </Table>
        </Card>
        <Card title="Pushover — capacity spectrum method" subtitle={`MCE demand reduced for β_eff ${(po.perfPoint.beff * 100).toFixed(1)}% (FEMA 440)`} action={<Badge tone={po.level === "Immediate Occupancy" ? "green" : po.level === "Life Safety" ? "blue" : "red"}>{po.level}</Badge>}>
          <MultiLine sets={[{ name: "Capacity", data: po.capacity.map((c) => ({ Sd: +(c.Sd * 1000).toFixed(1), Sa: +c.Sa.toFixed(4) })) }, { name: "Reduced MCE demand", data: po.demand.filter((c) => c.Sd <= sdMax).map((c) => ({ Sd: +(c.Sd * 1000).toFixed(1), Sa: +c.Sa.toFixed(4) })), color: "#eb6834", dashed: true }]}
            x="Sd" y="Sa" xLabel="Spectral displacement Sd (mm)" yLabel="Sa (g)" height={240} />
          <p className="mt-1 text-xs text-slate-500">Performance point: roof drift {(po.perfPoint.driftRatio * 100).toFixed(2)}%, base shear {fmt.n(po.perfPoint.V)} kN (Vy {fmt.n(po.Vy)} kN).</p>
        </Card>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Response-history analysis" subtitle={`Spectrum-scaled synthetic record, PGA ${hist.pga} g · Newmark-β MDOF, 5% Rayleigh damping`}>
          <LineViz data={hist.roof.map((r) => ({ t: r.t, "Roof displacement (mm)": r.u }))} x="t" xType="number" series={[{ key: "Roof displacement (mm)" }]} height={200} xLabel="Time (s)" />
          <KV rows={[["Peak roof displacement", `${(hist.peakRoof * 1000).toFixed(0)} mm`], ["Peak drift (elastic)", `${(hist.peakDriftRatio * 100).toFixed(2)}%`], ["Peak elastic base shear", `${fmt.n(hist.peakBaseShearElastic)} kN`], ["Implied R demand", (hist.peakBaseShearElastic / s.Vbase).toFixed(1)]]} />
        </Card>
        <Card title="Nonlinear equivalent-SDOF response" subtitle="Bilinear kinematic hysteresis calibrated to the pushover backbone">
          <MultiLine sets={[{ name: "Hysteresis", data: hist.nl.hysteresis.map((h) => ({ d: h.d, f: h.f })) }]} x="d" y="f" xLabel="Roof displacement (mm)" yLabel="Base shear (kN)" height={200} />
          <KV rows={[["Peak displacement", `${(hist.nl.peakDisp * 1000).toFixed(0)} mm`], ["Ductility demand μ", hist.nl.ductility.toFixed(2)], ["Residual displacement", `${(hist.nl.residual * 1000).toFixed(0)} mm`], ["System ductility capacity", `${s.system.mu}`]]} />
        </Card>
      </div>

      <SectionTitle sub={`V = ${w.V} m/s, Exposure ${w.exposure}, Kd ${w.Kd} · n₁ = ${w.n1} Hz (${w.flexible ? "flexible" : "rigid"})`}>Wind engineering</SectionTitle>
      <div className="grid gap-4 lg:grid-cols-3">
        <Card title="Pressure profile" subtitle="Windward qz·Kd·G·Cp and leeward suction" className="lg:col-span-2">
          <LineViz data={w.stories.map((st) => ({ z: +st.z.toFixed(1), "Windward (kPa)": st.pw, "Leeward (kPa)": Math.abs(st.pl) }))} x="z" layout="vertical" series={[{ key: "Windward (kPa)" }, { key: "Leeward (kPa)" }]} height={280} xLabel="kPa" yLabel="Height (m)" />
        </Card>
        <Card title="Serviceability & dynamics">
          <ul className="space-y-2.5 text-sm">
            <li className="flex justify-between gap-2"><span>Gust-effect factor<div className="text-[11px] text-slate-500">Iz {w.gustDetail.Iz} · Q {w.gustDetail.Q} · R {w.gustDetail.R}</div></span><b className="num">{w.G}</b></li>
            <li className="flex justify-between gap-2"><span>Roof drift (design wind)<div className="text-[11px] text-slate-500">limit H/400</div></span><StatusBadge status={w.roofDrift <= 1 / 400 ? "PASS" : "WARN"} label={`H/${Math.round(1 / Math.max(w.roofDrift, 1e-9))}`} /></li>
            <li className="flex justify-between gap-2"><span>Peak acceleration (10-yr)<div className="text-[11px] text-slate-500">limit {w.accel.limit} m/s²</div></span><StatusBadge status={w.accel.peak <= w.accel.limit ? "PASS" : "FAIL"} label={`${w.accel.mg} milli-g`} /></li>
            <li className="flex justify-between gap-2"><span>Vortex shedding<div className="text-[11px] text-slate-500">vcrit {w.vortex.vcrit} m/s vs 1.25·vm {(w.vortex.vm * 1.25).toFixed(1)}</div></span><StatusBadge status={w.vortex.check ? "WARN" : "PASS"} label={w.vortex.check ? "check" : "OK"} /></li>
            <li className="flex justify-between gap-2"><span>Base overturning moment</span><b className="num">{fmt.n(w.baseMoment / 1000)} MN·m</b></li>
          </ul>
        </Card>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Façade pressure map" subtitle="Net design pressures by face and height (kPa) — screening ahead of wind-tunnel / CFD">
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead><tr><th className="th">z (m)</th>{faces.map((f) => <th key={f} className="th text-center">{f}</th>)}</tr></thead>
              <tbody>
                {zs.map((z) => (
                  <tr key={z}><td className="td num">{z}</td>{faces.map((f) => { const v = w.heatmap.find((h) => h.face === f && h.z === z)!.p; return <td key={f} className="num px-1 py-1"><div className="rounded px-2 py-1.5 text-center font-semibold text-slate-900" style={{ background: heat(v) }}>{v.toFixed(2)}</div></td>; })}</tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
        <Card title="Pedestrian wind comfort" subtitle="Lawson LDDC criteria, 5% exceedance (screening)" pad={false}>
          <Table head={["Location", "Speed (m/s)", "Category"]}>
            {w.pedestrian.map((r) => <tr key={r.location}><td className="td">{r.location}</td><td className="td num">{r.speed}</td><td className="td"><Badge tone={r.category === "Sitting" || r.category === "Standing" ? "green" : r.category === "Walking" ? "amber" : "red"}>{r.category}</Badge></td></tr>)}
          </Table>
          <div className="border-t border-slate-100 p-4"><Table head={["Story", "z", "Kz", "qz (kPa)", "F (kN)", "V (kN)"]}>{windRows.map((r) => <tr key={r.level}><td className="td num">L{r.level}</td><td className="td num">{r.z.toFixed(1)}</td><td className="td num">{r.Kz}</td><td className="td num">{r.qz}</td><td className="td num">{fmt.n(r.F)}</td><td className="td num">{fmt.n(r.V)}</td></tr>)}</Table></div>
        </Card>
      </div>
      <Note>Wind accelerations, vortex shedding and pedestrian comfort are code-based screenings. Buildings with n₁ &lt; 1 Hz, height &gt; 120 m or complex surroundings should be wind-tunnel tested (HFFB/HFPI) or analysed with validated CFD.</Note>
    </>
  );
}
