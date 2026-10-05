import { body, fail, num, ok, str, withUser } from "@/lib/api";
import { assetHealth } from "@/lib/engine/operations";
import { createAsset, listAssets } from "@/lib/repo";

type Ctx = { params: Promise<{ id: string }> };
const ASSET_TYPES = ["chiller", "ahu", "pump", "lift", "boiler", "transformer", "facade", "structure", "generator"];

export const GET = withUser<Ctx>(async (_req, user, { params }) => {
  const a = listAssets(user.id, (await params).id);
  return a ? ok(a) : fail("Project not found", 404);
});

export const POST = withUser<Ctx>(async (req, user, { params }) => {
  const b = await body<Record<string, unknown>>(req);
  const name = str(b.name, 120);
  if (!name) return fail("Asset name is required");
  const type = ASSET_TYPES.includes(b.type as string) ? (b.type as string) : "pump";
  const row = { name, system: str(b.system, 60) || "HVAC", type, install_date: str(b.install_date, 10) || new Date().toISOString().slice(0, 10), condition: num(b.condition, 1, 5) ?? 3, runtime_hours: num(b.runtime_hours, 0, 1e6) ?? 0, criticality: num(b.criticality, 0, 1) ?? 0.5, location: str(b.location, 120) || null };
  const id = createAsset(user.id, (await params).id, row);
  if (!id) return fail("Project not found", 404);
  const h = assetHealth({ id, name: row.name, system: row.system, type: row.type, installDate: row.install_date, condition: row.condition, runtimeHours: row.runtime_hours, criticality: row.criticality, location: row.location ?? "" });
  return ok({ id, health: h }, 201);
});
