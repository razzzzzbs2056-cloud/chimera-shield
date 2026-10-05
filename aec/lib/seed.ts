// Seeds the demo workspace: demo user, standards library, six projects with
// borehole logs, assets and RFIs, a full engineering run per project and a
// set of saved design alternatives.

import { db } from "./db";
import { generateAlternatives } from "./engine/alternatives";
import { hashPassword } from "./password";
import { createAsset, createBorehole, createIssue, createOption, createProject, createStandard, newId, runProject, standards } from "./repo";
import { SEED_PROJECTS, SEED_STANDARDS } from "./seed-data";

export const DEMO_EMAIL = "demo@chimera.build";
export const DEMO_PASSWORD = "demo1234";

export function ensureStandards() {
  const n = (db().prepare("SELECT COUNT(*) AS n FROM standards").get() as { n: number }).n;
  if (!n) SEED_STANDARDS.forEach((s) => createStandard(s));
}

export function seedSampleProjects(userId: string, which: number[] = SEED_PROJECTS.map((_, i) => i), withAlternatives = true) {
  const ids: string[] = [];
  for (const i of which) {
    const sp = SEED_PROJECTS[i];
    const id = createProject(userId, { name: sp.name, code: sp.code, client: sp.client, stage: sp.stage, status: sp.status, address: sp.address, description: sp.description, intake: sp.intake, params: sp.params, pins: sp.pins });
    sp.boreholes.forEach((b) => createBorehole(userId, id, b));
    sp.assets?.forEach((a) => createAsset(userId, id, { name: a.name, system: a.system, type: a.type, install_date: a.installDate, condition: a.condition, runtime_hours: a.runtimeHours, criticality: a.criticality, location: a.location }));
    sp.rfis?.forEach((r) => createIssue(userId, id, { title: r.title, detail: r.detail, severity: r.severity, discipline: r.discipline, status: r.status, type: "rfi" }));
    runProject(userId, id);
    if (withAlternatives && i === 0) {
      const alts = generateAlternatives({ projectId: id, name: sp.name, code: sp.code, intake: sp.intake, params: sp.params, boreholes: sp.boreholes, standards: standards(), pins: sp.pins }, "balanced");
      alts.slice(0, 4).forEach((a) => createOption(userId, id, { name: a.name, objective: "balanced", params: a.params, metrics: a.metrics, score: a.score, notes: a.pareto ? "Pareto-optimal on cost vs carbon" : undefined }));
    }
    ids.push(id);
  }
  return ids;
}

export function ensureSeeded(log = false) {
  ensureStandards();
  const exists = db().prepare("SELECT id FROM users WHERE email = ?").get(DEMO_EMAIL);
  if (exists) return false;
  const t = Date.now();
  const userId = newId("u_");
  db().prepare("INSERT INTO users (id, email, name, password_hash, role, company) VALUES (?,?,?,?,?,?)")
    .run(userId, DEMO_EMAIL, "Alex Morgan", hashPassword(DEMO_PASSWORD), "Principal Engineer", "Chimera Engineering");
  seedSampleProjects(userId);
  if (log) console.log(`Seeded demo workspace in ${((Date.now() - t) / 1000).toFixed(1)} s — login ${DEMO_EMAIL} / ${DEMO_PASSWORD}`);
  return true;
}
