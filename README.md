# FloodSafe Sanitation Gambella: pitch animation

## 📌 Watch the videos (MP4)

**Latest: [▶ v3.1, 48.5 s, with the Anatomy gauge scene](https://github.com/edison9733/sus_animation/blob/main/v3.1_FloodSafe-Gambella_48s_teardown-film-with-anatomy-gauge-scene.mp4)**

| Version | Watch on GitHub | Download the MP4 | Branch |
|---|---|---|---|
| **v3.1 (latest)** | [▶ v3.1_FloodSafe-Gambella_48s_teardown-film-with-anatomy-gauge-scene.mp4](https://github.com/edison9733/sus_animation/blob/main/v3.1_FloodSafe-Gambella_48s_teardown-film-with-anatomy-gauge-scene.mp4) | [⬇ download (17.7 MB)](https://github.com/edison9733/sus_animation/raw/main/v3.1_FloodSafe-Gambella_48s_teardown-film-with-anatomy-gauge-scene.mp4) | `main` |
| v3 | [▶ v3_FloodSafe-Gambella_48s_teardown-cutaway-on-team-maps-and-data.mp4](https://github.com/edison9733/sus_animation/blob/v3-gambella-data-48s/v3_FloodSafe-Gambella_48s_teardown-cutaway-on-team-maps-and-data.mp4) | [⬇ download (46.5 MB)](https://github.com/edison9733/sus_animation/raw/v3-gambella-data-48s/v3_FloodSafe-Gambella_48s_teardown-cutaway-on-team-maps-and-data.mp4) | `v3-gambella-data-48s` |
| v2 | [▶ v2_FloodSafe_30s_teardown-turntable-cutaway-global-figures.mp4](https://github.com/edison9733/sus_animation/blob/v2-teardown-turntable-30s/v2_FloodSafe_30s_teardown-turntable-cutaway-global-figures.mp4) | [⬇ download (17.9 MB)](https://github.com/edison9733/sus_animation/raw/v2-teardown-turntable-30s/v2_FloodSafe_30s_teardown-turntable-cutaway-global-figures.mp4) | `v2-teardown-turntable-30s` |
| v1 | `v1_FloodSafe_30s_flat-2D-ground-cutaway-deck-colours.mp4` (missing, no export found) | — | `v1-flat-2d-cutaway-30s` |

"Watch" opens the video in GitHub's player. "Download" saves the MP4 file.

This repo holds the pitch animation for **FloodSafe Sanitation Gambella**, a GSC 2026–27 Student Challenge entry (Phase 1, IGNITE). The project is a low-cost kit that upgrades existing pit latrines so they survive floods and droughts. The pilot covers Jikawo, Wantawo and Lare in Gambela, western Ethiopia, plus one refugee camp.

> **Rule: the latest animation is always on `main`.** Every earlier animation lives on its own branch, with its own MP4. Every MP4's file name is a one-line description of that version.

## Branches: one per animation version

| Branch | Version | Date | MP4 on that branch | One-line description |
|---|---|---|---|---|
| [`main`](../../tree/main) | **v3.1 (latest)** | 19 Nov 2026 | `v3.1_FloodSafe-Gambella_48s_teardown-film-with-anatomy-gauge-scene.mp4` | v3 with scene 7 ("The signal") rebuilt as an Anatomy isometric gauge figure |
| [`v3-gambella-data-48s`](../../tree/v3-gambella-data-48s) | v3 | 19 Nov 2026 | `v3_FloodSafe-Gambella_48s_teardown-cutaway-on-team-maps-and-data.mp4` | 48.5 s rebuild on the Gambella data pack: team maps, Gambella figures, 8 scenes |
| [`v2-teardown-turntable-30s`](../../tree/v2-teardown-turntable-30s) | v2 | 16 Nov 2026 | `v2_FloodSafe_30s_teardown-turntable-cutaway-global-figures.mp4` | 30 s 3D turntable cutaway in a console window, with global figures |
| [`v1-flat-2d-cutaway-30s`](../../tree/v1-flat-2d-cutaway-30s) | v1 | 13 Nov 2026 | `v1_FloodSafe_30s_flat-2D-ground-cutaway-deck-colours.mp4` (**missing, to be added**) | 30 s flat 2D ground cutaway in the deck colours |

To get an older version: `git checkout <branch>`, or switch branch on GitHub and download its MP4.

## What's in `main`

The repo has two parts: the **context** (what the film is about and where every figure comes from) and the **animation** (the film's source, its tools and the agent skills used to make it).

```
v3.1_…anatomy-gauge-scene.mp4    the latest film (48.5 s, 1920×1080, 60 fps)
CLAUDE.md                        the repo rules, written for Claude (and for people)
context/                         PART 1: context
  HANDOFF_README.md              full handoff: scenes, timings, where each figure comes from
  voiceover/                     ElevenLabs script, clip timings (clips.csv), voice-clone reading text
  team-source/                   team draft v2 (.docx) and two deck slides (PNG)
  research/                      notes on the Teardown skill (the v2/v3 style reference)
  data-pack/                     the Gambella data pack: CSVs, maps, proposal PDF, deck PPTX, report, scripts, session log
animation/                       PART 2: animation
  motion-v3/                     source of the v3 Motion film (scene modules, CSS, score, assets)
  anatomy-scene7/                scene 7 rebuilt with the Anatomy skill, plus its build, render and splice scripts
  tools/merge_voiceover.sh       merges the 8 voice clips into the film at the scene starts
  tools/motion-export.mjs        exports a Motion film to MP4 from Claude Code, with the player's own exporter
skills/                          agent skills used (see below)
  anatomy/                       copy of the Anatomy skill (MIT)
```

## Agent skills and tools used

| Skill or tool | Used for | Where |
|---|---|---|
| **Motion** (Claude app animation artifact) | Building and playing the film, v1 to v3. Scenes are HTML, CSS and JS with `render(t)` pure in time | Live film: claude.ai/artifact/349Hs6ExK1E7amFfUazCMr (editable only in the Claude app). Source snapshot: `animation/motion-v3/`. MP4: the Export button, or `animation/tools/motion-export.mjs` |
| **Teardown** (elvarofficial/teardown, Claude Code skill) | Style reference for v2 and v3: a 3D cutaway in a console window with live gauges. Used as a reference, not run | `context/research/teardown_skill_notes.md` |
| **Anatomy** (github.com/wheresryan22/anatomy, MIT) | v3.1 scene 7: the latrine and its groundwater gauge as a detailed isometric figure, driven by the film's water-level model | `skills/anatomy/` (copy), `animation/anatomy-scene7/` |
| ElevenLabs (voice, not a skill) | The voiceover: 8 clips, one per scene | `context/voiceover/ELEVENLABS.md` |
| ffmpeg (tool) | Merging the voice, splicing scene 7, encoding | `animation/tools/`, `animation/anatomy-scene7/splice_scene7.sh` |

## Adding a new version (the workflow)

1. **Save the current latest to its own branch first.** Branch off `main` *before* changing anything, and name the branch `v<N>-<short-description>`, for example `git switch -c v3.1-anatomy-gauge-scene main`. On that branch, remove any older MP4s so it keeps only its own video. Push it.
2. **Put the new version on `main`.**
   - Replace the source.
   - Delete the old MP4.
   - Add the new MP4 at the repo root, named `v<N>_<what-it-is-in-one-line>.mp4`: no spaces, words joined with `-`, parts with `_`.
3. **Update the tables above.**
   - **Videos table:** add a row with "Watch" (`https://github.com/edison9733/sus_animation/blob/<branch>/<file>.mp4`) and "Download" (`.../raw/<branch>/<file>.mp4`) links. Point the old latest row at its new branch, and the "Latest" line at the new MP4 on `main`.
   - **Branch table:** add a row for the new version and move "(latest)". Keep one line per branch.
4. Commit and push both branches.

## Sources and links

- **Team deck (Canva):** canva.link/wgih1tj760ixhqn. Teammates edit it, so check it against the film before matching. Slide 16 still shows the v2 film.
- **Shared Drive folder:** drive.google.com/drive/folders/1N6ETbdtFfcJ4A9MJDBKQ9KzrQJ1bcx1t
- **Figures:** every on-screen figure comes from the data pack. The table "Where every on-screen figure comes from" in `context/HANDOFF_README.md` gives the source of each one. Don't add a number without a source.
