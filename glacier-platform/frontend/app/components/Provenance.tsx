// Renders the mandatory provenance line: source + acquisition + processing +
// resolution + confidence + age. Used at the foot of every data card.
export function ProvenanceFooter(props: {
  source?: string | null;
  acquisition?: string | null;
  processing?: string | null;
  resolution?: string | number | null;
  confidence?: string;
  age?: string | null;
  kind?: string | null;
}) {
  return (
    <div className="provenance">
      <span>
        <b>source:</b> {props.source || "—"}
      </span>
      {props.kind && (
        <span>
          <b>kind:</b> {props.kind}
        </span>
      )}
      <span>
        <b>acquired:</b> {props.acquisition || "unknown"}
      </span>
      <span>
        <b>processed:</b> {props.processing || "—"}
      </span>
      <span>
        <b>res:</b> {props.resolution ?? "—"}
      </span>
      <span>
        <b>conf:</b> {props.confidence || "UNKNOWN"}
      </span>
      <span>
        <b>age:</b> {props.age || "unknown"}
      </span>
    </div>
  );
}
