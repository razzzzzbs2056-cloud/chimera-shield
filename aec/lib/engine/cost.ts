// Quantity take-off, bill of quantities, cost estimate and embodied carbon.

import { round, sum } from "./linalg";
import type { ElecResult, HvacResult, HydResult } from "./mep";
import type { Derived } from "./site";
import type { DesignParams, Intake } from "./types";
import type { FoundationOption } from "./geotech";
import type { structuralQuantities } from "./structure";

export const LOCATION_FACTOR: Record<string, number> = {
  "San Francisco": 1.32, "Los Angeles": 1.18, Seattle: 1.12, "New York": 1.35, Boston: 1.22, Austin: 0.92, Houston: 0.9, Chicago: 1.1,
  London: 1.25, Manchester: 1.0, Sydney: 1.08, Melbourne: 1.02, Auckland: 1.05, Wellington: 1.04, Singapore: 0.95, Toronto: 1.08, Vancouver: 1.12,
};
export const locationFactor = (city: string) => LOCATION_FACTOR[city] ?? 1.0;

// A1–A3 factors (kgCO2e per unit) — ICE v3-style generic values
const CARBON: Record<string, number> = {
  concrete: 300, concreteGgbs50: 190, rebar: 1990, steel: 1550, pt: 2300, timber: 220, deck: 28, formwork: 4,
  glazing: 95, opaque: 60, mullion: 90, alu: 13000, duct: 6.5, pipe: 12, cable: 3.5, plant: 450, lift: 18000, finishes: 45, partitions: 25, pile: 340,
};

export interface BoqItem { code: string; section: string; item: string; unit: string; qty: number; rate: number; amount: number; carbon: number; discipline: string }
export interface CostResult {
  quantities: Record<string, { qty: number; unit: string }>;
  boq: BoqItem[]; subtotal: number; preliminaries: number; contingency: number; fees: number; escalation: number; total: number;
  perM2: number; byDiscipline: { name: string; value: number }[]; byFloor: { level: string; value: number }[]; bySystem: { name: string; value: number }[];
  budget: number; variance: number;
  carbon: { total: number; perM2: number; a1a3: number; a4a5: number; byCategory: { name: string; value: number }[]; target: number };
}

export function estimate(intake: Intake, d: Derived, p: DesignParams, sq: ReturnType<typeof structuralQuantities>, h: HvacResult, e: ElecResult, w: HydResult, fnd: FoundationOption): CostResult {
  const lf = locationFactor(intake.city);
  const gfa = d.gfa;
  const facadeA = d.perimeter * d.height;
  const glazA = facadeA * p.wwr, opaqueA = facadeA - glazA;
  const ductLen = (4 * (p.coreWidth + p.coreDepth + 20) + 30) * p.floors;
  const ductKg = ductLen * Math.PI * h.ducts.mainDiameter * 0.8 * 7.85; // 0.8 mm galv
  const pipeLen = (d.Lx * 2 + 40) * p.floors + d.height * 8;
  const cableLen = sum(e.risers.map((r) => r.length * r.parallel)) + d.gfaAbove * 1.6;
  const excavation = d.plateArea * (p.basementLevels * 3.5 + 1.2);
  const ggbs = p.ggbsReplacement;
  const conc = sq.concrete;
  const rebarT = sq.rebar;
  const fix = (x: number) => round(x, 0);
  const items: Omit<BoqItem, "amount">[] = [
    { code: "01 50 00", section: "Preliminaries", item: "Site establishment & temporary facilities", unit: "item", qty: 1, rate: 350000 + gfa * 4, carbon: 0, discipline: "General" },
    { code: "31 23 16", section: "Substructure", item: "Bulk excavation & disposal", unit: "m³", qty: fix(excavation), rate: 55, carbon: excavation * 3.5, discipline: "Civil" },
    { code: "31 50 00", section: "Substructure", item: "Excavation support & dewatering", unit: "m²", qty: fix(d.perimeter * (p.basementLevels * 3.5 + 1.2)), rate: p.basementLevels ? 950 : 0, carbon: d.perimeter * p.basementLevels * 3.5 * 120, discipline: "Civil" },
    { code: "31 60 00", section: "Substructure", item: `Foundations — ${fnd.label}`, unit: "item", qty: 1, rate: fnd.cost / lf, carbon: fnd.carbon * 1000, discipline: "Structure" },
    { code: "03 30 00", section: "Frame", item: `Cast-in-place concrete C${p.concreteGrade}${ggbs > 0 ? ` (${Math.round(ggbs * 100)} % GGBS)` : ""}`, unit: "m³", qty: fix(conc), rate: 300 + p.concreteGrade * 1.5, carbon: conc * (CARBON.concrete * (1 - ggbs * 0.75) + p.concreteGrade * 1.5), discipline: "Structure" },
    { code: "03 20 00", section: "Frame", item: "Reinforcing steel", unit: "t", qty: round(rebarT, 1), rate: 2650, carbon: rebarT * CARBON.rebar, discipline: "Structure" },
    { code: "03 11 00", section: "Frame", item: "Formwork", unit: "m²", qty: fix(sq.formwork), rate: 105, carbon: sq.formwork * CARBON.formwork, discipline: "Structure" },
    { code: "03 38 00", section: "Frame", item: "Post-tensioning strand", unit: "t", qty: round(sq.ptStrand, 1), rate: 5200, carbon: sq.ptStrand * CARBON.pt, discipline: "Structure" },
    { code: "05 12 00", section: "Frame", item: "Structural steel (columns, beams, bracing)", unit: "t", qty: round(sq.structuralSteel, 1), rate: 6400, carbon: sq.structuralSteel * CARBON.steel, discipline: "Structure" },
    { code: "05 31 00", section: "Frame", item: "Composite metal deck", unit: "m²", qty: fix(sq.deck), rate: 85, carbon: sq.deck * CARBON.deck, discipline: "Structure" },
    { code: "06 17 19", section: "Frame", item: "Mass timber (CLT / glulam)", unit: "m³", qty: round(sq.timber, 1), rate: 2100, carbon: sq.timber * CARBON.timber, discipline: "Structure" },
    { code: "08 44 13", section: "Envelope", item: `Glazed ${p.facadeType} (U ${p.glazingU}, SHGC ${p.shgc})`, unit: "m²", qty: fix(glazA), rate: p.facadeType === "unitised" ? 1650 : p.facadeType === "curtain-wall" ? 1350 : 950, carbon: glazA * CARBON.glazing, discipline: "Façade" },
    { code: "07 42 00", section: "Envelope", item: `Opaque wall / spandrel (U ${p.wallU})`, unit: "m²", qty: fix(opaqueA), rate: p.facadeType === "punched" ? 700 : 820, carbon: opaqueA * CARBON.opaque, discipline: "Façade" },
    { code: "07 50 00", section: "Envelope", item: `Roofing & insulation (U ${p.roofU})`, unit: "m²", qty: fix(d.plateArea), rate: 320, carbon: d.plateArea * 40, discipline: "Façade" },
    { code: "09 00 00", section: "Fit-out", item: "Floor, wall & ceiling finishes", unit: "m²", qty: fix(d.gfaAbove), rate: ({ hospital: 1150, hotel: 900, laboratory: 850, residential: 700, school: 520, retail: 450, office: 520, "mixed-use": 620, warehouse: 160 } as Record<string, number>)[intake.buildingType], carbon: d.gfaAbove * CARBON.finishes, discipline: "Architecture" },
    { code: "09 21 16", section: "Fit-out", item: "Partitions & doors", unit: "m²", qty: fix(d.gfaAbove * 0.6), rate: 170, carbon: d.gfaAbove * 0.6 * CARBON.partitions, discipline: "Architecture" },
    { code: "14 21 00", section: "Vertical transport", item: "Passenger & fire-service lifts", unit: "nr", qty: p.liftCount, rate: 240000 + p.floors * 14000, carbon: p.liftCount * CARBON.lift, discipline: "Vertical transport" },
    { code: "23 64 00", section: "Mechanical", item: `Chillers ${h.plant.chillers} × ${h.plant.chillerSize} kW`, unit: "kW", qty: h.plant.chillers * h.plant.chillerSize, rate: 520, carbon: h.plant.chillers * h.plant.chillerSize * 9, discipline: "Mechanical" },
    { code: "23 52 00", section: "Mechanical", item: p.heating === "heat-pump" ? `Air-source heat pumps × ${h.plant.heatPumps}` : `Boilers × ${h.plant.boilers}`, unit: "kW", qty: fix(h.heatingPeak), rate: p.heating === "heat-pump" ? 780 : 260, carbon: h.heatingPeak * 12, discipline: "Mechanical" },
    { code: "23 73 00", section: "Mechanical", item: `AHUs ${h.plant.ahus} × ${h.plant.ahuSize} m³/s`, unit: "nr", qty: h.plant.ahus, rate: 140000 + h.plant.ahuSize * 9000, carbon: h.plant.ahus * 9000, discipline: "Mechanical" },
    { code: "23 31 00", section: "Mechanical", item: "Ductwork (galvanised, insulated)", unit: "kg", qty: fix(ductKg), rate: 32, carbon: ductKg * CARBON.duct, discipline: "Mechanical" },
    { code: "23 05 00", section: "Mechanical", item: "Terminal units, controls & BMS", unit: "m²", qty: fix(d.gfaAbove), rate: 430, carbon: d.gfaAbove * 8, discipline: "Mechanical" },
    { code: "26 12 00", section: "Electrical", item: `Transformers ${e.transformers.config}`, unit: "kVA", qty: e.transformers.size * e.transformers.count, rate: 140, carbon: e.transformers.size * e.transformers.count * 6, discipline: "Electrical" },
    { code: "26 24 13", section: "Electrical", item: `Main switchboard ${e.mainSwitchboard.rating} A`, unit: "item", qty: 1, rate: 180000 + e.mainSwitchboard.rating * 60, carbon: 12000, discipline: "Electrical" },
    { code: "26 05 19", section: "Electrical", item: "LV cables & containment", unit: "m", qty: fix(cableLen), rate: 70, carbon: cableLen * CARBON.cable, discipline: "Electrical" },
    { code: "26 50 00", section: "Electrical", item: "Lighting & small power", unit: "m²", qty: fix(d.gfaAbove), rate: 360, carbon: d.gfaAbove * 9, discipline: "Electrical" },
    { code: "26 32 13", section: "Electrical", item: `Generator ${e.generator.kVA} kVA`, unit: "item", qty: 1, rate: 90000 + e.generator.kVA * 260, carbon: e.generator.kVA * 25, discipline: "Electrical" },
    { code: "48 14 00", section: "Electrical", item: `Rooftop PV ${e.pv.kWp} kWp`, unit: "kWp", qty: e.pv.kWp, rate: 1350, carbon: e.pv.kWp * 600, discipline: "Electrical" },
    { code: "26 33 53", section: "Electrical", item: `Battery storage ${e.battery.kWh} kWh`, unit: "kWh", qty: e.battery.kWh, rate: 520, carbon: e.battery.kWh * 75, discipline: "Electrical" },
    { code: "26 51 00", section: "Electrical", item: `EV chargers × ${e.ev.chargers}`, unit: "nr", qty: e.ev.chargers, rate: 4200, carbon: e.ev.chargers * 300, discipline: "Electrical" },
    { code: "22 11 16", section: "Hydraulics", item: "Domestic water piping", unit: "m", qty: fix(pipeLen), rate: 240, carbon: pipeLen * CARBON.pipe, discipline: "Hydraulics" },
    { code: "22 40 00", section: "Hydraulics", item: "Sanitary fixtures", unit: "nr", qty: sum(w.fixtures.map((x) => x.count)), rate: 2600, carbon: sum(w.fixtures.map((x) => x.count)) * 60, discipline: "Hydraulics" },
    { code: "22 11 23", section: "Hydraulics", item: `Booster pumps (${w.pressureZones} zones)`, unit: "item", qty: w.boosterRequired ? w.pressureZones : 0, rate: 65000, carbon: 4000, discipline: "Hydraulics" },
    { code: "22 14 00", section: "Hydraulics", item: "Storm drainage & rainwater harvesting", unit: "item", qty: 1, rate: 90000 + w.rainwater.tank * 900, carbon: 15000, discipline: "Hydraulics" },
    { code: "11 00 00", section: "Specialist systems", item: ({ hospital: "Medical gases, nurse call, imaging shielding & medical equipment", laboratory: "Lab services, fume exhaust & casework", school: "Educational FF&E & AV", hotel: "FF&E and kitchens", residential: "Kitchens, joinery & appliances", "mixed-use": "Tenant kitchens & joinery", office: "Lobby, amenity & AV", retail: "Shopfronts", warehouse: "Racking" } as Record<string, string>)[intake.buildingType], unit: "m²", qty: fix(d.gfaAbove), rate: ({ hospital: 1900, laboratory: 1250, school: 160, hotel: 420, residential: 330, "mixed-use": 220, office: 60, retail: 40, warehouse: 50 } as Record<string, number>)[intake.buildingType], carbon: d.gfaAbove * 20, discipline: "Architecture" },
    { code: "21 13 13", section: "Fire protection", item: "Wet-pipe sprinklers", unit: "m²", qty: p.sprinklered ? fix(d.gfa) : 0, rate: 70, carbon: d.gfa * 3, discipline: "Fire" },
    { code: "28 31 00", section: "Fire protection", item: "Fire alarm, EWIS & smoke control", unit: "m²", qty: fix(d.gfa), rate: 65, carbon: d.gfa * 2, discipline: "Fire" },
  ];
  const boq: BoqItem[] = items.filter((i) => i.qty > 0 && i.rate > 0).map((i) => ({ ...i, rate: round(i.rate * lf, 2), amount: round(i.qty * i.rate * lf, 0), carbon: round(i.carbon / 1000, 1) }));
  const subtotal = sum(boq.map((b) => b.amount));
  const preliminaries = subtotal * 0.11;
  const contingency = (subtotal + preliminaries) * 0.08;
  const fees = (subtotal + preliminaries) * 0.09;
  const escalation = (subtotal + preliminaries) * 0.035 * 2;
  const total = subtotal + preliminaries + contingency + fees + escalation;
  const disc = new Map<string, number>();
  boq.forEach((b) => disc.set(b.discipline, (disc.get(b.discipline) ?? 0) + b.amount));
  const sys = new Map<string, number>();
  boq.forEach((b) => sys.set(b.section, (sys.get(b.section) ?? 0) + b.amount));
  const substructure = sum(boq.filter((b) => b.section === "Substructure" || b.section === "Preliminaries").map((b) => b.amount));
  const perFloor = (subtotal - substructure) / p.floors;
  const byFloor = [{ level: "Substructure", value: round(substructure, 0) }, ...Array.from({ length: p.floors }, (_, i) => ({ level: `L${i + 1}`, value: round(perFloor * (i === 0 ? 1.35 : i === p.floors - 1 ? 1.25 : 0.985), 0) }))];
  const carbonA13 = sum(boq.map((b) => b.carbon)) * 1000;
  const a4a5 = carbonA13 * 0.12;
  const byCat = new Map<string, number>();
  boq.forEach((b) => byCat.set(b.section, (byCat.get(b.section) ?? 0) + b.carbon));
  return {
    quantities: {
      Concrete: { qty: sq.concrete, unit: "m³" }, Rebar: { qty: sq.rebar, unit: "t" }, "Structural steel": { qty: sq.structuralSteel, unit: "t" },
      "Mass timber": { qty: sq.timber, unit: "m³" }, Formwork: { qty: sq.formwork, unit: "m²" }, Glazing: { qty: round(glazA, 0), unit: "m²" },
      "Opaque façade": { qty: round(opaqueA, 0), unit: "m²" }, Ductwork: { qty: round(ductKg, 0), unit: "kg" }, Pipework: { qty: round(pipeLen, 0), unit: "m" },
      Cables: { qty: round(cableLen, 0), unit: "m" }, Fixtures: { qty: sum(w.fixtures.map((x) => x.count)), unit: "nr" }, Excavation: { qty: round(excavation, 0), unit: "m³" },
    },
    boq, subtotal: round(subtotal, 0), preliminaries: round(preliminaries, 0), contingency: round(contingency, 0), fees: round(fees, 0), escalation: round(escalation, 0),
    total: round(total, 0), perM2: round(total / gfa, 0),
    byDiscipline: [...disc.entries()].map(([name, value]) => ({ name, value: round(value, 0) })).sort((a, b) => b.value - a.value),
    byFloor, bySystem: [...sys.entries()].map(([name, value]) => ({ name, value: round(value, 0) })),
    budget: intake.budget, variance: round(total - intake.budget, 0),
    carbon: {
      total: round((carbonA13 + a4a5) / 1000, 0), perM2: round((carbonA13 + a4a5) / gfa, 0), a1a3: round(carbonA13 / 1000, 0), a4a5: round(a4a5 / 1000, 0),
      byCategory: [...byCat.entries()].map(([name, value]) => ({ name, value: round(value, 0) })).sort((a, b) => b.value - a.value), target: intake.targetCarbon,
    },
  };
}
