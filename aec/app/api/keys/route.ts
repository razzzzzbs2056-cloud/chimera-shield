import { body, ok, str, withUser } from "@/lib/api";
import { createApiKey, listApiKeys } from "@/lib/api-keys";
import { logActivity } from "@/lib/repo";

export const GET = withUser(async (_req, user) => ok(listApiKeys(user.id)));
export const POST = withUser(async (req, user) => {
  const b = await body<{ name?: string }>(req);
  const k = createApiKey(user.id, str(b.name, 60) || "API key");
  logActivity(user.id, null, "created API key", str(b.name, 60) || "API key");
  return ok(k, 201);
});
