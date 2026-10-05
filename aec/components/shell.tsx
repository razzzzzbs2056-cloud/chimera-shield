"use client";

import clsx from "clsx";
import { BookOpen, Building2, ChevronRight, LayoutDashboard, LogOut, Menu, Settings, X } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api } from "./ui";

const NAV = [
  { href: "/dashboard", label: "Dashboard", Icon: LayoutDashboard },
  { href: "/projects", label: "Projects", Icon: Building2 },
  { href: "/codes", label: "Code library", Icon: BookOpen },
  { href: "/settings", label: "Settings", Icon: Settings },
];

export function Shell({ user, recent, children }: { user: { name: string; email: string; role: string }; recent: { id: string; name: string; code: string; fail: number }[]; children: React.ReactNode }) {
  const path = usePathname();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  useEffect(() => setOpen(false), [path]);

  async function logout() {
    await api("/api/auth/logout", { method: "POST" });
    router.replace("/login");
    router.refresh();
  }

  const sidebar = (
    <div className="flex h-full flex-col bg-slate-950 text-slate-300">
      <div className="flex h-14 items-center gap-2 px-4 text-white">
        <img src="/logo.svg" alt="" className="h-7 w-7" />
        <span className="font-semibold tracking-tight">Chimera AEC</span>
      </div>
      <nav className="space-y-0.5 px-2 py-2" aria-label="Main">
        {NAV.map(({ href, label, Icon }) => {
          const active = path === href || (href !== "/dashboard" && path.startsWith(href));
          return (
            <Link key={href} href={href} className={clsx("flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium transition", active ? "bg-white/10 text-white" : "hover:bg-white/5 hover:text-white")}>
              <Icon className="h-4 w-4" /> {label}
            </Link>
          );
        })}
      </nav>
      <div className="mt-4 px-4 text-[11px] font-semibold uppercase tracking-wider text-slate-500">Recent projects</div>
      <div className="scrollbar-thin mt-1 flex-1 space-y-0.5 overflow-y-auto px-2">
        {recent.length === 0 && <p className="px-3 py-2 text-xs text-slate-500">No projects yet</p>}
        {recent.map((p) => {
          const active = path.startsWith(`/projects/${p.id}`);
          return (
            <Link key={p.id} href={`/projects/${p.id}`} className={clsx("group flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm transition", active ? "bg-white/10 text-white" : "hover:bg-white/5 hover:text-white")}>
              <span className={clsx("h-1.5 w-1.5 shrink-0 rounded-full", p.fail ? "bg-red-400" : "bg-emerald-400")} aria-label={p.fail ? `${p.fail} failing checks` : "all checks passing"} />
              <span className="truncate">{p.name}</span>
              <ChevronRight className="ml-auto h-3.5 w-3.5 opacity-0 group-hover:opacity-60" />
            </Link>
          );
        })}
      </div>
      <div className="border-t border-white/10 p-3">
        <div className="flex items-center gap-2.5 rounded-lg px-2 py-1.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-600 text-xs font-semibold text-white">{user.name.split(" ").map((s) => s[0]).join("").slice(0, 2)}</div>
          <div className="min-w-0 flex-1">
            <div className="truncate text-sm font-medium text-white">{user.name}</div>
            <div className="truncate text-xs text-slate-500">{user.role}</div>
          </div>
          <button onClick={logout} className="rounded-md p-1.5 text-slate-400 hover:bg-white/10 hover:text-white" aria-label="Sign out" title="Sign out"><LogOut className="h-4 w-4" /></button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen lg:pl-64">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 lg:block">{sidebar}</aside>
      {open && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="absolute inset-0 bg-slate-900/50" onClick={() => setOpen(false)} />
          <aside className="absolute inset-y-0 left-0 w-72 shadow-xl">{sidebar}</aside>
          <button onClick={() => setOpen(false)} className="absolute left-[18.5rem] top-3 rounded-md bg-white p-1.5" aria-label="Close menu"><X className="h-4 w-4" /></button>
        </div>
      )}
      <header className="sticky top-0 z-20 flex h-14 items-center gap-3 border-b border-slate-200 bg-white/90 px-4 backdrop-blur lg:hidden">
        <button onClick={() => setOpen(true)} className="rounded-md p-1.5 hover:bg-slate-100" aria-label="Open menu"><Menu className="h-5 w-5" /></button>
        <img src="/logo.svg" alt="" className="h-6 w-6" /><span className="font-semibold">Chimera AEC</span>
      </header>
      <main>{children}</main>
    </div>
  );
}
