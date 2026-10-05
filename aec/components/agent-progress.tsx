"use client";

import { CheckCircle2, Loader2 } from "lucide-react";
import { useEffect, useState } from "react";

const STEPS = [
  "Intake: normalising brief & site", "Code intelligence: resolving applicable standards", "Geotechnical: interpreting boreholes, Vs30, liquefaction",
  "Fire ↔ Architecture: exits, stairs & core planning", "Structural: comparing lateral systems", "Seismic: modal, CQC response spectrum, P-Δ, pushover",
  "Wind: gust factor, drift, accelerations", "Foundation optimiser: 5 systems", "MEP: HVAC, electrical, hydraulics", "Façade & building physics",
  "BIM: authoring IFC model, clash detection", "Cost, carbon & value engineering", "Construction: CPM, cranes, temporary works", "Independent verifier: cross-checks",
];

/** Full-screen progress overlay shown while the synchronous workflow runs on the server. */
export function AgentProgress() {
  const [i, setI] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setI((x) => Math.min(STEPS.length - 1, x + 1)), 380);
    return () => clearInterval(t);
  }, []);
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 p-4 backdrop-blur-sm" role="status" aria-live="polite">
      <div className="w-full max-w-md rounded-2xl bg-white p-5 shadow-xl">
        <div className="flex items-center gap-2 text-sm font-semibold"><Loader2 className="h-4 w-4 animate-spin text-brand-600" /> Agents are working…</div>
        <ul className="mt-4 space-y-1.5">
          {STEPS.map((s, k) => (
            <li key={s} className={`flex items-center gap-2 text-xs ${k < i ? "text-slate-500" : k === i ? "font-medium text-slate-900" : "text-slate-300"}`}>
              {k < i ? <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" /> : k === i ? <Loader2 className="h-3.5 w-3.5 animate-spin text-brand-600" /> : <span className="h-3.5 w-3.5 rounded-full border border-slate-200" />}
              {s}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
