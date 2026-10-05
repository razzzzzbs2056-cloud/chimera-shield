import { body, fail, num, ok, str, withUser } from "@/lib/api";
import type { Borehole } from "@/lib/engine/types";
import { deleteBorehole, updateBorehole } from "@/lib/repo";
import { cleanLayers } from "@/lib/validate";

type Ctx = { params: Promise<{ bid: string }> };

export const PATCH = withUser<Ctx>(async (req, user, { params }) => {
  const b = await body<Partial<Borehole>>(req);
  let layers;
  try { layers = b.layers ? cleanLayers(b.layers) : undefined; } catch (e) { return fail((e as Error).message); }
  const okk = updateBorehole(user.id, (await params).bid, { name: b.name ? str(b.name, 40) : undefined, x: num(b.x) ?? undefined, y: num(b.y) ?? undefined, gwl: num(b.gwl, 0, 100) ?? undefined, layers });
  return okk ? ok({ ok: true }) : fail("Borehole not found", 404);
});
export const DELETE = withUser<Ctx>(async (_req, user, { params }) => (deleteBorehole(user.id, (await params).bid) ? ok({ ok: true }) : fail("Borehole not found", 404)));
