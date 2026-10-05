// BIM authoring: deterministic element model generated from the design
// parameters and sized engineering outputs, physical + semantic clash
// detection, and IFC4 (ISO 16739) STEP export.

import { hashString, rng, round } from "./linalg";
import type { Derived } from "./site";
import type { BimElement, Box, Clash, DesignParams } from "./types";

export interface BimInputs {
  beamDepth: number; ductDiameter: number; riserDiameter: number; sprinklerMain: number; waterMain: number; ahus: number; ahuSize: number;
  chillers: number; riserAreaRequired: number; ceilingHeight: number; materialLabel: string; facadeLabel: string;
}

export interface BimModel { elements: BimElement[]; levels: { index: number; name: string; z: number }[]; grids: { name: string; axis: "x" | "y"; at: number }[]; bounds: Box }

const gridLetter = (i: number) => String.fromCharCode(65 + i);

export function generateModel(d: Derived, p: DesignParams, inp: BimInputs): BimModel {
  const els: BimElement[] = [];
  let n = 0;
  const add = (e: Omit<BimElement, "id">) => { els.push({ ...e, id: `${e.discipline}-${e.ifc.replace("Ifc", "")}-${(++n).toString(36).toUpperCase().padStart(4, "0")}` }); };
  const cx0 = (d.Lx - p.coreWidth) / 2, cy0 = (d.Ly - p.coreDepth) / 2;
  const inCore = (x: number, y: number) => x > cx0 - 0.01 && x < cx0 + p.coreWidth + 0.01 && y > cy0 - 0.01 && y < cy0 + p.coreDepth + 0.01;
  const levels = d.levelZ.slice(0, -1).map((z, i) => ({ index: i, name: i === 0 ? "Ground" : `Level ${i}`, z }));
  levels.push({ index: p.floors, name: "Roof", z: d.height });
  const grids = [
    ...Array.from({ length: p.baysX + 1 }, (_, i) => ({ name: `${i + 1}`, axis: "x" as const, at: i * p.spanX })),
    ...Array.from({ length: p.baysY + 1 }, (_, j) => ({ name: gridLetter(j), axis: "y" as const, at: j * p.spanY })),
  ];
  const t = p.slabThickness;
  const wallT = p.coreWallThickness;
  const hasBeams = ["beam-slab", "composite-deck", "clt"].includes(p.slabSystem) || p.material !== "concrete";
  const ductArea = Math.PI * inp.ductDiameter ** 2 / 4;
  const ductH = round(Math.min(0.6, Math.sqrt(ductArea / 2.5)), 2); // rectangular main, aspect ≈ 2.5:1
  const ductW = round(ductArea / ductH, 2);
  const ductOffset = 2.5; // m ring offset from core
  for (let j = 0; j < p.floors; j++) {
    const z0 = d.levelZ[j], z1 = d.levelZ[j + 1];
    const h = z1 - z0;
    const tier = Math.min(2, Math.floor((3 * j) / p.floors));
    const cs = Math.max(0.3, p.columnSize * [1, 0.85, 0.7][tier]);
    // columns
    for (let i = 0; i <= p.baysX; i++) for (let k = 0; k <= p.baysY; k++) {
      const x = i * p.spanX, y = k * p.spanY;
      if (inCore(x, y)) continue;
      add({ ifc: "IfcColumn", name: `C ${i + 1}/${gridLetter(k)}`, discipline: "STR", level: j, material: inp.materialLabel, box: { x: x - cs / 2, y: y - cs / 2, z: z0, dx: cs, dy: cs, dz: h - t }, props: { size: `${Math.round(cs * 1000)}×${Math.round(cs * 1000)}` } });
    }
    // slab (top of story)
    add({ ifc: "IfcSlab", name: `Slab L${j + 1}`, discipline: "STR", level: j, material: inp.materialLabel, box: { x: 0, y: 0, z: z1 - t, dx: d.Lx, dy: d.Ly, dz: t }, props: { system: p.slabSystem, thickness: t } });
    // beams along X on each Y gridline
    if (hasBeams) for (let k = 0; k <= p.baysY; k++) for (let i = 0; i < p.baysX; i++) {
      const xm = (i + 0.5) * p.spanX, y = k * p.spanY;
      if (inCore(xm, y)) continue;
      const bw = Math.max(0.3, inp.beamDepth * 0.5);
      add({ ifc: "IfcBeam", name: `B ${gridLetter(k)}/${i + 1}-${i + 2} L${j + 1}`, discipline: "STR", level: j, box: { x: i * p.spanX, y: y - bw / 2, z: z1 - t - inp.beamDepth, dx: p.spanX, dy: bw, dz: inp.beamDepth }, props: { depth: inp.beamDepth } });
    }
    // core walls
    add({ ifc: "IfcWall", name: `Core wall S L${j + 1}`, discipline: "STR", level: j, box: { x: cx0, y: cy0, z: z0, dx: p.coreWidth, dy: wallT, dz: h - t }, props: { lateral: true } });
    add({ ifc: "IfcWall", name: `Core wall N L${j + 1}`, discipline: "STR", level: j, box: { x: cx0, y: cy0 + p.coreDepth - wallT, z: z0, dx: p.coreWidth, dy: wallT, dz: h - t }, props: { lateral: true } });
    add({ ifc: "IfcWall", name: `Core wall W L${j + 1}`, discipline: "STR", level: j, box: { x: cx0, y: cy0, z: z0, dx: wallT, dy: p.coreDepth, dz: h - t }, props: { lateral: true } });
    add({ ifc: "IfcWall", name: `Core wall E L${j + 1}`, discipline: "STR", level: j, box: { x: cx0 + p.coreWidth - wallT, y: cy0, z: z0, dx: wallT, dy: p.coreDepth, dz: h - t }, props: { lateral: true } });
    // façade panels per bay
    for (let i = 0; i < p.baysX; i++) {
      add({ ifc: "IfcPlate", name: `Façade S ${i + 1} L${j + 1}`, discipline: "ARC", level: j, box: { x: i * p.spanX, y: -0.25, z: z0, dx: p.spanX, dy: 0.15, dz: h }, props: { type: inp.facadeLabel, wwr: p.wwr } });
      add({ ifc: "IfcPlate", name: `Façade N ${i + 1} L${j + 1}`, discipline: "ARC", level: j, box: { x: i * p.spanX, y: d.Ly + 0.1, z: z0, dx: p.spanX, dy: 0.15, dz: h }, props: { type: inp.facadeLabel, wwr: p.wwr } });
    }
    for (let k = 0; k < p.baysY; k++) {
      add({ ifc: "IfcPlate", name: `Façade W ${gridLetter(k)} L${j + 1}`, discipline: "ARC", level: j, box: { x: -0.25, y: k * p.spanY, z: z0, dx: 0.15, dy: p.spanY, dz: h }, props: { type: inp.facadeLabel, wwr: p.wwr } });
      add({ ifc: "IfcPlate", name: `Façade E ${gridLetter(k)} L${j + 1}`, discipline: "ARC", level: j, box: { x: d.Lx + 0.1, y: k * p.spanY, z: z0, dx: 0.15, dy: p.spanY, dz: h }, props: { type: inp.facadeLabel, wwr: p.wwr } });
    }
    if (p.lateralSystem === "shear-wall") for (const yy of [0, d.Ly - wallT]) for (const xx of [0, d.Lx - p.spanX]) {
      add({ ifc: "IfcWall", name: `Shear wall ${xx ? "E" : "W"}${yy ? "N" : "S"} L${j + 1}`, discipline: "STR", level: j, box: { x: xx, y: yy, z: z0, dx: p.spanX, dy: wallT, dz: h - t }, props: { lateral: true } });
    }
    // stairs & lifts inside core
    for (let s = 0; s < p.stairCount; s++) add({ ifc: "IfcStair", name: `Stair ${s + 1} L${j + 1}`, discipline: "ARC", level: j, box: { x: cx0 + wallT + 0.2 + s * (p.coreWidth / Math.max(p.stairCount, 1)), y: cy0 + wallT + 0.2, z: z0, dx: Math.min(p.stairWidth * 2 + 0.3, p.coreWidth / Math.max(p.stairCount, 1) - 0.4), dy: Math.min(5.5, p.coreDepth / 2 - 0.4), dz: h - t } });
    if (j === 0) for (let l = 0; l < p.liftCount; l++) add({ ifc: "IfcTransportElement", name: `Lift ${l + 1}`, discipline: "ARC", level: 0, box: { x: cx0 + wallT + 0.3 + (l % 6) * 2.6, y: cy0 + p.coreDepth - wallT - 2.7 - Math.floor(l / 6) * 2.8, z: 0, dx: 2.3, dy: 2.4, dz: d.height } });
    // MEP above ceiling
    const ceil = z0 + inp.ceilingHeight;
    const ductZ = ceil + 0.1;
    const ringX0 = cx0 - ductOffset, ringX1 = cx0 + p.coreWidth + ductOffset, ringY0 = cy0 - ductOffset, ringY1 = cy0 + p.coreDepth + ductOffset;
    const ductBox = (x: number, y: number, dx: number, dy: number): Box => ({ x, y, z: ductZ, dx, dy, dz: ductH });
    const size = `${Math.round(ductW * 1000)}×${Math.round(ductH * 1000)}`;
    add({ ifc: "IfcDuctSegment", name: `SA duct ring W L${j + 1}`, discipline: "MEC", level: j, box: ductBox(ringX0 - ductW / 2, ringY0, ductW, ringY1 - ringY0), props: { size } });
    add({ ifc: "IfcDuctSegment", name: `SA duct ring E L${j + 1}`, discipline: "MEC", level: j, box: ductBox(ringX1 - ductW / 2, ringY0, ductW, ringY1 - ringY0), props: { size } });
    add({ ifc: "IfcDuctSegment", name: `SA duct ring S L${j + 1}`, discipline: "MEC", level: j, box: ductBox(ringX0, ringY0 - ductW / 2, ringX1 - ringX0, ductW), props: { size } });
    add({ ifc: "IfcDuctSegment", name: `SA duct ring N L${j + 1}`, discipline: "MEC", level: j, box: ductBox(ringX0, ringY1 - ductW / 2, ringX1 - ringX0, ductW), props: { size } });
    // branch from riser through core wall
    add({ ifc: "IfcDuctSegment", name: `SA branch from riser L${j + 1}`, discipline: "MEC", level: j, box: ductBox(cx0 - ductOffset, cy0 + p.coreDepth / 2 - ductW / 2, ductOffset + wallT + 0.3, ductW), props: { size, penetratesCore: true } });
    // sprinkler main & valve
    const spZ = ductZ + ductH + 0.05;
    add({ ifc: "IfcPipeSegment", name: `Sprinkler main L${j + 1}`, discipline: "FIR", level: j, box: { x: 0.8, y: cy0 - ductOffset - 1.2, z: spZ, dx: d.Lx - 1.6, dy: inp.sprinklerMain, dz: inp.sprinklerMain }, props: { diameter: inp.sprinklerMain } });
    add({ ifc: "IfcValve", name: `Floor control valve L${j + 1}`, discipline: "FIR", level: j, box: { x: cx0 - 0.6, y: cy0 - ductOffset - 1.25, z: spZ - 0.05, dx: 0.4, dy: 0.3, dz: 0.3 }, props: { accessHeight: round(spZ - z0, 2) } });
    // domestic water + cable tray
    add({ ifc: "IfcPipeSegment", name: `CW branch L${j + 1}`, discipline: "PLB", level: j, box: { x: cx0 + p.coreWidth, y: cy0 + 1, z: ceil + 0.05, dx: ductOffset + 2, dy: inp.waterMain, dz: inp.waterMain } });
    add({ ifc: "IfcCableCarrierSegment", name: `Cable tray L${j + 1}`, discipline: "ELE", level: j, box: { x: cx0 + p.coreWidth + 0.3, y: cy0 + 0.6, z: ceil + 0.02, dx: ductOffset + 1.5, dy: 0.45, dz: 0.1 } });
  }
  // risers & roof plant
  add({ ifc: "IfcDuctSegment", name: "Main supply riser", discipline: "MEC", level: 0, box: { x: cx0 + wallT + 0.05, y: cy0 + p.coreDepth / 2 - inp.riserDiameter / 2, z: 0, dx: inp.riserDiameter, dy: inp.riserDiameter, dz: d.height }, props: { diameter: inp.riserDiameter } });
  const plantW = Math.min(d.Lx * 0.6, inp.ahus * 7), plantD = Math.min(d.Ly * 0.5, 14);
  for (let a = 0; a < inp.ahus; a++) {
    const perRow = Math.max(1, Math.floor(plantW / 7));
    add({ ifc: "IfcUnitaryEquipment", name: `AHU-${a + 1} (${inp.ahuSize} m³/s)`, discipline: "MEC", level: p.floors, box: { x: (d.Lx - plantW) / 2 + (a % perRow) * 6.2, y: (d.Ly - plantD) / 2 + Math.floor(a / perRow) * 4.2, z: d.height, dx: 5.4, dy: 3.4, dz: 2.6 }, props: { airflow: inp.ahuSize } });
  }
  for (let c = 0; c < inp.chillers; c++) add({ ifc: "IfcUnitaryEquipment", name: `CH-${c + 1}`, discipline: "MEC", level: p.basementLevels > 0 ? -1 : p.floors, box: { x: 2 + c * 5, y: 2, z: p.basementLevels > 0 ? -3.5 : d.height, dx: 4.2, dy: 2.0, dz: 2.4 } });
  return { elements: els, levels, grids, bounds: { x: -1, y: -1, z: 0, dx: d.Lx + 2, dy: d.Ly + 2, dz: d.height + 3 } };
}

// ---------------- clash detection ----------------
const overlap = (a: Box, b: Box, tol = 0.01) =>
  a.x < b.x + b.dx - tol && b.x < a.x + a.dx - tol && a.y < b.y + b.dy - tol && b.y < a.y + a.dy - tol && a.z < b.z + b.dz - tol && b.z < a.z + a.dz - tol;

const RULES: [string, string][] = [["MEC", "STR"], ["FIR", "STR"], ["PLB", "STR"], ["ELE", "STR"], ["MEC", "FIR"], ["MEC", "PLB"], ["ELE", "PLB"]];

export function detectClashes(model: BimModel, d: Derived, p: DesignParams, inp: BimInputs): Clash[] {
  const out: Clash[] = [];
  const byLevel = new Map<number, BimElement[]>();
  model.elements.forEach((e) => { if (!byLevel.has(e.level)) byLevel.set(e.level, []); byLevel.get(e.level)!.push(e); });
  const groups = new Map<string, { count: number; level: number; levels: Set<number>; a: BimElement; b: BimElement; depth: number }>();
  byLevel.forEach((els, level) => {
    for (const [da, db] of RULES) {
      const A = els.filter((e) => e.discipline === da), B = els.filter((e) => e.discipline === db);
      for (const a of A) for (const b of B) {
        if (a.props?.penetratesCore && b.ifc === "IfcWall") continue; // handled as a semantic (coordinated) penetration
        if (a.name.includes("riser") && b.ifc === "IfcSlab") continue; // risers pass through coordinated shaft openings
        if (!overlap(a.box, b.box)) continue;
        const depth = Math.min(a.box.z + a.box.dz, b.box.z + b.box.dz) - Math.max(a.box.z, b.box.z);
        const key = `${a.name.replace(/ L\d+$/, "")}|${b.ifc}`;
        const g = groups.get(key);
        if (g) { g.count++; g.levels.add(level); g.depth = Math.max(g.depth, depth); } else groups.set(key, { count: 1, level, levels: new Set([level]), a, b, depth });
      }
    }
  });
  groups.forEach((g, key) => {
    const sev = g.b.ifc === "IfcBeam" || g.b.ifc === "IfcColumn" || g.b.ifc === "IfcWall" ? "critical" : "major";
    out.push({
      key: `phys|${key}`, type: "physical", severity: sev, title: `${g.a.name.replace(/ L\d+$/, "")} × ${g.b.ifc.replace("Ifc", "")}`, a: g.a.name.replace(/ L\d+$/, ""), b: g.b.ifc.replace("Ifc", ""), level: g.level,
      location: `${g.levels.size > 1 ? `${g.levels.size} levels (typical floor)` : `L${g.level + 1}`} · ${g.count} intersection${g.count > 1 ? "s" : ""}`,
      detail: `Hard clash, vertical interpenetration ${Math.round(g.depth * 1000)} mm. ${g.b.ifc === "IfcBeam" ? `Ceiling void ${round(p.floorHeight - inp.ceilingHeight - p.slabThickness, 2)} m cannot fit ${Math.round(inp.beamDepth * 1000)} mm beams + ${g.a.props?.size ?? ""} mm duct — raise floor-to-floor, use flat slab, or reroute below beams.` : "Reroute or re-level one service."}`,
    });
  });
  // ---- semantic rules ----
  const sem = (key: string, severity: Clash["severity"], title: string, a: string, b: string, level: number, location: string, detail: string) =>
    out.push({ key: `sem|${key}`, type: "semantic", severity, title, a, b, level, location, detail });
  const area = Math.PI * inp.ductDiameter ** 2 / 4;
  const dH = Math.min(0.6, Math.sqrt(area / 2.5)), dW = area / dH;
  if (dW > 1.2) sem("core-penetration", "major", "Large penetration through primary lateral element", "SA branch from riser", "Core wall W", 0, "All levels · core west wall",
    `Opening ${Math.round(dW * 1000)}×${Math.round(dH * 1000)} mm exceeds 1200 mm wide in the shear core; needs structural opening design (coupling/pier check, ACI 318-19 §18.10) or split into two ducts.`);
  else sem("core-penetration-damper", "minor", "Fire damper required at rated core penetration", "SA branch from riser", "Core wall W (2 h)", 0, "All levels",
    "Duct crosses 2 h shaft wall — provide fire/smoke damper with access panel (IBC §717.5).");
  const valveH = inp.ceilingHeight + 0.1 + dH + 0.05;
  if (valveH > 3.0) sem("valve-access", "major", "Inaccessible floor control valve", "Floor control valve", "Ceiling grid", 0, "Typical floor",
    `Valve at ${round(valveH, 2)} m above FFL above a ${Math.round(dH * 1000)} mm deep duct — not reachable from a stepladder; relocate to riser cupboard (NFPA 13 §16.9.3).`);
  if (inp.beamDepth > 0.6 && ["beam-slab", "composite-deck"].includes(p.slabSystem)) sem("sprinkler-obstruction", "minor", "Sprinkler obstruction by deep beams", "Sprinkler heads", "Beams", 0, "Typical floor",
    `Beams ${Math.round(inp.beamDepth * 1000)} mm deep create bays requiring heads in each pocket (NFPA 13 §10.2.7 obstruction rules).`);
  const riserArea = (p.coreWidth * p.coreDepth) * 0.06;
  if (riserArea < inp.riserAreaRequired) sem("riser-space", "major", "Insufficient riser space in core", "Mechanical risers", "Core layout", 0, "Core",
    `Required riser area ${round(inp.riserAreaRequired, 1)} m² vs ~${round(riserArea, 1)} m² available — enlarge core or add secondary riser.`);
  const plantW = inp.ahus * 7;
  if (plantW > d.Lx * 0.6) sem("ahu-clearance", "major", "AHU maintenance clearance", "AHUs", "Roof plant enclosure", p.floors, "Roof",
    `${inp.ahus} AHUs need ${plantW} m of plant run but roof zone is ${round(d.Lx * 0.6, 1)} m — coil-pull & filter clearance (1 m) not achievable.`);
  if (p.coreWidth < 14) sem("wet-over-electrical", "minor", "Wet services above electrical room", "CW branch / WCs L2", "Main switch room L1", 0, "Core east",
    "Toilet stack sits above main LV switch room in a compact core — provide drip trays / re-plan (NEC 110.26(E)).");
  const voidH = p.floorHeight - inp.ceilingHeight - p.slabThickness;
  if (voidH < dH + 0.25 && !out.some((c) => c.type === "physical" && c.b.includes("B "))) sem("ceiling-void", "major", "Ceiling void below services zone", "Services zone", "Ceiling", 0, "Typical floor",
    `Void ${round(voidH, 2)} m < duct + sprinklers + tolerance (${round(dH + 0.25, 2)} m).`);
  return out;
}

// ---------------- IFC4 export ----------------
const B64 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_$";
export function ifcGuid(seed: string) {
  const r = rng(hashString(seed));
  const bytes = Array.from({ length: 16 }, () => Math.floor(r() * 256));
  bytes[6] = (bytes[6] & 0x0f) | 0x40; bytes[8] = (bytes[8] & 0x3f) | 0x80;
  let num = 0n;
  for (const b of bytes) num = (num << 8n) | BigInt(b);
  let s = "";
  for (let i = 0; i < 22; i++) { s = B64[Number(num & 63n)] + s; num >>= 6n; }
  return s;
}
const f = (v: number) => { const s = (Math.round(v * 10000) / 10000).toString(); return s.includes(".") || s.includes("e") ? s : `${s}.`; };
const str = (s: string) => `'${s.replace(/\\/g, "\\\\").replace(/'/g, "''").replace(/[^\x20-\x7e]/g, "")}'`;

const IFC_TYPE: Record<string, string> = {
  IfcColumn: ".COLUMN.", IfcBeam: ".BEAM.", IfcSlab: ".FLOOR.", IfcWall: ".SHEAR.", IfcPlate: ".CURTAIN_PANEL.", IfcStair: ".STRAIGHT_RUN_STAIR.",
  IfcTransportElement: ".ELEVATOR.", IfcDuctSegment: ".RIGIDSEGMENT.", IfcPipeSegment: ".RIGIDSEGMENT.", IfcValve: ".ISOLATING.",
  IfcCableCarrierSegment: ".CABLETRAYSEGMENT.", IfcUnitaryEquipment: ".AIRHANDLER.",
};

export function exportIfc(model: BimModel, project: { name: string; code: string; site: string }, timestamp = 0): string {
  const L: string[] = [];
  let id = 0;
  const e = (s: string) => { L.push(`#${++id}=${s};`); return `#${id}`; };
  const oh = (() => {
    const person = e("IFCPERSON($,$,'Chimera',$,$,$,$,$)");
    const org = e("IFCORGANIZATION($,'Chimera AEC',$,$,$)");
    const po = e(`IFCPERSONANDORGANIZATION(${person},${org},$)`);
    const app = e(`IFCAPPLICATION(${org},'0.1','Chimera AEC','CHIMERA-AEC')`);
    return e(`IFCOWNERHISTORY(${po},${app},$,.ADDED.,$,$,$,${Math.floor(timestamp / 1000)})`);
  })();
  const units = e(`IFCUNITASSIGNMENT((${[e("IFCSIUNIT(*,.LENGTHUNIT.,$,.METRE.)"), e("IFCSIUNIT(*,.AREAUNIT.,$,.SQUARE_METRE.)"), e("IFCSIUNIT(*,.VOLUMEUNIT.,$,.CUBIC_METRE.)"), e("IFCSIUNIT(*,.PLANEANGLEUNIT.,$,.RADIAN.)")].join(",")}))`);
  const origin = e("IFCCARTESIANPOINT((0.,0.,0.))");
  const zDir = e("IFCDIRECTION((0.,0.,1.))");
  const xDir = e("IFCDIRECTION((1.,0.,0.))");
  const wcs = e(`IFCAXIS2PLACEMENT3D(${origin},${zDir},${xDir})`);
  const ctx = e(`IFCGEOMETRICREPRESENTATIONCONTEXT($,'Model',3,1.E-05,${wcs},$)`);
  const body = e(`IFCGEOMETRICREPRESENTATIONSUBCONTEXT('Body','Model',*,*,*,*,${ctx},$,.MODEL_VIEW.,$)`);
  const proj = e(`IFCPROJECT('${ifcGuid(project.code + "proj")}',${oh},${str(project.name)},${str(project.code)},$,$,$,(${ctx}),${units})`);
  const place = (rel: string | null, x: number, y: number, z: number) => {
    const pt = e(`IFCCARTESIANPOINT((${f(x)},${f(y)},${f(z)}))`);
    const ax = e(`IFCAXIS2PLACEMENT3D(${pt},$,$)`);
    return e(`IFCLOCALPLACEMENT(${rel ?? "$"},${ax})`);
  };
  const sitePl = place(null, 0, 0, 0);
  const site = e(`IFCSITE('${ifcGuid(project.code + "site")}',${oh},${str(project.site)},$,$,${sitePl},$,$,.ELEMENT.,$,$,$,$,$)`);
  const bldPl = place(sitePl, 0, 0, 0);
  const bld = e(`IFCBUILDING('${ifcGuid(project.code + "bld")}',${oh},${str(project.name)},$,$,${bldPl},$,$,.ELEMENT.,$,$,$)`);
  e(`IFCRELAGGREGATES('${ifcGuid(project.code + "agg1")}',${oh},$,$,${proj},(${site}))`);
  e(`IFCRELAGGREGATES('${ifcGuid(project.code + "agg2")}',${oh},$,$,${site},(${bld}))`);
  const storeyRefs = new Map<number, { ref: string; pl: string; z: number }>();
  const levelSet = [...new Set(model.elements.map((x) => x.level))].sort((a, b) => a - b);
  for (const lv of levelSet) {
    const z = lv < 0 ? -3.5 : model.levels.find((l) => l.index === lv)?.z ?? 0;
    const pl = place(bldPl, 0, 0, z);
    const name = lv < 0 ? "Basement" : model.levels.find((l) => l.index === lv)?.name ?? `Level ${lv}`;
    const ref = e(`IFCBUILDINGSTOREY('${ifcGuid(project.code + "st" + lv)}',${oh},${str(name)},$,$,${pl},$,$,.ELEMENT.,${f(z)})`);
    storeyRefs.set(lv, { ref, pl, z });
  }
  e(`IFCRELAGGREGATES('${ifcGuid(project.code + "agg3")}',${oh},$,$,${bld},(${[...storeyRefs.values()].map((s) => s.ref).join(",")}))`);
  const contained = new Map<number, string[]>();
  const byDisc = new Map<string, string[]>();
  const p2 = e("IFCAXIS2PLACEMENT2D(" + e("IFCCARTESIANPOINT((0.,0.))") + ",$)");
  for (const el of model.elements) {
    const st = storeyRefs.get(el.level)!;
    const b = el.box;
    const pl = place(st.pl, b.x + b.dx / 2, b.y + b.dy / 2, b.z - st.z);
    const prof = e(`IFCRECTANGLEPROFILEDEF(.AREA.,$,${p2},${f(Math.max(b.dx, 0.001))},${f(Math.max(b.dy, 0.001))})`);
    const solid = e(`IFCEXTRUDEDAREASOLID(${prof},${wcs},${zDir},${f(Math.max(b.dz, 0.001))})`);
    const rep = e(`IFCSHAPEREPRESENTATION(${body},'Body','SweptSolid',(${solid}))`);
    const shape = e(`IFCPRODUCTDEFINITIONSHAPE($,$,(${rep}))`);
    const ref = e(`${el.ifc.toUpperCase()}('${ifcGuid(project.code + el.id)}',${oh},${str(el.name)},$,$,${pl},${shape},${str(el.id)},${IFC_TYPE[el.ifc] ?? ".NOTDEFINED."})`);
    if (!contained.has(el.level)) contained.set(el.level, []);
    contained.get(el.level)!.push(ref);
    if (!byDisc.has(el.discipline)) byDisc.set(el.discipline, []);
    byDisc.get(el.discipline)!.push(ref);
  }
  contained.forEach((refs, lv) => e(`IFCRELCONTAINEDINSPATIALSTRUCTURE('${ifcGuid(project.code + "cont" + lv)}',${oh},$,$,(${refs.join(",")}),${storeyRefs.get(lv)!.ref})`));
  byDisc.forEach((refs, disc) => {
    const prop = e(`IFCPROPERTYSINGLEVALUE('Discipline',$,IFCLABEL('${disc}'),$)`);
    const src = e(`IFCPROPERTYSINGLEVALUE('GeneratedBy',$,IFCLABEL('Chimera AEC parametric engine'),$)`);
    const pset = e(`IFCPROPERTYSET('${ifcGuid(project.code + "pset" + disc)}',${oh},'Pset_ChimeraCommon',$,(${prop},${src}))`);
    e(`IFCRELDEFINESBYPROPERTIES('${ifcGuid(project.code + "rdp" + disc)}',${oh},$,$,(${refs.join(",")}),${pset})`);
  });
  const date = new Date(timestamp || Date.UTC(2026, 0, 1)).toISOString().slice(0, 19);
  return [
    "ISO-10303-21;", "HEADER;", "FILE_DESCRIPTION(('ViewDefinition [ReferenceView_V1.2]'),'2;1');",
    `FILE_NAME(${str(project.code + ".ifc")},'${date}',('Chimera AEC'),('Chimera AEC'),'Chimera AEC engine','Chimera AEC','');`,
    "FILE_SCHEMA(('IFC4'));", "ENDSEC;", "DATA;", ...L, "ENDSEC;", "END-ISO-10303-21;", "",
  ].join("\n");
}
