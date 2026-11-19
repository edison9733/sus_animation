# FloodSafe scene 7, built with the Anatomy skill

This folder rebuilds scene 7 of the v3 FloodSafe Gambella film ("The signal", 36.5–42.0 s). It uses the Anatomy agent skill (github.com/wheresryan22/anatomy, MIT), a copy of which is in this repo at `skills/anatomy`.

## The object

The object is a Zone B latrine (raised slab and lined pit), cut open through its pit.
- **The gauge.** A float sits in a slotted well next to the latrine and rides the groundwater. Its rod carries a pointer up a staff painted green, yellow and red.
- **The flood.** As the level rises, the yard floods up to the design-flood mark on the post. The plinth stays above that mark.
- **The lid.** At red, the sliding lid is shut.
- **Other parts.** The cutaway also shows the inside lock, the solar light, the screened vent, the emergency pack, the handwashing point and the family's shallow well.

## One model, the film's model

`model.mjs` holds the film's own `W.kin(lv)`, rescaled to this block. Everything reads from it: the gauge, the floodwater, the lid and the readout.
- Peg thresholds: 0.32 and 0.67.
- The flood reaches the mark at lv = 1, and the plinth is 46 high against a 44 mark.
- The 5.5 s level curve and the lid timing are copied from `scene-signal.js`, so the clip fits the voiceover line for scene 7.

The proposal gives no dimensions and no groundwater depth ("must be measured on site"). So the figure shows no metres, and its caption says so.

## Files

| File | What it is |
|---|---|
| `build.mjs` | Builds the figure. `node build.mjs` writes the interactive page; `node build.mjs --film` writes the 1920×1080 film frame |
| `model.mjs`, `dyn.mjs` | The model, and the parts that change with the water. The page inlines the same source |
| `floodsafe-signal.html` | Interactive figure: move across it to raise the water, or use the arrow keys. An idle tour loops when nobody touches it |
| `floodsafe-signal-film.html` | Film frame with `window.renderAt(t)`, pure in t |
| `render-film.mjs` | Renders 330 frames in headless Chrome and encodes `FloodSafe_scene7_signal_anatomy.mp4` (5.5 s, 60 fps) |
| `splice_scene7.sh` | Replaces 36.5–42.0 s of your exported v3 MP4 with this clip and keeps the film's audio |

## Put it in the film

1. Export the v3 MP4 from the Motion artifact page.
2. Run the splice script:
   ```
   ./splice_scene7.sh ~/Downloads/FloodSafe.mp4 FloodSafe_v3_anatomy.mp4
   ```
3. Run `tools/merge_voiceover.sh` on the result, as before. The cut times are unchanged.

## Checks run

- The Anatomy line check reports `line ends: 0` across 435 line ends.
- The console is clean.
- Close-ups were checked of the interior, the gauge and the flood state.
