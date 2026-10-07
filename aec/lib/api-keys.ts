// API keys for the metered agents API. Keys are shown once and stored as SHA-256 hashes.

import crypto from "node:crypto";
import { db } from "./db";

export const MONTHLY_RUN_LIMIT = 5000;
const hash = (k: string) => crypto.createHash("sha256").update(k).digest("hex");

export interface ApiKeyRow { id: string; name: string; prefix: string; runs: number; month: string | null; month_runs: number; last_used_at: string | null; created_at: string }

export function createApiKey(userId: string, name: string) {
  const secret = `aec_live_${crypto.randomBytes(24).toString("base64url")}`;
  const id = "k_" + crypto.randomBytes(8).toString("base64url");
  db().prepare("INSERT INTO api_keys (id, user_id, name, prefix, key_hash) VALUES (?,?,?,?,?)").run(id, userId, name, secret.slice(0, 14), hash(secret));
  return { id, secret };
}

export function listApiKeys(userId: string): ApiKeyRow[] {
  return db().prepare("SELECT id, name, prefix, runs, month, month_runs, last_used_at, created_at FROM api_keys WHERE user_id = ? ORDER BY created_at DESC").all(userId) as ApiKeyRow[];
}

export function revokeApiKey(userId: string, id: string) {
  return db().prepare("DELETE FROM api_keys WHERE id = ? AND user_id = ?").run(id, userId).changes > 0;
}

/** Resolves a bearer key and enforces the monthly quota (does not meter). */
export function authenticateKey(header: string | null): { userId: string; keyId: string; monthRuns: number } | { error: string; status: number } {
  const m = header?.match(/^Bearer\s+(aec_live_[A-Za-z0-9_-]+)$/);
  if (!m) return { error: "Missing or malformed API key (Authorization: Bearer aec_live_…)", status: 401 };
  const row = db().prepare("SELECT id, user_id, month, month_runs FROM api_keys WHERE key_hash = ?").get(hash(m[1])) as { id: string; user_id: string; month: string | null; month_runs: number } | undefined;
  if (!row) return { error: "Invalid API key", status: 401 };
  const month = new Date().toISOString().slice(0, 7);
  const used = row.month === month ? row.month_runs : 0;
  if (used >= MONTHLY_RUN_LIMIT) return { error: `Monthly quota of ${MONTHLY_RUN_LIMIT} runs reached`, status: 429 };
  return { userId: row.user_id, keyId: row.id, monthRuns: used };
}

/** Meters one successful run against the key; returns runs used this month. */
export function meterRun(keyId: string): number {
  const month = new Date().toISOString().slice(0, 7);
  db().prepare("UPDATE api_keys SET runs = runs + 1, month_runs = CASE WHEN month = ? THEN month_runs + 1 ELSE 1 END, month = ?, last_used_at = datetime('now') WHERE id = ?").run(month, month, keyId);
  return (db().prepare("SELECT month_runs FROM api_keys WHERE id = ?").get(keyId) as { month_runs: number }).month_runs;
}
