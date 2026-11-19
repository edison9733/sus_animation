const { seg, eo, eio, lerp, TextFx } = kit;
kit.scene('ask', {
  init(kit) {
    const R = this.R = W.rig(kit, 'ask', {
      left: '<p class="td-k">The pilot</p><div class="td-blk ask-s1"><p class="td-big ask-n">500</p><p class="td-s">households, about 2,900 people</p></div>' +
        '<div class="td-blk ask-s2"><p class="td-big" style="font-size:60px">USD 540k</p><p class="td-s">estimated pilot cost</p></div>',
      caps: '<div class="words td-cap"><h1 class="td-capline ask-name" style="font-size:96px">FloodSafe Sanitation Gambella</h1><p class="td-s ask-sub">Pilot in Jikawo, Wantawo and Lare, plus one refugee camp</p></div>',
    });
    Object.assign(this, { s1: R.q('.ask-s1'), s2: R.q('.ask-s2'), n: R.q('.ask-n'), name: R.q('.ask-name'), sub: R.q('.ask-sub') });
    // the finished latrine, turning slowly under the name
    this.keys = [[0, 0, 8, 18, 0.8, 0, -30, -120], [0, 6.5, 30, 20, 0.88, 0, -30, -120]];
  },
  render(t) {
    const v = W.cam(kit, this.keys, t);
    const k = this.R.m.pose(v, { lv: 0.08 + 0.03 * Math.sin(t * 1.3), t: t, lined: 1, mark: 1, base: 1, lift: 46, lidOn: 1, lid: 0, vent: 1, pack: 1, lamp: 1 });
    this.R.gauges(k);
    const a = eo(seg(t, 0.3, 0.8)), b = eo(seg(t, 1.8, 2.3));
    this.s1.style.opacity = a.toFixed(3); this.s1.style.transform = 'translateX(' + lerp(30, 0, a).toFixed(1) + 'px)';
    this.s2.style.opacity = b.toFixed(3); this.s2.style.transform = 'translateX(' + lerp(30, 0, b).toFixed(1) + 'px)';
    this.n.textContent = Math.round(lerp(250, 500, eo(seg(t, 0.3, 1.3))));
    TextFx.fadeFromRight(this.name, t, 0.1);
    const c = eo(seg(t, 1.0, 1.5));
    this.sub.style.opacity = c.toFixed(3); this.sub.style.transform = 'translateY(' + lerp(16, 0, c).toFixed(1) + 'px)';
  },
});
