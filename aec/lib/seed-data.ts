// Realistic demo data: six projects across jurisdictions, borehole logs,
// a versioned standards library and operational assets.

import type { Borehole, DesignParams, Intake, StandardRef } from "./engine/types";

export interface SeedProject {
  name: string; code: string; client: string; stage: string; status: string; address: string; description: string;
  intake: Intake; params: DesignParams; boreholes: Borehole[]; pins: Record<string, string>;
  assets?: { name: string; system: string; type: string; installDate: string; condition: number; runtimeHours: number; criticality: number; location: string }[];
  rfis?: { title: string; detail: string; severity: "critical" | "major" | "minor"; discipline: string; status: string }[];
}

const pr = (cost: number, carbon: number, area: number, daylight: number, speed: number) => ({ cost, carbon, area, daylight, speed });

const baseParams: DesignParams = {
  floors: 10, basementLevels: 1, floorHeight: 3.9, groundFloorHeight: 5.0, baysX: 5, baysY: 4, spanX: 8.4, spanY: 8.4,
  coreWidth: 14, coreDepth: 10, coreWallThickness: 0.4, material: "concrete", lateralSystem: "auto", slabSystem: "post-tensioned",
  slabThickness: 0.25, columnSize: 0.7, concreteGrade: 50, wwr: 0.5, glazingU: 1.6, wallU: 0.3, roofU: 0.18, shgc: 0.28,
  facadeType: "unitised", heating: "heat-pump", stairCount: 2, stairWidth: 1.2, liftCount: 4, corridorWidth: 1.5, sprinklered: true,
  ggbsReplacement: 0.3, pvCoverage: 0.5,
};

export const SEED_PROJECTS: SeedProject[] = [
  {
    name: "Harbourview Tower", code: "HVT-2026", client: "Bayline Developments", stage: "Design Development", status: "active",
    address: "201 Embarcadero, San Francisco, CA", description: "32-storey Grade-A office tower on reclaimed land with two basement levels and a public plaza. Targeting LEED Platinum and net-zero operational carbon by 2030.",
    intake: {
      buildingType: "office", jurisdiction: "US", city: "San Francisco", siteWidth: 70, siteDepth: 55, budget: 395_000_000, climateZone: 3,
      summerDB: 28, winterDB: 3, hdd: 1500, cdd: 150, basicWindSpeed: 43, exposure: "C", Ss: 1.5, S1: 0.6, groundSnow: 0, rainfall: 45, annualRainfall: 600,
      floodZone: true, wildfireRisk: "moderate", ambientNoise: 72, parkingSpaces: 120, targetEUI: 95, targetCarbon: 550, certification: "LEED v5 Platinum",
      clientGoals: "Column-free 13.5 m lease depth, flexible floors for lab conversion on L3–L8, visible timber in lobby, net-zero ready.",
      priorities: pr(0.8, 1.0, 0.9, 0.6, 0.5), siteLevelDiff: 0.6,
    },
    params: { ...baseParams, floors: 32, basementLevels: 2, floorHeight: 4.0, groundFloorHeight: 6.0, baysX: 6, baysY: 4, spanX: 9.0, spanY: 9.0, coreWidth: 20, coreDepth: 13, coreWallThickness: 0.5, columnSize: 0.9, concreteGrade: 60, slabThickness: 0.25, stairCount: 2, stairWidth: 1.4, liftCount: 10, lateralSystem: "core", ggbsReplacement: 0.4, wwr: 0.55, glazingU: 1.5, shgc: 0.25, wallU: 0.33 },
    boreholes: [
      { name: "BH-01", x: 5, y: 5, gwl: 2.5, layers: [
        { top: 0, bottom: 4, soil: "fill", spt: 8, gamma: 18, phi: 28, Es: 10, finesPct: 15 },
        { top: 4, bottom: 9, soil: "sand", spt: 12, gamma: 19, phi: 31, Es: 20, finesPct: 8 },
        { top: 9, bottom: 22, soil: "clay", spt: 6, gamma: 17, cu: 45, Es: 8, cc: 0.45, e0: 1.4 },
        { top: 22, bottom: 34, soil: "sand", spt: 45, gamma: 20, phi: 38, Es: 90, finesPct: 6 },
        { top: 34, bottom: 60, soil: "rock", spt: 100, gamma: 23, Es: 1500 },
      ] },
      { name: "BH-02", x: 50, y: 30, gwl: 2.8, layers: [
        { top: 0, bottom: 3, soil: "fill", spt: 10, gamma: 18, phi: 29, Es: 12, finesPct: 18 },
        { top: 3, bottom: 8, soil: "sand", spt: 14, gamma: 19, phi: 32, Es: 22, finesPct: 10 },
        { top: 8, bottom: 20, soil: "clay", spt: 7, gamma: 17, cu: 50, Es: 9, cc: 0.4, e0: 1.3 },
        { top: 20, bottom: 36, soil: "sand", spt: 50, gamma: 20, phi: 39, Es: 100, finesPct: 5 },
        { top: 36, bottom: 60, soil: "rock", spt: 100, gamma: 23, Es: 1800 },
      ] },
      { name: "CPT-03", x: 28, y: 48, gwl: 2.6, layers: [
        { top: 0, bottom: 4, soil: "fill", spt: 7, gamma: 18, phi: 28, Es: 9, finesPct: 20 },
        { top: 4, bottom: 10, soil: "silt", spt: 9, gamma: 18, phi: 29, Es: 14, finesPct: 40 },
        { top: 10, bottom: 21, soil: "clay", spt: 6, gamma: 17, cu: 42, Es: 8, cc: 0.48, e0: 1.45 },
        { top: 21, bottom: 40, soil: "sand", spt: 42, gamma: 20, phi: 37, Es: 85, finesPct: 7 },
      ] },
    ],
    pins: {},
    rfis: [
      { title: "Confirm plaza transfer at grid C/4", detail: "Architect requests removal of column C/4 at ground for plaza entrance — structural transfer feasibility?", severity: "major", discipline: "Structural", status: "open" },
      { title: "Lab-ready floors L3–L8: vibration criterion", detail: "Client needs VC-A on L3–L8. Check PT slab footfall response at 9 m spans.", severity: "minor", discipline: "Structural", status: "in-review" },
    ],
  },
  {
    name: "Riverside Medical Pavilion", code: "RMP-2025", client: "Cascade Health System", stage: "Construction Documents", status: "active",
    address: "1400 Riverside Ave, Seattle, WA", description: "8-storey acute-care pavilion (Risk Category IV) with surgical suites, 180 inpatient beds and a rooftop helipad. Essential facility with 96-hour self-sufficiency.",
    intake: {
      buildingType: "hospital", jurisdiction: "US", city: "Seattle", siteWidth: 90, siteDepth: 70, budget: 178_000_000, climateZone: 4,
      summerDB: 29, winterDB: -4, hdd: 2600, cdd: 100, basicWindSpeed: 47, exposure: "B", Ss: 1.4, S1: 0.49, groundSnow: 0.96, rainfall: 40, annualRainfall: 950,
      floodZone: false, wildfireRisk: "moderate", ambientNoise: 68, parkingSpaces: 300, targetEUI: 420, targetCarbon: 650, certification: "LEED Gold",
      clientGoals: "Remain operational after design earthquake; 96 h utility independence; flexible OR floor; infection-control airflow cascades.",
      priorities: pr(0.6, 0.6, 0.5, 0.4, 0.8), siteLevelDiff: 1.2,
    },
    params: { ...baseParams, floors: 8, basementLevels: 1, floorHeight: 4.8, groundFloorHeight: 5.5, baysX: 7, baysY: 5, spanX: 9.0, spanY: 8.4, coreWidth: 16, coreDepth: 12, material: "composite", lateralSystem: "braced-frame", slabSystem: "composite-deck", slabThickness: 0.16, columnSize: 0.45, stairCount: 3, stairWidth: 1.4, liftCount: 8, corridorWidth: 2.44, wwr: 0.38, glazingU: 1.7, shgc: 0.3, wallU: 0.3, facadeType: "curtain-wall", heating: "district", ggbsReplacement: 0.3, pvCoverage: 0.3 },
    boreholes: [
      { name: "BH-A", x: 10, y: 10, gwl: 8, layers: [
        { top: 0, bottom: 3, soil: "fill", spt: 12, gamma: 18, phi: 30, Es: 15 },
        { top: 3, bottom: 15, soil: "sand", spt: 28, gamma: 19.5, phi: 35, Es: 45, finesPct: 12 },
        { top: 15, bottom: 40, soil: "gravel", spt: 55, gamma: 21, phi: 40, Es: 120 },
      ] },
      { name: "BH-B", x: 60, y: 40, gwl: 7.5, layers: [
        { top: 0, bottom: 2.5, soil: "fill", spt: 10, gamma: 18, phi: 29, Es: 12 },
        { top: 2.5, bottom: 14, soil: "sand", spt: 30, gamma: 19.5, phi: 35, Es: 50, finesPct: 10 },
        { top: 14, bottom: 40, soil: "gravel", spt: 60, gamma: 21, phi: 41, Es: 130 },
      ] },
    ],
    pins: { "ASCE 7": "7-16", IBC: "2021" },
    rfis: [
      { title: "Helipad dynamic load on composite deck", detail: "Confirm 1.5× impact factor for H-60 class helicopter and deck reinforcement.", severity: "major", discipline: "Structural", status: "open" },
      { title: "OR suite pressure cascade", detail: "Positive pressure 2.5 Pa ORs vs corridor; confirm AHU-3 capacity after VE.", severity: "minor", discipline: "Mechanical", status: "resolved" },
    ],
  },
  {
    name: "Elm Street Timber Residences", code: "ESR-2026", client: "Greenleaf Housing Trust", stage: "Concept", status: "active",
    address: "88 Elm Street, Austin, TX", description: "12-storey mass-timber residential building (Type IV-B) with ground-floor retail, 140 apartments and a podium garden. Embodied-carbon-led design.",
    intake: {
      buildingType: "residential", jurisdiction: "US", city: "Austin", siteWidth: 50, siteDepth: 40, budget: 47_500_000, climateZone: 2,
      summerDB: 37, winterDB: -2, hdd: 900, cdd: 1650, basicWindSpeed: 47, exposure: "B", Ss: 0.08, S1: 0.04, groundSnow: 0.25, rainfall: 100, annualRainfall: 860,
      floodZone: false, wildfireRisk: "low", ambientNoise: 66, parkingSpaces: 60, targetEUI: 85, targetCarbon: 300, certification: "LEED Gold / ILFI Zero Carbon",
      clientGoals: "Lowest embodied carbon; expose timber in units; 40 % affordable units; fast erection to cut financing costs.",
      priorities: pr(0.7, 1.0, 0.6, 0.6, 0.9), siteLevelDiff: 0.45,
    },
    params: { ...baseParams, floors: 12, basementLevels: 0, floorHeight: 3.3, groundFloorHeight: 4.5, baysX: 6, baysY: 3, spanX: 6.0, spanY: 6.6, coreWidth: 11, coreDepth: 8, coreWallThickness: 0.3, material: "timber", lateralSystem: "core", slabSystem: "clt", slabThickness: 0.2, columnSize: 0.5, concreteGrade: 40, wwr: 0.4, glazingU: 1.8, shgc: 0.25, wallU: 0.35, facadeType: "rainscreen", stairCount: 2, stairWidth: 1.2, liftCount: 3, ggbsReplacement: 0.5, pvCoverage: 0.6 },
    boreholes: [
      { name: "BH-1", x: 8, y: 8, gwl: 12, layers: [
        { top: 0, bottom: 2, soil: "fill", spt: 9, gamma: 18, phi: 28, Es: 10 },
        { top: 2, bottom: 9, soil: "clay", spt: 18, gamma: 19, cu: 110, Es: 25, cc: 0.18, e0: 0.7 },
        { top: 9, bottom: 30, soil: "rock", spt: 100, gamma: 22, Es: 800 },
      ] },
    ],
    pins: {},
  },
  {
    name: "Canary Wharf Life Sciences", code: "CWL-2026", client: "Thames Science Partners", stage: "Scheme Design", status: "active",
    address: "15 Bank Street, London E14", description: "14-storey speculative lab-enabled building with 4.5 m floor-to-floor, roof plant for 100 % fresh-air labs and a single basement for logistics.",
    intake: {
      buildingType: "laboratory", jurisdiction: "UK", city: "London", siteWidth: 60, siteDepth: 45, budget: 215_000_000, climateZone: 4,
      summerDB: 28, winterDB: -3, hdd: 2600, cdd: 60, basicWindSpeed: 36, exposure: "B", Ss: 0.05, S1: 0.02, groundSnow: 0.5, rainfall: 55, annualRainfall: 620,
      floodZone: true, wildfireRisk: "low", ambientNoise: 64, parkingSpaces: 20, targetEUI: 280, targetCarbon: 600, certification: "BREEAM Outstanding",
      clientGoals: "Lab floors to VC-A, 50/50 lab-office split, 3.0 kPa live load, flexible risers, flood-resilient plant.",
      priorities: pr(0.7, 0.8, 0.7, 0.5, 0.6), siteLevelDiff: 0.3,
    },
    params: { ...baseParams, floors: 14, basementLevels: 1, floorHeight: 4.5, groundFloorHeight: 6.0, baysX: 6, baysY: 4, spanX: 9.0, spanY: 7.5, coreWidth: 15, coreDepth: 11, material: "composite", lateralSystem: "core", slabSystem: "composite-deck", slabThickness: 0.15, columnSize: 0.5, wwr: 0.45, glazingU: 1.4, shgc: 0.3, wallU: 0.26, facadeType: "unitised", stairCount: 2, stairWidth: 1.3, liftCount: 6, heating: "heat-pump" },
    boreholes: [
      { name: "WS-101", x: 10, y: 10, gwl: 4.5, layers: [
        { top: 0, bottom: 3, soil: "fill", spt: 8, gamma: 18, phi: 28, Es: 10 },
        { top: 3, bottom: 7, soil: "gravel", spt: 32, gamma: 20, phi: 36, Es: 60 },
        { top: 7, bottom: 45, soil: "clay", spt: 30, gamma: 20, cu: 150, Es: 60, cc: 0.15, e0: 0.65 },
      ] },
      { name: "WS-102", x: 50, y: 35, gwl: 4.2, layers: [
        { top: 0, bottom: 3.5, soil: "fill", spt: 9, gamma: 18, phi: 28, Es: 10 },
        { top: 3.5, bottom: 8, soil: "gravel", spt: 35, gamma: 20, phi: 37, Es: 65 },
        { top: 8, bottom: 45, soil: "clay", spt: 32, gamma: 20, cu: 160, Es: 65, cc: 0.14, e0: 0.62 },
      ] },
    ],
    pins: {},
  },
  {
    name: "Southbank Residences", code: "SBR-2027", client: "Yarra Living Group", stage: "Feasibility", status: "active",
    address: "120 City Road, Southbank VIC", description: "45-storey residential tower with 420 apartments, sky lounge and 4-level podium. Slender 1:7 aspect ratio drives wind comfort design.",
    intake: {
      buildingType: "residential", jurisdiction: "AU", city: "Melbourne", siteWidth: 45, siteDepth: 40, budget: 300_000_000, climateZone: 3,
      summerDB: 35, winterDB: 3, hdd: 1600, cdd: 250, basicWindSpeed: 45, exposure: "C", Ss: 0.25, S1: 0.08, groundSnow: 0, rainfall: 60, annualRainfall: 650,
      floodZone: false, wildfireRisk: "low", ambientNoise: 70, parkingSpaces: 180, targetEUI: 90, targetCarbon: 500, certification: "Green Star 6",
      clientGoals: "Maximise saleable area; occupant comfort at upper levels; 7-star NatHERS apartments.",
      priorities: pr(1.0, 0.5, 1.0, 0.6, 0.6), siteLevelDiff: 0.2,
    },
    params: { ...baseParams, floors: 45, basementLevels: 3, floorHeight: 3.15, groundFloorHeight: 5.5, baysX: 5, baysY: 4, spanX: 7.8, spanY: 7.8, coreWidth: 15, coreDepth: 11, coreWallThickness: 0.45, material: "concrete", lateralSystem: "core-outrigger", slabSystem: "post-tensioned", slabThickness: 0.22, columnSize: 0.85, concreteGrade: 65, wwr: 0.5, glazingU: 2.0, shgc: 0.3, wallU: 0.35, facadeType: "unitised", stairCount: 2, stairWidth: 1.2, liftCount: 6, heating: "heat-pump" },
    boreholes: [
      { name: "BH-S1", x: 6, y: 6, gwl: 3.0, layers: [
        { top: 0, bottom: 2, soil: "fill", spt: 6, gamma: 18, phi: 27, Es: 8 },
        { top: 2, bottom: 14, soil: "clay", spt: 4, gamma: 16.5, cu: 25, Es: 5, cc: 0.6, e0: 1.8 },
        { top: 14, bottom: 22, soil: "sand", spt: 30, gamma: 19.5, phi: 35, Es: 50 },
        { top: 22, bottom: 60, soil: "rock", spt: 100, gamma: 23, Es: 1200 },
      ] },
    ],
    pins: {},
  },
  {
    name: "Lakeside Primary School", code: "LPS-2023", client: "Chicago Public Schools", stage: "Operations", status: "completed",
    address: "4500 N Lake Shore Dr, Chicago, IL", description: "3-storey 640-pupil primary school completed in 2023. Now in operation with BMS-connected digital twin and predictive maintenance programme.",
    intake: {
      buildingType: "school", jurisdiction: "US", city: "Chicago", siteWidth: 110, siteDepth: 70, budget: 38_500_000, climateZone: 5,
      summerDB: 33, winterDB: -20, hdd: 3500, cdd: 450, basicWindSpeed: 47, exposure: "C", Ss: 0.12, S1: 0.06, groundSnow: 1.2, rainfall: 85, annualRainfall: 940,
      floodZone: false, wildfireRisk: "low", ambientNoise: 60, parkingSpaces: 40, targetEUI: 110, targetCarbon: 450, certification: "LEED Gold",
      clientGoals: "Low operating cost, robust plant, daylit classrooms, community use after hours.",
      priorities: pr(1.0, 0.6, 0.5, 1.0, 0.5), siteLevelDiff: 0.9,
    },
    params: { ...baseParams, floors: 3, basementLevels: 0, floorHeight: 4.2, groundFloorHeight: 4.5, baysX: 10, baysY: 4, spanX: 8.4, spanY: 7.2, coreWidth: 12, coreDepth: 9, coreWallThickness: 0.3, material: "concrete", lateralSystem: "shear-wall", slabSystem: "beam-slab", slabThickness: 0.2, columnSize: 0.5, concreteGrade: 35, wwr: 0.35, glazingU: 1.7, shgc: 0.35, wallU: 0.28, roofU: 0.16, facadeType: "punched", heating: "gas-boiler", stairCount: 3, stairWidth: 1.5, liftCount: 2, corridorWidth: 2.4, pvCoverage: 0.7 },
    boreholes: [
      { name: "B-1", x: 10, y: 10, gwl: 3.5, layers: [
        { top: 0, bottom: 1.5, soil: "fill", spt: 8, gamma: 18, phi: 28, Es: 10 },
        { top: 1.5, bottom: 12, soil: "clay", spt: 12, gamma: 19, cu: 75, Es: 18, cc: 0.22, e0: 0.8 },
        { top: 12, bottom: 30, soil: "clay", spt: 30, gamma: 20, cu: 180, Es: 70, cc: 0.12, e0: 0.55 },
      ] },
    ],
    pins: {},
    assets: [
      { name: "Chiller CH-1", system: "HVAC", type: "chiller", installDate: "2023-03-14", condition: 4, runtimeHours: 9800, criticality: 0.8, location: "Roof plant" },
      { name: "Chiller CH-2", system: "HVAC", type: "chiller", installDate: "2023-03-14", condition: 3, runtimeHours: 13400, criticality: 0.8, location: "Roof plant" },
      { name: "AHU-1 Classrooms North", system: "HVAC", type: "ahu", installDate: "2023-02-20", condition: 4, runtimeHours: 11200, criticality: 0.7, location: "Roof plant" },
      { name: "AHU-2 Gymnasium", system: "HVAC", type: "ahu", installDate: "2023-02-20", condition: 2, runtimeHours: 16800, criticality: 0.6, location: "Roof plant" },
      { name: "Heating hot-water pump P-3", system: "Hydraulics", type: "pump", installDate: "2023-01-30", condition: 2, runtimeHours: 21000, criticality: 0.9, location: "Boiler room" },
      { name: "Domestic booster set", system: "Hydraulics", type: "pump", installDate: "2023-01-30", condition: 4, runtimeHours: 8000, criticality: 0.7, location: "Ground plant" },
      { name: "Condensing boiler B-1", system: "HVAC", type: "boiler", installDate: "2023-01-25", condition: 3, runtimeHours: 9000, criticality: 0.8, location: "Boiler room" },
      { name: "Passenger lift L1", system: "Vertical transport", type: "lift", installDate: "2023-04-02", condition: 3, runtimeHours: 7000, criticality: 0.6, location: "Core" },
      { name: "Transformer TX-1", system: "Electrical", type: "transformer", installDate: "2022-12-10", condition: 5, runtimeHours: 32000, criticality: 1.0, location: "Substation" },
      { name: "Standby generator G-1", system: "Electrical", type: "generator", installDate: "2023-01-12", condition: 4, runtimeHours: 210, criticality: 0.9, location: "Generator enclosure" },
      { name: "South curtain wall sealant", system: "Façade", type: "facade", installDate: "2022-11-01", condition: 4, runtimeHours: 30000, criticality: 0.4, location: "South elevation" },
      { name: "Gym roof long-span truss (SHM)", system: "Structure", type: "structure", installDate: "2022-09-01", condition: 5, runtimeHours: 35000, criticality: 1.0, location: "Gymnasium" },
    ],
  },
];

const S = (code: string, title: string, jurisdiction: string, discipline: string, edition: string, year: number, status: StandardRef["status"], supersededBy: string | null = null): StandardRef => ({ code, title, jurisdiction, discipline, edition, year, status, supersededBy });

export const SEED_STANDARDS: StandardRef[] = [
  S("IBC", "International Building Code", "US", "General", "2024", 2024, "current"), S("IBC", "International Building Code", "US", "General", "2021", 2021, "superseded", "2024"),
  S("ASCE 7", "Minimum Design Loads and Associated Criteria for Buildings and Other Structures", "US", "Structural", "7-22", 2022, "current"),
  S("ASCE 7", "Minimum Design Loads and Associated Criteria for Buildings and Other Structures", "US", "Structural", "7-16", 2017, "superseded", "7-22"),
  S("ASCE 7", "Minimum Design Loads (public comment draft)", "US", "Structural", "7-28", 2028, "draft"),
  S("ACI 318", "Building Code Requirements for Structural Concrete", "US", "Structural", "318-19 (R2022)", 2019, "current"),
  S("ACI 318", "Building Code Requirements for Structural Concrete", "US", "Structural", "318-25", 2025, "draft"),
  S("AISC 360", "Specification for Structural Steel Buildings", "US", "Structural", "360-22", 2022, "current"),
  S("AISC 341", "Seismic Provisions for Structural Steel Buildings", "US", "Structural", "341-22", 2022, "current"),
  S("NDS", "National Design Specification for Wood Construction", "US", "Structural", "2024", 2024, "current"),
  S("NFPA 13", "Standard for the Installation of Sprinkler Systems", "US", "Fire", "2022", 2022, "current"),
  S("NFPA 13", "Standard for the Installation of Sprinkler Systems", "US", "Fire", "2025", 2025, "draft"),
  S("NFPA 14", "Standard for the Installation of Standpipe and Hose Systems", "US", "Fire", "2024", 2024, "current"),
  S("NFPA 72", "National Fire Alarm and Signaling Code", "US", "Fire", "2022", 2022, "current"),
  S("NFPA 285", "Fire Test Method for Exterior Wall Assemblies", "US", "Fire", "2023", 2023, "current"),
  S("ASHRAE 90.1", "Energy Standard for Sites and Buildings", "US", "Energy", "2022", 2022, "current"), S("ASHRAE 90.1", "Energy Standard for Buildings", "US", "Energy", "2019", 2019, "superseded", "2022"),
  S("ASHRAE 62.1", "Ventilation and Acceptable Indoor Air Quality", "US", "Mechanical", "2022", 2022, "current"),
  S("ASHRAE 55", "Thermal Environmental Conditions for Human Occupancy", "US", "Mechanical", "2023", 2023, "current"),
  S("NEC", "National Electrical Code (NFPA 70)", "US", "Electrical", "2023", 2023, "current"), S("NEC", "National Electrical Code (NFPA 70)", "US", "Electrical", "2026", 2026, "draft"),
  S("IPC", "International Plumbing Code", "US", "Hydraulics", "2024", 2024, "current"),
  S("ADA 2010", "ADA Standards for Accessible Design", "US", "Accessibility", "2010", 2010, "current"),
  S("EN 1990", "Eurocode — Basis of structural design", "UK", "Structural", "2002+A1:2005", 2005, "current"),
  S("EN 1991-1-4", "Eurocode 1 — Wind actions", "UK", "Structural", "2005+A1:2010", 2010, "current"),
  S("EN 1998-1", "Eurocode 8 — Seismic design", "UK", "Structural", "2004+A1:2013", 2013, "current"),
  S("EN 1992-1-1", "Eurocode 2 — Concrete structures", "UK", "Structural", "2004+A1:2014", 2014, "current"),
  S("EN 1992-1-1", "Eurocode 2 — Concrete structures (2nd generation)", "UK", "Structural", "2023", 2023, "draft"),
  S("EN 1993-1-1", "Eurocode 3 — Steel structures", "UK", "Structural", "2005+A1:2014", 2014, "current"),
  S("EN 1997-1", "Eurocode 7 — Geotechnical design", "UK", "Geotechnical", "2004+A1:2013", 2013, "current"),
  S("Approved Document B", "Fire safety, Volume 2", "UK", "Fire", "2019 incorporating 2020 & 2022 amendments", 2022, "current"),
  S("Approved Document L", "Conservation of fuel and power, Volume 2", "UK", "Energy", "2021", 2021, "current"),
  S("Approved Document M", "Access to and use of buildings, Volume 2", "UK", "Accessibility", "2015 incorporating 2016 amendments", 2016, "current"),
  S("BS 7671", "Requirements for Electrical Installations", "UK", "Electrical", "2018+A2:2022", 2022, "current"),
  S("NCC", "National Construction Code Volume One", "AU", "General", "2022", 2022, "current"), S("NCC", "National Construction Code Volume One", "AU", "General", "2019 Amdt 1", 2019, "superseded", "2022"),
  S("NCC", "National Construction Code (public comment draft)", "AU", "General", "2025", 2025, "draft"),
  S("AS 1170.4", "Structural design actions — Earthquake actions", "AU", "Structural", "2007 (R2018) Amdt 2", 2018, "current"),
  S("AS/NZS 1170.2", "Structural design actions — Wind actions", "AU", "Structural", "2021", 2021, "current"),
  S("AS 3600", "Concrete structures", "AU", "Structural", "2018 Amdt 2", 2021, "current"),
  S("AS 1428.1", "Design for access and mobility", "AU", "Accessibility", "2021", 2021, "current"),
  S("AS/NZS 3000", "Wiring Rules", "AU", "Electrical", "2018 Amdt 2", 2021, "current"),
  S("NZBC", "New Zealand Building Code", "NZ", "General", "2024", 2024, "current"),
  S("NZS 1170.5", "Earthquake actions — New Zealand", "NZ", "Structural", "2004 A1", 2016, "current"),
  S("NZS 3101", "Concrete structures standard", "NZ", "Structural", "2006 A3", 2017, "current"),
  S("NBC", "National Building Code of Canada", "CA", "General", "2020", 2020, "current"), S("NBC", "National Building Code of Canada", "CA", "General", "2025", 2025, "draft"),
  S("CSA A23.3", "Design of concrete structures", "CA", "Structural", "A23.3:24", 2024, "current"),
  S("SS EN 1992", "Eurocode 2 with Singapore National Annex", "SG", "Structural", "2008", 2008, "current"),
  S("BCA Approved Document", "Acceptable solutions (Building Control Regulations)", "SG", "General", "2024", 2024, "current"),
];
