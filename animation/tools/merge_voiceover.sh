#!/usr/bin/env bash
# Merge the exported FloodSafe animation with the 8 ElevenLabs narration clips.
# Usage: tools/merge_voiceover.sh <animation.mp4> <folder with 01.mp3 … 08.mp3> [output.mp4]
# Each clip starts at its scene's start time (see voiceover/clips.csv). The film's music is lowered
# under the voice (sidechain ducking). Needs ffmpeg.
set -euo pipefail
VIDEO="$1"; VO="$2"; OUT="${3:-FloodSafe_with_voiceover.mp4}"
STARTS=(0 4.5 10.5 17 22.5 29 36.5 42)   # scene starts in seconds: yard map flood cutoff zones kit signal ask
inputs=(-i "$VIDEO"); filt=""; labels=""
for i in "${!STARTS[@]}"; do
  n=$(printf "%02d" $((i+1))); f="$VO/$n.mp3"
  [ -f "$f" ] || { echo "missing $f" >&2; exit 1; }
  inputs+=(-i "$f")
  ms=$(awk "BEGIN{printf \"%d\", ${STARTS[$i]}*1000}")
  filt+="[$((i+1)):a]aresample=48000,aformat=channel_layouts=stereo,adelay=${ms}|${ms}[v$i];"
  labels+="[v$i]"
done
# all voice clips on one track; it ducks the music, then both are mixed
filt+="${labels}amix=inputs=${#STARTS[@]}:normalize=0,volume=1.6,apad,asplit=2[voice][key];"
if ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$VIDEO" | grep -q .; then
  filt+="[0:a]aresample=48000,aformat=channel_layouts=stereo,volume=0.8[mus];[mus][key]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[duck];[duck][voice]amix=inputs=2:normalize=0:duration=first[out]"
else
  filt+="[key]anullsink;[voice]anull[out]"   # exported without sound: voice only
fi
ffmpeg -y "${inputs[@]}" -filter_complex "$filt" -map 0:v -map "[out]" -c:v copy -c:a aac -b:a 192k -shortest "$OUT"
echo "wrote $OUT"
