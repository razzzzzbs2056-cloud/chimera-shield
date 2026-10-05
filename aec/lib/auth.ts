import "server-only";
import crypto from "node:crypto";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { db } from "./db";

export const SESSION_COOKIE = "aec_session";
const SESSION_DAYS = 30;

export interface User { id: string; email: string; name: string; role: string; company: string | null; created_at: string }

export { hashPassword, verifyPassword } from "./password";

const tokenHash = (token: string) => crypto.createHash("sha256").update(token).digest("hex");

export async function createSession(userId: string) {
  const token = crypto.randomBytes(32).toString("base64url");
  const expires = new Date(Date.now() + SESSION_DAYS * 86400_000);
  db().prepare("INSERT INTO sessions (id, user_id, expires_at) VALUES (?, ?, ?)").run(tokenHash(token), userId, expires.toISOString());
  const jar = await cookies();
  jar.set(SESSION_COOKIE, token, { httpOnly: true, sameSite: "lax", secure: process.env.NODE_ENV === "production", path: "/", expires });
}

export async function destroySession() {
  const jar = await cookies();
  const token = jar.get(SESSION_COOKIE)?.value;
  if (token) db().prepare("DELETE FROM sessions WHERE id = ?").run(tokenHash(token));
  jar.delete(SESSION_COOKIE);
}

export async function currentUser(): Promise<User | null> {
  const jar = await cookies();
  const token = jar.get(SESSION_COOKIE)?.value;
  if (!token) return null;
  const row = db().prepare(
    `SELECT u.id, u.email, u.name, u.role, u.company, u.created_at, s.expires_at FROM sessions s JOIN users u ON u.id = s.user_id WHERE s.id = ?`,
  ).get(tokenHash(token)) as (User & { expires_at: string }) | undefined;
  if (!row) return null;
  if (new Date(row.expires_at) < new Date()) {
    db().prepare("DELETE FROM sessions WHERE id = ?").run(tokenHash(token));
    return null;
  }
  const { expires_at: _e, ...user } = row;
  return user;
}

export async function requireUser(): Promise<User> {
  const u = await currentUser();
  if (!u) redirect("/login");
  return u;
}
