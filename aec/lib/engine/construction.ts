// Construction engineering: activity network + CPM, 4D links, 5D cash-flow,
// crane selection, logistics, temporary works and constructability review.

import { round, sum } from "./linalg";
import type { CostResult } from "./cost";
import type { GeotechResult } from "./geotech";
import type { Derived } from "./site";
import type { DesignParams } from "./types";

export interface Activity {
  id: string; name: string; phase: string; duration: number; preds: string[];
  es: number; ef: number; ls: number; lf: number; float: number; critical: boolean; cost: number; levels?: number[];
}
export interface ConstructionResult {
  activities: Activity[]; durationDays: number; durationMonths: number; floorCycle: number; criticalPath: string[];
  cashflow: { month: number; monthly: number; cumulative: number; pct: number }[];
  cranes: { count: number; type: string; radius: number; tipLoad: number; heaviestLift: { item: string; weight: number; radius: number }; capacityAtRadius: number; ok: boolean; hookHoursPerWeek: number; utilisation: number };
  hoists: number; peakWorkforce: number; stagingArea: number; gates: number;
  temporaryWorks: { item: string; solution: string; check: string; ok: boolean }[];
  constructability: { severity: "high" | "medium" | "low"; issue: string; recommendation: string }[];
}

const CRANES = [ // luffing jib tower cranes: [name, max radius m, tip load t, max load t]
  ["Luffing LJ-160 (16 t)", 50, 3.2, 16], ["Luffing LJ-280 (20 t)", 55, 4.1, 20], ["Luffing LJ-420 (32 t)", 60, 5.6, 32], ["Luffing LJ-710 (50 t)", 65, 8.0, 50],
] as const;

export function construction(d: Derived, p: DesignParams, geo: GeotechResult, cost: CostResult, schedulePriority: number): ConstructionResult {
  const cycle = p.slabSystem === "post-tensioned" ? 6 : p.slabSystem === "flat-plate" ? 5 : p.slabSystem === "composite-deck" ? 4 : p.slabSystem === "clt" ? 3 : 7;
  const floorCycle = Math.max(3, cycle - (schedulePriority > 0.3 ? 1 : 0));
  const acts: Omit<Activity, "es" | "ef" | "ls" | "lf" | "float" | "critical">[] = [];
  const A = (id: string, name: string, phase: string, duration: number, preds: string[], cost = 0, levels?: number[]) => acts.push({ id, name, phase, duration: Math.max(1, Math.round(duration)), preds, cost, levels });
  const total = cost.subtotal;
  A("MOB", "Mobilisation & site establishment", "Preliminaries", 15, [], total * 0.02);
  A("EXC", `Excavation & ${p.basementLevels ? "retention" : "site prep"}`, "Substructure", p.basementLevels * 22 + 10, ["MOB"], total * 0.05);
  A("FND", `Foundations (${geo.selected.label})`, "Substructure", geo.selected.durationWeeks * 5, ["EXC"], total * 0.06);
  A("BSM", "Basement structure & waterproofing", "Substructure", p.basementLevels * 25 + 5, ["FND"], total * 0.05, [-1]);
  const structCost = total * 0.22 / p.floors;
  let prev = "BSM";
  for (let j = 0; j < p.floors; j++) {
    const id = `S${j + 1}`;
    A(id, `Structure L${j + 1}`, "Superstructure", j === 0 ? floorCycle + 4 : floorCycle, [prev], structCost, [j]);
    prev = id;
  }
  const lag = Math.min(6, Math.ceil(p.floors / 4));
  const facCost = total * 0.16 / p.floors, mepCost = total * 0.24 / p.floors, fitCost = total * 0.14 / p.floors;
  for (let j = 0; j < p.floors; j++) {
    const s = `S${Math.min(p.floors, j + 1 + lag)}`;
    A(`F${j + 1}`, `Façade L${j + 1}`, "Envelope", p.facadeType === "unitised" ? 3 : 6, [s, ...(j ? [`F${j}`] : [])], facCost, [j]);
    A(`M${j + 1}`, `MEP rough-in L${j + 1}`, "Services", 12, [`S${Math.min(p.floors, j + 2)}`, ...(j ? [`M${j}`] : [])], mepCost, [j]);
    A(`T${j + 1}`, `Fit-out L${j + 1}`, "Fit-out", 18, [`M${j + 1}`, `F${j + 1}`, ...(j ? [`T${j}`] : [])], fitCost, [j]);
  }
  A("RFP", "Roof plant & lifts installation", "Services", 40, [`S${p.floors}`], total * 0.04, [p.floors]);
  A("COM", "Testing, commissioning & handover", "Commissioning", 35 + p.floors, [`T${p.floors}`, "RFP"], total * 0.02);
  // CPM
  const map = new Map(acts.map((a) => [a.id, { ...a, es: 0, ef: 0, ls: 0, lf: 0, float: 0, critical: false }]));
  const order = [...map.values()];
  for (const a of order) { a.es = Math.max(0, ...a.preds.map((pid) => map.get(pid)!.ef)); a.ef = a.es + a.duration; }
  const end = Math.max(...order.map((a) => a.ef));
  for (const a of [...order].reverse()) {
    const succ = order.filter((s) => s.preds.includes(a.id));
    a.lf = succ.length ? Math.min(...succ.map((s) => s.ls)) : end;
    a.ls = a.lf - a.duration;
    a.float = a.ls - a.es;
    a.critical = a.float === 0;
  }
  const workDaysPerMonth = 21.7;
  const months = Math.ceil(end / workDaysPerMonth);
  const monthly = new Array(months).fill(0);
  order.forEach((a) => {
    for (let t = a.es; t < a.ef; t++) monthly[Math.min(months - 1, Math.floor(t / workDaysPerMonth))] += a.cost / a.duration;
  });
  const grand = cost.total;
  const scale = grand / Math.max(sum(monthly), 1);
  let cum = 0;
  const cashflow = monthly.map((m, i) => { cum += m * scale; return { month: i + 1, monthly: round(m * scale, 0), cumulative: round(cum, 0), pct: round((cum / grand) * 100, 1) }; });
  // cranes
  const cx = d.Lx / 2, cy = d.Ly / 2;
  const radius = Math.hypot(cx, cy) + 12; // reach farthest corner + loading bay offset
  const unitW = p.facadeType === "unitised" ? (p.spanX / 3) * p.floorHeight * 0.065 : 1.2;
  const steelCol = p.material === "steel" || p.material === "composite" ? p.columnSize ** 2 * 0.25 * 7.85 * p.floorHeight * 2 : 0;
  const timberPanel = p.material === "timber" ? 3 * 12 * p.slabThickness * 0.5 : 0;
  const lifts = [
    { item: "Unitised façade panel", weight: unitW, radius },
    { item: "Concrete bucket 2 m³", weight: 5.6, radius: radius * 0.8 },
    { item: "Rebar bundle", weight: 3.0, radius },
    ...(steelCol ? [{ item: "Steel column (2 storeys)", weight: steelCol, radius }] : []),
    ...(timberPanel ? [{ item: "CLT floor panel", weight: timberPanel, radius }] : []),
    { item: "AHU module", weight: 8.5, radius: radius * 0.4 },
  ];
  const crit = lifts.reduce((a, b) => (b.weight * b.radius > a.weight * a.radius ? b : a));
  const choice = CRANES.find((c) => c[1] >= radius && c[2] * (c[1] / radius) >= crit.weight * 1.1) ?? CRANES[CRANES.length - 1];
  const capAtR = choice[2] * (choice[1] / radius); // inverse-radius approximation of load chart
  const nCranes = d.plateArea > 2500 || p.floors > 45 ? 2 : 1;
  const hookHours = (p.material === "concrete" ? 32 : 46) + (p.facadeType === "unitised" ? 10 : 0);
  // temporary works
  const exDepth = p.basementLevels * 3.5 + 1.2;
  const retention = exDepth === 1.2 ? "Battered slopes" : exDepth < 5 ? "Cantilever sheet piles" : geo.gwlMin < exDepth ? "Secant pile wall + 2 levels of ground anchors" : "Soldier piles & lagging with anchors";
  const propLevels = p.slabSystem === "post-tensioned" ? 2 : p.slabSystem === "clt" || p.slabSystem === "composite-deck" ? 1 : 3;
  const constructionLoad = 1.5 + p.slabThickness * 24 * 1.1; // kPa wet concrete + construction LL
  const slabCapacity = p.slabThickness * 24 + 2.4 * 1.2;
  const temporaryWorks = [
    { item: "Excavation support", solution: retention, check: `${round(exDepth, 1)} m excavation, GWL ${geo.gwlMin} m`, ok: true },
    { item: "Dewatering", solution: geo.dewatering ? "Deep wells + cut-off from secant wall" : "Sump pumping only", check: geo.dewatering ? "GWL above formation" : "GWL below formation", ok: true },
    { item: "Back-propping", solution: `${propLevels} levels of back-props`, check: `Construction load ${round(constructionLoad, 1)} kPa shared over ${propLevels + 1} slabs vs ${round(slabCapacity, 1)} kPa each`, ok: constructionLoad / (propLevels + 1) <= slabCapacity },
    { item: "Core formwork", solution: p.floors > 15 ? "Self-climbing jump form (core leads deck by 3 floors)" : "Crane-handled gang forms", check: `${p.floors} storeys`, ok: true },
    { item: "Deck formwork", solution: p.slabSystem === "composite-deck" ? "Metal deck as permanent formwork" : p.slabSystem === "clt" ? "No formwork (prefabricated panels)" : "Table forms / aluminium panel system", check: `${floorCycle}-day cycle`, ok: true },
    { item: "Edge protection & scaffold", solution: p.floors > 10 ? "Climbing perimeter screens" : "Tube & fitting scaffold", check: "Fall-arrest at leading edge", ok: true },
    { item: "Temporary stability", solution: p.material === "steel" ? "Temporary bracing until deck diaphragm & core tie-in" : "Core-led stability; frame tied each lift", check: "Erection sequence check", ok: true },
  ];
  // constructability
  const cIssues: ConstructionResult["constructability"] = [];
  if (p.material === "concrete" && p.columnSize < 0.45 && p.floors > 20) cIssues.push({ severity: "high", issue: "Column reinforcement congestion likely (ρ > 4 %) at lower levels", recommendation: "Increase lower-tier columns or use C80 high-strength concrete" });
  if (p.floorHeight - p.slabThickness < 3.4) cIssues.push({ severity: "medium", issue: "Tight floor-to-floor for services coordination", recommendation: "Increase floor height ≥ 3.8 m or adopt flat slab with integrated services zone" });
  if (p.facadeType !== "unitised" && p.floors > 25) cIssues.push({ severity: "medium", issue: "Stick-built façade on a tall tower requires extensive external access", recommendation: "Switch to unitised system installed from floor plate" });
  if (geo.dewatering && p.basementLevels >= 3) cIssues.push({ severity: "high", issue: "Deep basement below groundwater", recommendation: "Top-down construction or secant wall with toe in low-permeability stratum" });
  if (crit.weight > capAtR) cIssues.push({ severity: "high", issue: `Critical lift (${crit.item}, ${round(crit.weight, 1)} t at ${round(crit.radius, 0)} m) exceeds crane capacity`, recommendation: "Add second crane closer to the façade or reduce panel size" });
  if (p.slabSystem === "post-tensioned") cIssues.push({ severity: "low", issue: "PT stressing hold point adds 1–2 days per cycle", recommendation: "Use early-strength mix; stagger stressing with next-floor formwork" });
  if (p.spanX > 10.5 && p.slabSystem === "flat-plate") cIssues.push({ severity: "medium", issue: `Flat plate spanning ${p.spanX} m — deflection & punching risk`, recommendation: "Post-tension or add drop panels" });
  if (p.material === "timber" && p.floors > 12) cIssues.push({ severity: "medium", issue: "Tall mass-timber: moisture protection during erection", recommendation: "Weather-protection tent + max 3 exposed floors" });
  return {
    activities: order, durationDays: end, durationMonths: months, floorCycle,
    criticalPath: order.filter((a) => a.critical).map((a) => a.id),
    cashflow,
    cranes: { count: nCranes, type: choice[0], radius: round(radius, 1), tipLoad: choice[2], heaviestLift: { ...crit, weight: round(crit.weight, 1), radius: round(crit.radius, 1) }, capacityAtRadius: round(capAtR, 1), ok: crit.weight <= capAtR, hookHoursPerWeek: hookHours, utilisation: round(hookHours / 50, 2) },
    hoists: Math.max(2, Math.ceil(p.floors / 15) * 2), peakWorkforce: Math.round(d.plateArea * 0.06 * Math.min(p.floors, 12) * 0.5 + 60),
    stagingArea: round(Math.max(150, d.plateArea * 0.15), 0), gates: d.plateArea > 2000 ? 2 : 1,
    temporaryWorks, constructability: cIssues,
  };
}
