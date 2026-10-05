import { body, fail, num, ok, str, withUser } from "@/lib/api";
import { deleteAsset, updateAsset } from "@/lib/repo";

type Ctx = { params: Promise<{ aid: string }> };

export const PATCH = withUser<Ctx>(async (req, user, { params }) => {
  const b = await body<Record<string, unknown>>(req);
  const okk = updateAsset(user.id, (await params).aid, {
    name: b.name !== undefined ? str(b.name, 120) : undefined, location: b.location !== undefined ? str(b.location, 120) : undefined,
    condition: b.condition !== undefined ? num(b.condition, 1, 5) ?? undefined : undefined, runtime_hours: b.runtime_hours !== undefined ? num(b.runtime_hours, 0, 1e6) ?? undefined : undefined,
    criticality: b.criticality !== undefined ? num(b.criticality, 0, 1) ?? undefined : undefined,
  });
  return okk ? ok({ ok: true }) : fail("Asset not found", 404);
});
export const DELETE = withUser<Ctx>(async (_req, user, { params }) => (deleteAsset(user.id, (await params).aid) ? ok({ ok: true }) : fail("Asset not found", 404)));
