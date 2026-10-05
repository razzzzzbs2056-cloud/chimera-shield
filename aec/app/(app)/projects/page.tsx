import { Plus } from "lucide-react";
import Link from "next/link";
import { Suspense } from "react";
import { Container, PageHeader } from "@/components/page";
import { ProjectsList, type ProjectCard } from "@/components/projects-list";
import { requireUser } from "@/lib/auth";
import { listProjects } from "@/lib/repo";

export const metadata = { title: "Projects" };

export default async function ProjectsPage() {
  const user = await requireUser();
  const cards: ProjectCard[] = listProjects(user.id).map((p) => ({
    id: p.id, name: p.name, code: p.code, client: p.client, stage: p.stage, status: p.status, city: p.intake.city, type: p.intake.buildingType,
    floors: p.params.floors, kpis: p.kpis, openIssues: p.openIssues, updated: p.updated_at,
  }));
  return (
    <Container>
      <PageHeader title="Projects" subtitle="Every project runs through intake → agent routing → solvers → BIM → compliance → cost → verification."
        actions={<Link href="/projects/new" className="inline-flex items-center gap-1.5 rounded-lg bg-brand-600 px-3.5 py-2 text-sm font-medium text-white shadow-sm hover:bg-brand-700"><Plus className="h-4 w-4" /> New project</Link>} />
      <Suspense><ProjectsList initial={cards} /></Suspense>
    </Container>
  );
}
