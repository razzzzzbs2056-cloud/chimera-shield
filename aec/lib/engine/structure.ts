// Structural engine: system catalogue + selection, gravity/seismic loads,
// planar FE model, modal analysis, response spectrum (CQC), drift, P-Δ,
// torsion screening, capacity-spectrum pushover and response-history analysis.

import { Frame2D, type FElem, type FLoadCase, type FNode } from "./frame2d";
import { invert, jacobiEigen, rng, round, sum, zeros, type Matrix } from "./linalg";
import { designSa, G, type Derived, type SeismicParams } from "./site";
import type { DesignParams, Intake, LateralSystem, StructuralMaterial } from "./types";

// ---------------- system catalogue (ASCE 7-22 Table 12.2-1) ----------------
export interface SystemInfo {
  id: Exclude<LateralSystem, "auto">; label: string; R: number; Cd: number; Omega0: number;
  Ct: number; x: number; limitD: number | null; limitE: number | null; limitF: number | null;
  materials: StructuralMaterial[]; row: string; listed: boolean; mu: number; damping: number;
}

export const SYSTEMS: SystemInfo[] = [
  { id: "core", label: "Concrete core walls (building frame)", R: 6, Cd: 5, Omega0: 2.5, Ct: 0.0488, x: 0.75, limitD: 73.2, limitE: 73.2, limitF: 30.5, materials: ["concrete", "steel", "composite", "timber"], row: "B4 Special reinforced concrete shear walls (with §12.2.5.4 increase)", listed: true, mu: 5, damping: 0.05 },
  { id: "core-outrigger", label: "Core + outrigger trusses", R: 6, Cd: 5, Omega0: 2.5, Ct: 0.0488, x: 0.75, limitD: 73.2, limitE: 73.2, limitF: 30.5, materials: ["concrete", "steel", "composite"], row: "B4 + outriggers (height above limit requires PBD, §12.2.1.1 / §1.3.1.3)", listed: true, mu: 5, damping: 0.05 },
  { id: "shear-wall", label: "Distributed shear walls", R: 6, Cd: 5, Omega0: 2.5, Ct: 0.0488, x: 0.75, limitD: 48.8, limitE: 48.8, limitF: 30.5, materials: ["concrete", "composite"], row: "B4 Special reinforced concrete shear walls", listed: true, mu: 5, damping: 0.05 },
  { id: "moment-frame", label: "Special moment frames", R: 8, Cd: 5.5, Omega0: 3, Ct: 0.0466, x: 0.9, limitD: null, limitE: null, limitF: null, materials: ["concrete", "steel", "composite"], row: "C1/C5 Special moment frames", listed: true, mu: 6, damping: 0.05 },
  { id: "braced-frame", label: "Buckling-restrained braced frames", R: 8, Cd: 5, Omega0: 2.5, Ct: 0.0731, x: 0.75, limitD: 48.8, limitE: 48.8, limitF: 30.5, materials: ["steel", "composite", "timber"], row: "B25 Buckling-restrained braced frames", listed: true, mu: 6, damping: 0.03 },
  { id: "dual", label: "Dual: moment frame + core walls", R: 7, Cd: 5.5, Omega0: 2.5, Ct: 0.0488, x: 0.75, limitD: null, limitE: null, limitF: null, materials: ["concrete", "steel", "composite"], row: "D3 Dual system, special RC walls + SMF", listed: true, mu: 6, damping: 0.05 },
  { id: "diagrid", label: "Steel diagrid", R: 6, Cd: 5, Omega0: 2, Ct: 0.0488, x: 0.75, limitD: null, limitE: null, limitF: null, materials: ["steel", "composite"], row: "Not listed – approved alternative / PBD (§12.2.1.1)", listed: false, mu: 4, damping: 0.03 },
  { id: "clt-wall", label: "Cross-laminated timber shear walls", R: 3, Cd: 3, Omega0: 3, Ct: 0.0488, x: 0.75, limitD: 19.8, limitE: 19.8, limitF: 19.8, materials: ["timber"], row: "A17 Cross-laminated timber shear walls", listed: true, mu: 3, damping: 0.04 },
];
export const systemInfo = (id: Exclude<LateralSystem, "auto">) => SYSTEMS.find((s) => s.id === id)!;

export function heightLimit(s: SystemInfo, sdc: string): number | null {
  if (["A", "B", "C"].includes(sdc)) return s.id === "clt-wall" ? 19.8 : null;
  return sdc === "D" ? s.limitD : sdc === "E" ? s.limitE : s.limitF;
}

// ---------------- materials & sections ----------------
export interface Sections {
  Ec: number; Es: number; Et: number; colE: number;
  colA: (tier: number) => number; colI: (tier: number) => number; colSize: (tier: number) => number;
  beamE: number; beamA: number; beamI: number; beamDepth: number;
  coreE: number; coreA: number; coreI: number; braceA: number; outriggerI: number;
}

export function sections(p: DesignParams, system: string): Sections {
  const Ec = 4700 * Math.sqrt(p.concreteGrade) * 1000; // kN/m², ACI 318-19 §19.2.2.1
  const Es = 200e6, Et = 12e6;
  const tierFactor = [1, 0.85, 0.7];
  const colSize = (t: number) => Math.max(0.3, p.columnSize * tierFactor[t]);
  let colE = Ec, colA = (t: number) => colSize(t) ** 2, colI = (t: number) => 0.7 * colSize(t) ** 4 / 12;
  if (p.material === "steel" || p.material === "composite") {
    colE = Es; colA = (t) => 0.25 * colSize(t) ** 2; colI = (t) => 0.045 * colSize(t) ** 4;
  } else if (p.material === "timber") {
    colE = Et; colA = (t) => colSize(t) ** 2; colI = (t) => colSize(t) ** 4 / 12;
  }
  const span = Math.max(p.spanX, p.spanY);
  let beamE = Ec, beamDepth = 0, beamA = 0, beamI = 0;
  if (p.slabSystem === "beam-slab") {
    beamDepth = Math.max(0.45, span / 14);
    const bw = Math.max(0.3, beamDepth * 0.5);
    beamA = bw * beamDepth; beamI = 0.35 * (bw * beamDepth ** 3) / 12 * 2; // T-beam flange ≈ 2× web inertia
  } else if (p.slabSystem === "flat-plate" || p.slabSystem === "post-tensioned") {
    const strip = p.spanY * 0.5; // effective slab-beam width for lateral (≈ ½ panel width)
    beamA = strip * p.slabThickness; beamI = (p.slabSystem === "post-tensioned" ? 0.5 : 0.25) * strip * p.slabThickness ** 3 / 12;
    beamDepth = p.slabThickness;
  } else if (p.slabSystem === "composite-deck") {
    beamE = Es; beamDepth = Math.max(0.36, span / 22); beamA = 0.04 * beamDepth ** 2; beamI = 1.8 * 0.0075 * beamDepth ** 4;
  } else {
    beamE = Et; beamDepth = Math.max(0.4, span / 17); const b = Math.max(0.2, beamDepth * 0.4);
    beamA = b * beamDepth; beamI = b * beamDepth ** 3 / 12;
  }
  const t = p.coreWallThickness;
  const D = p.coreWidth, B = p.coreDepth;
  let coreE = Ec, coreA = B * D - (B - 2 * t) * (D - 2 * t);
  let coreI = 0.75 * 0.5 * (B * D ** 3 - (B - 2 * t) * (D - 2 * t) ** 3) / 12; // openings × cracked
  if (system === "shear-wall") {
    const Lw = p.spanX; coreA = 4 * t * Lw; coreI = 0.5 * 4 * (t * Lw ** 3) / 12;
  }
  if (system === "clt-wall") { coreE = 4e6; coreI = (B * D ** 3 - (B - 2 * t) * (D - 2 * t) ** 3) / 12; }
  const braceA = p.material === "timber" ? 0.09 : 0.012 + 0.0004 * p.floors;
  return { Ec, Es, Et, colE, colA, colI, colSize, beamE, beamA, beamI, beamDepth, coreE, coreA, coreI, braceA, outriggerI: 2 * 2 * 0.08 * (p.floorHeight / 2) ** 2 }; // two 1-storey trusses, chord area 0.08 m²
}

// ---------------- gravity & seismic weight ----------------
export interface FloorLoads { dead: number; live: number; slabSelf: number; W: number[]; Wtotal: number; deadPerFloor: number[]; livePerFloor: number[] }

export function slabSelfWeight(p: DesignParams) {
  switch (p.slabSystem) {
    case "composite-deck": return p.slabThickness * 0.8 * 24 + 0.45;
    case "clt": return p.slabThickness * 5 + 1.2; // CLT + 50 mm screed
    case "beam-slab": return p.slabThickness * 24 + 0.9;
    default: return p.slabThickness * 24;
  }
}

export function facadeWeight(p: DesignParams) {
  return { "curtain-wall": 0.5, unitised: 0.65, punched: 3.0, rainscreen: 1.1 }[p.facadeType];
}

export function floorLoads(intake: Intake, d: Derived, p: DesignParams, system: string): FloorLoads {
  const s = sections(p, system);
  const slab = slabSelfWeight(p);
  const nCols = (p.baysX + 1) * (p.baysY + 1);
  const W: number[] = [], deadPF: number[] = [], livePF: number[] = [];
  const dens = p.material === "timber" ? 5 : p.material === "concrete" ? 24 : 78.5;
  for (let i = 0; i < p.floors; i++) {
    const h = d.storyHeights[i];
    const tier = Math.min(2, Math.floor((3 * i) / p.floors));
    const colW = nCols * s.colA(tier) * h * dens;
    const coreWall = system === "clt-wall" ? s.coreA * h * 5 : s.coreA * h * 24;
    const fac = d.perimeter * h * facadeWeight(p);
    const roof = i === p.floors - 1;
    const area = d.plateArea;
    const dead = area * (slab + d.sdl + (roof ? 1.2 : d.partition)) + colW + coreWall + fac;
    const live = area * (roof ? Math.max(1.0, 0) : d.liveLoad);
    // ASCE 7-22 §12.7.2: seismic weight includes 25 % storage live, partitions ≥ 0.48 kPa, operating equipment
    const seismic = dead + (intake.buildingType === "warehouse" ? 0.25 * live : 0);
    W.push(seismic); deadPF.push(dead); livePF.push(live);
  }
  return { dead: d.sdl + slab, live: d.liveLoad, slabSelf: slab, W, Wtotal: sum(W), deadPerFloor: deadPF, livePerFloor: livePF };
}

// ---------------- planar model ----------------
export interface Model {
  frame: Frame2D; perFloor: number; lines: number; coreNode: (j: number) => number; lineNode: (i: number, j: number) => number;
  hasCore: boolean; nF: number; elemKinds: string[]; xLines: number[];
}

export function buildModel(d: Derived, p: DesignParams, system: string): Model {
  const s = sections(p, system);
  const m = p.baysX; // bays → m+1 lines
  const lines = m + 1;
  const hasCore = ["core", "core-outrigger", "dual", "shear-wall", "clt-wall"].includes(system);
  const perFloor = lines + (hasCore ? 1 : 0);
  const nF = p.baysY + 1; // frames lumped into the plane
  const xLines = Array.from({ length: lines }, (_, i) => i * p.spanX);
  const cx = d.Lx / 2;
  const nodes: FNode[] = [];
  for (let j = 0; j <= p.floors; j++) {
    xLines.forEach((x) => nodes.push({ x, y: d.levelZ[j], fix: j === 0 ? [true, true, true] : undefined }));
    if (hasCore) nodes.push({ x: cx, y: d.levelZ[j], fix: j === 0 ? [true, true, true] : undefined });
  }
  const lineNode = (i: number, j: number) => j * perFloor + i;
  const coreNode = (j: number) => j * perFloor + lines;
  const elems: FElem[] = [];
  const momentBeams = ["moment-frame", "dual"].includes(system) || (p.material === "concrete" && system !== "diagrid");
  const momentFrames = system === "moment-frame" || system === "dual" ? nF : p.material === "concrete" ? nF : 0;
  const outriggerFloors = system === "core-outrigger"
    ? [Math.round(p.floors * 0.5), p.floors].filter((v, k, a) => a.indexOf(v) === k && v > 0) : [];
  const leftOfCore = xLines.filter((x) => x < cx - 1e-6).length - 1;
  const rightOfCore = xLines.findIndex((x) => x > cx + 1e-6);
  for (let j = 1; j <= p.floors; j++) {
    const tier = Math.min(2, Math.floor((3 * (j - 1)) / p.floors));
    for (let i = 0; i < lines; i++) {
      elems.push({ i: lineNode(i, j - 1), j: lineNode(i, j), E: s.colE, A: s.colA(tier) * nF, I: s.colI(tier) * nF, kind: "column" });
    }
    if (hasCore) elems.push({ i: coreNode(j - 1), j: coreNode(j), E: s.coreE, A: s.coreA, I: s.coreI, kind: "core" });
    for (let i = 0; i < m; i++) {
      elems.push({
        i: lineNode(i, j), j: lineNode(i + 1, j), E: s.beamE, A: Math.max(s.beamA * nF, 1), I: momentBeams ? s.beamI * Math.max(momentFrames, 1) : 1e-9,
        kind: "beam", pinned: !momentBeams,
      });
    }
    if (hasCore) {
      const isOut = outriggerFloors.includes(j);
      if (leftOfCore >= 0) elems.push(isOut
        ? { i: lineNode(0, j), j: coreNode(j), E: s.Es, A: 0.5, I: s.outriggerI, kind: "outrigger" }
        : { i: lineNode(leftOfCore, j), j: coreNode(j), E: s.Es, A: 5, I: 0, kind: "link", pinned: true });
      if (rightOfCore > 0) elems.push(isOut
        ? { i: coreNode(j), j: lineNode(lines - 1, j), E: s.Es, A: 0.5, I: s.outriggerI, kind: "outrigger" }
        : { i: coreNode(j), j: lineNode(rightOfCore, j), E: s.Es, A: 5, I: 0, kind: "link", pinned: true });
    }
    if (system === "braced-frame") {
      const c = Math.floor((m - 1) / 2);
      const A = s.braceA * 2; // two braced frames
      elems.push({ i: lineNode(c, j - 1), j: lineNode(c + 1, j), E: s.Es, A, I: 0, kind: "brace", pinned: true });
      elems.push({ i: lineNode(c + 1, j - 1), j: lineNode(c, j), E: s.Es, A, I: 0, kind: "brace", pinned: true });
    }
    if (system === "diagrid") {
      for (let i = 0; i < m; i++) {
        const up = (i + j) % 2 === 0;
        elems.push({ i: lineNode(up ? i : i + 1, j - 1), j: lineNode(up ? i + 1 : i, j), E: s.Es, A: s.braceA * 2, I: 0, kind: "brace", pinned: true });
      }
    }
  }
  const frame = new Frame2D(nodes, elems).assemble();
  return { frame, perFloor, lines, coreNode, lineNode, hasCore, nF, elemKinds: elems.map((e) => e.kind), xLines };
}

// ---------------- analyses ----------------
export interface ModalResult { periods: number[]; massRatios: number[]; cumMass: number[]; shapes: number[][]; gammas: number[] }
export interface StoryResult { level: number; z: number; h: number; W: number; F: number; V: number; disp: number; drift: number; driftRatio: number; limit: number; theta: number; thetaMax: number; windDisp?: number; windDriftRatio?: number }

export interface StructuralAnalysis {
  system: SystemInfo; heightLimit: number | null; prescriptive: boolean;
  W: number; Ta: number; CuTa: number; T1: number; Tused: number; Cs: number; Vbase: number; k: number;
  Vrsa: number; rsaScale: number; modal: ModalResult; stories: StoryResult[];
  maxDriftRatio: number; driftLimitRatio: number; maxTheta: number; thetaMax: number;
  torsionRatio: number; torsionClass: string; Ax: number;
  gravity: { colAxialBase: number; colAxialHand: number; colCapacity: number; colUtil: number; punching: null | { vu: number; phiVc: number; util: number }; slabMin: number; beamMidFEA: number; beamStaticFEA: number; beamMidHand: number; sumRy: number; appliedGravity: number };
  equilibrium: { appliedLateral: number; sumRx: number };
  roofDispELF: number; baseMomentCore: number; coreShare: number;
  pushover: Pushover; history: History; sections: { colSize: number; beamDepth: number; coreWall: number };
  stiffness: Matrix; masses: number[];
}

function ctFor(sys: SystemInfo, mat: StructuralMaterial) {
  if (sys.id === "moment-frame") return mat === "concrete" ? { Ct: 0.0466, x: 0.9 } : { Ct: 0.0724, x: 0.8 };
  return { Ct: sys.Ct, x: sys.x };
}
function cuFor(SD1: number) {
  if (SD1 >= 0.4) return 1.4; if (SD1 >= 0.3) return 1.4; if (SD1 >= 0.2) return 1.5; if (SD1 >= 0.15) return 1.6; return 1.7;
}

export function lateralCase(model: Model, forces: number[]): FLoadCase {
  const nodal = new Map<number, [number, number, number]>();
  forces.forEach((F, i) => nodal.set(model.lineNode(0, i + 1), [F, 0, 0]));
  return { name: "lateral", nodal, udl: new Map() };
}

export function floorDisp(model: Model, d: Float64Array, floors: number) {
  return Array.from({ length: floors }, (_, i) => d[model.lineNode(0, i + 1) * 3]);
}

function cqc(values: number[][], omegas: number[], zeta: number) {
  // values[mode][dof]
  const n = values[0].length;
  const out = new Array(n).fill(0);
  for (let a = 0; a < n; a++) {
    let s = 0;
    for (let i = 0; i < values.length; i++) for (let j = 0; j < values.length; j++) {
      const r = omegas[j] / omegas[i];
      const rho = (8 * zeta * zeta * (1 + r) * r ** 1.5) / ((1 - r * r) ** 2 + 4 * zeta * zeta * r * (1 + r) ** 2);
      s += rho * values[i][a] * values[j][a];
    }
    out[a] = Math.sqrt(Math.max(s, 0));
  }
  return out;
}

export function analyse(intake: Intake, d: Derived, p: DesignParams, seis: SeismicParams, systemId: Exclude<LateralSystem, "auto">, opts: { history?: boolean } = {}): StructuralAnalysis & { model: Model } {
  const sys = systemInfo(systemId);
  const model = buildModel(d, p, systemId);
  const loads = floorLoads(intake, d, p, systemId);
  const N = p.floors;
  const Wf = loads.W;
  const W = loads.Wtotal;

  // --- gravity (service D, L) ---
  const gD: FLoadCase = { name: "D", nodal: new Map(), udl: new Map() };
  const gL: FLoadCase = { name: "L", nodal: new Map(), udl: new Map() };
  const elems = model.frame.elems;
  elems.forEach((e, k) => {
    if (e.kind !== "beam") return;
    const j = Math.round(model.frame.nodes[e.i].y * 1000);
    const level = d.levelZ.findIndex((z) => Math.round(z * 1000) === j) - 1;
    const isRoof = level === N - 1;
    gD.udl.set(k, (loads.slabSelf + d.sdl + (isRoof ? 1.2 : d.partition)) * d.Ly);
    gL.udl.set(k, (isRoof ? 1.0 : d.liveLoad) * d.Ly);
  });
  // façade + column + core self weights as nodal loads
  for (let j = 1; j <= N; j++) {
    const h = d.storyHeights[j - 1];
    const fac = (2 * d.Ly + 2 * d.Lx) * h * facadeWeight(p);
    gD.nodal.set(model.lineNode(0, j), [0, -fac / 2, 0]);
    gD.nodal.set(model.lineNode(model.lines - 1, j), [0, -fac / 2, 0]);
    if (model.hasCore) gD.nodal.set(model.coreNode(j), [0, -sections(p, systemId).coreA * h * 24, 0]);
  }
  const rD = model.frame.run(gD), rL = model.frame.run(gL);
  const appliedGravity = sum([...gD.udl.values()].map((w) => w * p.spanX)) + sum([...gL.udl.values()].map((w) => w * p.spanX))
    + sum([...gD.nodal.values()].map((v) => -v[1]));
  let sumRy = 0;
  rD.reactions.forEach((r) => (sumRy += r[1]));
  rL.reactions.forEach((r) => (sumRy += r[1]));
  // interior column (line 1) axial at base, per physical column
  const baseColIdx = elems.findIndex((e) => e.kind === "column" && e.i === model.lineNode(Math.min(1, model.lines - 1), 0));
  const PuLine = 1.2 * Math.abs(rD.forces[baseColIdx].N1) + 1.6 * Math.abs(rL.forces[baseColIdx].N1);
  const interiorCols = Math.max(p.baysY, 1); // edge frames carry half tributary width
  const colAxialBase = Math.abs(PuLine) / interiorCols;
  const tribA = p.spanX * p.spanY;
  const colAxialHand = N * tribA * (1.2 * (loads.slabSelf + d.sdl + d.partition) + 1.6 * d.liveLoad);
  const s = sections(p, systemId);
  const fc = p.concreteGrade * 1000;
  let colCapacity: number;
  if (p.material === "concrete") colCapacity = 0.65 * 0.8 * (0.85 * fc * s.colA(0) * 0.98 + 420000 * s.colA(0) * 0.02); // ACI 318-19 §22.4.2
  else if (p.material === "timber") colCapacity = 0.8 * 24000 * s.colA(0) * 0.7;
  else colCapacity = 0.9 * 345000 * s.colA(0) * 0.85; // AISC 360-22 Ch. E with χ≈0.85
  const colUtil = colAxialHand / colCapacity;
  // punching shear for flat plates — ACI 318-19 §22.6.5.2
  let punching: StructuralAnalysis["gravity"]["punching"] = null;
  if (p.slabSystem === "flat-plate" || p.slabSystem === "post-tensioned") {
    const dEff = p.slabThickness - 0.035;
    const c = s.colSize(2);
    const b0 = 4 * (c + dEff);
    const qu = 1.2 * (loads.slabSelf + d.sdl + d.partition) + 1.6 * d.liveLoad;
    const Vu = qu * (tribA - (c + dEff) ** 2);
    const vu = Vu / (b0 * dEff); // kPa
    const phiVc = 0.75 * 0.33 * Math.sqrt(p.concreteGrade) * 1000 * (p.slabSystem === "post-tensioned" ? 1.25 : 1);
    punching = { vu: round(vu / 1000, 3), phiVc: round(phiVc / 1000, 3), util: round(vu / phiVc, 3) };
  }
  const ln = Math.max(p.spanX, p.spanY) - p.columnSize;
  const slabMin = p.slabSystem === "flat-plate" ? ln / 30 : p.slabSystem === "post-tensioned" ? ln / 45 : p.slabSystem === "beam-slab" ? Math.max(0.125, ln / 36) : p.slabSystem === "clt" ? ln / 30 : 0.13;
  // beam midspan check vs hand calc (interior span, roof-1 floor)
  const midBeam = elems.findIndex((e) => e.kind === "beam" && e.i === model.lineNode(Math.floor(p.baysX / 2) - (p.baysX > 1 ? 1 : 0), Math.max(1, Math.floor(N / 2))));
  const wTot = (gD.udl.get(midBeam) ?? 0) + (gL.udl.get(midBeam) ?? 0);
  const beamMidFEA = Math.abs(rD.forces[midBeam].Mmid + rL.forces[midBeam].Mmid);
  // independent statics: midspan sagging + average hogging = free-span moment wL²/8 for any end fixity
  const beamStaticFEA = Math.abs(rD.forces[midBeam].Mmid + rL.forces[midBeam].Mmid) + (Math.abs(rD.forces[midBeam].M1 + rL.forces[midBeam].M1) + Math.abs(rD.forces[midBeam].M2 + rL.forces[midBeam].M2)) / 2;
  const beamMidHand = (wTot * p.spanX ** 2) / 8;

  // --- lateral stiffness via flexibility (unit loads per floor) ---
  const F = zeros(N, N);
  for (let j = 0; j < N; j++) {
    const unit = new Array(N).fill(0); unit[j] = 1;
    const r = model.frame.run(lateralCase(model, unit));
    const u = floorDisp(model, r.d, N);
    for (let i = 0; i < N; i++) F[i][j] = u[i];
  }
  for (let i = 0; i < N; i++) for (let j = i + 1; j < N; j++) { const a = (F[i][j] + F[j][i]) / 2; F[i][j] = a; F[j][i] = a; }
  const K = invert(F);
  const masses = Wf.map((w) => w / G); // tonnes (kN·s²/m)
  const Mh = masses.map((m) => 1 / Math.sqrt(m));
  const A = K.map((r, i) => r.map((v, j) => v * Mh[i] * Mh[j]));
  const eig = jacobiEigen(A);
  const omegas = eig.values.map((v) => Math.sqrt(Math.max(v, 1e-9)));
  const shapes = eig.vectors.map((v) => v.map((x, i) => x * Mh[i]));
  const totalMass = sum(masses);
  const gammas: number[] = [], massRatios: number[] = [];
  shapes.forEach((ph) => {
    const L = sum(ph.map((x, i) => x * masses[i]));
    const Mn = sum(ph.map((x, i) => x * x * masses[i]));
    gammas.push(L / Mn); massRatios.push((L * L) / Mn / totalMass);
  });
  const periods = omegas.map((w) => (2 * Math.PI) / w);
  const cum: number[] = [];
  massRatios.reduce((acc, v) => { cum.push(acc + v); return acc + v; }, 0);
  const T1 = periods[0];

  // --- ELF (ASCE 7-22 §12.8) ---
  const { Ct, x } = ctFor(sys, p.material);
  const Ta = Ct * d.height ** x;
  const CuTa = cuFor(seis.SD1) * Ta;
  const Tused = Math.min(T1, CuTa);
  const RI = sys.R / d.Ie;
  let Cs = seis.SDS / RI;
  const CsMax = Tused <= seis.TL ? seis.SD1 / (Tused * RI) : (seis.SD1 * seis.TL) / (Tused * Tused * RI);
  Cs = Math.min(Cs, CsMax);
  Cs = Math.max(Cs, 0.044 * seis.SDS * d.Ie, 0.01);
  if (intake.S1 >= 0.6) Cs = Math.max(Cs, (0.5 * intake.S1) / RI);
  const V = Cs * W;
  const k = Tused <= 0.5 ? 1 : Tused >= 2.5 ? 2 : 1 + (Tused - 0.5) / 2;
  const wh = Wf.map((w, i) => w * d.levelZ[i + 1] ** k);
  const Fx = wh.map((v) => (v / sum(wh)) * V);
  const rElf = model.frame.run(lateralCase(model, Fx));
  const uElf = floorDisp(model, rElf.d, N);
  let sumRx = 0; rElf.reactions.forEach((r) => (sumRx += r[0]));
  let coreShare = 0, baseMomentCore = 0;
  if (model.hasCore) {
    const ci = elems.findIndex((e) => e.kind === "core" && e.i === model.coreNode(0));
    coreShare = Math.abs(rElf.forces[ci].V1) / V;
    baseMomentCore = Math.abs(rElf.forces[ci].M1);
  }

  // --- response spectrum (§12.9.1), CQC ---
  const zeta = 0.05;
  const modeDisp: number[][] = [], modeShear: number[][] = [];
  shapes.forEach((ph, n) => {
    const Sa = designSa(periods[n], seis) * G / RI;
    const Sd = Sa / omegas[n] ** 2;
    const u = ph.map((v) => gammas[n] * v * Sd);
    const f = ph.map((v, i) => gammas[n] * v * masses[i] * Sa);
    const shear = f.map((_, i) => sum(f.slice(i)));
    modeDisp.push(u); modeShear.push(shear);
  });
  const uRsa = cqc(modeDisp, omegas, zeta);
  const vRsa = cqc(modeShear, omegas, zeta);
  const Vrsa = vRsa[0];
  const rsaScale = Vrsa < V ? V / Vrsa : 1; // §12.9.1.4.1 scale forces to 100 % ELF
  // drift from RSA displacements (inter-story from modal combination of drifts)
  const modeDrift = modeDisp.map((u) => u.map((v, i) => v - (i > 0 ? u[i - 1] : 0)));
  const driftRsa = cqc(modeDrift, omegas, zeta);
  const limitRatio = d.riskCategory === "IV" ? 0.01 : d.riskCategory === "III" ? 0.015 : 0.02; // Table 12.12-1
  const shearScaled = vRsa.map((v) => v * rsaScale);
  const stories: StoryResult[] = Fx.map((F, i) => {
    const h = d.storyHeights[i];
    const drift = (driftRsa[i] * sys.Cd) / d.Ie;
    const Px = sum(loads.deadPerFloor.slice(i)) + sum(loads.livePerFloor.slice(i)) * 0.5;
    const Vx = Math.max(shearScaled[i], 1e-6);
    const theta = (Px * drift * d.Ie) / (Vx * h * sys.Cd);
    return {
      level: i + 1, z: d.levelZ[i + 1], h, W: Wf[i], F, V: shearScaled[i], disp: (uRsa[i] * sys.Cd) / d.Ie,
      drift, driftRatio: drift / h, limit: limitRatio * h, theta, thetaMax: Math.min(0.5 / sys.Cd, 0.25),
    };
  });
  const maxDriftRatio = Math.max(...stories.map((s) => s.driftRatio));
  const maxTheta = Math.max(...stories.map((s) => s.theta));

  // --- torsion screening: rigid diaphragm, accidental eccentricity 5 % (§12.8.4.2) ---
  const e = 0.05 * d.Ly;
  const rFrames = (d.Ly / 2) * 0.82;
  const rCore = 0.6 * Math.sqrt(p.coreWidth * p.coreDepth);
  const share = model.hasCore ? Math.min(0.95, Math.max(coreShare, 0.4)) : 0;
  const rEff2 = share * rCore ** 2 + (1 - share) * rFrames ** 2 + (model.hasCore ? (p.coreWidth * p.coreDepth) / 3 : 0);
  const torsionRatio = 1 + (e * (d.Ly / 2)) / rEff2;
  const torsionClass = torsionRatio > 1.4 ? "Extreme torsional irregularity (1b)" : torsionRatio > 1.2 ? "Torsional irregularity (1a)" : "Regular";
  const Ax = torsionRatio > 1.2 ? Math.min(3, (torsionRatio / 1.2) ** 2) : 1; // Eq. 12.8-14

  const pushover = runPushover(seis, sys, d, V, uElf[N - 1], shapes[0], gammas[0], massRatios[0], W);
  const history = opts.history === false ? emptyHistory() : runHistory(K, masses, omegas, seis, pushover, d, shapes[0], gammas[0], intake);

  return {
    model, system: sys, heightLimit: heightLimit(sys, seis.sdc), prescriptive: sys.listed && (heightLimit(sys, seis.sdc) === null || d.height <= heightLimit(sys, seis.sdc)!),
    W, Ta, CuTa, T1, Tused, Cs, Vbase: V, k, Vrsa, rsaScale,
    modal: { periods, massRatios, cumMass: cum, shapes, gammas }, stories,
    maxDriftRatio, driftLimitRatio: limitRatio, maxTheta, thetaMax: Math.min(0.5 / sys.Cd, 0.25),
    torsionRatio, torsionClass, Ax,
    gravity: { colAxialBase, colAxialHand, colCapacity, colUtil, punching, slabMin, beamMidFEA, beamStaticFEA, beamMidHand, sumRy, appliedGravity },
    equilibrium: { appliedLateral: V, sumRx: -sumRx },
    roofDispELF: uElf[N - 1], baseMomentCore, coreShare,
    pushover, history, sections: { colSize: p.columnSize, beamDepth: s.beamDepth, coreWall: p.coreWallThickness },
    stiffness: K, masses,
  };
}

// ---------------- capacity-spectrum pushover (simplified, ATC-40 / FEMA 440) ----------------
export interface Pushover { curve: { d: number; V: number }[]; Vy: number; dy: number; du: number; perfPoint: { d: number; V: number; driftRatio: number; beff: number }; level: string; demand: { Sd: number; Sa: number }[]; capacity: { Sd: number; Sa: number }[] }

function runPushover(seis: SeismicParams, sys: SystemInfo, d: Derived, V: number, roofElf: number, phi1: number[], gamma1: number, alpha1: number, W: number): Pushover {
  const K0 = V / Math.max(roofElf, 1e-9);
  const Vy = sys.Omega0 * V * 1.1;
  const dy = Vy / K0;
  const du = dy * sys.mu * 1.4;
  const curve: { d: number; V: number }[] = [];
  for (let i = 0; i <= 40; i++) {
    const dd = (du * i) / 40;
    curve.push({ d: dd, V: dd <= dy ? K0 * dd : Vy + 0.05 * K0 * (dd - dy) });
  }
  const phiRoof = phi1[phi1.length - 1];
  const toAD = (pt: { d: number; V: number }) => ({ Sd: pt.d / (gamma1 * phiRoof), Sa: pt.V / (alpha1 * W) });
  const capacity = curve.map(toAD);
  const ay = toAD({ d: dy, V: Vy }).Sa, dyS = toAD({ d: dy, V: Vy }).Sd;
  const mce = { ...seis, SDS: seis.SMS, SD1: seis.SM1 };
  let dp = dyS * 1.5, beff = sys.damping;
  for (let it = 0; it < 60; it++) {
    const ap = dp <= dyS ? (ay / dyS) * dp : ay + 0.05 * (ay / dyS) * (dp - dyS);
    const mu = Math.max(dp / dyS, 1);
    beff = sys.damping + (mu > 1 ? 0.637 * 0.67 * ((ay * dp - dyS * ap) / (ap * dp)) : 0); // κ = 0.67 (type B)
    beff = Math.min(beff, 0.35);
    const Teff = 2 * Math.PI * Math.sqrt(dp / (ap * G));
    const B = 4 / (5.6 - Math.log(100 * beff)); // FEMA 440 damping coefficient
    const Sa = designSa(Teff, mce) / B;
    const Sd = (Sa * G * Teff ** 2) / (4 * Math.PI ** 2);
    if (Math.abs(Sd - dp) < 1e-5) { dp = Sd; break; }
    dp = 0.5 * dp + 0.5 * Sd;
  }
  const dRoof = dp * gamma1 * phiRoof;
  const Vp = dRoof <= dy ? K0 * dRoof : Vy + 0.05 * K0 * (dRoof - dy);
  const driftRatio = dRoof / d.height;
  const level = driftRatio < 0.01 ? "Immediate Occupancy" : driftRatio < 0.02 ? "Life Safety" : driftRatio < 0.04 ? "Collapse Prevention" : "Beyond Collapse Prevention";
  const B = 4 / (5.6 - Math.log(100 * beff));
  const demand = Array.from({ length: 40 }, (_, i) => {
    const T = 0.05 + i * 0.15;
    const Sa = designSa(T, mce) / B;
    return { Sd: (Sa * G * T * T) / (4 * Math.PI ** 2), Sa };
  });
  return { curve, Vy, dy, du, perfPoint: { d: dRoof, V: Vp, driftRatio, beff }, level, demand, capacity };
}

// ---------------- response history ----------------
export interface History {
  dt: number; pga: number; record: { t: number; a: number }[]; roof: { t: number; u: number }[];
  peakRoof: number; peakDriftRatio: number; peakBaseShearElastic: number;
  nl: { peakDisp: number; ductility: number; residual: number; hysteresis: { d: number; f: number }[] };
}
const emptyHistory = (): History => ({ dt: 0, pga: 0, record: [], roof: [], peakRoof: 0, peakDriftRatio: 0, peakBaseShearElastic: 0, nl: { peakDisp: 0, ductility: 0, residual: 0, hysteresis: [] } });

export function syntheticRecord(seed: number, pgaG: number, duration = 24, dt = 0.01) {
  // Kanai-Tajimi filtered noise with a Jennings envelope, scaled to the target PGA.
  const R = rng(seed);
  const n = Math.round(duration / dt);
  const wg = 2 * Math.PI * 2.5, zg = 0.6;
  let x = 0, v = 0;
  const a: number[] = [];
  for (let i = 0; i < n; i++) {
    const t = i * dt;
    const w = (R() * 2 - 1) * Math.sqrt(3) * 10;
    const acc = w - 2 * zg * wg * v - wg * wg * x;
    v += acc * dt; x += v * dt;
    const env = t < 2 ? (t / 2) ** 2 : t < 10 ? 1 : Math.exp(-0.25 * (t - 10));
    a.push((-2 * zg * wg * v - wg * wg * x) * env);
  }
  const peak = Math.max(...a.map(Math.abs));
  return a.map((v) => (v / peak) * pgaG * G);
}

function runHistory(K: Matrix, m: number[], omegas: number[], seis: SeismicParams, po: Pushover, d: Derived, phi1: number[], _gamma1: number, intake: Intake): History {
  const n = m.length;
  const dt = 0.01;
  const ag = syntheticRecord(Math.round(intake.Ss * 1000 + intake.S1 * 100 + n), seis.pga);
  // Rayleigh damping 5 % at modes 1 and 3 (or last)
  const w1 = omegas[0], w2 = omegas[Math.min(2, n - 1)];
  const z = 0.05;
  const a0 = (2 * z * w1 * w2) / (w1 + w2), a1 = (2 * z) / (w1 + w2);
  const C = K.map((r, i) => r.map((v, j) => a1 * v + (i === j ? a0 * m[i] : 0)));
  // Newmark average acceleration
  const beta = 0.25, gam = 0.5;
  const Keff = K.map((r, i) => r.map((v, j) => v + (gam / (beta * dt)) * C[i][j] + (i === j ? m[i] / (beta * dt * dt) : 0)));
  const Ki = invert(Keff);
  let u = new Array(n).fill(0), v = new Array(n).fill(0), acc = new Array(n).fill(0);
  let peakRoof = 0, peakDrift = 0, peakV = 0;
  const roof: { t: number; u: number }[] = [];
  for (let s = 0; s < ag.length; s++) {
    const p = m.map((mi) => -mi * ag[s]);
    const rhs = p.map((pi, i) => {
      let t = pi;
      for (let j = 0; j < n; j++) {
        t += m[i] * (i === j ? 1 : 0) * (u[j] / (beta * dt * dt) + v[j] / (beta * dt) + (1 / (2 * beta) - 1) * acc[j]);
        t += C[i][j] * ((gam / (beta * dt)) * u[j] + (gam / beta - 1) * v[j] + dt * (gam / (2 * beta) - 1) * acc[j]);
      }
      return t;
    });
    const un = Ki.map((r) => r.reduce((t, k, j) => t + k * rhs[j], 0));
    const an = un.map((x, i) => (x - u[i]) / (beta * dt * dt) - v[i] / (beta * dt) - (1 / (2 * beta) - 1) * acc[i]);
    const vn = v.map((x, i) => x + dt * ((1 - gam) * acc[i] + gam * an[i]));
    u = un; v = vn; acc = an;
    peakRoof = Math.max(peakRoof, Math.abs(u[n - 1]));
    for (let i = 0; i < n; i++) peakDrift = Math.max(peakDrift, Math.abs(u[i] - (i ? u[i - 1] : 0)) / d.storyHeights[i]);
    const Vb = Math.abs(sum(K.map((r) => r.reduce((t, k, j) => t + k * u[j], 0))));
    peakV = Math.max(peakV, Vb);
    if (s % 8 === 0) roof.push({ t: round(s * dt, 2), u: round(u[n - 1] * 1000, 2) });
  }
  // nonlinear equivalent SDOF (bilinear kinematic hardening, backbone from the pushover curve)
  const phiN = phi1.map((v) => v / phi1[n - 1]);
  const mstar = sum(m.map((mi, i) => mi * phiN[i]));
  const Gam = mstar / sum(m.map((mi, i) => mi * phiN[i] ** 2));
  const Dy = po.dy / Gam, Fy = po.Vy / Gam;
  const k0 = Fy / Dy, k2 = 0.05 * k0;
  const wn = Math.sqrt(k0 / mstar);
  const c = 2 * 0.05 * wn * mstar;
  let x = 0, xv = 0, fs = 0, peak = 0;
  const hyst: { d: number; f: number }[] = [];
  const sub = Math.max(4, Math.ceil((dt * wn) / 0.2));
  const h = dt / sub;
  for (let s = 0; s < ag.length; s++) {
    for (let q = 0; q < sub; q++) {
      const xa = (-mstar * ag[s] - c * xv - fs) / mstar;
      xv += xa * h;
      const dx = xv * h;
      x += dx;
      const upper = Fy + k2 * (x - Dy), lower = -Fy + k2 * (x + Dy);
      fs = Math.min(Math.max(fs + k0 * dx, lower), upper);
    }
    peak = Math.max(peak, Math.abs(x));
    if (s % 6 === 0) hyst.push({ d: round(x * Gam * 1000, 2), f: round(fs * Gam, 0) });
  }
  return {
    dt, pga: seis.pga, record: ag.filter((_, i) => i % 8 === 0).map((a, i) => ({ t: round(i * 8 * dt, 2), a: round(a / G, 4) })),
    roof, peakRoof, peakDriftRatio: peakDrift, peakBaseShearElastic: peakV,
    nl: { peakDisp: peak * Gam, ductility: peak / Dy, residual: Math.abs(x) * Gam, hysteresis: hyst },
  };
}

// ---------------- quick quantities per system (used by selection & QTO) ----------------
export function structuralQuantities(d: Derived, p: DesignParams, system: string) {
  const s = sections(p, system);
  const nCols = (p.baysX + 1) * (p.baysY + 1);
  let colVol = 0;
  for (let i = 0; i < p.floors; i++) {
    const tier = Math.min(2, Math.floor((3 * i) / p.floors));
    colVol += nCols * s.colSize(tier) ** 2 * d.storyHeights[i];
  }
  const hasCore = ["core", "core-outrigger", "dual", "shear-wall"].includes(system);
  const coreVol = hasCore ? s.coreA * d.height * (system === "shear-wall" ? 1 : 1) : 0;
  const cltWallVol = system === "clt-wall" ? s.coreA * d.height : 0;
  const slabVolPerFloor = d.plateArea * (p.slabSystem === "composite-deck" ? p.slabThickness * 0.75 : p.slabSystem === "clt" ? 0.06 : p.slabThickness);
  const beamLen = (p.baysX * (p.baysY + 1) * p.spanX + p.baysY * (p.baysX + 1) * p.spanY);
  const slabVol = slabVolPerFloor * (p.floors + p.basementLevels);
  const beamConcrete = p.slabSystem === "beam-slab" ? beamLen * s.beamDepth * Math.max(0.3, s.beamDepth * 0.5) * p.floors : 0;
  const steelMember = (p.material === "steel" || p.material === "composite");
  const steelBeams = p.slabSystem === "composite-deck" ? beamLen * (0.04 * s.beamDepth ** 2) * 7.85 * p.floors : 0; // t
  const steelCols = steelMember ? colVol * 0.25 * 7.85 : 0;
  const braces = system === "braced-frame" ? p.floors * 4 * Math.hypot(p.spanX, p.floorHeight) * s.braceA * 7.85
    : system === "diagrid" ? p.floors * p.baysX * 4 * Math.hypot(p.spanX, p.floorHeight) * s.braceA * 7.85 : 0;
  const outriggers = system === "core-outrigger" ? 2 * 2 * (d.Lx / 2) * 0.08 * 7.85 * 4 : 0;
  const concrete = (p.material === "concrete" ? colVol : 0) + coreVol + (p.slabSystem === "clt" ? 0 : slabVol) + beamConcrete;
  const rebar = ((p.material === "concrete" ? colVol * 220 : 0) + coreVol * 180 + (p.slabSystem === "clt" ? 0 : slabVol) * (p.slabSystem === "post-tensioned" ? 55 : 100) + beamConcrete * 160) / 1000;
  const ptStrand = p.slabSystem === "post-tensioned" ? slabVol * 9 / 1000 : 0;
  const timber = (p.material === "timber" ? colVol + beamLen * 0.4 * s.beamDepth * p.floors * 0.4 : 0) + (p.slabSystem === "clt" ? d.plateArea * p.floors * p.slabThickness : 0) + cltWallVol;
  const formwork = (p.slabSystem === "clt" || p.slabSystem === "composite-deck" ? 0 : d.plateArea * (p.floors + p.basementLevels)) + (p.material === "concrete" ? nCols * 4 * p.columnSize * d.height : 0) + (hasCore ? 4 * (p.coreWidth + p.coreDepth) * d.height : 0);
  const deck = p.slabSystem === "composite-deck" ? d.plateArea * p.floors : 0;
  return {
    concrete: round(concrete, 1), rebar: round(rebar, 1), structuralSteel: round(steelBeams + steelCols + braces + outriggers, 1),
    ptStrand: round(ptStrand, 2), timber: round(timber, 1), formwork: round(formwork, 0), deck: round(deck, 0),
    colVol: round(colVol, 1), coreVol: round(coreVol, 1), slabVol: round(slabVol, 1), beamConcrete: round(beamConcrete, 1),
  };
}
