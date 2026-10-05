import { createSession, verifyPassword } from "@/lib/auth";
import { db } from "@/lib/db";
import { fail, ok, str } from "@/lib/api";
import { ensureSeeded } from "@/lib/seed";
import { logActivity } from "@/lib/repo";

export async function POST(req: Request) {
  ensureSeeded();
  const b = (await req.json().catch(() => ({}))) as Record<string, unknown>;
  const email = str(b.email, 200).toLowerCase(), password = typeof b.password === "string" ? b.password : "";
  if (!email || !password) return fail("Email and password are required");
  const u = db().prepare("SELECT id, password_hash FROM users WHERE email = ?").get(email) as { id: string; password_hash: string } | undefined;
  if (!u || !verifyPassword(password, u.password_hash)) return fail("Invalid email or password", 401);
  await createSession(u.id);
  logActivity(u.id, null, "signed in");
  return ok({ ok: true });
}
