// MEP engines: HVAC (loads, ventilation, plant, ducts, comfort), electrical
// (load schedule, transformers, cables, VD, fault level, PV/BESS/EV,
// generator) and hydraulics (fixtures, water, pumps, sewer, storm, DHW,
// rainwater and greywater).

import { round, sum } from "./linalg";
import type { Derived } from "./site";
import type { BuildingType, DesignParams, Intake } from "./types";

// ---------------- thermal comfort: ISO 7730 PMV/PPD ----------------
export function pmv(ta: number, tr: number, vel: number, rh: number, met: number, clo: number) {
  const pa = rh * 10 * Math.exp(16.6536 - 4030.183 / (ta + 235));
  const icl = 0.155 * clo, m = met * 58.15, w = 0, mw = m - w;
  const fcl = icl <= 0.078 ? 1 + 1.29 * icl : 1.05 + 0.645 * icl;
  const hcf = 12.1 * Math.sqrt(vel);
  const taa = ta + 273, tra = tr + 273;
  let tcla = taa + (35.5 - ta) / (3.5 * icl + 0.1);
  const p1 = icl * fcl, p2 = p1 * 3.96, p3 = p1 * 100, p4 = p1 * taa, p5 = 308.7 - 0.028 * mw + p2 * (tra / 100) ** 4;
  let xn = tcla / 100, xf = tcla / 50, hc = hcf, n = 0;
  while (Math.abs(xn - xf) > 0.00015 && n < 150) {
    xf = (xf + xn) / 2;
    const hcn = 2.38 * Math.abs(100 * xf - taa) ** 0.25;
    hc = hcf > hcn ? hcf : hcn;
    xn = (p5 + p4 * hc - p2 * xf ** 4) / (100 + p3 * hc);
    n++;
  }
  const tcl = 100 * xn - 273;
  const hl1 = 3.05 * 0.001 * (5733 - 6.99 * mw - pa);
  const hl2 = mw > 58.15 ? 0.42 * (mw - 58.15) : 0;
  const hl3 = 1.7 * 0.00001 * m * (5867 - pa);
  const hl4 = 0.0014 * m * (34 - ta);
  const hl5 = 3.96 * fcl * (xn ** 4 - (tra / 100) ** 4);
  const hl6 = fcl * hc * (tcl - ta);
  const ts = 0.303 * Math.exp(-0.036 * m) + 0.028;
  const PMV = ts * (mw - hl1 - hl2 - hl3 - hl4 - hl5 - hl6);
  const PPD = 100 - 95 * Math.exp(-0.03353 * PMV ** 4 - 0.2179 * PMV ** 2);
  return { PMV: round(PMV, 2), PPD: round(PPD, 1) };
}

const INTERNAL: Record<BuildingType, { light: number; equip: number; Rp: number; Ra: number; hours: number; dhw: number; water: number }> = {
  // W/m² lighting & equipment; ASHRAE 62.1-2022 Table 6.2.2.1 Rp (L/s·person), Ra (L/s·m²); operating h/yr; DHW & cold water L/person/day
  office: { light: 6.5, equip: 12, Rp: 2.5, Ra: 0.3, hours: 3000, dhw: 4, water: 40 },
  residential: { light: 5, equip: 6, Rp: 2.5, Ra: 0.3, hours: 6000, dhw: 50, water: 150 },
  hospital: { light: 10, equip: 20, Rp: 2.5, Ra: 0.6, hours: 8760, dhw: 60, water: 400 },
  school: { light: 8, equip: 6, Rp: 3.8, Ra: 0.3, hours: 2200, dhw: 5, water: 25 },
  retail: { light: 12, equip: 8, Rp: 3.8, Ra: 0.6, hours: 4000, dhw: 2, water: 10 },
  "mixed-use": { light: 7, equip: 10, Rp: 2.5, Ra: 0.3, hours: 4000, dhw: 20, water: 70 },
  laboratory: { light: 10, equip: 35, Rp: 5, Ra: 0.9, hours: 4500, dhw: 6, water: 60 },
  hotel: { light: 7, equip: 8, Rp: 2.5, Ra: 0.3, hours: 7000, dhw: 70, water: 250 },
  warehouse: { light: 5, equip: 3, Rp: 0, Ra: 0.3, hours: 3000, dhw: 2, water: 15 },
};
export const internalGains = (t: BuildingType) => INTERNAL[t];

export interface HvacResult {
  zones: { name: string; area: number; sensible: number; latent: number; airflow: number; wPerM2: number }[];
  coolingPeak: number; heatingPeak: number; coolingWm2: number; heatingWm2: number; oa: number; oaPerPerson: number;
  breakdown: { name: string; kW: number }[];
  plant: { chillers: number; chillerSize: number; redundancy: string; towers: number; boilers: number; boilerSize: number; heatPumps: number; ahus: number; ahuSize: number; plantArea: number; riserArea: number };
  ducts: { mainDiameter: number; mainVelocity: number; riserDiameter: number; frictionRate: number; ceilingVoid: number };
  comfort: { summer: { PMV: number; PPD: number }; winter: { PMV: number; PPD: number } };
  fanPower: number; pumpPower: number;
}

export function hvac(intake: Intake, d: Derived, p: DesignParams): HvacResult {
  const g = INTERNAL[intake.buildingType];
  const tIn = 24, tInW = 21;
  const dTs = Math.max(intake.summerDB - tIn, 4);
  const dTw = Math.max(tInW - intake.winterDB, 5);
  const floorFacade = d.perimeter * p.floorHeight;
  const glazing = floorFacade * p.wwr, opaque = floorFacade - glazing;
  const people = d.occupantsPerFloor;
  const solarI = 420 + intake.climateZone * -20; // W/m² peak on glazing, orientation-averaged
  const perimeterDepth = 4.5;
  const perimArea = d.perimeter * perimeterDepth - 4 * perimeterDepth ** 2;
  const coreZoneArea = d.plateArea - perimArea - d.coreArea;
  const oaFloor = (g.Rp * people + g.Ra * (d.plateArea - d.coreArea)) / 0.8; // Ez = 0.8 ceiling supply
  const comps = {
    conduction: (glazing * p.glazingU + opaque * p.wallU) * dTs / 1000,
    solar: glazing * p.shgc * solarI * 0.6 / 1000,
    people: people * 75 / 1000,
    lighting: (d.plateArea - d.coreArea) * g.light / 1000,
    equipment: (d.plateArea - d.coreArea) * g.equip / 1000,
    ventilation: 1.23 * oaFloor * dTs / 1000,
  };
  const latentPeople = people * 55 / 1000;
  const latentOA = 3010 * (oaFloor / 1000) * 0.006; // Δw ≈ 6 g/kg
  const sensFloor = sum(Object.values(comps).slice(0, 5));
  const zones = ["North", "East", "South", "West"].map((n, i) => {
    const area = perimArea / 4;
    const solarF = [0.55, 1.1, 0.9, 1.25][i];
    const s = (comps.conduction / 4 + comps.solar / 4 * solarF + (comps.people + comps.lighting + comps.equipment) * (area / (d.plateArea - d.coreArea)));
    return { name: `${n} perimeter`, area: round(area, 0), sensible: round(s, 1), latent: round(latentPeople * area / (d.plateArea - d.coreArea), 1), airflow: round(s / (1.23 * 10) * 1000, 0), wPerM2: round((s * 1000) / area, 0) };
  });
  const coreS = (comps.people + comps.lighting + comps.equipment) * (coreZoneArea / (d.plateArea - d.coreArea));
  zones.push({ name: "Interior", area: round(coreZoneArea, 0), sensible: round(coreS, 1), latent: round(latentPeople * coreZoneArea / (d.plateArea - d.coreArea), 1), airflow: round(coreS / 12.3 * 1000, 0), wPerM2: round((coreS * 1000) / Math.max(coreZoneArea, 1), 0) });
  const diversity = 0.85;
  const coolingPeak = (sensFloor + comps.ventilation + latentPeople + latentOA) * p.floors * diversity * 1.1; // +10 % fan/duct gains
  const heatingPeak = ((glazing * p.glazingU + opaque * p.wallU) * dTw / 1000 + 1.23 * oaFloor * dTw / 1000 * 0.35) * p.floors + d.plateArea * p.roofU * dTw / 1000;
  const breakdown = [
    { name: "Envelope conduction", kW: comps.conduction }, { name: "Solar", kW: comps.solar }, { name: "People", kW: comps.people + latentPeople },
    { name: "Lighting", kW: comps.lighting }, { name: "Equipment", kW: comps.equipment }, { name: "Ventilation", kW: comps.ventilation + latentOA },
  ].map((b) => ({ name: b.name, kW: round(b.kW * p.floors * diversity, 0) }));
  // plant (N+1 chillers)
  const chillerSize = [350, 500, 700, 1000, 1400, 1750, 2100].find((s) => s * 2 >= coolingPeak) ?? 2100;
  const chillers = Math.ceil(coolingPeak / chillerSize) + 1;
  const boilerSize = [150, 300, 500, 800, 1200].find((s) => s * 2 >= heatingPeak) ?? 1200;
  const hp = p.heating === "heat-pump";
  const oa = oaFloor * p.floors;
  const supply = sum(zones.map((z) => z.airflow)) * p.floors / 1000; // m³/s
  const ahuSize = [5, 10, 15, 20, 25, 30].find((s) => s * 4 >= supply) ?? 30;
  const ahus = Math.max(2, Math.ceil(supply / ahuSize));
  const floorSupply = sum(zones.map((z) => z.airflow)) / 1000; // m³/s per floor
  const mainVelocity = 7.5;
  const mainDiameter = Math.sqrt((4 * (floorSupply / 2)) / (Math.PI * mainVelocity)); // two loops per floor
  const riserFlow = supply / Math.max(1, Math.ceil(p.floors / 20)) / 2;
  const riserDiameter = Math.sqrt((4 * riserFlow) / (Math.PI * 10));
  const ceilingVoid = p.floorHeight - 2.7 - p.slabThickness;
  return {
    zones, coolingPeak: round(coolingPeak, 0), heatingPeak: round(heatingPeak, 0),
    coolingWm2: round((coolingPeak * 1000) / d.gfaAbove, 1), heatingWm2: round((heatingPeak * 1000) / d.gfaAbove, 1),
    oa: round(oa / 1000, 2), oaPerPerson: round(oaFloor / Math.max(people, 1), 1), breakdown,
    plant: {
      chillers, chillerSize, redundancy: "N+1", towers: chillers - 1, boilers: hp ? 0 : Math.ceil(heatingPeak / boilerSize) + 1, boilerSize,
      heatPumps: hp ? Math.ceil(heatingPeak / 400) + 1 : 0, ahus, ahuSize,
      plantArea: round(coolingPeak * 0.12 + ahus * 25, 0), riserArea: round(riserDiameter ** 2 * 1.6 * 2 + 1.2, 1),
    },
    ducts: { mainDiameter: round(mainDiameter, 2), mainVelocity, riserDiameter: round(riserDiameter, 2), frictionRate: 1.0, ceilingVoid: round(ceilingVoid, 2) },
    comfort: { summer: pmv(24, 25, 0.15, 50, 1.2, 0.5), winter: pmv(21.5, 21, 0.1, 40, 1.2, 1.0) },
    fanPower: round(supply * 1.8, 0), pumpPower: round(coolingPeak * 0.025, 0),
  };
}

// ---------------- electrical ----------------
const CABLES = [ // Cu XLPE 4-core, mm², ampacity (A) in tray, R (Ω/km @90 °C), X (Ω/km)
  [16, 91, 1.47, 0.08], [25, 119, 0.927, 0.08], [35, 147, 0.668, 0.08], [50, 179, 0.494, 0.079], [70, 229, 0.342, 0.078],
  [95, 278, 0.247, 0.078], [120, 322, 0.196, 0.077], [150, 371, 0.159, 0.077], [185, 424, 0.128, 0.077], [240, 500, 0.0984, 0.076], [300, 576, 0.0799, 0.076],
] as const;
const BREAKERS = [63, 80, 100, 125, 160, 200, 250, 320, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3200, 4000];

export interface ElecResult {
  schedule: { load: string; connected: number; demandFactor: number; demand: number }[];
  maxDemandKW: number; maxDemandKVA: number; pf: number; vaPerM2: number;
  transformers: { count: number; size: number; config: string; utilisation: number };
  mainSwitchboard: { current: number; rating: number; faultKA: number };
  risers: { name: string; length: number; current: number; cable: string; parallel: number; vd: number; breaker: number }[];
  pv: { kWp: number; annual: number; share: number }; battery: { kWh: number; kW: number };
  ev: { chargers: number; kW: number; managedKW: number };
  generator: { kVA: number; lifeSafetyKW: number; standbyKW: number; fuelHours: number };
  lifts: number;
}

export function electrical(intake: Intake, d: Derived, p: DesignParams, h: HvacResult): ElecResult {
  const g = INTERNAL[intake.buildingType];
  const nla = d.plateArea * p.floors - d.coreArea * p.floors;
  const hp = p.heating === "heat-pump";
  const liftKW = p.liftCount * 30;
  const evChargers = Math.ceil(intake.parkingSpaces * 0.2);
  const rows = [
    { load: "Lighting", connected: nla * g.light / 1000, demandFactor: 0.9 },
    { load: "Small power", connected: nla * g.equip / 1000, demandFactor: 0.6 },
    { load: "Chillers", connected: (h.coolingPeak / 5.8) * (h.plant.chillers - 1) / Math.max(h.plant.chillers - 1, 1), demandFactor: 0.9 },
    { load: "Heating / heat pumps", connected: hp ? h.heatingPeak / 3.2 : h.heatingPeak * 0.02, demandFactor: 0.7 },
    { load: "AHU & fans", connected: h.fanPower, demandFactor: 0.85 },
    { load: "Pumps", connected: h.pumpPower + 30, demandFactor: 0.8 },
    { load: "Lifts", connected: liftKW, demandFactor: p.liftCount > 4 ? 0.6 : 0.8 },
    { load: "EV charging (managed)", connected: evChargers * 7.4, demandFactor: 0.35 },
    { load: "Domestic water & hydraulics", connected: 25 + p.floors * 1.5, demandFactor: 0.6 },
    { load: "Life safety (smoke fans, fire pumps)", connected: 90 + p.floors * 6, demandFactor: 0.1 },
  ].map((r) => ({ ...r, connected: round(r.connected, 0), demand: round(r.connected * r.demandFactor, 0) }));
  const pf = 0.92;
  const maxDemandKW = sum(rows.map((r) => r.demand));
  const kva = maxDemandKW / pf;
  const sizes = [500, 750, 1000, 1500, 2000, 2500, 3150];
  const critical = intake.buildingType === "hospital" || intake.buildingType === "laboratory";
  const count = critical ? 2 : kva > 2500 ? Math.ceil(kva / 2500) : 1;
  const size = sizes.find((s) => s * (critical ? 1 : count) >= kva * 1.2) ?? 3150;
  const V = 400;
  const I = (kva * 1000) / (Math.sqrt(3) * V) / count;
  const faultKA = (size * 1000) / (Math.sqrt(3) * V * 0.06) / 1000;
  const breaker = (a: number) => BREAKERS.find((b) => b >= a * 1.1) ?? 4000;
  const riserLoads = [
    { name: "Riser 1 – Levels 1–mid lighting & power", kw: (rows[0].demand + rows[1].demand) / 2, length: d.height / 2 + 30 },
    { name: "Riser 2 – mid–roof lighting & power", kw: (rows[0].demand + rows[1].demand) / 2, length: d.height + 30 },
    { name: "Mech plant (roof)", kw: rows[2].demand + rows[4].demand * 0.6, length: d.height + 40 },
    { name: "Lifts", kw: rows[6].demand, length: d.height + 20 },
    { name: "EV / car park", kw: rows[7].demand, length: 80 },
  ];
  const risers = riserLoads.map((r) => {
    const current = (r.kw * 1000) / (Math.sqrt(3) * V * pf);
    let choice = CABLES[CABLES.length - 1], parallel = 1, vd = 99;
    outer: for (parallel = 1; parallel <= 8; parallel++) {
      for (const c of CABLES) {
        if (c[1] * parallel * 0.8 < current) continue; // 0.8 grouping derate
        vd = (Math.sqrt(3) * current * (r.length / 1000) * ((c[2] * pf + c[3] * Math.sqrt(1 - pf * pf)) / parallel)) / V * 100;
        if (vd <= 3) { choice = c; break outer; }
      }
    }
    return { name: r.name, length: round(r.length, 0), current: round(current, 0), cable: `${choice[0]} mm² Cu XLPE`, parallel, vd: round(vd, 2), breaker: breaker(current) };
  });
  const roof = d.plateArea * p.pvCoverage * 0.75;
  const kWp = roof * 0.2;
  const yieldPerKwp = 1700 - intake.climateZone * 110;
  const annual = kWp * yieldPerKwp;
  const lifeSafetyKW = rows[9].connected + (d.highRise ? 2 * 30 : 0) + nla * 1 / 1000;
  const standbyKW = critical ? maxDemandKW * 0.7 : maxDemandKW * 0.15;
  return {
    schedule: rows, maxDemandKW: round(maxDemandKW, 0), maxDemandKVA: round(kva, 0), pf, vaPerM2: round((kva * 1000) / d.gfaAbove, 1),
    transformers: { count, size, config: critical || count > 1 ? `${count} × ${size} kVA (N+1 / 2N)` : `1 × ${size} kVA`, utilisation: round(kva / (size * count), 2) },
    mainSwitchboard: { current: round(I, 0), rating: breaker(I), faultKA: round(faultKA, 1) },
    risers, pv: { kWp: round(kWp, 0), annual: round(annual / 1000, 0), share: 0 },
    battery: { kWh: round(maxDemandKW * 0.2 * 2, 0), kW: round(maxDemandKW * 0.2, 0) },
    ev: { chargers: evChargers, kW: round(evChargers * 7.4, 0), managedKW: rows[7].demand },
    generator: { kVA: [200, 300, 400, 500, 750, 1000, 1250, 1500, 2000, 2500].find((s) => s * 0.8 >= lifeSafetyKW + standbyKW) ?? 2500, lifeSafetyKW: round(lifeSafetyKW, 0), standbyKW: round(standbyKW, 0), fuelHours: critical ? 72 : 24 },
    lifts: p.liftCount,
  };
}

// ---------------- hydraulics ----------------
export interface HydResult {
  fixtures: { type: string; count: number; wsfu: number; dfu: number }[];
  wsfu: number; peakFlow: number; mainDiameter: number; velocity: number; dailyDemand: number;
  pressureZones: number; boosterHead: number; boosterKW: number; boosterRequired: boolean;
  dfu: number; stackDiameter: number; buildingDrain: number;
  storm: { roofArea: number; flow: number; drains: number; drainSize: number; detention: number; overflow: boolean };
  dhw: { storage: number; heaterKW: number; recirculation: boolean };
  rainwater: { annualYield: number; tank: number; demandOffset: number };
  greywater: { daily: number; flushingOffset: number };
}

const hwLoss = (Q: number, D: number, C = 140) => 10.67 * Q ** 1.852 / (C ** 1.852 * D ** 4.87); // m/m

export function hydraulics(intake: Intake, d: Derived, p: DesignParams): HydResult {
  const g = INTERNAL[intake.buildingType];
  const occ = d.occupants;
  const res = ["residential", "hotel"].includes(intake.buildingType);
  const units = res ? Math.round(d.nla / 75) : 0;
  const wc = res ? units * 1.5 : Math.ceil(occ / 40);
  const lav = res ? units * 1.5 : Math.ceil(occ / 60);
  const shower = res ? units : Math.ceil(occ / 200);
  const sink = res ? units : p.floors * 2;
  const df = Math.ceil(occ / 150);
  const fixtures = [
    { type: "Water closet (flush valve)", count: wc, wsfu: 5, dfu: 4 },
    { type: "Lavatory", count: lav, wsfu: 1, dfu: 1 },
    { type: "Shower", count: shower, wsfu: 2, dfu: 2 },
    { type: "Kitchen sink", count: sink, wsfu: 1.5, dfu: 2 },
    { type: "Drinking fountain", count: df, wsfu: 0.25, dfu: 0.5 },
  ].map((f) => ({ ...f, count: Math.round(f.count) }));
  const wsfu = sum(fixtures.map((f) => f.count * f.wsfu));
  const dfu = sum(fixtures.map((f) => f.count * f.dfu));
  const peakFlow = 0.1 * wsfu ** 0.62; // Hunter-curve fit, L/s (flush-valve dominated)
  const Qm3 = peakFlow / 1000;
  const sizes = [0.05, 0.065, 0.08, 0.1, 0.125, 0.15, 0.2];
  const mainDiameter = sizes.find((D) => Qm3 / (Math.PI * D * D / 4) <= 2.0) ?? 0.2;
  const velocity = Qm3 / (Math.PI * mainDiameter ** 2 / 4);
  const cityPressure = 350; // kPa
  const static_ = d.height * 9.81;
  const friction = hwLoss(Qm3, mainDiameter) * (d.height + 60) * 9.81 * 1.3;
  const residual = 100;
  const boosterRequired = static_ + friction + residual > cityPressure;
  const boosterHead = Math.max(0, static_ + friction + residual - cityPressure * 0.5);
  const boosterKW = (9.81 * Qm3 * 1000 * (boosterHead / 9.81)) / 1000 / 0.65;
  const pressureZones = Math.max(1, Math.ceil(static_ / 450));
  const stackDiameter = dfu > 1000 ? 0.15 : dfu > 500 ? 0.125 : dfu > 240 ? 0.1 : 0.075;
  const buildingDrain = dfu > 1400 ? 0.2 : dfu > 700 ? 0.15 : 0.1;
  const roofArea = d.plateArea;
  const flow = (0.95 * intake.rainfall * roofArea) / 3600; // L/s (rational method, C = 0.95)
  const drainCap = 9; // L/s per 100 mm drain at 50 mm head
  const drains = Math.max(2, Math.ceil(flow / drainCap));
  const detention = Math.max(0, (flow - 0.5 * flow) * 3.6); // m³ for 1 h at 50 % discharge limit
  const dailyDemand = (occ * g.water) / 1000;
  const storage = (occ * g.dhw * 0.4);
  const annualYield = (roofArea * intake.annualRainfall * 0.8) / 1000;
  const flushDemand = (wc * (res ? 4 : 6) * 4 * 260) / 1000;
  return {
    fixtures, wsfu: round(wsfu, 0), peakFlow: round(peakFlow, 2), mainDiameter, velocity: round(velocity, 2), dailyDemand: round(dailyDemand, 1),
    pressureZones, boosterHead: round(boosterHead, 0), boosterKW: round(boosterKW, 1), boosterRequired,
    dfu: round(dfu, 0), stackDiameter, buildingDrain,
    storm: { roofArea: round(roofArea, 0), flow: round(flow, 1), drains, drainSize: 100, detention: round(detention, 1), overflow: true },
    dhw: { storage: round(storage, 0), heaterKW: round(storage * 0.0116 * 50 / 2, 0), recirculation: d.height > 20 },
    rainwater: { annualYield: round(annualYield, 0), tank: round(Math.min(annualYield / 12, flushDemand / 12), 0), demandOffset: round(Math.min(1, annualYield / Math.max(flushDemand, 1)) * 100, 0) },
    greywater: { daily: round(occ * (res ? 60 : 5) / 1000, 1), flushingOffset: round(Math.min(100, (occ * (res ? 60 : 5)) / Math.max(wc * 6 * 4, 1) * 100), 0) },
  };
}
