// Parts that change shape with the water. Pure: (kit, projection, geometry, pose) -> attribute values.
// The build calls it for the first frame, and the page inlines this same source and calls it every frame.

export function dynamic(k, P, G) {
  const at = (p) => k.iso(p, P);
  const poly = (pts) => k.pathOf(pts.map(at), true);
  const front = (x0, x1, z0, z1) => poly([[x0, G.CUT, z0], [x1, G.CUT, z0], [x1, G.CUT, z1], [x0, G.CUT, z1]]);
  const side = (x, y0, y1, z0, z1) => poly([[x, y0, z0], [x, y1, z0], [x, y1, z1], [x, y0, z1]]);
  const B = G.BLOCK;
  const xR = B.x + B.w, yB = B.y;

  // the band of a box's two visible outer faces under the water, minus any face that lies on the cut
  const boxBand = (p, h) => {
    const out = [side(p.x + p.w, p.y, p.y + p.d, 0, h)];
    if (p.y + p.d < G.CUT - 0.01) out.push(poly([[p.x, p.y + p.d, 0], [p.x + p.w, p.y + p.d, 0], [p.x + p.w, p.y + p.d, h], [p.x, p.y + p.d, h]]));
    return out.join("");
  };
  // the band on the visible part of a round post (or the half pipe on the cut)
  const roundBand = (cx, cy, r, h, cutY) => {
    const v = k.towardViewer(P), pts = [];
    for (let i = 0; i <= 48; i++) {
      const a = (i / 48) * Math.PI * 2, nx = Math.cos(a), ny = Math.sin(a);
      if (nx * v[0] + ny * v[1] <= 0) continue;
      if (cutY !== undefined && cy + r * ny > cutY + 1e-6) continue;
      pts.push([cx + r * nx, cy + r * ny]);
    }
    if (pts.length < 2) return "";
    pts.sort((p, q) => Math.atan2(p[1] - cy, p[0] - cx) - Math.atan2(q[1] - cy, q[0] - cx));
    return poly([...pts.map(([x, y]) => [x, y, 0]), ...pts.reverse().map(([x, y]) => [x, y, h])]);
  };

  return function draw(s) {
    const { gw, h, pointer } = s.k;
    const d = {};
    // groundwater: from the block bottom up to its surface, on the cut and on the right side
    d.gwFront = front(B.x, xR, -G.DEPTH, gw);
    d.gwSide = side(xR, yB, G.CUT, -G.DEPTH, gw);
    d.gwLine = k.pathOf([at([B.x, G.CUT, gw]), at([xR, G.CUT, gw]), at([xR, yB, gw])]);
    // inside the gauge pipe the water stands at the groundwater level; the float rides on it
    d.bore = front(G.GX - G.GBORE, G.GX + G.GBORE, -G.GDEEP, gw);
    d.float = front(G.GX - G.GBORE + 1, G.GX + G.GBORE - 1, gw - 3, gw + 5);
    d.rodLow = front(G.GX - 0.8, G.GX + 0.8, gw + 5, G.GTOP);
    // above the cap the rod is round; it is rebuilt to its length each frame
    const top = pointer;
    const rod = k.cylinder(G.GX, G.ROD_Y, 1.3, G.GTOP + 4, Math.max(0.1, top - G.GTOP - 4), P, 14);
    d.rodFill = rod.fill; d.rodShade = rod.shades.filter(Boolean).join(""); d.rodTop = rod.top; d.rodEdge = rod.outline;
    d.pointer = k.translateAlong(P, [0, 0, top]);
    d.lid = k.translateAlong(P, [0, -G.LID_TRAVEL * (1 - s.lid), 0]);
    // floodwater over the yard: a sheet at depth h, its two cut sides, and a band on everything standing in it
    const wet = h > 0.05;
    d.sheet = wet ? poly([[B.x, yB, h], [xR, yB, h], [xR, G.CUT, h], [B.x, G.CUT, h]]) : "";
    d.sheetRim = wet ? k.pathOf([at([B.x, G.CUT, h]), at([B.x, yB, h]), at([xR, yB, h])]) : "";
    d.sheetFront = wet ? front(B.x, xR, 0, h) : "";
    d.sheetSide = wet ? side(xR, yB, G.CUT, 0, h) : "";
    d.waterline = wet ? k.pathOf([at([B.x, G.CUT, h]), at([xR, G.CUT, h]), at([xR, yB, h])]) : "";
    for (const c of G.COLLARS) d["collar-" + c.id] = wet ? (c.round ? roundBand(c.cx, c.cy, c.r, Math.min(h, c.top ?? h), c.cutY) : boxBand(c.plan, Math.min(h, c.top ?? h))) : "";
    return d;
  };
}
