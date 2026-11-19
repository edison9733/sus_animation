// Fig 7 · The signal: the FloodSafe Zone B latrine, cut open on the plane y = CUT, built with the Anatomy skill.
// node build.mjs            -> floodsafe-signal.html (interactive figure, cream theme)
// node build.mjs --film     -> floodsafe-signal-film.html (1920 x 1080 frame for the v3 film; window.renderAt(t))
import { writeFileSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import * as k from "../../skills/anatomy/kit/iso-kit.mjs";
import { kitScript } from "../../skills/anatomy/scripts/inline-kit.mjs";
import * as M from "./model.mjs";
import { dynamic } from "./dyn.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const FILM = process.argv.includes("--film");
const WIDTH = 640, HEIGHT = 380;

// ---- world plan (x right, y back to front, z up; the cut plane is y = CUT) ----
const CUT = 60;
const DEPTH = M.BLOCK_DEPTH;
const BLOCK = { x: -170, y: -110, w: 340, d: CUT + 110, r: 0 };
const PX = -70, PIT_R = 36, PIT_WALL = 6, PIT_FLOOR = -118, RINGS = 5;
const PLINTH = { x: -130, y: -50, w: 120, d: CUT + 50, r: 0 };
const SLAB = { x: -134, y: -54, w: 128, d: CUT + 54, r: 0 };
const SLAB_TOP = M.PLINTH + 8;
const ROOF_Z = 150;
const GX = 40, GR = 7, GBORE = 5, GTOP = 60, GDEEP = 140, ROD_Y = 56;
const STAFF = { x: 50, y: 42, w: 10, d: 5, r: 0.6 };
const STAFF_TOP = 160;
const LID_TRAVEL = 20;
const POST = { x: 146, y: -96, w: 8, d: 8, r: 0.8 };
const WASH = [92, 108];
const WY = -60;
const WELL = [122, 24], WELL_R = 13;

const P = k.fitProjection(
  [...k.boxCorners(BLOCK, -DEPTH, 0), [-142, -62, 158], [2, 0, 158], [-6, CUT, ROOF_Z], [-22, -40, 197], [STAFF.x + STAFF.w, STAFF.y, STAFF_TOP + 2]],
  WIDTH, HEIGHT, { pad: 30, azimuth: 58, elevation: 30 },
);
const at = (p) => k.iso(p, P);
const S = (paths, style) => k.solidSvg(paths, style);
const L = (d, style) => k.lineSvg(d, style);
const D = (pts, style) => k.dotsSvg(pts, style);
const poly = (pts, cls, extra = "") => `<path class="${cls}" d="${k.pathOf(pts.map(at), true)}"${extra}/>`;
const onCut = (x0, x1, z0, z1, cls) => poly([[x0, CUT, z0], [x1, CUT, z0], [x1, CUT, z1], [x0, CUT, z1]], cls);
const onSide = (x, y0, y1, z0, z1, cls) => poly([[x, y0, z0], [x, y1, z0], [x, y1, z1], [x, y0, z1]], cls);
const seg3 = (a, b) => k.pathOf([at(a), at(b)]);
const wavy = (z, amp, phase, n = 40) => Array.from({ length: n + 1 }, (_, i) => {
  const x = BLOCK.x + (BLOCK.w * i) / n;
  return [x, z + amp * Math.sin(x / 37 + phase) + amp * 0.5 * Math.sin(x / 13 + phase * 2)];
});
const wavySide = (z, amp, phase, n = 20) => Array.from({ length: n + 1 }, (_, i) => {
  const y = CUT - (BLOCK.d * i) / n;
  return [y, z + amp * Math.sin((BLOCK.x + BLOCK.w) / 37 + phase + (CUT - y) / 29)];
});

const G = {
  CUT, DEPTH, BLOCK, GX, GBORE, GDEEP, GTOP, ROD_Y, LID_TRAVEL,
  COLLARS: [
    { id: "plinth", plan: PLINTH },
    { id: "gauge", round: true, cx: GX, cy: CUT, r: GR, cutY: CUT },
    { id: "staff", plan: STAFF },
    { id: "post", plan: POST },
    { id: "wash0", plan: { x: WASH[0] - 1.5, y: WY - 1.5, w: 3, d: 3 } },
    { id: "wash1", plan: { x: WASH[1] - 1.5, y: WY - 1.5, w: 3, d: 3 } },
    { id: "well", round: true, cx: WELL[0], cy: WELL[1], r: WELL_R + 0.4, top: 14 },
    { id: "wpost0", plan: { x: WELL[0] - 19, y: WELL[1] - 2, w: 4, d: 4 } },
    { id: "wpost1", plan: { x: WELL[0] + 15, y: WELL[1] - 2, w: 4, d: 4 } },
  ],
};
const draw = dynamic(k, P, G);
const first = FILM ? M.filmAt(0) : M.tourAt(0);
const D0 = draw({ k: M.kin(first.lv), lid: first.lid });
const dyn = (id, cls, extra = "") => `<path data-d="${id}" class="${cls}" d="${D0[id]}"${extra}/>`;

// ---- 1. the ground block, cut through the pit and the gauge ----
function ground() {
  const out = [`<path class="iso-halo" d="${k.haloOf(BLOCK, -DEPTH, DEPTH, P)}"/>`];
  out.push(S(k.slabOf(BLOCK, -DEPTH, DEPTH, P, 2), { tone: "mid" }));
  const xR = BLOCK.x + BLOCK.w;
  // strata on the cut: sand under everything, then topsoil and swelling clay
  out.push(onCut(BLOCK.x, xR, -DEPTH, 0, "fs-sand"), onSide(xR, BLOCK.y, CUT, -DEPTH, 0, "fs-sand fs-side"));
  const top = wavy(-16, 2.2, 0.4), clay = wavy(-122, 3, 1.7);
  out.push(poly([[BLOCK.x, CUT, 0], [xR, CUT, 0], ...top.slice().reverse().map(([x, z]) => [x, CUT, z])], "fs-topsoil"));
  out.push(poly([...clay.map(([x, z]) => [x, CUT, z]), [xR, CUT, -DEPTH], [BLOCK.x, CUT, -DEPTH]], "fs-clay"));
  const sTop = wavySide(-16, 2.2, 0.4), sClay = wavySide(-122, 3, 1.7);
  out.push(poly([[xR, CUT, 0], [xR, BLOCK.y, 0], ...sTop.slice().reverse().map(([y, z]) => [xR, y, z])], "fs-topsoil fs-side"));
  out.push(poly([...sClay.map(([y, z]) => [xR, y, z]), [xR, BLOCK.y, -DEPTH], [xR, CUT, -DEPTH]], "fs-clay fs-side"));
  // groundwater, rising with the model
  out.push(dyn("gwFront", "fs-gw"), dyn("gwSide", "fs-gw fs-side"));
  // grain: seeded specks in each band, and the band lines running edge to edge
  let seed = 7;
  const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  const specks = [];
  for (let i = 0; i < 150; i++) {
    const x = BLOCK.x + 4 + rnd() * (BLOCK.w - 8), z = -4 - rnd() * (DEPTH - 8);
    if (x > PX - PIT_R - PIT_WALL - 3 && x < PX + PIT_R + PIT_WALL + 3 && z > PIT_FLOOR - 4) continue;
    if (x > GX - GR - 4 && x < GX + GR + 4) continue;
    specks.push(at([x, CUT, z]));
  }
  out.push(D(specks, { size: 0.45, tone: "lo" }));
  out.push(L(k.pathOf(top.map(([x, z]) => at([x, CUT, z]))) + k.pathOf(sTop.map(([y, z]) => at([xR, y, z]))), { tone: "mid" }));
  out.push(L(k.pathOf(clay.map(([x, z]) => at([x, CUT, z]))) + k.pathOf(sClay.map(([y, z]) => at([xR, y, z]))), { tone: "mid" }));
  out.push(dyn("gwLine", "iso-line fs-gw-line"));
  // depth ruler strip down the left end of the cut, ticks hanging from its edge
  out.push(onCut(BLOCK.x, BLOCK.x + 7, -DEPTH + 4, -4, "fs-ruler"));
  let minor = "", major = "";
  for (let z = -DEPTH + 8, i = 0; z <= -6; z += 5, i++) (i % 5 === 0 ? (major += seg3([BLOCK.x + 7, CUT, z], [BLOCK.x + 2.4, CUT, z])) : (minor += seg3([BLOCK.x + 7, CUT, z], [BLOCK.x + 4.4, CUT, z])));
  out.push(L(minor, { tone: "lo" }), L(major, { tone: "mid" }));
  out.push(L(k.pathOf([at([BLOCK.x + 7, CUT, -DEPTH + 4]), at([BLOCK.x + 7, CUT, -4])]), { tone: "lo" }));
  out.push(L(k.pathOf([at([BLOCK.x, CUT, -DEPTH + 4]), at([BLOCK.x + 7, CUT, -DEPTH + 4])]) + k.pathOf([at([BLOCK.x, CUT, -4]), at([BLOCK.x + 7, CUT, -4])]), { tone: "lo" }));
  // label plate on the right side, four screws, one engraved word
  const lp = { y0: -60, y1: -20, z0: -40, z1: -26 };
  out.push(onSide(xR, lp.y0, lp.y1, lp.z0, lp.z1, "fs-plate"));
  out.push(L(k.pathOf([at([xR, lp.y0, lp.z0]), at([xR, lp.y1, lp.z0]), at([xR, lp.y1, lp.z1]), at([xR, lp.y0, lp.z1])], true), { tone: "mid" }));
  out.push(D([[lp.y0 + 2, lp.z0 + 2], [lp.y1 - 2, lp.z0 + 2], [lp.y0 + 2, lp.z1 - 2], [lp.y1 - 2, lp.z1 - 2]].map(([y, z]) => at([xR, y, z])), { size: 0.45, tone: "mid" }));
  out.push(k.faceTextSvg(k.sideMatrix([xR, -40], -31.5, P, "right"), "ZONE B", { size: 4.2, tone: "mid", anchor: "middle" }));
  return out.join("");
}

// ---- the lined pit and the gauge well, in section on the cut ----
function sections() {
  const out = [];
  const x0 = PX - PIT_R, x1 = PX + PIT_R;
  out.push(onCut(x0 - PIT_WALL, x1 + PIT_WALL, PIT_FLOOR - 4, 0, "fs-cavity"));
  // the far half of the pit wall: ring joints seen as arcs, landing on the section of the lining
  const ringH = -PIT_FLOOR / RINGS;
  let arcs = "";
  for (let i = 1; i < RINGS; i++) {
    const z = -i * ringH;
    arcs += k.pathOf(Array.from({ length: 25 }, (_, j) => { const a = (j / 24) * Math.PI; return at([PX + PIT_R * Math.cos(a), CUT - PIT_R * Math.sin(a), z]); }));
  }
  out.push(L(arcs, { tone: "lo" }));
  // waste in the bottom: its top surface is a half disc, its face a band on the cut
  const wTop = PIT_FLOOR + 16;
  out.push(poly(Array.from({ length: 25 }, (_, j) => { const a = (j / 24) * Math.PI; return [PX + PIT_R * Math.cos(a), CUT - PIT_R * Math.sin(a), wTop]; }), "fs-waste-top"));
  out.push(onCut(x0, x1, PIT_FLOOR, wTop, "fs-waste"));
  out.push(L(k.pathOf([at([x0, CUT, wTop]), at([x1, CUT, wTop])]), { tone: "mid" }));
  // the lining rings in section, two columns, with their joints
  for (let i = 0; i < RINGS; i++) {
    const za = -i * ringH - 0.6, zb = -(i + 1) * ringH + 0.6;
    for (const [a, b] of [[x0 - PIT_WALL, x0], [x1, x1 + PIT_WALL]]) {
      out.push(onCut(a, b, zb, za, "fs-ring"));
      out.push(L(k.pathOf([at([a, CUT, za]), at([b, CUT, za]), at([b, CUT, zb]), at([a, CUT, zb])], true), { tone: "hi" }));
    }
  }
  // the base ring under the pit floor
  out.push(onCut(x0 - PIT_WALL, x1 + PIT_WALL, PIT_FLOOR - 4, PIT_FLOOR, "fs-ring"));
  out.push(L(k.pathOf([at([x0 - PIT_WALL, CUT, PIT_FLOOR]), at([x1 + PIT_WALL, CUT, PIT_FLOOR]), at([x1 + PIT_WALL, CUT, PIT_FLOOR - 4]), at([x0 - PIT_WALL, CUT, PIT_FLOOR - 4])], true), { tone: "hi" }));
  // the gauge well: slotted pipe in a gravel pack, its water and the float
  const gx0 = GX - GR, gx1 = GX + GR;
  out.push(onCut(gx0 - 4, gx1 + 4, -GDEEP, -GDEEP + 26, "fs-gravel"));
  const gravel = [];
  for (let i = 0; i < 46; i++) { const x = gx0 - 3.5 + ((i * 7.3) % (gx1 - gx0 + 7)), z = -GDEEP + 1.5 + ((i * 5.7) % 23); if (x < GX - GR + 0.5 || x > GX + GR - 0.5) gravel.push(at([x, CUT, z])); }
  out.push(D(gravel, { size: 0.55, tone: "mid" }));
  out.push(onCut(GX - GBORE, GX + GBORE, -GDEEP, 0, "fs-cavity"));
  out.push(dyn("bore", "fs-bore"));
  out.push(dyn("rodLow", "fs-lit-fill"), dyn("float", "fs-lit-fill fs-float"));
  for (const [a, b] of [[gx0, GX - GBORE], [GX + GBORE, gx1]]) {
    out.push(onCut(a, b, -GDEEP, 0, "fs-pipe"));
    out.push(L(k.pathOf([at([a, CUT, 0]), at([a, CUT, -GDEEP]), at([b, CUT, -GDEEP]), at([b, CUT, 0])]), { tone: "hi" }));
    // slots in the screen section: closed slots across the wall
    for (let z = -GDEEP + 4; z < -GDEEP + 24; z += 4) out.push(onCut(a + 0.4, b - 0.4, z, z + 1.4, "fs-slot"));
  }
  out.push(L(k.pathOf([at([gx0 - 4, CUT, -GDEEP]), at([gx0 - 4, CUT, -GDEEP + 26]), at([gx1 + 4, CUT, -GDEEP + 26]), at([gx1 + 4, CUT, -GDEEP])], true), { tone: "lo" }));
  // the cut face's own outline, over its drawings
  out.push(L(k.pathOf([at([BLOCK.x, CUT, 0]), at([BLOCK.x + BLOCK.w, CUT, 0]), at([BLOCK.x + BLOCK.w, CUT, -DEPTH]), at([BLOCK.x, CUT, -DEPTH])], true) + k.pathOf([at([BLOCK.x + BLOCK.w, CUT, 0]), at([BLOCK.x + BLOCK.w, BLOCK.y, 0]), at([BLOCK.x + BLOCK.w, BLOCK.y, -DEPTH]), at([BLOCK.x + BLOCK.w, CUT, -DEPTH])]), { tone: "hi" }));
  return out.join("");
}

// ---- on the yard: stepping stones, then the floodwater sheet ----
function yard() {
  const out = [];
  let seed = 11;
  const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  const pts = [];
  for (let i = 0; i < 120; i++) { const x = BLOCK.x + 5 + rnd() * (BLOCK.w - 10), y = BLOCK.y + 5 + rnd() * (BLOCK.d - 10); if (x > -140 && x < 0 && y > -60) continue; pts.push(at([x, y, 0])); }
  out.push(D(pts, { size: 0.5, tone: "lo" }));
  for (const [x, y, w, d] of [[6, -30, 14, 10], [28, -44, 12, 11], [52, -40, 13, 9], [72, -54, 11, 10]]) {
    out.push(S(k.slabOf({ x, y, w, d, r: 3 }, 0, 1.4, P, 4, 0.4), { tone: "lo", crease: "none" }));
  }
  return out.join("");
}
function flood() {
  return dyn("sheet", "fs-water") + dyn("sheetRim", "iso-line fs-waterline fs-rim") + dyn("sheetFront", "fs-water fs-water-side") + dyn("sheetSide", "fs-water fs-water-side") + dyn("waterline", "iso-line fs-waterline");
}
const collar = (id) => dyn("collar-" + id, "fs-water fs-collar");

// ---- the latrine: plinth, slab, shelter, lid, light, vent, pack, panel ----
function latrine() {
  const out = [];
  const pR = PLINTH.x + PLINTH.w;
  out.push(S(k.slabOf(PLINTH, 0, M.PLINTH, P, 2), { tone: "mid" }));
  // block courses on the outer side and on the cut, joints staggered
  let courses = "";
  for (let i = 1; i < 4; i++) {
    const z = (M.PLINTH * i) / 4;
    courses += seg3([pR, PLINTH.y, z], [pR, CUT, z]) + seg3([PLINTH.x, CUT, z], [PX - 9, CUT, z]) + seg3([PX + 9, CUT, z], [pR, CUT, z]);
  }
  for (let i = 0; i < 4; i++) {
    const z0 = (M.PLINTH * i) / 4, z1 = (M.PLINTH * (i + 1)) / 4, off = i % 2 ? 12 : 0;
    for (let y = PLINTH.y + 18 + off; y < CUT - 4; y += 24) courses += seg3([pR, y, z0], [pR, y, z1]);
    for (let x = PLINTH.x + 14 + off; x < pR - 4; x += 24) if (Math.abs(x - PX) > 13) courses += seg3([x, CUT, z0], [x, CUT, z1]);
  }
  out.push(L(courses, { tone: "lo" }));
  // the drop chute through the plinth and slab, down into the pit
  out.push(onCut(PX - 9, PX + 9, 0, SLAB_TOP, "fs-cavity"));
  out.push(L(k.pathOf([at([PX - 9, CUT, 0]), at([PX - 9, CUT, SLAB_TOP])]) + k.pathOf([at([PX + 9, CUT, 0]), at([PX + 9, CUT, SLAB_TOP])]), { tone: "hi" }));
  out.push(collar("plinth"));
  // the slab, overhanging the plinth
  out.push(S(k.slabOf(SLAB, M.PLINTH, 8, P, 2, 0.6), { tone: "hi", crease: "lo" }));
  out.push(onCut(PX - 9, PX + 9, M.PLINTH, SLAB_TOP, "fs-cavity"));
  out.push(L(k.pathOf([at([PX - 9, CUT, M.PLINTH]), at([PX - 9, CUT, SLAB_TOP])]) + k.pathOf([at([PX + 9, CUT, M.PLINTH]), at([PX + 9, CUT, SLAB_TOP])]), { tone: "hi" }));
  // walls: back and left first (their inner faces show through the cut)
  out.push(S(k.slabOf({ x: -134, y: -54, w: 128, d: 6, r: 0 }, SLAB_TOP, ROOF_Z - SLAB_TOP, P, 2), { tone: "mid" }));
  let courseBack = "";
  for (let z = SLAB_TOP + 12; z < ROOF_Z; z += 12) courseBack += seg3([-128, -48, z], [-12, -48, z]);
  out.push(L(courseBack + seg3([-128, -48, SLAB_TOP], [-128, -48, ROOF_Z]), { tone: "faint" }));
  out.push(S(k.slabOf({ x: -134, y: -48, w: 6, d: CUT + 48, r: 0 }, SLAB_TOP, ROOF_Z - SLAB_TOP, P, 2), { tone: "mid" }));
  // the door in the left wall, seen from inside: planks, a Z brace, hinge pins, and the inside lock (a slide bolt)
  const door = { y0: -24, y1: 30, z0: SLAB_TOP + 2, z1: 140 };
  out.push(S(k.slabOf({ x: -128, y: door.y0, w: 0.8, d: door.y1 - door.y0, r: 0 }, door.z0, door.z1 - door.z0, P, 2), { tone: "mid" }));
  const dx = -127.2;
  let planks = "";
  for (let y = door.y0 + 9; y < door.y1 - 2; y += 9) planks += seg3([dx, y, door.z0], [dx, y, door.z1]);
  out.push(L(planks, { tone: "faint" }));
  out.push(L(seg3([dx, door.y0, door.z0 + 14], [dx, door.y1, door.z0 + 14]) + seg3([dx, door.y0, door.z1 - 14], [dx, door.y1, door.z1 - 14]) + seg3([dx, door.y1, door.z0 + 14], [dx, door.y0, door.z1 - 14]), { tone: "mid" }));
  out.push(D([[door.y0 + 2, door.z0 + 14], [door.y0 + 2, door.z1 - 14]].map(([y, z]) => at([dx, y, z])), { size: 0.7, tone: "hi" }));
  out.push(S(k.slabOf({ x: dx, y: door.y1 - 12, w: 1.6, d: 9, r: 0.4 }, 96, 3.2, P, 2), { tone: "hi", lit: false }));
  out.push(S(k.slabOf({ x: dx, y: door.y1 + 0.5, w: 1.8, d: 3.5, r: 0.4 }, 95, 5.2, P, 2), { tone: "hi" }));
  out.push(S(k.cylinder(-124.6, door.y1 - 8, 1, 99.2, 3, P, 10), { tone: "hi" }));
  // the emergency pack on its shelf against the back wall
  const PZ = SLAB_TOP + 3;
  out.push(S(k.slabOf({ x: -125, y: -46, w: 34, d: 16, r: 0.5 }, SLAB_TOP, 3, P, 2, 0.4), { tone: "mid" }));
  out.push(S(k.slabOf({ x: -122, y: -44, w: 28, d: 13, r: 2 }, PZ, 24, P, 4, 0.6), { tone: "hi", crease: "lo" }));
  let straps = "";
  for (const x of [-115, -101]) straps += k.pathOf([at([x, -44, PZ + 24]), at([x, -31, PZ + 24]), at([x, -31, PZ])]);
  out.push(L(straps, { tone: "mid" }));
  out.push(S(k.slabOf({ x: -112, y: -31, w: 8, d: 2, r: 0.5 }, PZ + 8, 7, P, 2), { tone: "mid" }));
  out.push(S(k.slabOf({ x: -113, y: -48, w: 10, d: 4, r: 1.5 }, PZ + 24, 2.4, P, 3), { tone: "mid" }));
  // the solar lamp on the back wall, its cable up to the roof
  out.push(S(k.slabOf({ x: -60, y: -48, w: 18, d: 7, r: 1.2 }, 110, 9, P, 3, 0.5), { tone: "hi", crease: "lo" }));
  out.push(poly([[-57, -41, 111.4], [-45, -41, 111.4], [-45, -41, 113.8], [-57, -41, 113.8]], "fs-lens"));
  out.push(L(k.pathOf([at([-51, -44.5, 119]), at([-51, -44.5, ROOF_Z])]), { tone: "mid" }));
  out.push(D([at([-51, -44.5, 119])], { size: 0.6, tone: "hi" }));
  // the vent pipe inside the back right corner, up to the roof
  out.push(S(k.cylinder(-22, -40, 5, SLAB_TOP, ROOF_Z - SLAB_TOP, P, 24), { tone: "mid", crease: "none" }));
  out.push(L(k.sideArc(-22, -40, 5, SLAB_TOP + 3, P, 20) + k.sideArc(-22, -40, 5, 100, P, 20), { tone: "lo" }));
  out.push(S(k.cylinder(-22, -40, 6.4, SLAB_TOP, 3, P, 24), { tone: "mid" }));
  // the squat hole, footrests, the lid's rails
  out.push(poly(Array.from({ length: 25 }, (_, j) => { const a = (j / 24) * Math.PI; return [PX + 9 * Math.cos(a), CUT - 9 * Math.sin(a), SLAB_TOP]; }), "fs-cavity"));
  out.push(L(k.pathOf(Array.from({ length: 25 }, (_, j) => { const a = (j / 24) * Math.PI; return at([PX + 9 * Math.cos(a), CUT - 9 * Math.sin(a), SLAB_TOP]); })), { tone: "hi" }));
  for (const x of [PX - 22, PX + 14]) out.push(S(k.slabOf({ x, y: 22, w: 8, d: 30, r: 3 }, SLAB_TOP, 2, P, 4, 0.4), { tone: "mid" }));
  for (const x of [PX - 13, PX + 12]) out.push(S(k.slabOf({ x, y: 22, w: 1.2, d: CUT - 22, r: 0 }, SLAB_TOP, 1.2, P, 2), { tone: "mid", crease: "none" }));
  out.push(S(k.slabOf({ x: PX - 13, y: 20, w: 26.2, d: 2, r: 0 }, SLAB_TOP, 2.4, P, 2), { tone: "mid", crease: "none" }));
  // the sliding lid, a part that moves: shut at red
  const lid = { x: PX - 12, y: CUT - 16, w: 24, d: 16, r: 0.6 };
  out.push(`<g data-d-t="lid" transform="${D0.lid}">` +
    S(k.slabOf(lid, SLAB_TOP + 1.2, 2.8, P, 2, 0.4), { tone: "hi", crease: "lo" }) +
    L(k.planOutline(k.insetPlan(lid, 2.4), SLAB_TOP + 4, P, 2), { tone: "faint" }) +
    S(k.slabOf({ x: PX - 4, y: CUT - 15, w: 8, d: 3, r: 1 }, SLAB_TOP + 4, 2.2, P, 3), { tone: "mid" }) + `</g>`);
  // the right wall, with a screened window slot
  out.push(S(k.slabOf({ x: -12, y: -48, w: 6, d: CUT + 48, r: 0 }, SLAB_TOP, ROOF_Z - SLAB_TOP, P, 2), { tone: "mid" }));
  let courseR = "";
  for (let z = SLAB_TOP + 12; z < ROOF_Z; z += 12) if (z < 126 || z > 140) courseR += seg3([-6, -48, z], [-6, CUT, z]);
  out.push(L(courseR, { tone: "faint" }), L(seg3([-6, CUT, SLAB_TOP], [-6, CUT, ROOF_Z]), { tone: "mid" }));
  out.push(poly([[-6, -30, 128], [-6, 10, 128], [-6, 10, 140], [-6, -30, 140]], "fs-cavity"));
  let mesh = "";
  for (let y = -27; y < 10; y += 3) mesh += seg3([-6, y, 128], [-6, y, 140]);
  for (let z = 131; z < 140; z += 3) mesh += seg3([-6, -30, z], [-6, 10, z]);
  out.push(L(mesh, { tone: "lo" }), L(k.pathOf([at([-6, -30, 128]), at([-6, 10, 128]), at([-6, 10, 140]), at([-6, -30, 140])], true), { tone: "mid" }));
  // the roof sheet with its corrugations
  const roof = { x: -142, y: -62, w: 144, d: 62, r: 0 };
  out.push(S(k.slabOf(roof, ROOF_Z, 3, P, 2, 0.5), { tone: "mid" }));
  let ribs = "";
  for (let x = roof.x + 6; x < roof.x + roof.w - 2; x += 6) ribs += k.lineOnTop([x, roof.y], [x, roof.y + roof.d], ROOF_Z + 3, P);
  out.push(L(ribs, { tone: "faint" }));
  out.push(D([[-138, -58], [-138, -4], [-2, -58], [-2, -4], [-70, -58], [-70, -4]].map(([x, y]) => at([x, y, ROOF_Z + 3])), { size: 0.5, tone: "mid" }));
  // the solar panel on two rails, its cells, and the cable to the lamp
  for (const y of [-40, -10]) out.push(S(k.slabOf({ x: -110, y, w: 52, d: 3, r: 0.4 }, ROOF_Z + 3, 3, P, 2), { tone: "mid" }));
  const panel = { x: -114, y: -44, w: 60, d: 40, r: 1 };
  out.push(S(k.slabOf(panel, ROOF_Z + 6, 2.4, P, 3, 0.5), { tone: "hi", crease: "lo" }));
  const cells = k.insetPlan(panel, 2.2), ztop = ROOF_Z + 8.4;
  let grid = k.planOutline(cells, ztop, P, 2);
  for (let i = 1; i < 6; i++) grid += k.lineOnTop([cells.x + (cells.w * i) / 6, cells.y], [cells.x + (cells.w * i) / 6, cells.y + cells.d], ztop, P);
  for (let i = 1; i < 4; i++) grid += k.lineOnTop([cells.x, cells.y + (cells.d * i) / 4], [cells.x + cells.w, cells.y + (cells.d * i) / 4], ztop, P);
  out.push(L(grid, { tone: "mid" }));
  out.push(S(k.slabOf({ x: -54, y: -28, w: 5, d: 7, r: 0.6 }, ROOF_Z + 3, 4, P, 2), { tone: "mid" }));
  out.push(k.wireSvg(at([-51.5, -21, ROOF_Z + 5]), at([-51, -44.5, ROOF_Z + 3]), { via: [at([-46, -21, ROOF_Z + 3])], tone: "mid", size: 0.8 }));
  // the vent above the roof, its fly-screen cap
  out.push(S(k.cylinder(-22, -40, 7, ROOF_Z + 3, 2, P, 24), { tone: "mid" }));
  out.push(S(k.cylinder(-22, -40, 5, ROOF_Z + 5, 32, P, 24), { tone: "mid", crease: "none" }));
  out.push(S(k.cylinder(-22, -40, 7.4, ROOF_Z + 37, 8, P, 28), { tone: "mid", crease: "none" }));
  out.push(L(k.knurl(-22, -40, 7.4, ROOF_Z + 37.6, ROOF_Z + 44.4, 30, P, 0.4) + k.sideArc(-22, -40, 7.4, ROOF_Z + 41, P, 24), { tone: "lo" }));
  out.push(S(k.cylinder(-22, -40, 8.6, ROOF_Z + 45, 2, P, 28, 0.4), { tone: "mid" }));
  return out.join("");
}

// ---- the gauge: the half pipe on the cut, its cap, the staff with the colour pegs, the float rod and pointer ----
function gauge() {
  const out = [];
  // footing of the staff, then the staff with its coloured bands and ruler
  out.push(S(k.slabOf({ x: 46, y: 38, w: 18, d: 13, r: 1.5 }, 0, 6, P, 3, 0.5), { tone: "mid" }));
  out.push(S(k.slabOf(STAFF, 6, STAFF_TOP - 6, P, 2, 0.4), { tone: "mid" }));
  const fy = STAFF.y + STAFF.d;
  const bandCls = ["fs-peg-green", "fs-peg-yellow", "fs-peg-red"];
  for (let i = 0; i < 3; i++) {
    const z0 = M.BANDS[i], z1 = i === 2 ? STAFF_TOP - 4 : M.BANDS[i + 1];
    out.push(poly([[STAFF.x + 0.6, fy, z0], [STAFF.x + STAFF.w - 0.6, fy, z0], [STAFF.x + STAFF.w - 0.6, fy, z1], [STAFF.x + 0.6, fy, z1]], bandCls[i]));
    out.push(poly([[STAFF.x + STAFF.w, STAFF.y + 0.6, z0], [STAFF.x + STAFF.w, fy - 0.6, z0], [STAFF.x + STAFF.w, fy - 0.6, z1], [STAFF.x + STAFF.w, STAFF.y + 0.6, z1]], bandCls[i] + " fs-side"));
  }
  let minor = "", major = "";
  for (let z = M.BANDS[0], i = 0; z <= STAFF_TOP - 4; z += 4, i++) (i % 5 === 0 ? (major += seg3([STAFF.x + STAFF.w, fy, z], [STAFF.x + STAFF.w - 4.2, fy, z])) : (minor += seg3([STAFF.x + STAFF.w, fy, z], [STAFF.x + STAFF.w - 2.4, fy, z])));
  out.push(L(minor, { tone: "lo" }), L(major, { tone: "hi" }));
  out.push(L(seg3([STAFF.x, fy, M.BANDS[1]], [STAFF.x + STAFF.w, fy, M.BANDS[1]]) + seg3([STAFF.x + STAFF.w, fy, M.BANDS[1]], [STAFF.x + STAFF.w, STAFF.y, M.BANDS[1]]) + seg3([STAFF.x, fy, M.BANDS[2]], [STAFF.x + STAFF.w, fy, M.BANDS[2]]) + seg3([STAFF.x + STAFF.w, fy, M.BANDS[2]], [STAFF.x + STAFF.w, STAFF.y, M.BANDS[2]]), { tone: "hi" }));
  out.push(S(k.slabOf(k.insetPlan(STAFF, -0.8), STAFF_TOP, 2, P, 2), { tone: "mid" }));
  out.push(D([at([STAFF.x + 5, fy, 12]), at([STAFF.x + 5, fy, 30])], { size: 0.5, tone: "mid" }));
  out.push(collar("staff"));
  // the half pipe above ground (cut on the plane, so its bore shows), and its cap
  const half = (r) => Array.from({ length: 25 }, (_, j) => { const a = Math.PI + (j / 24) * Math.PI; return [GX + r * Math.cos(a), CUT + r * Math.sin(a)]; });
  out.push(S(k.extrude(half(GR), 0, GTOP, P), { tone: "mid" }));
  out.push(onCut(GX - GBORE, GX + GBORE, 0, GTOP, "fs-cavity"));
  out.push(L(k.pathOf([at([GX - GBORE, CUT, 0]), at([GX - GBORE, CUT, GTOP])]) + k.pathOf([at([GX + GBORE, CUT, 0]), at([GX + GBORE, CUT, GTOP])]), { tone: "hi" }));
  out.push(collar("gauge"));
  out.push(S(k.extrude(half(GR + 1.6), GTOP, 4, P, { bevel: 0.4 }), { tone: "mid" }));
  out.push(onCut(GX - 1.6, GX + 1.6, GTOP, GTOP + 4, "fs-cavity"));
  // the float rod above the cap (rebuilt to its length), and the pointer it carries
  out.push(`<g class="iso-solid" data-lit=""><path class="iso-fill" data-d="rodFill" d="${D0.rodFill}"/><path class="iso-shade" data-shade="2" data-d="rodShade" d="${D0.rodShade}"/><path class="iso-top" data-d="rodTop" d="${D0.rodTop}"/><path class="iso-line iso-edge" data-tone="lit" data-d="rodEdge" d="${D0.rodEdge}"/></g>`);
  const arm = { x: GX - 2, y: fy, w: STAFF.w + 13, d: 3, r: 0.6 };
  out.push(`<g data-d-t="pointer" transform="${D0.pointer}">` +
    S(k.slabOf(arm, -1.4, 2.8, P, 2, 0.3), { tone: "hi", lit: true }) +
    S(k.cylinder(GX, ROD_Y, 2.2, -2.4, 4.8, P, 16), { tone: "hi", lit: true }) +
    L(k.lineOnTop([STAFF.x + STAFF.w + 1.5, fy + 1.5], [STAFF.x - 0.5, fy + 1.5], 1.4, P), { tone: "lit", free: "end" }) + `</g>`);
  return out.join("");
}

// ---- the flood-mark post (the worst remembered flood, marked on a fixed point) ----
function post() {
  const out = [];
  out.push(S(k.slabOf(k.insetPlan(POST, -4), 0, 5, P, 3, 0.5), { tone: "mid" }));
  out.push(S(k.slabOf(POST, 5, 87, P, 2, 0.4), { tone: "mid" }));
  const z0 = M.FLOOD_MAX - 1.2, z1 = M.FLOOD_MAX + 1.2, xR = POST.x + POST.w, yF = POST.y + POST.d;
  out.push(poly([[POST.x, yF, z0], [xR, yF, z0], [xR, yF, z1], [POST.x, yF, z1]], "fs-peg-red"));
  out.push(poly([[xR, POST.y, z0], [xR, yF, z0], [xR, yF, z1], [xR, POST.y, z1]], "fs-peg-red fs-side"));
  out.push(L(k.pathOf([at([POST.x, yF, z1]), at([xR, yF, z1]), at([xR, POST.y, z1])]) + k.pathOf([at([POST.x, yF, z0]), at([xR, yF, z0]), at([xR, POST.y, z0])]), { tone: "hi" }));
  out.push(S(k.slabOf(k.insetPlan(POST, -1), 92, 2, P, 2), { tone: "mid" }));
  out.push(D([at([POST.x + 4, yF, 70]), at([POST.x + 4, yF, 20])], { size: 0.5, tone: "mid" }));
  out.push(collar("post"));
  return out.join("");
}

// ---- the handwashing point: a frame, a hung jerrycan, a foot pedal on a cord ----
function wash() {
  const out = [];
  for (const [i, x] of WASH.entries()) {
    out.push(S(k.slabOf({ x: x - 1.5, y: WY - 1.5, w: 3, d: 3, r: 0.4 }, 0, 70, P, 2), { tone: "mid", crease: "none" }));
    out.push(collar("wash" + i));
  }
  out.push(S(k.slabOf({ x: WASH[0] - 3, y: WY - 2, w: WASH[1] - WASH[0] + 6, d: 4, r: 0.5 }, 70, 3, P, 2, 0.3), { tone: "mid" }));
  const can = { x: 95, y: WY - 6, w: 10, d: 12, r: 2 };
  out.push(k.wireSvg(at([100, WY, 70]), at([100, WY, 62.5]), { tone: "mid", size: 0.6 }));
  out.push(S(k.slabOf(can, 44, 18, P, 4, 0.6), { tone: "hi", crease: "lo" }));
  out.push(L(k.sideSeam ? k.sideSeam(can, 50, P, 4) + k.sideSeam(can, 56, P, 4) : "", { tone: "faint" }));
  out.push(S(k.cylinder(104, WY + 4, 1.6, 58, 5, P, 12), { tone: "mid" }));
  out.push(S(k.slabOf({ x: 95, y: WY + 18, w: 14, d: 3, r: 0.6 }, 0, 1.6, P, 2), { tone: "mid", crease: "none" }));
  out.push(k.wireSvg(at([102, WY + 19.5, 1.6]), at([104, WY + 4, 58]), { tone: "lo", size: 0.6 }));
  out.push(S(k.cylinder(90, WY + 8, 2.6, 0, 3, P, 14), { tone: "mid" }));
  return out.join("");
}

// ---- the family's shallow well: a ring wall, a windlass on two posts, a bucket on its rope ----
function well() {
  const out = [];
  const [x, y] = WELL;
  out.push(`<path class="iso-halo" d="${k.haloOf({ x: x - WELL_R, y: y - WELL_R, w: 2 * WELL_R, d: 2 * WELL_R, r: WELL_R }, 0, 14, P)}" style="opacity:.18"/>`);
  out.push(S(k.cylinder(x, y, WELL_R, 0, 14, P, 48, 0.6), { tone: "mid" }));
  out.push(poly(Array.from({ length: 48 }, (_, j) => { const a = (j / 48) * Math.PI * 2; return [x + (WELL_R - 3) * Math.cos(a), y + (WELL_R - 3) * Math.sin(a), 14]; }), "fs-cavity"));
  out.push(L(k.ring(x, y, WELL_R - 3, 14, P, 48), { tone: "mid" }));
  out.push(L([4.5, 9.5].map((z) => k.sideArc(x, y, WELL_R, z, P, 32)).join(""), { tone: "faint" }));
  out.push(collar("well"));
  for (const [i, px] of [x - 17, x + 17].entries()) {
    out.push(S(k.slabOf({ x: px - 2, y: y - 2, w: 4, d: 4, r: 0.5 }, 0, 44, P, 2), { tone: "mid", crease: "none" }));
    out.push(collar("wpost" + i));
  }
  out.push(S(k.slabOf({ x: x - 19, y: y - 1.6, w: 38, d: 3.2, r: 1.6 }, 40, 3.2, P, 6), { tone: "mid" }));
  out.push(S(k.slabOf({ x: x + 19, y: y - 1, w: 2, d: 2, r: 0.5 }, 41.6, 1.2, P, 2), { tone: "mid", crease: "none" }));
  out.push(S(k.slabOf({ x: x + 20, y: y - 1, w: 1.6, d: 2, r: 0.5 }, 34, 8, P, 2), { tone: "mid", crease: "none" }));
  out.push(k.wireSvg(at([x, y, 40]), at([x, y, 31]), { tone: "mid", size: 0.6 }));
  out.push(S(k.cylinder(x, y, 4.4, 22, 8, P, 20, 0.4), { tone: "hi", crease: "lo" }));
  out.push(L(k.sideArc(x, y, 4.4, 27, P, 16), { tone: "faint" }));
  return out.join("");
}

// ---- assemble, back to front ----
const things = [
  { at: [150, -92, 0], svg: post() },
  { at: [100, WY, 0], svg: wash() },
  { at: WELL.concat(0), svg: well() },
  { at: [-70, 5, 0], svg: latrine() },
  { at: [50, 48, 0], svg: gauge() },
].sort((a, b) => k.depthOf(a.at, P) - k.depthOf(b.at, P));

const svg = k.figureSvg({
  width: WIDTH, height: HEIGHT,
  label: "A FloodSafe latrine for flood-edge ground (zone B), cut open through its pit. A lined pit under a raised slab and plinth, a shelter with an inside lock, a solar light, a screened vent and an emergency pack, and a sliding lid. Beside it a groundwater gauge: a float in a slotted well lifts a rod and pointer past green, yellow and red pegs. As the water rises the pointer reaches red, the floodwater covers the yard up to the mark on the post, and the lid is slid shut.",
  body: [ground(), sections(), yard(), flood(), ...things.map((t) => t.svg)],
});

const k0 = M.kin(first.lv);
const theme = `<style>
.iso[data-theme="light"]{
  --anatomy-page:#F1ECE2;--anatomy-card:#F7F3EB;--anatomy-text:#3d4b5c;--anatomy-strong:#13283F;--anatomy-muted:#7d8692;
  --anatomy-paper:#F7F3EB;--anatomy-face:#FCFAF5;--anatomy-top:#FDFBF7;
  --anatomy-shade-0:#E3DBCC;--anatomy-shade-1:#E9E2D5;--anatomy-shade-2:#EFE9DF;--anatomy-shade-3:#F4EFE7;
  --anatomy-lit-top:#FFFFFF;--anatomy-lit-shade:#F6E9E4;
  --anatomy-hi:#13283F;--anatomy-mid:#7A8494;--anatomy-lo:#AEB1B2;--anatomy-faint:#D6D0C4;--anatomy-lit:#C24A33;
  --anatomy-halo:#5f5646;--anatomy-halo-opacity:.3;--anatomy-dot:#13283F;
  --fs-sand:#ECE3D2;--fs-topsoil:#DDCFB6;--fs-clay:#D3C2A6;--fs-cavity:#4A4A47;--fs-waste:#6E5A49;--fs-waste-top:#83705E;
  --fs-ring:#E2DFD8;--fs-pipe:#EEEAE2;--fs-gravel:#DCD3C3;--fs-plate:#F7F3EB;
  --fs-gw:rgba(38,105,166,.26);--fs-water:rgba(38,105,166,.30);--fs-water-side:rgba(38,105,166,.40);--fs-river:#2669A6;--fs-bore:rgba(38,105,166,.85);
  --fs-green:#3E8F5A;--fs-yellow:#E8B04A;--fs-red:#C24A33;--fs-lens:#E8B04A;
}
.fs-sand{fill:var(--fs-sand)} .fs-topsoil{fill:var(--fs-topsoil)} .fs-clay{fill:var(--fs-clay)} .fs-cavity{fill:var(--fs-cavity)} .fs-waste{fill:var(--fs-waste)} .fs-waste-top{fill:var(--fs-waste-top)}
.fs-ring{fill:var(--fs-ring)} .fs-pipe{fill:var(--fs-pipe)} .fs-gravel{fill:var(--fs-gravel)} .fs-slot{fill:var(--fs-cavity)} .fs-plate{fill:var(--fs-plate)} .fs-ruler{fill:var(--anatomy-card)}
.fs-gw{fill:var(--fs-gw)} .fs-bore{fill:var(--fs-bore)} .fs-lens{fill:var(--fs-lens)}
.fs-gw-line{stroke:var(--fs-river);stroke-width:1px;stroke-dasharray:6 4}
.fs-water{fill:var(--fs-water)} .fs-water-side{fill:var(--fs-water-side)} .fs-collar{fill:var(--fs-water-side)}
.fs-waterline{stroke:var(--fs-river);stroke-width:1px} .fs-rim{opacity:.55}
.fs-lit-fill{fill:var(--anatomy-lit)}
.fs-peg-green{fill:var(--fs-green)} .fs-peg-yellow{fill:var(--fs-yellow)} .fs-peg-red{fill:var(--fs-red)}
.fs-side{filter:brightness(.9)}
</style>`;

const live = `
${readFileSync(join(HERE, "model.mjs"), "utf8").replace(/^export /gm, "")}
${readFileSync(join(HERE, "dyn.mjs"), "utf8").replace(/^export /gm, "")}
const P = ${JSON.stringify(P)};
const G = ${JSON.stringify(G)};
const k = { iso, pathOf, cylinder, translateAlong, towardViewer };
const drawAt = dynamic(k, P, G);
const svg = document.querySelector(".iso-stage svg");
const nodes = [...svg.querySelectorAll("[data-d]")].map((el) => [el, el.dataset.d, "d"]).concat([...svg.querySelectorAll("[data-d-t]")].map((el) => [el, el.dataset.dT, "transform"]));
const readout = document.querySelector("[data-readout]");
const stage = document.querySelector(".iso-stage");
const last = {};
function paint(lv, lid) {
  const kk = kin(lv), d = drawAt({ k: kk, lid });
  for (const [el, id, attr] of nodes) if (last[id] !== d[id]) { el.setAttribute(attr, d[id]); last[id] = d[id]; }
  const text = readoutOf(kk, lid);
  if (readout.textContent !== text) readout.textContent = text;
  return kk;
}
window.renderAt = (t) => { const s = filmAt(t); const kk = paint(s.lv, s.lid); window.dispatchEvent(new CustomEvent("fs-frame", { detail: { t, sig: kk.sig } })); return true; };
`;

const interactive = `
const still = matchMedia("(prefers-reduced-motion: reduce)");
let lv = ${first.lv}, lid = ${first.lid}, target = lv, lidTarget = lid, clock = 0, touring = !still.matches, frame = 0, prev = 0, visible = false, idle = 0;
function tick(now) {
  const dt = prev ? Math.min((now - prev) / 1000, 1 / 30) : 1 / 60; prev = now;
  const calm = still.matches;
  if (touring) { clock += dt; const s = tourAt(clock); target = s.lv; lidTarget = s.lid; }
  else { const sig = kin(target).sig; if (sig === 2) lidTarget = 1; else if (sig === 0) lidTarget = 0; }
  lv = calm ? target : lv + (target - lv) * (1 - Math.exp(-dt / (touring ? 0.05 : 0.3)));
  lid = calm ? lidTarget : lid + (lidTarget - lid) * (1 - Math.exp(-dt / (touring ? 0.05 : 0.25)));
  if (Math.abs(target - lv) < 1e-4) lv = target; if (Math.abs(lidTarget - lid) < 1e-4) lid = lidTarget;
  paint(lv, lid);
  const settled = !touring && lv === target && lid === lidTarget;
  frame = visible && !settled ? requestAnimationFrame(tick) : 0;
}
const run = () => { if (!frame && visible) { prev = 0; frame = requestAnimationFrame(tick); } };
const describe = () => { const kk = kin(target); stage.setAttribute("aria-valuenow", String(Math.round(target * 100))); stage.setAttribute("aria-valuetext", COLOURS[kk.sig] + ": " + WORDS[kk.sig] + ". Floodwater " + Math.round(100 * kk.h / FLOOD_MAX) + " percent of the design-flood mark."); };
const steer = (next) => { touring = false; target = Math.min(1, Math.max(0, next)); describe(); clearTimeout(idle); idle = setTimeout(() => { touring = !still.matches; clock = 0; run(); }, 3600); run(); };
new IntersectionObserver((e) => { visible = e[e.length - 1].isIntersecting; if (visible) run(); }, { rootMargin: "120px 0px" }).observe(stage);
stage.addEventListener("pointermove", (e) => { const b = svg.getBoundingClientRect(); steer(((e.clientX - b.left) / b.width - 0.15) / 0.7); });
stage.addEventListener("keydown", (e) => {
  const step = e.shiftKey ? 0.2 : 0.05; let to = null;
  if (e.key === "ArrowRight" || e.key === "ArrowUp") to = target + step;
  if (e.key === "ArrowLeft" || e.key === "ArrowDown") to = target - step;
  if (e.key === "Home") to = 0; if (e.key === "End") to = 1;
  if (to === null) return; e.preventDefault(); steer(to);
});
if (still.matches) { const s = filmAt(${M.FILM_SECONDS}); lv = target = s.lv; lid = lidTarget = s.lid; }
describe(); paint(lv, lid);
`;

const plate = k.plateHtml({
  fig: "Fig 7",
  title: "The signal",
  hint: FILM ? "FloodSafe Gambella · zone B" : "Move across to raise the water",
  readout: M.readoutOf(k0, first.lid),
  keys: FILM ? [] : [
    { mark: "lit", label: "Float, rod and pointer: they ride the groundwater" },
    { mark: "raised", label: "Lined pit, raised slab and sliding lid" },
    { mark: "blue", label: "Groundwater and floodwater, one level" },
  ],
  caption: FILM ? "" : "A float in a slotted well beside the toilet rides the groundwater, and its rod carries a pointer past green, yellow and red pegs on a staff. No power is needed. Green: use as usual. Yellow: treat drinking water. Red: slide the lid shut and use the emergency pack. The plinth stands above the design flood, marked on the post. Levels follow the film's model; real depths are to be measured on site.",
  body: `<div class="iso-stage" tabindex="0" role="slider" aria-label="FloodSafe groundwater gauge: arrow keys raise or lower the water" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${Math.round(first.lv * 100)}">${svg}</div>`,
});

if (FILM) {
  const film = `<style>
html,body{margin:0;width:1920px;height:1080px;overflow:hidden;background:#F1ECE2}
.fs-film{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:flex-start;padding-top:40px}
.fs-film .iso-figure{width:1520px;margin:0}
.fs-film .iso-plate{padding:64px 40px 56px;box-shadow:0 0 0 2px var(--anatomy-mid)}
.fs-film .iso-plate-corners{inset:24px 30px}
.fs-film .iso-plate-corner{font-size:24px}
.fs-film .iso{--anatomy-weight:1.5px}
.fs-film{--anatomy-weight:1.5px}
.fs-film .iso-svg{height:740px;width:auto;max-width:100%}
.fs-cap{position:absolute;left:0;right:0;bottom:44px;text-align:center;font:700 64px/1.05 "Space Grotesk","Helvetica Neue",Arial,sans-serif;letter-spacing:-0.02em;color:#13283F}
.fs-cap span{display:inline-block}
</style>
<div class="fs-film">${plate}</div>
<div class="fs-cap"><span data-cap="0">Green, yellow, red. No power needed</span></div>
<div class="fs-cap"><span data-cap="1">At red, seal the lid and use the pack</span></div>`;
  const capScript = `
const caps = [...document.querySelectorAll("[data-cap]")];
const fadeIn = (t, t0) => { const a = Math.min(1, Math.max(0, (t - t0) / 0.5)); const e = 1 - Math.pow(1 - a, 3); return { o: e, x: 40 * (1 - e) }; };
window.addEventListener("fs-frame", (ev) => {
  const t = ev.detail.t;
  const a = fadeIn(t, -0.3), out = 1 - Math.min(1, Math.max(0, (t - 3.3) / 0.35));
  caps[0].style.opacity = (a.o * out).toFixed(3); caps[0].style.transform = "translateX(" + a.x.toFixed(1) + "px)";
  const b = fadeIn(t, 3.75); caps[1].style.opacity = b.o.toFixed(3); caps[1].style.transform = "translateX(" + b.x.toFixed(1) + "px)";
});
window.renderAt(0);
`;
  writeFileSync(join(HERE, "floodsafe-signal-film.html"), k.pageHtml({ title: "FloodSafe · The signal (film)", theme: "light", body: theme + film, script: kitScript() + live + capScript, width: 1920 }));
  console.log("wrote floodsafe-signal-film.html");
} else {
  writeFileSync(join(HERE, "floodsafe-signal.html"), k.pageHtml({ title: "FloodSafe · The signal", theme: "light", body: theme + plate, script: kitScript() + live + interactive, width: 760 }));
  console.log("wrote floodsafe-signal.html");
}
