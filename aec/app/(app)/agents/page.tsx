import { headers } from "next/headers";
import Link from "next/link";
import { AgentCatalog } from "@/components/agent-catalog";
import { Container, PageHeader } from "@/components/page";
import { requireUser } from "@/lib/auth";
import { AGENTS } from "@/lib/agent-catalog";

export const metadata = { title: "Agent catalog" };

export default async function AgentsPage() {
  await requireUser();
  const h = await headers();
  const origin = `${h.get("x-forwarded-proto") ?? "http"}://${h.get("host") ?? "localhost:3100"}`;
  const skills = AGENTS.reduce((s, a) => s + a.skills.length, 0);
  return (
    <Container>
      <PageHeader eyebrow="Product" title="Agent catalog" subtitle={`${AGENTS.length} specialist agents · ${skills} engineering skills · every agent available in the app, through the API and as a Claude Skill.`}
        actions={<Link href="/sell" className="inline-flex items-center rounded-lg bg-brand-600 px-3.5 py-2 text-sm font-medium text-white shadow-sm hover:bg-brand-700">Where to sell them →</Link>} />
      <AgentCatalog agents={AGENTS} origin={origin} />
    </Container>
  );
}
