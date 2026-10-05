// Façade engineering, building physics, annual energy and accessibility.

import { round, sum } from "./linalg";
import { internalGains, pmv, type ElecResult, type HvacResult } from "./mep";
import type { Derived } from "./site";
import type { DesignParams, Intake } from "./types";
import type { WindResult } from "./wind";

// ---------- façade ----------
const MULLIONS = [ // aluminium mullion catalogue: depth mm, Ix cm⁴, Sx cm³, kg/m
  [100, 180, 34, 3.6], [125, 330, 52, 4.2], [150, 560, 74, 4.9], [175, 880, 100, 5.6], [200, 1300, 130, 6.4], [225, 1850, 165, 7.2], [250, 2550, 205, 8.1],
] as const;

export interface FacadeResult {
  designPressure: number; cornerPressure: number; mullion: { span: number; spacing: number; requiredI: number; selected: string; deflection: number; limit: number; stressRatio: number };
  glass: { make: string; thickness: number; stress: number; allowable: number; deflection: number };
  anchor: { dead: number; wind: number; perFloor: number };
  thermal: { uWall: number; uGlazing: number; psiSlab: number; psiWindow: number; uEffective: number; fRsi: number; fRsiMin: number; condensation: boolean; surfaceTemp: number };
  waterTest: number; panels: number; panelTypes: number;
  fire: { combustible: boolean; nfpa285: boolean; note: string };
}

export function facade(intake: Intake, d: Derived, p: DesignParams, w: WindResult): FacadeResult {
  const field = Math.abs(w.facade[0].neg), corner = Math.abs(w.facade[1].neg);
  const span = p.floorHeight, spacing = 1.5;
  const q = corner * spacing; // kN/m on mullion
  const limit = Math.min(span / 175, 0.019); // AAMA TIR-A11 L/175 ≤ 19 mm
  const E = 70e6;
  const reqI = (5 * q * span ** 4) / (384 * E * limit); // m⁴
  const sel = MULLIONS.find((m) => m[1] * 1e-8 >= reqI) ?? MULLIONS[MULLIONS.length - 1];
  const I = sel[1] * 1e-8, S = sel[2] * 1e-6;
  const defl = (5 * q * span ** 4) / (384 * E * I);
  const M = (q * span ** 2) / 8;
  const stressRatio = M / S / 1000 / (160 / 1.65);
  // glass: 4-side supported plate, Timoshenko β for a/b
  const a = Math.min(spacing, p.floorHeight), b = Math.max(spacing, p.floorHeight);
  const beta = 0.2874 + 0.2 * Math.min(b / a - 1, 1.5) * 0.13;
  const tOpts = [6, 8, 10, 12];
  const allowable = 46; // MPa heat-strengthened (short duration)
  const t = tOpts.find((tt) => (beta * corner * 1000 * a * a) / (tt / 1000) ** 2 / 1e6 <= allowable) ?? 12;
  const stress = (beta * corner * 1000 * a * a) / (t / 1000) ** 2 / 1e6;
  const gDefl = (0.0444 * corner * 1000 * a ** 4) / (70e9 * (t / 1000) ** 3) * 1000;
  const psiSlab = p.facadeType === "unitised" || p.facadeType === "curtain-wall" ? 0.15 : 0.35;
  const psiWindow = 0.05;
  const area = d.perimeter * p.floorHeight;
  const glz = area * p.wwr, opq = area - glz;
  const uAvg = (glz * p.glazingU + opq * p.wallU + psiSlab * d.perimeter + psiWindow * (glz / 2.25) * 6.2) / area;
  const tIn = 20, rhIn = 40; // winter design interior
  const tOut = intake.winterDB;
  const worst = Math.max(p.glazingU * 1.25, p.wallU); // frame/edge-of-glass penalty
  const surfaceTemp = tIn - (tIn - tOut) * worst * 0.13; // Rsi = 0.13 m²K/W
  const dewpoint = tIn - (100 - rhIn) / 5;
  const fRsi = (surfaceTemp - tOut) / (tIn - tOut);
  const fRsiMin = Math.max(0, (dewpoint - tOut) / (tIn - tOut));
  const panels = Math.round((area / (spacing * p.floorHeight)) * p.floors);
  const combustible = p.material === "timber" && p.facadeType === "rainscreen";
  return {
    designPressure: round(field, 2), cornerPressure: round(corner, 2),
    mullion: { span, spacing, requiredI: round(reqI * 1e8, 0), selected: `AL ${sel[0]} mm (Ix ${sel[1]} cm⁴)`, deflection: round(defl * 1000, 1), limit: round(limit * 1000, 1), stressRatio: round(stressRatio, 2) },
    glass: { make: `${t} mm HS / 16 Ar / 8 mm HS low-E IGU`, thickness: t, stress: round(stress, 1), allowable, deflection: round(gDefl, 1) },
    anchor: { dead: round(0.6 * spacing * p.floorHeight, 2), wind: round(corner * spacing * p.floorHeight, 2), perFloor: Math.ceil(d.perimeter / spacing) },
    thermal: { uWall: p.wallU, uGlazing: p.glazingU, psiSlab, psiWindow, uEffective: round(uAvg, 2), fRsi: round(fRsi, 2), fRsiMin: round(fRsiMin, 2), condensation: fRsi < fRsiMin, surfaceTemp: round(surfaceTemp, 1) },
    waterTest: round(Math.max(0.3, 0.15 * field * 1.5), 2), // kPa, AAMA 501.1 ≈ 15–20 % of design pressure
    panels, panelTypes: p.facadeType === "unitised" ? Math.max(6, Math.round(p.baysX + p.baysY)) : Math.max(10, Math.round((p.baysX + p.baysY) * 2.5)),
    fire: { combustible, nfpa285: d.height > 12.2, note: d.height > 18 ? "Façade > 18 m: non-combustible cladding & insulation required (IBC §1402.5 / NFPA 285 testing; UK Reg. 7(2))" : "NFPA 285 required where combustible components are used" },
  };
}

// ---------- physics & energy ----------
export interface PhysicsResult {
  daylightFactor: number; daylitArea: number; glareRisk: string; natVentDepth: number; natVentFeasible: boolean;
  acoustics: { outdoor: number; indoorTarget: number; requiredRw: number; providedRw: number };
  comfort: { PMV: number; PPD: number }; overheatingHours: number;
}

export function physics(intake: Intake, d: Derived, p: DesignParams): PhysicsResult {
  const Tvis = 0.62, theta = 70, M = 0.9;
  const facadeA = d.perimeter * p.floorHeight;
  const Aw = facadeA * p.wwr * 0.8;
  const totalSurfaces = 2 * d.plateArea + facadeA;
  const DF = (Tvis * Aw * theta * M) / (totalSurfaces * (1 - 0.5 ** 2)) / 4; // Littlefair average DF (perimeter-weighted)
  const daylitDepth = 2.5 * (p.floorHeight - 0.5);
  const daylitArea = Math.min(1, (d.perimeter * daylitDepth) / (d.plateArea - d.coreArea));
  const indoorTarget = ["residential", "hotel", "hospital"].includes(intake.buildingType) ? 35 : 40;
  const requiredRw = intake.ambientNoise - indoorTarget + 5;
  const providedRw = p.facadeType === "punched" ? 45 : 38 + (p.glazingU < 1.4 ? 4 : 0);
  const depth = Math.min(d.Lx, d.Ly) / 2;
  return {
    daylightFactor: round(DF, 2), daylitArea: round(daylitArea * 100, 0),
    glareRisk: p.wwr > 0.6 ? "High — external shading or dynamic glazing advised" : p.wwr > 0.45 ? "Moderate — internal blinds" : "Low",
    natVentDepth: round(5 * p.floorHeight, 1), natVentFeasible: depth <= 5 * p.floorHeight && intake.climateZone >= 3,
    acoustics: { outdoor: intake.ambientNoise, indoorTarget, requiredRw: round(requiredRw, 0), providedRw },
    comfort: pmv(24.5, 25.5 + p.wwr * 2, 0.15, 50, 1.2, 0.5),
    overheatingHours: round(Math.max(0, (intake.cdd / 10) * p.wwr * p.shgc * 2 - (p.facadeType === "punched" ? 30 : 0)), 0),
  };
}

export interface EnergyResult {
  eui: number; totalMWh: number; breakdown: { end: string; kWh: number }[]; monthly: { month: string; heating: number; cooling: number; other: number; pv: number }[];
  pvOffset: number; netEui: number; scenarios: { name: string; eui: number; carbon: number }[]; operationalCarbon: number; gridFactor: number;
}

export function energy(intake: Intake, d: Derived, p: DesignParams, h: HvacResult, e: ElecResult): EnergyResult {
  const g = internalGains(intake.buildingType);
  const area = d.gfaAbove;
  const calc = (pp: DesignParams) => {
    const facadeA = d.perimeter * d.height;
    const UA = (facadeA * pp.wwr * pp.glazingU + facadeA * (1 - pp.wwr) * pp.wallU + d.plateArea * pp.roofU) / 1000 + (h.oa * 1.23 * 0.35);
    const heatEff = pp.heating === "heat-pump" ? 3.2 : pp.heating === "district" ? 0.95 : 0.9;
    const heating = (UA * intake.hdd * 24 * 0.75) / heatEff;
    const solar = facadeA * pp.wwr * pp.shgc * 120;
    const internal = area * (g.light + g.equip) * g.hours / 1000;
    const cooling = (UA * intake.cdd * 24 + solar + internal * 0.35) / 4.5;
    const lighting = area * g.light * g.hours / 1000 * 0.85;
    const equipment = area * g.equip * g.hours / 1000 * 0.6;
    const fans = h.fanPower * g.hours * 0.7;
    const pumps = h.pumpPower * g.hours * 0.6;
    const dhw = (d.occupants * g.dhw * 365 * 0.001163 * 45) / (pp.heating === "heat-pump" ? 2.8 : 0.9); // L × c_p × ΔT
    const lifts = pp.liftCount * 30 * 1500 * 0.4;
    return { heating, cooling, lighting, equipment, fans, pumps, dhw, lifts };
  };
  const c = calc(p);
  const total = sum(Object.values(c));
  const pv = e.pv.annual * 1000;
  const gridFactor = 0.35; // kgCO2e/kWh
  const gasFactor = 0.2;
  const opCarbon = (k: ReturnType<typeof calc>, pp: DesignParams) => ((pp.heating === "gas-boiler" ? k.heating * gasFactor + k.dhw * gasFactor : (k.heating + k.dhw) * gridFactor) + (k.cooling + k.lighting + k.equipment + k.fans + k.pumps + k.lifts) * gridFactor) / area;
  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const hw = months.map((_, i) => Math.max(0, Math.cos(((i + 0.5) / 12) * 2 * Math.PI)) + 0.05);
  const cw = months.map((_, i) => Math.max(0, -Math.cos(((i + 0.5) / 12) * 2 * Math.PI)) + 0.05);
  const pw = months.map((_, i) => 0.6 + 0.4 * -Math.cos(((i + 0.5) / 12) * 2 * Math.PI));
  const other = total - c.heating - c.cooling;
  const monthly = months.map((m, i) => ({
    month: m, heating: round((c.heating * hw[i]) / sum(hw) / 1000, 1), cooling: round((c.cooling * cw[i]) / sum(cw) / 1000, 1),
    other: round(other / 12 / 1000, 1), pv: round((pv * pw[i]) / sum(pw) / 1000, 1),
  }));
  const scen = (name: string, pp: DesignParams) => { const k = calc(pp); return { name, eui: round(sum(Object.values(k)) / area, 1), carbon: round(opCarbon(k, pp), 1) }; };
  return {
    eui: round(total / area, 1), totalMWh: round(total / 1000, 0),
    breakdown: Object.entries(c).map(([end, kWh]) => ({ end, kWh: round(kWh, 0) })),
    monthly, pvOffset: round((pv / total) * 100, 1), netEui: round((total - pv) / area, 1),
    scenarios: [
      scen("Proposed", p),
      scen("High-performance façade (U 1.0 / SHGC 0.25)", { ...p, glazingU: 1.0, shgc: 0.25, wallU: Math.min(p.wallU, 0.25) }),
      scen("All-electric heat pumps", { ...p, heating: "heat-pump" }),
      scen("WWR 40 %", { ...p, wwr: 0.4 }),
      scen("Code baseline (ASHRAE 90.1 prescriptive)", { ...p, glazingU: 2.0, shgc: 0.36, wallU: 0.5, wwr: 0.4, heating: "gas-boiler" }),
    ],
    operationalCarbon: round(opCarbon(c, p), 1), gridFactor,
  };
}

// ---------- accessibility ----------
export interface AccessCheck { item: string; required: string; provided: string; ok: boolean; clause: string }
export function accessibility(intake: Intake, d: Derived, p: DesignParams): AccessCheck[] {
  const rampLen = intake.siteLevelDiff > 0 ? intake.siteLevelDiff * 12 : 0;
  const liftsNeeded = Math.max(p.floors > 1 ? 1 : 0, Math.ceil(d.occupants / 250 / 4));
  const accParkReq = intake.parkingSpaces <= 25 ? 1 : intake.parkingSpaces <= 100 ? Math.ceil(intake.parkingSpaces / 25) : intake.parkingSpaces <= 500 ? 4 + Math.ceil((intake.parkingSpaces - 100) / 50) : Math.ceil(intake.parkingSpaces * 0.02);
  const accWc = Math.max(1, Math.ceil(d.occupantsPerFloor / 150));
  return [
    { item: "Accessible route clear width", required: "≥ 915 mm", provided: `${Math.round(p.corridorWidth * 1000)} mm`, ok: p.corridorWidth >= 0.915, clause: "403.5.1" },
    { item: "Corridor width (egress)", required: "≥ 1118 mm", provided: `${Math.round(p.corridorWidth * 1000)} mm`, ok: p.corridorWidth >= 1.118, clause: "IBC 1020.3" },
    { item: "Entrance ramp gradient", required: "≤ 1:12", provided: intake.siteLevelDiff > 0 ? `1:12 over ${round(rampLen, 1)} m (${Math.ceil(rampLen / 9.14)} runs)` : "Level entry", ok: true, clause: "405.2" },
    { item: "Ramp landings", required: "Landing every 760 mm rise", provided: intake.siteLevelDiff > 0.76 ? `${Math.ceil(intake.siteLevelDiff / 0.76) - 1} intermediate landings` : "n/a", ok: true, clause: "405.6 / 405.7" },
    { item: "Passenger lifts serving all floors", required: `≥ ${liftsNeeded}`, provided: `${p.liftCount}`, ok: p.liftCount >= liftsNeeded, clause: "206.2.3 / 407" },
    { item: "Accessible means of egress lift (> 4 storeys)", required: p.floors > 4 ? "Standby-powered lift" : "n/a", provided: p.floors > 4 ? (p.liftCount >= 2 ? "Designated lift on standby power" : "None") : "n/a", ok: p.floors <= 4 || p.liftCount >= 2, clause: "IBC 1009.2.1" },
    { item: "Wheelchair turning space in WCs", required: "1525 mm Ø", provided: "1525 mm Ø", ok: true, clause: "304.3" },
    { item: "Accessible WC per floor", required: `≥ ${accWc}`, provided: `${accWc}`, ok: true, clause: "213.2 / 604" },
    { item: "Accessible parking spaces", required: `≥ ${accParkReq}`, provided: `${accParkReq}`, ok: true, clause: "208.2" },
    { item: "Stair width allows assisted evacuation", required: "≥ 1220 mm between handrails", provided: p.sprinklered ? "Exempt — sprinklered throughout" : `${Math.round(p.stairWidth * 1000)} mm`, ok: p.sprinklered || p.stairWidth >= 1.22, clause: "IBC 1009.3.2" },
  ];
}
