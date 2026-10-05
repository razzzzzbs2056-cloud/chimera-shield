import { fail, withUser } from "@/lib/api";
import { getProject, latestRun } from "@/lib/repo";

type Ctx = { params: Promise<{ id: string }> };
const csv = (rows: (string | number | null | undefined)[][]) => rows.map((r) => r.map((v) => `"${String(v ?? "").replace(/"/g, '""')}"`).join(",")).join("\n");

export const GET = withUser<Ctx>(async (req, user, { params }) => {
  const id = (await params).id;
  const p = getProject(user.id, id);
  const run = latestRun(user.id, id);
  if (!p || !run) return fail("Project or run not found", 404);
  const type = new URL(req.url).searchParams.get("type") ?? "findings";
  let body: string;
  if (type === "boq") body = csv([["Code", "Section", "Item", "Unit", "Qty", "Rate (USD)", "Amount (USD)", "Carbon (tCO2e)"], ...run.cost.boq.map((b) => [b.code, b.section, b.item, b.unit, b.qty, b.rate, b.amount, b.carbon]), [], ["", "", "Preliminaries", "", "", "", run.cost.preliminaries, ""], ["", "", "Contingency", "", "", "", run.cost.contingency, ""], ["", "", "Fees", "", "", "", run.cost.fees, ""], ["", "", "Escalation", "", "", "", run.cost.escalation, ""], ["", "", "TOTAL", "", "", "", run.cost.total, ""]]);
  else if (type === "schedule") body = csv([["ID", "Activity", "Phase", "Duration (d)", "ES", "EF", "LS", "LF", "Float", "Critical"], ...run.construction.activities.map((a) => [a.id, a.name, a.phase, a.duration, a.es, a.ef, a.ls, a.lf, a.float, a.critical ? "yes" : ""])]);
  else body = csv([["Status", "Discipline", "Check", "Standard", "Clause", "Requirement", "Evidence", "Value", "Limit", "Unit", "Proxy"], ...run.findings.map((f) => [f.status, f.discipline, f.check, f.standard, f.clause, f.requirement, f.evidence, f.value, f.limit, f.unit, f.proxy ? "yes" : ""])]);
  return new Response(body, { headers: { "Content-Type": "text/csv; charset=utf-8", "Content-Disposition": `attachment; filename="${p.code}-${type}.csv"` } });
});
