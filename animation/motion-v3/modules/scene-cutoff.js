const { seg, eo, eob, eio, lerp, TextFx } = kit;
kit.scene('cutoff', {
  init(kit) {
    this.rain = W.drops(kit, 60);
    const ld = '<path class="cutoff-ld" style="stroke:var(--accent);stroke-width:3;fill:var(--accent)"/>';
    const R = this.R = W.rig(kit, 'cutoff', {
      svg: this.rain.markup + ld + ld + ld + ld,
      tags: '<div class="td-tag td-x cutoff-tg">Unsafe at night</div><div class="td-tag td-x cutoff-tg">Waste reaches wells</div>' +
        '<div class="td-tag td-x cutoff-tg">97.2% never emptied</div><div class="td-tag td-x cutoff-tg">Swelling clay cracks pits</div>',
      left: '<p class="td-k">The problem</p><p class="td-s cutoff-s">Pit latrines flood, collapse in swelling clay and are never emptied</p>',
      caps: '<div class="words td-cap"><h2 class="td-capline cutoff-cap">Why pit latrines fail here</h2></div>',
    });
    this.rain.bind(R.q('.drops'));
    Object.assign(this, { tg: R.all('.cutoff-tg'), ld: R.all('.cutoff-ld'), s: R.q('.cutoff-s'), cap: R.q('.cutoff-cap') });
    // where each failure sits on the machine, and where its label stands: hut, well, pit, clay
    this.at = [[[-250, 234, -50], -250, -104], [[280, 62, -50], 30, -130], [[-250, -170, 0], 60, 30], [[120, -330, 0], 60, -110]];
    // wide again, the table turning back the other way
    this.keys = [[0, 0, 30, 22, 0.84, 0, -40, -120], [0, 4.5, 8, 20, 0.88, 0, -40, -120]];
  },
  render(t) {
    const v = W.cam(kit, this.keys, t);
    const k = this.R.m.pose(v, { lv: 0.96 + 0.03 * Math.sin(t * 1.7), t: t + 6, spill: 1, seep: 1, taint: 1 });
    this.R.gauges(k);
    this.rain.render(t * 1.4 + 3, 1);
    this.at.forEach((p, i) => W.callout(v, this.tg[i], this.ld[i], p[0], p[1], p[2], eob(seg(t, 0.5 + i * 0.5, 0.95 + i * 0.5), 1.7)));
    const a = eo(seg(t, 0.1, 0.6));
    this.s.style.opacity = a.toFixed(3); this.s.style.transform = 'translateX(' + lerp(30, 0, a).toFixed(1) + 'px)';
    TextFx.fadeFromRight(this.cap, t, 0.1);
  },
});
