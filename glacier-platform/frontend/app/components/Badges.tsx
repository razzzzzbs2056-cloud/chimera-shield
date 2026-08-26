// Presentational badges for the mandatory metadata every observation carries.
import { Freshness } from "@/lib/api";

const CONF_COLOR: Record<string, string> = {
  HIGH: "#2ecc71",
  MEDIUM: "#f1c40f",
  LOW: "#e67e22",
  UNKNOWN: "#7f8c8d",
};

export function ConfidenceBadge({ value }: { value?: string }) {
  const v = (value || "UNKNOWN").toUpperCase();
  return (
    <span className="badge" title="Confidence in this value">
      <span className="dot" style={{ background: CONF_COLOR[v] || "#7f8c8d" }} />
      conf: {v}
    </span>
  );
}

export function FreshnessBadge({ freshness }: { freshness?: Freshness }) {
  if (!freshness) {
    return (
      <span className="badge">
        <span className="dot" style={{ background: "#7f8c8d" }} /> age: unknown
      </span>
    );
  }
  return (
    <span className="badge" title="Age of the underlying observation">
      <span className="dot" style={{ background: freshness.color }} />
      {freshness.status} · {freshness.age_human}
      {freshness.is_live ? " · LIVE" : ""}
    </span>
  );
}

// The strict rule: we only ever render "LIVE" when the backend confirms the
// source is near-real-time AND the timestamp supports it. Otherwise never.
export function LiveOrDelayed({ freshness }: { freshness?: Freshness }) {
  if (freshness?.is_live)
    return <span className="badge" style={{ color: "#2ecc71" }}>● LIVE</span>;
  return (
    <span className="badge dim">
      not live — {freshness ? freshness.status.toLowerCase() : "unknown"}
    </span>
  );
}
