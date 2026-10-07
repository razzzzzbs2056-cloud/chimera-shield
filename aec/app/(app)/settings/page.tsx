import { ApiKeys } from "@/components/api-keys";
import { Container, PageHeader } from "@/components/page";
import { SettingsForm } from "@/components/settings-form";
import { listApiKeys, MONTHLY_RUN_LIMIT } from "@/lib/api-keys";
import { requireUser } from "@/lib/auth";

export const metadata = { title: "Settings" };

export default async function Settings() {
  const user = await requireUser();
  return (
    <Container>
      <PageHeader title="Settings" subtitle="Your profile, security, API keys and integrations." />
      <SettingsForm user={{ name: user.name, email: user.email, role: user.role, company: user.company }} claudeEnabled={!!(process.env.ANTHROPIC_API_KEY || process.env.ANTHROPIC_AUTH_TOKEN)} />
      <ApiKeys initial={listApiKeys(user.id)} limit={MONTHLY_RUN_LIMIT} />
    </Container>
  );
}
