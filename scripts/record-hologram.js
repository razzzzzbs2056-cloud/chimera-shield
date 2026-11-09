// Renders the /hologram route to video, frame by frame, with a virtual clock so
// playback is smooth regardless of how fast the machine renders.
//
//   npm run build && npx next start -p 3000 &
//   node scripts/record-hologram.js [format] [baseUrl] [outDir] [seconds]
//
// format is 16x9 (1920x1080) or 1x1 (1080x1080); writes hologram-<format>.mp4.
// Needs Playwright and ffmpeg on PATH.
const { chromium } = require("playwright");
const { execFileSync } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

const FORMATS = {
  "16x9": { width: 1920, height: 1080 },
  "1x1": { width: 1080, height: 1080 },
};
const format = process.argv[2] || "16x9";
const base = process.argv[3] || "http://localhost:3000";
const outDir = path.resolve(process.argv[4] || "media");
const seconds = Number(process.argv[5] || 12);
const fps = 30;
const size = FORMATS[format];
if (!size) throw new Error(`Unknown format ${format}; use ${Object.keys(FORMATS).join(" or ")}`);

(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const frameDir = fs.mkdtempSync(path.join(os.tmpdir(), "holo-frames-"));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: size, deviceScaleFactor: 1 });
  // Freeze time before load so the power-up intro starts on frame one.
  await page.clock.install({ time: new Date("2026-01-01T00:00:00Z") });
  await page.clock.pauseAt(new Date("2026-01-01T00:00:01Z"));
  await page.goto(`${base}/hologram?aspect=${format}`);
  // Hydration needs timers, so step the paused clock until the hologram is ready.
  for (let i = 0; !(await page.$("[data-ready=true]")); i++) {
    if (i > 600) throw new Error("Hologram never became ready");
    await page.clock.runFor(16);
  }
  await page.addStyleTag({ content: "nextjs-portal{display:none!important}" });

  const total = seconds * fps;
  let elapsed = 0;
  for (let f = 0; f < total; f++) {
    const target = Math.round(((f + 1) * 1000) / fps);
    await page.clock.runFor(target - elapsed);
    elapsed = target;
    // Sweep the tilt slowly so the depth reads on video.
    const t = f / total;
    const cx = size.width / 2, cy = size.height / 2;
    await page.mouse.move(cx + Math.sin(t * Math.PI * 2) * cx * 0.55, cy + Math.cos(t * Math.PI * 2) * cy * 0.3);
    await page.screenshot({ path: path.join(frameDir, `f${String(f).padStart(5, "0")}.jpg`), type: "jpeg", quality: 95 });
  }
  await browser.close();

  const out = path.join(outDir, `hologram-${format}.mp4`);
  execFileSync(
    "ffmpeg",
    ["-y", "-framerate", String(fps), "-i", path.join(frameDir, "f%05d.jpg"),
     "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "slow", "-movflags", "+faststart", out],
    { stdio: "ignore" },
  );
  fs.rmSync(frameDir, { recursive: true, force: true });
  console.log(`Wrote ${out}`);
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
