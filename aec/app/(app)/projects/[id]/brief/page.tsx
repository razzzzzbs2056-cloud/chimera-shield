import { IntakeForm } from "@/components/intake-form";
import { loadProject } from "@/lib/project-page";

export default async function Brief({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const { project } = await loadProject(id);
  return (
    <IntakeForm mode="edit" projectId={id} initialIntake={project.intake} initialFloors={project.params.floors}
      initialMeta={{ name: project.name, code: project.code, client: project.client ?? "", address: project.address ?? "", description: project.description ?? "", stage: project.stage }} />
  );
}
