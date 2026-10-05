// Geotechnical engine: borehole interpretation, Vs30 / site class, bearing
// capacity, settlement, liquefaction triggering and a foundation optimiser.

import { round, sum } from "./linalg";
import type { SiteClass } from "./site";
import type { Borehole, BoreholeLayer, DesignParams } from "./types";

export interface LiquefactionRow { borehole: string; depth: number; soil: string; N160: number; CSR: number; CRR: number; FS: number; liquefiable: boolean }

export interface FoundationOption {
  id: "pads" | "raft" | "piles" | "barrettes" | "piled-raft";
  label: string; feasible: boolean; capacityOK: boolean; settlement: number; differential: number;
  cost: number; carbon: number; durationWeeks: number; score: number; notes: string[];
  detail: Record<string, number | string>;
}

export interface GeotechResult {
  profile: { name: string; gwl: number; layers: (BoreholeLayer & { vs: number })[] }[];
  vs30: number; siteClass: SiteClass; foundingDepth: number; foundingSoil: string;
  qult: number; qall: number; bearingPressure: number; raftSettlement: number;
  liquefaction: LiquefactionRow[]; liquefactionRisk: "none" | "low" | "high"; liquefiedThickness: number;
  options: FoundationOption[]; selected: FoundationOption; dewatering: boolean; gwlMin: number;
  pile: { diameter: number; length: number; capacity: number; count: number; shaft: number; base: number };
}

const vsFromN = (N: number, soil: string) => (soil === "rock" ? 900 : 97 * Math.max(N, 1) ** 0.314); // Imai (1977)

function siteClassFromVs(vs: number): SiteClass {
  // ASCE 7-22 Table 20.2-1
  if (vs > 1524) return "A"; if (vs > 914) return "B"; if (vs > 640) return "BC"; if (vs > 442) return "C";
  if (vs > 305) return "CD"; if (vs > 213) return "D"; if (vs > 152) return "DE"; return "E";
}

function layerAt(bh: Borehole, z: number) {
  return bh.layers.find((l) => z >= l.top && z < l.bottom) ?? bh.layers[bh.layers.length - 1];
}

function sigmaV(bh: Borehole, z: number) {
  let s = 0, u = 0;
  for (const l of bh.layers) {
    const t = Math.max(0, Math.min(z, l.bottom) - l.top);
    s += t * l.gamma;
  }
  if (z > bh.gwl) u = (z - bh.gwl) * 9.81;
  return { total: s, eff: s - u };
}

// Bearing capacity factors (Vesić / Meyerhof)
const Nq = (phi: number) => Math.exp(Math.PI * Math.tan(phi)) * Math.tan(Math.PI / 4 + phi / 2) ** 2;
const Nc = (phi: number) => (phi < 1e-3 ? 5.14 : (Nq(phi) - 1) / Math.tan(phi));
const Ng = (phi: number) => 2 * (Nq(phi) + 1) * Math.tan(phi);

export function geotech(boreholes: Borehole[], p: DesignParams, plate: { Lx: number; Ly: number }, loads: { totalService: number; colService: number }, pga: number, Mw = 7.5, region = 1): GeotechResult {
  const bhs = boreholes.length ? boreholes : [{ name: "Assumed", x: 0, y: 0, gwl: 6, layers: [{ top: 0, bottom: 40, soil: "sand" as const, spt: 25, gamma: 19, phi: 32, Es: 40 }] }];
  const profile = bhs.map((b) => ({ name: b.name, gwl: b.gwl, layers: b.layers.map((l) => ({ ...l, vs: round(vsFromN(l.spt, l.soil), 0) })) }));
  // Vs30 averaged over boreholes (harmonic per borehole)
  const vs30s = profile.map((b) => {
    let t = 0;
    for (const l of b.layers) {
      const th = Math.max(0, Math.min(30, l.bottom) - Math.min(30, l.top));
      t += th / l.vs;
    }
    const covered = Math.min(30, b.layers[b.layers.length - 1].bottom);
    if (covered < 30) t += (30 - covered) / b.layers[b.layers.length - 1].vs;
    return 30 / t;
  });
  const vs30 = sum(vs30s) / vs30s.length;
  const siteClass = siteClassFromVs(vs30);

  const foundingDepth = p.basementLevels * 3.5 + 1.0;
  const ref = bhs[0];
  const fl = layerAt(ref, foundingDepth + 0.5);
  const gwlMin = Math.min(...bhs.map((b) => b.gwl));
  const B = Math.min(plate.Lx, plate.Ly), L = Math.max(plate.Lx, plate.Ly);
  const sv = sigmaV(ref, foundingDepth);
  let qult: number;
  if (fl.soil === "clay" || (fl.soil === "silt" && (fl.cu ?? 0) > 0)) {
    const cu = fl.cu ?? 6 * fl.spt;
    qult = cu * 5.14 * (1 + 0.2 * (B / L)) * (1 + 0.2 * Math.min(foundingDepth / B, 1)) + sv.total;
  } else if (fl.soil === "rock") {
    qult = 6000 + fl.spt * 20;
  } else {
    const phi = ((fl.phi ?? 30) * Math.PI) / 180;
    const gammaEff = foundingDepth > ref.gwl ? fl.gamma - 9.81 : fl.gamma;
    qult = sv.eff * Nq(phi) * (1 + (B / L) * Math.tan(phi)) + 0.5 * gammaEff * Math.min(B, 6) * Ng(phi) * (1 - 0.4 * (B / L));
    qult = Math.min(qult, 12000);
  }
  const qall = qult / 3;
  const area = plate.Lx * plate.Ly;
  const bearingPressure = loads.totalService / area - sv.total * (p.basementLevels > 0 ? 1 : 0); // net of excavation relief

  // Settlement under raft (2:1 distribution, elastic + 1-D consolidation)
  const raftSettle = (bh: Borehole, q: number) => {
    let s = 0;
    for (let z = foundingDepth; z < Math.min(foundingDepth + 2 * B, bh.layers[bh.layers.length - 1].bottom); z += 0.5) {
      const l = layerAt(bh, z);
      const dz = 0.5;
      const zr = z - foundingDepth;
      const dsig = (q * B * L) / ((B + zr) * (L + zr));
      if (l.soil === "clay" && l.cc && l.e0) {
        const s0 = Math.max(sigmaV(bh, z).eff, 10);
        s += (l.cc * dz / (1 + l.e0)) * Math.log10((s0 + dsig) / s0);
      } else {
        s += (dsig * dz) / (l.Es * 1000);
      }
    }
    return s;
  };
  const qNet = Math.max(bearingPressure, 0);
  const sets = bhs.map((b) => raftSettle(b, qNet));
  const raftSettlement = Math.max(...sets);
  const differential = Math.max(...sets) - Math.min(...sets) + raftSettlement * 0.25;

  // Liquefaction triggering — simplified procedure (Youd et al. 2001)
  const liquefaction: LiquefactionRow[] = [];
  const MSF = 10 ** 2.24 / Mw ** 2.56;
  for (const b of bhs) {
    for (const l of b.layers) {
      if (!["sand", "silt", "fill"].includes(l.soil)) continue;
      for (let z = l.top + 0.75; z < Math.min(l.bottom, 20); z += 1.5) {
        if (z < b.gwl) continue;
        const sv0 = sigmaV(b, z);
        const CN = Math.min(1.7, Math.sqrt(100 / Math.max(sv0.eff, 10)));
        const fc = l.finesPct ?? (l.soil === "silt" ? 40 : 8);
        const a = fc <= 5 ? 0 : fc >= 35 ? 5 : Math.exp(1.76 - 190 / (fc * fc));
        const bb = fc <= 5 ? 1 : fc >= 35 ? 1.2 : 0.99 + fc ** 1.5 / 1000;
        const N160 = a + bb * l.spt * CN * 1.0;
        const rd = z <= 9.15 ? 1 - 0.00765 * z : 1.174 - 0.0267 * z;
        const CSR = 0.65 * pga * (sv0.total / sv0.eff) * rd;
        const CRR = N160 >= 30 ? 2 : 1 / (34 - N160) + N160 / 135 + 50 / (10 * N160 + 45) ** 2 - 1 / 200;
        const FS = (CRR * MSF) / CSR;
        liquefaction.push({ borehole: b.name, depth: round(z, 2), soil: l.soil, N160: round(N160, 1), CSR: round(CSR, 3), CRR: round(CRR * MSF, 3), FS: round(FS, 2), liquefiable: FS < 1.0 });
      }
    }
  }
  const liquefiedThickness = liquefaction.filter((r) => r.liquefiable).length * 1.5 / Math.max(bhs.length, 1);
  const liquefactionRisk = liquefiedThickness === 0 ? "none" : liquefiedThickness < 2 ? "low" : "high";

  // Pile design (bored piles) — α/β methods
  const pileD = loads.colService > 12000 ? 1.5 : loads.colService > 6000 ? 1.2 : 0.9;
  const shaftCap = (len: number) => {
    let qs = 0;
    for (let z = foundingDepth; z < foundingDepth + len; z += 0.5) {
      const l = layerAt(ref, z);
      if (liquefaction.some((r) => r.liquefiable && Math.abs(r.depth - z) < 0.75)) continue; // ignore liquefiable layers
      const unit = l.soil === "clay" ? 0.55 * (l.cu ?? 6 * l.spt) : l.soil === "rock" ? 250 : Math.min(0.3 * sigmaV(ref, z).eff, 150);
      qs += unit * Math.PI * pileD * 0.5;
    }
    return qs;
  };
  const baseCap = (len: number) => {
    const l = layerAt(ref, foundingDepth + len);
    const qb = l.soil === "clay" ? 9 * (l.cu ?? 6 * l.spt) : l.soil === "rock" ? 8000 : Math.min(0.6 * 57.5 * l.spt, 4500);
    return qb * (Math.PI * pileD * pileD) / 4;
  };
  let pileLen = 10;
  const targetWorking = pileD >= 1.5 ? 9000 : pileD >= 1.2 ? 5500 : 3000; // kN per pile
  while (pileLen < 60 && shaftCap(pileLen) + baseCap(pileLen) < targetWorking * 2.5) pileLen += 1;
  const pileCap = (shaftCap(pileLen) + baseCap(pileLen)) / 2.5;
  const pileCount = Math.ceil((loads.totalService * 1.05) / pileCap);

  const concreteRate = 210; // USD/m³ in place (foundations)
  const opts: FoundationOption[] = [];
  const mk = (o: Omit<FoundationOption, "score">) => opts.push({ ...o, score: 0 });
  const padArea = loads.colService / qall;
  const padsFeasible = padArea < (p.spanX * p.spanY) * 0.5 && liquefactionRisk === "none";
  const padVol = ((p.baysX + 1) * (p.baysY + 1)) * padArea * Math.max(0.8, Math.sqrt(padArea) / 4);
  mk({ id: "pads", label: "Isolated pad footings", feasible: padsFeasible, capacityOK: padArea < p.spanX * p.spanY * 0.5, settlement: round(raftSettlement * 1.3 * 1000, 0), differential: round(differential * 1.6 * 1000, 0), cost: padVol * (concreteRate + 180), carbon: padVol * 340, durationWeeks: 4, notes: padsFeasible ? ["Lowest cost if pads stay < 50 % of bay area"] : ["Pad area exceeds 50 % of bay or liquefaction present — not suitable"], detail: { padSide: round(Math.sqrt(padArea), 2) } });
  const raftT = Math.max(0.9, p.floors / 25);
  const raftVol = area * raftT;
  const raftOK = qNet <= qall && raftSettlement < 0.075;
  mk({ id: "raft", label: "Mat (raft) foundation", feasible: liquefactionRisk !== "high", capacityOK: raftOK, settlement: round(raftSettlement * 1000, 0), differential: round(differential * 1000, 0), cost: raftVol * (concreteRate + 220), carbon: raftVol * 360, durationWeeks: 6, notes: [raftOK ? "Bearing and settlement within limits" : qNet > qall ? "Net pressure exceeds allowable bearing" : "Settlement exceeds 75 mm"], detail: { thickness: round(raftT, 2), netPressure: round(qNet, 0) } });
  const pileVol = pileCount * pileLen * Math.PI * pileD * pileD / 4;
  const capVol = area * 0.4 * Math.max(0.6, raftT * 0.6);
  mk({ id: "piles", label: `Bored piles Ø${pileD} m`, feasible: true, capacityOK: true, settlement: round(Math.min(raftSettlement, 0.025) * 1000 * 0.6, 0), differential: round(differential * 300, 0), cost: pileVol * 520 + capVol * (concreteRate + 220), carbon: pileVol * 380 + capVol * 360, durationWeeks: Math.ceil(pileCount / 12) + 3, notes: ["Bypasses liquefiable/compressible layers", `${pileCount} piles × ${pileLen} m`], detail: { count: pileCount, length: pileLen, capacity: round(pileCap, 0) } });
  const barretteCount = Math.ceil(pileCount / 2.6);
  const barrVol = barretteCount * pileLen * 1.2 * 2.8 * 1.05;
  mk({ id: "barrettes", label: "Barrettes (1.2 × 2.8 m)", feasible: p.floors > 30 || loads.colService > 15000, capacityOK: true, settlement: round(Math.min(raftSettlement, 0.02) * 1000 * 0.5, 0), differential: round(differential * 250, 0), cost: barrVol * 610 + capVol * (concreteRate + 220), carbon: barrVol * 390 + capVol * 360, durationWeeks: Math.ceil(barretteCount / 6) + 4, notes: ["High capacity under core; needs diaphragm-wall rig & bentonite plant"], detail: { count: barretteCount, length: pileLen } });
  const prCount = Math.ceil(pileCount * 0.55);
  const prVol = prCount * pileLen * Math.PI * pileD * pileD / 4;
  mk({ id: "piled-raft", label: "Piled raft", feasible: liquefactionRisk !== "high", capacityOK: true, settlement: round(raftSettlement * 0.45 * 1000, 0), differential: round(differential * 0.4 * 1000, 0), cost: prVol * 520 + raftVol * 0.85 * (concreteRate + 220), carbon: prVol * 380 + raftVol * 0.85 * 360, durationWeeks: Math.ceil(prCount / 12) + 5, notes: ["Raft shares load; piles act as settlement reducers (~55 % of full pile count)"], detail: { count: prCount, length: pileLen } });

  const feasible = opts.filter((o) => o.feasible && o.capacityOK && o.settlement <= 75);
  const minCost = Math.min(...feasible.map((o) => o.cost), Infinity);
  const minCarbon = Math.min(...feasible.map((o) => o.carbon), Infinity);
  opts.forEach((o) => {
    o.cost = round(o.cost * region, 0); o.carbon = round(o.carbon / 1000, 1);
    o.score = o.feasible && o.capacityOK && o.settlement <= 75 ? round(100 * (0.5 * (minCost * region) / o.cost + 0.3 * (minCarbon / 1000) / o.carbon + 0.2 * (4 / o.durationWeeks)), 1) : 0;
  });
  const selected = [...opts].sort((a, b) => b.score - a.score)[0];

  return {
    profile, vs30: round(vs30, 0), siteClass, foundingDepth, foundingSoil: fl.soil, qult: round(qult, 0), qall: round(qall, 0),
    bearingPressure: round(qNet, 0), raftSettlement: round(raftSettlement * 1000, 1), liquefaction, liquefactionRisk,
    liquefiedThickness: round(liquefiedThickness, 1), options: opts, selected, dewatering: gwlMin < foundingDepth, gwlMin,
    pile: { diameter: pileD, length: pileLen, capacity: round(pileCap, 0), count: pileCount, shaft: round(shaftCap(pileLen), 0), base: round(baseCap(pileLen), 0) },
  };
}
