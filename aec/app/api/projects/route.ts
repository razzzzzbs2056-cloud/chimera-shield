import { body, fail, ok, str, withUser } from "@/lib/api";
import { defaultIntake, defaultParams } from "@/lib/defaults";
import type { DesignParams, Intake } from "@/lib/engine/types";
import { createProject, listProjects, runProject } from "@/lib/repo";

export const GET = withUser(async (_req, user) => ok(listProjects(user.id)));

export const POST = withUser(async (req, user) => {
  const b = await body<{ name?: string; code?: string; client?: string; address?: string; description?: string; stage?: string; intake?: Partial<Intake>; floors?: number; params?: Partial<DesignParams> }>(req);
  const name = str(b.name, 120);
  if (!name) return fail("Project name is required");
  const base = defaultIntake(b.intake?.buildingType ?? "office", b.intake?.city ?? "San Francisco");
  const intake: Intake = { ...base, ...b.intake, priorities: { ...base.priorities, ...(b.intake?.priorities ?? {}) } };
  const floors = Math.max(1, Math.min(90, Math.round(b.floors ?? 10)));
  const params: DesignParams = { ...defaultParams(intake, floors), ...(b.params ?? {}) };
  const code = str(b.code, 20) || name.split(/\s+/).map((w) => w[0]).join("").toUpperCase().slice(0, 4) + "-" + new Date().getFullYear();
  const id = createProject(user.id, { name, code, client: str(b.client, 120), address: str(b.address, 200), description: str(b.description, 2000), stage: str(b.stage, 40) || "Concept", intake, params });
  const result = runProject(user.id, id);
  return ok({ id, kpis: result?.kpis }, 201);
});
