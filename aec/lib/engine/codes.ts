// Code intelligence: applicable standards by jurisdiction & classification,
// clause-level references for every automated check, and code-version control.

import type { Derived } from "./site";
import type { DesignParams, Intake, Jurisdiction, StandardRef } from "./types";

type Ref = { std: string; clause: string };
// family names used in the standards library (StandardRef.code prefix match)
export const CLAUSES: Record<string, Partial<Record<Jurisdiction, Ref>>> = {
  "seismic-base-shear": { US: { std: "ASCE 7", clause: "§12.8.1, Eq. 12.8-1/12.8-2" }, UK: { std: "EN 1998-1", clause: "§4.3.3.2.2" }, AU: { std: "AS 1170.4", clause: "§6.2" }, NZ: { std: "NZS 1170.5", clause: "§6.2" }, CA: { std: "NBC", clause: "Div. B 4.1.8.11" } },
  "seismic-period": { US: { std: "ASCE 7", clause: "§12.8.2, Table 12.8-1" }, UK: { std: "EN 1998-1", clause: "§4.3.3.2.2(3)" }, NZ: { std: "NZS 1170.5", clause: "§4.1.2" } },
  "rsa-scaling": { US: { std: "ASCE 7", clause: "§12.9.1.4.1" }, NZ: { std: "NZS 1170.5", clause: "§5.2.2.2" } },
  "modal-mass": { US: { std: "ASCE 7", clause: "§12.9.1.1" }, UK: { std: "EN 1998-1", clause: "§4.3.3.3.1(3)" }, NZ: { std: "NZS 1170.5", clause: "§6.3.3" } },
  "story-drift": { US: { std: "ASCE 7", clause: "§12.12.1, Table 12.12-1" }, UK: { std: "EN 1998-1", clause: "§4.4.3.2" }, AU: { std: "AS 1170.4", clause: "§5.4.4" }, NZ: { std: "NZS 1170.5", clause: "§7.5.1" }, CA: { std: "NBC", clause: "Div. B 4.1.8.13" } },
  "p-delta": { US: { std: "ASCE 7", clause: "§12.8.7, Eq. 12.8-16/17" }, UK: { std: "EN 1998-1", clause: "§4.4.2.2(2)" }, NZ: { std: "NZS 1170.5", clause: "§6.5" } },
  "torsion": { US: { std: "ASCE 7", clause: "§12.3.2.1, Table 12.3-1 (1a/1b); §12.8.4.3" }, UK: { std: "EN 1998-1", clause: "§4.3.3.2.4" }, NZ: { std: "NZS 1170.5", clause: "§4.5.2" } },
  "height-limit": { US: { std: "ASCE 7", clause: "Table 12.2-1; §12.2.5.4" }, NZ: { std: "NZS 1170.5", clause: "§2.6" } },
  "site-class": { US: { std: "ASCE 7", clause: "Ch. 20, Table 20.2-1" }, UK: { std: "EN 1998-1", clause: "§3.1.2, Table 3.1" }, AU: { std: "AS 1170.4", clause: "§4.2" }, NZ: { std: "NZS 1170.5", clause: "§3.1.3" } },
  "liquefaction": { US: { std: "ASCE 7", clause: "§11.8.3(b)" }, UK: { std: "EN 1998-5", clause: "§4.1.4" }, NZ: { std: "NZS 1170.5", clause: "C3.1.3 (MBIE Module 3)" } },
  "wind-pressure": { US: { std: "ASCE 7", clause: "§26.10, Eq. 26.10-1; §27.3" }, UK: { std: "EN 1991-1-4", clause: "§4.5" }, AU: { std: "AS/NZS 1170.2", clause: "§2.4" }, NZ: { std: "AS/NZS 1170.2", clause: "§2.4" }, CA: { std: "NBC", clause: "Div. B 4.1.7" } },
  "gust-factor": { US: { std: "ASCE 7", clause: "§26.11.5" }, UK: { std: "EN 1991-1-4", clause: "§6.3" }, AU: { std: "AS/NZS 1170.2", clause: "§6.2" } },
  "wind-drift": { US: { std: "ASCE 7", clause: "Appendix CC.2.2 (serviceability)" }, UK: { std: "EN 1990", clause: "A1.4.3" } },
  "wind-accel": { US: { std: "ASCE 7", clause: "Commentary C26.11 / ISO 10137" }, UK: { std: "ISO 10137", clause: "Annex D" } },
  "vortex": { US: { std: "ASCE 7", clause: "C26.11 (vortex shedding)" }, UK: { std: "EN 1991-1-4", clause: "Annex E.1.3.2" } },
  "snow": { US: { std: "ASCE 7", clause: "§7.3, Eq. 7.3-1" }, UK: { std: "EN 1991-1-3", clause: "§5.2" }, NZ: { std: "AS/NZS 1170.3", clause: "§4" } },
  "live-load": { US: { std: "ASCE 7", clause: "Table 4.3-1" }, UK: { std: "EN 1991-1-1", clause: "Table 6.2" }, AU: { std: "AS/NZS 1170.1", clause: "Table 3.1" }, NZ: { std: "AS/NZS 1170.1", clause: "Table 3.1" } },
  "column-axial": { US: { std: "ACI 318", clause: "§22.4.2" }, UK: { std: "EN 1992-1-1", clause: "§6.1" }, AU: { std: "AS 3600", clause: "§10.6" }, NZ: { std: "NZS 3101", clause: "§10.3.4" } },
  "punching": { US: { std: "ACI 318", clause: "§22.6.5.2" }, UK: { std: "EN 1992-1-1", clause: "§6.4.4" }, AU: { std: "AS 3600", clause: "§9.3.3" }, NZ: { std: "NZS 3101", clause: "§12.7" } },
  "slab-thickness": { US: { std: "ACI 318", clause: "Table 8.3.1.1" }, UK: { std: "EN 1992-1-1", clause: "§7.4.2" }, AU: { std: "AS 3600", clause: "§9.3.4" } },
  "bearing": { US: { std: "IBC", clause: "§1806.2 / §1803.6" }, UK: { std: "EN 1997-1", clause: "§6.5.2" }, AU: { std: "AS 2159", clause: "§4" } },
  "settlement": { US: { std: "IBC", clause: "§1808.2" }, UK: { std: "EN 1997-1", clause: "§6.6, Annex H" } },
  "occupant-load": { US: { std: "IBC", clause: "§1004.5, Table 1004.5" }, UK: { std: "Approved Document B", clause: "Vol 2, Table 2.1 (B1)" }, AU: { std: "NCC", clause: "Vol One D2D18 (Table D2D18)" } },
  "exit-count": { US: { std: "IBC", clause: "§1006.3.3" }, UK: { std: "Approved Document B", clause: "Vol 2, §2.8 (Table 2.2)" }, AU: { std: "NCC", clause: "Vol One D2D3" } },
  "egress-width": { US: { std: "IBC", clause: "§1005.3.1" }, UK: { std: "Approved Document B", clause: "Vol 2, §3.20 (Table 3.1)" }, AU: { std: "NCC", clause: "Vol One D2D17" } },
  "stair-width": { US: { std: "IBC", clause: "§1011.2" }, UK: { std: "Approved Document B", clause: "Vol 2, Table 3.1" }, AU: { std: "NCC", clause: "Vol One D2D17" } },
  "travel-distance": { US: { std: "IBC", clause: "§1017.2, Table 1017.2" }, UK: { std: "Approved Document B", clause: "Vol 2, Table 2.1" }, AU: { std: "NCC", clause: "Vol One D2D5" } },
  "construction-type": { US: { std: "IBC", clause: "Tables 504.3/504.4, Table 601" }, UK: { std: "Approved Document B", clause: "Vol 2, Table B4" } },
  "sprinklers": { US: { std: "IBC", clause: "§903.2, §403.3; NFPA 13" }, UK: { std: "Approved Document B", clause: "Vol 2, §7.3 (B3)" }, AU: { std: "NCC", clause: "Vol One E1D4; AS 2118.1" } },
  "standpipes": { US: { std: "IBC", clause: "§905.3.1; NFPA 14" }, UK: { std: "Approved Document B", clause: "Vol 2, §16 (B5)" } },
  "fire-lift": { US: { std: "IBC", clause: "§3007.1" }, UK: { std: "Approved Document B", clause: "Vol 2, §17 (B5)" } },
  "aset-rset": { US: { std: "SFPE Handbook", clause: "Ch. 59 (hydraulic model) / ISO 13571" }, UK: { std: "BS 7974", clause: "PD 7974-6" } },
  "facade-fire": { US: { std: "IBC", clause: "§1402.5; NFPA 285" }, UK: { std: "Approved Document B", clause: "Vol 2, Reg. 7(2) & §12" }, AU: { std: "NCC", clause: "Vol One C2D10" } },
  "envelope-u": { US: { std: "ASHRAE 90.1", clause: "§5.5, Tables 5.5-1…5.5-8" }, UK: { std: "Approved Document L", clause: "Vol 2, Table 4.1" }, AU: { std: "NCC", clause: "Vol One Section J4" } },
  "wwr": { US: { std: "ASHRAE 90.1", clause: "§5.5.4.2.1 (≤ 40 %)" }, AU: { std: "NCC", clause: "Vol One J4D6" } },
  "ventilation": { US: { std: "ASHRAE 62.1", clause: "§6.2.2, Table 6.2.2.1" }, UK: { std: "Approved Document F", clause: "Vol 2, §1.21" }, AU: { std: "AS 1668.2", clause: "§2" } },
  "comfort": { US: { std: "ASHRAE 55", clause: "§5.3 (PMV –0.5…+0.5)" }, UK: { std: "EN 16798-1", clause: "Cat. II" } },
  "voltage-drop": { US: { std: "NEC", clause: "210.19(A) Info. Note 4; 215.2(A)(2)" }, UK: { std: "BS 7671", clause: "Appx 4 §6.4" }, AU: { std: "AS/NZS 3000", clause: "§3.6.2" }, NZ: { std: "AS/NZS 3000", clause: "§3.6.2" } },
  "transformer": { US: { std: "NEC", clause: "Art. 220 / 450.3" }, UK: { std: "BS 7671", clause: "§311" } },
  "emergency-power": { US: { std: "NEC", clause: "Art. 700/701; IBC §2702" }, UK: { std: "BS 5266-1", clause: "§5" } },
  "water-pressure": { US: { std: "IPC", clause: "§604.8 (max 80 psi / 552 kPa)" }, UK: { std: "BS EN 806-2", clause: "§3.5" }, AU: { std: "AS/NZS 3500.1", clause: "§3.3" } },
  "fixtures": { US: { std: "IPC", clause: "Table 2902.1" }, UK: { std: "BS 6465-1", clause: "§6" }, AU: { std: "NCC", clause: "Vol One F4D4" } },
  "roof-drainage": { US: { std: "IPC", clause: "§1106, §1108 (secondary drains)" }, UK: { std: "BS EN 12056-3", clause: "§5" }, AU: { std: "AS/NZS 3500.3", clause: "§5" } },
  "accessibility": { US: { std: "ADA 2010", clause: "" }, UK: { std: "Approved Document M", clause: "Vol 2" }, AU: { std: "AS 1428.1", clause: "" }, NZ: { std: "NZS 4121", clause: "" } },
  "condensation": { US: { std: "ASHRAE 160", clause: "§4" }, UK: { std: "BS EN ISO 13788", clause: "§5 (fRsi)" } },
  "mullion-deflection": { US: { std: "AAMA TIR-A11", clause: "L/175 ≤ 19 mm" }, UK: { std: "CWCT", clause: "Std. §3.3 / EN 13830" } },
  "embodied-carbon": { US: { std: "Client target", clause: "LETI / SE 2050 benchmark" } },
  "energy": { US: { std: "ASHRAE 90.1", clause: "Appendix G / §4.2.1" }, UK: { std: "Approved Document L", clause: "Vol 2, §2" }, AU: { std: "NCC", clause: "Vol One J1V3" } },
};

export function ref(check: string, j: Jurisdiction): Ref & { proxy: boolean } {
  const m = CLAUSES[check] ?? {};
  const r = m[j];
  if (r) return { ...r, proxy: false };
  return { ...(m.US ?? { std: "Engineering practice", clause: "" }), proxy: j !== "US" };
}

export interface ApplicableCode { code: string; title: string; edition: string; status: string; reason: string; pinned?: string; versionIssue?: string }

const TRIGGERS: { family: string; when: (i: Intake, d: Derived, p: DesignParams) => string | null }[] = [
  { family: "IBC", when: () => "Building code (adopted model code)" },
  { family: "ASCE 7", when: () => "Minimum design loads — wind, seismic, snow, live" },
  { family: "ACI 318", when: (_, __, p) => (p.material === "concrete" || p.lateralSystem !== "braced-frame" ? "Concrete core / slabs" : null) },
  { family: "AISC 360", when: (_, __, p) => (p.material === "steel" || p.material === "composite" ? "Structural steel members" : null) },
  { family: "AISC 341", when: (_, __, p) => (p.material === "steel" || p.material === "composite" ? "Seismic steel detailing" : null) },
  { family: "NDS", when: (_, __, p) => (p.material === "timber" ? "Mass-timber members & connections" : null) },
  { family: "NFPA 13", when: (_, __, p) => (p.sprinklered ? "Automatic sprinkler system" : null) },
  { family: "NFPA 14", when: (_, d) => (d.height > 9.1 ? "Standpipes (floor > 30 ft)" : null) },
  { family: "NFPA 72", when: () => "Fire alarm & emergency communication" },
  { family: "NFPA 285", when: (_, d) => (d.height > 12.2 ? "Exterior wall fire propagation" : null) },
  { family: "ASHRAE 90.1", when: () => "Energy efficiency" },
  { family: "ASHRAE 62.1", when: (i) => (i.buildingType !== "residential" ? "Ventilation for acceptable IAQ" : null) },
  { family: "ASHRAE 55", when: () => "Thermal comfort" },
  { family: "NEC", when: () => "Electrical installations (NFPA 70)" },
  { family: "IPC", when: () => "Plumbing" },
  { family: "ADA 2010", when: () => "Accessibility" },
  { family: "EN 1990", when: () => "Basis of structural design" },
  { family: "EN 1991-1-4", when: () => "Wind actions" },
  { family: "EN 1998-1", when: () => "Seismic design" },
  { family: "EN 1992-1-1", when: (_, __, p) => (p.material !== "timber" ? "Concrete structures" : null) },
  { family: "EN 1993-1-1", when: (_, __, p) => (p.material === "steel" || p.material === "composite" ? "Steel structures" : null) },
  { family: "EN 1995-1-1", when: (_, __, p) => (p.material === "timber" ? "Timber structures" : null) },
  { family: "EN 1997-1", when: () => "Geotechnical design" },
  { family: "Approved Document B", when: () => "Fire safety" },
  { family: "Approved Document L", when: () => "Conservation of fuel & power" },
  { family: "Approved Document M", when: () => "Access to and use of buildings" },
  { family: "BS 7671", when: () => "Wiring regulations" },
  { family: "NCC", when: () => "National Construction Code" },
  { family: "AS 1170.4", when: () => "Earthquake actions" },
  { family: "AS/NZS 1170.2", when: () => "Wind actions" },
  { family: "AS 3600", when: (_, __, p) => (p.material !== "timber" ? "Concrete structures" : null) },
  { family: "AS 1428.1", when: () => "Design for access and mobility" },
  { family: "AS/NZS 3000", when: () => "Wiring rules" },
  { family: "NZBC", when: () => "New Zealand Building Code" },
  { family: "NZS 1170.5", when: () => "Earthquake actions" },
  { family: "NZS 3101", when: (_, __, p) => (p.material !== "timber" ? "Concrete structures" : null) },
  { family: "NBC", when: () => "National Building Code of Canada" },
  { family: "CSA A23.3", when: (_, __, p) => (p.material !== "timber" ? "Design of concrete structures" : null) },
  { family: "SS EN 1992", when: () => "Concrete (Singapore NA)" },
  { family: "BCA Approved Document", when: () => "Building Control Act acceptable solutions" },
];

export function applicableCodes(intake: Intake, d: Derived, p: DesignParams, library: StandardRef[], pins: Record<string, string>): ApplicableCode[] {
  const out: ApplicableCode[] = [];
  for (const t of TRIGGERS) {
    const reason = t.when(intake, d, p);
    if (!reason) continue;
    const editions = library.filter((s) => s.code === t.family && (s.jurisdiction === intake.jurisdiction || s.jurisdiction === "INT"));
    if (!editions.length) continue;
    const current = editions.find((s) => s.status === "current") ?? [...editions].sort((a, b) => b.year - a.year)[0];
    const pinned = pins[t.family];
    const used = pinned ? editions.find((s) => s.edition === pinned) ?? current : current;
    let versionIssue: string | undefined;
    if (pinned && used.status === "superseded") versionIssue = `Project pinned to ${t.family} ${used.edition} (superseded by ${current.edition}). Confirm the permit application date supports the older edition.`;
    if (current.status === "draft") versionIssue = `Only a draft edition of ${t.family} is in the library.`;
    const newerDraft = editions.find((s) => s.status === "draft" && s.year > used.year);
    if (!versionIssue && newerDraft) versionIssue = `${t.family} ${newerDraft.edition} is in public review — monitor for adoption.`;
    out.push({ code: t.family, title: used.title, edition: used.edition, status: used.status, reason, pinned, versionIssue });
  }
  return out;
}
