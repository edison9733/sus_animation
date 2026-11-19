// One family yard, cut open: sky, the latrine over its pit, a shallow well, the water under the ground.
// Ground surface is y=640; the dry-season water table sits at y=960.
window.W = {
  SURF: 640, TABLE: 960, HUT: 700, WELL: 1330,
  // Sky and far country: pale hills and a few distant roofs from a seeded loop.
  far(kit, id, seed) {
    const r = kit.rng(seed);
    let s = '<defs><linearGradient id="' + id + '-skyg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" style="stop-color:var(--sky)"/><stop offset="1" style="stop-color:var(--ground)"/></linearGradient></defs>' +
      '<rect class="' + id + '-sky" width="1920" height="660" fill="url(#' + id + '-skyg)"/>' +
      '<g class="' + id + '-hills"><path d="M-20 610 Q300 540 640 590 T1300 575 T1940 590 V660 H-20 Z" style="fill:var(--hill);opacity:.55"/>' +
      '<path d="M-20 630 Q420 590 860 620 T1940 612 V660 H-20 Z" style="fill:var(--hill)"/>';
    for (let x = 30; x < 1900; x += 140 + r() * 220) {
      const w = 34 + r() * 26, y = 618 + r() * 10;
      s += '<path d="M' + x.toFixed(0) + ' ' + y.toFixed(0) + ' v-' + (w * 0.55).toFixed(0) + ' l' + (w / 2).toFixed(0) + ' -' + (w * 0.35).toFixed(0) + ' l' + (w / 2).toFixed(0) + ' ' + (w * 0.35).toFixed(0) + ' v' + (w * 0.55).toFixed(0) + ' Z" style="fill:color-mix(in srgb, var(--hill) 70%, var(--second))"/>';
    }
    return s + '</g>';
  },
  // The cut: topsoil, sand and clay bands with a dotted grain, and grass tufts along the top.
  soil(kit, id) {
    const r = kit.rng(7);
    let tufts = '';
    for (let x = 10; x < 1920; x += 38 + r() * 50) tufts += '<path d="M' + x.toFixed(0) + ' 641 l6 -16 l4 14 l6 -20 l5 22 Z" style="fill:var(--leaf)"/>';
    return '<defs><pattern id="' + id + '-grain" width="46" height="34" patternUnits="userSpaceOnUse"><circle cx="8" cy="9" r="2.6" style="fill:var(--shade)"/><circle cx="31" cy="24" r="2" style="fill:var(--shade)"/><circle cx="38" cy="6" r="1.4" style="fill:var(--shade)"/></pattern>' +
      '<pattern id="' + id + '-stone" width="120" height="70" patternUnits="userSpaceOnUse"><ellipse cx="30" cy="20" rx="10" ry="6" style="fill:var(--shade)"/><ellipse cx="90" cy="52" rx="7" ry="4" style="fill:var(--shade)"/></pattern></defs>' +
      '<g class="' + id + '-soil"><rect y="640" width="1920" height="440" style="fill:var(--sand)"/>' +
      '<path d="M0 640 H1920 V720 Q1500 740 960 712 T0 728 Z" style="fill:var(--soil)"/>' +
      '<path d="M0 1010 Q520 990 980 1012 T1920 1000 V1080 H0 Z" style="fill:var(--clay)"/>' +
      '<rect y="640" width="1920" height="440" fill="url(#' + id + '-grain)"/><rect y="1000" width="1920" height="80" fill="url(#' + id + '-stone)"/>' +
      '<rect y="636" width="1920" height="8" style="fill:color-mix(in srgb, var(--soil) 70%, var(--second))"/>' + tufts + '</g>';
  },
  // Groundwater: a translucent band whose top a scene moves with translateY. Origin at its top edge.
  table(id) {
    return '<g class="' + id + '-table"><rect x="0" y="0" width="1920" height="600" style="fill:color-mix(in srgb, var(--main) 34%, transparent)"/>' +
      '<path d="M0 0 H1920" style="stroke:var(--main);stroke-width:4;stroke-dasharray:22 14;fill:none"/></g>';
  },
  // The latrine shelter, standing on its slab at (0,0) = ground level over the pit's centre. Lit from the left.
  hut(cls) {
    let blocks = '';
    for (let y = -40; y > -210; y -= 28) for (let x = -92 + ((y / 28) % 2 ? 0 : 22); x < 88; x += 44) blocks += '<rect x="' + x + '" y="' + y + '" width="42" height="26" rx="2" style="fill:' + (x > 20 ? 'var(--blockdk)' : 'var(--block)') + '"/>';
    return '<g class="' + cls + '"><defs><clipPath id="' + cls + '-wall"><rect x="-92" y="-212" width="184" height="200"/></clipPath></defs>' +
      '<rect x="-96" y="-214" width="192" height="204" style="fill:color-mix(in srgb, var(--second) 30%, var(--ground))"/>' +
      '<g clip-path="url(#' + cls + '-wall)">' + blocks + '</g>' +
      '<rect x="-34" y="-170" width="68" height="158" rx="4" style="fill:var(--wood)"/><rect x="-26" y="-162" width="52" height="142" rx="3" style="fill:color-mix(in srgb, var(--wood) 80%, var(--ground))"/><circle cx="16" cy="-90" r="5" style="fill:var(--second)"/>' +
      '<path d="M-124 -206 L120 -236 L128 -220 L-118 -190 Z" style="fill:color-mix(in srgb, var(--main) 45%, var(--block))"/>' +
      '<path d="M-110 -200 L-108 -194 M-80 -204 L-78 -197 M-50 -208 L-48 -201 M-20 -211 L-18 -205 M10 -215 L12 -208 M40 -219 L42 -212 M70 -222 L72 -216 M100 -226 L102 -219" style="stroke:var(--shade);stroke-width:4"/>' +
      '<rect x="-116" y="-14" width="232" height="16" rx="3" style="fill:var(--blockdk)"/></g>';
  },
  // The old pit under the hut: a ragged unlined hole, top centre at (0,0), with its waste as a separate group a scene can fill.
  pit(cls, depth) {
    const d = depth || 250;
    return '<g class="' + cls + '"><path d="M-78 2 Q-86 ' + (d * 0.3) + ' -80 ' + (d * 0.55) + ' Q-88 ' + (d * 0.8) + ' -74 ' + d + ' Q0 ' + (d + 14) + ' 74 ' + d + ' Q90 ' + (d * 0.75) + ' 80 ' + (d * 0.5) + ' Q88 ' + (d * 0.25) + ' 78 2 Z" style="fill:color-mix(in srgb, var(--second) 72%, var(--soil))"/>' +
      '<g class="' + cls + '-waste"><path d="M-82 0 Q0 -10 82 0 V' + (d + 14) + ' H-82 Z" style="fill:var(--waste)"/></g></g>';
  },
  // A shallow well: block ring above ground, crossbar and bucket, shaft down past the water table. Origin at ground centre.
  well(cls) {
    let ring = '';
    for (let i = 0; i < 3; i++) for (let x = -70 + (i % 2) * 18; x < 66; x += 36) ring += '<rect x="' + x + '" y="' + (-24 - i * 24) + '" width="34" height="22" rx="2" style="fill:' + (x > 10 ? 'var(--blockdk)' : 'var(--block)') + '"/>';
    return '<g class="' + cls + '"><rect x="-44" y="0" width="88" height="390" style="fill:color-mix(in srgb, var(--second) 62%, var(--soil))"/>' +
      '<rect x="-44" y="330" width="88" height="60" style="fill:var(--water)"/>' +
      '<g clip-path="none">' + ring + '</g>' +
      '<path d="M-62 -72 V-190 M62 -72 V-190 M-76 -190 H76" style="stroke:var(--wood);stroke-width:12;fill:none;stroke-linecap:round"/>' +
      '<path d="M0 -190 V-118" style="stroke:var(--second);stroke-width:3"/><path d="M-20 -118 H20 L15 -86 H-15 Z" style="fill:var(--main)"/></g>';
  },
  // A papaya tree at (0,0): a thin trunk and a crown of long leaves.
  tree(cls) {
    let leaves = '';
    [-150, -115, -70, -30, 15, 55, 100, 140].forEach((a, i) => leaves += '<path d="M0 0 Q' + (Math.sin(a * Math.PI / 180) * 60).toFixed(0) + ' ' + (-Math.cos(a * Math.PI / 180) * 60 - 20).toFixed(0) + ' ' + (Math.sin(a * Math.PI / 180) * 120).toFixed(0) + ' ' + (-Math.cos(a * Math.PI / 180) * 70).toFixed(0) + ' Q' + (Math.sin(a * Math.PI / 180) * 60).toFixed(0) + ' ' + (-Math.cos(a * Math.PI / 180) * 40).toFixed(0) + ' 0 0 Z" style="fill:' + (i % 2 ? 'var(--leaf)' : 'color-mix(in srgb, var(--leaf) 75%, var(--ground))') + '"/>');
    return '<g class="' + cls + '"><path d="M-7 0 Q-4 -150 -2 -300 H6 Q6 -150 9 0 Z" style="fill:var(--wood)"/>' +
      '<g transform="translate(2 -300)">' + leaves + '<circle cx="-10" cy="14" r="11" style="fill:var(--accent)"/><circle cx="10" cy="18" r="10" style="fill:color-mix(in srgb, var(--accent) 70%, var(--ground))"/></g></g>';
  },
  // A plastic jerrycan by the well, a small true thing of this yard.
  can(cls) {
    return '<g class="' + cls + '"><rect x="-22" y="-50" width="44" height="50" rx="6" style="fill:color-mix(in srgb, var(--accent) 60%, var(--ground))"/><rect x="-8" y="-60" width="16" height="12" rx="2" style="fill:var(--accent)"/><rect x="-22" y="-50" width="12" height="50" rx="4" style="fill:color-mix(in srgb, var(--ground) 30%, transparent)"/></g>';
  },
  // Floodwater over the ground: a wavy surface at height `level`, worked out from t alone.
  waveD(t, level, x0, x1, amp) {
    let d = 'M' + x0 + ' 1080 V' + level.toFixed(1);
    for (let x = x0; x <= x1; x += 40) d += ' L' + x + ' ' + (level + amp * Math.sin(x * 0.012 + t * 2.2) + amp * 0.5 * Math.sin(x * 0.031 - t * 1.4)).toFixed(1);
    return d + ' V1080 Z';
  },
  // Waste carried through the soil from pit to well: seeded specks, each placed from t alone.
  seep(kit, n, x0, y0, x1, y1) {
    const r = kit.rng(n + 3), list = Array.from({ length: n }, () => ({ at: r() * 3, dy: (r() - 0.5) * 80, s: 5 + r() * 6 }));
    return {
      markup: '<g class="seep">' + list.map(() => '<circle style="fill:var(--waste)"/>').join('') + '</g>',
      bind(g) { list.forEach((p, i) => { p.el = g.children[i]; }); },
      render(t, on) {
        for (const p of list) {
          const q = (((t - p.at) / 3) % 1 + 1) % 1;
          p.el.setAttribute('cx', (x0 + (x1 - x0) * q).toFixed(1));
          p.el.setAttribute('cy', (y0 + (y1 - y0) * q + p.dy * Math.sin(q * Math.PI)).toFixed(1));
          p.el.setAttribute('r', p.s.toFixed(1));
          p.el.style.opacity = (on * (q < 0.1 ? q * 10 : q > 0.85 ? (1 - q) / 0.15 : 1) * 0.85).toFixed(3);
        }
      },
    };
  },
  // Camera: put world point (cx,cy) at the stage centre at zoom z, kept inside the drawing.
  look(el, cx, cy, z) {
    z = Math.max(1, z);
    cx = Math.min(1920 - 960 / z, Math.max(960 / z, cx)); cy = Math.min(1080 - 540 / z, Math.max(540 / z, cy));
    el.style.transformOrigin = '0px 0px';
    el.style.transform = 'translate(' + (960 - cx * z).toFixed(2) + 'px,' + (540 - cy * z).toFixed(2) + 'px) scale(' + z.toFixed(4) + ')';
  },
  // A camera path. keys[0] = [0, 0, cx, cy, z] is the opening view; each later key [t0, t1, cx, cy, z] moves there between t0 and t1.
  // A slow creep runs under it all, so no hold is ever frozen.
  path(kit, el, keys, t) {
    let cx = keys[0][2], cy = keys[0][3], lz = Math.log(keys[0][4]);
    for (let i = 1; i < keys.length; i++) {
      const k = keys[i], p = kit.eio(kit.seg(t, k[0], k[1]));
      cx += (k[2] - cx) * p; cy += (k[3] - cy) * p; lz += (Math.log(k[4]) - lz) * p;
    }
    window.W.look(el, cx, cy, Math.exp(lz) * (1 + 0.004 * Math.max(0, t)));
  },
};
// ---- The teardown rig ------------------------------------------------------------------------------
// The yard as a block cut open on the plane z = 0 (x right, y up, z towards the viewer), seen by an orthographic camera that stays in
// the (+x,+y,+z) octant: every box shows its top, front and right faces, and the draw order below never changes.
// Each face is a <g class="f3"> of plain 2D drawing; a frame only rewrites the matrices.
Object.assign(window.W, {
  // One input drives everything: lv, from 0 (dry season) to 1 (worst flood). The model, the gauge and the panels all read this.
  kin(lv) {
    lv = Math.min(1, Math.max(0, lv));
    return { lv: lv, gw: 290 - 190 * lv, h: 44 * Math.min(1, Math.max(0, (lv - 0.5) / 0.5)), sig: lv < 0.32 ? 0 : lv < 0.67 ? 1 : 2 };
  },
  // A view that puts world point (tx,ty,tz) at the middle of the 1800 x 744 window.
  view(yaw, pitch, s, tx, ty, tz) {
    const a = yaw * Math.PI / 180, b = pitch * Math.PI / 180;
    const r0 = Math.cos(a), r2 = -Math.sin(a), u0 = -Math.sin(a) * Math.sin(b), u1 = Math.cos(b), u2 = -Math.cos(a) * Math.sin(b);
    const ox = 900 - s * (tx * r0 + tz * r2), oy = 372 + s * (tx * u0 + ty * u1 + tz * u2);
    const pt = (x, y, z) => [ox + s * (x * r0 + z * r2), oy - s * (x * u0 + y * u1 + z * u2)];
    const L = { z: [s * r0, -s * u0, 0, s * u1], y: [s * r0, -s * u0, s * r2, -s * u2], x: [-s * r2, s * u2, 0, s * u1] };
    return { s: s, pt: pt,
      // the matrix of a face: 'z' front (local x, y down), 'y' top (local x, z), 'x' right side (local -z, y down), at offset o, moved by d
      m(k, o, d) {
        const p = k === 'z' ? pt(d[0], d[1], o + d[2]) : k === 'y' ? pt(d[0], o + d[1], d[2]) : pt(o + d[0], d[1], d[2]), l = L[k];
        return 'matrix(' + l[0].toFixed(4) + ' ' + l[1].toFixed(4) + ' ' + l[2].toFixed(4) + ' ' + l[3].toFixed(4) + ' ' + p[0].toFixed(2) + ' ' + p[1].toFixed(2) + ')';
      } };
  },
  // Camera keys: [t0, t1, yaw, pitch, zoom, tx, ty, tz]. keys[0] is the opening view; each later key eases there between t0 and t1.
  // A slow orbit and creep run under it all, so no hold is frozen.
  cam(kit, keys, t) {
    const c = keys[0].slice(2); c[2] = Math.log(c[2]);
    for (let i = 1; i < keys.length; i++) {
      const k = keys[i], p = kit.eio(kit.seg(t, k[0], k[1]));
      for (let j = 0; j < 6; j++) c[j] += ((j === 2 ? Math.log(k[4]) : k[j + 2]) - c[j]) * p;
    }
    return window.W.view(Math.min(60, Math.max(3, c[0] + 0.5 * Math.max(0, t))), c[1], Math.exp(c[2]) * (1 + 0.004 * Math.max(0, t)), c[3], c[4], c[5]);
  },
  face(k, o, g, inner) { return '<g class="f3" data-k="' + k + '" data-o="' + o + '" data-g="' + (g || '') + '">' + inner + '</g>'; },
  // A box as three faces: top at full color, front and right side shaded. f picks faces: 't', 'f', 's'.
  box(x0, x1, y0, y1, z0, z1, col, g, f) {
    const R = (x, y, w, h, b) => '<rect x="' + x + '" y="' + y + '" width="' + w + '" height="' + h + '" style="fill:color-mix(in srgb, ' + col + ' ' + b + '%, var(--second));stroke:var(--ink3);stroke-width:1.5;vector-effect:non-scaling-stroke"/>';
    f = f || 'tfs';
    return (f.indexOf('t') < 0 ? '' : window.W.face('y', y1, g, R(x0, z0, x1 - x0, z1 - z0, 100))) +
      (f.indexOf('f') < 0 ? '' : window.W.face('z', z1, g, R(x0, -y1, x1 - x0, y1 - y0, 84))) +
      (f.indexOf('s') < 0 ? '' : window.W.face('x', x1, g, R(-z1, -y1, z1 - z0, y1 - y0, 66)));
  },
  // The whole machine. pose(view, st) sets it from st: { lv, t, lined, lift, base, lid, lidOn, vent, pack, lamp, mark, spill, seep, taint, lean, truck, back }.
  model(kit, id) {
    const W = window.W, B = W.box, F = W.face, P = id + '-m';
    const ink = 'stroke:var(--ink3);stroke-width:1.5;vector-effect:non-scaling-stroke';
    const dark = 'color-mix(in srgb, var(--second) 72%, var(--soil))', pale = 'color-mix(in srgb, var(--ground) 85%, var(--second))', pl = 'color-mix(in srgb, var(--main) 35%, var(--ground))';
    const wt = 'fill:color-mix(in srgb, var(--water) 72%, transparent)', wf = 'fill:color-mix(in srgb, var(--main) 55%, transparent)', wsd = 'fill:color-mix(in srgb, var(--deep) 55%, transparent)';
    const R = (c, x, y, w, h, st) => '<rect class="' + c + '" x="' + x + '" y="' + y + '" width="' + w + '" height="' + h + '" style="' + st + '"/>';
    // floodwater in the front strip, between the things that stand in it: a top, lifted by the flood depth, and a front on the cut
    const wbox = (x0, x1) => F('y', 0, 'wt', R(P + '-w', x0, -100, x1 - x0, 100, wt)) + F('z', 0, '', R(P + '-w ' + P + '-wf', x0, 0, x1 - x0, 0, wf));
    const seep = W.seep(kit, 16, -168, 150, 236, 262);
    let rings = '', course = '', bricks = '';
    for (let i = 0; i < 5; i++) rings += '<g class="' + P + '-ring">' + R('', -346, i * 50, 16, 48, 'fill:var(--block);' + ink) + R('', -170, i * 50, 16, 48, 'fill:var(--blockdk);' + ink) + '</g>';
    for (let x = -364; x < -140; x += 46) course += 'M' + x + ' -46 V-23 M' + (x + 23) + ' -23 V0 ';
    for (let y = -42; y > -220; y -= 28) bricks += 'M-350 ' + y + ' H-150 ';
    const markup = '<defs><pattern id="' + P + '-gr" width="46" height="34" patternUnits="userSpaceOnUse"><circle cx="8" cy="9" r="2.6" style="fill:var(--shade)"/><circle cx="31" cy="24" r="2" style="fill:var(--shade)"/><circle cx="38" cy="6" r="1.4" style="fill:var(--shade)"/></pattern>' +
      '<clipPath id="' + P + '-tc"><rect x="-500" y="-240" width="1000" height="240"/></clipPath></defs>' +
      // 1 the block of ground: top, right side, and the cut face with the pit, the gauge pipe and the well in section
      F('y', 0, '', R('', -500, -240, 1000, 240, 'fill:color-mix(in srgb, var(--leaf) 28%, var(--sand));' + ink) + R('', 240, -90, 80, 90, 'fill:' + dark) +
        '<g clip-path="url(#' + P + '-tc)"><ellipse class="' + P + '-spill" cx="-250" cy="-40" rx="0" ry="0" style="fill:var(--waste)"/></g>') +
      F('x', 500, '', R('', 0, 0, 240, 360, 'fill:color-mix(in srgb, var(--sand) 80%, var(--second))') + R('', 0, 0, 240, 82, 'fill:color-mix(in srgb, var(--soil) 80%, var(--second))') + R('', 0, 300, 240, 60, 'fill:color-mix(in srgb, var(--clay) 80%, var(--second))') +
        R(P + '-gws', 0, 290, 240, 70, 'fill:color-mix(in srgb, var(--main) 40%, transparent)') + R('', 0, 0, 240, 360, 'fill:none;' + ink)) +
      F('z', 0, '', R('', -500, 0, 1000, 360, 'fill:var(--sand)') + '<path d="M-500 0 H500 V80 Q290 100 0 72 T-500 88 Z" style="fill:var(--soil)"/><path d="M-500 300 Q-240 286 0 304 T500 294 V360 H-500 Z" style="fill:var(--clay)"/>' +
        '<rect x="-500" y="0" width="1000" height="360" fill="url(#' + P + '-gr)"/>' +
        R(P + '-gw', -500, 290, 1000, 70, 'fill:color-mix(in srgb, var(--main) 34%, transparent)') + '<path class="' + P + '-gwl" d="M-500 0 H500" style="stroke:var(--main);stroke-width:4;stroke-dasharray:22 14;fill:none"/>' +
        R('', 240, 0, 80, 330, 'fill:' + dark) + R(P + '-ww', 240, 290, 80, 40, 'fill:var(--water)') + R(P + '-taint', 240, 290, 80, 40, 'fill:var(--waste);opacity:0') +
        R('', -92, 0, 24, 310, 'fill:' + pale + ';' + ink) + R(P + '-gin', -89, 290, 18, 20, 'fill:var(--water)') +
        '<path class="' + P + '-pito" d="M-328 2 Q-336 75 -330 138 Q-338 200 -324 250 Q-250 264 -176 250 Q-160 188 -170 125 Q-162 62 -172 2 Z" style="fill:' + dark + '"/>' +
        R(P + '-pitl', -330, 0, 160, 252, 'fill:' + dark + ';opacity:0') + R(P + '-waste', -324, 205, 148, 47, 'fill:var(--waste)') + seep.markup + R('', -500, 0, 1000, 360, 'fill:none;' + ink)) +
      // 2 water at the back, the flats that stand in it (tree, power pole, truck), more water, the jerrycan
      F('y', 0, 'wt', R(P + '-w', -500, -240, 1000, 50, wt)) + F('x', 500, '', R(P + '-w ' + P + '-wf', 0, 0, 240, 0, wsd)) +
      F('z', -190, '', '<g class="' + P + '-tree" transform="translate(410 0)">' + W.tree(P + '-tr') + '</g>' +
        '<g class="' + P + '-pole" transform="translate(-40 0)"><path d="M-8 0 L-6 -330 H6 L8 0 Z" style="fill:var(--wood)"/><rect x="-50" y="-316" width="100" height="10" rx="3" style="fill:var(--wood)"/></g>' +
        '<g class="' + P + '-truck" style="opacity:0"><rect x="-120" y="-96" width="150" height="74" rx="10" style="fill:color-mix(in srgb, var(--main) 70%, var(--ground))"/><path d="M34 -22 V-80 Q34 -90 44 -90 H82 L112 -56 V-22 Z" style="fill:var(--blockdk)"/>' +
        '<path d="M48 -82 H78 L100 -58 H48 Z" style="fill:var(--sky)"/><rect x="-124" y="-26" width="240" height="10" rx="4" style="fill:var(--second)"/><circle cx="-80" cy="-6" r="22" style="fill:var(--second)"/><circle cx="70" cy="-6" r="22" style="fill:var(--second)"/></g>') +
      F('y', 0, 'wt', R(P + '-w', -500, -190, 1000, 90, wt) + '<path class="' + P + '-w ' + P + '-rip" d="M-460 -160 H460 M-420 -128 H480" style="stroke:var(--ground);stroke-width:3;stroke-dasharray:60 90;fill:none"/>') +
      F('z', -100, '', '<g class="' + P + '-can">' + W.can(P + '-cn') + '</g>') +
      // 3 the front strip, left to right: water, the raised base, the hut cut in half (slab, shelf and pack, walls, light, lid, roof, vent), the gauge, the well
      wbox(-500, -364) +
      B(-364, -136, 0, 46, -114, 0, 'var(--blockdk)', 'base') + F('z', 0, 'base', '<path d="M-364 -23 H-136 ' + course + '" style="fill:none;' + ink + '"/>') +
      B(-362, -138, 0, 14, -112, 0, 'var(--blockdk)', 'hut') + F('y', 14, 'hut', '<path d="M-282 0 A32 28 0 0 1 -218 0 Z" style="fill:' + dark + '"/>') + F('z', 0, 'hut', R('', -282, -14, 64, 14, 'fill:' + dark)) +
      B(-440, -350, 150, 160, -70, -10, 'var(--wood)', 'pack') + B(-436, -406, 160, 206, -58, -22, pl, 'pack') + B(-439, -403, 206, 214, -61, -19, 'var(--main)', 'pack') +
      B(-398, -368, 160, 206, -58, -22, pl, 'pack') + B(-401, -365, 206, 214, -61, -19, 'var(--main)', 'pack') +
      B(-350, -150, 14, 220, -100, -90, 'var(--block)', 'hut', 'f') + F('z', -90, 'hut', '<path d="' + bricks + '" style="fill:none;' + ink + '"/>') +
      F('z', -89, 'lamp', '<circle cx="-250" cy="-193" r="48" style="fill:#E8B04A;opacity:.3"/>') + B(-262, -238, 186, 200, -90, -82, '#E8B04A', 'lamp') +
      B(-350, -340, 14, 220, -90, 0, 'var(--block)', 'hut', 'fs') +
      B(-288, -212, 14, 22, -64, 0, 'var(--main)', 'lid') +
      B(-160, -150, 14, 220, -100, 0, 'var(--block)', 'hut', 'fs') +
      B(-364, -136, 220, 234, -114, 0, 'color-mix(in srgb, var(--main) 45%, var(--block))', 'hut') +
      B(-132, -116, 14, 330, -100, -84, 'var(--blockdk)', 'vent', 'fs') + B(-136, -112, 330, 350, -104, -80, 'var(--second)', 'vent') +
      wbox(-136, -95) + F('y', 0, 'wt', R(P + '-w', -95, -100, 30, 70, wt)) +
      B(-95, -65, 0, 250, -30, 0, pale, '') + F('z', 0, '', R('', -91, -124, 22, 60, 'fill:#3E8F5A') + R('', -91, -184, 22, 60, 'fill:#E8B04A') + R('', -91, -244, 22, 60, 'fill:var(--accent)') +
        '<g class="' + P + '-float"><path d="M-112 0 H-48 M-48 0 l14 -11 v22 Z" style="stroke:var(--second);stroke-width:7;fill:var(--second)"/></g>') +
      wbox(-65, 230) +
      B(230, 330, 0, 60, -100, -90, 'var(--block)', '') + B(230, 240, 0, 60, -90, 0, 'var(--block)', '') +
      F('z', -50, '', '<path d="M218 0 V-200 M342 0 V-200 M204 -200 H356" style="stroke:var(--wood);stroke-width:12;fill:none;stroke-linecap:round"/><path d="M280 -200 V-128" style="stroke:var(--second);stroke-width:3"/><path d="M260 -128 H300 L295 -96 H265 Z" style="fill:var(--main)"/>') +
      B(320, 330, 0, 60, -100, 0, 'var(--block)', '') +
      wbox(330, 500) +
      // 4 on the cut plane, in front of everything: the lining rings that drop in, and the design flood mark
      F('z', 0, '', rings + '<path class="' + P + '-mark" d="M-470 -34 H-120" style="stroke:var(--accent);stroke-width:4;stroke-dasharray:14 10;fill:none;opacity:0"/>');
    let faces = [];
    const e = {};
    return {
      markup: markup,
      bind(root) {
        faces = Array.from(root.querySelectorAll('.f3')).map((el) => ({ el: el, k: el.dataset.k, o: +el.dataset.o, g: el.dataset.g || '' }));
        ['gws', 'gw', 'gwl', 'ww', 'taint', 'gin', 'pito', 'pitl', 'waste', 'spill', 'float', 'mark', 'pole', 'truck', 'can', 'rip', 'tree'].forEach((n) => { e[n] = root.querySelector('.' + P + '-' + n); });
        e.w = Array.from(root.querySelectorAll('.' + P + '-w')); e.wf = Array.from(root.querySelectorAll('.' + P + '-wf')); e.rings = Array.from(root.querySelectorAll('.' + P + '-ring'));
        seep.bind(root.querySelector('.seep'));
      },
      pose(v, st) {
        const k = W.kin(st.lv), c = (x) => Math.min(1, Math.max(0, x)), o = (x) => c(x).toFixed(3), t = st.t || 0;
        const lift = st.lift || 0, Z = [0, 0, 0];
        const D = { '': Z, base: Z, wt: [0, k.h, 0], hut: [0, lift, 0], lid: [-50 * (1 - (st.lid || 0)), lift, 0], vent: [0, 300 * (1 - (st.vent || 0)), 0], pack: [0, lift + 220 * (1 - (st.pack || 0)), 0], lamp: [0, lift, 0] };
        const A = { base: st.base || 0, lid: st.lidOn || 0, vent: (st.vent || 0) * 4, pack: (st.pack || 0) * 4, lamp: st.lamp || 0 };
        for (const q of faces) {
          q.el.setAttribute('transform', v.m(q.k, q.o, D[q.g] || Z));
          if (A[q.g] !== undefined) q.el.style.opacity = o(A[q.g]);
        }
        const gw = k.gw, wy = Math.max(26, gw);
        e.gw.setAttribute('y', gw.toFixed(1)); e.gw.setAttribute('height', (360 - gw).toFixed(1));
        e.gws.setAttribute('y', gw.toFixed(1)); e.gws.setAttribute('height', (360 - gw).toFixed(1));
        e.gwl.setAttribute('transform', 'translate(0 ' + gw.toFixed(1) + ')'); e.gwl.style.strokeDashoffset = (-t * 24).toFixed(1);
        e.ww.setAttribute('y', wy.toFixed(1)); e.ww.setAttribute('height', (330 - wy).toFixed(1));
        e.taint.setAttribute('y', wy.toFixed(1)); e.taint.setAttribute('height', (330 - wy).toFixed(1)); e.taint.style.opacity = o(0.8 * (st.taint || 0));
        e.gin.setAttribute('y', gw.toFixed(1)); e.gin.setAttribute('height', (310 - gw).toFixed(1));
        e.float.setAttribute('transform', 'translate(0 ' + (-(70 + 170 * k.lv)).toFixed(1) + ')');
        // an unlined pit fills as the water rises and spills at ground level; a lined one keeps the water out
        const lined = c(st.lined || 0), wTop = 205 - (1 - lined) * 207 * kit.eio(c((k.lv - 0.15) / 0.6));
        e.pito.style.opacity = o(1 - lined * 3); e.pitl.style.opacity = o(lined * 3);
        e.waste.setAttribute('y', wTop.toFixed(1)); e.waste.setAttribute('height', (252 - wTop).toFixed(1));
        const sp = c(st.spill || 0);
        e.spill.setAttribute('rx', (40 + 240 * sp).toFixed(1)); e.spill.setAttribute('ry', (16 + 100 * sp).toFixed(1)); e.spill.style.opacity = o(sp * 2.4);
        seep.render(t * 1.3, c(st.seep || 0));
        const wo = o(k.h / 5);
        for (const x of e.w) x.style.opacity = wo;
        for (const x of e.wf) { x.setAttribute('y', (-k.h).toFixed(1)); x.setAttribute('height', k.h.toFixed(1)); }
        e.rip.style.strokeDashoffset = (t * 40).toFixed(1);
        e.rings.forEach((r, i) => {
          const q = c(lined * 1.8 - (4 - i) * 0.2);
          r.setAttribute('transform', 'translate(0 ' + (-420 * (1 - kit.eo(q))).toFixed(1) + ')'); r.style.opacity = o(q * 6);
        });
        e.mark.style.opacity = o(st.mark || 0);
        e.pole.setAttribute('transform', 'translate(-40 0) rotate(' + (st.lean || 0).toFixed(2) + ')');
        e.truck.style.opacity = o(st.truck || 0);
        e.truck.setAttribute('transform', 'translate(' + (190 + 70 * (st.back || 0)).toFixed(1) + ' ' + (2 * Math.sin(t * 3)).toFixed(1) + ') rotate(' + (1.2 * Math.sin(t * 2.2)).toFixed(2) + ')');
        e.tree.setAttribute('transform', 'translate(410 0) rotate(' + (2 * Math.sin(t * 1.5) + 0.7 * Math.sin(t * 3.7)).toFixed(2) + ')');
        const fl = c(k.h / 20);
        e.can.setAttribute('transform', 'translate(' + (410 + 12 * fl * Math.sin(t * 0.9)).toFixed(1) + ' ' + (-k.h * 0.8 + 3 * fl * Math.sin(t * 2.4)).toFixed(1) + ') rotate(' + (fl * (9 + 5 * Math.sin(t * 1.9))).toFixed(2) + ')');
        return k;
      },
    };
  },
  // The console every scene shares: a window card with the model in it, a readout on the left and live gauges on the right. A scene adds its own words.
  rig(kit, id, o) {
    const m = window.W.model(kit, id);
    kit.stage.append(kit.h('<div class="ground td-bg"><div class="td-card"><div class="td-view"><svg class="art" viewBox="0 0 1800 744">' + m.markup + (o.svg || '') + '</svg>' + (o.tags || '') + '</div>' +
      '<div class="td-bar"><i></i><i></i><i></i><p class="td-file">FloodSafe Gambella · live cutaway</p></div>' +
      '<div class="td-panel td-left">' + o.left + '</div>' +
      '<div class="td-panel td-right"><p class="td-k">Groundwater</p><div class="td-track"><div class="td-fill ' + id + '-bg"></div></div><p class="td-k">Flood</p><div class="td-track"><div class="td-fill ' + id + '-bf"></div></div><p class="td-k">Signal</p>' +
      '<div class="td-lamps"><div class="td-lamp ' + id + '-lamp" style="background:#3E8F5A"></div><div class="td-lamp ' + id + '-lamp" style="background:#E8B04A"></div><div class="td-lamp ' + id + '-lamp" style="background:var(--accent)"></div></div></div></div>' + o.caps + '</div>'));
    m.bind(kit.stage);
    const q = (s) => kit.stage.querySelector(s), bg = q('.' + id + '-bg'), bf = q('.' + id + '-bf'), lamps = Array.from(kit.stage.querySelectorAll('.' + id + '-lamp'));
    return { m: m, q: q, all: (s) => Array.from(kit.stage.querySelectorAll(s)),
      // the panel reads the same numbers that pose the model
      gauges(k) {
        bg.style.transform = 'scaleX(' + (0.06 + 0.94 * k.lv).toFixed(4) + ')'; bf.style.transform = 'scaleX(' + (k.h / 44).toFixed(4) + ')';
        const w0 = 1 - kit.smoothstep(0.28, 0.36, k.lv), w2 = kit.smoothstep(0.63, 0.71, k.lv), w = [w0, 1 - w0 - w2, w2];
        lamps.forEach((l, i) => { l.style.opacity = (0.16 + 0.84 * w[i]).toFixed(3); l.style.transform = 'scale(' + (0.84 + 0.16 * w[i]).toFixed(3) + ')'; });
        return w;
      } };
  },
  // A label on a leader: the tag sits at the projected point p plus (dx,dy) and pops by a (0..1, may overshoot).
  callout(v, tag, line, p, dx, dy, a) {
    const s = v.pt(p[0], p[1], p[2]), op = Math.min(1, Math.max(0, a * 3)).toFixed(3);
    tag.style.opacity = op;
    tag.style.transform = 'translate(' + (s[0] + dx).toFixed(1) + 'px,' + (s[1] + dy).toFixed(1) + 'px) scale(' + Math.max(0, a).toFixed(3) + ')';
    line.setAttribute('d', 'M' + s[0].toFixed(1) + ' ' + s[1].toFixed(1) + ' L' + (s[0] + dx + 30).toFixed(1) + ' ' + (s[1] + dy + 26).toFixed(1) + ' M' + (s[0] - 7).toFixed(1) + ' ' + s[1].toFixed(1) + ' a7 7 0 1 0 14 0 a7 7 0 1 0 -14 0');
    line.style.opacity = op;
  },
  // Rain across the window: seeded streaks, each placed from t alone.
  drops(kit, n) {
    const r = kit.rng(n), list = Array.from({ length: n }, () => ({ x: r() * 1900, at: r(), v: 0.9 + r() * 0.5 }));
    return {
      markup: '<g class="drops">' + list.map(() => '<path style="stroke:color-mix(in srgb, var(--main) 55%, var(--ground));stroke-width:3;stroke-linecap:round;fill:none"/>').join('') + '</g>',
      bind(g) { list.forEach((p, i) => { p.el = g.children[i]; }); },
      render(t, on) {
        for (const p of list) {
          const q = (((t * p.v + p.at) % 1) + 1) % 1;
          p.el.setAttribute('d', 'M' + (p.x - 60 * q).toFixed(1) + ' ' + (-40 + 500 * q).toFixed(1) + ' l-8 36');
          p.el.style.opacity = (on * (q < 0.1 ? q * 10 : q > 0.8 ? (1 - q) * 5 : 1) * 0.7).toFixed(3);
        }
      },
    };
  },
});
window.W.tdEnd = {
  noop() {
    return 0;
  },
};
