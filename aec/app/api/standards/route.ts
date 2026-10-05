import { body, fail, num, ok, str, withUser } from "@/lib/api";
import type { StandardRef } from "@/lib/engine/types";
import { createStandard, standards } from "@/lib/repo";

const STATUS = ["current", "superseded", "draft"];

export const GET = withUser(async () => ok(standards()));

export const POST = withUser(async (req) => {
  const b = await body<Partial<StandardRef>>(req);
  const code = str(b.code, 60), edition = str(b.edition, 60);
  if (!code || !edition) return fail("Code family and edition are required");
  const s: StandardRef = { code, title: str(b.title, 200) || code, jurisdiction: str(b.jurisdiction, 10) || "US", discipline: str(b.discipline, 40) || "General", edition, year: num(b.year, 1900, 2100) ?? new Date().getFullYear(), status: STATUS.includes(b.status as string) ? (b.status as StandardRef["status"]) : "current", supersededBy: str(b.supersededBy, 60) || null };
  return ok({ id: createStandard(s) }, 201);
});
