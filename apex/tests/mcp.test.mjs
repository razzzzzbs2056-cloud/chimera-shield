// Apex MCP server test: speaks JSON-RPC over stdio to the real server with a temp data file.
//   node apex/tests/mcp.test.mjs
import { spawn } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'apex-mcp-'));
const data = path.join(dir, 'data.json');
const proc = spawn(process.execPath, [path.join(root, 'mcp', 'server.mjs')], { env: { ...process.env, APEX_DATA: data } });

let buf = '';
const waiting = new Map();
let stderr = '';
proc.stderr.on('data', (d) => { stderr += d; });
proc.stdout.on('data', (d) => {
  buf += d;
  let i;
  while ((i = buf.indexOf('\n')) >= 0) {
    const msg = JSON.parse(buf.slice(0, i));
    buf = buf.slice(i + 1);
    waiting.get(msg.id)?.(msg);
  }
});
let nextId = 1;
const rpc = (method, params) => new Promise((resolve, reject) => {
  const id = nextId++;
  const t = setTimeout(() => reject(new Error('timeout on ' + method)), 5000);
  waiting.set(id, (m) => { clearTimeout(t); resolve(m); });
  proc.stdin.write(JSON.stringify({ jsonrpc: '2.0', id, method, params }) + '\n');
});
const call = async (name, args) => {
  const r = await rpc('tools/call', { name, arguments: args || {} });
  return { isError: !!r.result.isError, value: r.result.isError ? r.result.content[0].text : JSON.parse(r.result.content[0].text) };
};

try {
  const init = await rpc('initialize', { protocolVersion: '2025-06-18', capabilities: {}, clientInfo: { name: 'test', version: '0' } });
  assert.equal(init.result.serverInfo.name, 'apex');
  proc.stdin.write(JSON.stringify({ jsonrpc: '2.0', method: 'notifications/initialized' }) + '\n');

  const tools = (await rpc('tools/list')).result.tools.map((t) => t.name);
  for (const t of ['list_trackers', 'get_life_score', 'get_trend', 'weekly_report', 'get_day', 'log_day', 'get_principles', 'get_rank']) assert.ok(tools.includes(t), 'missing tool ' + t);

  // every <script> module in index.html must load and register in Node too
  const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
  const expected = [...html.matchAll(/js\/modules\/([\w-]+)\.js/g)].map((m) => m[1]);
  const trackers = (await call('list_trackers')).value.map((t) => t.id);
  assert.deepEqual([...trackers].sort(), [...expected].sort(), 'trackers loaded in MCP server');

  const empty = (await call('get_life_score')).value;
  assert.equal(empty.lifeScore, 0);

  const logged = (await call('log_day', { tracker: 'finance', data: { noSpend: true } })).value;
  assert.ok(logged.score > 0, 'finance score after logging');
  assert.ok(fs.existsSync(data), 'data file written');
  assert.equal(JSON.parse(fs.readFileSync(data, 'utf8')).app, 'apex', 'data file is an Apex backup');

  const day = (await call('get_day', { tracker: 'finance' })).value;
  assert.equal(day.data.noSpend, true);

  assert.equal((await call('get_trend', { days: 7 })).value.length, 7);
  const report = (await call('weekly_report')).value;
  assert.equal(report.daily.length, 7);
  assert.ok(report.rank && report.rank.rank, 'weekly report includes rank');
  const rank = (await call('get_rank')).value;
  assert.equal(rank.rank, 'Recruit');
  assert.ok(rank.xp > 0 && rank.next.rank === 'Private');
  assert.ok(Array.isArray(report.recommendedPrinciples));
  assert.ok((await call('get_principles', { tracker: 'sleep' })).value.length > 0);

  assert.ok((await call('get_day', { tracker: 'nope' })).isError, 'unknown tracker errors');
  assert.ok((await call('log_day', { tracker: 'sleep', date: '2999-01-01', data: {} })).isError, 'future date rejected');
  assert.ok((await call('get_life_score', { date: 'bogus' })).isError, 'bad date rejected');
  assert.ok((await rpc('nope/method')).error, 'unknown method errors');

  assert.equal(stderr, '', 'server stderr should be empty, got: ' + stderr);
  console.log('PASS mcp (' + trackers.length + ' trackers, ' + tools.length + ' tools)');
} catch (e) {
  console.error('FAIL mcp:', e.message);
  process.exitCode = 1;
} finally {
  proc.kill();
  fs.rmSync(dir, { recursive: true, force: true });
}
