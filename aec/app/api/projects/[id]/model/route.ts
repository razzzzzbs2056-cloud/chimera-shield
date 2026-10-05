import { fail, ok, withUser } from "@/lib/api";
import { projectModel } from "@/lib/repo";

type Ctx = { params: Promise<{ id: string }> };

export const GET = withUser<Ctx>(async (_req, user, { params }) => {
  const m = projectModel(user.id, (await params).id);
  return m ? ok(m) : fail("Run the workflow first", 404);
});
