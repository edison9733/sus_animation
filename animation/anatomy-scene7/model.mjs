// The one model. Same numbers as the v3 film's W.kin(lv) in motion/modules/shared.js,
// rescaled from the film's 360-deep ground block to this figure's 150-deep block.
// lv runs from 0 (dry season) to 1 (the design flood: the worst remembered flood, marked on a fixed post).
// The proposal gives no sizes or depths (groundwater depth "must be measured on site"), so nothing here is in metres.

export const BLOCK_DEPTH = 150;      // ground surface z = 0, block bottom z = -150
export const FLOOD_MAX = 44;         // flood depth over the yard at lv = 1 = the design-flood mark
export const PLINTH = 46;            // plinth height: "plinth above the design flood"
export const PEG = [0.32, 0.67];     // green below 0.32, yellow to 0.67, red above (the film's thresholds)
export const ROD = 190;              // float to pointer: the pointer rides the groundwater 190 units higher
export const WORDS = ["use as usual", "treat drinking water", "seal the lid, use the pack"];
export const COLOURS = ["green", "yellow", "red"];

const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));

export function kin(lv) {
  lv = clamp(lv);
  const gw = -BLOCK_DEPTH * (290 - 190 * lv) / 360;          // groundwater surface, z
  const h = FLOOD_MAX * clamp((lv - 0.5) / 0.5);              // floodwater depth over the yard
  const sig = lv < PEG[0] ? 0 : lv < PEG[1] ? 1 : 2;
  return { lv, gw, h, sig, pointer: gw + ROD };
}

// The pointer height at each peg boundary, so the coloured bands on the staff are where the model switches.
export const BANDS = [0, PEG[0], PEG[1], 1].map((lv) => kin(lv).pointer);

// The film's scene 7 ("The signal", 36.5–42 s, 5.5 s), copied from scene-signal.js:
// the level rises in two steps, then at red the household slides the lid shut.
export const seg = (t, a, b) => clamp((t - a) / (b - a));
export const eio = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
export const FILM_SECONDS = 5.5;
export function filmAt(t) {
  const lv = 0.1 + 0.4 * eio(seg(t, 0.9, 1.8)) + 0.42 * eio(seg(t, 2.5, 3.4)) + 0.012 * Math.sin(t * 2.1);
  return { lv, lid: eio(seg(t, 3.8, 4.3)) };
}

// The idle tour on the page: the film's 5.5 s, a hold, then the water drains and the lid opens again.
export const TOUR_SECONDS = 11;
export function tourAt(t) {
  t %= TOUR_SECONDS;
  if (t < 7.2) return filmAt(Math.min(t, FILM_SECONDS));
  const end = filmAt(FILM_SECONDS);
  const d = eio(seg(t, 7.2, 9.6));
  return { lv: end.lv + (0.1 - end.lv) * d, lid: 1 - eio(seg(t, 9.2, 9.9)) };
}

export function readoutOf(k, lid) {
  const flood = Math.round((100 * k.h) / FLOOD_MAX);
  const state = k.sig === 2 && lid > 0.98 ? "lid sealed" : lid > 0.02 && lid < 0.98 ? "lid sliding" : "lid open";
  return `${COLOURS[k.sig]} · ${state} · flood ${flood}% of mark`;
}
