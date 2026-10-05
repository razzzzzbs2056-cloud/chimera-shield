// Wind engine: ASCE 7-22 Ch. 26-27/30 directional procedure with the
// §26.11.5 gust-effect factor for flexible buildings, serviceability
// accelerations, vortex-shedding screening, façade (C&C) pressures and a
// pedestrian-comfort screen. Not a substitute for CFD or wind-tunnel testing.

import { round } from "./linalg";
import type { Derived } from "./site";
import type { DesignParams, Intake } from "./types";

const EXPO = {
  B: { alpha: 7.5, zg: 1000, ab: 1 / 4, bb: 0.45, c: 0.3, l: 97.54, eps: 1 / 3 },
  C: { alpha: 9.8, zg: 750, ab: 1 / 6.5, bb: 0.65, c: 0.2, l: 152.4, eps: 1 / 5 },
  D: { alpha: 11.5, zg: 590, ab: 1 / 9, bb: 0.8, c: 0.15, l: 198.12, eps: 1 / 8 },
};

export const Kz = (z: number, exp: "B" | "C" | "D") => {
  const e = EXPO[exp];
  return 2.41 * (Math.max(z, 4.6) / e.zg) ** (2 / e.alpha);
};

export interface WindResult {
  V: number; exposure: string; Kd: number; qh: number; n1: number; flexible: boolean; G: number;
  gustDetail: { Iz: number; Lz: number; Q: number; R: number; gR: number; Vz: number };
  stories: { level: number; z: number; Kz: number; qz: number; pw: number; pl: number; F: number; V: number }[];
  baseShear: number; baseMoment: number;
  accel: { peak: number; limit: number; mg: number; V10: number };
  vortex: { St: number; vcrit: number; vm: number; check: boolean };
  facade: { zone: string; pos: number; neg: number }[];
  pedestrian: { location: string; speed: number; category: string }[];
  heatmap: { face: string; z: number; p: number }[];
}

export function windAnalysis(intake: Intake, d: Derived, p: DesignParams, n1: number, damping: number): WindResult {
  const exp = intake.exposure;
  const e = EXPO[exp];
  const V = intake.basicWindSpeed;
  const Kd = 0.85, Kzt = 1, Ke = 1;
  const H = d.height, B = d.Ly, L = d.Lx; // wind along X: B is width normal to wind
  const q = (z: number) => (0.613 * Kz(z, exp) * Kzt * Ke * V * V) / 1000; // kPa, Eq. 26.10-1
  const qh = q(H);

  // Gust effect factor
  const zbar = Math.max(0.6 * H, 4.6);
  const Iz = e.c * (10 / zbar) ** (1 / 6);
  const Lz = e.l * (zbar / 10) ** e.eps;
  const Q = Math.sqrt(1 / (1 + 0.63 * ((B + H) / Lz) ** 0.63));
  const gQ = 3.4, gv = 3.4;
  const flexible = n1 < 1;
  const Vz = e.bb * (zbar / 10) ** e.ab * V;
  let Gf = 0.925 * ((1 + 1.7 * gQ * Iz * Q) / (1 + 1.7 * gv * Iz));
  let R = 0, gR = 0;
  if (flexible) {
    const N1 = (n1 * Lz) / Vz;
    const Rn = (7.47 * N1) / (1 + 10.3 * N1) ** (5 / 3);
    const Rl = (eta: number) => (eta > 0 ? 1 / eta - (1 / (2 * eta * eta)) * (1 - Math.exp(-2 * eta)) : 1);
    const Rh = Rl((4.6 * n1 * H) / Vz), RB = Rl((4.6 * n1 * B) / Vz), RL = Rl((15.4 * n1 * L) / Vz);
    R = Math.sqrt((1 / damping) * Rn * Rh * RB * (0.53 + 0.47 * RL));
    gR = Math.sqrt(2 * Math.log(3600 * n1)) + 0.577 / Math.sqrt(2 * Math.log(3600 * n1));
    Gf = 0.925 * ((1 + 1.7 * Iz * Math.sqrt(gQ * gQ * Q * Q + gR * gR * R * R)) / (1 + 1.7 * gv * Iz));
  } else {
    Gf = Math.max(0.85, Gf);
  }
  const LB = L / B;
  const Cpl = LB <= 1 ? -0.5 : LB <= 2 ? -0.5 + 0.2 * (LB - 1) : LB <= 4 ? -0.3 + 0.05 * (LB - 2) : -0.2;
  let cum = 0;
  const stories = d.storyHeights.map((h, i) => {
    const z = d.levelZ[i + 1];
    const hTrib = (h + (d.storyHeights[i + 1] ?? 0)) / 2;
    const pw = q(z) * Kd * Gf * 0.8;
    const pl = qh * Kd * Gf * Cpl;
    const F = (pw - pl) * B * hTrib;
    return { level: i + 1, z, Kz: round(Kz(z, exp), 3), qz: round(q(z), 3), pw: round(pw, 3), pl: round(pl, 3), F, V: 0 };
  });
  for (let i = stories.length - 1; i >= 0; i--) { cum += stories[i].F; stories[i].V = cum; }
  const baseShear = cum;
  const baseMoment = stories.reduce((s, st) => s + st.F * st.z, 0);

  // Serviceability acceleration (ASCE 7-22 commentary C26.11, 10-year wind ≈ 0.74·V700 → use 0.62·V)
  const V10 = 0.62 * V;
  const Vz10 = e.bb * (zbar / 10) ** e.ab * V10;
  const massPerH = (d.plateArea * (0.25 * 24 + 2.0)) / p.floorHeight; // t-ish per m, kN/m ÷ g below
  const mu = massPerH / 9.81; // tonnes/m
  const m1 = (mu * H) / 3; // ∫ μ φ² dz with φ = z/H
  const K = 1.65 ** e.ab / (e.ab + 1 + 1);
  let peak = 0;
  if (n1 > 0) {
    const N1 = (n1 * Lz) / Vz10;
    const Rn = (7.47 * N1) / (1 + 10.3 * N1) ** (5 / 3);
    const Rl = (eta: number) => (eta > 0 ? 1 / eta - (1 / (2 * eta * eta)) * (1 - Math.exp(-2 * eta)) : 1);
    const R10 = Math.sqrt((1 / damping) * Rn * Rl((4.6 * n1 * H) / Vz10) * Rl((4.6 * n1 * B) / Vz10) * (0.53 + 0.47 * Rl((15.4 * n1 * L) / Vz10)));
    const sigma = (0.85 * 1.225e-3 * B * H * 1.3 * Vz10 * Vz10 * Iz * K * R10) / m1; // m/s²
    const g10 = Math.sqrt(2 * Math.log(600 * n1)) + 0.577 / Math.sqrt(2 * Math.log(600 * n1));
    peak = g10 * sigma;
  }
  const limit = ["residential", "hotel", "hospital"].includes(intake.buildingType) ? 0.15 : 0.2;

  // Vortex shedding (EN 1991-1-4 Annex E screening)
  const St = 0.12;
  const vcrit = (n1 * Math.min(B, L)) / St;
  const vm = e.bb * (H / 10) ** e.ab * V * 0.75;

  // C&C pressures (ASCE 7-22 Fig. 30.4-1 / h > 18.3 m approximations, effective area ≥ 1 m²)
  const qhn = qh * Kd;
  const facade = [
    { zone: "Zone 4 (field)", pos: round(qhn * 0.9 + qhn * 0.18, 2), neg: round(-(qhn * 0.9 + qhn * 0.18), 2) },
    { zone: "Zone 5 (corner, a = 0.1·least width)", pos: round(qhn * 0.9 + qhn * 0.18, 2), neg: round(-(qhn * 1.8 + qhn * 0.18), 2) },
    { zone: "Roof field", pos: 0, neg: round(-(qhn * 1.4 + qhn * 0.18), 2) },
    { zone: "Roof corner", pos: 0, neg: round(-(qhn * 2.3 + qhn * 0.18), 2) },
  ];

  // Pedestrian comfort screen (Lawson LDDC, 5 % exceedance)
  const vRef = 0.18 * V;
  const amp = (k: number) => Math.min(2.2, Math.max(1, k + H / 160));
  const cat = (v: number) => (v < 4 ? "Sitting" : v < 6 ? "Standing" : v < 8 ? "Walking" : v < 10 ? "Uncomfortable" : "Unsafe");
  const pedestrian = [
    { location: "Main entrance (leeward, canopy)", k: 0.75 },
    { location: "Windward corner", k: 1.2 },
    { location: "Side façade passage", k: 1.05 },
    { location: "Podium roof terrace", k: 0.95 },
  ].map(({ location, k }) => {
    const v = vRef * amp(k);
    return { location, speed: round(v, 1), category: cat(v) };
  });

  const heatmap: WindResult["heatmap"] = [];
  const zs = [0.1, 0.3, 0.5, 0.7, 0.9, 1].map((f) => f * H);
  for (const z of zs) {
    heatmap.push({ face: "Windward", z: round(z, 1), p: round(q(z) * Kd * Gf * 0.8, 2) });
    heatmap.push({ face: "Side", z: round(z, 1), p: round(qh * Kd * Gf * -0.7, 2) });
    heatmap.push({ face: "Leeward", z: round(z, 1), p: round(qh * Kd * Gf * Cpl, 2) });
    heatmap.push({ face: "Corner", z: round(z, 1), p: round(-(qhn * 1.8 + qhn * 0.18), 2) });
  }

  return {
    V, exposure: exp, Kd, qh: round(qh, 3), n1: round(n1, 3), flexible, G: round(Gf, 3),
    gustDetail: { Iz: round(Iz, 3), Lz: round(Lz, 1), Q: round(Q, 3), R: round(R, 3), gR: round(gR, 2), Vz: round(Vz, 1) },
    stories, baseShear, baseMoment,
    accel: { peak: round(peak, 3), limit, mg: round((peak / 9.81) * 1000, 1), V10: round(V10, 1) },
    vortex: { St, vcrit: round(vcrit, 1), vm: round(vm, 1), check: vcrit <= 1.25 * vm },
    facade, pedestrian, heatmap,
  };
}
