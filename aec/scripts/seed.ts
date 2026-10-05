import { ensureSeeded } from "../lib/seed";

const created = ensureSeeded(true);
if (!created) console.log("Demo workspace already seeded (npm run db:reset to start over).");
