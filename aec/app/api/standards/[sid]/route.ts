import { body, fail, num, ok, str, withUser } from "@/lib/api";
import type { StandardRef } from "@/lib/engine/types";
import { deleteStandard, updateStandard } from "@/lib/repo";

type Ctx = { params: Promise<{ sid: string }> };

export const PATCH = withUser<Ctx>(async (req, _user, { params }) => {
  const b = await body<Partial<StandardRef>>(req);
  if (b.status && !["current", "superseded", "draft"].includes(b.status)) return fail("Invalid status");
  const patch: Partial<StandardRef> = {};
  (["code", "title", "jurisdiction", "discipline", "edition"] as const).forEach((k) => { if (b[k] !== undefined) patch[k] = str(b[k], 200); });
  if (b.year !== undefined) patch.year = num(b.year, 1900, 2100) ?? undefined;
  if (b.status) patch.status = b.status;
  if (b.supersededBy !== undefined) patch.supersededBy = str(b.supersededBy, 60) || null;
  return updateStandard((await params).sid, patch) ? ok({ ok: true }) : fail("Standard not found", 404);
});
export const DELETE = withUser<Ctx>(async (_req, _user, { params }) => (deleteStandard((await params).sid) ? ok({ ok: true }) : fail("Standard not found", 404)));
