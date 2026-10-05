// Automatic agent routing: decides which specialist agents a project needs.

import type { Derived, SeismicParams } from "./site";
import type { AgentInfo, Borehole, DesignParams, Intake } from "./types";

export const AGENT_CATALOG: { id: string; name: string; discipline: string }[] = [
  { id: "intake", name: "Intake & Brief", discipline: "Management" },
  { id: "codes", name: "Code Intelligence", discipline: "Compliance" },
  { id: "architecture", name: "Architecture", discipline: "Architecture" },
  { id: "geotech", name: "Geotechnical", discipline: "Geotechnical" },
  { id: "structural", name: "Structural", discipline: "Structural" },
  { id: "seismic", name: "Seismic", discipline: "Structural" },
  { id: "wind", name: "Wind Engineering", discipline: "Structural" },
  { id: "foundation", name: "Foundation Optimiser", discipline: "Geotechnical" },
  { id: "hvac", name: "HVAC", discipline: "Mechanical" },
  { id: "electrical", name: "Electrical", discipline: "Electrical" },
  { id: "hydraulic", name: "Hydraulic", discipline: "Hydraulics" },
  { id: "fire", name: "Fire Engineering", discipline: "Fire" },
  { id: "facade", name: "Façade Engineering", discipline: "Façade" },
  { id: "physics", name: "Building Physics & Energy", discipline: "Sustainability" },
  { id: "sustainability", name: "Carbon & Resilience", discipline: "Sustainability" },
  { id: "accessibility", name: "Accessibility", discipline: "Architecture" },
  { id: "civil", name: "Civil & Stormwater", discipline: "Civil" },
  { id: "bim", name: "BIM Coordination", discipline: "BIM" },
  { id: "cost", name: "Cost & BOQ", discipline: "Commercial" },
  { id: "ve", name: "Value Engineering", discipline: "Commercial" },
  { id: "construction", name: "Construction Planning", discipline: "Construction" },
  { id: "operations", name: "Digital Twin & Operations", discipline: "Operations" },
  { id: "verifier", name: "Independent Verifier", discipline: "QA" },
];

export function routeAgents(intake: Intake, d: Derived, p: DesignParams, seis: SeismicParams, boreholes: Borehole[]): AgentInfo[] {
  const why: Record<string, [boolean, string]> = {
    intake: [true, "Normalises brief, site and performance targets"],
    codes: [true, `Jurisdiction ${intake.jurisdiction}, occupancy ${d.occupancyGroup}, risk category ${d.riskCategory}`],
    architecture: [true, `${p.floors}-storey ${intake.buildingType}, ${Math.round(d.gfa).toLocaleString()} m² GFA`],
    geotech: [true, boreholes.length ? `${boreholes.length} borehole log(s) to interpret` : "No boreholes — assumed profile, investigation required"],
    structural: [true, "Gravity & lateral system design"],
    seismic: [seis.sdc !== "A", `SDC ${seis.sdc} (SDS ${seis.SDS} g, SD1 ${seis.SD1} g)`],
    wind: [true, d.height > 60 ? `Tall building (${Math.round(d.height)} m) — dynamic wind response` : `Basic wind speed ${intake.basicWindSpeed} m/s`],
    foundation: [true, `${p.basementLevels} basement level(s), compare 5 foundation systems`],
    hvac: [true, `Climate zone ${intake.climateZone}, ${intake.cdd} CDD / ${intake.hdd} HDD`],
    electrical: [true, intake.parkingSpaces > 0 ? `Includes ${intake.parkingSpaces}-space EV infrastructure` : "Power, lighting, PV & emergency"],
    hydraulic: [true, `${d.occupants.toLocaleString()} occupants, ${intake.rainfall} mm/h design storm`],
    fire: [true, d.highRise ? "High-rise provisions (IBC §403)" : "Egress & fire protection"],
    facade: [true, `${p.facadeType}, WWR ${Math.round(p.wwr * 100)} %`],
    physics: [true, `Target EUI ${intake.targetEUI} kWh/m²·yr`],
    sustainability: [true, `Embodied-carbon target ${intake.targetCarbon} kgCO₂e/m²; ${intake.floodZone ? "flood zone" : "resilience screening"}`],
    accessibility: [true, "Accessible routes, lifts, facilities"],
    civil: [intake.rainfall > 0, "Stormwater detention & site drainage"],
    bim: [true, "IFC model authoring and clash detection"],
    cost: [true, `Budget $${(intake.budget / 1e6).toFixed(1)} M`],
    ve: [true, "Proposes cheaper alternatives with performance checks"],
    construction: [true, "Sequencing, 4D/5D, cranes, temporary works"],
    operations: [true, "Asset register, predictive maintenance, optimisation"],
    verifier: [true, "Re-derives key results by independent methods"],
  };
  return AGENT_CATALOG.map((a) => ({ ...a, required: why[a.id][0], reason: why[a.id][1] }));
}
