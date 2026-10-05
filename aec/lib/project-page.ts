import "server-only";
import { notFound } from "next/navigation";
import { requireUser } from "./auth";
import { getProject, latestRun } from "./repo";

export async function loadProject(id: string) {
  const user = await requireUser();
  const project = getProject(user.id, id);
  if (!project) notFound();
  const run = latestRun(user.id, id);
  return { user, project, run };
}
