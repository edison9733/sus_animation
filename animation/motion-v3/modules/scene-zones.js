const { seg, eo, eio, lerp, TextFx } = kit;
kit.scene('zones', {
  init(kit) {
    const row = (c, z, name, n) => '<p class="td-s zones-r" style="display:flex;gap:14px;align-items:baseline"><b style="flex:none;width:40px;height:40px;border-radius:8px;background:' + c + ';color:var(--ground);text-align:center;line-height:40px;font-size:26px">' + z + '</b><span>' + name + ' <b style="color:var(--accent)">' + n + '</b></span></p>';
    const M = this.M = W.mapCard(kit, 'zones', {
      img: 'gambella-zones.webp', w: 1000, h: 1015, file: 'Gambela region · toilet type per area (own analysis)',
      left: '<p class="td-k">Pick the design</p>' + row('#1F5A8C', 'A', 'Raised / sealed', '211k') + row('#7DB3DA', 'B', 'Raised slab, lined pit', '110k') +
        row('#D2AD6A', 'C', 'Lined pit on clay', '275k') + row('#8C6A5A', 'D', 'Steep ground', '36k'),
      caps: '<div class="words td-cap"><h2 class="td-capline zones-cap">Four designs for four kinds of ground</h2></div>',
    });
    Object.assign(this, { rows: M.all('.zones-r'), cap: M.q('.zones-cap') });
    // the whole region, then in over the blue flood plain
    this.keys = [[0, 0, 520, 505, 0.74], [1.6, 3.4, 340, 330, 1.3]];
  },
  render(t) {
    this.M.cam(this.keys, t);
    this.rows.forEach((r, i) => {
      const a = eo(seg(t, 0.6 + i * 0.45, 1.1 + i * 0.45));
      r.style.opacity = a.toFixed(3); r.style.transform = 'translateX(' + lerp(26, 0, a).toFixed(1) + 'px)';
    });
    TextFx.fadeFromRight(this.cap, t, 0.15);
  },
});
