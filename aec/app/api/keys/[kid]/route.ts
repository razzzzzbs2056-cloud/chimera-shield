import { fail, ok, withUser } from "@/lib/api";
import { revokeApiKey } from "@/lib/api-keys";

type Ctx = { params: Promise<{ kid: string }> };
export const DELETE = withUser<Ctx>(async (_req, user, { params }) => (revokeApiKey(user.id, (await params).kid) ? ok({ ok: true }) : fail("Key not found", 404)));
