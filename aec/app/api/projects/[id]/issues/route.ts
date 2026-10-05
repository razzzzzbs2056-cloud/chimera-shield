import { body, fail, ok, str, withUser } from "@/lib/api";
import { createIssue, listIssues } from "@/lib/repo";

type Ctx = { params: Promise<{ id: string }> };
const SEV = ["critical", "major", "minor"];

export const GET = withUser<Ctx>(async (_req, user, { params }) => {
  const i = listIssues(user.id, (await params).id);
  return i ? ok(i) : fail("Project not found", 404);
});

export const POST = withUser<Ctx>(async (req, user, { params }) => {
  const b = await body<Record<string, unknown>>(req);
  const title = str(b.title, 200);
  if (!title) return fail("Title is required");
  const id = createIssue(user.id, (await params).id, { title, severity: SEV.includes(b.severity as string) ? (b.severity as string) : "minor", detail: str(b.detail, 4000) || null, discipline: str(b.discipline, 60) || null, location: str(b.location, 120) || null, assignee: str(b.assignee, 80) || null, type: "rfi" });
  return id ? ok({ id }, 201) : fail("Project not found", 404);
});
