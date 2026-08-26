import { api, GlacierReport } from "@/lib/api";
import { RiskGauge, ComponentBreakdown } from "../../components/RiskGauge";
import { FreshnessBadge, ConfidenceBadge, LiveOrDelayed } from "../../components/Badges";
import { ProvenanceFooter } from "../../components/Provenance";

export const dynamic = "force-dynamic";

async function safeReport(id: string): Promise<GlacierReport | null> {
  try {
    return await api.glacier(id);
  } catch {
    return null;
  }
}

export default async function GlacierDetail({ params }: { params: { id: string } }) {
  const r = await safeReport(params.id);
  if (!r) {
    return (
      <div className="container">
        <div className="notice">
          Could not load <b>{params.id}</b> from the backend. No data is fabricated in its place.
        </div>
      </div>
    );
  }

  const g = r.glacier;
  const t = r.temperature || {};
  const st = r.surface_temperature || {};
  const fl = r.freezing_level || {};
  const pdd = r.pdd || {};
  const eq = r.earthquakes || {};
  const s1 = r.satellite?.sentinel1 || {};
  const s2 = r.satellite?.sentinel2 || {};

  return (
    <div className="container">
      <div className="row between" style={{ marginBottom: 8 }}>
        <div>
          <h2 style={{ fontSize: 22, margin: 0 }}>{g.name}</h2>
          <div className="dim small mono">
            {g.latitude}, {g.longitude} · terminus {g.terminus_elevation_m} m · median{" "}
            {g.median_elevation_m} m · {g.river_system}
          </div>
          <div className="dim small">{g.geometry_note}</div>
        </div>
        <a href="/" className="mono small">
          ← overview
        </a>
      </div>

      {/* RISK + ANALYST */}
      <div className="grid cols-2">
        <div className="panel">
          <h2>Risk Engine</h2>
          <RiskGauge
            score={r.risk.glacier_risk_score_0_100}
            level={r.risk.risk_level}
            confidence={r.risk.confidence}
          />
          <div style={{ marginTop: 16 }}>
            <ComponentBreakdown components={r.risk.components} />
          </div>
        </div>

        <div className="panel">
          <h2>AI Analyst — evidence fusion</h2>
          <div className="assessment">{r.analyst.assessment}</div>
          <div style={{ marginTop: 12 }}>
            {r.analyst.evidence.map((e, i) => (
              <div className="evidence-item" key={i}>
                <div className="label">{e.label}</div>
                <div className="value">{e.value}</div>
                {e.anomaly && <div className="dim small mono">{e.anomaly}</div>}
                {e.association && <div className="dim small mono">assoc: {e.association}</div>}
              </div>
            ))}
          </div>
          <div className="disclaimer">{r.analyst.disclaimer}</div>
        </div>
      </div>

      {/* DATA CARDS */}
      <div className="grid cols-3" style={{ marginTop: 16 }}>
        {/* Air temperature */}
        <div className="panel">
          <div className="row between">
            <h2>Air Temperature</h2>
            <LiveOrDelayed freshness={t.freshness} />
          </div>
          <div className="metric">
            <span className="big">{t.current_glacier_air_temp_c ?? "UNKNOWN"}</span>
            <span className="unit">°C</span>
          </div>
          <div className="dim small">
            elevation-adjusted estimate · anomaly {sign(t.anomaly_c)} °C · trend{" "}
            {t.trend_c_per_day ?? "—"} °C/day
          </div>
          <div className="row wrap" style={{ marginTop: 8, gap: 6 }}>
            <FreshnessBadge freshness={t.freshness} />
          </div>
          {t.elevation_correction && (
            <div className="dim small mono" style={{ marginTop: 8 }}>
              lapse {t.elevation_correction.lapse_rate_c_per_m
                ? (t.elevation_correction.lapse_rate_c_per_m * 1000).toFixed(1)
                : "—"}{" "}
              °C/km over {t.elevation_correction.elevation_difference_m} m (estimated)
            </div>
          )}
          <ProvenanceFooter
            source="Open-Meteo / ERA5 (model)"
            kind="elevation_adjusted"
            resolution="~11 km grid"
            confidence={t.freshness ? undefined : "UNKNOWN"}
            age={t.freshness?.age_human}
          />
        </div>

        {/* Surface temperature — SEPARATE from air */}
        <div className="panel">
          <div className="row between">
            <h2>Surface Temperature (skin)</h2>
          </div>
          <div className="metric">
            <span className="big">{st.value ?? "UNKNOWN"}</span>
            <span className="unit">°C</span>
          </div>
          <div className="dim small">
            {st.note || "Satellite LST — not air temperature"}
          </div>
          <ProvenanceFooter
            source="VIIRS LST (measured)"
            kind={st.kind}
            resolution="750 m"
            confidence={st.confidence}
            age={st.freshness?.age_human}
          />
        </div>

        {/* Freezing level */}
        <div className="panel">
          <h2>Freezing Level</h2>
          <div className="metric">
            <span className="big">{fl.current_m ?? "UNKNOWN"}</span>
            <span className="unit">m</span>
          </div>
          <div className="dim small">
            glacier terminus {fl.glacier_terminus_m ?? g.terminus_elevation_m} m · median{" "}
            {fl.glacier_median_m ?? g.median_elevation_m} m
          </div>
          <div className="dim small mono" style={{ marginTop: 6 }}>
            hrs above median (7d): {fl.hours_above_median_7d ?? "—"}
          </div>
        </div>

        {/* PDD */}
        <div className="panel">
          <h2>Melt Pressure (PDD)</h2>
          <div className="metric">
            <span className="big">{pdd.pdd_30d_cumulative ?? "UNKNOWN"}</span>
            <span className="unit">°C·d / 30d</span>
          </div>
          <div className="dim small">
            anomaly {sign(pdd.anomaly_30d_pct)} % vs seasonal normal
          </div>
          <div className="dim small">{pdd.caveat}</div>
        </div>

        {/* Earthquakes */}
        <div className="panel">
          <div className="row between">
            <h2>Earthquakes</h2>
            <FreshnessBadge freshness={eq.freshness} />
          </div>
          {eq.latest ? (
            <>
              <div className="metric">
                <span className="big">M{eq.latest.magnitude}</span>
                <span className="unit">{eq.latest.distance_km} km</span>
              </div>
              <div className="dim small mono">assoc: {eq.association}</div>
            </>
          ) : (
            <div className="dim">
              {eq.count_30d === 0 ? "No M≥2.5 events in 30d / radius" : "UNKNOWN"}
            </div>
          )}
          <div className="dim small">{eq.caveat}</div>
          <ProvenanceFooter
            source="USGS (measured)"
            resolution="point"
            confidence={eq.confidence}
            age={eq.freshness?.age_human}
          />
        </div>

        {/* Satellite */}
        <div className="panel">
          <h2>Satellite Coverage</h2>
          <div className="row between" style={{ marginTop: 4 }}>
            <span className="dim small">Sentinel-1 SAR</span>
            <FreshnessBadge freshness={s1.freshness} />
          </div>
          <div className="row between" style={{ marginTop: 8 }}>
            <span className="dim small">Sentinel-2 optical</span>
            <FreshnessBadge freshness={s2.freshness} />
          </div>
          {s2.latest_cloud_cover_pct != null && (
            <div className="dim small mono" style={{ marginTop: 8 }}>
              cloud cover {s2.latest_cloud_cover_pct}%{" "}
              {s2.change_pair_valid === false && "· optical change not valid (cloud)"}
            </div>
          )}
          {!s1.available && (
            <div className="dim small" style={{ marginTop: 8 }}>
              {s1.note}
            </div>
          )}
        </div>
      </div>

      {/* Downstream */}
      <div className="panel" style={{ marginTop: 16 }}>
        <h2>Downstream exposure (reference)</h2>
        <div className="row wrap" style={{ gap: 8 }}>
          {(r.downstream || []).map((d: any) => (
            <span className="badge" key={d.id}>
              {d.name} · {d.kind} · {d.elevation_m} m
            </span>
          ))}
          {(!r.downstream || r.downstream.length === 0) && (
            <span className="dim small">none in reference set</span>
          )}
        </div>
        <div className="dim small" style={{ marginTop: 8 }}>
          Coarse river-system relationship; full routing requires DEM flow tracing.
        </div>
      </div>
    </div>
  );
}

function sign(v: number | null | undefined) {
  if (v === null || v === undefined) return "UNKNOWN";
  return (v >= 0 ? "+" : "") + v;
}
