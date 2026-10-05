"use client";

import clsx from "clsx";
import { AlertTriangle, CheckCircle2, Info, Loader2, X, XCircle } from "lucide-react";
import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react";

export const cx = clsx;

export function Button({ variant = "primary", size = "md", loading, className, children, ...rest }: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "secondary" | "ghost" | "danger"; size?: "sm" | "md"; loading?: boolean }) {
  return (
    <button
      {...rest}
      disabled={rest.disabled || loading}
      className={clsx(
        "inline-flex items-center justify-center gap-1.5 rounded-lg font-medium transition focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-500/40 disabled:cursor-not-allowed disabled:opacity-60",
        size === "sm" ? "px-2.5 py-1.5 text-xs" : "px-3.5 py-2 text-sm",
        variant === "primary" && "bg-brand-600 text-white shadow-sm hover:bg-brand-700",
        variant === "secondary" && "border border-slate-300 bg-white text-slate-700 shadow-sm hover:bg-slate-50",
        variant === "ghost" && "text-slate-600 hover:bg-slate-100",
        variant === "danger" && "bg-red-600 text-white hover:bg-red-700",
        className,
      )}
    >
      {loading && <Loader2 className="h-4 w-4 animate-spin" />}
      {children}
    </button>
  );
}

export function Card({ title, subtitle, action, children, className, pad = true }: { title?: ReactNode; subtitle?: ReactNode; action?: ReactNode; children: ReactNode; className?: string; pad?: boolean }) {
  return (
    <section className={clsx("card", className)}>
      {(title || action) && (
        <header className="flex items-start justify-between gap-3 border-b border-slate-100 px-4 py-3">
          <div className="min-w-0">
            {title && <h3 className="text-sm font-semibold text-slate-900">{title}</h3>}
            {subtitle && <p className="mt-0.5 text-xs text-slate-500">{subtitle}</p>}
          </div>
          {action}
        </header>
      )}
      <div className={pad ? "p-4" : ""}>{children}</div>
    </section>
  );
}

const STATUS = {
  PASS: { cls: "bg-emerald-50 text-emerald-700 ring-emerald-600/20", Icon: CheckCircle2 },
  FAIL: { cls: "bg-red-50 text-red-700 ring-red-600/20", Icon: XCircle },
  WARN: { cls: "bg-amber-50 text-amber-800 ring-amber-600/20", Icon: AlertTriangle },
  INFO: { cls: "bg-slate-100 text-slate-600 ring-slate-500/20", Icon: Info },
};
export function StatusBadge({ status, label }: { status: keyof typeof STATUS | string; label?: string }) {
  const s = STATUS[status as keyof typeof STATUS] ?? STATUS.INFO;
  return (
    <span className={clsx("inline-flex items-center gap-1 rounded-md px-1.5 py-0.5 text-[11px] font-semibold ring-1 ring-inset", s.cls)}>
      <s.Icon className="h-3 w-3" aria-hidden />
      {label ?? status}
    </span>
  );
}

export function Badge({ children, tone = "slate", className }: { children: ReactNode; tone?: "slate" | "blue" | "green" | "amber" | "red" | "violet"; className?: string }) {
  const tones = {
    slate: "bg-slate-100 text-slate-700", blue: "bg-brand-50 text-brand-700", green: "bg-emerald-50 text-emerald-700",
    amber: "bg-amber-50 text-amber-800", red: "bg-red-50 text-red-700", violet: "bg-violet-50 text-violet-700",
  };
  return <span className={clsx("inline-flex items-center rounded-md px-1.5 py-0.5 text-[11px] font-medium", tones[tone], className)}>{children}</span>;
}

export const severityTone = (s: string) => (s === "critical" ? "red" : s === "major" ? "amber" : "slate") as "red" | "amber" | "slate";

export function Stat({ label, value, unit, hint, tone }: { label: string; value: ReactNode; unit?: string; hint?: ReactNode; tone?: "good" | "bad" | "warn" }) {
  return (
    <div className="card px-4 py-3">
      <div className="text-xs font-medium text-slate-500">{label}</div>
      <div className="mt-1 flex items-baseline gap-1">
        <span className="num text-2xl font-semibold tracking-tight text-slate-900">{value}</span>
        {unit && <span className="text-xs text-slate-500">{unit}</span>}
      </div>
      {hint && <div className={clsx("mt-1 text-xs", tone === "good" ? "text-emerald-700" : tone === "bad" ? "text-red-700" : tone === "warn" ? "text-amber-700" : "text-slate-500")}>{hint}</div>}
    </div>
  );
}

export function EmptyState({ icon: Icon, title, body, action }: { icon: React.ComponentType<{ className?: string }>; title: string; body: ReactNode; action?: ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-slate-300 bg-white px-6 py-12 text-center">
      <div className="flex h-11 w-11 items-center justify-center rounded-full bg-brand-50 text-brand-600"><Icon className="h-5 w-5" /></div>
      <h3 className="mt-3 text-sm font-semibold text-slate-900">{title}</h3>
      <p className="mt-1 max-w-sm text-sm text-slate-500">{body}</p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

export function Skeleton({ className }: { className?: string }) {
  return <div className={clsx("skeleton", className)} />;
}

export function Field({ label, children, hint, className }: { label: string; children: ReactNode; hint?: string; className?: string }) {
  return (
    <label className={clsx("block", className)}>
      <span className="label">{label}</span>
      {children}
      {hint && <span className="mt-1 block text-[11px] text-slate-400">{hint}</span>}
    </label>
  );
}

export function Modal({ open, onClose, title, children, footer, wide }: { open: boolean; onClose: () => void; title: string; children: ReactNode; footer?: ReactNode; wide?: boolean }) {
  useEffect(() => {
    if (!open) return;
    const h = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", h);
    return () => window.removeEventListener("keydown", h);
  }, [open, onClose]);
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-slate-900/40 p-0 backdrop-blur-sm sm:items-center sm:p-4" onMouseDown={onClose} role="dialog" aria-modal aria-label={title}>
      <div className={clsx("max-h-[92vh] w-full overflow-y-auto rounded-t-2xl bg-white shadow-xl sm:rounded-2xl", wide ? "sm:max-w-3xl" : "sm:max-w-lg")} onMouseDown={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between border-b border-slate-100 px-5 py-3.5">
          <h2 className="text-base font-semibold">{title}</h2>
          <button onClick={onClose} className="rounded-md p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600" aria-label="Close"><X className="h-4 w-4" /></button>
        </div>
        <div className="px-5 py-4">{children}</div>
        {footer && <div className="flex justify-end gap-2 border-t border-slate-100 bg-slate-50/60 px-5 py-3">{footer}</div>}
      </div>
    </div>
  );
}

// ---------- toasts ----------
type Toast = { id: number; tone: "success" | "error" | "info"; text: string };
const ToastCtx = createContext<(t: Omit<Toast, "id">) => void>(() => {});
export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const push = useCallback((t: Omit<Toast, "id">) => {
    const id = Date.now() + Math.random();
    setToasts((x) => [...x, { ...t, id }]);
    setTimeout(() => setToasts((x) => x.filter((y) => y.id !== id)), 4000);
  }, []);
  return (
    <ToastCtx.Provider value={push}>
      {children}
      <div className="pointer-events-none fixed bottom-4 right-4 z-[60] flex w-[calc(100%-2rem)] max-w-sm flex-col gap-2" aria-live="polite">
        {toasts.map((t) => (
          <div key={t.id} className={clsx("pointer-events-auto flex items-start gap-2 rounded-lg border bg-white px-3 py-2.5 text-sm shadow-lg", t.tone === "error" ? "border-red-200" : t.tone === "success" ? "border-emerald-200" : "border-slate-200")}>
            {t.tone === "error" ? <XCircle className="mt-0.5 h-4 w-4 text-red-600" /> : t.tone === "success" ? <CheckCircle2 className="mt-0.5 h-4 w-4 text-emerald-600" /> : <Info className="mt-0.5 h-4 w-4 text-brand-600" />}
            <span className="text-slate-700">{t.text}</span>
          </div>
        ))}
      </div>
    </ToastCtx.Provider>
  );
}
export const useToast = () => useContext(ToastCtx);

export async function api<T = unknown>(url: string, opts: { method?: string; body?: unknown } = {}): Promise<T> {
  const res = await fetch(url, {
    method: opts.method ?? (opts.body ? "POST" : "GET"),
    headers: opts.body ? { "Content-Type": "application/json" } : undefined,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error((data as { error?: string }).error ?? `Request failed (${res.status})`);
  return data as T;
}

export { fmt } from "@/lib/format";

export function Table({ head, children, className }: { head: ReactNode[]; children: ReactNode; className?: string }) {
  return (
    <div className={clsx("scrollbar-thin overflow-x-auto", className)}>
      <table className="min-w-full divide-y divide-slate-100">
        <thead className="bg-slate-50/70"><tr>{head.map((h, i) => <th key={i} className="th whitespace-nowrap">{h}</th>)}</tr></thead>
        <tbody className="divide-y divide-slate-100">{children}</tbody>
      </table>
    </div>
  );
}

export function Segmented<T extends string>({ value, onChange, options }: { value: T; onChange: (v: T) => void; options: { value: T; label: string }[] }) {
  return (
    <div className="inline-flex rounded-lg border border-slate-200 bg-slate-100 p-0.5 text-xs">
      {options.map((o) => (
        <button key={o.value} onClick={() => onChange(o.value)} className={clsx("rounded-md px-2.5 py-1 font-medium transition", value === o.value ? "bg-white text-slate-900 shadow-sm" : "text-slate-500 hover:text-slate-700")}>{o.label}</button>
      ))}
    </div>
  );
}

export function Meter({ value, max, tone }: { value: number; max: number; tone?: "good" | "bad" | "warn" }) {
  const pct = Math.max(0, Math.min(100, (value / Math.max(max, 1e-9)) * 100));
  return (
    <div className="h-1.5 w-full rounded-full bg-slate-100" role="meter" aria-valuenow={value} aria-valuemax={max}>
      <div className={clsx("h-1.5 rounded-full", tone === "bad" ? "bg-red-600" : tone === "warn" ? "bg-amber-500" : "bg-brand-600")} style={{ width: `${pct}%` }} />
    </div>
  );
}
