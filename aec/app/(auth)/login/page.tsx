import { Suspense } from "react";
import { AuthForm } from "@/components/auth-form";

export const metadata = { title: "Sign in" };

export default function LoginPage() {
  return (
    <div className="w-full max-w-sm">
      <div className="mb-6 flex items-center gap-2 lg:hidden"><img src="/logo.svg" alt="" className="h-8 w-8" /><span className="font-semibold">Chimera AEC</span></div>
      <h2 className="text-2xl font-semibold tracking-tight">Welcome back</h2>
      <p className="mt-1 text-sm text-slate-500">Sign in to your engineering workspace.</p>
      <div className="mt-4 rounded-lg border border-brand-100 bg-brand-50 px-3 py-2 text-xs text-brand-800">Demo account pre-filled: <b>demo@chimera.build</b> / <b>demo1234</b></div>
      <div className="mt-6"><Suspense><AuthForm mode="login" /></Suspense></div>
    </div>
  );
}
