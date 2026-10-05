import { Boxes, Building2, Calculator, ShieldCheck } from "lucide-react";

const POINTS = [
  { Icon: Building2, title: "Agents that collaborate", body: "23 specialist agents pass models, loads and constraints to each other — and iterate the design until it converges." },
  { Icon: Calculator, title: "Real solvers, not guesses", body: "Finite-element frames, modal & response-spectrum analysis, pushover, time-history, geotechnics and MEP sizing." },
  { Icon: ShieldCheck, title: "Clause-level compliance", body: "Every check shows requirement, clause, evidence and PASS/FAIL — with code-edition control." },
  { Icon: Boxes, title: "openBIM native", body: "IFC4 model, physical & semantic clash detection, 4D/5D, BOQ and a digital twin for operations." },
];

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      <aside className="relative hidden overflow-hidden bg-slate-950 p-12 text-white lg:flex lg:flex-col">
        <div className="absolute inset-0 opacity-30" style={{ backgroundImage: "linear-gradient(rgba(148,163,184,.12) 1px, transparent 1px), linear-gradient(90deg, rgba(148,163,184,.12) 1px, transparent 1px)", backgroundSize: "36px 36px" }} />
        <div className="relative flex items-center gap-2 text-lg font-semibold"><img src="/logo.svg" alt="" className="h-8 w-8" /> Chimera AEC</div>
        <div className="relative mt-auto max-w-lg">
          <h1 className="text-3xl font-semibold leading-tight">A digital architecture & engineering consultancy.</h1>
          <p className="mt-3 text-slate-300">From site brief to digital twin — LLM agents orchestrate engineering solvers, BIM, codes, optimisation and independent verification in one workflow.</p>
          <ul className="mt-8 space-y-5">
            {POINTS.map(({ Icon, title, body }) => (
              <li key={title} className="flex gap-3">
                <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-white/10"><Icon className="h-4 w-4" /></div>
                <div><div className="font-medium">{title}</div><div className="text-sm text-slate-400">{body}</div></div>
              </li>
            ))}
          </ul>
        </div>
        <p className="relative mt-10 text-xs text-slate-500">Engineering outputs are decision support and must be reviewed and sealed by a licensed professional.</p>
      </aside>
      <main className="flex items-center justify-center px-4 py-12 sm:px-8">{children}</main>
    </div>
  );
}
