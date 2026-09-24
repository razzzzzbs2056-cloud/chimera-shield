// Renders every *.html in this folder to ../png/<name>.png at its native size.
// Run from anywhere:  NODE_PATH=$(npm root -g) node docs/company/marketing/ads/src/render.mjs
// Uses the preinstalled Chromium; does not download browsers.
import { createRequire } from 'module';
import { readdirSync } from 'fs';
import { dirname, join, basename } from 'path';
import { fileURLToPath } from 'url';
const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require(join(process.env.NODE_PATH || '/usr/local/lib/node_modules', 'playwright'))); }
const here = dirname(fileURLToPath(import.meta.url));
const out = join(here, '..', 'png');
const sizes = { li: [1200, 627], sq: [1080, 1080] };
const exe = process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';
const browser = await chromium.launch({ executablePath: exe });
let problems = 0;
for (const f of readdirSync(here).filter(n => n.endsWith('.html')).sort()) {
  const [w, h] = sizes[f.slice(0, 2)];
  const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
  await page.goto('file://' + join(here, f));
  // Flag any element that overflows the canvas or its own box (clipped text).
  const issues = await page.evaluate(([W, H]) => {
    const bad = [];
    for (const el of document.querySelectorAll('.ad *')) {
      if (el.closest('svg') || el.classList.contains('accent')) continue;
      const r = el.getBoundingClientRect();
      if (r.width === 0) continue;
      if (r.right > W + 0.5 || r.bottom > H + 0.5 || r.left < -0.5 || r.top < -0.5) bad.push(`${el.tagName}.${el.className} outside canvas`);
      if (el.scrollWidth > el.clientWidth + 1 && getComputedStyle(el).overflow !== 'visible') bad.push(`${el.tagName}.${el.className} h-overflow`);
    }
    return bad;
  }, [w, h]);
  // Text collision check between the content wrapper and the footer.
  const overlap = await page.evaluate(() => {
    const foot = document.querySelector('.foot')?.getBoundingClientRect();
    const blocks = [...document.querySelectorAll('.wrap > *, .left > *, .card, .steps')];
    return blocks.filter(b => foot && b.getBoundingClientRect().bottom > foot.top + 0.5).map(b => b.className || b.tagName);
  });
  const png = join(out, basename(f, '.html') + '.png');
  await page.screenshot({ path: png });
  const all = issues.concat(overlap.map(o => `${o} overlaps footer`));
  problems += all.length;
  console.log(`${f} -> ${png} ${all.length ? 'ISSUES: ' + all.join('; ') : 'ok'}`);
  await page.close();
}
await browser.close();
process.exit(problems ? 1 : 0);
