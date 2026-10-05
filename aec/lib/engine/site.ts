import { interp, round } from "./linalg";
import type { BuildingType, DesignParams, Intake } from "./types";

export const G = 9.81;

export interface Derived {
  Lx: number; Ly: number; plateArea: number; height: number; storyHeights: number[]; levelZ: number[];
  gfa: number; gfaAbove: number; nla: number; coreArea: number; perimeter: number; facadeArea: number;
  occupancyGroup: string; riskCategory: "II" | "III" | "IV"; Ie: number;
  occupantsPerFloor: number; occupants: number; highRise: boolean;
  liveLoad: number; liveLoadCorridor: number; sdl: number; partition: number;
}

const OCC: Record<BuildingType, { group: string; olf: number; live: number; risk: "II" | "III" | "IV"; netRatio: number }> = {
  // olf = occupant load factor m²/person (IBC 2024 Table 1004.5 gross/net converted); live in kPa (ASCE 7-22 Table 4.3-1)
  office: { group: "B", olf: 13.9, live: 2.4, risk: "II", netRatio: 0.82 },
  residential: { group: "R-2", olf: 18.6, live: 1.92, risk: "II", netRatio: 0.8 },
  hospital: { group: "I-2", olf: 22.3, live: 2.87, risk: "IV", netRatio: 0.7 },
  school: { group: "E", olf: 4.6, live: 1.92, risk: "III", netRatio: 0.75 },
  retail: { group: "M", olf: 5.6, live: 4.79, risk: "II", netRatio: 0.85 },
  "mixed-use": { group: "B / M / R-2", olf: 12, live: 2.4, risk: "II", netRatio: 0.8 },
  laboratory: { group: "B", olf: 9.3, live: 4.79, risk: "II", netRatio: 0.72 },
  hotel: { group: "R-1", olf: 18.6, live: 1.92, risk: "II", netRatio: 0.78 },
  warehouse: { group: "S-1", olf: 27.9, live: 6.0, risk: "II", netRatio: 0.92 },
};
export const occupancyInfo = (t: BuildingType) => OCC[t];

export function derive(intake: Intake, p: DesignParams): Derived {
  const Lx = p.baysX * p.spanX;
  const Ly = p.baysY * p.spanY;
  const plateArea = Lx * Ly;
  const storyHeights = Array.from({ length: p.floors }, (_, i) => (i === 0 ? p.groundFloorHeight : p.floorHeight));
  const levelZ = [0];
  storyHeights.forEach((h) => levelZ.push(levelZ[levelZ.length - 1] + h));
  const height = levelZ[levelZ.length - 1];
  const coreArea = p.coreWidth * p.coreDepth;
  const gfaAbove = plateArea * p.floors;
  const gfa = gfaAbove + plateArea * p.basementLevels;
  const occ = OCC[intake.buildingType];
  const nla = (plateArea - coreArea) * p.floors * occ.netRatio / 0.88;
  const perimeter = 2 * (Lx + Ly);
  const facadeArea = perimeter * height;
  const occupantsPerFloor = Math.ceil(plateArea / occ.olf);
  let risk = occ.risk;
  if (intake.buildingType === "school" && occupantsPerFloor * p.floors < 250) risk = "II";
  const Ie = risk === "IV" ? 1.5 : risk === "III" ? 1.25 : 1.0;
  return {
    Lx, Ly, plateArea, height, storyHeights, levelZ, gfa, gfaAbove, nla: round(nla, 0), coreArea, perimeter, facadeArea,
    occupancyGroup: occ.group, riskCategory: risk, Ie,
    occupantsPerFloor, occupants: occupantsPerFloor * p.floors,
    highRise: height - p.groundFloorHeight > 22.86, // IBC 202: occupied floor > 75 ft above fire-department access
    liveLoad: occ.live, liveLoadCorridor: 3.83, sdl: 1.5,
    partition: ["office", "laboratory", "mixed-use"].includes(intake.buildingType) ? 0.72 : 0.5,
  };
}

// ---------- seismic site parameters ----------
export type SiteClass = "A" | "B" | "BC" | "C" | "CD" | "D" | "DE" | "E";

const FA_SS = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5];
const FA: Record<string, number[]> = {
  A: [0.8, 0.8, 0.8, 0.8, 0.8, 0.8], B: [0.9, 0.9, 0.9, 0.9, 0.9, 0.9],
  C: [1.3, 1.3, 1.2, 1.2, 1.2, 1.2], D: [1.6, 1.4, 1.2, 1.1, 1.0, 1.0], E: [2.4, 1.7, 1.3, 1.1, 0.9, 0.8],
};
const FV_S1 = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6];
const FV: Record<string, number[]> = {
  A: [0.8, 0.8, 0.8, 0.8, 0.8, 0.8], B: [0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
  C: [1.5, 1.5, 1.5, 1.5, 1.5, 1.4], D: [2.4, 2.2, 2.0, 1.9, 1.8, 1.7], E: [4.2, 3.3, 2.8, 2.4, 2.2, 2.0],
};
function coef(table: Record<string, number[]>, xs: number[], cls: SiteClass, x: number) {
  const mix: Record<string, [string, string]> = { BC: ["B", "C"], CD: ["C", "D"], DE: ["D", "E"] };
  if (mix[cls]) {
    const [a, b] = mix[cls];
    return (interp(x, xs, table[a]) + interp(x, xs, table[b])) / 2;
  }
  return interp(x, xs, table[cls]);
}

export interface SeismicParams {
  siteClass: SiteClass; Fa: number; Fv: number; SMS: number; SM1: number; SDS: number; SD1: number;
  T0: number; Ts: number; TL: number; sdc: "A" | "B" | "C" | "D" | "E" | "F"; pga: number;
}

export function seismicParams(Ss: number, S1: number, siteClass: SiteClass, risk: "II" | "III" | "IV"): SeismicParams {
  const Fa = coef(FA, FA_SS, siteClass, Ss);
  const Fv = coef(FV, FV_S1, siteClass, S1);
  const SMS = Fa * Ss, SM1 = Fv * S1;
  const SDS = (2 / 3) * SMS, SD1 = (2 / 3) * SM1;
  const iv = risk === "IV";
  const bySds = SDS < 0.167 ? 0 : SDS < 0.33 ? 1 : SDS < 0.5 ? 2 : 3;
  const bySd1 = SD1 < 0.067 ? 0 : SD1 < 0.133 ? 1 : SD1 < 0.2 ? 2 : 3;
  let lvl = Math.max(bySds, bySd1);
  if (iv && lvl >= 1 && lvl < 3) lvl += 1;
  let sdc: SeismicParams["sdc"] = (["A", "B", "C", "D"] as const)[lvl];
  if (S1 >= 0.75) sdc = iv ? "F" : "E";
  return {
    siteClass, Fa: round(Fa, 3), Fv: round(Fv, 3), SMS: round(SMS, 3), SM1: round(SM1, 3), SDS: round(SDS, 3), SD1: round(SD1, 3),
    T0: round((0.2 * SD1) / Math.max(SDS, 1e-6), 3), Ts: round(SD1 / Math.max(SDS, 1e-6), 3), TL: 8, sdc, pga: round(0.4 * SDS, 3),
  };
}

/** ASCE 7-22 §11.4.5 two-period design response spectrum, Sa in g. */
export function designSa(T: number, s: SeismicParams): number {
  if (T < s.T0) return s.SDS * (0.4 + (0.6 * T) / Math.max(s.T0, 1e-6));
  if (T <= s.Ts) return s.SDS;
  if (T <= s.TL) return s.SD1 / T;
  return (s.SD1 * s.TL) / (T * T);
}

// ---------- snow (ASCE 7-22 Ch. 7) ----------
export function flatRoofSnow(pg: number, risk: "II" | "III" | "IV", exposure: "B" | "C" | "D") {
  const Is = risk === "IV" ? 1.2 : risk === "III" ? 1.1 : 1.0;
  const Ce = exposure === "B" ? 1.0 : exposure === "C" ? 0.9 : 0.8;
  const Ct = 1.0;
  const pf = 0.7 * Ce * Ct * Is * pg;
  return { Ce, Ct, Is, pf: round(Math.max(pf, pg > 0 ? Math.min(pg, 0.96) * Is : 0), 3) };
}
