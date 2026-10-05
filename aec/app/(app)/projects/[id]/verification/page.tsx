import { NoRun } from "@/components/no-run";
import { Note } from "@/components/page";
import { Badge, Card, Stat, StatusBadge, Table } from "@/components/ui";
import { fmt } from "@/lib/format";
import { loadProject } from "@/lib/project-page";

export default async function Verification({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const { run } = await loadProject(id);
  if (!run) return <NoRun id={id} />;
  const v = run.verification;
  const n = (s: string) => v.filter((x) => x.status === s).length;
  return (
    <>
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <Stat label="Independent cross-checks" value={v.length} hint="Different method, same quantity" />
        <Stat label="Agree within tolerance" value={n("PASS")} tone="good" hint={`${fmt.pct((n("PASS") / v.length) * 100, 0)} of checks`} />
        <Stat label="Discrepancies (review)" value={n("WARN")} tone={n("WARN") ? "warn" : "good"} hint="Flagged for engineer review" />
        <Stat label="Failures" value={n("FAIL")} tone={n("FAIL") ? "bad" : "good"} hint="Model or input error suspected" />
      </div>
      <Card title="Independent verification" subtitle="The verifier agent re-derives key results by a second method and compares — LLMs never produce the numbers" pad={false}>
        <Table head={["Discipline", "Quantity", "Method A (primary)", "Method B (independent)", "Deviation", "Tolerance", "Result"]}>
          {v.map((x) => (
            <tr key={x.check}>
              <td className="td"><Badge>{x.discipline}</Badge></td>
              <td className="td font-medium">{x.check}</td>
              <td className="td text-xs"><div className="num font-semibold text-slate-900">{fmt.n(x.valueA, Math.abs(x.valueA) < 10 ? 3 : 0)} {x.unit}</div>{x.methodA}</td>
              <td className="td text-xs"><div className="num font-semibold text-slate-900">{fmt.n(x.valueB, Math.abs(x.valueB) < 10 ? 3 : 0)} {x.unit}</div>{x.methodB}</td>
              <td className="td num">{x.deviation}%</td><td className="td num">{x.tolerance}</td>
              <td className="td"><StatusBadge status={x.status} label={x.status === "PASS" ? "agrees" : x.status === "WARN" ? "review" : "mismatch"} /></td>
            </tr>
          ))}
        </Table>
      </Card>
      <Note>Verification compares numbers produced by deterministic solvers using independent formulations (equilibrium, Rayleigh quotient vs eigen-solution, statics vs FE, Boussinesq vs 2:1 spread, element volumes vs parametric QTO, CPM closure). A licensed engineer must still review and seal the design.</Note>
    </>
  );
}
