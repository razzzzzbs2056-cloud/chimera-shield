import { body, fail, num, ok, str, withUser } from "@/lib/api";
import type { Borehole, BoreholeLayer } from "@/lib/engine/types";
import { cleanLayers } from "@/lib/validate";
import { createBorehole, listBoreholes } from "@/lib/repo";

type Ctx = { params: Promise<{ id: string }> };
export const GET = withUser<Ctx>(async (_req, user, { params }) => {
  const b = listBoreholes(user.id, (await params).id);
  return b ? ok(b) : fail("Project not found", 404);
});

export const POST = withUser<Ctx>(async (req, user, { params }) => {
  const b = await body<Partial<Borehole>>(req);
  if (!str(b.name)) return fail("Borehole name is required");
  let layers: BoreholeLayer[];
  try { layers = cleanLayers(b.layers); } catch (e) { return fail((e as Error).message); }
  const id = createBorehole(user.id, (await params).id, { name: str(b.name, 40), x: num(b.x) ?? 0, y: num(b.y) ?? 0, gwl: num(b.gwl, 0, 100) ?? 5, layers });
  return id ? ok({ id }, 201) : fail("Project not found", 404);
});
