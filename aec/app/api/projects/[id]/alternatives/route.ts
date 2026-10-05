import { body, fail, ok, withUser } from "@/lib/api";
import { generateAlternatives, type Objective } from "@/lib/engine/alternatives";
import { getProject, listBoreholes, standards } from "@/lib/repo";

type Ctx = { params: Promise<{ id: string }> };
const OBJ: Objective[] = ["balanced", "cost", "carbon", "area", "daylight", "structure", "speed"];

export const POST = withUser<Ctx>(async (req, user, { params }) => {
  const id = (await params).id;
  const p = getProject(user.id, id);
  if (!p) return fail("Project not found", 404);
  const { objective } = await body<{ objective?: Objective }>(req);
  const obj = OBJ.includes(objective as Objective) ? (objective as Objective) : "balanced";
  const alts = generateAlternatives({ projectId: id, name: p.name, code: p.code, intake: p.intake, params: p.params, boreholes: listBoreholes(user.id, id) ?? [], standards: standards(), pins: p.pins }, obj);
  return ok(alts);
});
