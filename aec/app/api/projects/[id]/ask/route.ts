import { body, fail, ok, str, withUser } from "@/lib/api";
import { askClaude, type ChatTurn } from "@/lib/assistant";
import { getProject, latestRun } from "@/lib/repo";

type Ctx = { params: Promise<{ id: string }> };
export const maxDuration = 120;

export const POST = withUser<Ctx>(async (req, user, { params }) => {
  const id = (await params).id;
  const p = getProject(user.id, id);
  const r = latestRun(user.id, id);
  if (!p || !r) return fail("Run the workflow before asking questions", 404);
  const b = await body<{ question?: string; history?: ChatTurn[] }>(req);
  const question = str(b.question, 4000);
  if (!question) return fail("Ask a question");
  const history = (Array.isArray(b.history) ? b.history : []).filter((t) => (t.role === "user" || t.role === "assistant") && typeof t.content === "string").map((t) => ({ role: t.role, content: t.content.slice(0, 8000) }));
  return ok(await askClaude(p, r, history, question));
});
