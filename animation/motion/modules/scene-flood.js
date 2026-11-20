const { seg, eo, ei, eio, lerp, TextFx } = kit;
kit.scene('flood', {
  init(kit) {
    this.rain = W.drops(kit, 60);
    const R = this.R = W.rig(kit, 'flood', {
      svg: this.rain.markup,
      left: '<p class="td-k">Gambela</p><div class="td-blk flood-s1"><p class="td-big flood-n1" style="font-size:60px">185,200</p><p class="td-s" style="font-size:28px">displaced by the 2022 flood</p></div>' +
        '<div class="flood-ch"><p class="td-ck">People displaced by floods</p>' + W.colsHtml('flood-c', [["'19", 11128, 'var(--main)', ''], ["'20", 18819, 'var(--main)', ''], ["'21", 11749, 'var(--main)', ''], ["'22", 185200, 'var(--accent)', '185k'], ["'23", 25140, 'var(--main)', ''], ["'24", 41060, 'var(--main)', ''], ["'25", 35410, 'var(--main)', '']], 185200) + '</div>' +
        '<div class="td-blk flood-s2"><p class="td-big flood-n2" style="font-size:60px">2,194</p><p class="td-s" style="font-size:28px">cholera cases, Jan–May 2025</p></div>',
      caps: '<div class="words td-cap"><h2 class="td-capline flood-cap0">Water rises from above and below</h2></div>' +
        '<div class="words td-cap"><h2 class="td-capline flood-cap1">Waste reaches the well</h2></div>',
    });
    this.rain.bind(R.q('.drops'));
    Object.assign(this, { cols: R.all('.flood-c'), ch: R.q('.flood-ch'), s1: R.q('.flood-s1'), s2: R.q('.flood-s2'), n1: R.q('.flood-n1'), n2: R.q('.flood-n2'), cap0: R.q('.flood-cap0'), cap1: R.q('.flood-cap1') });
    // close on the pit while it fills, then follow the waste through the soil to the well
    this.keys = [[0, 0, 20, 18, 1.1, -60, -30, -60], [0.5, 2.0, 12, 13, 2.05, -250, -70, 0], [3.3, 4.6, 24, 13, 1.95, 250, -190, 0]];
  },
  render(t) {
    const v = W.cam(kit, this.keys, t);
    const k = this.R.m.pose(v, { lv: lerp(0.08, 1, eio(seg(t, 0.2, 3.2))), t: t, spill: eo(seg(t, 2.0, 4.2)), seep: seg(t, 1.8, 2.4), taint: eio(seg(t, 3.8, 5.8)) });
    this.R.gauges(k);
    this.rain.render(t * 1.4, 1);
    const a = eo(seg(t, 0.4, 0.9)), b = eo(seg(t, 2.9, 3.4));
    this.s1.style.opacity = a.toFixed(3); this.s1.style.transform = 'translateX(' + lerp(30, 0, a).toFixed(1) + 'px)';
    this.s2.style.opacity = b.toFixed(3); this.s2.style.transform = 'translateX(' + lerp(30, 0, b).toFixed(1) + 'px)';
    this.ch.style.opacity = kit.seg(t, 0.8, 1.1).toFixed(3);
    W.grow(kit, this.cols, t, 1.0, 0.14, 'y');
    this.n1.textContent = Math.round(lerp(92600, 185200, eo(seg(t, 0.4, 1.6)))).toLocaleString('en-US');
    this.n2.textContent = Math.round(lerp(1100, 2194, eo(seg(t, 2.9, 4.0)))).toLocaleString('en-US');
    TextFx.fadeFromRight(this.cap0, t, 0.15);
    this.cap0.parentNode.style.opacity = (1 - ei(seg(t, 3.0, 3.35))).toFixed(3);
    TextFx.fadeFromRight(this.cap1, t, 3.5);
  },
});
