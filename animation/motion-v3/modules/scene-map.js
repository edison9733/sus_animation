const { seg, eo, eob, eio, lerp, TextFx } = kit;
Object.assign(W, {
  // The same console window, showing one of the team's own maps instead of the model. o: { img, w, h, left, right, caps, over }.
  // over is markup drawn on the map in its own pixels, so it moves and scales with it.
  mapCard(kit, id, o) {
    kit.stage.append(kit.h('<div class="ground td-bg"><div class="td-card"><div class="td-view">' +
      '<div class="' + id + '-mapw" style="position:absolute;left:0;top:0;width:' + o.w + 'px;height:' + o.h + 'px;transform-origin:0px 0px">' +
        '<img src="' + kit.assets.url(o.img) + '" alt="" style="display:block;width:100%;height:100%;border-radius:6px;box-shadow:0 0 0 3px var(--ink3)"/>' + (o.over || '') + '</div>' + (o.tags || '') + '</div>' +
      '<div class="td-bar"><i></i><i></i><i></i><p class="td-file">' + o.file + '</p></div>' +
      '<div class="td-panel td-left">' + o.left + '</div>' + (o.right ? '<div class="td-panel td-right">' + o.right + '</div>' : '') + '</div>' + o.caps + '</div>'));
    const wrap = kit.stage.querySelector('.' + id + '-mapw');
    return {
      q: (s) => kit.stage.querySelector(s), all: (s) => Array.from(kit.stage.querySelectorAll(s)),
      // keys: [t0, t1, cx, cy, s] as in W.cam; the map point (cx,cy) sits at the window's middle at scale s, with a slow creep
      cam(keys, t) {
        let cx = keys[0][2], cy = keys[0][3], ls = Math.log(keys[0][4]);
        for (let i = 1; i < keys.length; i++) { const k = keys[i], p = kit.eio(kit.seg(t, k[0], k[1])); cx += (k[2] - cx) * p; cy += (k[3] - cy) * p; ls += (Math.log(k[4]) - ls) * p; }
        const s = Math.exp(ls) * (1 + 0.005 * Math.max(0, t));
        wrap.style.transform = 'translate(' + (900 - cx * s).toFixed(2) + 'px,' + (372 - cy * s).toFixed(2) + 'px) scale(' + s.toFixed(4) + ')';
        return (x, y) => [900 + (x - cx) * s, 372 + (y - cy) * s];
      },
    };
  },
});
kit.scene('map', {
  init(kit) {
    const M = this.M = W.mapCard(kit, 'map', {
      img: 'gambella-priority.webp', w: 1000, h: 1010, file: 'Gambela region · sanitation priority (own analysis)',
      over: '<svg viewBox="0 0 1000 1010" style="position:absolute;inset:0;width:100%;height:100%;overflow:visible"><ellipse class="map-ring" cx="300" cy="200" rx="235" ry="112" pathLength="1" style="fill:none;stroke:var(--second);stroke-width:5;stroke-dasharray:1 1"/></svg>',
      tags: '<div class="td-tag map-tg">Start here: Jikawo, Wantawo, Lare</div>',
      left: '<p class="td-k">Flood risk</p><p class="td-big map-n">50%</p><p class="td-s">of residents live where a 100-year river flood reaches</p>',
      caps: '<div class="words td-cap"><h2 class="td-capline map-cap">Most people live on a plain that floods</h2></div>',
    });
    Object.assign(this, { ring: M.q('.map-ring'), tg: M.q('.map-tg'), n: M.q('.map-n'), cap: M.q('.map-cap') });
    // the whole region, then a push onto the dark red north-west, where the first phase goes
    this.keys = [[0, 0, 520, 505, 0.74], [1.4, 3.0, 300, 230, 1.75]];
  },
  render(t) {
    const P = this.M.cam(this.keys, t);
    this.ring.style.strokeDashoffset = (1 - eio(seg(t, 3.0, 3.8))).toFixed(4);
    const a = Math.max(0, eob(seg(t, 3.6, 4.05), 1.7)), p = P(300, 88);
    this.tg.style.opacity = Math.min(1, a * 3).toFixed(3);
    this.tg.style.transform = 'translate(' + (p[0] - 165).toFixed(1) + 'px,' + (p[1] - 120).toFixed(1) + 'px) scale(' + a.toFixed(3) + ')';
    this.n.textContent = Math.round(lerp(25, 50, eo(seg(t, 0.3, 1.4)))) + '%';
    TextFx.fadeFromRight(this.cap, t, 0.2);
  },
});
