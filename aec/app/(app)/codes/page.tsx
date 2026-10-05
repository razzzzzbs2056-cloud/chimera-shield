import { Container, PageHeader } from "@/components/page";
import { StandardsManager } from "@/components/standards-manager";
import { requireUser } from "@/lib/auth";
import { standards } from "@/lib/repo";

export const metadata = { title: "Code library" };

export default async function Codes() {
  await requireUser();
  const list = standards() as (ReturnType<typeof standards>[number] & { id: string })[];
  return (
    <Container>
      <PageHeader title="Code library" subtitle="Versioned standards per jurisdiction. Every project run resolves applicable codes from here and warns when a pinned edition is superseded." />
      <StandardsManager initial={list} />
    </Container>
  );
}
