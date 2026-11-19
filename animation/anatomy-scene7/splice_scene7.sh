#!/bin/sh
# Put the Anatomy version of scene 7 ("The signal", 36.5–42.0 s) into the exported v3 film.
# The picture from 36.5 s to 42.0 s is replaced; the film's own audio (score) is kept untouched,
# so tools/merge_voiceover.sh still lines up with the cuts afterwards.
#
# usage: ./splice_scene7.sh FloodSafe.mp4 [FloodSafe_v3_anatomy.mp4]
set -eu
IN="${1:?usage: $0 FloodSafe.mp4 [out.mp4]}"
OUT="${2:-FloodSafe_v3_anatomy.mp4}"
CLIP="$(dirname "$0")/FloodSafe_scene7_signal_anatomy.mp4"
[ -f "$CLIP" ] || { echo "missing $CLIP (run: node render-film.mjs)"; exit 1; }

# does the export have an audio track?
if ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$IN" | grep -q .; then AMAP="-map 0:a -c:a copy"; else AMAP=""; fi

ffmpeg -y -loglevel error -i "$IN" -i "$CLIP" -filter_complex "\
[0:v]trim=0:36.5,setpts=PTS-STARTPTS,fps=60,scale=1920:1080,setsar=1,format=yuv420p[a];\
[1:v]trim=0:5.5,setpts=PTS-STARTPTS,fps=60,scale=1920:1080,setsar=1,format=yuv420p[b];\
[0:v]trim=start=42,setpts=PTS-STARTPTS,fps=60,scale=1920:1080,setsar=1,format=yuv420p[c];\
[a][b][c]concat=n=3:v=1:a=0[v]" \
  -map "[v]" $AMAP -c:v libx264 -crf 16 -preset slow -pix_fmt yuv420p -movflags +faststart "$OUT"
echo "wrote $OUT"
