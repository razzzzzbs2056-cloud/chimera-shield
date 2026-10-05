// Design alternatives generator: explores structural material/system, slab
// system, grid and façade combinations, evaluates each with the full engine
// (light mode) and ranks them against the selected optimisation objective.

import { round } from "./linalg";
import type { DesignParams, LateralSystem, SlabSystem, StructuralMaterial } from "./types";
import { evaluate, type WorkflowInput } from "./workflow";

export type Objective = "balanced" | "cost" | "carbon" | "area" | "daylight" | "structure" | "speed";

const VARIANTS: { name: string; material: StructuralMaterial; lateral: LateralSystem; slab: SlabSystem; slabT: number; tweak?: Partial<DesignParams> }[] = [
  { name: "Concrete core + PT flat slab", material: "concrete", lateral: "core", slab: "post-tensioned", slabT: 0.24 },
  { name: "Concrete core + outriggers", material: "concrete", lateral: "core-outrigger", slab: "flat-plate", slabT: 0.28 },
  { name: "Concrete dual system", material: "concrete", lateral: "dual", slab: "beam-slab", slabT: 0.2 },
  { name: "Composite steel + concrete core", material: "composite", lateral: "core", slab: "composite-deck", slabT: 0.14 },
  { name: "Steel BRBF", material: "steel", lateral: "braced-frame", slab: "composite-deck", slabT: 0.14 },
  { name: "Steel diagrid", material: "steel", lateral: "diagrid", slab: "composite-deck", slabT: 0.14 },
  { name: "Mass timber + concrete core", material: "timber", lateral: "core", slab: "clt", slabT: 0.2, tweak: { columnSize: 0.6 } },
  { name: "Daylight-optimised (WWR 55 %, slim plate)", material: "concrete", lateral: "core", slab: "post-tensioned", slabT: 0.24, tweak: { wwr: 0.55, glazingU: 1.1, shgc: 0.25 } },
];

export function generateAlternatives(input: WorkflowInput, objective: Objective) {
  const base = input.params;
  const rows = VARIANTS.map((v) => {
    const p: DesignParams = { ...base, material: v.material, lateralSystem: v.lateral, slabSystem: v.slab, slabThickness: v.slabT, ...(v.tweak ?? {}) };
    if (v.material === "timber" && base.floors > 18) return null;
    try {
      const e = evaluate(input, p);
      return { name: v.name, params: e.params, metrics: { cost: e.cost, carbon: e.carbon, nla: e.nla, efficiency: e.efficiency, daylight: e.daylight, drift: e.drift, driftLimit: e.driftLimit, eui: e.eui, months: e.months, fails: e.fails, T1: e.T1, clashes: e.clashes } };
    } catch { return null; }
  }).filter(Boolean) as { name: string; params: DesignParams; metrics: Record<string, number> }[];
  const min = (k: string) => Math.min(...rows.map((r) => r.metrics[k]));
  const max = (k: string) => Math.max(...rows.map((r) => r.metrics[k]));
  const W: Record<Objective, Record<string, number>> = {
    balanced: { cost: 1, carbon: 1, area: 1, daylight: 0.5, structure: 0.5, speed: 0.5 },
    cost: { cost: 3, carbon: 0.3, area: 0.5, daylight: 0.2, structure: 0.3, speed: 0.5 },
    carbon: { cost: 0.5, carbon: 3, area: 0.3, daylight: 0.2, structure: 0.3, speed: 0.2 },
    area: { cost: 0.5, carbon: 0.3, area: 3, daylight: 0.3, structure: 0.3, speed: 0.2 },
    daylight: { cost: 0.4, carbon: 0.3, area: 0.4, daylight: 3, structure: 0.2, speed: 0.2 },
    structure: { cost: 0.4, carbon: 0.3, area: 0.3, daylight: 0.1, structure: 3, speed: 0.2 },
    speed: { cost: 0.5, carbon: 0.2, area: 0.3, daylight: 0.1, structure: 0.3, speed: 3 },
  };
  const w = W[objective];
  const scored = rows.map((r) => {
    const m = r.metrics;
    const s = {
      cost: min("cost") / m.cost, carbon: min("carbon") / m.carbon, area: m.nla / max("nla"), daylight: m.daylight / Math.max(max("daylight"), 1),
      structure: Math.max(0, 1 - m.drift / m.driftLimit), speed: min("months") / m.months,
    };
    const tot = Object.values(w).reduce((a, b) => a + b, 0);
    const score = (Object.keys(w) as (keyof typeof s)[]).reduce((acc, k) => acc + w[k] * s[k], 0) / tot;
    const penalty = m.fails * 0.04 + (m.drift > m.driftLimit ? 0.3 : 0);
    return { ...r, scores: Object.fromEntries(Object.entries(s).map(([k, v]) => [k, round(v * 100, 0)])), score: round(Math.max(0, score - penalty) * 100, 1) };
  });
  const pareto = scored.map((a) => ({ ...a, pareto: !scored.some((b) => b !== a && b.metrics.cost <= a.metrics.cost && b.metrics.carbon <= a.metrics.carbon && (b.metrics.cost < a.metrics.cost || b.metrics.carbon < a.metrics.carbon)) }));
  return pareto.sort((a, b) => b.score - a.score);
}
