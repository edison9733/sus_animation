# Rules for this repo (read before changing anything)

This repo holds the FloodSafe Sanitation Gambella pitch animation. `README.md` has the full picture. These are the rules:

1. **The latest animation is always on `main`.** Its MP4 sits at the repo root of `main`. It is the only MP4 at the root.
2. **Every earlier animation lives on its own branch.** Each branch holds that version's MP4, plus its source where one exists.
   - **Branch names:** `v<N>-<short-description>`, for example `v2-teardown-turntable-30s`.
   - **MP4 file names:** a one-line description, `v<N>_<Project>_<length>_<what-it-is>.mp4`, with no spaces, `-` inside a part and `_` between parts.
3. **When a new version is made:**
   - **Save the old one first.** Branch off `main` before changing anything, name the branch after the version that is on `main` now, keep only that version's MP4 on it, and push it.
   - **Then update `main`.** Replace the source and the MP4 there.
   - **Then update the README.** Add the new MP4's "Play" links (the 720p and 480p copies on GitHub Pages) and "Full quality" link to the pinned "📌 Videos (MP4)" table at the top, and re-point the old version's download link to its branch. The video site (`.github/workflows/video-site.yml`) rebuilds itself on each push to `main`. Add one line per branch to the branch table and move "(latest)". Never delete an old branch.
4. **Two parts.** `context/` is what the film says and where its figures come from. `animation/` is the source, the tools and the agent skills (`skills/`). Keep new files in the right part.
5. **Figures need a source.** Every number on screen must come from `context/data-pack/` and be listed in the figure table in `context/HANDOFF_README.md`. Don't invent numbers. The proposal gives no sizes or groundwater depths, so drawings show none.
6. **The film's source is `animation/motion/`.** Edit the scene modules there and render the MP4 with `animation/tools/motion-export.mjs` (its header says how to set it up; use `MOTION_SUPERSAMPLE=1`). Then splice the Anatomy scene 7 in with `animation/anatomy-scene7/splice_scene7.sh`. The Claude Motion artifact (claude.ai/artifact/349Hs6ExK1E7amFfUazCMr) still holds v3 and is not kept in step.
7. **Skills.** The skills used are listed in the README. If you use a new one, add it to that table. Keep its licence if you copy it into `skills/`.

## Branches now

| Branch | One-line description |
|---|---|
| `main` | v3.2 (latest): data charts in 6 scenes, maps coloured to the district borders, a more detailed model, a sharper export, a 2-minute narration script |
| `v3.1-anatomy-gauge-scene` | v3.1: v3 with scene 7 rebuilt as an Anatomy isometric gauge figure |
| `v3-gambella-data-48s` | v3: 48.5 s rebuild on the Gambella data pack, team maps, 8 scenes |
| `v2-teardown-turntable-30s` | v2: 30 s 3D turntable cutaway in a console window, global figures |
| `v1-flat-2d-cutaway-30s` | v1: 30 s flat 2D ground cutaway in the deck colours (MP4 still missing) |
