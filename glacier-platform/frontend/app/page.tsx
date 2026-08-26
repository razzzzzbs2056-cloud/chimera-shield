import { api, GlacierSummary, GlacierReport } from "@/lib/api";
import { levelColor } from "./components/RiskGauge";
import { FreshnessBadge, ConfidenceBadge } from "./components/Badges";

export const dynamic = "force-dynamic";

async function safeGlaciers(): Promise<GlacierSummary[]> {
  try {
    return await api.glaciers();
  } catch {
    return [];
  }
}

async function safeReport(id: string): Promise<GlacierReport | null> {
  try {
    return await api.glacier(id);
  } catch {
    return null;
  }
}

export default async function Overview() {
  const glaciers = await safeGlaciers();
  const reports = await Promise.all(glaciers.map((g) => safeReport(g.id)));

  return (
    <div className="container">
      {glaciers.length === 0 && (
        <div className="notice" style={{ marginBottom: 16 }}>
          No data from the backend API at <span className="mono">{process.env.NEXT_PUBLIC_API_BASE}</span>.
          Start the backend (see README) — this page never invents glaciers or measurements.
        </div>
      )}

      <div className="grid cols-3">
        {glaciers.map((g, i) => {
          const r = reports[i];
          const risk = r?.risk;
          const level = risk?.risk_level || "UNKNOWN";
          const score = risk?.glacier_risk_score_0_100 ?? null;
          const tempFresh = r?.temperature?.freshness;
          return (
            <a className="glacier-card" key={g.id} href={`/glacier/${g.id}`}>
              <div className="row between">
                <div>
                  <div style={{ fontSize: 16, fontWeight: 600 }}>{g.name}</div>
                  <div className="dim small mono">
                    {g.latitude.toFixed(3)}, {g.longitude.toFixed(3)} · {g.catchment}
                  </div>
                </div>
                <span
                  className="level-pill"
                  style={{ background: levelColor(level) + "22", color: levelColor(level) }}
                >
                  {score ?? "—"}
                </span>
              </div>

              <div style={{ marginTop: 12 }} className="row between">
                <span className="dim small">RISK</span>
                <span style={{ color: levelColor(level), fontWeight: 600 }} className="mono">
                  {level}
                </span>
              </div>
              <div className="row between" style={{ marginTop: 6 }}>
                <span className="dim small">AIR TEMP (adj. est.)</span>
                <span className="mono">
                  {r?.temperature?.current_glacier_air_temp_c ?? "UNKNOWN"} °C
                </span>
              </div>
              <div className="row between" style={{ marginTop: 6 }}>
                <span className="dim small">ANOMALY</span>
                <span className="mono">
                  {fmtSigned(r?.temperature?.anomaly_c)} °C
                </span>
              </div>

              <div className="row wrap" style={{ marginTop: 12, gap: 6 }}>
                <FreshnessBadge freshness={tempFresh} />
                <ConfidenceBadge value={risk?.confidence} />
              </div>
            </a>
          );
        })}
      </div>

      <div className="disclaimer" style={{ marginTop: 20 }}>
        All figures are experimental hazard indicators derived from cited sources with
        stated confidence and age. Nothing here is an official warning or a prediction of
        when any event will occur.
      </div>
    </div>
  );
}

function fmtSigned(v: number | null | undefined) {
  if (v === null || v === undefined) return "UNKNOWN";
  return (v >= 0 ? "+" : "") + v;
}
