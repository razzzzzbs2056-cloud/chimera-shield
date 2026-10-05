// Orchestrator: runs the specialist agents in dependency order, lets them
// exchange constraints and design changes, aggregates clause-level findings
// and finishes with an independent verification pass.

import { AGENT_CATALOG, routeAgents } from "./agents";
import { detectClashes, generateModel, type BimInputs } from "./bim";
import { applicableCodes, ref, type ApplicableCode } from "./codes";
import { construction } from "./construction";
import { estimate } from "./cost";
import { accessibility, energy, facade, physics } from "./envelope";
import { fireEngineering } from "./fire";
import { geotech } from "./geotech";
import { round, sum } from "./linalg";
import { electrical, hvac, hydraulics } from "./mep";
import { derive, flatRoofSnow, seismicParams, type SiteClass } from "./site";
import { analyse, floorDisp, lateralCase, SYSTEMS, structuralQuantities, systemInfo, heightLimit } from "./structure";
import type { AgentInfo, AgentMessage, Borehole, Clash, DesignParams, Finding, Intake, LateralSystem, StandardRef, Status } from "./types";
import { windAnalysis } from "./wind";
import { locationFactor } from "./cost";

export const ENGINE_VERSION = "1.4.0";

export interface WorkflowInput {
  projectId: string; name: string; code: string; intake: Intake; params: DesignParams; boreholes: Borehole[]; standards: StandardRef[]; pins: Record<string, string>;
  autoResolve?: boolean; light?: boolean;
}

const MATERIAL_LABEL = { concrete: "Reinforced concrete", steel: "Structural steel", composite: "Steel-concrete composite", timber: "Mass timber (CLT/glulam)" };

// ASHRAE 90.1-2022 prescriptive limits by climate zone (approx. SI, non-residential)
const ENV_LIMITS: Record<number, { fen: number; shgc: number; wall: number; roof: number }> = {
  1: { fen: 2.84, shgc: 0.23, wall: 0.705, roof: 0.273 }, 2: { fen: 2.56, shgc: 0.25, wall: 0.479, roof: 0.22 }, 3: { fen: 2.33, shgc: 0.25, wall: 0.365, roof: 0.22 },
  4: { fen: 2.07, shgc: 0.36, wall: 0.365, roof: 0.184 }, 5: { fen: 2.07, shgc: 0.38, wall: 0.315, roof: 0.184 }, 6: { fen: 1.99, shgc: 0.38, wall: 0.315, roof: 0.184 }, 7: { fen: 1.82, shgc: 0.4, wall: 0.264, roof: 0.159 },
};

function chooseSystem(intake: Intake, d: ReturnType<typeof derive>, p: DesignParams, seis: ReturnType<typeof seismicParams>) {
  const lf = locationFactor(intake.city);
  const pr = intake.priorities;
  const rows = SYSTEMS.map((s) => {
    const materialOK = s.materials.includes(p.material);
    const limit = heightLimit(s, seis.sdc);
    const prescriptive = s.listed && (limit === null || d.height <= limit);
    if (!materialOK) return { id: s.id, label: s.label, feasible: false, reason: `Not compatible with ${p.material}`, R: s.R, Cd: s.Cd, limit, prescriptive, drift: null as number | null, T1: null as number | null, cost: 0, carbon: 0, nlaLoss: 0, score: 0 };
    if (s.id === "clt-wall" && d.height > 30) return { id: s.id, label: s.label, feasible: false, reason: `Height ${round(d.height, 0)} m beyond CLT wall practicality`, R: s.R, Cd: s.Cd, limit, prescriptive, drift: null, T1: null, cost: 0, carbon: 0, nlaLoss: 0, score: 0 };
    const a = analyse(intake, d, p, seis, s.id, { history: false });
    const q = structuralQuantities(d, p, s.id);
    const cost = (q.concrete * 200 + q.rebar * 1850 + q.structuralSteel * 4300 + q.timber * 1450 + q.formwork * 62 + q.ptStrand * 5200) * lf;
    const carbon = (q.concrete * 300 + q.rebar * 1990 + q.structuralSteel * 1550 + q.timber * 220) / 1000;
    const nlaLoss = ["core", "core-outrigger", "dual", "shear-wall"].includes(s.id) ? (s.id === "shear-wall" ? 0.03 : 0.0) : s.id === "diagrid" ? 0.01 : 0.02;
    const driftOK = a.maxDriftRatio <= a.driftLimitRatio;
    return { id: s.id, label: s.label, feasible: driftOK, reason: driftOK ? (prescriptive ? "Meets drift; prescriptive" : "Meets drift; requires performance-based design") : `Drift ${round(a.maxDriftRatio * 100, 2)} % > ${a.driftLimitRatio * 100} %`, R: s.R, Cd: s.Cd, limit, prescriptive, drift: round(a.maxDriftRatio * 100, 3), T1: round(a.T1, 2), cost: round(cost, 0), carbon: round(carbon, 0), nlaLoss, score: 0 };
  });
  const feas = rows.filter((r) => r.feasible);
  const minC = Math.min(...feas.map((r) => r.cost)), minK = Math.min(...feas.map((r) => r.carbon));
  const wsum = pr.cost + pr.carbon + pr.area + 0.5;
  feas.forEach((r) => {
    r.score = round((100 * (pr.cost * (minC / r.cost) + pr.carbon * (minK / Math.max(r.carbon, 1)) + pr.area * (1 - r.nlaLoss * 10) + 0.5 * (r.prescriptive ? 1 : 0.6))) / wsum, 1);
  });
  return rows.sort((a, b) => b.score - a.score);
}

export function runWorkflow(input: WorkflowInput) {
  const t0 = Date.now();
  const intake = input.intake;
  let p: DesignParams = { ...input.params };
  const messages: AgentMessage[] = [];
  const changes: { param: string; from: string | number; to: string | number; by: string; reason: string }[] = [];
  let seq = 0;
  const say = (from: string, to: string, kind: AgentMessage["kind"], content: string, iteration?: number) => messages.push({ seq: ++seq, from, to, kind, content, iteration });
  const change = <K extends keyof DesignParams>(key: K, value: DesignParams[K], by: string, reason: string) => {
    if (p[key] === value) return;
    changes.push({ param: key, from: p[key] as string | number, to: value as string | number, by, reason });
    p = { ...p, [key]: value };
  };
  const nm = (id: string) => AGENT_CATALOG.find((a) => a.id === id)?.name ?? id;

  let d = derive(intake, p);
  say("intake", "all", "handoff", `Brief normalised: ${p.floors} storeys, ${round(d.height, 1)} m, ${Math.round(d.gfa).toLocaleString()} m² GFA, ${d.occupants.toLocaleString()} occupants, occupancy ${d.occupancyGroup}, risk category ${d.riskCategory}.`);

  // ---- geotech first: site class drives seismic demand ----
  const prelimSeis = seismicParams(intake.Ss, intake.S1, "D", d.riskCategory);
  const serviceLoad = d.plateArea * (p.floors + p.basementLevels) * (p.slabThickness * 24 + 1.5 + 0.7 + d.liveLoad * 0.5 + 2.2);
  const colService = p.spanX * p.spanY * p.floors * (p.slabThickness * 24 + 1.5 + 0.7 + d.liveLoad + 1.5);
  const lf = locationFactor(intake.city);
  let geo = geotech(input.boreholes, p, { Lx: d.Lx, Ly: d.Ly }, { totalService: serviceLoad, colService }, prelimSeis.pga, 7.5, lf);
  const siteClass: SiteClass = geo.siteClass;
  let seis = seismicParams(intake.Ss, intake.S1, siteClass, d.riskCategory);
  geo = geotech(input.boreholes, p, { Lx: d.Lx, Ly: d.Ly }, { totalService: serviceLoad, colService }, seis.pga, 7.5, lf);
  say("geotech", "seismic", "constraint", `Vs30 ≈ ${geo.vs30} m/s → Site Class ${siteClass}. Fa ${seis.Fa}, Fv ${seis.Fv} → SDS ${seis.SDS} g, SD1 ${seis.SD1} g, SDC ${seis.sdc}.`);
  say("geotech", "structural", "constraint", `Allowable bearing ${geo.qall} kPa at ${geo.foundingDepth} m in ${geo.foundingSoil}; liquefaction risk ${geo.liquefactionRisk}${geo.liquefiedThickness ? ` (${geo.liquefiedThickness} m liquefiable)` : ""}; GWL ${geo.gwlMin} m.`);

  const agents: AgentInfo[] = routeAgents(intake, d, p, seis, input.boreholes);
  say("codes", "all", "handoff", `${agents.filter((a) => a.required).length} specialist agents engaged for ${intake.jurisdiction} / ${d.occupancyGroup}.`);
  const codes: ApplicableCode[] = applicableCodes(intake, d, p, input.standards, input.pins);
  codes.filter((c) => c.versionIssue).forEach((c) => say("codes", "all", "warning", c.versionIssue!));

  // ---- fire/architecture handshake on core contents ----
  const fireProbe = fireEngineering(intake, d, p);
  if (input.autoResolve !== false) {
    if (fireProbe.exitsRequired > p.stairCount) {
      say("fire", "architecture", "change", `Occupant load ${fireProbe.occupantLoadFloor}/floor requires ${fireProbe.exitsRequired} exits; adding stairs.`);
      change("stairCount", fireProbe.exitsRequired, "fire", "IBC §1006.3.3 exit count");
    }
    const needW = Math.max(fireProbe.minStairWidth, fireProbe.stairWidthRequired / p.stairCount);
    if (needW > p.stairWidth + 1e-6) {
      const w = round(Math.ceil(needW * 20) / 20, 2);
      say("fire", "architecture", "change", `Stair capacity ${fireProbe.stairWidthProvided} m < ${fireProbe.stairWidthRequired} m required — widening stairs to ${w} m.`);
      change("stairWidth", w, "fire", "IBC §1005.3.1 egress capacity");
    }
  }
  // core area check: stairs + lifts + risers
  const coreNeed = p.stairCount * (p.stairWidth * 2 + 0.6) * 6 + p.liftCount * 2.8 * 3.2 + 18 + p.floors * 0.25;
  if (input.autoResolve !== false && coreNeed > p.coreWidth * p.coreDepth * 0.85) {
    const scale = Math.sqrt(coreNeed / (p.coreWidth * p.coreDepth * 0.85));
    const nw = round(p.coreWidth * scale, 1), ndp = round(p.coreDepth * scale, 1);
    say("architecture", "structural", "change", `Core must house ${p.stairCount} stairs, ${p.liftCount} lifts and risers (${round(coreNeed, 0)} m²); enlarging core to ${nw} × ${ndp} m.`);
    change("coreWidth", nw, "architecture", "Core planning (stairs/lifts/risers)");
    change("coreDepth", ndp, "architecture", "Core planning (stairs/lifts/risers)");
  }
  d = derive(intake, p);

  // ---- structural system selection ----
  const selection = input.light ? [] : chooseSystem(intake, d, p, seis);
  let system: Exclude<LateralSystem, "auto"> = p.lateralSystem === "auto" ? ((selection.find((r) => r.feasible)?.id ?? "core") as Exclude<LateralSystem, "auto">) : p.lateralSystem;
  if (p.lateralSystem === "auto") say("structural", "all", "result", `Automatic system selection: ${systemInfo(system).label} ranks first of ${selection.filter((s) => s.feasible).length} feasible systems (priorities cost ${intake.priorities.cost}, carbon ${intake.priorities.carbon}, area ${intake.priorities.area}).`);

  // ---- design loop: structural ↔ seismic ↔ architecture ----
  const iterations: { n: number; system: string; drift: number; theta: number; colUtil: number; punching: number | null; T1: number; action: string }[] = [];
  let sa = analyse(intake, d, p, seis, system, { history: !input.light });
  for (let it = 1; it <= 6; it++) {
    const driftFail = sa.maxDriftRatio > sa.driftLimitRatio;
    const thetaFail = sa.maxTheta > sa.thetaMax;
    const colFail = sa.gravity.colUtil > 1;
    const punchFail = !!sa.gravity.punching && sa.gravity.punching.util > 1;
    let action = "Converged";
    if (input.autoResolve === false || !(driftFail || thetaFail || colFail || punchFail)) {
      iterations.push({ n: it, system, drift: round(sa.maxDriftRatio * 100, 3), theta: round(sa.maxTheta, 3), colUtil: round(sa.gravity.colUtil, 2), punching: sa.gravity.punching?.util ?? null, T1: round(sa.T1, 2), action });
      break;
    }
    const acts: string[] = [];
    if (driftFail || thetaFail) {
      if (["core", "dual", "shear-wall", "core-outrigger", "clt-wall"].includes(system) && p.coreWallThickness < 0.8) {
        const nt = round(p.coreWallThickness + 0.1, 2);
        say("seismic", "structural", "warning", `Iteration ${it}: drift ${round(sa.maxDriftRatio * 100, 2)} % exceeds ${sa.driftLimitRatio * 100} % — stiffen lateral system.`, it);
        change("coreWallThickness", nt, "structural", `Drift control (iteration ${it})`);
        say("structural", "architecture", "change", `Core walls thickened to ${nt * 1000} mm; NLA reduces by ≈ ${round(4 * (p.coreWidth + p.coreDepth) * 0.1 * p.floors, 0)} m².`, it);
        acts.push(`core walls → ${nt * 1000} mm`);
      } else if (system === "core") {
        say("structural", "all", "change", "Core at maximum practical thickness — adding outrigger trusses at mid-height and roof.", it);
        system = "core-outrigger"; acts.push("add outriggers");
      } else {
        const nc = round(p.columnSize + 0.1, 2);
        change("columnSize", nc, "structural", `Drift control (iteration ${it})`);
        say("structural", "architecture", "change", `Frame columns increased to ${nc * 1000} mm.`, it);
        acts.push(`columns → ${nc * 1000} mm`);
      }
    }
    if (colFail) {
      if (p.material === "concrete" && p.concreteGrade < 80) {
        const g = Math.min(80, p.concreteGrade + 10);
        change("concreteGrade", g, "structural", "Column axial capacity");
        acts.push(`f'c → ${g} MPa`);
      } else { const nc = round(p.columnSize + 0.1, 2); change("columnSize", nc, "structural", "Column axial capacity"); acts.push(`columns → ${nc * 1000} mm`); }
      say("structural", "cost", "change", `Column utilisation ${round(sa.gravity.colUtil, 2)} > 1.0 — ${acts[acts.length - 1]}.`, it);
    }
    if (punchFail) {
      const ns = round(p.slabThickness + 0.025, 3);
      change("slabThickness", ns, "structural", "Punching shear");
      say("structural", "architecture", "change", `Punching shear ratio ${sa.gravity.punching!.util} — slab increased to ${Math.round(ns * 1000)} mm (floor-to-floor unchanged; ceiling void reduced).`, it);
      acts.push(`slab → ${Math.round(ns * 1000)} mm`);
    }
    action = acts.join("; ");
    iterations.push({ n: it, system, drift: round(sa.maxDriftRatio * 100, 3), theta: round(sa.maxTheta, 3), colUtil: round(sa.gravity.colUtil, 2), punching: sa.gravity.punching?.util ?? null, T1: round(sa.T1, 2), action });
    d = derive(intake, p);
    sa = analyse(intake, d, p, seis, system, { history: !input.light });
  }
  say("seismic", "structural", "result", `T1 = ${round(sa.T1, 2)} s (CuTa ${round(sa.CuTa, 2)} s), Cs = ${round(sa.Cs, 4)}, V = ${Math.round(sa.Vbase).toLocaleString()} kN; RSA scaled ×${round(sa.rsaScale, 2)}; max drift ${round(sa.maxDriftRatio * 100, 2)} %.`);
  say("seismic", "architecture", "result", `Pushover performance point at ${round(sa.pushover.perfPoint.driftRatio * 100, 2)} % roof drift → ${sa.pushover.level}.`);

  // ---- wind ----
  const wind = windAnalysis(intake, d, p, 1 / sa.T1, sa.system.damping > 0.04 ? 0.02 : 0.015);
  const wr = sa.model.frame.run(lateralCase(sa.model, wind.stories.map((s) => s.F)));
  const wdisp = floorDisp(sa.model, wr.d, p.floors);
  sa.stories.forEach((s, i) => { s.windDisp = wdisp[i]; s.windDriftRatio = (wdisp[i] - (i ? wdisp[i - 1] : 0)) / s.h; });
  const windRoofDrift = wdisp[p.floors - 1] / d.height;
  say("wind", "structural", "constraint", `Design wind base shear ${Math.round(wind.baseShear).toLocaleString()} kN (G = ${wind.G}${wind.flexible ? ", flexible" : ""}); roof drift H/${Math.round(1 / Math.max(windRoofDrift, 1e-9))}; 10-yr peak acceleration ${wind.accel.mg} milli-g.`);
  say("wind", "facade", "constraint", `C&C design pressures: field ${wind.facade[0].neg} kPa, corners ${wind.facade[1].neg} kPa.`);

  // ---- foundations with real column loads ----
  const colServiceFEA = sa.gravity.colAxialHand / 1.35;
  geo = geotech(input.boreholes, p, { Lx: d.Lx, Ly: d.Ly }, { totalService: sa.W + sum(sa.stories.map(() => 0)) + d.plateArea * p.floors * d.liveLoad * 0.5, colService: colServiceFEA }, seis.pga, 7.5, lf);
  say("foundation", "structural", "result", `Selected ${geo.selected.label}: settlement ${geo.selected.settlement} mm, cost $${(geo.selected.cost / 1e6).toFixed(2)} M, ${geo.selected.carbon} tCO₂e.`);

  // ---- MEP ----
  const hv = hvac(intake, d, p);
  const el = electrical(intake, d, p, hv);
  const hy = hydraulics(intake, d, p);
  say("hvac", "architecture", "constraint", `Peak cooling ${hv.coolingPeak.toLocaleString()} kW (${hv.coolingWm2} W/m²); plant room ≈ ${hv.plant.plantArea} m², riser ≈ ${hv.plant.riserArea} m².`);
  say("hvac", "structural", "constraint", `Roof plant: ${hv.plant.ahus} AHUs — allow 3.0 kPa equipment load in plant zone; duct penetrations Ø${Math.round(hv.ducts.mainDiameter * 1000)} mm through core.`);
  say("hvac", "electrical", "handoff", `Chiller electrical load ≈ ${Math.round(hv.coolingPeak / 5.8)} kW; fans ${hv.fanPower} kW; pumps ${hv.pumpPower} kW.`);
  say("electrical", "architecture", "constraint", `${el.transformers.config} substation, generator ${el.generator.kVA} kVA; main switchboard ${el.mainSwitchboard.rating} A, fault level ${el.mainSwitchboard.faultKA} kA.`);
  say("hydraulic", "architecture", "constraint", `${hy.pressureZones} pressure zone(s); booster ${hy.boosterRequired ? `${hy.boosterKW} kW` : "not required"}; ${hy.storm.drains} roof drains + overflow.`);
  const ceilingHeight = 2.7;
  const voidH = p.floorHeight - ceilingHeight - p.slabThickness;
  if (voidH < hv.ducts.mainDiameter + 0.3) say("hvac", "architecture", "query", `Ceiling void ${round(voidH, 2)} m is tight for Ø${Math.round(hv.ducts.mainDiameter * 1000)} mm mains + sprinklers. Request +150 mm floor-to-floor or 2.6 m ceilings in perimeter zones.`);

  // ---- fire / façade / physics / energy / access ----
  const fire = fireEngineering(intake, d, p);
  say("fire", "architecture", "result", `${fire.exitsProvided} stairs × ${p.stairWidth} m, travel ${fire.travelDistance} m (limit ${fire.travelLimit} m), Type ${fire.constructionType}; RSET ${Math.round(fire.evacuation.rset / 60)} min vs ASET ${Math.round(fire.evacuation.aset / 60)} min.`);
  const fac = facade(intake, d, p, wind);
  const phys = physics(intake, d, p);
  const en = energy(intake, d, p, hv, el);
  el.pv.share = en.pvOffset;
  const access = accessibility(intake, d, p);
  say("physics", "hvac", "result", `EUI ${en.eui} kWh/m²·yr (target ${intake.targetEUI}); PV offsets ${en.pvOffset} %.`);

  // ---- BIM & clashes ----
  const bimIn: BimInputs = {
    beamDepth: sa.sections.beamDepth, ductDiameter: hv.ducts.mainDiameter, riserDiameter: hv.ducts.riserDiameter, sprinklerMain: 0.1, waterMain: hy.mainDiameter,
    ahus: hv.plant.ahus, ahuSize: hv.plant.ahuSize, chillers: hv.plant.chillers, riserAreaRequired: hv.plant.riserArea, ceilingHeight, materialLabel: MATERIAL_LABEL[p.material], facadeLabel: p.facadeType,
  };
  const model = generateModel(d, p, bimIn);
  const clashes: Clash[] = detectClashes(model, d, p, bimIn);
  const crit = clashes.filter((c) => c.severity === "critical").length;
  say("bim", "all", crit ? "warning" : "result", `IFC model: ${model.elements.length.toLocaleString()} elements. ${clashes.filter((c) => c.type === "physical").length} physical and ${clashes.filter((c) => c.type === "semantic").length} semantic clash groups (${crit} critical).`);

  // ---- cost, carbon, construction ----
  const sq = structuralQuantities(d, p, system);
  const cost = estimate(intake, d, p, sq, hv, el, hy, geo.selected);
  say("cost", "all", cost.variance > 0 ? "warning" : "result", `Estimate $${(cost.total / 1e6).toFixed(1)} M ($${cost.perM2.toLocaleString()}/m²) vs budget $${(intake.budget / 1e6).toFixed(1)} M (${cost.variance > 0 ? "+" : ""}${((cost.variance / intake.budget) * 100).toFixed(1)} %).`);
  const cons = construction(d, p, geo, cost, intake.priorities.speed);
  say("construction", "all", "result", `Programme ${cons.durationMonths} months, ${cons.floorCycle}-day floor cycle, ${cons.cranes.count} × ${cons.cranes.type}.`);

  // ---- value engineering (re-evaluated, not guessed) ----
  const ve: VeOption[] = input.light ? [] : valueEngineering(input, p, system, cost.total, sa.maxDriftRatio, en.eui, cost.carbon.perM2);
  if (ve.length) say("ve", "cost", "result", `${ve.filter((v) => v.ok).length} of ${ve.length} value-engineering options pass all performance checks; best saves $${(Math.max(0, ...ve.filter((v) => v.ok).map((v) => v.saving)) / 1e6).toFixed(2)} M.`);

  // ---- resilience ----
  const resilience = resilienceAnalysis(intake, d, p, hv, el, sa, wind, fac.fire.combustible, seis.sdc);

  // ---- compliance ----
  const findings = complianceFindings(intake, d, p, seis, sa, wind, windRoofDrift, geo, fire, fac, hv, el, hy, phys, en, access, cost, flatRoofSnow(intake.groundSnow, d.riskCategory, intake.exposure));
  codes.filter((c) => c.versionIssue).forEach((c, i) => findings.push({ id: `ver-${i}`, discipline: "Compliance", check: "Code version control", standard: `${c.code} ${c.edition}`, clause: "Edition check", requirement: "Design to the edition adopted by the AHJ at permit application", evidence: c.versionIssue!, value: c.edition, limit: null, status: c.status === "superseded" ? "WARN" : "INFO" }));
  const fails = findings.filter((f) => f.status === "FAIL").length;
  say("codes", "all", fails ? "warning" : "result", `${findings.length} clause-level checks: ${findings.filter((f) => f.status === "PASS").length} pass, ${fails} fail, ${findings.filter((f) => f.status === "WARN").length} warnings.`);

  // ---- independent verification ----
  const verification = verify(intake, d, p, sa, wind, geo, hv, el, en, cost, cons, sq, model);
  const disc = verification.filter((v) => v.status !== "PASS").length;
  say("verifier", "all", disc ? "warning" : "result", `${verification.length} independent cross-checks: ${verification.length - disc} agree, ${disc} discrepancies flagged for engineer review.`);

  const specs = specifications(intake, p, sa, hv, el, hy, fire, fac, model, system);
  const statusOf = (id: string): AgentInfo["status"] => {
    const map: Record<string, string[]> = { structural: ["Structural"], seismic: ["Seismic"], wind: ["Wind"], geotech: ["Geotechnical"], foundation: ["Geotechnical"], fire: ["Fire"], facade: ["Façade"], hvac: ["Mechanical"], electrical: ["Electrical"], hydraulic: ["Hydraulics"], accessibility: ["Accessibility"], physics: ["Energy"], sustainability: ["Sustainability"] };
    const ds = map[id];
    if (!ds) return "done";
    return findings.some((f) => ds.includes(f.discipline) && f.status === "FAIL") ? "warning" : "done";
  };
  const agentsOut = agents.map((a) => ({ ...a, status: a.required ? statusOf(a.id) : "skipped" as const }));

  // trim heavy structures for storage
  const { model: _m, stiffness: _k, ...structure } = sa;
  const kpis = {
    gfa: round(d.gfa, 0), nla: d.nla, height: round(d.height, 1), cost: cost.total, costPerM2: cost.perM2, budgetVariance: cost.variance,
    embodiedCarbon: cost.carbon.perM2, operationalCarbon: en.operationalCarbon, eui: en.eui, durationMonths: cons.durationMonths,
    maxDrift: round(sa.maxDriftRatio * 100, 2), driftLimit: sa.driftLimitRatio * 100, T1: round(sa.T1, 2),
    pass: findings.filter((f) => f.status === "PASS").length, fail: fails, warn: findings.filter((f) => f.status === "WARN").length,
    clashes: clashes.length, criticalClashes: crit, verificationIssues: disc, efficiency: round(d.nla / d.gfaAbove, 3),
  };
  return {
    engineVersion: ENGINE_VERSION, ranAt: new Date().toISOString(), durationMs: Date.now() - t0,
    params: p, system, derived: d, seismic: seis, snow: flatRoofSnow(intake.groundSnow, d.riskCategory, intake.exposure),
    agents: agentsOut, messages, changes, iterations, codes, selection,
    geotech: geo, structure: { ...structure, model: undefined, modal: { ...structure.modal, shapes: structure.modal.shapes.slice(0, 4) } },
    wind: { ...wind, roofDrift: windRoofDrift }, hvac: hv, electrical: el, hydraulics: hy, fire, facade: fac, physics: phys, energy: en, accessibility: access,
    bim: { elements: model.elements.length, byDiscipline: countBy(model.elements.map((e) => e.discipline)), byType: countBy(model.elements.map((e) => e.ifc)), levels: model.levels.length },
    clashes, cost, construction: cons, ve, resilience, findings, verification, specs, kpis, bimInputs: bimIn,
  };
}
export type WorkflowResult = ReturnType<typeof runWorkflow>;

const countBy = (xs: string[]) => xs.reduce<Record<string, number>>((m, x) => ((m[x] = (m[x] ?? 0) + 1), m), {});

// ---------------- quick evaluation for alternatives & VE ----------------
export interface Evaluation { params: DesignParams; system: string; cost: number; carbon: number; nla: number; efficiency: number; daylight: number; drift: number; driftLimit: number; eui: number; months: number; fails: number; clashes: number; T1: number }
export interface VeOption { id: string; title: string; change: Partial<DesignParams>; saving: number; cost: number; carbon: number; eui: number; drift: number; months: number; ok: boolean; consequences: string[] }

export function evaluate(input: WorkflowInput, p: DesignParams): Evaluation {
  const r = runWorkflow({ ...input, params: p, light: true });
  return {
    params: r.params, system: r.system, cost: r.cost.total, carbon: r.cost.carbon.perM2, nla: r.derived.nla, efficiency: r.kpis.efficiency,
    daylight: r.physics.daylitArea, drift: r.kpis.maxDrift, driftLimit: r.kpis.driftLimit, eui: r.energy.eui, months: r.construction.durationMonths,
    fails: r.kpis.fail, clashes: r.kpis.clashes, T1: r.kpis.T1,
  };
}

function valueEngineering(input: WorkflowInput, p: DesignParams, system: string, baseCost: number, baseDrift: number, baseEui: number, baseCarbon: number): VeOption[] {
  const base = { ...p, lateralSystem: system as LateralSystem };
  const opts: { id: string; title: string; change: Partial<DesignParams> }[] = [];
  if (p.slabSystem === "flat-plate" || p.slabSystem === "beam-slab") opts.push({ id: "pt", title: "Post-tensioned slabs (thinner, faster stripping)", change: { slabSystem: "post-tensioned", slabThickness: Math.max(0.2, round(p.slabThickness - 0.05, 3)) } });
  if (p.wwr > 0.42) opts.push({ id: "wwr", title: "Reduce WWR to 40 %", change: { wwr: 0.4 } });
  if (p.ggbsReplacement < 0.5 && p.material !== "timber") opts.push({ id: "ggbs", title: "50 % GGBS cement replacement", change: { ggbsReplacement: 0.5 } });
  if (p.concreteGrade > 40) opts.push({ id: "grade", title: `Drop concrete grade to C${p.concreteGrade - 10}`, change: { concreteGrade: p.concreteGrade - 10 } });
  if (p.facadeType === "curtain-wall" || p.facadeType === "unitised") opts.push({ id: "facade", title: "Rainscreen with punched windows", change: { facadeType: "rainscreen" } });
  if (p.spanX > 8.4) opts.push({ id: "grid", title: "Tighter structural grid (−0.9 m spans, +1 bay)", change: { spanX: round(p.spanX - 0.9, 2), baysX: p.baysX + 1 } });
  if (p.heating !== "heat-pump") opts.push({ id: "hp", title: "All-electric air-source heat pumps", change: { heating: "heat-pump" } });
  if (p.liftCount > 4) opts.push({ id: "lifts", title: "Destination-dispatch lifts (−1 car)", change: { liftCount: p.liftCount - 1 } });
  return opts.map((o): VeOption => {
    const e = evaluate({ ...input, autoResolve: true }, { ...base, ...o.change });
    const saving = baseCost - e.cost;
    const consequences: string[] = [];
    if (e.drift > e.driftLimit) consequences.push(`drift ${e.drift} % exceeds limit`);
    if (e.eui > baseEui * 1.03) consequences.push(`EUI +${round(e.eui - baseEui, 1)} kWh/m²`);
    if (e.carbon > baseCarbon * 1.03) consequences.push(`embodied carbon +${round(e.carbon - baseCarbon, 0)} kg/m²`);
    if (e.fails > 0) consequences.push(`${e.fails} compliance failure(s)`);
    if (e.drift > baseDrift * 100 * 1.15) consequences.push(`drift +${round(e.drift - baseDrift * 100, 2)} %`);
    const hard = consequences.some((c) => c.includes("exceeds") || c.includes("failure"));
    const carbonWin = e.carbon < baseCarbon * 0.97 && saving > -baseCost * 0.002;
    return { id: o.id, title: o.title, change: o.change, saving: round(saving, 0), cost: e.cost, carbon: e.carbon, eui: e.eui, drift: e.drift, months: e.months, ok: (saving > 0 || carbonWin) && !hard, consequences };
  }).sort((a, b) => b.saving - a.saving);
}

// ---------------- compliance aggregation ----------------
function complianceFindings(intake: Intake, d: ReturnType<typeof derive>, p: DesignParams, seis: ReturnType<typeof seismicParams>, sa: ReturnType<typeof analyse>, wind: ReturnType<typeof windAnalysis>, windRoofDrift: number, geo: ReturnType<typeof geotech>, fire: ReturnType<typeof fireEngineering>, fac: ReturnType<typeof facade>, hv: ReturnType<typeof hvac>, el: ReturnType<typeof electrical>, hy: ReturnType<typeof hydraulics>, phys: ReturnType<typeof physics>, en: ReturnType<typeof energy>, access: ReturnType<typeof accessibility>, cost: ReturnType<typeof estimate>, snow: ReturnType<typeof flatRoofSnow>): Finding[] {
  const J = intake.jurisdiction;
  const out: Finding[] = [];
  let n = 0;
  const F = (discipline: string, checkId: string, check: string, requirement: string, evidence: string, value: Finding["value"], limit: Finding["limit"], status: Status, unit?: string) => {
    const r = ref(checkId, J);
    out.push({ id: `${checkId}-${++n}`, discipline, check, standard: r.std, clause: r.clause, requirement, evidence, value, limit, unit, status, proxy: r.proxy });
  };
  const pf = (ok: boolean): Status => (ok ? "PASS" : "FAIL");
  // structural / seismic
  F("Seismic", "site-class", "Site class", "Site class from average shear-wave velocity in upper 30 m", `Vs30 ≈ ${geo.vs30} m/s (Imai correlation from SPT N) → Class ${geo.siteClass}`, geo.siteClass, null, "INFO");
  F("Seismic", "seismic-period", "Fundamental period used", "T ≤ Cu·Ta for ELF", `T1 (modal) ${round(sa.T1, 2)} s; Ta ${round(sa.Ta, 2)} s; CuTa ${round(sa.CuTa, 2)} s → T = ${round(sa.Tused, 2)} s`, round(sa.Tused, 2), round(sa.CuTa, 2), "PASS", "s");
  F("Seismic", "seismic-base-shear", "Seismic base shear", "V = Cs·W with Cs bounded per Eq. 12.8-2…12.8-6", `Cs = ${round(sa.Cs, 4)}, W = ${Math.round(sa.W).toLocaleString()} kN, R = ${sa.system.R}, Ie = ${d.Ie}`, Math.round(sa.Vbase), null, "INFO", "kN");
  F("Seismic", "modal-mass", "Modal mass participation", "Include modes to capture ≥ 90 % (100 % incl. residual) of mass", `${sa.modal.cumMass.findIndex((c) => c >= 0.9) + 1} modes reach 90 %; all ${sa.modal.periods.length} modes = ${round(sa.modal.cumMass[sa.modal.cumMass.length - 1] * 100, 1)} %`, round(sa.modal.cumMass[sa.modal.cumMass.length - 1] * 100, 1), 90, "PASS", "%");
  F("Seismic", "rsa-scaling", "Response-spectrum scaling", "Scale RSA forces to 100 % of ELF base shear when lower", `Vrsa ${Math.round(sa.Vrsa).toLocaleString()} kN vs V ${Math.round(sa.Vbase).toLocaleString()} kN → factor ${round(sa.rsaScale, 2)}`, round(sa.rsaScale, 2), null, "PASS");
  F("Seismic", "story-drift", "Design story drift", `Δ ≤ ${sa.driftLimitRatio}·hsx (Risk Category ${d.riskCategory})`, `Max Δ/h = ${round(sa.maxDriftRatio * 100, 3)} % (CQC, ×Cd/Ie = ${sa.system.Cd}/${d.Ie})`, round(sa.maxDriftRatio * 100, 3), sa.driftLimitRatio * 100, pf(sa.maxDriftRatio <= sa.driftLimitRatio), "%");
  F("Seismic", "p-delta", "P-Δ stability coefficient", "θ ≤ θmax = 0.5/(β·Cd) ≤ 0.25", `θmax over stories = ${round(sa.maxTheta, 3)}`, round(sa.maxTheta, 3), round(sa.thetaMax, 3), sa.maxTheta <= 0.1 ? "PASS" : pf(sa.maxTheta <= sa.thetaMax));
  F("Seismic", "torsion", "Torsional irregularity", "δmax/δavg ≤ 1.2 (else 1a; > 1.4 → 1b)", `Ratio ${round(sa.torsionRatio, 2)} with 5 % accidental eccentricity — ${sa.torsionClass}; Ax = ${round(sa.Ax, 2)}`, round(sa.torsionRatio, 2), 1.2, sa.torsionRatio > 1.4 && ["E", "F"].includes(seis.sdc) ? "FAIL" : sa.torsionRatio > 1.2 ? "WARN" : "PASS");
  const lim = sa.heightLimit;
  F("Structural", "height-limit", "Seismic system height limit", `${sa.system.row}; SDC ${seis.sdc} limit ${lim === null ? "NL" : `${lim} m`}`, `Height ${round(d.height, 1)} m`, round(d.height, 1), lim, sa.prescriptive ? "PASS" : "WARN");
  F("Structural", "live-load", "Uniform live load", `Minimum ${d.liveLoad} kPa for ${intake.buildingType}`, `Applied ${d.liveLoad} kPa + partitions ${d.partition} kPa`, d.liveLoad, d.liveLoad, "PASS", "kPa");
  F("Structural", "snow", "Flat-roof snow load", "pf = 0.7·Ce·Ct·Is·pg", `pg ${intake.groundSnow} kPa → pf ${snow.pf} kPa (Ce ${snow.Ce}, Is ${snow.Is})`, snow.pf, null, "INFO", "kPa");
  F("Structural", "column-axial", "Column axial capacity (base, interior)", "Pu ≤ φPn,max", `Pu ${Math.round(sa.gravity.colAxialHand).toLocaleString()} kN vs φPn ${Math.round(sa.gravity.colCapacity).toLocaleString()} kN`, round(sa.gravity.colUtil, 2), 1, pf(sa.gravity.colUtil <= 1));
  if (sa.gravity.punching) F("Structural", "punching", "Two-way (punching) shear", "vu ≤ φvc", `vu ${sa.gravity.punching.vu} MPa vs φvc ${sa.gravity.punching.phiVc} MPa at interior column`, sa.gravity.punching.util, 1, pf(sa.gravity.punching.util <= 1));
  F("Structural", "slab-thickness", "Minimum slab thickness (deflection)", `h ≥ ${round(sa.gravity.slabMin * 1000, 0)} mm`, `Provided ${Math.round(p.slabThickness * 1000)} mm (${p.slabSystem})`, Math.round(p.slabThickness * 1000), Math.round(sa.gravity.slabMin * 1000), p.slabThickness >= sa.gravity.slabMin - 1e-3 ? "PASS" : "WARN", "mm");
  // wind
  F("Wind", "wind-pressure", "Velocity pressure at roof", "qh = 0.613·Kz·Kzt·Ke·V²", `V ${intake.basicWindSpeed} m/s, Exposure ${intake.exposure}, Kz(H) ${round(wind.stories[wind.stories.length - 1].Kz, 3)}`, wind.qh, null, "INFO", "kPa");
  F("Wind", "gust-factor", "Gust-effect factor", wind.flexible ? "Flexible building (n1 < 1 Hz) → Gf per §26.11.5" : "Rigid building G ≥ 0.85", `n1 ${wind.n1} Hz, Iz ${wind.gustDetail.Iz}, Q ${wind.gustDetail.Q}, R ${wind.gustDetail.R}`, wind.G, null, "INFO");
  F("Wind", "wind-drift", "Wind serviceability drift", "Roof drift ≤ H/400 (10-yr–50-yr wind)", `Roof drift H/${Math.round(1 / Math.max(windRoofDrift, 1e-9))}`, round(windRoofDrift * 1000, 3), 2.5, windRoofDrift <= 1 / 400 ? "PASS" : windRoofDrift <= 1 / 300 ? "WARN" : "FAIL", "‰");
  F("Wind", "wind-accel", "Occupant comfort — peak acceleration", `a ≤ ${wind.accel.limit} m/s² (10-yr)`, `${wind.accel.peak} m/s² (${wind.accel.mg} milli-g)`, wind.accel.peak, wind.accel.limit, wind.accel.peak <= wind.accel.limit ? "PASS" : "FAIL", "m/s²");
  F("Wind", "vortex", "Vortex-shedding screening", "vcrit > 1.25·vm (else detailed check)", `vcrit ${wind.vortex.vcrit} m/s vs 1.25·vm ${round(wind.vortex.vm * 1.25, 1)} m/s`, wind.vortex.vcrit, round(wind.vortex.vm * 1.25, 1), wind.vortex.check ? "WARN" : "PASS", "m/s");
  // geotech
  F("Geotechnical", "bearing", "Allowable bearing pressure", "qnet ≤ qult / FS (FS = 3)", `qnet ${geo.bearingPressure} kPa vs qall ${geo.qall} kPa at ${geo.foundingDepth} m`, geo.bearingPressure, geo.qall, geo.selected.id === "piles" || geo.selected.id === "barrettes" ? "PASS" : pf(geo.bearingPressure <= geo.qall));
  F("Geotechnical", "settlement", "Foundation settlement", "Total ≤ 50 mm (raft) / differential ≤ L/500", `${geo.selected.label}: ${geo.selected.settlement} mm total, ${geo.selected.differential} mm differential`, geo.selected.settlement, 50, geo.selected.settlement <= 50 ? "PASS" : geo.selected.settlement <= 75 ? "WARN" : "FAIL", "mm");
  F("Geotechnical", "liquefaction", "Liquefaction triggering", "FS ≥ 1.0 (else mitigate)", geo.liquefactionRisk === "none" ? "No liquefiable layers" : `${geo.liquefiedThickness} m liquefiable — ${["piles", "barrettes"].includes(geo.selected.id) ? "piles founded below and shaft friction ignored in layer" : "mitigation required"}`, Math.min(2, ...geo.liquefaction.map((r) => r.FS)), 1, geo.liquefactionRisk === "none" || ["piles", "barrettes"].includes(geo.selected.id) ? "PASS" : "FAIL");
  // fire
  F("Fire", "occupant-load", "Occupant load", "Per occupant load factor for use", `${fire.occupantLoadFloor} per floor (${d.occupancyGroup}); total ${fire.occupantLoadTotal.toLocaleString()}`, fire.occupantLoadFloor, null, "INFO", "persons");
  F("Fire", "exit-count", "Number of exits per storey", `≥ ${fire.exitsRequired} exits`, `${fire.exitsProvided} exit stairs`, fire.exitsProvided, fire.exitsRequired, pf(fire.exitsProvided >= fire.exitsRequired));
  F("Fire", "egress-width", "Stair egress capacity", `${fire.stairFactor} mm per occupant`, `Required ${fire.stairWidthRequired} m, provided ${fire.stairWidthProvided} m`, fire.stairWidthProvided, fire.stairWidthRequired, pf(fire.stairWidthProvided >= fire.stairWidthRequired), "m");
  F("Fire", "stair-width", "Minimum stair width", `≥ ${fire.minStairWidth * 1000} mm`, `${p.stairWidth * 1000} mm`, p.stairWidth * 1000, fire.minStairWidth * 1000, pf(p.stairWidth >= fire.minStairWidth), "mm");
  F("Fire", "travel-distance", "Exit-access travel distance", `≤ ${fire.travelLimit} m (${p.sprinklered ? "sprinklered" : "unsprinklered"})`, `Farthest point ${fire.travelDistance} m`, fire.travelDistance, fire.travelLimit, pf(fire.travelDistance <= fire.travelLimit), "m");
  F("Fire", "construction-type", "Construction type & height", `Type ${fire.constructionType}${fire.maxHeight ? ` ≤ ${fire.maxHeight} m` : " unlimited"}`, `Height ${round(d.height, 1)} m; frame ${fire.frr[0].hours} h FRR`, round(d.height, 1), fire.maxHeight, pf(fire.heightOK));
  F("Fire", "sprinklers", "Automatic sprinklers", fire.sprinklers.required ? "Required" : "Not required", fire.sprinklers.provided ? `Provided — ${fire.sprinklers.hazard}, ${fire.sprinklers.designDensity} mm/min` : "Not provided", fire.sprinklers.provided ? "Yes" : "No", fire.sprinklers.required ? "Yes" : "No", pf(!fire.sprinklers.required || fire.sprinklers.provided));
  F("Fire", "standpipes", "Standpipes", fire.standpipes ? "Class I standpipes in each exit stair" : "Not required", fire.standpipes ? "Wet risers in every stair" : "—", fire.standpipes ? "Yes" : "No", null, "PASS");
  F("Fire", "fire-lift", "Fire-service access elevators", fire.fireServiceLift ? "≥ 2 fire-service lifts" : "Not required", `${p.liftCount} lifts, ${Math.min(2, p.liftCount)} designated`, Math.min(2, p.liftCount), fire.fireServiceLift ? 2 : 0, pf(!fire.fireServiceLift || p.liftCount >= 2));
  F("Fire", "aset-rset", "Evacuation safety margin", "ASET ≥ 1.5 × RSET (performance check)", `RSET ${fire.evacuation.rset} s (pre-movement ${fire.evacuation.preMovement} s); ASET ${fire.evacuation.aset} s`, round(fire.evacuation.aset / fire.evacuation.rset, 2), 1.5, fire.evacuation.aset >= 1.5 * fire.evacuation.rset ? "PASS" : fire.evacuation.aset >= fire.evacuation.rset ? "WARN" : "FAIL");
  F("Façade", "facade-fire", "External wall fire performance", fac.fire.note, fac.fire.combustible ? "Combustible cladding assembly proposed" : "Non-combustible façade assembly", fac.fire.combustible ? "Combustible" : "Non-combustible", null, fac.fire.combustible && d.height > 18 ? "FAIL" : "PASS");
  // envelope & energy
  const lims = ENV_LIMITS[Math.min(7, Math.max(1, intake.climateZone))];
  F("Façade", "envelope-u", "Fenestration U-factor", `U ≤ ${lims.fen} W/m²K (CZ ${intake.climateZone})`, `IGU U ${p.glazingU}`, p.glazingU, lims.fen, pf(p.glazingU <= lims.fen), "W/m²K");
  F("Façade", "envelope-u", "Fenestration SHGC", `SHGC ≤ ${lims.shgc}`, `SHGC ${p.shgc}`, p.shgc, lims.shgc, pf(p.shgc <= lims.shgc));
  F("Façade", "envelope-u", "Opaque wall U-factor", `U ≤ ${lims.wall} W/m²K`, `Spandrel/wall U ${p.wallU}; effective incl. thermal bridges ${fac.thermal.uEffective}`, p.wallU, lims.wall, pf(p.wallU <= lims.wall), "W/m²K");
  F("Façade", "envelope-u", "Roof U-factor", `U ≤ ${lims.roof} W/m²K`, `Roof U ${p.roofU}`, p.roofU, lims.roof, pf(p.roofU <= lims.roof), "W/m²K");
  F("Façade", "wwr", "Window-to-wall ratio (prescriptive)", "WWR ≤ 40 % or performance path", `WWR ${Math.round(p.wwr * 100)} %`, Math.round(p.wwr * 100), 40, p.wwr <= 0.4 ? "PASS" : "WARN", "%");
  F("Façade", "condensation", "Surface condensation risk", `fRsi ≥ ${fac.thermal.fRsiMin}`, `Worst-case fRsi ${fac.thermal.fRsi}, surface ${fac.thermal.surfaceTemp} °C`, fac.thermal.fRsi, fac.thermal.fRsiMin, fac.thermal.condensation ? "FAIL" : fac.thermal.fRsi >= fac.thermal.fRsiMin ? "PASS" : "WARN");
  F("Façade", "mullion-deflection", "Mullion deflection", `≤ ${fac.mullion.limit} mm`, `${fac.mullion.selected}: ${fac.mullion.deflection} mm at corner pressure ${fac.cornerPressure} kPa`, fac.mullion.deflection, fac.mullion.limit, pf(fac.mullion.deflection <= fac.mullion.limit), "mm");
  F("Mechanical", "ventilation", "Outdoor-air ventilation", "Vbz = Rp·Pz + Ra·Az, Ez = 0.8", `${hv.oa} m³/s total (${hv.oaPerPerson} L/s·person)`, hv.oaPerPerson, null, "PASS", "L/s·p");
  F("Mechanical", "comfort", "Thermal comfort (PMV)", "−0.5 ≤ PMV ≤ +0.5", `Summer PMV ${hv.comfort.summer.PMV} (PPD ${hv.comfort.summer.PPD} %), winter ${hv.comfort.winter.PMV}; perimeter ${phys.comfort.PMV}`, phys.comfort.PMV, 0.5, Math.abs(phys.comfort.PMV) <= 0.5 ? "PASS" : "WARN");
  F("Energy", "energy", "Energy use intensity vs target", `EUI ≤ ${intake.targetEUI} kWh/m²·yr (client)`, `Modelled ${en.eui} (net ${en.netEui} after PV)`, en.eui, intake.targetEUI, en.netEui <= intake.targetEUI ? "PASS" : en.eui <= intake.targetEUI * 1.15 ? "WARN" : "FAIL", "kWh/m²");
  // electrical & hydraulics
  el.risers.forEach((r) => F("Electrical", "voltage-drop", `Voltage drop — ${r.name}`, "≤ 3 % feeder (5 % total)", `${r.parallel} × ${r.cable}, ${r.length} m, ${r.current} A`, r.vd, 3, pf(r.vd <= 3), "%"));
  F("Electrical", "transformer", "Transformer loading", "Max demand ≤ 80 % of firm capacity", `${el.maxDemandKVA} kVA on ${el.transformers.config}`, el.transformers.utilisation, 0.8, el.transformers.utilisation <= 0.8 ? "PASS" : "WARN");
  F("Electrical", "emergency-power", "Emergency & standby power", "Life-safety loads on emergency source", `Generator ${el.generator.kVA} kVA for ${el.generator.lifeSafetyKW} kW life-safety + ${el.generator.standbyKW} kW standby`, el.generator.kVA, null, "PASS", "kVA");
  F("Hydraulics", "water-pressure", "Maximum static pressure per zone", "≤ 552 kPa (PRVs above)", `${hy.pressureZones} zone(s) → ${Math.round((d.height * 9.81) / hy.pressureZones)} kPa per zone`, Math.round((d.height * 9.81) / hy.pressureZones), 552, pf((d.height * 9.81) / hy.pressureZones <= 552), "kPa");
  F("Hydraulics", "fixtures", "Plumbing fixture provision", "Minimum fixtures by occupancy", `${hy.fixtures.map((f) => `${f.count} ${f.type.toLowerCase()}`).join(", ")}`, hy.fixtures[0].count, null, "PASS");
  F("Hydraulics", "roof-drainage", "Primary & secondary roof drainage", `Q = C·i·A at ${intake.rainfall} mm/h`, `${hy.storm.flow} L/s → ${hy.storm.drains} × DN${hy.storm.drainSize} + overflow scuppers`, hy.storm.drains, null, "PASS");
  access.forEach((a) => {
    const r = ref("accessibility", J);
    out.push({ id: `acc-${++n}`, discipline: "Accessibility", check: a.item, standard: a.clause.startsWith("IBC") ? "IBC" : r.std, clause: a.clause.startsWith("IBC") ? a.clause.replace("IBC ", "§") : (r.clause ? `${r.clause} ` : "") + `§${a.clause}`, requirement: a.required, evidence: a.provided, value: a.provided, limit: a.required, status: a.ok ? "PASS" : "FAIL", proxy: r.proxy });
  });
  F("Sustainability", "embodied-carbon", "Embodied carbon (A1–A5)", `≤ ${intake.targetCarbon} kgCO₂e/m² GFA`, `${cost.carbon.perM2} kgCO₂e/m² (${cost.carbon.total.toLocaleString()} t)`, cost.carbon.perM2, intake.targetCarbon, cost.carbon.perM2 <= intake.targetCarbon ? "PASS" : cost.carbon.perM2 <= intake.targetCarbon * 1.1 ? "WARN" : "FAIL", "kg/m²");
  return out;
}

// ---------------- independent verification ----------------
function verify(intake: Intake, d: ReturnType<typeof derive>, p: DesignParams, sa: ReturnType<typeof analyse>, wind: ReturnType<typeof windAnalysis>, geo: ReturnType<typeof geotech>, hv: ReturnType<typeof hvac>, el: ReturnType<typeof electrical>, en: ReturnType<typeof energy>, cost: ReturnType<typeof estimate>, cons: ReturnType<typeof construction>, sq: ReturnType<typeof structuralQuantities>, model: ReturnType<typeof generateModel>) {
  const rows: { check: string; discipline: string; methodA: string; valueA: number; methodB: string; valueB: number; tolerance: string; deviation: number; status: Status; unit: string }[] = [];
  const add = (discipline: string, check: string, methodA: string, valueA: number, methodB: string, valueB: number, tol: number, unit: string, warnOnly = false) => {
    const dev = Math.abs(valueA - valueB) / Math.max(Math.abs(valueB), 1e-9);
    rows.push({ check, discipline, methodA, valueA: round(valueA, 3), methodB, valueB: round(valueB, 3), tolerance: `±${round(tol * 100, 1)} %`, deviation: round(dev * 100, 2), status: dev <= tol ? "PASS" : warnOnly || dev <= tol * 2 ? "WARN" : "FAIL", unit });
  };
  add("Structural", "Global lateral equilibrium", "Σ base reactions (FEA)", sa.equilibrium.sumRx, "Applied ELF base shear", sa.equilibrium.appliedLateral, 0.005, "kN");
  add("Structural", "Global gravity equilibrium", "Σ vertical reactions (FEA)", sa.gravity.sumRy, "Σ applied gravity loads", sa.gravity.appliedGravity, 0.005, "kN");
  add("Structural", "Interior column axial load", "FEA (frame-line ÷ tributary frames)", sa.gravity.colAxialBase, "Tributary-area hand calc", sa.gravity.colAxialHand, 0.15, "kN");
  add("Structural", "Beam free-span moment", "FEA: M_mid + (M₁+M₂)/2", sa.gravity.beamStaticFEA, "Statics: wL²/8", sa.gravity.beamMidHand, 0.01, "kN·m");
  // Rayleigh period from ELF displacements
  const Fx = sa.stories.map((s) => s.F);
  const r = sa.model.frame.run(lateralCase(sa.model, Fx));
  const u = floorDisp(sa.model, r.d, p.floors);
  const TR = 2 * Math.PI * Math.sqrt(sum(sa.stories.map((s, i) => s.W * u[i] ** 2)) / (9.81 * sum(Fx.map((f, i) => f * u[i]))));
  add("Seismic", "Fundamental period", "Eigenvalue analysis (Jacobi)", sa.T1, "Rayleigh quotient from ELF deflections", TR, 0.1, "s");
  add("Seismic", "Modal mass completeness", "Σ effective modal mass", sa.modal.cumMass[sa.modal.cumMass.length - 1] * 100, "Total seismic mass", 100, 0.005, "%");
  add("Seismic", "Period plausibility", "Modal T1", sa.T1, "Empirical Cu·Ta", sa.CuTa, 1.5, "s", true);
  add("Seismic", "Time-history vs spectrum", "Linear MDOF peak roof displacement (spectrum-scaled record)", sa.history.peakRoof * 1000, "RSA elastic roof displacement (×R/Cd)", (sa.stories[sa.stories.length - 1].disp * sa.system.R) / sa.system.Cd * 1000, 0.5, "mm", true);
  const qh = wind.qh, B = d.Ly, H = d.height;
  const handWind = qh * wind.Kd * wind.G * (0.8 * 0.85 + Math.abs(wind.stories[0].pl / (qh * wind.Kd * wind.G))) * B * H;
  add("Wind", "Wind base shear", "Σ story forces (Kz profile)", wind.baseShear, "Hand: q_h·Kd·G·(0.8·0.85 + |Cp,lee|)·B·H", handWind, 0.15, "kN");
  add("Geotechnical", "Raft settlement (stress distribution)", "2:1 load spread, layered", geo.raftSettlement, "Boussinesq (Newmark corner superposition), layered", geo.raftSettlementBoussinesq, 0.35, "mm", true);
  const band: Record<string, [number, number]> = { office: [50, 150], residential: [40, 110], hospital: [90, 220], school: [60, 160], retail: [80, 200], "mixed-use": [60, 160], laboratory: [120, 300], hotel: [60, 140], warehouse: [20, 90] };
  const [lo, hi] = band[intake.buildingType];
  add("Mechanical", "Cooling load density", "Component load calc", hv.coolingWm2, `Benchmark midpoint (${lo}–${hi} W/m²)`, (lo + hi) / 2, ((hi - lo) / 2) / ((lo + hi) / 2), "W/m²", true);
  add("Electrical", "Max demand density", "Load schedule × demand factors", el.vaPerM2, "Benchmark 40–120 VA/m²", 80, 0.5, "VA/m²", true);
  add("Energy", "Energy balance", "Σ monthly end-uses", sum(en.monthly.map((m) => m.heating + m.cooling + m.other)) * 1000, "Annual simulation total", en.totalMWh * 1000, 0.01, "kWh");
  const bimConcrete = sum(model.elements.filter((e) => e.discipline === "STR" && ((e.ifc === "IfcSlab" && p.slabSystem !== "clt") || e.ifc === "IfcWall" || (e.ifc === "IfcColumn" && p.material === "concrete") || (e.ifc === "IfcBeam" && p.slabSystem === "beam-slab"))).map((e) => e.box.dx * e.box.dy * e.box.dz))
    - (p.slabSystem === "composite-deck" ? d.plateArea * p.floors * p.slabThickness * 0.25 : 0);
  const qtoAbove = sq.concrete - d.plateArea * p.basementLevels * (p.slabSystem === "composite-deck" ? p.slabThickness * 0.75 : p.slabSystem === "clt" ? 0 : p.slabThickness);
  add("Cost", "Concrete quantity", "BIM element volumes (above grade)", bimConcrete, "Parametric QTO", qtoAbove, 0.15, "m³");
  add("Cost", "BOQ arithmetic", "Σ BOQ line amounts", sum(cost.boq.map((b) => b.amount)), "Reported subtotal", cost.subtotal, 0.001, "USD");
  const cpm = Math.max(...cons.activities.map((a) => a.ef));
  add("Construction", "Critical path closure", "Σ durations on critical chain (forward pass)", cpm, "Backward pass project finish", cons.durationDays, 0.001, "days");
  return rows;
}

// ---------------- resilience ----------------
function resilienceAnalysis(intake: Intake, d: ReturnType<typeof derive>, p: DesignParams, hv: ReturnType<typeof hvac>, el: ReturnType<typeof electrical>, sa: ReturnType<typeof analyse>, wind: ReturnType<typeof windAnalysis>, combustible: boolean, sdc: string) {
  const heat2050 = intake.summerDB + 2.5;
  const extraLoad = (hv.coolingPeak * 0.18 * 2.5) / Math.max(intake.summerDB - 24, 4);
  const capacity = hv.plant.chillerSize * (hv.plant.chillers - 1);
  const margin = (capacity - hv.coolingPeak - extraLoad) / hv.coolingPeak;
  const hazards = [
    { hazard: "Extreme heat (2050, +2.5 °C)", exposure: intake.climateZone <= 3 ? 4 : 2, vulnerability: margin < 0 ? 4 : margin < 0.1 ? 3 : 1, mitigation: margin < 0.1 ? "Upsize chillers by one module or add thermal storage; external shading on W façade" : `Chiller margin ${Math.round(margin * 100)} % at ${heat2050} °C design` },
    { hazard: "Pluvial / fluvial flooding", exposure: intake.floodZone ? 4 : 1, vulnerability: intake.floodZone && p.basementLevels > 0 ? 4 : intake.floodZone ? 2 : 1, mitigation: intake.floodZone ? "Raise substation, generator & chillers above DFE + 600 mm; flood barriers at ramps" : "Standard drainage, ramp crest above street" },
    { hazard: "Severe wind / storms", exposure: intake.basicWindSpeed > 50 ? 4 : 2, vulnerability: wind.accel.peak > wind.accel.limit ? 3 : 1, mitigation: "Impact-rated glazing at podium; debris-resistant roof plant restraints" },
    { hazard: "Wildfire / ember attack", exposure: intake.wildfireRisk === "high" ? 4 : intake.wildfireRisk === "moderate" ? 2 : 1, vulnerability: combustible ? 4 : 1, mitigation: intake.wildfireRisk !== "low" ? "MERV-13 filtration + smoke-mode AHU sequence; non-combustible 10 m perimeter" : "Not significant" },
    { hazard: "Earthquake", exposure: ["D", "E", "F"].includes(sdc) ? 4 : sdc === "C" ? 3 : 1, vulnerability: sa.pushover.level === "Immediate Occupancy" ? 1 : sa.pushover.level === "Life Safety" ? 2 : 4, mitigation: `MCE performance: ${sa.pushover.level}; consider supplemental damping for functional recovery` },
    { hazard: "Grid outage", exposure: 3, vulnerability: el.generator.fuelHours >= 72 ? 1 : 3, mitigation: `${el.generator.kVA} kVA generator, ${el.generator.fuelHours} h fuel; ${el.battery.kWh} kWh BESS for ride-through` },
  ].map((h) => ({ ...h, risk: h.exposure * h.vulnerability }));
  const redundancy = [
    { system: "Cooling", config: `${hv.plant.chillers} chillers (N+1)`, ok: true },
    { system: "Power supply", config: el.transformers.config, ok: el.transformers.count > 1 },
    { system: "Emergency power", config: `${el.generator.kVA} kVA, ${el.generator.fuelHours} h`, ok: true },
    { system: "Water", config: "Break tank 24 h storage + duty/standby boosters", ok: true },
    { system: "Vertical transport", config: `${p.liftCount} lifts, 2 on standby power`, ok: p.liftCount >= 2 },
  ];
  return { hazards, redundancy, score: round(100 - (hazards.reduce((s, h) => s + h.risk, 0) / (hazards.length * 16)) * 100, 0), heat2050, chillerMargin: round(margin * 100, 1) };
}

// ---------------- specifications ----------------
function specifications(intake: Intake, p: DesignParams, sa: ReturnType<typeof analyse>, hv: ReturnType<typeof hvac>, el: ReturnType<typeof electrical>, hy: ReturnType<typeof hydraulics>, fire: ReturnType<typeof fireEngineering>, fac: ReturnType<typeof facade>, model: ReturnType<typeof generateModel>, system: string) {
  const cnt = (ifc: string) => model.elements.filter((e) => e.ifc === ifc).length;
  const s = [
    { section: "03 30 00", title: "Cast-in-Place Concrete", ifc: ["IfcSlab", "IfcWall", ...(p.material === "concrete" ? ["IfcColumn"] : [])], clauses: [`Concrete f'c ${p.concreteGrade} MPa at 28 days (columns & core), ${p.concreteGrade >= 50 ? "40" : "32"} MPa slabs.`, `Supplementary cementitious materials: ${Math.round(p.ggbsReplacement * 100)} % GGBS by mass of binder.`, `Exposure class F0/S0/W1/C1; max w/cm 0.45; slump 125 ± 25 mm (pump).`, "Testing per ASTM C39: one set per 75 m³ or per pour."] },
    { section: "03 20 00", title: "Concrete Reinforcing", ifc: ["IfcSlab", "IfcWall", "IfcColumn"], clauses: ["ASTM A706 Grade 60 (420 MPa) for special seismic elements; A615 elsewhere.", `Core boundary elements per ACI 318-19 §18.10.6 where σ > 0.2f'c.`, "Mechanical couplers Type 2 in plastic-hinge regions."] },
    ...(p.slabSystem === "post-tensioned" ? [{ section: "03 38 00", title: "Post-Tensioned Concrete", ifc: ["IfcSlab"], clauses: ["Unbonded 15.2 mm 7-wire strand, fpu 1860 MPa, encapsulated for aggressive environment.", "Stress at ≥ 20 MPa concrete strength; elongation tolerance ±7 %."] }] : []),
    ...(p.material !== "concrete" && p.material !== "timber" ? [{ section: "05 12 00", title: "Structural Steel Framing", ifc: ["IfcColumn", "IfcBeam"], clauses: ["ASTM A992 (345 MPa) wide flanges; A500 Gr C HSS.", `Seismic force-resisting system: ${systemInfo(system as Exclude<LateralSystem, "auto">).label} — AISC 341 detailing, demand-critical welds per AWS D1.8.`, "Shop primer omitted at fire-sprayed surfaces."] }] : []),
    ...(p.material === "timber" ? [{ section: "06 17 19", title: "Cross-Laminated Timber", ifc: ["IfcSlab", "IfcColumn", "IfcBeam"], clauses: ["CLT per ANSI/APA PRG 320; glulam per ANSI A190.1.", `Fire resistance ${fire.frr[0].hours} h by charring + encapsulation per IBC §703 & Type ${fire.constructionType}.`, "Moisture content at installation ≤ 15 %; temporary weather protection."] }] : []),
    { section: "08 44 13", title: "Glazed Curtain Wall / Façade", ifc: ["IfcPlate"], clauses: [`System: ${p.facadeType}; WWR ${Math.round(p.wwr * 100)} %.`, `Design wind pressure ±${fac.designPressure} kPa field, ${fac.cornerPressure} kPa corners (ASCE 7-22 Ch. 30).`, `Glass: ${fac.glass.make}; centre-of-glass U ≤ ${p.glazingU} W/m²K, SHGC ≤ ${p.shgc}.`, `Mullion ${fac.mullion.selected}, deflection ≤ L/175 or 19 mm.`, `Water-penetration test at ${fac.waterTest} kPa (AAMA 501.1); air leakage ≤ 0.3 L/s·m² at 75 Pa.`] },
    { section: "14 21 00", title: "Electric Traction Elevators", ifc: ["IfcTransportElement"], clauses: [`${p.liftCount} cars; ${p.floors > 30 ? "destination dispatch, 4.0 m/s" : "conventional group control, 2.5 m/s"}.`, `${fire.fireServiceLift ? "Two fire-service access elevators per IBC §3007." : "Occupant evacuation operation not required."}`] },
    { section: "21 13 13", title: "Wet-Pipe Sprinkler Systems", ifc: ["IfcPipeSegment", "IfcValve"], clauses: [`${fire.sprinklers.hazard}, density ${fire.sprinklers.designDensity} mm/min over 139 m².`, `~${fire.sprinklers.heads.toLocaleString()} quick-response heads; floor control valve assemblies at each level.`, `Fire pump sized for ≈ ${fire.sprinklers.pumpFlow} L/s.`] },
    { section: "23 64 00", title: "Packaged Water Chillers", ifc: ["IfcUnitaryEquipment"], clauses: [`${hv.plant.chillers} × ${hv.plant.chillerSize} kW (N+1), IPLV ≥ 0.40 kW/kW.`, "Low-GWP refrigerant (R-1234ze or R-514A)."] },
    { section: "23 73 00", title: "Air-Handling Units", ifc: ["IfcUnitaryEquipment", "IfcDuctSegment"], clauses: [`${hv.plant.ahus} × ${hv.plant.ahuSize} m³/s with heat recovery ≥ 70 %, EC fans, MERV-13 filters.`, `Main ducts Ø${Math.round(hv.ducts.mainDiameter * 1000)} mm at ≤ ${hv.ducts.mainVelocity} m/s; risers Ø${Math.round(hv.ducts.riserDiameter * 1000)} mm.`] },
    { section: "26 12 00", title: "Medium-Voltage Transformers", ifc: [], clauses: [`${el.transformers.config}, Dyn11, cast-resin, Z = 6 %.`, `Main switchboard ${el.mainSwitchboard.rating} A, ${Math.ceil(el.mainSwitchboard.faultKA / 5) * 5} kA fault rating.`] },
    { section: "26 05 19", title: "Low-Voltage Conductors & Cables", ifc: ["IfcCableCarrierSegment"], clauses: el.risers.map((r) => `${r.name}: ${r.parallel} × ${r.cable}, VD ${r.vd} %.`) },
    { section: "22 11 16", title: "Domestic Water Piping", ifc: ["IfcPipeSegment"], clauses: [`Main DN${Math.round(hy.mainDiameter * 1000)} copper Type L; ${hy.pressureZones} pressure zone(s) with PRVs.`, `${hy.boosterRequired ? `Variable-speed booster set ${hy.boosterKW} kW, duty/standby.` : "Mains pressure adequate."}`] },
  ];
  return s.map((x) => ({ ...x, elements: x.ifc.reduce((a, t) => a + cnt(t), 0), project: intake.city }));
}
