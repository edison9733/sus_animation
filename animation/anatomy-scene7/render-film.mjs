// Render floodsafe-signal-film.html frame by frame (pure in t) and encode a 1920x1080 60 fps MP4.
// node render-film.mjs [--still 4.6]   (with --still, writes one PNG at that time instead)
import { spawn, spawnSync } from "node:child_process";
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const PAGE = pathToFileURL(join(HERE, "floodsafe-signal-film.html")).href;
const FPS = 60, SECONDS = 5.5, W = 1920, H = 1080;
const stillAt = process.argv.includes("--still") ? Number(process.argv[process.argv.indexOf("--still") + 1]) : null;
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 9300 + Math.floor(Math.random() * 400);
const profile = mkdtempSync(join(tmpdir(), "fs-chrome-"));

const chrome = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${PORT}`, `--user-data-dir=${profile}`, "--hide-scrollbars", "--force-color-profile=srgb", "about:blank"], { stdio: "ignore" });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let target;
for (let i = 0; i < 80 && !target; i++) {
  await sleep(150);
  try { target = await (await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: "PUT" })).json(); } catch {}
}
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r, { once: true }));
let id = 0;
const pending = new Map();
ws.addEventListener("message", (e) => { const m = JSON.parse(e.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } });
const send = (method, params = {}) => new Promise((r) => { const n = ++id; pending.set(n, r); ws.send(JSON.stringify({ id: n, method, params })); });

await send("Page.enable");
await send("Emulation.setDeviceMetricsOverride", { width: W, height: H, deviceScaleFactor: 1, mobile: false });
await send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-reduced-motion", value: "reduce" }] });
await send("Page.navigate", { url: PAGE });
for (let i = 0; i < 60; i++) { await sleep(100); const r = await send("Runtime.evaluate", { expression: "typeof window.renderAt === 'function' && document.fonts.status === 'loaded'", returnByValue: true }); if (r.result?.result?.value) break; }

const shot = async (t) => {
  await send("Runtime.evaluate", { expression: `window.renderAt(${t})`, returnByValue: true });
  await send("Runtime.evaluate", { expression: "new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))", awaitPromise: true });
  const r = await send("Page.captureScreenshot", { format: "png", clip: { x: 0, y: 0, width: W, height: H, scale: 1 } });
  return Buffer.from(r.result.data, "base64");
};

if (stillAt !== null) {
  mkdirSync(join(HERE, "shots"), { recursive: true });
  const out = join(HERE, "shots", `film-${stillAt.toFixed(2)}.png`);
  writeFileSync(out, await shot(stillAt));
  console.log("wrote", out);
} else {
  const dir = join(HERE, ".frames");
  rmSync(dir, { recursive: true, force: true });
  mkdirSync(dir, { recursive: true });
  const n = Math.round(SECONDS * FPS);
  for (let i = 0; i < n; i++) {
    writeFileSync(join(dir, `f${String(i).padStart(4, "0")}.png`), await shot(i / FPS));
    if (i % 60 === 0) console.log(`frame ${i}/${n}`);
  }
  const mp4 = join(HERE, "FloodSafe_scene7_signal_anatomy.mp4");
  const ff = spawnSync("ffmpeg", ["-y", "-loglevel", "error", "-framerate", String(FPS), "-i", join(dir, "f%04d.png"), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", "-preset", "slow", "-movflags", "+faststart", mp4], { stdio: "inherit" });
  if (ff.status !== 0) process.exitCode = 1; else console.log("wrote", mp4);
}
ws.close();
const gone = new Promise((r) => chrome.once("exit", r));
chrome.kill();
await gone;
try { rmSync(profile, { recursive: true, force: true, maxRetries: 5 }); } catch {}
