const { seg, eo, eob, eio, lerp, TextFx } = kit;
kit.scene('kit', {
  init(kit) {
    const ld = '<path class="kit-ld" style="stroke:var(--main);stroke-width:3;fill:var(--main)"/>';
    const R = this.R = W.rig(kit, 'kit', {
      svg: ld + ld + ld + ld + ld,
      tags: '<div class="td-tag td-ok kit-tg">Lined pit walls</div><div class="td-tag td-ok kit-tg">Raised slab, sliding lid</div>' +
        '<div class="td-tag td-ok kit-tg">Vent with fly screen</div><div class="td-tag td-ok kit-tg">Lock and solar light</div><div class="td-tag td-ok kit-tg">Emergency pack</div>',
      left: '<p class="td-k">Zone B, built</p><p class="td-s kit-s">Built and repaired by trained local masons</p>' +
        '<div class="td-blk kit-c"><p class="td-ck">Cost per household</p><p class="td-big" style="font-size:60px">USD 350</p><p class="td-src">estimate, range USD 200–500 (zone B unit)</p></div>',
      caps: '<div class="words td-cap"><h2 class="td-capline kit-cap">Upgrade the latrine families already have</h2></div>',
    });
    Object.assign(this, { c: R.q('.kit-c'), tg: R.all('.kit-tg'), ld: R.all('.kit-ld'), s: R.q('.kit-s'), cap: R.q('.kit-cap') });
    // each part, where its label stands, and when it lands
    this.at = [[[-162, -125, 0], 50, -30, 1.5], [[-138, 52, 0], 50, -20, 2.8], [[-124, 345, -92], 50, -40, 4.3], [[-238, 239, -86], 150, -60, 5.0], [[-400, 216, -40], -300, -90, 6.0]];
    // close on the pit for the lining, up to the slab and lid, then back for the vent, the light and the pack
    this.keys = [[0, 0, 24, 18, 1.45, -200, 40, -40], [0.3, 1.5, 12, 12, 1.75, -190, -70, 0], [1.9, 3.0, 18, 16, 1.6, -180, 40, -20], [3.6, 4.8, 28, 20, 1.2, -210, 90, -50]];
  },
  render(t) {
    const v = W.cam(kit, this.keys, t);
    const k = this.R.m.pose(v, { lv: 0.12 + 0.02 * Math.sin(t * 1.3), t: t,
      lined: seg(t, 0.6, 2.0), mark: eo(seg(t, 2.0, 2.3)), base: seg(t, 2.1, 2.4), lift: 46 * Math.max(0, eob(seg(t, 2.2, 2.8), 1.6)),
      lidOn: seg(t, 3.0, 3.2), lid: eio(seg(t, 3.1, 3.6)), vent: eo(seg(t, 3.9, 4.5)), lamp: eo(seg(t, 4.7, 5.1)) * (0.85 + 0.15 * Math.sin(t * 5)),
      pack: Math.max(0, eob(seg(t, 5.5, 6.1), 1.6)) });
    this.R.gauges(k);
    this.at.forEach((p, i) => W.callout(v, this.tg[i], this.ld[i], p[0], p[1], p[2], eob(seg(t, p[3], p[3] + 0.45), 1.7)));
    const a = eo(seg(t, 0.2, 0.7));
    this.s.style.opacity = a.toFixed(3); this.s.style.transform = 'translateX(' + lerp(30, 0, a).toFixed(1) + 'px)';
    const c = eo(seg(t, 1.0, 1.5));
    this.c.style.opacity = c.toFixed(3); this.c.style.transform = 'translateX(' + lerp(30, 0, c).toFixed(1) + 'px)';
    TextFx.fadeFromRight(this.cap, t, 0.2);
  },
});
