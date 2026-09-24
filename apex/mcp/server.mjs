#!/usr/bin/env node
// Apex MCP server: gives Claude (or any MCP client) read/write access to your Apex data,
// so an AI coach can see your Life Score, find weak areas, and log entries for you.
//
// Zero dependencies. It loads the app's own core and tracker files in a sandbox, so the
// scores are computed by exactly the same code as the web app.
//
// Data lives in a JSON file in the same format as the app's Settings → Export JSON:
//   APEX_DATA=/path/to/apex-backup.json   (default: ~/.apex/data.json)
// Move data between the app and this server with Export and Import in the app's Settings.
//
// Usage:
//   node apex/mcp/server.mjs            # MCP over stdio
//   node apex/mcp/server.mjs --report   # print this week's report and exit
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import vm from 'node:vm';
import readline from 'node:readline';
import { fileURLToPath } from 'node:url';

const APP = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DATA = process.env.APEX_DATA || path.join(os.homedir(), '.apex', 'data.json');
const VERSION = '1.0.0';

// ---------- sandbox: run the browser code with a file-backed localStorage ----------
function loadData() {
  try {
    const dump = JSON.parse(fs.readFileSync(DATA, 'utf8'));
    return dump && dump.data ? dump.data : {};
  } catch {
    return {};
  }
}

const raw = {}; // key -> JSON string
Object.entries(loadData()).forEach(([k, v]) => { raw[k] = JSON.stringify(v); });

function persist() {
  const data = {};
  Object.entries(raw).forEach(([k, v]) => { data[k] = JSON.parse(v); });
  fs.mkdirSync(path.dirname(DATA), { recursive: true });
  const tmp = DATA + '.tmp';
  fs.writeFileSync(tmp, JSON.stringify({ app: 'apex', version: 1, exportedAt: new Date().toISOString(), data }, null, 2));
  fs.renameSync(tmp, DATA);
}

const localStorage = {
  getItem: (k) => (k in raw ? raw[k] : null),
  setItem: (k, v) => { raw[k] = String(v); if (!k.endsWith('__test')) persist(); },
  removeItem: (k) => { if (k in raw) { delete raw[k]; persist(); } },
  key: (i) => Object.keys(raw)[i] ?? null,
  get length() { return Object.keys(raw).length; },
};

// Minimal DOM stand-in: modules may inject a <style> at load time; nothing is rendered here.
const stubEl = () => {
  const el = { style: {}, dataset: {}, children: [], classList: { add() {}, remove() {}, toggle() {}, contains: () => false } };
  Object.assign(el, { appendChild: (c) => c, append() {}, setAttribute() {}, addEventListener() {}, remove() {}, querySelector: () => null, querySelectorAll: () => [] });
  return el;
};
const document = Object.assign(stubEl(), {
  head: stubEl(), body: stubEl(), documentElement: stubEl(),
  createElement: stubEl, createElementNS: stubEl, createTextNode: stubEl,
  getElementById: () => null,
});

const sandbox = {
  console: { log() {}, info() {}, warn() {}, error: (...a) => process.stderr.write('[apex] ' + a.join(' ') + '\n') },
  localStorage, document, navigator: {}, location: { hash: '', protocol: 'file:' },
  setTimeout, clearTimeout, setInterval: () => 0, clearInterval() {},
  addEventListener() {}, removeEventListener() {},
  Node: function Node() {},
};
sandbox.window = sandbox;
sandbox.self = sandbox;
vm.createContext(sandbox);

const html = fs.readFileSync(path.join(APP, 'index.html'), 'utf8');
const scripts = [...html.matchAll(/<script src="([^"]+)"/g)].map((m) => m[1]).filter((s) => !s.endsWith('core/app.js'));
for (const src of scripts) {
  const file = path.join(APP, src);
  if (!fs.existsSync(file)) continue;
  try {
    vm.runInContext(fs.readFileSync(file, 'utf8'), sandbox, { filename: src });
  } catch (e) {
    process.stderr.write(`[apex] could not load ${src}: ${e.message}\n`);
  }
}
const Apex = sandbox.Apex;

// ---------- tool implementations ----------
const today = () => Apex.date.today();
const isDate = (d) => typeof d === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(d);
const dateArg = (d) => {
  if (d == null || d === '' || d === 'today') return today();
  if (d === 'yesterday') return Apex.date.add(today(), -1);
  if (!isDate(d)) throw new Error(`date must be YYYY-MM-DD, "today" or "yesterday" (got ${JSON.stringify(d)})`);
  return d;
};
const moduleArg = (id) => {
  const m = Apex.modules.get(id);
  if (!m) throw new Error(`unknown tracker "${id}". Available: ${Apex.modules.all().map((x) => x.id).join(', ')}`);
  return m;
};
const plain = (v) => JSON.parse(JSON.stringify(v ?? null));

function lifeScore(date) {
  const ls = Apex.lifeScore(date);
  return {
    date,
    lifeScore: ls.score,
    tier: Apex.tier(ls.score).label,
    logged: `${ls.tracked}/${ls.total}`,
    byCategory: plain(ls.byCategory),
    trackers: Apex.modules.enabled().map((m) => ({
      id: m.id, name: m.name, category: m.category, score: ls.byModule[m.id] ?? null, summary: Apex.moduleSummary(m, date),
    })),
  };
}

function weeklyReport(end) {
  const days = Apex.date.lastN(end, 7);
  const daily = days.map((d) => ({ date: d, score: Apex.lifeScore(d).score }));
  const avg = Math.round(daily.reduce((a, b) => a + b.score, 0) / days.length);
  const trackers = Apex.modules.enabled().map((m) => {
    const scores = days.map((d) => Apex.moduleScore(m, d));
    const logged = scores.filter((s) => s != null);
    return {
      id: m.id, name: m.name, category: m.category,
      daysLogged: logged.length,
      average: Math.round(scores.reduce((a, s) => a + (s ?? 0), 0) / days.length),
    };
  }).sort((a, b) => a.average - b.average);
  const weakest = trackers.slice(0, 3);
  return {
    week: `${days[0]} → ${end}`,
    averageLifeScore: avg,
    tier: Apex.tier(avg).label,
    streakDaysAtOrAbove70: Apex.streak(end, 70),
    daily,
    trackers,
    weakest: weakest.map((t) => t.id),
    strongest: trackers.slice(-3).reverse().map((t) => t.id),
    recommendedPrinciples: weakest.map((t) => plain(Apex.knowledge.daily(end, [t.id]))).filter(Boolean),
  };
}

const TOOLS = [
  {
    name: 'list_trackers',
    description: 'List every Apex tracker (life area): id, name, category, description, weight in the Life Score, and whether it is enabled.',
    inputSchema: { type: 'object', properties: {} },
    run: () => Apex.modules.all().map((m) => ({
      id: m.id, name: m.name, icon: m.icon, category: m.category, description: m.description,
      weight: Apex.modules.weight(m), enabled: Apex.modules.enabled().includes(m),
    })),
  },
  {
    name: 'get_life_score',
    description: "Get the day's overall Life Score (0-100), tier (Top 1% / Top 5% / …), per-category scores, and each tracker's score and summary.",
    inputSchema: { type: 'object', properties: { date: { type: 'string', description: 'YYYY-MM-DD, "today" (default) or "yesterday"' } } },
    run: (a) => lifeScore(dateArg(a.date)),
  },
  {
    name: 'get_trend',
    description: 'Daily Life Scores for the last N days (default 14, max 365), oldest first.',
    inputSchema: { type: 'object', properties: { days: { type: 'integer', minimum: 1, maximum: 365 }, end: { type: 'string', description: 'YYYY-MM-DD, default today' } } },
    run: (a) => {
      const n = Math.max(1, Math.min(365, a.days || 14));
      return Apex.date.lastN(dateArg(a.end), n).map((d) => ({ date: d, score: Apex.lifeScore(d).score }));
    },
  },
  {
    name: 'weekly_report',
    description: 'Seven-day coaching report: average Life Score, streak, each tracker ranked by average, weakest/strongest areas, and book principles aimed at the weakest areas.',
    inputSchema: { type: 'object', properties: { end: { type: 'string', description: 'last day of the week, YYYY-MM-DD, default today' } } },
    run: (a) => weeklyReport(dateArg(a.end)),
  },
  {
    name: 'get_day',
    description: "Raw logged data for one tracker on one day, plus that tracker's score, summary, and settings. Call this before log_day so you know the data shape.",
    inputSchema: { type: 'object', required: ['tracker'], properties: { tracker: { type: 'string' }, date: { type: 'string' } } },
    run: (a) => {
      const m = moduleArg(a.tracker);
      const date = dateArg(a.date);
      return {
        tracker: m.id, date, logged: Apex.store.has(m.id, date),
        data: plain(Apex.store.has(m.id, date) ? Apex.store.get(m.id, date) : null),
        score: Apex.moduleScore(m, date), summary: Apex.moduleSummary(m, date),
        settings: plain(Apex.store.getConfig(m.id)),
      };
    },
  },
  {
    name: 'log_day',
    description: "Write data for one tracker on one day. By default `data` is shallow-merged into the existing entry. Use the same field names that get_day returns (check another day's entry if today is empty). Returns the tracker's new score.",
    inputSchema: {
      type: 'object', required: ['tracker', 'data'],
      properties: {
        tracker: { type: 'string' },
        date: { type: 'string' },
        data: { type: 'object', description: 'fields to write, e.g. {"hours": 7.5}' },
        replace: { type: 'boolean', description: 'replace the whole entry instead of merging (default false)' },
      },
    },
    run: (a) => {
      const m = moduleArg(a.tracker);
      const date = dateArg(a.date);
      if (date > today()) throw new Error('cannot log future dates');
      if (!a.data || typeof a.data !== 'object' || Array.isArray(a.data)) throw new Error('data must be an object');
      const next = a.replace ? a.data : Object.assign(Apex.store.has(m.id, date) ? Apex.store.get(m.id, date) : {}, a.data);
      Apex.store.set(m.id, date, next);
      return { tracker: m.id, date, data: plain(next), score: Apex.moduleScore(m, date), summary: Apex.moduleSummary(m, date), lifeScore: Apex.lifeScore(date).score };
    },
  },
  {
    name: 'get_principles',
    description: 'Search the Apex library of book principles (Atomic Habits, Deep Work, Why We Sleep, The Psychology of Money…). Filter by tracker id and/or a text query.',
    inputSchema: { type: 'object', properties: { tracker: { type: 'string' }, query: { type: 'string' }, limit: { type: 'integer', minimum: 1, maximum: 50 } } },
    run: (a) => {
      let list = a.query ? Apex.knowledge.search(a.query) : Apex.knowledge.principles;
      if (a.tracker) list = list.filter((p) => p.modules.includes(a.tracker));
      return plain(list.slice(0, a.limit || 10));
    },
  },
];

// ---------- CLI ----------
if (process.argv.includes('--report')) {
  console.log(JSON.stringify(weeklyReport(today()), null, 2));
  process.exit(0);
}

// ---------- MCP over stdio (newline-delimited JSON-RPC 2.0) ----------
const send = (msg) => process.stdout.write(JSON.stringify({ jsonrpc: '2.0', ...msg }) + '\n');

function handle(req) {
  const { id, method, params = {} } = req;
  const isRequest = id !== undefined && id !== null;
  switch (method) {
    case 'initialize':
      return send({ id, result: {
        protocolVersion: params.protocolVersion || '2025-06-18',
        capabilities: { tools: {} },
        serverInfo: { name: 'apex', version: VERSION },
        instructions: 'Apex is a personal life tracker. Start with weekly_report or get_life_score. Before log_day, call get_day to learn the data shape. Always confirm with the user before writing data.',
      } });
    case 'ping':
      return isRequest && send({ id, result: {} });
    case 'tools/list':
      return send({ id, result: { tools: TOOLS.map(({ name, description, inputSchema }) => ({ name, description, inputSchema })) } });
    case 'tools/call': {
      const tool = TOOLS.find((t) => t.name === params.name);
      if (!tool) return send({ id, error: { code: -32602, message: `unknown tool ${params.name}` } });
      try {
        const out = tool.run(params.arguments || {});
        return send({ id, result: { content: [{ type: 'text', text: JSON.stringify(out, null, 2) }] } });
      } catch (e) {
        return send({ id, result: { isError: true, content: [{ type: 'text', text: e.message }] } });
      }
    }
    default:
      if (isRequest) send({ id, error: { code: -32601, message: `method not found: ${method}` } });
  }
}

readline.createInterface({ input: process.stdin }).on('line', (line) => {
  if (!line.trim()) return;
  let req;
  try {
    req = JSON.parse(line);
  } catch {
    return send({ id: null, error: { code: -32700, message: 'parse error' } });
  }
  (Array.isArray(req) ? req : [req]).forEach(handle);
});
