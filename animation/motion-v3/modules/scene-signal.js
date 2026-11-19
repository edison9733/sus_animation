const { seg, eo, ei, eob, eio, lerp, TextFx } = kit;
kit.scene('signal', {
  init(kit) {
    const R = this.R = W.rig(kit, 'signal', {
      svg: '<path class="signal-ld" style="stroke:var(--accent);stroke-width:3;fill:var(--accent)"/>',
      tags: '<div class="td-tag td-x signal-tg">Emergency pack</div>',
      left: '<p class="td-k">Warning signs</p><p class="td-s signal-r" style="border-left:14px solid #3E8F5A;padding-left:16px">Green: use as usual</p>' +
        '<p class="td-s signal-r" style="border-left:14px solid #E8B04A;padding-left:16px">Yellow: treat drinking water</p>' +
        '<p class="td-s signal-r" style="border-left:14px solid var(--accent);padding-left:16px">Red: seal the lid, use the pack</p>',
      caps: '<div class="words td-cap"><h2 class="td-capline signal-cap0">Green, yellow, red. No power needed</h2></div>' +
        '<div class="words td-cap"><h2 class="td-capline signal-cap1">At red, seal the lid and use the pack</h2></div>',
    });
    Object.assign(this, { tg: R.q('.signal-tg'), ld: R.q('.signal-ld'), rows: R.all('.signal-r'), cap0: R.q('.signal-cap0'), cap1: R.q('.signal-cap1') });
    // close on the gauge while the float climbs, then back to see the lid seal and the pack
    this.keys = [[0, 0, 10, 10, 2.2, -20, 150, 0], [3.4, 4.7, 22, 18, 1.15, -200, 60, -50]];
  },
  render(t) {
    const v = W.cam(kit, this.keys, t);
    const lv = 0.1 + 0.4 * eio(seg(t, 0.9, 1.8)) + 0.42 * eio(seg(t, 2.5, 3.4)) + 0.012 * Math.sin(t * 2.1);
    const k = this.R.m.pose(v, { lv: lv, t: t, lined: 1, mark: 1, base: 1, lift: 46, lidOn: 1, lid: eio(seg(t, 3.8, 4.3)), vent: 1, pack: 1, lamp: 1 });
    const w = this.R.gauges(k);
    this.rows.forEach((r, i) => {
      const a = eo(seg(t, -0.3 + i * 0.2, 0.2 + i * 0.2));
      r.style.opacity = (a * lerp(0.4, 1, w[i])).toFixed(3);
      r.style.transformOrigin = '0px 50%';
      r.style.transform = 'translateX(' + lerp(26, 0, a).toFixed(1) + 'px) scale(' + lerp(1, 1.05, w[i]).toFixed(4) + ')';
    });
    W.callout(v, this.tg, this.ld, [-400, 262, -40], -290, -84, eob(seg(t, 4.5, 4.95), 1.7));
    TextFx.fadeFromRight(this.cap0, t, -0.3);
    this.cap0.parentNode.style.opacity = (1 - ei(seg(t, 3.3, 3.65))).toFixed(3);
    TextFx.fadeFromRight(this.cap1, t, 3.75);
  },
});
