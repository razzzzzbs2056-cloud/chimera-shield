// Shared types for the engineering engine. Everything is SI unless the
// field name says otherwise (m, kN, kPa, MPa, kW, L/s, °C).

export type BuildingType =
  | "office" | "residential" | "hospital" | "school" | "retail"
  | "mixed-use" | "laboratory" | "hotel" | "warehouse";

export type Jurisdiction = "US" | "UK" | "AU" | "NZ" | "SG" | "CA";

export type StructuralMaterial = "concrete" | "steel" | "composite" | "timber";
export type LateralSystem =
  | "auto" | "core" | "core-outrigger" | "moment-frame" | "braced-frame"
  | "shear-wall" | "diagrid" | "dual" | "clt-wall";
export type SlabSystem = "flat-plate" | "post-tensioned" | "beam-slab" | "composite-deck" | "clt";
export type FacadeType = "curtain-wall" | "unitised" | "punched" | "rainscreen";
export type SoilType = "fill" | "clay" | "silt" | "sand" | "gravel" | "rock";
export type HeatingSource = "gas-boiler" | "heat-pump" | "district";

export interface Priorities { cost: number; carbon: number; area: number; daylight: number; speed: number }

export interface Intake {
  buildingType: BuildingType;
  jurisdiction: Jurisdiction;
  city: string;
  siteWidth: number;      // m (X)
  siteDepth: number;      // m (Y)
  budget: number;         // USD
  climateZone: number;    // ASHRAE 1..7
  summerDB: number;       // °C design dry bulb
  winterDB: number;       // °C design dry bulb
  hdd: number;            // heating degree days (18 °C base)
  cdd: number;            // cooling degree days (18 °C base)
  basicWindSpeed: number; // m/s, 3-s gust
  exposure: "B" | "C" | "D";
  Ss: number;             // g, MCER short period
  S1: number;             // g, MCER 1 s
  groundSnow: number;     // kPa
  rainfall: number;       // mm/h design intensity
  annualRainfall: number; // mm/yr
  floodZone: boolean;
  wildfireRisk: "low" | "moderate" | "high";
  ambientNoise: number;   // dB(A) at façade
  parkingSpaces: number;
  targetEUI: number;      // kWh/m²/yr
  targetCarbon: number;   // kgCO2e/m² A1-A5
  certification: string;
  clientGoals: string;
  priorities: Priorities;
  siteLevelDiff: number;  // m between street and ground floor
}

export interface DesignParams {
  floors: number;
  basementLevels: number;
  floorHeight: number;
  groundFloorHeight: number;
  baysX: number;
  baysY: number;
  spanX: number;
  spanY: number;
  coreWidth: number;
  coreDepth: number;
  coreWallThickness: number;
  material: StructuralMaterial;
  lateralSystem: LateralSystem;
  slabSystem: SlabSystem;
  slabThickness: number;
  columnSize: number;
  concreteGrade: number;  // MPa
  wwr: number;            // window-to-wall ratio 0..1
  glazingU: number;       // W/m²K
  wallU: number;
  roofU: number;
  shgc: number;
  facadeType: FacadeType;
  heating: HeatingSource;
  stairCount: number;
  stairWidth: number;     // m clear
  liftCount: number;
  corridorWidth: number;  // m
  sprinklered: boolean;
  ggbsReplacement: number; // 0..0.7 cement replacement
  pvCoverage: number;      // fraction of roof
}

export interface BoreholeLayer {
  top: number; bottom: number; soil: SoilType;
  spt: number; gamma: number; cu?: number; phi?: number; Es: number;
  cc?: number; e0?: number; finesPct?: number;
}
export interface Borehole { id?: string; name: string; x: number; y: number; gwl: number; layers: BoreholeLayer[] }

export interface StandardRef {
  id?: string; code: string; title: string; jurisdiction: string; discipline: string;
  edition: string; year: number; status: "current" | "superseded" | "draft"; supersededBy?: string | null;
}

export type Status = "PASS" | "FAIL" | "WARN" | "INFO";

export interface Finding {
  id: string;
  discipline: string;
  check: string;
  standard: string;
  clause: string;
  requirement: string;
  evidence: string;
  value: number | string | null;
  limit: number | string | null;
  unit?: string;
  status: Status;
  proxy?: boolean;          // clause from a proxy standard (local equivalent not encoded)
}

export interface AgentMessage {
  seq: number; from: string; to: string; kind: "handoff" | "constraint" | "change" | "query" | "result" | "warning";
  content: string; iteration?: number;
}

export interface AgentInfo { id: string; name: string; discipline: string; required: boolean; reason: string; status?: "done" | "skipped" | "warning" }

export interface Box { x: number; y: number; z: number; dx: number; dy: number; dz: number }
export interface BimElement {
  id: string; ifc: string; name: string; discipline: "ARC" | "STR" | "MEC" | "ELE" | "PLB" | "FIR";
  level: number; material?: string; box: Box; props?: Record<string, string | number | boolean>;
}

export interface Clash {
  key: string; type: "physical" | "semantic"; severity: "critical" | "major" | "minor";
  title: string; a: string; b: string; level: number; location: string; detail: string;
}

export interface Series { name: string; data: { x: number; y: number }[] }
