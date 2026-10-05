import { fail, ok, withUser } from "@/lib/api";
import { applyOption, runProject } from "@/lib/repo";

type Ctx = { params: Promise<{ oid: string }> };

export const POST = withUser<Ctx>(async (_req, user, { params }) => {
  const projectId = applyOption(user.id, (await params).oid);
  if (!projectId) return fail("Option not found", 404);
  const r = runProject(user.id, projectId);
  return ok({ projectId, kpis: r?.kpis });
});
