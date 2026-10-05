import { Container, PageHeader } from "@/components/page";
import { IntakeForm } from "@/components/intake-form";

export const metadata = { title: "New project" };

export default function NewProject() {
  return (
    <Container>
      <PageHeader eyebrow="Project intake engine" title="New project" subtitle="Describe the site, brief and targets. A parametric scheme is generated and routed to the specialist agents automatically." />
      <IntakeForm mode="create" />
    </Container>
  );
}
