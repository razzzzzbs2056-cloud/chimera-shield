// Data-access layer. Every project-scoped call checks ownership.

import crypto from "node:crypto";
import { db, json } from "./db";
import { generateModel } from "./engine/bim";
import { derive } from "./engine/site";
import type { Borehole, Clash, DesignParams, Intake, StandardRef } from "./engine/types";
import { runWorkflow, type WorkflowResult } from "./engine/workflow";

export const newId = (prefix = "") => prefix + crypto.randomBytes(9).toString("base64url");

export interface ProjectRow {
  id: string; owner_id: string; name: string; code: string; client: string | null; stage: string; status: string; address: string | null;
  description: string | null; intake: Intake; params: DesignParams; pins: Record<string, string>; created_at: string; updated_at: string;
}
export interface ProjectSummary extends ProjectRow { kpis: WorkflowResult["kpis"] | null; lastRunAt: string | null; openIssues: number }

type Raw = Omit<ProjectRow, "intake" | "params" | "pins"> & { intake: string; params: string; pins: string };
const parseProject = (r: Raw): ProjectRow => ({ ...r, intake: json(r.intake, {} as Intake), params: json(r.params, {} as DesignParams), pins: json(r.pins, {}) });

export function logActivity(userId: string | null, projectId: string | null, action: string, detail = "") {
  db().prepare("INSERT INTO activity (user_id, project_id, action, detail) VALUES (?, ?, ?, ?)").run(userId, projectId, action, detail);
}

export function listActivity(userId: string, limit = 12) {
  return db().prepare(
    `SELECT a.*, p.name AS project_name FROM activity a LEFT JOIN projects p ON p.id = a.project_id
     WHERE a.user_id = ? OR p.owner_id = ? ORDER BY a.id DESC LIMIT ?`,
  ).all(userId, userId, limit) as { id: number; action: string; detail: string; project_id: string | null; project_name: string | null; created_at: string }[];
}

// ---------------- projects ----------------
export function listProjects(userId: string): ProjectSummary[] {
  const rows = db().prepare(
    `SELECT p.*, (SELECT kpis FROM runs r WHERE r.project_id = p.id ORDER BY r.created_at DESC, r.rowid DESC LIMIT 1) AS kpis,
            (SELECT created_at FROM runs r WHERE r.project_id = p.id ORDER BY r.created_at DESC, r.rowid DESC LIMIT 1) AS last_run_at,
            (SELECT COUNT(*) FROM issues i WHERE i.project_id = p.id AND i.status != 'resolved') AS open_issues
     FROM projects p WHERE p.owner_id = ? ORDER BY p.updated_at DESC`,
  ).all(userId) as (Raw & { kpis: string | null; last_run_at: string | null; open_issues: number })[];
  return rows.map((r) => ({ ...parseProject(r), kpis: json(r.kpis, null), lastRunAt: r.last_run_at, openIssues: r.open_issues }));
}

export function getProject(userId: string, id: string): ProjectRow | null {
  const r = db().prepare("SELECT * FROM projects WHERE id = ? AND owner_id = ?").get(id, userId) as Raw | undefined;
  return r ? parseProject(r) : null;
}

export function createProject(userId: string, data: { name: string; code: string; client?: string; stage?: string; status?: string; address?: string; description?: string; intake: Intake; params: DesignParams; pins?: Record<string, string> }) {
  const id = newId("p_");
  db().prepare(
    `INSERT INTO projects (id, owner_id, name, code, client, stage, status, address, description, intake, params, pins) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)`,
  ).run(id, userId, data.name, data.code, data.client ?? null, data.stage ?? "Concept", data.status ?? "active", data.address ?? null, data.description ?? null, JSON.stringify(data.intake), JSON.stringify(data.params), JSON.stringify(data.pins ?? {}));
  logActivity(userId, id, "created project", data.name);
  return id;
}

const PROJECT_FIELDS = ["name", "code", "client", "stage", "status", "address", "description"] as const;
export function updateProject(userId: string, id: string, patch: Partial<Omit<ProjectRow, "id" | "owner_id">>) {
  const p = getProject(userId, id);
  if (!p) return null;
  const sets: string[] = [], vals: unknown[] = [];
  for (const f of PROJECT_FIELDS) if (patch[f] !== undefined) { sets.push(`${f} = ?`); vals.push(patch[f]); }
  if (patch.intake) { sets.push("intake = ?"); vals.push(JSON.stringify({ ...p.intake, ...patch.intake })); }
  if (patch.params) { sets.push("params = ?"); vals.push(JSON.stringify({ ...p.params, ...patch.params })); }
  if (patch.pins) { sets.push("pins = ?"); vals.push(JSON.stringify(patch.pins)); }
  if (!sets.length) return p;
  sets.push("updated_at = datetime('now')");
  db().prepare(`UPDATE projects SET ${sets.join(", ")} WHERE id = ? AND owner_id = ?`).run(...vals, id, userId);
  logActivity(userId, id, "updated project", Object.keys(patch).join(", "));
  return getProject(userId, id);
}

export function deleteProject(userId: string, id: string) {
  const r = db().prepare("DELETE FROM projects WHERE id = ? AND owner_id = ?").run(id, userId);
  if (r.changes) logActivity(userId, null, "deleted project", id);
  return r.changes > 0;
}

// ---------------- runs ----------------
export function standards(): StandardRef[] {
  return db().prepare("SELECT id, code, title, jurisdiction, discipline, edition, year, status, superseded_by AS supersededBy FROM standards ORDER BY jurisdiction, code, year DESC").all() as StandardRef[];
}

export function runProject(userId: string, projectId: string): WorkflowResult | null {
  const p = getProject(userId, projectId);
  if (!p) return null;
  const result = runWorkflow({
    projectId: p.id, name: p.name, code: p.code, intake: p.intake, params: p.params, boreholes: listBoreholes(userId, p.id) ?? [],
    standards: standards(), pins: p.pins,
  });
  const runId = newId("r_");
  const tx = db().transaction(() => {
    db().prepare("INSERT INTO runs (id, project_id, user_id, engine_version, duration_ms, kpis, result) VALUES (?,?,?,?,?,?,?)")
      .run(runId, p.id, userId, result.engineVersion, result.durationMs, JSON.stringify(result.kpis), JSON.stringify(result));
    // keep the 10 most recent runs
    db().prepare("DELETE FROM runs WHERE project_id = ? AND id NOT IN (SELECT id FROM runs WHERE project_id = ? ORDER BY created_at DESC, rowid DESC LIMIT 10)").run(p.id, p.id);
    syncIssues(p.id, result.clashes);
    db().prepare("UPDATE projects SET updated_at = datetime('now') WHERE id = ?").run(p.id);
  });
  tx();
  logActivity(userId, p.id, "ran engineering workflow", `${result.kpis.pass} pass · ${result.kpis.fail} fail · ${result.kpis.clashes} clash groups`);
  return result;
}

function syncIssues(projectId: string, clashes: Clash[]) {
  const existing = db().prepare("SELECT id, key, status FROM issues WHERE project_id = ? AND key IS NOT NULL").all(projectId) as { id: string; key: string; status: string }[];
  const seen = new Set<string>();
  const ins = db().prepare(`INSERT INTO issues (id, project_id, key, type, severity, title, detail, discipline, location, status) VALUES (?,?,?,?,?,?,?,?,?, 'open')
    ON CONFLICT(project_id, key) DO UPDATE SET severity = excluded.severity, title = excluded.title, detail = excluded.detail, location = excluded.location,
      status = CASE WHEN issues.status = 'resolved' AND issues.assignee = 'auto' THEN 'open' ELSE issues.status END, updated_at = datetime('now')`);
  for (const c of clashes) {
    seen.add(c.key);
    const discipline = c.a.startsWith("SA") || c.a.includes("riser") || c.a.includes("AHU") ? "Mechanical" : c.a.includes("Cable") ? "Electrical" : c.a.includes("Sprinkler") || c.a.includes("valve") ? "Fire" : c.a.includes("CW") ? "Hydraulics" : "Coordination";
    ins.run(newId("i_"), projectId, c.key, c.type, c.severity, c.title, c.detail, discipline, c.location);
  }
  const resolve = db().prepare("UPDATE issues SET status = 'resolved', assignee = 'auto', updated_at = datetime('now') WHERE id = ?");
  existing.forEach((e) => { if (!seen.has(e.key) && e.status !== "resolved") resolve.run(e.id); });
}

export function latestRun(userId: string, projectId: string): (WorkflowResult & { runId: string; createdAt: string }) | null {
  if (!getProject(userId, projectId)) return null;
  const r = db().prepare("SELECT id, result, created_at FROM runs WHERE project_id = ? ORDER BY created_at DESC, rowid DESC LIMIT 1").get(projectId) as { id: string; result: string; created_at: string } | undefined;
  if (!r) return null;
  return { ...json<WorkflowResult>(r.result, {} as WorkflowResult), runId: r.id, createdAt: r.created_at };
}

export function runHistory(userId: string, projectId: string) {
  if (!getProject(userId, projectId)) return [];
  return db().prepare("SELECT id, engine_version, duration_ms, kpis, created_at FROM runs WHERE project_id = ? ORDER BY created_at DESC, rowid DESC").all(projectId)
    .map((r) => { const x = r as { id: string; engine_version: string; duration_ms: number; kpis: string; created_at: string }; return { ...x, kpis: json<WorkflowResult["kpis"] | null>(x.kpis, null) }; });
}

export function projectModel(userId: string, projectId: string) {
  const p = getProject(userId, projectId);
  const run = latestRun(userId, projectId);
  if (!p || !run) return null;
  const d = derive(p.intake, run.params);
  return generateModel(d, run.params, run.bimInputs);
}

// ---------------- sub-resources ----------------
function owns(userId: string, projectId: string) { return !!getProject(userId, projectId); }
function ownerOf(table: string, id: string): string | null {
  const r = db().prepare(`SELECT p.owner_id FROM ${table} t JOIN projects p ON p.id = t.project_id WHERE t.id = ?`).get(id) as { owner_id: string } | undefined;
  return r?.owner_id ?? null;
}

export function listBoreholes(userId: string, projectId: string): (Borehole & { id: string })[] | null {
  if (!owns(userId, projectId)) return null;
  return (db().prepare("SELECT * FROM boreholes WHERE project_id = ? ORDER BY name").all(projectId) as { id: string; name: string; x: number; y: number; gwl: number; layers: string }[])
    .map((b) => ({ ...b, layers: json(b.layers, []) }));
}
export function createBorehole(userId: string, projectId: string, b: Borehole) {
  if (!owns(userId, projectId)) return null;
  const id = newId("b_");
  db().prepare("INSERT INTO boreholes (id, project_id, name, x, y, gwl, layers) VALUES (?,?,?,?,?,?,?)").run(id, projectId, b.name, b.x, b.y, b.gwl, JSON.stringify(b.layers));
  logActivity(userId, projectId, "added borehole", b.name);
  return id;
}
export function updateBorehole(userId: string, id: string, b: Partial<Borehole>) {
  if (ownerOf("boreholes", id) !== userId) return false;
  const cur = db().prepare("SELECT * FROM boreholes WHERE id = ?").get(id) as { name: string; x: number; y: number; gwl: number; layers: string };
  db().prepare("UPDATE boreholes SET name = ?, x = ?, y = ?, gwl = ?, layers = ? WHERE id = ?").run(b.name ?? cur.name, b.x ?? cur.x, b.y ?? cur.y, b.gwl ?? cur.gwl, b.layers ? JSON.stringify(b.layers) : cur.layers, id);
  return true;
}
export function deleteBorehole(userId: string, id: string) {
  if (ownerOf("boreholes", id) !== userId) return false;
  return db().prepare("DELETE FROM boreholes WHERE id = ?").run(id).changes > 0;
}

export interface IssueRow { id: string; project_id: string; key: string | null; type: string; severity: string; title: string; detail: string | null; discipline: string | null; location: string | null; status: string; assignee: string | null; created_at: string; updated_at: string }
export function listIssues(userId: string, projectId: string): IssueRow[] | null {
  if (!owns(userId, projectId)) return null;
  return db().prepare(`SELECT * FROM issues WHERE project_id = ? ORDER BY CASE status WHEN 'open' THEN 0 WHEN 'in-review' THEN 1 ELSE 2 END,
    CASE severity WHEN 'critical' THEN 0 WHEN 'major' THEN 1 ELSE 2 END, updated_at DESC`).all(projectId) as IssueRow[];
}
export function createIssue(userId: string, projectId: string, i: Pick<IssueRow, "title" | "severity"> & Partial<IssueRow>) {
  if (!owns(userId, projectId)) return null;
  const id = newId("i_");
  db().prepare("INSERT INTO issues (id, project_id, type, severity, title, detail, discipline, location, status, assignee) VALUES (?,?,?,?,?,?,?,?,?,?)")
    .run(id, projectId, i.type ?? "rfi", i.severity, i.title, i.detail ?? null, i.discipline ?? null, i.location ?? null, i.status ?? "open", i.assignee ?? null);
  logActivity(userId, projectId, "raised issue", i.title);
  return id;
}
export function updateIssue(userId: string, id: string, patch: Partial<IssueRow>) {
  if (ownerOf("issues", id) !== userId) return false;
  const fields = ["title", "detail", "severity", "status", "assignee", "discipline", "location"] as const;
  const sets: string[] = [], vals: unknown[] = [];
  fields.forEach((f) => { if (patch[f] !== undefined) { sets.push(`${f} = ?`); vals.push(patch[f]); } });
  if (!sets.length) return true;
  db().prepare(`UPDATE issues SET ${sets.join(", ")}, updated_at = datetime('now') WHERE id = ?`).run(...vals, id);
  return true;
}
export function deleteIssue(userId: string, id: string) {
  if (ownerOf("issues", id) !== userId) return false;
  return db().prepare("DELETE FROM issues WHERE id = ?").run(id).changes > 0;
}

export interface OptionRow { id: string; project_id: string; name: string; objective: string; params: DesignParams; metrics: Record<string, number>; score: number; notes: string | null; starred: number; created_at: string }
export function listOptions(userId: string, projectId: string): OptionRow[] | null {
  if (!owns(userId, projectId)) return null;
  return (db().prepare("SELECT * FROM design_options WHERE project_id = ? ORDER BY starred DESC, score DESC").all(projectId) as (Omit<OptionRow, "params" | "metrics"> & { params: string; metrics: string })[])
    .map((o) => ({ ...o, params: json(o.params, {} as DesignParams), metrics: json(o.metrics, {}) }));
}
export function createOption(userId: string, projectId: string, o: { name: string; objective: string; params: DesignParams; metrics: Record<string, number>; score: number; notes?: string }) {
  if (!owns(userId, projectId)) return null;
  const id = newId("o_");
  db().prepare("INSERT INTO design_options (id, project_id, name, objective, params, metrics, score, notes) VALUES (?,?,?,?,?,?,?,?)")
    .run(id, projectId, o.name, o.objective, JSON.stringify(o.params), JSON.stringify(o.metrics), o.score, o.notes ?? null);
  logActivity(userId, projectId, "saved design option", o.name);
  return id;
}
export function updateOption(userId: string, id: string, patch: { name?: string; notes?: string; starred?: boolean }) {
  if (ownerOf("design_options", id) !== userId) return false;
  const cur = db().prepare("SELECT name, notes, starred FROM design_options WHERE id = ?").get(id) as { name: string; notes: string | null; starred: number };
  db().prepare("UPDATE design_options SET name = ?, notes = ?, starred = ? WHERE id = ?").run(patch.name ?? cur.name, patch.notes ?? cur.notes, patch.starred === undefined ? cur.starred : patch.starred ? 1 : 0, id);
  return true;
}
export function deleteOption(userId: string, id: string) {
  if (ownerOf("design_options", id) !== userId) return false;
  return db().prepare("DELETE FROM design_options WHERE id = ?").run(id).changes > 0;
}
export function applyOption(userId: string, id: string) {
  if (ownerOf("design_options", id) !== userId) return null;
  const o = db().prepare("SELECT project_id, name, params FROM design_options WHERE id = ?").get(id) as { project_id: string; name: string; params: string };
  updateProject(userId, o.project_id, { params: json(o.params, {} as DesignParams) });
  logActivity(userId, o.project_id, "applied design option", o.name);
  return o.project_id;
}

export interface AssetRow { id: string; project_id: string; name: string; system: string; type: string; install_date: string; condition: number; runtime_hours: number; criticality: number; location: string | null; created_at: string }
export function listAssets(userId: string, projectId: string): AssetRow[] | null {
  if (!owns(userId, projectId)) return null;
  return db().prepare("SELECT * FROM assets WHERE project_id = ? ORDER BY system, name").all(projectId) as AssetRow[];
}
export function createAsset(userId: string, projectId: string, a: Omit<AssetRow, "id" | "project_id" | "created_at">) {
  if (!owns(userId, projectId)) return null;
  const id = newId("a_");
  db().prepare("INSERT INTO assets (id, project_id, name, system, type, install_date, condition, runtime_hours, criticality, location) VALUES (?,?,?,?,?,?,?,?,?,?)")
    .run(id, projectId, a.name, a.system, a.type, a.install_date, a.condition, a.runtime_hours, a.criticality, a.location ?? null);
  logActivity(userId, projectId, "registered asset", a.name);
  return id;
}
export function updateAsset(userId: string, id: string, patch: Partial<AssetRow>) {
  if (ownerOf("assets", id) !== userId) return false;
  const fields = ["name", "system", "type", "install_date", "condition", "runtime_hours", "criticality", "location"] as const;
  const sets: string[] = [], vals: unknown[] = [];
  fields.forEach((f) => { if (patch[f] !== undefined) { sets.push(`${f} = ?`); vals.push(patch[f]); } });
  if (sets.length) db().prepare(`UPDATE assets SET ${sets.join(", ")} WHERE id = ?`).run(...vals, id);
  return true;
}
export function deleteAsset(userId: string, id: string) {
  if (ownerOf("assets", id) !== userId) return false;
  return db().prepare("DELETE FROM assets WHERE id = ?").run(id).changes > 0;
}

// standards library (shared across the workspace)
export function createStandard(s: StandardRef) {
  const id = newId("s_");
  db().prepare("INSERT INTO standards (id, code, title, jurisdiction, discipline, edition, year, status, superseded_by) VALUES (?,?,?,?,?,?,?,?,?)")
    .run(id, s.code, s.title, s.jurisdiction, s.discipline, s.edition, s.year, s.status, s.supersededBy ?? null);
  return id;
}
export function updateStandard(id: string, patch: Partial<StandardRef>) {
  const cur = db().prepare("SELECT * FROM standards WHERE id = ?").get(id) as Record<string, unknown> | undefined;
  if (!cur) return false;
  const map: Record<string, string> = { code: "code", title: "title", jurisdiction: "jurisdiction", discipline: "discipline", edition: "edition", year: "year", status: "status", supersededBy: "superseded_by" };
  const sets: string[] = [], vals: unknown[] = [];
  Object.entries(map).forEach(([k, col]) => { const v = (patch as Record<string, unknown>)[k]; if (v !== undefined) { sets.push(`${col} = ?`); vals.push(v); } });
  if (sets.length) db().prepare(`UPDATE standards SET ${sets.join(", ")} WHERE id = ?`).run(...vals, id);
  return true;
}
export function deleteStandard(id: string) { return db().prepare("DELETE FROM standards WHERE id = ?").run(id).changes > 0; }

export function portfolioStats(userId: string) {
  const projects = listProjects(userId);
  const withKpi = projects.filter((p) => p.kpis);
  const s = (f: (p: ProjectSummary) => number) => withKpi.reduce((a, p) => a + f(p), 0);
  return {
    projects, count: projects.length, gfa: s((p) => p.kpis!.gfa), cost: s((p) => p.kpis!.cost),
    carbon: withKpi.length ? s((p) => p.kpis!.embodiedCarbon * p.kpis!.gfa) / Math.max(s((p) => p.kpis!.gfa), 1) : 0,
    pass: s((p) => p.kpis!.pass), fail: s((p) => p.kpis!.fail), warn: s((p) => p.kpis!.warn),
    openIssues: projects.reduce((a, p) => a + p.openIssues, 0), critical: s((p) => p.kpis!.criticalClashes),
  };
}
