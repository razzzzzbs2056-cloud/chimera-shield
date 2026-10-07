import { NextResponse } from "next/server";
import { AGENTS } from "@/lib/agent-catalog";
import { authenticateKey, meterRun, MONTHLY_RUN_LIMIT } from "@/lib/api-keys";
import { BUILDING_TYPES, CITIES, defaultIntake, defaultParams } from "@/lib/defaults";
import type { Borehole, BuildingType, DesignParams, Intake } from "@/lib/engine/types";
import { runWorkflow } from "@/lib/engine/workflow";
import { standards } from "@/lib/repo";
import { cleanLayers } from "@/lib/validate";

export const maxDuration = 120;

interface Body { name?: string; buildingType?: BuildingType; city?: string; floors?: number; intake?: Partial<Intake>; params?: Partial<DesignParams>; boreholes?: Borehole[]; agents?: string[]; pins?: Record<string, string> }

/**
 * POST /api/v1/analyze — run the multi-agent workflow on a brief.
 * Authorization: Bearer aec_live_…  ·  Body: { buildingType, city, floors, intake?, params?, boreholes?, agents? }
 * Returns KPIs, findings summary and the result sections owned by the requested agents.
 */
export async function POST(req: Request) {
  const auth = authenticateKey(req.headers.get("authorization"));
  if ("error" in auth) return NextResponse.json({ error: auth.error }, { status: auth.status });
  let b: Body;
  try { b = (await req.json()) as Body; } catch { return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 }); }
  const type = b.buildingType ?? b.intake?.buildingType ?? "office";
  if (!BUILDING_TYPES.some((t) => t.value === type)) return NextResponse.json({ error: `buildingType must be one of ${BUILDING_TYPES.map((t) => t.value).join(", ")}` }, { status: 400 });
  const city = b.city ?? b.intake?.city ?? "San Francisco";
  if (!b.intake?.jurisdiction && !CITIES.some((c) => c.city === city)) return NextResponse.json({ error: `Unknown city; use one of ${CITIES.map((c) => c.city).join(", ")} or pass full intake hazard data` }, { status: 400 });
  const floors = Math.max(1, Math.min(90, Math.round(b.floors ?? 10)));
  const base = defaultIntake(type, city);
  const intake: Intake = { ...base, ...b.intake, buildingType: type, priorities: { ...base.priorities, ...(b.intake?.priorities ?? {}) } };
  const params: DesignParams = { ...defaultParams(intake, floors), ...(b.params ?? {}), floors };
  let boreholes: Borehole[] = [];
  try { boreholes = (b.boreholes ?? []).slice(0, 20).map((h, i) => ({ name: String(h.name ?? `BH-${i + 1}`).slice(0, 40), x: Number(h.x) || 0, y: Number(h.y) || 0, gwl: Number(h.gwl) || 5, layers: cleanLayers(h.layers) })); }
  catch (e) { return NextResponse.json({ error: (e as Error).message }, { status: 400 }); }
  const wanted = (b.agents?.length ? b.agents : ["codes", "verifier"]).filter((a) => AGENTS.some((x) => x.id === a));
  try {
    const r = runWorkflow({ projectId: `api-${auth.keyId}`, name: b.name ?? "API project", code: "API", intake, params, boreholes, standards: standards(), pins: b.pins ?? {} });
    const all = r as unknown as Record<string, unknown>;
    const sections: Record<string, Record<string, unknown>> = {};
    for (const id of wanted) {
      const spec = AGENTS.find((a) => a.id === id)!;
      sections[id] = Object.fromEntries(spec.resultKeys.map((k) => [k, all[k]]));
    }
    const monthRuns = meterRun(auth.keyId);
    return NextResponse.json({
      engineVersion: r.engineVersion, durationMs: r.durationMs, usage: { monthRuns, monthlyLimit: MONTHLY_RUN_LIMIT },
      system: r.system, params: r.params, kpis: r.kpis, changes: r.changes,
      failing: r.findings.filter((f) => f.status === "FAIL"), agents: sections,
      disclaimer: "Decision support only. Results must be reviewed and sealed by a licensed professional.",
    });
  } catch (e) {
    return NextResponse.json({ error: `Analysis failed: ${(e as Error).message}` }, { status: 422 });
  }
}
