kit.score(function (S, T) {
  const B = 60 / 80;
  S.tempo(80, { t0: T.ask - 56 * B });   // beat 56 lands on the end card
  S.program('pad', 'pad', { rev: 0.6, gain: -2 }); S.program('bass', 'bass'); S.program('mallet', 'marimba', { rev: 0.3 }); S.program('bell', 'vibes', { rev: 0.5 });
  // The yard: a quiet open while the machine turns, a pop for each label, air under the push in.
  S.chord('pad', ['D3', 'A3', 'F4'], { t: 0, dur: 4.6, vel: 26 });
  S.note('mallet', 'A4', { t: 0.4, dur: 0.6, vel: 34 }); S.note('mallet', 'D5', { t: 1.0, dur: 0.6, vel: 38 }); S.note('mallet', 'F5', { t: 2.6, dur: 0.6, vel: 36 }); S.note('mallet', 'E5', { t: 3.4, dur: 0.8, vel: 32 });
  S.fx('pop', T.yard + 1.7, { vel: 40 }); S.fx('pop', T.yard + 2.1, { vel: 44 }); S.fx('whoosh', T.yard + 3.0, { dur: 1.2, vel: 24 });
  // The map: the push onto the flood plain, the ring drawn round the first woredas, the label.
  S.chord('pad', ['D3', 'G3', 'C4'], { t: T.map, dur: 6, vel: 30 });
  S.note('mallet', 'D5', { t: T.map + 0.4, dur: 0.6, vel: 34 }); S.note('mallet', 'C5', { t: T.map + 1.2, dur: 0.6, vel: 32 });
  S.fx('whoosh', T.map + 1.4, { dur: 1.6, vel: 30 }); S.fx('sparkle', T.map + 3.0, { vel: 34 }); S.fx('pop', T.map + 3.65, { vel: 46 });
  // The flood: darker pad, rain on the shaker, the push in to the pit, the pan to the well.
  S.chord('pad', ['D2', 'A2', 'F3', 'C4'], { t: T.flood, dur: 6.5, vel: 44 });
  S.drums({ shaker: 'oxoxoxoxoxoxoxox' }, { from: 14, repeat: 1 });
  S.fx('whoosh', T.flood + 0.5, { dur: 1.4, vel: 40 }); S.fx('thud', T.flood + 3.2, { vel: 50, pitch: -6 }); S.fx('whoosh', T.flood + 3.3, { dur: 1.2, vel: 28 });
  S.note('bass', 'D2', { t: T.flood + 0.8, dur: 2, vel: 50 }); S.note('bass', 'C2', { t: T.flood + 3.3, dur: 2.6, vel: 50 });
  // Why pits fail: a struck mark for each.
  S.chord('pad', ['A#1', 'F2', 'D3', 'A3'], { t: T.cutoff, dur: 5.5, vel: 46 });
  [0, 1, 2, 3].forEach((i) => { S.fx('thud', T.cutoff + 0.55 + i * 0.5, { vel: 60 }); S.note('mallet', ['D4', 'C4', 'A#3', 'A3'][i], { t: T.cutoff + 0.55 + i * 0.5, dur: 0.4, vel: 56 }); });
  // The zones: lighter, a note as each design is listed.
  S.chord('pad', ['F3', 'A3', 'D4'], { t: T.zones, dur: 6.5, vel: 34 });
  ['F5', 'A5', 'C6', 'A5'].forEach((p, i) => S.note('mallet', p, { t: T.zones + 0.65 + i * 0.45, dur: 0.4, vel: 46 }));
  S.fx('whoosh', T.zones + 1.6, { dur: 1.6, vel: 26 });
  // The kit: the groove comes in, brighter, in F. Each part lands with its own sound.
  S.fx('revswell', T.kit, { dur: 0.8, vel: 40 });
  [0, 1, 2, 3, 4].forEach((j) => S.fx('tick', T.kit + 1.38 + j * 0.155, { vel: 46 }));
  S.fx('thud', T.kit + 2.7, { vel: 58 }); S.fx('click', T.kit + 3.6, { vel: 50 }); S.fx('whoosh', T.kit + 3.9, { dur: 0.6, vel: 30, into: 1 });
  S.fx('sparkle', T.kit + 4.8, { vel: 40 }); S.fx('pop', T.kit + 6.0, { vel: 52 });
  S.chord('pad', ['F3', 'A3', 'C4'], { beat: 39, beats: 4, vel: 40 }); S.chord('pad', ['C3', 'G3', 'E4'], { beat: 43, beats: 4, vel: 40 });
  S.chord('pad', ['A#2', 'F3', 'D4'], { beat: 47, beats: 4, vel: 42 }); S.chord('pad', ['C3', 'G3', 'E4'], { beat: 51, beats: 4, vel: 34 });
  S.pattern('bass', 'x...x.x.', { from: 39, repeat: 4, pitch: ['F2', 'F2', 'C3', 'C2', 'C2', 'G2', 'A#1', 'A#1', 'F2', 'C2', 'C2', 'G2'], vel: 60 });
  S.pattern('mallet', 'x.x.X.x.', { from: 39, repeat: 4, pitch: ['F5', 'A5', 'C6', 'A5', 'G5', 'E5', 'G5', 'C5', 'D5', 'F5', 'A5', 'F5', 'E5', 'G5', 'C6', 'G5'], vel: 48 });
  S.drums({ kick: 'x.......x.......', hat: '..o...o...o...o.', sidestick: '............x...' }, { from: 39, repeat: 1 });
  S.drums({ kick: 'x.......x.......', hat: '..o...o...o...o.' }, { from: 47, repeat: 1 });
  // The signal: a bell for yellow, a higher one for red, then the lid shuts and the pack is marked.
  S.fx('ding', T.signal + 1.5, { vel: 46 }); S.fx('ding', T.signal + 3.1, { vel: 56, pitch: 5 }); S.fx('whoosh', T.signal + 3.5, { dur: 1.0, vel: 26 });
  S.fx('click', T.signal + 4.3, { vel: 54 }); S.fx('pop', T.signal + 4.6, { vel: 48 });
  // The pilot: swell, land the hit on the end card and let it ring.
  S.fx('revswell', T.ask, { dur: 1.4, vel: 50 });
  S.chord('pad', ['F2', 'C3', 'A3', 'F4'], { beat: 56, beats: 8, vel: 72 });
  S.note('bass', 'F1', { beat: 56, beats: 5, vel: 80 });
  S.drum('kick', { beat: 56, vel: 90 }); S.drum('crash', { beat: 56, vel: 46 });
  S.run('mallet', ['C5', 'F5', 'A5', 'C6'], { t: T.ask + 0.05, step: 0.09, vel: 66, cresc: 1.1 });
  S.fx('chime', T.ask + 0.9, { vel: 50 }); S.fx('pop', T.ask + 1.85, { vel: 40 });
  S.chord('bell', ['F5', 'A5', 'C6'], { t: T.ask + 1.1, dur: 3.4, vel: 36 });
  S.master({ gain: -8, fadeOut: 1.5 });
});
