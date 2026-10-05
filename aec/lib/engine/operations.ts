// Digital twin, predictive maintenance and operational optimisation.
// Sensor series are synthesised deterministically from the asset id so the
// demo is reproducible; in production they are replaced by BMS/IoT feeds.

import { hashString, rng, round } from "./linalg";

export interface AssetInput { id: string; name: string; system: string; type: string; installDate: string; condition: number; runtimeHours: number; criticality: number; location: string }

const WEIBULL: Record<string, { beta: number; eta: number; mttr: number; metric: string; unit: string; base: number; noise: number }> = {
  chiller: { beta: 2.2, eta: 42000, mttr: 24, metric: "kW/ton", unit: "kW/t", base: 0.62, noise: 0.03 },
  ahu: { beta: 1.9, eta: 38000, mttr: 8, metric: "Fan vibration", unit: "mm/s", base: 2.1, noise: 0.3 },
  pump: { beta: 1.6, eta: 30000, mttr: 6, metric: "Bearing temperature", unit: "°C", base: 48, noise: 1.5 },
  lift: { beta: 1.8, eta: 25000, mttr: 12, metric: "Door faults / day", unit: "count", base: 0.4, noise: 0.3 },
  boiler: { beta: 2.0, eta: 45000, mttr: 16, metric: "Flue temperature", unit: "°C", base: 140, noise: 4 },
  transformer: { beta: 3.0, eta: 180000, mttr: 72, metric: "Winding temperature", unit: "°C", base: 72, noise: 2 },
  facade: { beta: 2.5, eta: 220000, mttr: 40, metric: "Sealant ΔT anomaly", unit: "K", base: 0.5, noise: 0.2 },
  structure: { beta: 3.5, eta: 400000, mttr: 200, metric: "Crack-gauge width", unit: "mm", base: 0.18, noise: 0.01 },
  generator: { beta: 1.7, eta: 15000, mttr: 10, metric: "Start time", unit: "s", base: 8, noise: 0.6 },
};

export interface AssetHealth {
  id: string; name: string; system: string; type: string; location: string; condition: number; health: number; pf90: number; rul: number;
  nextService: string; risk: number; status: "healthy" | "watch" | "action"; metric: string; unit: string;
  series: { t: string; v: number; limit: number }[]; anomalies: number;
}

export function assetHealth(a: AssetInput, today = new Date("2026-10-05")): AssetHealth {
  const w = WEIBULL[a.type] ?? WEIBULL.pump;
  const R = rng(hashString(a.id + a.name));
  // condition (1–5) shifts effective age
  const effAge = a.runtimeHours * (1 + (3 - a.condition) * 0.25);
  const rel = (t: number) => Math.exp(-((t / w.eta) ** w.beta));
  const horizon = 90 * 24 * 0.6; // operating hours in 90 days
  const pf90 = 1 - rel(effAge + horizon) / Math.max(rel(effAge), 1e-9);
  // remaining useful life: hours until R(t)/R(age) = 0.5
  let t = effAge;
  while (rel(t) / Math.max(rel(effAge), 1e-9) > 0.5 && t < effAge + w.eta * 3) t += w.eta / 200;
  const rul = (t - effAge) / (24 * 0.6); // days
  const drift = (1 - a.condition / 5) * 0.25 + pf90;
  const series: AssetHealth["series"] = [];
  let anomalies = 0;
  const limit = w.base * (1 + 0.35);
  for (let i = 59; i >= 0; i--) {
    const day = new Date(today.getTime() - i * 86400000);
    const trend = w.base * (1 + drift * (1 - i / 60) * 0.5);
    let v = trend + (R() - 0.5) * 2 * w.noise;
    if (R() < 0.03 + pf90 * 0.15) { v += w.noise * 4; anomalies++; }
    series.push({ t: day.toISOString().slice(5, 10), v: round(v, 3), limit: round(limit, 3) });
  }
  const health = Math.max(0, Math.min(100, round((1 - pf90) * 70 + a.condition * 6, 0)));
  const risk = round(pf90 * a.criticality * 100, 1);
  const next = new Date(today.getTime() + Math.max(7, Math.min(rul * 0.4, 180)) * 86400000);
  return {
    id: a.id, name: a.name, system: a.system, type: a.type, location: a.location, condition: a.condition, health, pf90: round(pf90 * 100, 1), rul: round(rul, 0),
    nextService: next.toISOString().slice(0, 10), risk, status: risk > 20 || health < 45 ? "action" : risk > 8 || health < 65 ? "watch" : "healthy",
    metric: w.metric, unit: w.unit, series, anomalies,
  };
}

export interface TwinState {
  zones: { level: number; zone: string; temp: number; co2: number; occupancy: number; setpoint: number }[];
  energy: { hour: number; actual: number; baseline: number; anomaly: boolean }[];
  kpis: { eui: number; comfort: number; anomalies: number; savingsPotential: number };
  recommendations: { title: string; saving: number; detail: string }[];
}

export function twinState(projectId: string, floors: number, eui: number, gfa: number): TwinState {
  const R = rng(hashString(projectId + "twin"));
  const zones: TwinState["zones"] = [];
  const sample = Math.min(floors, 12);
  for (let k = 0; k < sample; k++) {
    const level = Math.round(((k + 1) * floors) / sample);
    for (const zone of ["N", "E", "S", "W", "Core"]) {
      const sun = zone === "W" ? 1.2 : zone === "S" ? 0.8 : zone === "E" ? 0.5 : 0;
      zones.push({ level, zone, temp: round(22.4 + sun + (R() - 0.5) * 1.4, 1), co2: Math.round(520 + R() * 480), occupancy: Math.round(R() * 100), setpoint: 22.5 });
    }
  }
  const hourlyBase = (eui * gfa) / 8760;
  const energy = Array.from({ length: 48 }, (_, i) => {
    const h = i % 24;
    const occ = h >= 7 && h <= 19 ? 1 : 0.35;
    const baseline = hourlyBase * (0.6 + occ * 0.9);
    const spike = (i === 26 || i === 27 || i === 3) ? 1.35 : 1;
    const actual = baseline * (0.92 + R() * 0.12) * spike;
    return { hour: i, actual: round(actual, 0), baseline: round(baseline, 0), anomaly: actual > baseline * 1.25 };
  });
  const anomalies = energy.filter((e) => e.anomaly).length;
  const hot = zones.filter((z) => z.temp > 24).length;
  const recommendations = [
    { title: "After-hours HVAC running (02:00–04:00)", saving: round(hourlyBase * 0.35 * 3 * 365 * 0.18, 0), detail: "AHUs held occupied mode overnight; enforce BMS time schedule & optimum start." },
    { title: "Supply-air temperature reset", saving: round(eui * gfa * 0.04 * 0.18, 0), detail: "Reset SAT 13 → 16 °C on low-load days; chiller kW/t improves ≈ 6 %." },
    { title: `West-zone overheating (${hot} zones > 24 °C)`, saving: round(eui * gfa * 0.01 * 0.18, 0), detail: "Automate blinds by solar position before raising cooling capacity." },
    { title: "Demand-controlled ventilation on CO₂", saving: round(eui * gfa * 0.025 * 0.18, 0), detail: "Several zones < 600 ppm: OA can be reduced while meeting ASHRAE 62.1 Rp." },
  ];
  return {
    zones, energy,
    kpis: { eui: round(eui * (0.95 + R() * 0.1), 1), comfort: round(100 - (hot / zones.length) * 100, 0), anomalies, savingsPotential: round(recommendations.reduce((s, r) => s + r.saving, 0), 0) },
    recommendations,
  };
}
