import { Shell } from "@/components/shell";
import { requireUser } from "@/lib/auth";
import { listProjects } from "@/lib/repo";

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const user = await requireUser();
  const recent = listProjects(user.id).slice(0, 8).map((p) => ({ id: p.id, name: p.name, code: p.code, fail: p.kpis?.fail ?? 0 }));
  return <Shell user={{ name: user.name, email: user.email, role: user.role }} recent={recent}>{children}</Shell>;
}
