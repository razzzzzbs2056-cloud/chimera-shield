// Fire engineering: occupant load, egress capacity, travel distance,
// construction type & fire resistance, sprinklers/standpipes, smoke control
// and a hydraulic (SFPE) evacuation model with an ASET screen.

import { round } from "./linalg";
import type { Derived } from "./site";
import type { DesignParams, Intake } from "./types";

export interface FireResult {
  occupantLoadFloor: number; occupantLoadTotal: number; exitsRequired: number; exitsProvided: number;
  stairWidthRequired: number; stairWidthProvided: number; stairFactor: number; minStairWidth: number;
  travelDistance: number; travelLimit: number; commonPath: number;
  constructionType: string; frr: { element: string; hours: number }[]; maxHeight: number | null; heightOK: boolean;
  sprinklers: { required: boolean; provided: boolean; hazard: string; heads: number; designDensity: number; pumpFlow: number };
  standpipes: boolean; fireServiceLift: boolean; smokeControl: string; compartmentArea: number;
  evacuation: { rset: number; aset: number; movement: number; preMovement: number; detection: number; flowLimited: number; curve: { t: number; remaining: number }[]; phased: number; full: number; strategy: string };
}

const TRAVEL: Record<string, [number, number]> = { // IBC Table 1017.2 (unsprinklered, sprinklered) m
  B: [61, 91], "R-2": [61, 76], "R-1": [61, 76], "I-2": [0, 61], E: [61, 76], M: [61, 76], "S-1": [61, 76], "B / M / R-2": [61, 76],
};

export function fireEngineering(intake: Intake, d: Derived, p: DesignParams): FireResult {
  const olFloor = d.occupantsPerFloor;
  const exitsRequired = olFloor > 1000 ? 4 : olFloor > 500 ? 3 : 2; // IBC §1006.3.3
  const exitsProvided = p.stairCount;
  const hospital = d.occupancyGroup === "I-2";
  const stairFactor = p.sprinklered && !hospital ? 5.1 : 7.6; // mm/occupant (IBC §1005.3.1 & exception)
  const stairWidthRequired = (olFloor * stairFactor) / 1000; // m total
  const minStairWidth = olFloor > 50 ? 1.118 : 0.914; // IBC §1011.2
  const stairWidthProvided = p.stairCount * p.stairWidth;
  // travel distance: farthest corner → nearest stair in core, rectilinear path ×1.1
  const dx = (d.Lx - p.coreWidth) / 2, dy = (d.Ly - p.coreDepth) / 2;
  const travelDistance = (dx + dy) * 1.1 + 6;
  const [tu, ts] = TRAVEL[d.occupancyGroup] ?? [61, 76];
  const travelLimit = p.sprinklered ? ts : tu;
  const commonPath = Math.min(dx, dy) + 3;
  // Construction type (IBC Table 504.3 / 504.4, Table 601)
  const timber = p.material === "timber";
  const H = d.height;
  let constructionType: string;
  let maxHeight: number | null;
  if (timber) {
    if (H <= 25.9 && p.floors <= 9) { constructionType = "IV-C"; maxHeight = 25.9; }
    else if (H <= 54.9 && p.floors <= 12) { constructionType = "IV-B"; maxHeight = 54.9; }
    else { constructionType = "IV-A"; maxHeight = 82.3; }
  } else if (H > 54.9 || p.floors > 12) { constructionType = "I-A"; maxHeight = null; }
  else { constructionType = "I-B"; maxHeight = 54.9; }
  const frrMap: Record<string, number[]> = { "I-A": [3, 2, 2, 1.5], "I-B": [2, 2, 2, 1], "IV-A": [3, 2, 2, 1.5], "IV-B": [2, 2, 2, 1], "IV-C": [2, 2, 2, 1] };
  const h = frrMap[constructionType];
  const frr = [
    { element: "Primary structural frame", hours: h[0] }, { element: "Floor construction", hours: h[2] },
    { element: "Exit stair & shaft enclosures", hours: p.floors >= 4 ? 2 : 1 }, { element: "Roof construction", hours: h[3] },
  ];
  const sprinkRequired = d.highRise || d.occupants > 300 || ["I-2", "R-1", "R-2"].includes(d.occupancyGroup) || timber;
  const hazard = intake.buildingType === "warehouse" ? "Ordinary Hazard Group 2" : intake.buildingType === "retail" || intake.buildingType === "laboratory" ? "Ordinary Hazard Group 1" : "Light Hazard";
  const density = hazard === "Light Hazard" ? 4.1 : hazard === "Ordinary Hazard Group 1" ? 6.1 : 8.1; // mm/min (NFPA 13 Fig. 19.2.3.1.1)
  const heads = Math.ceil((d.plateArea / (hazard === "Light Hazard" ? 20.9 : 12.1)) * (p.floors + p.basementLevels));
  const designArea = hazard === "Light Hazard" ? 139 : 139;
  const pumpFlow = (density * designArea) / 60 + 31.5; // L/s incl. 1900 L/min hose allowance (approx.)
  // Evacuation — SFPE hydraulic model
  const effWidth = Math.max(p.stairWidth - 0.3, 0.3);
  const Fs = 1.01; // persons/s/m effective width (stairs, max specific flow)
  const flowAll = Fs * effWidth * p.stairCount;
  const total = d.occupants;
  const travelDown = (d.height * 1.9) / 0.48; // stair path length ≈ 1.9×height, speed 0.48 m/s along incline
  const flowLimited = total / flowAll;
  const movement = Math.max(flowLimited, travelDown) + travelDistance / 1.2;
  const detection = 60, preMovement = d.occupancyGroup.startsWith("R") ? 300 : hospital ? 600 : 180;
  const fullRset = detection + preMovement + movement;
  const phasedRset = (olFloor * 3) / flowAll + travelDistance / 1.2 + 3 * p.floorHeight * 1.9 / 0.48 + detection + preMovement;
  const rset = d.highRise ? phasedRset : fullRset; // high-rise: phased evacuation of fire floor ±1
  const curve: { t: number; remaining: number }[] = [];
  for (let t = 0; t <= fullRset * 1.05; t += Math.max(15, Math.round(fullRset / 40))) {
    const tm = Math.max(0, t - detection - preMovement);
    curve.push({ t, remaining: Math.max(0, Math.round(total - flowAll * Math.max(0, tm - Math.min(travelDown, 120) * 0.3))) });
  }
  // ASET: smoke layer descent in a sprinklered/unsprinklered compartment (Zukoski filling, t² fast fire, capped by sprinkler control)
  const roomA = d.plateArea * 0.5, ceil = p.floorHeight - p.slabThickness - 0.6;
  const alpha = 0.047; // kW/s² fast
  const Q = (t: number) => Math.min(alpha * t * t, p.sprinklered ? 1500 : 5000);
  let z = ceil, t = 0;
  while (z > 1.8 && t < 3600) {
    const qc = 0.7 * Q(t); // convective HRR
    const mPlume = 0.071 * Math.max(qc, 1) ** (1 / 3) * z ** (5 / 3) + 0.0018 * qc; // Heskestad plume, kg/s
    z -= mPlume / (1.0 * roomA); // smoke density ≈ 1.0 kg/m³
    t += 1;
  }
  const aset = p.sprinklered ? Math.max(t, 1200) : t;
  return {
    occupantLoadFloor: olFloor, occupantLoadTotal: total, exitsRequired, exitsProvided,
    stairWidthRequired: round(stairWidthRequired, 2), stairWidthProvided: round(stairWidthProvided, 2), stairFactor, minStairWidth,
    travelDistance: round(travelDistance, 1), travelLimit, commonPath: round(commonPath, 1),
    constructionType, frr, maxHeight, heightOK: maxHeight === null || H <= maxHeight,
    sprinklers: { required: sprinkRequired, provided: p.sprinklered, hazard, heads, designDensity: density, pumpFlow: round(pumpFlow, 1) },
    standpipes: H > 9.1, fireServiceLift: H > 36.6, // IBC §905.3.1, §3007.1 (120 ft)
    smokeControl: d.highRise ? "Stair pressurisation + smoke venting (IBC §909, §403.4.7)" : "Natural smoke venting",
    compartmentArea: round(d.plateArea, 0),
    evacuation: { rset: round(rset, 0), aset: round(aset, 0), movement: round(movement, 0), preMovement, detection, flowLimited: round(flowLimited, 0), curve, phased: round(phasedRset, 0), full: round(fullRset, 0), strategy: d.highRise ? "Phased (fire floor ± 1)" : "Simultaneous" },
  };
}
