const { seg, eo, eob, eio, lerp, TextFx } = kit;
kit.scene('yard', {
  init(kit) {
    const R = this.R = W.rig(kit, 'yard', {
      svg: '<path class="yard-ld0" style="stroke:var(--second);stroke-width:3;fill:var(--second)"/><path class="yard-ld1" style="stroke:var(--second);stroke-width:3;fill:var(--second)"/>',
      tags: '<div class="td-tag yard-tg0">Pit latrine</div><div class="td-tag yard-tg1">Shallow well</div>',
      left: '<p class="td-k">Gambela, Ethiopia</p><p class="td-big yard-n">47%</p><p class="td-s">practise open defecation (DHS 2024)</p>',
      caps: '<div class="words td-cap"><h1 class="td-capline yard-cap">Toilets that survive the flood</h1></div>',
    });
    Object.assign(this, { n: R.q('.yard-n'), cap: R.q('.yard-cap'), tg: [R.q('.yard-tg0'), R.q('.yard-tg1')], ld: [R.q('.yard-ld0'), R.q('.yard-ld1')] });
    // the machine turns on its table, then one push in
    this.keys = [[0, 0, 6, 16, 0.84, 0, -40, -120], [0.2, 3.0, 30, 20, 0.84, 0, -40, -120], [3.0, 4.3, 22, 18, 1.08, 40, 10, -60]];
  },
  render(t) {
    const v = W.cam(kit, this.keys, t);
    const k = this.R.m.pose(v, { lv: 0.06 + 0.02 * Math.sin(t * 1.3), t: t });
    this.R.gauges(k);
    this.n.textContent = Math.round(lerp(24, 47, eo(seg(t, -0.6, 0.9)))) + '%';
    TextFx.fadeFromRight(this.cap, t, -0.45);
    W.callout(v, this.tg[0], this.ld[0], [-250, 234, -50], -90, -96, eob(seg(t, 1.6, 2.05), 1.7));
    W.callout(v, this.tg[1], this.ld[1], [280, 206, -50], -60, -84, eob(seg(t, 2.0, 2.45), 1.7));
  },
});
