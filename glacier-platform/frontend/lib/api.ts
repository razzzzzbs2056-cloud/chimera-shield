// Typed API client for the Glacier Intelligence backend.
// Every server value carries provenance/freshness/confidence; the UI surfaces
// those on every card and never presents a value without them.

export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export interface Freshness {
  age_seconds: number | null;
  age_human: string;
  status: "FRESH" | "DELAYED" | "STALE" | "UNKNOWN";
  color: string;
  is_live: boolean;
}

export interface GlacierSummary {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  catchment: string;
  river_system: string;
  monitor_radius_km: number;
}

export interface RiskFactor {
  factor: string;
  value: number | null;
  unit: string | null;
  source: string | null;
  subscore_0_100: number | null;
  weight: number;
  contribution: number | null;
  confidence: string;
  age_seconds: number | null;
  available: boolean;
  note?: string | null;
}

export interface RiskComponent {
  component: string;
  score_0_100: number | null;
  level: string;
  confidence: string;
  coverage: number;
  factors: RiskFactor[];
}

export interface GlacierReport {
  generated_at: string;
  glacier: any;
  weather_available: boolean;
  climatology: any;
  temperature: any;
  pdd: any;
  freeze_thaw: any;
  freezing_level: any;
  precipitation: any;
  surface_temperature: any;
  earthquakes: any;
  satellite: any;
  lake: any;
  velocity: any;
  downstream: any[];
  risk: {
    glacier_risk_score_0_100: number | null;
    risk_level: string;
    confidence: string;
    component_weights: Record<string, number>;
    components: RiskComponent[];
    disclaimer: string;
  };
  analyst: {
    headline: string;
    evidence: { label: string; value: string; [k: string]: any }[];
    assessment: string;
    disclaimer: string;
  };
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`${path} -> ${res.status}`);
  return res.json();
}

export const api = {
  glaciers: () => get<GlacierSummary[]>("/glaciers"),
  glacier: (id: string) => get<GlacierReport>(`/glaciers/${id}`),
  alerts: () => get<{ count: number; alerts: any[] }>("/alerts"),
  config: () => get<any>("/config"),
};
