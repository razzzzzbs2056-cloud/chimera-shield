import Database from "better-sqlite3";
import fs from "node:fs";
import path from "node:path";

const SCHEMA = `
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY, email TEXT NOT NULL UNIQUE COLLATE NOCASE, name TEXT NOT NULL, password_hash TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'Engineer', company TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS sessions (
  id TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE, expires_at TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS projects (
  id TEXT PRIMARY KEY, owner_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE, name TEXT NOT NULL, code TEXT NOT NULL,
  client TEXT, stage TEXT NOT NULL DEFAULT 'Concept', status TEXT NOT NULL DEFAULT 'active', address TEXT, description TEXT,
  intake TEXT NOT NULL, params TEXT NOT NULL, pins TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT (datetime('now')), updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS boreholes (
  id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE, name TEXT NOT NULL,
  x REAL NOT NULL DEFAULT 0, y REAL NOT NULL DEFAULT 0, gwl REAL NOT NULL, layers TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS runs (
  id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE, user_id TEXT,
  engine_version TEXT NOT NULL, duration_ms INTEGER NOT NULL, kpis TEXT NOT NULL, result TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS runs_project ON runs(project_id, created_at DESC);
CREATE TABLE IF NOT EXISTS design_options (
  id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE, name TEXT NOT NULL,
  objective TEXT NOT NULL DEFAULT 'balanced', params TEXT NOT NULL, metrics TEXT NOT NULL, score REAL NOT NULL DEFAULT 0,
  notes TEXT, starred INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS issues (
  id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE, key TEXT,
  type TEXT NOT NULL, severity TEXT NOT NULL, title TEXT NOT NULL, detail TEXT, discipline TEXT, location TEXT,
  status TEXT NOT NULL DEFAULT 'open', assignee TEXT, created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')), UNIQUE(project_id, key)
);
CREATE TABLE IF NOT EXISTS standards (
  id TEXT PRIMARY KEY, code TEXT NOT NULL, title TEXT NOT NULL, jurisdiction TEXT NOT NULL, discipline TEXT NOT NULL,
  edition TEXT NOT NULL, year INTEGER NOT NULL, status TEXT NOT NULL, superseded_by TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS assets (
  id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE, name TEXT NOT NULL,
  system TEXT NOT NULL, type TEXT NOT NULL, install_date TEXT NOT NULL, condition INTEGER NOT NULL DEFAULT 3,
  runtime_hours REAL NOT NULL DEFAULT 0, criticality REAL NOT NULL DEFAULT 0.5, location TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS activity (
  id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, project_id TEXT, action TEXT NOT NULL, detail TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
`;

declare global {
  // eslint-disable-next-line no-var
  var __aecDb: Database.Database | undefined;
}

export function db(): Database.Database {
  if (!globalThis.__aecDb) {
    const file = process.env.AEC_DB_PATH || path.join(process.cwd(), "data", "aec.db");
    fs.mkdirSync(path.dirname(file), { recursive: true });
    const conn = new Database(file);
    conn.exec(SCHEMA);
    globalThis.__aecDb = conn;
  }
  return globalThis.__aecDb;
}

export const json = <T>(s: string | null | undefined, fallback: T): T => {
  if (!s) return fallback;
  try { return JSON.parse(s) as T; } catch { return fallback; }
};
