"""Write index.html for the video site from <site>/videos.tsv (branch, file, date), newest version first.

Run by .github/workflows/video-site.yml. Every MP4 name follows the repo rule
v<N>_<Project>_<length>_<what-it-is>.mp4, so the titles come from the file names.
"""
import html
import re
import sys
from pathlib import Path

site = Path(sys.argv[1])
rows = [line.split("\t") for line in (site / "videos.tsv").read_text().splitlines() if line.strip()]
REPO = "https://github.com/edison9733/sus_animation"


def version_key(name):
    m = re.match(r"v(\d+)(?:\.(\d+))?", name)
    return (int(m.group(1)), int(m.group(2) or 0)) if m else (-1, 0)


def words(part):
    return part.replace("-", " ")


cards = []
for branch, name, date in sorted(rows, key=lambda r: version_key(r[1]), reverse=True):
    parts = Path(name).stem.split("_")
    ver = parts[0]
    project = words(parts[1]) if len(parts) > 1 else ""
    length = parts[2].replace("s", " s") if len(parts) > 2 else ""
    what = words("_".join(parts[3:])) if len(parts) > 3 else ""
    latest = branch == "main"
    size = (site / name).stat().st_size / 1e6
    web = site / "web" / name
    light = web.exists()
    play = f"web/{name}" if light else name
    play_mb = (web if light else site / name).stat().st_size / 1e6
    sd = site / "web" / "480" / name
    sd_src = f"web/480/{name}" if sd.exists() else play
    sd_mb = (sd if sd.exists() else site / play).stat().st_size / 1e6
    poster = f"web/{Path(name).stem}.jpg"
    poster_attr = f' poster="{html.escape(poster)}"' if (site / poster).exists() else ""
    e = html.escape
    cards.append(f"""
  <article class="card{' latest' if latest else ''}" id="{e(ver)}">
    <header>
      <h2>{e(ver)}{' <span class="tag">latest</span>' if latest else ''}</h2>
      <p class="what">{e(what[:1].upper() + what[1:])}</p>
      <p class="meta">{e(project)} · {e(length)} · branch <a href="{REPO}/tree/{e(branch)}"><code>{e(branch)}</code></a></p>
    </header>
    <video controls playsinline preload="none"{poster_attr} src="{e(play)}" data-hd="{e(play)}" data-sd="{e(sd_src)}"></video>
    <p class="links"><a href="{e(play)}">720p ({play_mb:.1f} MB)</a> · <a href="{e(sd_src)}">480p ({sd_mb:.1f} MB)</a> · <a href="{e(name)}">Full quality</a> · <a href="{e(name)}" download>Download the original ({size:.1f} MB)</a></p>
  </article>""")

page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FloodSafe Videos</title>
<style>
  :root {{ --ground:#F1ECE2; --card:#FBF8F2; --ink:#13283F; --soft:#4A5A6C; --main:#2669A6; --accent:#C24A33; --line:#DCD3C4; }}
  @media (prefers-color-scheme: dark) {{ :root {{ --ground:#0F1C2B; --card:#16263A; --ink:#EEF2F6; --soft:#A9B6C4; --main:#6FA8DC; --accent:#E07A62; --line:#2A3D55; }} }}
  * {{ box-sizing:border-box }}
  body {{ margin:0; background:var(--ground); color:var(--ink); font:16px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif }}
  main {{ max-width:1040px; margin:0 auto; padding:32px 16px 64px }}
  h1 {{ font-size:clamp(26px, 4vw, 38px); line-height:1.15; margin:0 0 6px; letter-spacing:-0.01em }}
  .lede {{ color:var(--soft); margin:0 0 28px; max-width:62ch }}
  .card {{ background:var(--card); border:1px solid var(--line); border-radius:14px; padding:18px; margin:0 0 22px }}
  .card.latest {{ border-color:var(--main); box-shadow:0 0 0 2px color-mix(in srgb, var(--main) 25%, transparent) }}
  h2 {{ margin:0; font-size:22px; display:flex; align-items:center; gap:10px }}
  .tag {{ font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:.06em; color:#fff; background:var(--accent); padding:2px 8px; border-radius:99px }}
  .what {{ margin:4px 0 2px; font-weight:600 }}
  .meta, .links {{ margin:0; color:var(--soft); font-size:14px }}
  video {{ display:block; width:100%; aspect-ratio:16/9; background:#000; border-radius:10px; margin:14px 0 10px }}
  a {{ color:var(--main) }}
  code {{ font-size:13px }}
  footer {{ color:var(--soft); font-size:14px }}
  .quality {{ display:flex; flex-wrap:wrap; align-items:center; gap:8px; margin:0 0 22px; font-size:14px; color:var(--soft) }}
  .quality button {{ font:inherit; color:var(--ink); background:var(--card); border:1px solid var(--line); border-radius:99px; padding:5px 14px; cursor:pointer }}
  .quality button[aria-pressed="true"] {{ background:var(--main); border-color:var(--main); color:#fff }}
  #qnote {{ flex-basis:100% }}
</style>
</head>
<body>
<main>
  <h1>FloodSafe Sanitation Gambella: pitch animation</h1>
  <p class="lede">Every version of the film, newest first. The latest is always the one on <code>main</code>; each older version lives on its own branch of <a href="{REPO}">the repo</a>.</p>
  <div class="quality" role="group" aria-label="Video quality">Quality:
    <button type="button" data-q="hd" aria-pressed="true">720p</button>
    <button type="button" data-q="sd" aria-pressed="false">480p, for a slow connection</button>
    <span id="qnote"></span>
  </div>
  {''.join(cards)}
  <footer>Built from the repo by its "Video site" GitHub Action.</footer>
</main>
<script>
(() => {{
  const vids = [...document.querySelectorAll("video[data-sd]")];
  const btns = [...document.querySelectorAll(".quality button")];
  const note = document.getElementById("qnote");
  const setQ = (q, why) => {{
    vids.forEach((v) => {{
      const want = v.dataset[q];
      if (v.getAttribute("src") === want) return;
      const t = v.currentTime, playing = !v.paused;
      v.src = want;
      if (t > 0) v.currentTime = t;
      if (playing) v.play().catch(() => {{}});
    }});
    btns.forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.q === q)));
    note.textContent = why || "";
  }};
  btns.forEach((b) => b.addEventListener("click", () => {{
    try {{ localStorage.setItem("fs-quality", b.dataset.q); }} catch (e) {{}}
    setQ(b.dataset.q, "");
  }}));
  let saved = null;
  try {{ saved = localStorage.getItem("fs-quality"); }} catch (e) {{}}
  if (saved === "hd" || saved === "sd") {{ setQ(saved, ""); return; }}
  // No choice saved: time the poster images. Below about 60 KB/s the 720p copy would pause to load, so play 480p.
  const slow = "Your connection looks slow, so the 480p copy plays. Pick 720p for a sharper picture.";
  window.addEventListener("load", () => {{
    const rs = performance.getEntriesByType("resource").filter((r) => /\\.jpg$/.test(r.name) && r.transferSize > 0);
    if (rs.length) {{
      const bytes = rs.reduce((a, r) => a + r.transferSize, 0);
      const ms = Math.max(...rs.map((r) => r.responseEnd)) - Math.min(...rs.map((r) => r.responseStart));
      if (ms > 0 && (bytes / ms) * 1000 < 60000) setQ("sd", slow);
    }} else if (navigator.connection && navigator.connection.downlink && navigator.connection.downlink < 0.5) {{
      setQ("sd", slow);
    }}
  }});
}})();
</script>
</body>
</html>
"""
(site / "index.html").write_text(page)
(site / ".nojekyll").write_text("")
print(f"index.html: {len(cards)} videos")
