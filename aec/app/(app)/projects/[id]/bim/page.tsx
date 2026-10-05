import { BimViewer } from "@/components/bim-viewer";
import { IssuesManager } from "@/components/issues-manager";
import { NoRun } from "@/components/no-run";
import { KV, Note } from "@/components/page";
import { Card, Stat } from "@/components/ui";
import { fmt } from "@/lib/format";
import { loadProject } from "@/lib/project-page";
import { listIssues } from "@/lib/repo";

export default async function Bim({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const { user, run } = await loadProject(id);
  if (!run) return <NoRun id={id} />;
  const issues = listIssues(user.id, id) ?? [];
  const phys = run.clashes.filter((c) => c.type === "physical"), sem = run.clashes.filter((c) => c.type === "semantic");
  return (
    <>
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <Stat label="IFC elements" value={fmt.n(run.bim.elements)} hint={`${run.bim.levels} levels · IFC4 openBIM`} />
        <Stat label="Physical clash groups" value={phys.length} hint={`${phys.filter((c) => c.severity === "critical").length} critical (structure)`} tone={phys.some((c) => c.severity === "critical") ? "bad" : "good"} />
        <Stat label="Semantic clashes" value={sem.length} hint="Access, clearance, penetrations, wet-over-electrical" tone={sem.some((c) => c.severity !== "minor") ? "warn" : "good"} />
        <Stat label="Open coordination issues" value={issues.filter((i) => i.status !== "resolved").length} hint={`${issues.filter((i) => i.type === "rfi").length} RFIs`} />
      </div>
      <div className="grid gap-4 xl:grid-cols-3">
        <Card title="Federated model" subtitle="Architecture · structure · MEP · fire — generated from the parametric scheme and sized engineering outputs" className="xl:col-span-2">
          <BimViewer projectId={id} ifcHref={`/api/projects/${id}/ifc`} />
        </Card>
        <Card title="Model contents" pad={false}>
          <div className="p-4"><KV cols={1} rows={Object.entries(run.bim.byType).sort((a, b) => b[1] - a[1]).map(([k, v]) => [k, fmt.n(v)])} /></div>
        </Card>
      </div>
      <IssuesManager projectId={id} initial={issues} />
      <Note>Clash detection runs automatically on every workflow run: physical AABB tests between disciplines, plus semantic rules (maintenance clearance, valve access height, penetrations through lateral elements, fire dampers, riser space, wet services over switchrooms). Clashes that disappear after a design change are auto-resolved.</Note>
    </>
  );
}
