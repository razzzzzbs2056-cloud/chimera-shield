import { num } from "./api";
import type { BoreholeLayer, SoilType } from "./engine/types";

const SOILS: SoilType[] = ["fill", "clay", "silt", "sand", "gravel", "rock"];

export function cleanLayers(raw: unknown): BoreholeLayer[] {
  if (!Array.isArray(raw) || raw.length === 0) throw new Error("At least one soil layer is required");
  const layers = raw.map((l: Record<string, unknown>) => {
    const soil = SOILS.includes(l.soil as SoilType) ? (l.soil as SoilType) : "sand";
    const top = num(l.top, 0, 200), bottom = num(l.bottom, 0, 200);
    if (top === null || bottom === null || bottom <= top) throw new Error("Each layer needs top < bottom (m)");
    return {
      top, bottom, soil, spt: num(l.spt, 0, 100) ?? 10, gamma: num(l.gamma, 10, 26) ?? 18,
      cu: soil === "clay" || soil === "silt" ? num(l.cu, 5, 1000) ?? 50 : undefined, phi: soil !== "clay" ? num(l.phi, 0, 50) ?? 30 : undefined,
      Es: num(l.Es, 1, 5000) ?? 20, cc: soil === "clay" ? num(l.cc, 0.01, 2) ?? 0.3 : undefined, e0: soil === "clay" ? num(l.e0, 0.2, 4) ?? 1 : undefined,
      finesPct: num(l.finesPct, 0, 100) ?? undefined,
    };
  }).sort((a, b) => a.top - b.top);
  return layers;
}

