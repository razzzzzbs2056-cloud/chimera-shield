import { body, fail, ok, str, withUser } from "@/lib/api";
import type { DesignParams } from "@/lib/engine/types";
import { createOption, listOptions } from "@/lib/repo";

type Ctx = { params: Promise<{ id: string }> };

export const GET = withUser<Ctx>(async (_req, user, { params }) => {
  const o = listOptions(user.id, (await params).id);
  return o ? ok(o) : fail("Project not found", 404);
});

export const POST = withUser<Ctx>(async (req, user, { params }) => {
  const b = await body<{ name?: string; objective?: string; params?: DesignParams; metrics?: Record<string, number>; score?: number; notes?: string }>(req);
  if (!str(b.name) || !b.params) return fail("Name and params are required");
  const id = createOption(user.id, (await params).id, { name: str(b.name, 120), objective: str(b.objective, 30) || "balanced", params: b.params, metrics: b.metrics ?? {}, score: Number(b.score) || 0, notes: str(b.notes, 1000) || undefined });
  return id ? ok({ id }, 201) : fail("Project not found", 404);
});
