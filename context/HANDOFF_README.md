# FloodSafe Sanitation Gambella: animation handoff

Read this first. It is the hand-over from a Claude (Cowork) session, 13–19 Nov 2026, so that Claude Code can continue.

## Who and what

- **Edison Liu**, an ECE student at ZJUI, is on a team entry in the **GSC 2026–27 Student Challenge (Phase 1, IGNITE)**. The project is **FloodSafe Sanitation**: a low-cost kit that upgrades existing pit latrines to survive floods and droughts.
- The pilot site is the **Gambela region of western Ethiopia**, starting in the Jikawo, Wantawo and Lare woredas plus one refugee camp.
- **Goal of this session:** a short pitch animation (now 48.5 s, 1920×1080, 60 fps). Edison will add an ElevenLabs voiceover, then the voice and video will be merged into one MP4.

## Where things live

| Thing | Location |
|---|---|
| The live animation (source of truth) | Claude Motion artifact: https://claude.ai/artifact/349Hs6ExK1E7amFfUazCMr (slug `10a29e34-6ea3-49b6-8c57-22648aab059d`) |
| Snapshot of its source code (this zip) | `motion/`: `modules/*.js`, `base.css`, `scenes.json`, `score.js`, `film_script.js`, `assets/` |
| Voiceover script and timings | `voiceover/ELEVENLABS.md`, `voiceover/clips.csv` |
| Merge tool (video + 8 voice clips) | `tools/merge_voiceover.sh`, tested with dummy files |
| Original team inputs | `source/`: draft v2 (.docx) and two deck slides (PNG) |
| Style reference research | `research/teardown_skill_notes.md` |
| Gambella data pack (not in this zip) | Edison's Mac: `~/Downloads/global b lablaa/` (CSV data, maps, 33-slide PPTX, 19-page proposal PDF, HTML report, scripts, earlier session log) |

## How the film code works

The film is a Claude **Motion** artifact. Its player ("kit") runs one module per scene in a sandbox, and `render(t)` must be a pure function of time. This zip has the scene code but not the player runtime, so it will not play on its own. To change the film itself, continue in the Claude app (Cowork), where the artifact tools exist. In Claude Code, use this code as the reference, for example for a re-implementation in Remotion or three.js, or a real Teardown build (see the research notes).

The kit calls the code uses:

- `kit.scene(id, {init, render})`
- `kit.stage`, `kit.h(html)`, `kit.assets.url(name)`
- `seg(t,a,b)`, `lerp`, eases `eo`, `ei`, `eio`, `eob`, `kit.smoothstep`, `kit.rng(seed)`
- `TextFx.fadeFromRight(el, t, t0)`
- `kit.score(fn(S,T))`: a synthesized score (pad, bass, marimba, vibes, drums, fx)

What's in `shared.js`:

- **`window.W`** holds the world:
  - the old 2D yard (`far`, `soil`, `hut`, `pit`, `well`, ...)
  - the **teardown rig**:
    - `W.kin(lv)`: one water level, 0–1, drives everything
    - `W.view` / `W.cam`: orthographic camera with orbit and zoom keys
    - `W.box` / `W.face`: SVG faces drawn as 3D boxes
    - `W.model`: the cut-open yard with its `pose(view, state)`
    - `W.rig`: the console card, the left readout panel and the live gauges on the right
    - `W.callout`: labels on leader lines
    - `W.drops`: rain
- **`W.mapCard`**, defined at the head of `scene-map.js`, puts a team map image in the same window with camera keys.

## Scenes (current, 48.5 s)

| # | id | Starts | Seconds | What's on screen |
|---|---|---|---|---|
| 1 | yard | 0 | 4.5 | Cutaway yard turns; "47% practise open defecation (DHS 2024)"; caption "Toilets that survive the flood" |
| 2 | map | 4.5 | 6 | Team priority map; push to the north-west, ring round Jikawo, Wantawo and Lare; "50% of residents live where a 100-year river flood reaches" |
| 3 | flood | 10.5 | 6.5 | Pit floods and overflows, waste reaches the well; "185,200 displaced by the 2022 flood", "2,194 cholera cases, Jan–May 2025" |
| 4 | cutoff | 17 | 5.5 | "Why pit latrines fail here": unsafe at night, waste reaches wells, 97.2% never emptied, swelling clay cracks pits |
| 5 | zones | 22.5 | 6.5 | Team toilet-zone map; A raised/sealed 211k, B raised slab + lined pit 110k, C lined pit on clay 275k, D steep 36k |
| 6 | kit | 29 | 7.5 | Close-ups as the kit is built: lined walls, raised slab and sliding lid, vent with fly screen, lock and solar light, emergency pack |
| 7 | signal | 36.5 | 5.5 | Gauge float climbs green → yellow → red; at red the lid seals and the pack is used |
| 8 | ask | 42 | 6.5 | "FloodSafe Sanitation Gambella"; 500 households (~2,900 people); USD 540k estimated pilot cost; pilot in Jikawo, Wantawo and Lare plus one refugee camp |

## Where every on-screen figure comes from

All figures are from the Gambella data pack. Do not add numbers without a source.

| Figure | Source |
|---|---|
| 47% open defecation | DHS 2024, regional figure 46.9% |
| 50% of residents in 100-year flood reach | Own analysis: JRC flood maps + WorldPop 2020, cells with flood ≥10% |
| 185,200 displaced, 2022 | OCHA/GDACS (`gambella_flood_drought_events.csv`) |
| 2,194 cholera cases, Jan–May 2025 | WHO/regional reports (`gambella_economy_sanitation.csv`) |
| 97.2% of on-site toilets never emptied | DHS 2024 |
| Zone people counts | Own zone rules (`sanitation_priority_woredas.csv`) |
| 500 households, ~2,900 people, USD 540k | Team assumptions and own estimate (`budget_*.csv`), range 333k–818k; labelled "estimated" |
| v3.2: Ethiopia 27% open defecation (yard chart) | DHS 2024-25, population practising open defecation, Ethiopia 27.2% (`gambella_economy_sanitation.csv`) |
| v3.2: people displaced by floods per year, 2019–2025 (flood chart) | `gambella_flood_drought_yearly.csv`, column `flood_displaced`: 11,128 · 18,819 · 11,749 · 185,200 · 25,140 · 41,060 · 35,410 |
| v3.2: never emptied, Gambela 97% vs Ethiopia 89% (problem chart) | DHS 2024-25: 97.2% and 89.4% (`gambella_economy_sanitation.csv`) |
| v3.2: people in each zone as bars (zones chart) | Same zone counts as above (`sanitation_priority_woredas.csv`) |
| v3.2: USD 350 per household, range 200–500 (kit scene) | `budget_estimate.csv`, line 4, zone B raised slab + lined pit, unit cost low / mid / high; labelled "estimate" |
| v3.2: budget split (pilot scene) | `budget_summary.csv`, mid totals: toilet units (zones A + B) 291k, staff and transport 95k, other activities 73k (lines 1, 2, 5, 6, 8, 9), contingency 49k, gauges and packs 32k; sum 540,280 |

The maps are labelled "own analysis" in the window title bar.

## Next steps

1. Edison exports the MP4 from the artifact page (Export button).
2. Edison generates the 8 clips in ElevenLabs from `voiceover/ELEVENLABS.md`, named `01.mp3` … `08.mp3`. He can do this in the ElevenLabs app, or via its MCP server (setup in the same file).
3. Merge them: `tools/merge_voiceover.sh FloodSafe.mp4 path/to/clips FloodSafe_with_voiceover.mp4`. Clips are placed at the scene starts and the music ducks under the voice. If a clip runs past its scene, shorten the text or speed it up. Don't shift the start times, because they match the cuts.
4. Open items Edison may raise:
   - make it longer or shorter
   - a vertical 1080×1920 version for Reels (a second film, recomposed rather than cropped)
   - a real Teardown 3D build
   - matching the team's Canva deck (Edison owns the "06 Impact" section, slides 21–22)

## History of the animation

- **v1 (13 Nov):** a 30 s flat 2D "ground cutaway" in the FloodSafe deck colours (cream #F1ECE2, river blue #2669A6, navy #13283F, brick red #C24A33), built from draft v2 and two slides.
- **v2 (16 Nov):** restyled after the Instagram reel promoting the "Teardown" Claude Code skill (see research notes). It became a 3D turntable cutaway in a console window, with live gauges and close-ups.
- **v3 (19 Nov):** rebuilt on the Gambella data pack, with the team's maps, Gambella figures, a new "Why pits fail" scene, a zones scene, a lock and solar light, and a 48.5 s cut with a matching score.
- **v3.1 (19 Nov):** scene 7 ("The signal") rebuilt as a detailed Anatomy isometric figure and spliced into the v3 export.
- **v3.2 (20 Nov):** after the team watched v3.1 (feedback: better animation quality, more detailed modelling, narration aligned with better data visualisation). Animated charts in six scenes, a cost figure in the kit scene, a solar panel, vent screen and brick courses on the latrine model, a supersampled export, and `voiceover/NARRATION_v3.2.md`, a 2-minute live narration with three pause points for the team's recording. Timings are unchanged (48.5 s), so the ElevenLabs clips and scene 7 splice still line up. Source: `animation/motion/`.
