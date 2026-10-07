import { Building2, Check, ExternalLink, KeyRound, ShieldCheck } from "lucide-react";
import Link from "next/link";
import { Container, Note, PageHeader, SectionTitle } from "@/components/page";
import { Badge, Card, Table } from "@/components/ui";
import { requireUser } from "@/lib/auth";
import { AGENTS, PLANS } from "@/lib/agent-catalog";
import { CHANNELS, LAUNCH_PLAN, READINESS, SEGMENTS } from "@/lib/gtm";

export const metadata = { title: "Sell agents" };

const name = (id: string) => (id === "all" ? "All agents" : AGENTS.find((a) => a.id === id)?.name ?? id);
const effortTone = { Low: "green", Medium: "amber", High: "red" } as const;

export default async function SellPage() {
  await requireUser();
  return (
    <Container>
      <PageHeader eyebrow="Go-to-market playbook" title="Where to sell these agents to businesses" subtitle="Buyer segments, sales channels and marketplaces, packaging and pricing, launch plan and what to have in place before the first contract." />

      <SectionTitle sub="Who pays, what hurts, and which agents to lead with">1 · Buyer segments</SectionTitle>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {SEGMENTS.map((s) => (
          <Card key={s.segment} title={s.segment} subtitle={`Economic buyer: ${s.buyer}`}>
            <p className="text-sm text-slate-600"><b className="text-slate-800">Pain:</b> {s.pain}</p>
            <p className="mt-2 text-sm text-slate-600"><b className="text-slate-800">Offer:</b> {s.offer}</p>
            <div className="mt-3 flex flex-wrap gap-1">{s.agents.map((a) => <Badge key={a}>{name(a)}</Badge>)}</div>
          </Card>
        ))}
      </div>

      <SectionTitle sub="Marketplaces, platforms, AI ecosystems, partners and direct sales — check each programme's current terms before applying">2 · Where to sell</SectionTitle>
      <Card pad={false}>
        <Table head={["Channel", "Reaches", "How to sell", "Package", "Lead agents", "Effort", "Time to revenue"]}>
          {CHANNELS.map((c) => (
            <tr key={c.name}>
              <td className="td min-w-[180px]"><div className="font-medium text-slate-900">{c.name}</div><Badge className="mt-1">{c.type}</Badge>{c.url && <a href={c.url} target="_blank" rel="noreferrer" className="mt-1 flex items-center gap-1 text-[11px] text-brand-700 hover:underline">{c.url.replace("https://", "")}<ExternalLink className="h-3 w-3" /></a>}</td>
              <td className="td min-w-[160px] text-xs">{c.who}</td>
              <td className="td min-w-[240px] text-xs">{c.howToSell}</td>
              <td className="td min-w-[140px] text-xs">{c.packageAs}</td>
              <td className="td min-w-[150px] text-xs">{c.agents.map(name).join(", ")}</td>
              <td className="td"><Badge tone={effortTone[c.effort]}>{c.effort}</Badge></td>
              <td className="td whitespace-nowrap text-xs">{c.timeToRevenue}</td>
            </tr>
          ))}
        </Table>
      </Card>

      <SectionTitle sub="Suggested list prices — validate with pilots before publishing">3 · Packaging & pricing</SectionTitle>
      <div className="grid gap-4 lg:grid-cols-3">
        {PLANS.map((p, i) => (
          <div key={p.tier} className={`card flex flex-col p-5 ${i === 1 ? "ring-2 ring-brand-500" : ""}`}>
            <div className="flex items-center justify-between"><h3 className="font-semibold">{p.tier}</h3>{i === 1 && <Badge tone="blue">Most firms start here</Badge>}</div>
            <div className="mt-2"><span className="text-3xl font-semibold tracking-tight">{p.price}</span> <span className="text-sm text-slate-500">{p.unit}</span></div>
            <p className="mt-1 text-xs text-slate-500">{p.for}</p>
            <ul className="mt-4 space-y-1.5">{p.includes.map((x) => <li key={x} className="flex gap-1.5 text-sm"><Check className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" />{x}</li>)}</ul>
            <div className="mt-4 border-t border-slate-100 pt-3 text-xs text-slate-500">Agents: {AGENTS.filter((a) => (p.tier === "Starter" ? a.tier === "Starter" : p.tier === "Professional" ? a.tier !== "Enterprise" : true)).length}</div>
          </div>
        ))}
      </div>
      <Card title="Other pricing models that work in AEC">
        <ul className="grid gap-2 text-sm text-slate-700 sm:grid-cols-2">
          <li><b>Per project / per tender</b> — contractors and developers buy by job (e.g. a flat fee per feasibility or bid).</li>
          <li><b>Metered API runs</b> — platforms and integrators pay per analysis via <code>/api/v1/analyze</code>.</li>
          <li><b>Per GFA</b> — owners relate to $/m² of building analysed.</li>
          <li><b>White-label licence</b> — resellers and consultancies rebrand the workspace for their clients.</li>
        </ul>
      </Card>

      <SectionTitle sub="A 24-week plan from proof to scale">4 · Launch plan</SectionTitle>
      <div className="grid gap-4 lg:grid-cols-3">
        {LAUNCH_PLAN.map((p) => <Card key={p.phase} title={p.phase} subtitle={p.weeks}><ul className="space-y-1.5">{p.actions.map((a) => <li key={a} className="flex gap-1.5 text-sm text-slate-700"><Building2 className="mt-0.5 h-4 w-4 shrink-0 text-brand-600" />{a}</li>)}</ul></Card>)}
      </div>

      <SectionTitle sub="Enterprise and marketplace buyers will ask for these">5 · Before you sell</SectionTitle>
      <Card pad={false}>
        <ul className="divide-y divide-slate-100">{READINESS.map((r) => <li key={r.item} className="flex gap-3 px-4 py-3"><ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" /><div><div className="text-sm font-medium">{r.item}</div><div className="text-xs text-slate-600">{r.why}</div></div></li>)}</ul>
      </Card>

      <SectionTitle sub="Already built into this app">6 · What you can sell today</SectionTitle>
      <div className="grid gap-4 md:grid-cols-3">
        <Card title="SaaS workspace"><p className="text-sm text-slate-600">Multi-user web app with authentication, projects, all 23 agents, BIM, compliance and reports.</p></Card>
        <Card title="Metered agents API" action={<KeyRound className="h-4 w-4 text-slate-400" />}><p className="text-sm text-slate-600">Create keys in <Link href="/settings" className="font-medium text-brand-700 hover:underline">Settings</Link>. <code>POST /api/v1/analyze</code> runs any subset of agents; <code>GET /api/v1/agents</code> publishes the catalog. Usage is metered per key per month.</p></Card>
        <Card title="Claude Skill"><p className="text-sm text-slate-600"><code>aec/skills/chimera-aec-agents/</code> lets any Claude user run the agents through your API, so Claude becomes a distribution channel for your paid keys.</p></Card>
      </div>
      <Note>Channel names and URLs are real programmes, but their eligibility rules, fees and review times change. Confirm current terms with each provider. Prices are suggestions to test in pilots, not market data.</Note>
    </Container>
  );
}
