import Link from "next/link";
import { FindingsTable } from "@/components/findings-table";
import { NoRun } from "@/components/no-run";
import { Note } from "@/components/page";
import { Badge, Card, Stat, Table } from "@/components/ui";
import { loadProject } from "@/lib/project-page";

export default async function Compliance({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const { project, run } = await loadProject(id);
  if (!run) return <NoRun id={id} />;
  const k = run.kpis;
  const proxies = run.findings.filter((f) => f.proxy).length;
  return (
    <>
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <Stat label="Checks evaluated" value={run.findings.length} hint={`${run.codes.length} applicable standards`} />
        <Stat label="Failing" value={k.fail} tone={k.fail ? "bad" : "good"} hint={k.fail ? "Design action required" : "None"} />
        <Stat label="Warnings" value={k.warn} tone={k.warn ? "warn" : "good"} hint="Engineering judgement / PBD" />
        <Stat label="Proxy clauses" value={proxies} hint={proxies ? `Local ${project.intake.jurisdiction} clause not encoded — verified by method` : "All clauses local"} tone={proxies ? "warn" : "good"} />
      </div>
      <Card title="Code intelligence & version control" subtitle={`Standards applicable to ${project.intake.jurisdiction} · ${run.derived.occupancyGroup} · ${run.derived.highRise ? "high-rise" : "non-high-rise"} — editions resolved from the code library`} pad={false} action={<Link href="/codes" className="text-xs font-medium text-brand-700 hover:underline">Manage library</Link>}>
        <Table head={["Standard", "Edition used", "Status", "Why it applies", "Version control"]}>
          {run.codes.map((c) => (
            <tr key={c.code}>
              <td className="td"><div className="font-medium">{c.code}</div><div className="text-[11px] text-slate-500">{c.title}</div></td>
              <td className="td num">{c.edition}{c.pinned && <Badge tone="violet" className="ml-1.5">pinned</Badge>}</td>
              <td className="td"><Badge tone={c.status === "current" ? "green" : c.status === "superseded" ? "red" : "amber"}>{c.status === "draft" ? "pending adoption" : c.status}</Badge></td>
              <td className="td text-xs">{c.reason}</td>
              <td className="td text-xs">{c.versionIssue ? <span className="text-amber-800">{c.versionIssue}</span> : <span className="text-emerald-700">Up to date</span>}</td>
            </tr>
          ))}
        </Table>
      </Card>
      <FindingsTable findings={run.findings} csvHref={`/api/projects/${id}/export?type=findings`} />
      <Note>Clause references identify where each requirement lives; values and limits are computed by the engine. Always confirm against the licensed, adopted edition and local amendments — findings are decision support, not a permit review.</Note>
    </>
  );
}
