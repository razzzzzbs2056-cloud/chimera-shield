"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { api, Button, Card, Field, useToast } from "./ui";

export function SettingsForm({ user, claudeEnabled }: { user: { name: string; email: string; role: string; company: string | null }; claudeEnabled: boolean }) {
  const [p, setP] = useState({ name: user.name, role: user.role, company: user.company ?? "" });
  const [pw, setPw] = useState({ currentPassword: "", newPassword: "" });
  const [busy, setBusy] = useState<"" | "profile" | "pw">("");
  const toast = useToast();
  const router = useRouter();
  async function saveProfile(e: React.FormEvent) {
    e.preventDefault(); setBusy("profile");
    try { await api("/api/me", { method: "PATCH", body: p }); toast({ tone: "success", text: "Profile updated" }); router.refresh(); } catch (err) { toast({ tone: "error", text: (err as Error).message }); }
    setBusy("");
  }
  async function savePw(e: React.FormEvent) {
    e.preventDefault(); setBusy("pw");
    try { await api("/api/me", { method: "PATCH", body: pw }); toast({ tone: "success", text: "Password changed" }); setPw({ currentPassword: "", newPassword: "" }); } catch (err) { toast({ tone: "error", text: (err as Error).message }); }
    setBusy("");
  }
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <Card title="Profile">
        <form onSubmit={saveProfile} className="space-y-3">
          <Field label="Email"><input className="input" value={user.email} disabled /></Field>
          <Field label="Name"><input className="input" value={p.name} onChange={(e) => setP({ ...p, name: e.target.value })} /></Field>
          <div className="grid grid-cols-2 gap-3"><Field label="Role"><input className="input" value={p.role} onChange={(e) => setP({ ...p, role: e.target.value })} /></Field><Field label="Company"><input className="input" value={p.company} onChange={(e) => setP({ ...p, company: e.target.value })} /></Field></div>
          <Button type="submit" loading={busy === "profile"}>Save profile</Button>
        </form>
      </Card>
      <div className="space-y-4">
        <Card title="Password">
          <form onSubmit={savePw} className="space-y-3">
            <Field label="Current password"><input className="input" type="password" value={pw.currentPassword} onChange={(e) => setPw({ ...pw, currentPassword: e.target.value })} autoComplete="current-password" /></Field>
            <Field label="New password" hint="At least 8 characters"><input className="input" type="password" value={pw.newPassword} onChange={(e) => setPw({ ...pw, newPassword: e.target.value })} autoComplete="new-password" /></Field>
            <Button type="submit" variant="secondary" loading={busy === "pw"} disabled={!pw.currentPassword || pw.newPassword.length < 8}>Change password</Button>
          </form>
        </Card>
        <Card title="AI integration">
          <p className="text-sm text-slate-600">{claudeEnabled ? "Claude is connected: the project assistant explains and recommends using solver results." : "No ANTHROPIC_API_KEY detected. The assistant uses the deterministic solver summary; set the key in aec/.env.local to enable Claude."}</p>
          <p className="mt-2 text-xs text-slate-500">Engineering numbers are always computed by the deterministic engines and independently verified — the language model never produces calculations.</p>
        </Card>
      </div>
    </div>
  );
}
