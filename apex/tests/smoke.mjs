// Apex smoke test: serves apex/ over HTTP, opens every route in headless Chromium,
// exercises inputs, and fails on any console error or broken module.
//   node apex/tests/smoke.mjs            # all modules
//   node apex/tests/smoke.mjs sleep      # just one module (plus dashboard)
//   SHOTS=1 node apex/tests/smoke.mjs    # also save screenshots to apex/tests/shots/
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
let chromium;
try {
  ({ chromium } = require('playwright'));
} catch {
  const globalRoot = execSync('npm root -g').toString().trim();
  ({ chromium } = require(path.join(globalRoot, 'playwright')));
}

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const only = process.argv[2];
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.svg': 'image/svg+xml', '.webmanifest': 'application/manifest+json', '.json': 'application/json', '.png': 'image/png' };

const server = http.createServer((req, res) => {
  const url = decodeURIComponent(req.url.split('?')[0]);
  const file = path.join(root, url === '/' ? 'index.html' : url);
  if (!file.startsWith(root) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
    res.writeHead(404);
    return res.end('not found');
  }
  res.writeHead(200, { 'content-type': TYPES[path.extname(file)] || 'application/octet-stream' });
  fs.createReadStream(file).pipe(res);
});
await new Promise((r) => server.listen(0, r));
const base = `http://127.0.0.1:${server.address().port}/`;

const browser = await chromium.launch();
const failures = [];
const shots = process.env.SHOTS ? path.join(root, 'tests', 'shots') : null;
if (shots) fs.mkdirSync(shots, { recursive: true });

async function check(viewport, label) {
  const page = await browser.newPage({ viewport });
  const errors = [];
  page.on('console', (m) => m.type() === 'error' && errors.push(m.text()));
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('requestfailed', (r) => errors.push('request failed ' + r.url()));
  page.on('response', (r) => r.status() >= 400 && errors.push(`${r.status()} ${r.url()}`));

  await page.goto(base);
  await page.waitForSelector('.hero');
  const ids = await page.evaluate(() => Apex.modules.all().map((m) => m.id));
  const targets = only ? ids.filter((i) => i === only) : ids;
  if (only && !targets.length) failures.push(`module "${only}" did not register`);

  for (const id of targets) {
    await page.goto(base + '#/m/' + id);
    await page.waitForSelector('.module-body');
    const broke = await page.$('.module-body >> text=Something broke');
    if (broke) failures.push(`[${label}] ${id}: render threw`);

    // Exercise the first few inputs of each kind, then re-check.
    for (const sel of ['.module-body input[type=number]', '.module-body .pill', '.module-body input[type=checkbox]']) {
      const els = await page.$$(sel);
      for (const el of els.slice(0, 3)) {
        try {
          if (sel.includes('number')) { await el.fill('5'); await el.dispatchEvent('change'); }
          else if (sel.includes('checkbox')) { await el.evaluate((n) => n.click()); }
          else await el.click({ timeout: 1000 });
        } catch { /* element may have been re-rendered away; fine */ }
      }
    }
    const res = await page.evaluate((mid) => {
      const m = Apex.modules.get(mid);
      const d = Apex.date.today();
      return { score: Apex.moduleScore(m, d), summary: Apex.moduleSummary(m, d), overflow: document.documentElement.scrollWidth > window.innerWidth + 1 };
    }, id);
    if (res.overflow) failures.push(`[${label}] ${id}: horizontal overflow`);
    console.log(`  ${label.padEnd(7)} ${id.padEnd(10)} score=${res.score} summary="${res.summary}"`);
    if (shots) await page.screenshot({ path: path.join(shots, `${label}-${id}.png`), fullPage: true });
  }

  await page.goto(base + '#/');
  await page.waitForSelector('.hero');
  if (shots) await page.screenshot({ path: path.join(shots, `${label}-dashboard.png`), fullPage: true });
  await page.goto(base + '#/settings');
  await page.waitForSelector('.settings-list');

  errors.forEach((e) => failures.push(`[${label}] console: ${e}`));
  await page.close();
}

await check({ width: 1280, height: 900 }, 'desktop');
await check({ width: 390, height: 844 }, 'mobile');
await browser.close();
server.close();

if (failures.length) {
  console.error('\nFAIL\n' + failures.map((f) => ' - ' + f).join('\n'));
  process.exit(1);
}
console.log('\nPASS');
