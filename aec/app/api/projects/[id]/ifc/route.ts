import { fail, withUser } from "@/lib/api";
import { exportIfc } from "@/lib/engine/bim";
import { getProject, logActivity, projectModel } from "@/lib/repo";

type Ctx = { params: Promise<{ id: string }> };

export const GET = withUser<Ctx>(async (_req, user, { params }) => {
  const id = (await params).id;
  const p = getProject(user.id, id);
  const m = projectModel(user.id, id);
  if (!p || !m) return fail("Run the workflow first", 404);
  const ifc = exportIfc(m, { name: p.name, code: p.code, site: p.address ?? p.intake.city }, Date.now());
  logActivity(user.id, id, "exported IFC4 model", `${m.elements.length} elements`);
  return new Response(ifc, { headers: { "Content-Type": "application/x-step", "Content-Disposition": `attachment; filename="${p.code}.ifc"` } });
});
