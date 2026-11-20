// Export a Motion film to MP4 from Claude Code, with the Motion player's own exporter (the code behind its Export button).
// Set up a film folder first (nothing of the player is kept in this repo, because it belongs to the Claude app):
//   index.html, artifact-type/app.js, artifact-type/app.css   read from the film with the Artifact tool (action "read", path)
//   cut.js (= animation/motion/film_script.js), modules/ (the scene modules), assets/ (the images, plus the Inter font as Inter.woff2)
// Then:
// Drives the player's headless entry (index.html#tools → window.__animation) in headless Chrome:
// node motion-export.mjs <filmDir> stills 0.8,20,40   → PNGs from the film's renderer, into <outDir>
// node motion-export.mjs <filmDir> export <out.mp4>   → exportFilm(): the same encoder the Export button runs
// MOTION_SUPERSAMPLE=1 renders each frame at twice the size and scales it down: smoother edges and text, slower.
// The page gets no network: every host resolves to nothing and all traffic goes to a dead proxy.
import { spawn } from "node:child_process";
import { mkdirSync, mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { extname, join, resolve } from "node:path";
import { pathToFileURL } from "node:url";

const [dirArg, verb, arg, outDir] = process.argv.slice(2);
const DIR = resolve(dirArg);
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 9700 + Math.floor(Math.random() * 300);
const profile = mkdtempSync(join(tmpdir(), "motion-chrome-"));
const MIME = { ".png": "image/png", ".jpg": "image/jpeg", ".webp": "image/webp", ".woff2": "font/woff2", ".woff": "font/woff", ".ttf": "font/ttf", ".otf": "font/otf" };
const KIND = { ".css": "css", ".js": "js", ".json": "json", ".html": "html", ".txt": "text" };
const files = {
  title: "FloodSafe Sanitation",
  script: readFileSync(join(DIR, "cut.js"), "utf8"),
  modules: readdirSync(join(DIR, "modules")).map((n) => ({ name: n, kind: KIND[extname(n)], text: readFileSync(join(DIR, "modules", n), "utf8") })),
  assets: readdirSync(join(DIR, "assets")).map((n) => ({ name: n, mime: MIME[extname(n).toLowerCase()], base64: readFileSync(join(DIR, "assets", n)).toString("base64") })),
};

const chrome = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${PORT}`, `--user-data-dir=${profile}`, "--hide-scrollbars",
  "--force-color-profile=srgb", "--font-render-hinting=none", "--disable-lcd-text", "--autoplay-policy=no-user-gesture-required",
  "--host-resolver-rules=MAP * ^NOTFOUND", "--proxy-server=http://127.0.0.1:9", "--proxy-bypass-list=<-loopback>",
  "--force-webrtc-ip-handling-policy=disable_non_proxied_udp", "about:blank"], { stdio: "ignore" });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let target;
for (let i = 0; i < 80 && !target; i++) { await sleep(150); try { target = await (await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: "PUT" })).json(); } catch {} }
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener("open", r, { once: true }));
let id = 0; const pending = new Map(); const logs = [];
ws.addEventListener("message", (e) => { const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
  if (m.method === "Runtime.exceptionThrown") logs.push("exception: " + (m.params.exceptionDetails?.exception?.description ?? m.params.exceptionDetails?.text));
  if (m.method === "Runtime.consoleAPICalled" && m.params.type !== "log" && m.params.type !== "debug") logs.push(m.params.type + ": " + m.params.args.map((a) => a.value ?? a.description).join(" ").slice(0, 300)); });
const send = (method, params = {}) => new Promise((r) => { const n = ++id; pending.set(n, r); ws.send(JSON.stringify({ id: n, method, params })); });
const ev = async (expression, awaitPromise = false) => { const r = await send("Runtime.evaluate", { expression, awaitPromise, returnByValue: true });
  if (r.result?.exceptionDetails) throw new Error(r.result.exceptionDetails.exception?.description ?? r.result.exceptionDetails.text); return r.result?.result?.value; };

try {
  await send("Page.enable"); await send("Runtime.enable");
  await send("Emulation.setDeviceMetricsOverride", { width: 1920, height: 1080, deviceScaleFactor: 1, mobile: false });
  await send("Page.navigate", { url: pathToFileURL(join(DIR, "index.html")).href + "#tools" });
  for (let i = 0; i < 200; i++) { await sleep(100); if (await ev("typeof window.__animation === 'object'")) break; }
  const res = await ev(`window.__animation.load(${JSON.stringify(files)}).then(r => JSON.stringify(r))`, true);
  const loaded = JSON.parse(res);
  if (loaded.error) throw new Error("load failed: " + JSON.stringify(loaded.error));
  console.log("meta", JSON.stringify(loaded.meta).slice(0, 600));
  console.log("score", JSON.stringify(await ev("JSON.stringify(window.__animation.scoreReport())")).slice(0, 400));
  console.log("fonts", await ev("[...document.fonts].map(f => f.family + ' ' + f.weight + ' ' + f.status).join(' | ')"));

  if (verb === "stills") {
    const out = resolve(outDir ?? mkdtempSync(join(tmpdir(), "v3stills-"))); mkdirSync(out, { recursive: true });
    for (const t of arg.split(",").map(Number)) {
      const url = await ev(`window.__animation.frame(${t}, { scale: 1 })`, true);
      const f = join(out, `t_${t.toFixed(2)}.png`); writeFileSync(f, Buffer.from(url.split(",")[1], "base64")); console.log(f);
    }
  } else if (verb === "export") {
    console.log("estimate", JSON.stringify(await ev("JSON.stringify(window.__animation.estimateExport({ height: 1080, fps: 60, quality: 'high' }))", true)));
    await ev(`window.__prog = null; window.__done = window.__animation.exportFilm({ title: 'film', height: 1080, fps: 60, quality: 'high', supersample: ${process.env.MOTION_SUPERSAMPLE === '1'},
      onProgress: (d, t, p) => { window.__prog = [d, t, p]; } }).then(r => (window.__res = r), e => (window.__res = { error: String(e && e.stack || e) })); 0`);
    let last = "";
    for (;;) { await sleep(2000);
      const s = await ev("JSON.stringify({ p: window.__prog, r: window.__res ?? null })"); const { p, r } = JSON.parse(s);
      if (r) { if (r.error) throw new Error("export failed: " + r.error);
        console.log("result", JSON.stringify({ ...r, blob: undefined }));
        const chunks = []; const step = 3 * 1024 * 1024;
        for (let off = 0; off < r.bytes; off += step) chunks.push(Buffer.from(await ev(`window.__animation.read(${JSON.stringify(r.blob)}, ${off}, ${step})`), "base64"));
        const buf = Buffer.concat(chunks); if (buf.length !== r.bytes) throw new Error(`read ${buf.length} of ${r.bytes} bytes`);
        writeFileSync(resolve(arg), buf); console.log("wrote", resolve(arg), buf.length, "bytes", r.mime); break; }
      const line = JSON.stringify(p); if (line !== last) { console.log("progress", line); last = line; } }
  }
} catch (e) { console.error(String(e.message ?? e)); process.exitCode = 1; }
finally {
  for (const l of logs.slice(0, 40)) console.log("page " + l);
  ws.close(); const gone = new Promise((r) => chrome.once("exit", r)); chrome.kill(); await gone;
  try { rmSync(profile, { recursive: true, force: true, maxRetries: 5 }); } catch {}
}
