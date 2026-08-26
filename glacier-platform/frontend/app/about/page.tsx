export const dynamic = "force-dynamic";

const RULES = [
  "Never present delayed satellite data as live. 'LIVE' appears only when a source is near-real-time and its latest timestamp is within minutes.",
  "Every observation carries source, acquisition time, processing time, spatial resolution, confidence, and age of data.",
  "Missing or unavailable data is shown as UNKNOWN — never replaced with an invented number.",
  "Air (2 m) temperature and satellite surface/skin temperature are stored and displayed separately.",
  "Weather-model output is labelled model; forecasts are labelled forecast; neither is presented as a thermometer measurement.",
  "Elevation-adjusted glacier temperatures are labelled estimated, not measured, with the lapse-rate assumption shown.",
  "Correlation is never presented as causation. An earthquake near a glacier is an association, never a stated cause of an avalanche.",
  "A decrease in lake area is never by itself called a GLOF. A possible river blockage is always 'requires verification', never a confirmed dam.",
  "Cloud-obscured optical pixels are never treated as confirmed surface change.",
  "Risk scores are experimental hazard indicators — not predictions and not official evacuation warnings.",
  "The risk model is a transparent weighted blend, not a blind average: every factor shows its value, source, weight, contribution, confidence, and age.",
];

export default function About() {
  return (
    <div className="container">
      <div className="panel">
        <h2>Method & Scientific Integrity</h2>
        <p className="dim" style={{ lineHeight: 1.6 }}>
          This platform continuously fuses satellite, meteorological, seismic and
          hydrological data into evidence-grounded glacier hazard indicators for the
          Nepal–Tibet Himalayan border. Its core promise is honesty about what is known,
          how well, and how recently.
        </p>
        <ol style={{ lineHeight: 1.7 }}>
          {RULES.map((r, i) => (
            <li key={i} style={{ marginBottom: 8 }}>
              {r}
            </li>
          ))}
        </ol>
      </div>

      <div className="panel" style={{ marginTop: 16 }}>
        <h2>Data pipeline</h2>
        <div className="mono small" style={{ lineHeight: 1.9, color: "var(--text-dim)" }}>
          Satellite&nbsp;→&nbsp;Weather + Temperature&nbsp;→&nbsp;Change detection&nbsp;→&nbsp;
          Lake monitoring&nbsp;→&nbsp;Slope monitoring&nbsp;→&nbsp;Earthquakes&nbsp;→&nbsp;
          Hydrology&nbsp;→&nbsp;AI evidence fusion&nbsp;→&nbsp;Risk engine&nbsp;→&nbsp;
          3D Earth&nbsp;→&nbsp;Alerts
        </div>
      </div>
    </div>
  );
}
