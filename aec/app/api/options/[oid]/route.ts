import { body, fail, ok, withUser } from "@/lib/api";
import { deleteOption, updateOption } from "@/lib/repo";

type Ctx = { params: Promise<{ oid: string }> };

export const PATCH = withUser<Ctx>(async (req, user, { params }) => {
  const b = await body<{ name?: string; notes?: string; starred?: boolean }>(req);
  return updateOption(user.id, (await params).oid, b) ? ok({ ok: true }) : fail("Option not found", 404);
});
export const DELETE = withUser<Ctx>(async (_req, user, { params }) => (deleteOption(user.id, (await params).oid) ? ok({ ok: true }) : fail("Option not found", 404)));
