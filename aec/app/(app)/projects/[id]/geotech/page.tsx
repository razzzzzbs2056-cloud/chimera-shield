import { BoreholeManager } from "@/components/borehole-manager";
import { PointCloud, SoilColumns } from "@/components/eng-charts";
import { NoRun } from "@/components/no-run";
import { KV, Note } from "@/components/page";
import { Badge, Card, Stat, StatusBadge, Table } from "@/components/ui";
import { fmt } from "@/lib/format";
import { loadProject } from "@/lib/project-page";
import { listBoreholes } from "@/lib/repo";

export default async function Geotech({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const { user, run } = await loadProject(id);
  const holes = listBoreholes(user.id, id) ?? [];
  const g = run?.geotech;
  return (
    <>
      {g && (
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <Stat label="Vs30 → Site class" value={`${g.vs30} m/s`} hint={`Site Class ${g.siteClass} (ASCE 7-22 Table 20.2-1)`} />
          <Stat label="Allowable bearing" value={fmt.n(g.qall)} unit="kPa" hint={`at ${g.foundingDepth} m in ${g.foundingSoil}, FS 3`} />
          <Stat label="Liquefaction" value={g.liquefactionRisk} hint={g.liquefiedThickness ? `${g.liquefiedThickness} m liquefiable (FS < 1)` : "No triggering at design PGA"} tone={g.liquefactionRisk === "high" ? "bad" : g.liquefactionRisk === "low" ? "warn" : "good"} />
          <Stat label="Selected foundation" value={g.selected.label.split(" ")[0]} hint={`${g.selected.label} · ${g.selected.settlement} mm`} />
        </div>
      )}
      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Borehole logs" subtitle="Create, edit and delete logs; re-run to update the interpretation"><BoreholeManager projectId={id} initial={holes} /></Card>
        <Card title="Interpreted soil profile">{g ? <SoilColumns holes={g.profile} foundingDepth={g.foundingDepth} /> : <p className="text-sm text-slate-500">Run the workflow to interpret the logs.</p>}</Card>
      </div>
      {!run || !g ? <NoRun id={id} /> : (
        <>
          <div className="grid gap-4 lg:grid-cols-2">
            <Card title="Liquefaction triggering" subtitle="Simplified procedure (Youd et al. 2001), Mw 7.5, PGA = 0.4·SDS">
              {g.liquefaction.length ? <PointCloud data={g.liquefaction.map((r) => ({ FS: Math.min(r.FS, 3), depth: r.depth, liq: r.liquefiable ? 1 : 0 }))} x="FS" y="depth" xLabel="Factor of safety (capped at 3)" yLabel="Depth (m)" reversedY flag="liq" refX={1} />
                : <p className="py-10 text-center text-sm text-slate-500">No saturated granular layers within 20 m.</p>}
            </Card>
            <Card title="Bearing & settlement">
              <KV cols={1} rows={[["Founding depth", `${g.foundingDepth} m`], ["Ultimate bearing qult", `${fmt.n(g.qult)} kPa`], ["Allowable (FS 3)", `${fmt.n(g.qall)} kPa`], ["Net raft pressure", `${fmt.n(g.bearingPressure)} kPa`], ["Raft settlement (2:1)", `${g.raftSettlement} mm`], ["Raft settlement (Boussinesq)", `${g.raftSettlementBoussinesq} mm`], ["Dewatering required", g.dewatering ? `Yes — GWL ${g.gwlMin} m above formation` : "No"], ["Pile design", `Ø${g.pile.diameter} m × ${g.pile.length} m, ${fmt.n(g.pile.capacity)} kN working (shaft ${fmt.n(g.pile.shaft)} + base ${fmt.n(g.pile.base)} kN ult.)`]]} />
            </Card>
          </div>
          <Card title="Foundation optimiser" subtitle="Five systems compared on capacity, settlement, cost, carbon and duration" pad={false}>
            <Table head={["System", "Feasible", "Settlement", "Differential", "Cost", "Carbon (t)", "Duration", "Score", "Notes"]}>
              {[...g.options].sort((a, b) => b.score - a.score).map((o) => (
                <tr key={o.id} className={o.id === g.selected.id ? "bg-brand-50/50" : undefined}>
                  <td className="td font-medium">{o.label}{o.id === g.selected.id && <Badge tone="blue" className="ml-1.5">selected</Badge>}</td>
                  <td className="td"><StatusBadge status={o.feasible && o.capacityOK ? "PASS" : "FAIL"} label={o.feasible && o.capacityOK ? "yes" : "no"} /></td>
                  <td className="td num">{o.settlement} mm</td><td className="td num">{o.differential} mm</td><td className="td num">{fmt.money(o.cost)}</td><td className="td num">{o.carbon}</td><td className="td num">{o.durationWeeks} wk</td>
                  <td className="td num font-semibold">{o.score || "—"}</td><td className="td text-xs text-slate-500">{o.notes.join("; ")}</td>
                </tr>
              ))}
            </Table>
          </Card>
          <Card title="Liquefaction results" pad={false}>
            <Table head={["Borehole", "Depth (m)", "Soil", "(N₁)₆₀cs", "CSR", "CRR·MSF", "FS", ""]}>
              {g.liquefaction.map((r, i) => <tr key={i}><td className="td">{r.borehole}</td><td className="td num">{r.depth}</td><td className="td">{r.soil}</td><td className="td num">{r.N160}</td><td className="td num">{r.CSR}</td><td className="td num">{r.CRR}</td><td className="td num">{r.FS}</td><td className="td"><StatusBadge status={r.liquefiable ? "FAIL" : "PASS"} label={r.liquefiable ? "liquefies" : "OK"} /></td></tr>)}
            </Table>
          </Card>
          <Note>Correlations (Imai Vs–N, α/β pile methods, simplified liquefaction) are screening-level. A geotechnical engineer must confirm with site-specific testing (CPT, shear-wave, lab consolidation).</Note>
        </>
      )}
    </>
  );
}
