import { Cpu } from "lucide-react";
import { EmptyState } from "./ui";
import { RunButton } from "./project-nav";

export function NoRun({ id }: { id: string }) {
  return <EmptyState icon={Cpu} title="No analysis yet" body="Run the multi-agent workflow to generate structural, MEP, compliance, BIM, cost and construction results." action={<RunButton id={id} />} />;
}
