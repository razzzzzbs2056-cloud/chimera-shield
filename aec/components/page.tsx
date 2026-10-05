export function PageHeader({ title, subtitle, actions, eyebrow }: { title: React.ReactNode; subtitle?: React.ReactNode; actions?: React.ReactNode; eyebrow?: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
      <div className="min-w-0">
        {eyebrow && <div className="mb-1 text-xs font-medium text-brand-700">{eyebrow}</div>}
        <h1 className="truncate text-2xl font-semibold tracking-tight text-slate-900">{title}</h1>
        {subtitle && <p className="mt-1 text-sm text-slate-500">{subtitle}</p>}
      </div>
      {actions && <div className="flex shrink-0 flex-wrap gap-2">{actions}</div>}
    </div>
  );
}
export const Container = ({ children }: { children: React.ReactNode }) => <div className="mx-auto max-w-7xl space-y-6 px-4 py-6 sm:px-6 lg:px-8">{children}</div>;

export function KV({ rows, cols = 2 }: { rows: [React.ReactNode, React.ReactNode][]; cols?: 1 | 2 | 3 }) {
  return (
    <dl className={`grid gap-x-6 gap-y-2 text-sm ${cols === 3 ? "sm:grid-cols-3" : cols === 2 ? "sm:grid-cols-2" : ""}`}>
      {rows.map(([k, v], i) => (
        <div key={i} className="flex items-baseline justify-between gap-3 border-b border-dashed border-slate-100 pb-1.5">
          <dt className="text-slate-500">{k}</dt><dd className="num text-right font-medium text-slate-900">{v}</dd>
        </div>
      ))}
    </dl>
  );
}

export function SectionTitle({ children, sub }: { children: React.ReactNode; sub?: React.ReactNode }) {
  return <div className="pt-2"><h2 className="text-base font-semibold text-slate-900">{children}</h2>{sub && <p className="text-xs text-slate-500">{sub}</p>}</div>;
}

export function Note({ children }: { children: React.ReactNode }) {
  return <p className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-500">{children}</p>;
}
