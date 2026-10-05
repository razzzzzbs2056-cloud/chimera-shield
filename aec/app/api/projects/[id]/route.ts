import { body, fail, ok, withUser } from "@/lib/api";
import { deleteProject, getProject, updateProject, type ProjectRow } from "@/lib/repo";

type Ctx = { params: Promise<{ id: string }> };

export const GET = withUser<Ctx>(async (_req, user, { params }) => {
  const p = getProject(user.id, (await params).id);
  return p ? ok(p) : fail("Project not found", 404);
});

export const PATCH = withUser<Ctx>(async (req, user, { params }) => {
  const patch = await body<Partial<ProjectRow>>(req);
  const p = updateProject(user.id, (await params).id, patch);
  return p ? ok(p) : fail("Project not found", 404);
});

export const DELETE = withUser<Ctx>(async (_req, user, { params }) => (deleteProject(user.id, (await params).id) ? ok({ ok: true }) : fail("Project not found", 404)));
