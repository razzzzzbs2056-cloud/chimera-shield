"use client";

import clsx from "clsx";
import { Play } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { AgentProgress } from "./agent-progress";
import { api, Button, useToast } from "./ui";

export const PROJECT_TABS = [
  { slug: "", label: "Overview" }, { slug: "brief", label: "Brief" }, { slug: "agents", label: "Agents" }, { slug: "design", label: "Design" },
  { slug: "structure", label: "Structure" }, { slug: "seismic-wind", label: "Seismic & Wind" }, { slug: "geotech", label: "Geotech" }, { slug: "mep", label: "MEP" },
  { slug: "fire", label: "Fire & Access" }, { slug: "envelope", label: "Envelope & Energy" }, { slug: "sustainability", label: "Carbon & Resilience" },
  { slug: "compliance", label: "Compliance" }, { slug: "bim", label: "BIM & Clashes" }, { slug: "drawings", label: "Drawings & Specs" },
  { slug: "cost", label: "Cost & BOQ" }, { slug: "construction", label: "Construction" }, { slug: "operations", label: "Operations" },
  { slug: "verification", label: "Verification" }, { slug: "assistant", label: "Assistant" },
];

export function ProjectNav({ id }: { id: string }) {
  const path = usePathname();
  const base = `/projects/${id}`;
  return (
    <nav className="scrollbar-thin -mb-px flex gap-1 overflow-x-auto" aria-label="Project sections">
      {PROJECT_TABS.map((t) => {
        const href = t.slug ? `${base}/${t.slug}` : base;
        const active = t.slug ? path.startsWith(href) : path === base;
        return (
          <Link key={t.slug} href={href} className={clsx("whitespace-nowrap border-b-2 px-2.5 py-2.5 text-sm font-medium transition", active ? "border-brand-600 text-brand-700" : "border-transparent text-slate-500 hover:border-slate-300 hover:text-slate-800")}>
            {t.label}
          </Link>
        );
      })}
    </nav>
  );
}

export function RunButton({ id, label = "Run workflow" }: { id: string; label?: string }) {
  const [busy, setBusy] = useState(false);
  const router = useRouter();
  const toast = useToast();
  async function run() {
    setBusy(true);
    try {
      const r = await api<{ kpis: { pass: number; fail: number; clashes: number }; durationMs: number; changes: unknown[] }>(`/api/projects/${id}/run`, { method: "POST" });
      toast({ tone: "success", text: `Workflow complete in ${(r.durationMs / 1000).toFixed(1)} s — ${r.kpis.pass} pass, ${r.kpis.fail} fail, ${r.changes.length} agent design changes` });
      router.refresh();
    } catch (e) {
      toast({ tone: "error", text: (e as Error).message });
    } finally { setBusy(false); }
  }
  return (
    <>
      {busy && <AgentProgress />}
      <Button onClick={run} loading={busy}>{!busy && <Play className="h-4 w-4" />}{label}</Button>
    </>
  );
}
