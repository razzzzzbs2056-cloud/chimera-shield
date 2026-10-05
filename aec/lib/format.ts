// Number/date formatting shared by server and client components.
export const fmt = {
  n: (v: number, d = 0) => (Number.isFinite(v) ? v.toLocaleString("en-US", { maximumFractionDigits: d, minimumFractionDigits: d }) : "—"),
  money: (v: number) => (Math.abs(v) >= 1e6 ? `$${(v / 1e6).toFixed(1)}M` : Math.abs(v) >= 1e3 ? `$${(v / 1e3).toFixed(0)}k` : `$${v.toFixed(0)}`),
  pct: (v: number, d = 1) => `${v.toFixed(d)}%`,
  date: (s: string) => new Date(s.includes("T") ? s : s.replace(" ", "T") + "Z").toLocaleString("en-US", { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" }),
};

