import { NextResponse } from "next/server";
import { currentUser, type User } from "./auth";

export const ok = (data: unknown, status = 200) => NextResponse.json(data, { status });
export const fail = (error: string, status = 400) => NextResponse.json({ error }, { status });

/** Wraps a route handler with authentication and uniform error handling. */
export function withUser<C>(fn: (req: Request, user: User, ctx: C) => Promise<Response> | Response) {
  return async (req: Request, ctx: C) => {
    const user = await currentUser();
    if (!user) return fail("Not authenticated", 401);
    try {
      return await fn(req, user, ctx);
    } catch (e) {
      console.error(e);
      return fail(e instanceof Error ? e.message : "Unexpected error", 500);
    }
  };
}

export async function body<T>(req: Request): Promise<T> {
  try { return (await req.json()) as T; } catch { throw new Error("Invalid JSON body"); }
}

export const str = (v: unknown, max = 500) => (typeof v === "string" ? v.trim().slice(0, max) : "");
export const num = (v: unknown, lo = -Infinity, hi = Infinity) => {
  const n = typeof v === "number" ? v : Number(v);
  if (!Number.isFinite(n)) return null;
  return Math.min(hi, Math.max(lo, n));
};
