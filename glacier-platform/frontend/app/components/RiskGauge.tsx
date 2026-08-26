import { RiskComponent } from "@/lib/api";

const LEVEL_COLOR: Record<string, string> = {
  LOW: "#2ecc71",
  WATCH: "#a3d977",
  ELEVATED: "#f1c40f",
  HIGH: "#e67e22",
  "CRITICAL INVESTIGATION": "#e74c3c",
  UNKNOWN: "#7f8c8d",
};

export function levelColor(level: string) {
  return LEVEL_COLOR[level] || "#7f8c8d";
}

export function RiskGauge({
  score,
  level,
  confidence,
}: {
  score: number | null;
  level: string;
  confidence: string;
}) {
  const color = levelColor(level);
  return (
    <div className="gauge-wrap">
      <div
        className="gauge"
        style={
          {
            ["--v" as any]: score ?? 0,
            ["--gcolor" as any]: color,
          } as React.CSSProperties
        }
      >
        <span className="val">{score ?? "—"}</span>
      </div>
      <div>
        <div className="dim small">GLACIER RISK INDICATOR</div>
        <div style={{ fontSize: 22, fontWeight: 600, color }}>{level}</div>
        <div className="dim small mono">confidence: {confidence}</div>
        <div className="disclaimer" style={{ maxWidth: 260 }}>
          Experimental hazard indicator — NOT an official evacuation warning.
        </div>
      </div>
    </div>
  );
}

export function ComponentBreakdown({ components }: { components: RiskComponent[] }) {
  return (
    <div>
      {components.map((c) => (
        <details key={c.component} style={{ marginBottom: 8 }}>
          <summary className="row between" style={{ cursor: "pointer" }}>
            <span style={{ textTransform: "capitalize" }}>
              {c.component.replace(/_/g, " ")}
            </span>
            <span className="mono">
              <span style={{ color: levelColor(c.level) }}>
                {c.score_0_100 ?? "UNKNOWN"}
              </span>
              <span className="dim small">
                {" "}
                · {c.confidence} · cov {(c.coverage * 100).toFixed(0)}%
              </span>
            </span>
          </summary>
          <table className="factor-table">
            <thead>
              <tr>
                <th>Factor</th>
                <th>Value</th>
                <th>Source</th>
                <th style={{ textAlign: "right" }}>Weight</th>
                <th style={{ textAlign: "right" }}>Contribution</th>
                <th>Conf</th>
              </tr>
            </thead>
            <tbody>
              {c.factors.map((f) => (
                <tr key={f.factor} style={{ opacity: f.available ? 1 : 0.5 }}>
                  <td>{f.factor.replace(/_/g, " ")}</td>
                  <td className="num">
                    {f.value ?? "—"} {f.unit ?? ""}
                  </td>
                  <td className="dim">{f.source || "—"}</td>
                  <td className="num">{f.weight}</td>
                  <td className="num">
                    {f.available ? (
                      <div className="row" style={{ justifyContent: "flex-end", gap: 6 }}>
                        <div className="bar">
                          <span style={{ width: `${f.contribution ?? 0}%` }} />
                        </div>
                        {f.contribution ?? "—"}
                      </div>
                    ) : (
                      <span className="dim">excluded (no data)</span>
                    )}
                  </td>
                  <td className="dim">{f.confidence}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </details>
      ))}
    </div>
  );
}
