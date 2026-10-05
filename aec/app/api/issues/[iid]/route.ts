import { body, fail, ok, str, withUser } from "@/lib/api";
import { deleteIssue, updateIssue } from "@/lib/repo";

type Ctx = { params: Promise<{ iid: string }> };
const STATUS = ["open", "in-review", "resolved"], SEV = ["critical", "major", "minor"];

export const PATCH = withUser<Ctx>(async (req, user, { params }) => {
  const b = await body<Record<string, unknown>>(req);
  if (b.status !== undefined && !STATUS.includes(b.status as string)) return fail("Invalid status");
  if (b.severity !== undefined && !SEV.includes(b.severity as string)) return fail("Invalid severity");
  const okk = updateIssue(user.id, (await params).iid, {
    status: b.status as string | undefined, severity: b.severity as string | undefined, title: b.title !== undefined ? str(b.title, 200) : undefined,
    detail: b.detail !== undefined ? str(b.detail, 4000) : undefined, assignee: b.assignee !== undefined ? str(b.assignee, 80) : undefined,
  });
  return okk ? ok({ ok: true }) : fail("Issue not found", 404);
});
export const DELETE = withUser<Ctx>(async (_req, user, { params }) => (deleteIssue(user.id, (await params).iid) ? ok({ ok: true }) : fail("Issue not found", 404)));
