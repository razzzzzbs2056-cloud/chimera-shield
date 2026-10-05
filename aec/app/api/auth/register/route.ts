import { createSession, hashPassword } from "@/lib/auth";
import { db } from "@/lib/db";
import { fail, ok, str } from "@/lib/api";
import { newId } from "@/lib/repo";
import { ensureStandards } from "@/lib/seed";

export async function POST(req: Request) {
  ensureStandards();
  const b = (await req.json().catch(() => ({}))) as Record<string, unknown>;
  const name = str(b.name, 100), email = str(b.email, 200).toLowerCase(), company = str(b.company, 120);
  const password = typeof b.password === "string" ? b.password : "";
  if (!name || !email) return fail("Name and email are required");
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return fail("Enter a valid email address");
  if (password.length < 8) return fail("Password must be at least 8 characters");
  if (db().prepare("SELECT 1 FROM users WHERE email = ?").get(email)) return fail("An account with this email already exists", 409);
  const id = newId("u_");
  db().prepare("INSERT INTO users (id, email, name, password_hash, role, company) VALUES (?,?,?,?,?,?)").run(id, email, name, hashPassword(password), "Engineer", company || null);
  await createSession(id);
  return ok({ ok: true }, 201);
}
