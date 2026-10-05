import { Suspense } from "react";
import { AuthForm } from "@/components/auth-form";

export const metadata = { title: "Create account" };

export default function RegisterPage() {
  return (
    <div className="w-full max-w-md">
      <div className="mb-6 flex items-center gap-2 lg:hidden"><img src="/logo.svg" alt="" className="h-8 w-8" /><span className="font-semibold">Chimera AEC</span></div>
      <h2 className="text-2xl font-semibold tracking-tight">Create your workspace</h2>
      <p className="mt-1 text-sm text-slate-500">Start a project from a brief, or load a sample tower to explore.</p>
      <div className="mt-6"><Suspense><AuthForm mode="register" /></Suspense></div>
    </div>
  );
}
