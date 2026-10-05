"use client";

import { Bot, MapPin } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { BUILDING_TYPES, CITIES, defaultIntake } from "@/lib/defaults";
import type { BuildingType, Intake } from "@/lib/engine/types";
import { AgentProgress } from "./agent-progress";
import { api, Button, Card, Field, useToast } from "./ui";

interface Meta { name: string; code: string; client: string; address: string; description: string; stage: string }

export function IntakeForm({ mode, projectId, initialIntake, initialMeta, initialFloors }: { mode: "create" | "edit"; projectId?: string; initialIntake?: Intake; initialMeta?: Meta; initialFloors?: number }) {
  const router = useRouter();
  const toast = useToast();
  const [intake, setIntake] = useState<Intake>(initialIntake ?? defaultIntake("office", "San Francisco"));
  const [meta, setMeta] = useState<Meta>(initialMeta ?? { name: "", code: "", client: "", address: "", description: "", stage: "Concept" });
  const [floors, setFloors] = useState(initialFloors ?? 12);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const set = <K extends keyof Intake>(k: K, v: Intake[K]) => setIntake((x) => ({ ...x, [k]: v }));
  const numIn = (k: keyof Intake, step = 1) => (
    <input className="input num" type="number" step={step} value={intake[k] as number} onChange={(e) => set(k, Number(e.target.value) as never)} />
  );
  function pickCity(city: string) {
    const c = CITIES.find((x) => x.city === city)!;
    setIntake((x) => ({ ...x, city, jurisdiction: c.jurisdiction, climateZone: c.climateZone, summerDB: c.summerDB, winterDB: c.winterDB, hdd: c.hdd, cdd: c.cdd, basicWindSpeed: c.wind, Ss: c.Ss, S1: c.S1, groundSnow: c.snow, rainfall: c.rain, annualRainfall: c.annual }));
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (!meta.name.trim()) { setError("Project name is required"); return; }
    setBusy(true);
    try {
      if (mode === "create") {
        const { id } = await api<{ id: string }>("/api/projects", { body: { ...meta, intake, floors } });
        toast({ tone: "success", text: "Project created — agents finished the first engineering pass" });
        router.push(`/projects/${id}/agents`);
        router.refresh();
      } else {
        await api(`/api/projects/${projectId}`, { method: "PATCH", body: { ...meta, intake, params: { floors } } });
        await api(`/api/projects/${projectId}/run`, { method: "POST" });
        toast({ tone: "success", text: "Brief updated and workflow re-run" });
        router.refresh();
        setBusy(false);
      }
    } catch (err) {
      setError((err as Error).message);
      setBusy(false);
    }
  }

  const pr = intake.priorities;
  return (
    <form onSubmit={submit} className="space-y-4">
      {busy && <AgentProgress />}
      <Card title="Project" subtitle="Who and what">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <Field label="Project name *"><input className="input" value={meta.name} onChange={(e) => setMeta({ ...meta, name: e.target.value })} placeholder="e.g. Harbourview Tower" required /></Field>
          <Field label="Project code" hint="Auto-generated if blank"><input className="input" value={meta.code} onChange={(e) => setMeta({ ...meta, code: e.target.value })} placeholder="HVT-2026" /></Field>
          <Field label="Client"><input className="input" value={meta.client} onChange={(e) => setMeta({ ...meta, client: e.target.value })} /></Field>
          <Field label="Site address" className="sm:col-span-2"><input className="input" value={meta.address} onChange={(e) => setMeta({ ...meta, address: e.target.value })} /></Field>
          <Field label="Stage">
            <select className="input" value={meta.stage} onChange={(e) => setMeta({ ...meta, stage: e.target.value })}>
              {["Feasibility", "Concept", "Scheme Design", "Design Development", "Construction Documents", "Construction", "Operations"].map((s) => <option key={s}>{s}</option>)}
            </select>
          </Field>
          <Field label="Client goals" className="sm:col-span-2 lg:col-span-3"><textarea className="input min-h-[70px]" value={intake.clientGoals} onChange={(e) => set("clientGoals", e.target.value)} placeholder="e.g. column-free floors, net-zero ready, visible timber…" /></Field>
        </div>
      </Card>

      <Card title="Building & site" subtitle="Occupancy, massing envelope and parking">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Field label="Building type">
            <select className="input" value={intake.buildingType} onChange={(e) => set("buildingType", e.target.value as BuildingType)}>
              {BUILDING_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
            </select>
          </Field>
          <Field label="Storeys above grade"><input className="input num" type="number" min={1} max={90} value={floors} onChange={(e) => setFloors(Number(e.target.value))} /></Field>
          <Field label="Site width (m)">{numIn("siteWidth")}</Field>
          <Field label="Site depth (m)">{numIn("siteDepth")}</Field>
          <Field label="Parking spaces">{numIn("parkingSpaces")}</Field>
          <Field label="Street-to-ground level difference (m)">{numIn("siteLevelDiff", 0.05)}</Field>
          <Field label="Ambient noise at façade (dBA)">{numIn("ambientNoise")}</Field>
          <Field label="Budget (USD)">{numIn("budget", 1_000_000)}</Field>
        </div>
      </Card>

      <Card title="Location, jurisdiction & hazards" subtitle="Picking a city pre-fills climate and hazard data — override with site-specific values" action={<MapPin className="h-4 w-4 text-slate-400" />}>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Field label="City"><select className="input" value={intake.city} onChange={(e) => pickCity(e.target.value)}>{CITIES.map((c) => <option key={c.city}>{c.city}</option>)}</select></Field>
          <Field label="Jurisdiction"><select className="input" value={intake.jurisdiction} onChange={(e) => set("jurisdiction", e.target.value as Intake["jurisdiction"])}>{["US", "UK", "AU", "NZ", "SG", "CA"].map((j) => <option key={j}>{j}</option>)}</select></Field>
          <Field label="ASHRAE climate zone">{numIn("climateZone")}</Field>
          <Field label="Wind exposure"><select className="input" value={intake.exposure} onChange={(e) => set("exposure", e.target.value as Intake["exposure"])}>{["B", "C", "D"].map((x) => <option key={x}>{x}</option>)}</select></Field>
          <Field label="Basic wind speed V (m/s)">{numIn("basicWindSpeed")}</Field>
          <Field label="Ss — MCEᵣ short period (g)">{numIn("Ss", 0.01)}</Field>
          <Field label="S1 — MCEᵣ 1 s (g)">{numIn("S1", 0.01)}</Field>
          <Field label="Ground snow pg (kPa)">{numIn("groundSnow", 0.05)}</Field>
          <Field label="Summer design DB (°C)">{numIn("summerDB")}</Field>
          <Field label="Winter design DB (°C)">{numIn("winterDB")}</Field>
          <Field label="Heating degree days">{numIn("hdd", 50)}</Field>
          <Field label="Cooling degree days">{numIn("cdd", 50)}</Field>
          <Field label="Design rainfall (mm/h)">{numIn("rainfall")}</Field>
          <Field label="Annual rainfall (mm)">{numIn("annualRainfall", 10)}</Field>
          <Field label="Wildfire exposure"><select className="input" value={intake.wildfireRisk} onChange={(e) => set("wildfireRisk", e.target.value as Intake["wildfireRisk"])}>{["low", "moderate", "high"].map((x) => <option key={x}>{x}</option>)}</select></Field>
          <label className="flex items-center gap-2 self-end pb-2 text-sm text-slate-700"><input type="checkbox" className="h-4 w-4 rounded border-slate-300" checked={intake.floodZone} onChange={(e) => set("floodZone", e.target.checked)} /> In mapped flood zone</label>
        </div>
      </Card>

      <Card title="Performance targets & priorities" subtitle="Priorities weight the structural-system selection, alternatives and value engineering">
        <div className="grid gap-4 sm:grid-cols-3">
          <Field label="Target EUI (kWh/m²·yr)">{numIn("targetEUI")}</Field>
          <Field label="Embodied carbon target (kgCO₂e/m²)">{numIn("targetCarbon", 10)}</Field>
          <Field label="Certification"><input className="input" value={intake.certification} onChange={(e) => set("certification", e.target.value)} placeholder="LEED Platinum, BREEAM…" /></Field>
        </div>
        <div className="mt-5 grid gap-x-6 gap-y-4 sm:grid-cols-2 lg:grid-cols-5">
          {(Object.keys(pr) as (keyof typeof pr)[]).map((k) => (
            <label key={k} className="block">
              <span className="label flex justify-between capitalize"><span>{k === "area" ? "Usable area" : k}</span><span className="num text-slate-400">{pr[k].toFixed(1)}</span></span>
              <input type="range" min={0} max={1} step={0.1} value={pr[k]} onChange={(e) => set("priorities", { ...pr, [k]: Number(e.target.value) })} className="w-full accent-brand-600" />
            </label>
          ))}
        </div>
      </Card>

      {error && <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700" role="alert">{error}</p>}
      <div className="flex justify-end gap-2">
        {mode === "create" && <Button type="button" variant="secondary" onClick={() => router.back()}>Cancel</Button>}
        <Button type="submit" loading={busy}><Bot className="h-4 w-4" />{mode === "create" ? "Create & run agents" : "Save brief & re-run"}</Button>
      </div>
    </form>
  );
}
