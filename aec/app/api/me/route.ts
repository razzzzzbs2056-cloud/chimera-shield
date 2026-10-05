import { body, fail, ok, str, withUser } from "@/lib/api";
import { hashPassword, verifyPassword } from "@/lib/auth";
import { db } from "@/lib/db";

export const PATCH = withUser(async (req, user) => {
  const b = await body<{ name?: string; role?: string; company?: string; currentPassword?: string; newPassword?: string }>(req);
  if (b.newPassword !== undefined) {
    const row = db().prepare("SELECT password_hash FROM users WHERE id = ?").get(user.id) as { password_hash: string };
    if (!verifyPassword(b.currentPassword ?? "", row.password_hash)) return fail("Current password is incorrect", 403);
    if (b.newPassword.length < 8) return fail("New password must be at least 8 characters");
    db().prepare("UPDATE users SET password_hash = ? WHERE id = ?").run(hashPassword(b.newPassword), user.id);
    return ok({ ok: true });
  }
  const name = str(b.name, 100) || user.name;
  db().prepare("UPDATE users SET name = ?, role = ?, company = ? WHERE id = ?").run(name, str(b.role, 60) || user.role, str(b.company, 120) || null, user.id);
  return ok({ ok: true });
});
