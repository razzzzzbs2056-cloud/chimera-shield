import { ok, withUser } from "@/lib/api";
import { seedSampleProjects } from "@/lib/seed";
import { SEED_PROJECTS } from "@/lib/seed-data";

export const POST = withUser(async (req, user) => {
  const b = (await req.json().catch(() => ({}))) as { index?: number };
  const idx = Math.max(0, Math.min(SEED_PROJECTS.length - 1, b.index ?? 0));
  const [id] = seedSampleProjects(user.id, [idx], idx === 0);
  return ok({ id }, 201);
});
