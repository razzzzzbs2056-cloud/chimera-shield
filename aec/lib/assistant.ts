// Consultancy assistant. Claude answers questions grounded strictly in the
// solver outputs of the latest run; numbers always come from the engine.
// Without credentials a deterministic retrieval responder is used instead.

import Anthropic from "@anthropic-ai/sdk";
import type { WorkflowResult } from "./engine/workflow";
import type { ProjectRow } from "./repo";

export interface ChatTurn { role: "user" | "assistant"; content: string }

const SYSTEM = `You are the lead engineer of a multi-disciplinary architecture & engineering consultancy, answering questions about one building project.
Ground every statement in the PROJECT RESULTS JSON supplied with the conversation. Those numbers were produced by deterministic engineering solvers (FE frame analysis, modal/RSA, wind, geotechnics, MEP sizing, cost/QTO, CPM) and independently verified — quote them, do not recompute or invent values.
When a quantity is not in the results, say so plainly and suggest which analysis would produce it.
Cite standards and clauses exactly as they appear in the findings. Flag FAIL and WARN items when relevant and propose concrete design actions (which parameter to change and why).
Be concise: short paragraphs or bullet lists, SI units, no preamble. Remind the user that a licensed engineer must review decisions with life-safety consequences when you recommend them.`;

export function projectContext(p: ProjectRow, r: WorkflowResult) {
  return {
    project: { name: p.name, code: p.code, stage: p.stage, city: p.intake.city, jurisdiction: p.intake.jurisdiction, type: p.intake.buildingType, clientGoals: p.intake.clientGoals, budget: p.intake.budget, targetEUI: p.intake.targetEUI, targetCarbon: p.intake.targetCarbon },
    kpis: r.kpis,
    params: r.params,
    system: { id: r.system, label: r.structure.system.label, R: r.structure.system.R, Cd: r.structure.system.Cd, prescriptive: r.structure.prescriptive, heightLimit: r.structure.heightLimit },
    seismic: { ...r.seismic, T1: r.structure.T1, Ta: r.structure.Ta, Cs: r.structure.Cs, V: Math.round(r.structure.Vbase), maxDriftPct: +(r.structure.maxDriftRatio * 100).toFixed(3), torsion: r.structure.torsionClass, pushover: r.structure.pushover.level, ductilityDemand: +r.structure.history.nl.ductility.toFixed(2) },
    wind: { qh: r.wind.qh, G: r.wind.G, baseShear: Math.round(r.wind.baseShear), accel_mg: r.wind.accel.mg, roofDrift: `H/${Math.round(1 / Math.max(r.wind.roofDrift, 1e-9))}`, vortexCheck: r.wind.vortex.check },
    geotech: { siteClass: r.geotech.siteClass, vs30: r.geotech.vs30, qall: r.geotech.qall, liquefaction: r.geotech.liquefactionRisk, foundation: r.geotech.selected.label, settlement_mm: r.geotech.selected.settlement },
    mep: { coolingKW: r.hvac.coolingPeak, heatingKW: r.hvac.heatingPeak, chillers: `${r.hvac.plant.chillers}x${r.hvac.plant.chillerSize}kW`, maxDemandKVA: r.electrical.maxDemandKVA, transformers: r.electrical.transformers.config, pvKWp: r.electrical.pv.kWp, waterZones: r.hydraulics.pressureZones },
    fire: { exits: `${r.fire.exitsProvided}/${r.fire.exitsRequired}`, stairWidth: `${r.fire.stairWidthProvided}/${r.fire.stairWidthRequired} m`, travel: `${r.fire.travelDistance}/${r.fire.travelLimit} m`, rset_s: r.fire.evacuation.rset, aset_s: r.fire.evacuation.aset, type: r.fire.constructionType },
    energy: { eui: r.energy.eui, netEui: r.energy.netEui, scenarios: r.energy.scenarios },
    cost: { total: r.cost.total, perM2: r.cost.perM2, variance: r.cost.variance, byDiscipline: r.cost.byDiscipline, carbonPerM2: r.cost.carbon.perM2 },
    construction: { months: r.construction.durationMonths, floorCycle: r.construction.floorCycle, crane: r.construction.cranes.type, constructability: r.construction.constructability },
    valueEngineering: r.ve.map((v) => ({ title: v.title, saving: v.saving, ok: v.ok, consequences: v.consequences })),
    findings: r.findings.filter((f) => f.status !== "PASS" && f.status !== "INFO").map((f) => ({ status: f.status, check: f.check, standard: f.standard, clause: f.clause, evidence: f.evidence, value: f.value, limit: f.limit })),
    passingChecks: r.findings.filter((f) => f.status === "PASS").map((f) => `${f.check} (${f.standard} ${f.clause})`),
    clashes: r.clashes.map((c) => ({ type: c.type, severity: c.severity, title: c.title, location: c.location })),
    verification: r.verification.map((v) => ({ check: v.check, status: v.status, deviation: v.deviation })),
    agentChanges: r.changes,
  };
}

export async function askClaude(p: ProjectRow, r: WorkflowResult, history: ChatTurn[], question: string): Promise<{ answer: string; source: "claude" | "local"; model?: string; note?: string }> {
  const hasCreds = !!(process.env.ANTHROPIC_API_KEY || process.env.ANTHROPIC_AUTH_TOKEN);
  if (!hasCreds) return { answer: localAnswer(question, r, p), source: "local", note: "Set ANTHROPIC_API_KEY to enable Claude; showing solver-grounded summary." };
  const client = new Anthropic();
  const messages: Anthropic.Beta.BetaMessageParam[] = [
    ...history.slice(-10).map((t) => ({ role: t.role, content: t.content })),
    { role: "user", content: question },
  ];
  try {
    const stream = client.beta.messages.stream({
      model: "claude-opus-5-5",
      max_tokens: 8000,
      betas: ["server-side-fallback-2026-07-01"],
      fallbacks: "default",
      output_config: { effort: "medium" },
      system: [
        { type: "text", text: SYSTEM },
        { type: "text", text: `PROJECT RESULTS JSON:\n${JSON.stringify(projectContext(p, r))}`, cache_control: { type: "ephemeral" } },
      ],
      messages,
    });
    const msg = await stream.finalMessage();
    if (msg.stop_reason === "refusal") return { answer: "The model declined to answer this request. Try rephrasing the engineering question.", source: "claude", model: msg.model };
    const text = msg.content.filter((b): b is Anthropic.Beta.BetaTextBlock => b.type === "text").map((b) => b.text).join("\n").trim();
    return { answer: text || "No answer was returned.", source: "claude", model: msg.model };
  } catch (e) {
    const reason = e instanceof Anthropic.AuthenticationError ? "API key rejected" : e instanceof Anthropic.RateLimitError ? "rate limited" : e instanceof Anthropic.APIError ? `API error ${e.status}` : "connection error";
    return { answer: localAnswer(question, r, p), source: "local", note: `Claude unavailable (${reason}); showing solver-grounded summary.` };
  }
}

/** Deterministic retrieval responder over the run results. */
export function localAnswer(q: string, r: WorkflowResult, p: ProjectRow): string {
  const s = q.toLowerCase();
  const out: string[] = [];
  const k = r.kpis;
  const has = (...w: string[]) => w.some((x) => s.includes(x));
  const fails = r.findings.filter((f) => f.status === "FAIL");
  if (has("drift", "seismic", "earthquake", "period", "lateral", "pushover", "structur")) {
    out.push(`**Structure & seismic** — ${r.structure.system.label}, T₁ = ${r.structure.T1.toFixed(2)} s (CuTa ${r.structure.CuTa.toFixed(2)} s), Cs = ${r.structure.Cs.toFixed(4)}, V = ${Math.round(r.structure.Vbase).toLocaleString()} kN. Max design drift ${(r.structure.maxDriftRatio * 100).toFixed(2)}% vs ${r.structure.driftLimitRatio * 100}% limit (ASCE 7-22 Table 12.12-1). Pushover performance: ${r.structure.pushover.level}; NL ductility demand ${r.structure.history.nl.ductility.toFixed(2)}.`);
    if (!r.structure.prescriptive) out.push(`Height ${k.height} m exceeds the prescriptive limit for this system — performance-based design (ASCE 7-22 §12.2.1.1) is required.`);
  }
  if (has("wind", "accel", "comfort", "vortex")) out.push(`**Wind** — qh ${r.wind.qh} kPa, G ${r.wind.G}, base shear ${Math.round(r.wind.baseShear).toLocaleString()} kN, roof drift H/${Math.round(1 / Math.max(r.wind.roofDrift, 1e-9))}, 10-yr peak acceleration ${r.wind.accel.mg} milli-g (limit ${r.wind.accel.limit * 102} milli-g).`);
  if (has("foundation", "soil", "geotech", "pile", "liquef", "settle", "bearing")) out.push(`**Geotechnics** — Site Class ${r.geotech.siteClass} (Vs30 ${r.geotech.vs30} m/s), qall ${r.geotech.qall} kPa, liquefaction ${r.geotech.liquefactionRisk}. Selected ${r.geotech.selected.label}: ${r.geotech.selected.settlement} mm settlement, ${(r.geotech.selected.cost / 1e6).toFixed(1)} M USD.`);
  if (has("cost", "budget", "boq", "cheap", "value", "save", "ve")) {
    out.push(`**Cost** — $${(k.cost / 1e6).toFixed(1)} M ($${k.costPerM2.toLocaleString()}/m²), ${k.budgetVariance > 0 ? "over" : "under"} budget by $${(Math.abs(k.budgetVariance) / 1e6).toFixed(1)} M.`);
    const ve = r.ve.filter((v) => v.ok).slice(0, 3);
    if (ve.length) out.push(`Recommended VE: ${ve.map((v) => `${v.title} (saves $${(v.saving / 1e6).toFixed(2)} M)`).join("; ")}.`);
  }
  if (has("carbon", "embodied", "sustain", "leed", "net zero", "net-zero")) out.push(`**Carbon** — embodied ${k.embodiedCarbon} kgCO₂e/m² (target ${p.intake.targetCarbon}); operational ${k.operationalCarbon} kgCO₂e/m²·yr. Largest contributors: ${r.cost.carbon.byCategory.slice(0, 3).map((c) => `${c.name} ${c.value} t`).join(", ")}.`);
  if (has("energy", "eui", "hvac", "cooling", "heating")) out.push(`**Energy & HVAC** — EUI ${k.eui} kWh/m²·yr (net ${r.energy.netEui}), target ${p.intake.targetEUI}. Peak cooling ${r.hvac.coolingPeak.toLocaleString()} kW with ${r.hvac.plant.chillers} × ${r.hvac.plant.chillerSize} kW chillers. Best scenario: ${[...r.energy.scenarios].sort((a, b) => a.eui - b.eui)[0].name}.`);
  if (has("fire", "egress", "exit", "stair", "evacuat", "sprinkler")) out.push(`**Fire** — ${r.fire.exitsProvided} stairs (need ${r.fire.exitsRequired}), capacity ${r.fire.stairWidthProvided} m vs ${r.fire.stairWidthRequired} m, travel ${r.fire.travelDistance} m (limit ${r.fire.travelLimit} m), Type ${r.fire.constructionType}. RSET ${Math.round(r.fire.evacuation.rset / 60)} min vs ASET ${Math.round(r.fire.evacuation.aset / 60)} min (${r.fire.evacuation.strategy}).`);
  if (has("clash", "bim", "coordinat", "ifc")) out.push(`**Coordination** — ${r.clashes.length} clash groups: ${r.clashes.slice(0, 4).map((c) => `${c.severity} ${c.type} “${c.title}”`).join("; ")}.`);
  if (has("schedule", "programme", "program", "crane", "construct")) out.push(`**Construction** — ${r.construction.durationMonths} months, ${r.construction.floorCycle}-day floor cycle, ${r.construction.cranes.count} × ${r.construction.cranes.type}. ${r.construction.constructability.length} constructability flags.`);
  if (has("verif", "check", "trust", "accura")) out.push(`**Verification** — ${r.verification.filter((v) => v.status === "PASS").length}/${r.verification.length} independent cross-checks agree within tolerance${r.verification.some((v) => v.status !== "PASS") ? `; review: ${r.verification.filter((v) => v.status !== "PASS").map((v) => v.check).join(", ")}` : ""}.`);
  if (!out.length || has("fail", "issue", "problem", "summary", "status", "overview")) {
    out.push(`**Status** — ${k.pass} checks pass, ${k.fail} fail, ${k.warn} warnings across ${r.findings.length} clause-level checks.`);
    if (fails.length) out.push(`Failing: ${fails.slice(0, 5).map((f) => `${f.check} (${f.standard} ${f.clause}: ${f.value}${f.limit !== null ? ` vs ${f.limit}` : ""})`).join("; ")}.`);
  }
  return out.join("\n\n");
}
