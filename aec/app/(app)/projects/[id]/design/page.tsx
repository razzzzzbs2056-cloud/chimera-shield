import { DesignStudio } from "@/components/design-studio";
import { NoRun } from "@/components/no-run";
import { Badge, Card, StatusBadge, Table } from "@/components/ui";
import { fmt } from "@/lib/format";
import { loadProject } from "@/lib/project-page";
import { listBoreholes, listOptions, standards } from "@/lib/repo";

export default async function Design({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const { user, project, run } = await loadProject(id);
  if (!run) return <NoRun id={id} />;
  const k = run.kpis;
  const baseline = { params: run.params, system: run.system, cost: k.cost, carbon: k.embodiedCarbon, nla: k.nla, efficiency: k.efficiency, daylight: run.physics.daylitArea, drift: k.maxDrift, driftLimit: k.driftLimit, eui: k.eui, months: k.durationMonths, fails: k.fail, clashes: k.clashes, T1: k.T1 };
  return (
    <>
      <DesignStudio ctx={{ id, name: project.name, code: project.code, intake: project.intake, boreholes: listBoreholes(user.id, id) ?? [], standards: standards(), pins: project.pins }}
        params={project.params} baseline={baseline} initialOptions={listOptions(user.id, id) ?? []} />
      <Card title="Automatic structural system selection" subtitle={`Each candidate analysed with the FE model for SDC ${run.seismic.sdc}; ranked by cost, carbon, usable area and code path`} pad={false}>
        <Table head={["Rank", "System", "R / Cd", "Height limit", "T₁ (s)", "Drift %", "Structure cost", "Carbon (t)", "Code path", "Status"]}>
          {run.selection.map((r, i) => (
            <tr key={r.id} className={r.id === run.system ? "bg-brand-50/50" : undefined}>
              <td className="td num">{r.feasible ? i + 1 : "—"}</td>
              <td className="td font-medium">{r.label}{r.id === run.system && <Badge tone="blue" className="ml-1.5">selected</Badge>}</td>
              <td className="td num">{r.R} / {r.Cd}</td>
              <td className="td num">{r.limit === null ? "NL" : `${r.limit} m`}</td>
              <td className="td num">{r.T1 ?? "—"}</td>
              <td className="td num">{r.drift ?? "—"}</td>
              <td className="td num">{r.cost ? fmt.money(r.cost) : "—"}</td>
              <td className="td num">{r.carbon ? fmt.n(r.carbon) : "—"}</td>
              <td className="td text-xs">{r.prescriptive ? "Prescriptive" : "Performance-based"}</td>
              <td className="td"><StatusBadge status={r.feasible ? "PASS" : "FAIL"} label={r.feasible ? `score ${r.score}` : "infeasible"} /><div className="mt-0.5 text-[11px] text-slate-500">{r.reason}</div></td>
            </tr>
          ))}
        </Table>
        {run.selection.length === 0 && <p className="px-4 py-6 text-sm text-slate-500">System fixed by the brief ({run.system}); set lateral system to “auto” to compare.</p>}
      </Card>
    </>
  );
}
