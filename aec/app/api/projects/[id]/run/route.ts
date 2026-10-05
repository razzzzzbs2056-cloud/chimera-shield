import { fail, ok, withUser } from "@/lib/api";
import { runProject } from "@/lib/repo";

type Ctx = { params: Promise<{ id: string }> };

export const POST = withUser<Ctx>(async (_req, user, { params }) => {
  const r = runProject(user.id, (await params).id);
  return r ? ok({ kpis: r.kpis, durationMs: r.durationMs, changes: r.changes }) : fail("Project not found", 404);
});
