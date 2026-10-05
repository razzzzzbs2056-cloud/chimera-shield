"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
import { api, Button, Field } from "./ui";

export function AuthForm({ mode }: { mode: "login" | "register" }) {
  const router = useRouter();
  const search = useSearchParams();
  const [form, setForm] = useState({ name: "", email: mode === "login" ? "demo@chimera.build" : "", password: mode === "login" ? "demo1234" : "", company: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const set = (k: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement>) => setForm({ ...form, [k]: e.target.value });

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError(""); setLoading(true);
    try {
      await api(`/api/auth/${mode}`, { body: form });
      router.replace(mode === "login" ? search.get("next") || "/dashboard" : "/projects?welcome=1");
      router.refresh();
    } catch (err) {
      setError((err as Error).message);
      setLoading(false);
    }
  }

  return (
    <form onSubmit={submit} className="space-y-4">
      {mode === "register" && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Field label="Full name"><input className="input" value={form.name} onChange={set("name")} required autoComplete="name" /></Field>
          <Field label="Company"><input className="input" value={form.company} onChange={set("company")} autoComplete="organization" /></Field>
        </div>
      )}
      <Field label="Work email"><input className="input" type="email" value={form.email} onChange={set("email")} required autoComplete="email" /></Field>
      <Field label="Password" hint={mode === "register" ? "At least 8 characters" : undefined}>
        <input className="input" type="password" value={form.password} onChange={set("password")} required minLength={mode === "register" ? 8 : 1} autoComplete={mode === "login" ? "current-password" : "new-password"} />
      </Field>
      {error && <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700" role="alert">{error}</p>}
      <Button type="submit" loading={loading} className="w-full">{mode === "login" ? "Sign in" : "Create account"}</Button>
      <p className="text-center text-sm text-slate-500">
        {mode === "login" ? <>New to Chimera? <Link className="font-medium text-brand-700 hover:underline" href="/register">Create an account</Link></> : <>Already have an account? <Link className="font-medium text-brand-700 hover:underline" href="/login">Sign in</Link></>}
      </p>
    </form>
  );
}
