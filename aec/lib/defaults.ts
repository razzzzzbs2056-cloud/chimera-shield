// Intake defaults and a parametric scheme generator used when a new project
// is created from the intake form.

import type { BuildingType, DesignParams, Intake, Jurisdiction } from "./engine/types";

export const BUILDING_TYPES: { value: BuildingType; label: string }[] = [
  { value: "office", label: "Office" }, { value: "residential", label: "Residential" }, { value: "hospital", label: "Hospital" },
  { value: "school", label: "School" }, { value: "retail", label: "Retail" }, { value: "mixed-use", label: "Mixed-use" },
  { value: "laboratory", label: "Laboratory" }, { value: "hotel", label: "Hotel" }, { value: "warehouse", label: "Warehouse" },
];

export const CITIES: { city: string; jurisdiction: Jurisdiction; climateZone: number; summerDB: number; winterDB: number; hdd: number; cdd: number; wind: number; Ss: number; S1: number; snow: number; rain: number; annual: number }[] = [
  { city: "San Francisco", jurisdiction: "US", climateZone: 3, summerDB: 28, winterDB: 3, hdd: 1500, cdd: 150, wind: 43, Ss: 1.5, S1: 0.6, snow: 0, rain: 45, annual: 600 },
  { city: "Los Angeles", jurisdiction: "US", climateZone: 3, summerDB: 33, winterDB: 6, hdd: 700, cdd: 700, wind: 43, Ss: 2.0, S1: 0.7, snow: 0, rain: 50, annual: 380 },
  { city: "Seattle", jurisdiction: "US", climateZone: 4, summerDB: 29, winterDB: -4, hdd: 2600, cdd: 100, wind: 43, Ss: 1.4, S1: 0.49, snow: 0.96, rain: 40, annual: 950 },
  { city: "New York", jurisdiction: "US", climateZone: 4, summerDB: 32, winterDB: -9, hdd: 2600, cdd: 650, wind: 49, Ss: 0.28, S1: 0.07, snow: 1.2, rain: 75, annual: 1200 },
  { city: "Boston", jurisdiction: "US", climateZone: 5, summerDB: 31, winterDB: -14, hdd: 3100, cdd: 400, wind: 54, Ss: 0.22, S1: 0.07, snow: 1.9, rain: 70, annual: 1100 },
  { city: "Chicago", jurisdiction: "US", climateZone: 5, summerDB: 33, winterDB: -20, hdd: 3500, cdd: 450, wind: 47, Ss: 0.12, S1: 0.06, snow: 1.2, rain: 85, annual: 940 },
  { city: "Austin", jurisdiction: "US", climateZone: 2, summerDB: 37, winterDB: -2, hdd: 900, cdd: 1650, wind: 47, Ss: 0.08, S1: 0.04, snow: 0.25, rain: 100, annual: 860 },
  { city: "Houston", jurisdiction: "US", climateZone: 2, summerDB: 36, winterDB: 1, hdd: 700, cdd: 1900, wind: 60, Ss: 0.07, S1: 0.04, snow: 0, rain: 120, annual: 1260 },
  { city: "London", jurisdiction: "UK", climateZone: 4, summerDB: 28, winterDB: -3, hdd: 2600, cdd: 60, wind: 36, Ss: 0.05, S1: 0.02, snow: 0.5, rain: 55, annual: 620 },
  { city: "Manchester", jurisdiction: "UK", climateZone: 4, summerDB: 26, winterDB: -4, hdd: 2900, cdd: 20, wind: 38, Ss: 0.05, S1: 0.02, snow: 0.5, rain: 50, annual: 870 },
  { city: "Sydney", jurisdiction: "AU", climateZone: 3, summerDB: 32, winterDB: 6, hdd: 700, cdd: 500, wind: 45, Ss: 0.2, S1: 0.07, snow: 0, rain: 120, annual: 1200 },
  { city: "Melbourne", jurisdiction: "AU", climateZone: 3, summerDB: 35, winterDB: 3, hdd: 1600, cdd: 250, wind: 45, Ss: 0.25, S1: 0.08, snow: 0, rain: 60, annual: 650 },
  { city: "Auckland", jurisdiction: "NZ", climateZone: 3, summerDB: 26, winterDB: 4, hdd: 1100, cdd: 100, wind: 45, Ss: 0.4, S1: 0.15, snow: 0, rain: 70, annual: 1200 },
  { city: "Wellington", jurisdiction: "NZ", climateZone: 4, summerDB: 23, winterDB: 3, hdd: 1800, cdd: 20, wind: 55, Ss: 1.2, S1: 0.45, snow: 0, rain: 60, annual: 1250 },
  { city: "Singapore", jurisdiction: "SG", climateZone: 1, summerDB: 33, winterDB: 23, hdd: 0, cdd: 3400, wind: 33, Ss: 0.05, S1: 0.03, snow: 0, rain: 150, annual: 2400 },
  { city: "Toronto", jurisdiction: "CA", climateZone: 6, summerDB: 31, winterDB: -18, hdd: 3700, cdd: 300, wind: 45, Ss: 0.25, S1: 0.07, snow: 1.9, rain: 70, annual: 830 },
  { city: "Vancouver", jurisdiction: "CA", climateZone: 5, summerDB: 27, winterDB: -6, hdd: 2800, cdd: 50, wind: 42, Ss: 1.1, S1: 0.4, snow: 1.0, rain: 45, annual: 1450 },
];

export function defaultIntake(type: BuildingType, city: string): Intake {
  const c = CITIES.find((x) => x.city === city) ?? CITIES[0];
  const eui: Record<BuildingType, number> = { office: 110, residential: 95, hospital: 380, school: 110, retail: 150, "mixed-use": 120, laboratory: 280, hotel: 160, warehouse: 60 };
  return {
    buildingType: type, jurisdiction: c.jurisdiction, city: c.city, siteWidth: 60, siteDepth: 45, budget: 120_000_000,
    climateZone: c.climateZone, summerDB: c.summerDB, winterDB: c.winterDB, hdd: c.hdd, cdd: c.cdd, basicWindSpeed: c.wind, exposure: "C",
    Ss: c.Ss, S1: c.S1, groundSnow: c.snow, rainfall: c.rain, annualRainfall: c.annual, floodZone: false, wildfireRisk: "low",
    ambientNoise: 65, parkingSpaces: 50, targetEUI: eui[type], targetCarbon: 500, certification: "", clientGoals: "",
    priorities: { cost: 0.8, carbon: 0.7, area: 0.7, daylight: 0.5, speed: 0.5 }, siteLevelDiff: 0.3,
  };
}

/** Parametric scheme from site & brief: fills the site with a regular grid and sizes the core. */
export function defaultParams(intake: Intake, floors: number): DesignParams {
  const res = ["residential", "hotel"].includes(intake.buildingType);
  const span = res ? 7.2 : intake.buildingType === "hospital" || intake.buildingType === "laboratory" ? 9.0 : 8.4;
  const usableW = intake.siteWidth * 0.85, usableD = intake.siteDepth * 0.85;
  const baysX = Math.max(2, Math.round(usableW / span));
  const baysY = Math.max(2, Math.round(usableD / span));
  const plate = baysX * baysY * span * span;
  const lifts = Math.max(2, Math.ceil((plate * floors) / (res ? 9000 : 6000)));
  const coreArea = Math.max(60, plate * (floors > 30 ? 0.18 : 0.13));
  const coreW = Math.round(Math.sqrt(coreArea * 1.4) * 2) / 2, coreD = Math.round((coreArea / coreW) * 2) / 2;
  const fh = intake.buildingType === "laboratory" ? 4.5 : intake.buildingType === "hospital" ? 4.6 : res ? 3.2 : 3.9;
  return {
    floors, basementLevels: floors > 20 ? 2 : floors > 6 ? 1 : 0, floorHeight: fh, groundFloorHeight: Math.max(fh, 5), baysX, baysY, spanX: span, spanY: span,
    coreWidth: Math.min(coreW, baysX * span * 0.5), coreDepth: Math.min(coreD, baysY * span * 0.5), coreWallThickness: floors > 40 ? 0.6 : floors > 20 ? 0.45 : 0.3,
    material: floors <= 12 && intake.priorities.carbon > 0.8 ? "timber" : "concrete", lateralSystem: "auto", slabSystem: floors <= 12 && intake.priorities.carbon > 0.8 ? "clt" : "post-tensioned",
    slabThickness: 0.24, columnSize: Math.min(1.2, Math.max(0.45, 0.35 + floors * 0.018)), concreteGrade: floors > 30 ? 60 : 40,
    wwr: 0.45, glazingU: 1.6, wallU: 0.3, roofU: 0.18, shgc: 0.28, facadeType: floors > 15 ? "unitised" : "curtain-wall",
    heating: "heat-pump", stairCount: 2, stairWidth: 1.2, liftCount: lifts, corridorWidth: intake.buildingType === "hospital" ? 2.44 : 1.5,
    sprinklered: true, ggbsReplacement: 0.3, pvCoverage: 0.5,
  };
}
