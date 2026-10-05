import Link from "next/link";
import { Badge } from "@/components/ui";
import { ProjectNav, RunButton } from "@/components/project-nav";
import { loadProject } from "@/lib/project-page";

export default async function ProjectLayout({ children, params }: { children: React.ReactNode; params: Promise<{ id: string }> }) {
  const { id } = await params;
  const { project, run } = await loadProject(id);
  return (
    <div>
      <div className="border-b border-slate-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 pt-5 sm:px-6 lg:px-8">
          <div className="text-xs text-slate-500"><Link href="/projects" className="hover:underline">Projects</Link> / {project.code}</div>
          <div className="mt-1 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div className="min-w-0">
              <h1 className="truncate text-xl font-semibold tracking-tight">{project.name}</h1>
              <div className="mt-1 flex flex-wrap items-center gap-1.5 text-xs text-slate-500">
                <Badge tone="blue">{project.stage}</Badge><Badge className="capitalize">{project.intake.buildingType}</Badge>
                <Badge>{project.intake.jurisdiction} · {project.intake.city}</Badge>
                <span>{run ? `Last run ${new Date(run.createdAt.replace(" ", "T") + "Z").toLocaleString("en-US", { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" })} · engine v${run.engineVersion}` : "Not analysed yet"}</span>
              </div>
            </div>
            <RunButton id={project.id} label={run ? "Re-run workflow" : "Run workflow"} />
          </div>
          <div className="mt-3"><ProjectNav id={project.id} /></div>
        </div>
      </div>
      <div className="mx-auto max-w-7xl space-y-5 px-4 py-6 sm:px-6 lg:px-8">{children}</div>
    </div>
  );
}
