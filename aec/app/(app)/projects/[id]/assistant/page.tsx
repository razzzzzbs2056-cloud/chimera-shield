import { Assistant } from "@/components/assistant";
import { NoRun } from "@/components/no-run";
import { loadProject } from "@/lib/project-page";

export default async function AssistantPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const { project, run } = await loadProject(id);
  if (!run) return <NoRun id={id} />;
  return <Assistant projectId={id} projectName={project.name} />;
}
