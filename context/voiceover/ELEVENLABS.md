# Voiceover for the FloodSafe animation (current 48.5 s version)

Generate 8 separate clips with ONE voice and the same settings, download as MP3, name them 01.mp3 … 08.mp3.
Each clip must finish before its scene ends (see clips.csv). Clips 4, 6 and 7 are the tightest: raise speed slightly or regenerate if long.
Numbers are spelled out on purpose so the voice reads them correctly.

| # | Starts | Scene | Text |
|---|---|---|---|
| 1 | 0:00 | The yard | In Gambela, Ethiopia, nearly half of people still defecate in the open. |
| 2 | 0:04.5 | The flood plain (map) | Half of residents live on a plain that floods. We start in Jikawo, Wantawo and Lare. |
| 3 | 0:10.5 | The flood | In 2022, floods displaced a hundred and eighty-five thousand people. Pits overflow, and waste reaches the wells. |
| 4 | 0:17 | Why pits fail | Pits flood, crack in swelling clay and are never emptied, and nights are unsafe. |
| 5 | 0:22.5 | Four designs (map) | So we match the toilet to the ground: four designs, chosen from flood and soil data. |
| 6 | 0:29 | The kit | Local masons upgrade the latrine families have: lined walls, a raised slab, a vent, a lock and a solar light. |
| 7 | 0:36.5 | The signal | Green, yellow, red: no power needed. At red, seal the lid and use the pack. |
| 8 | 0:42 | The pilot | FloodSafe Sanitation Gambella: a five-hundred-household pilot, and we're looking for partners. |

Then: `tools/merge_voiceover.sh FloodSafe.mp4 <folder-with-01..08.mp3> FloodSafe_with_voiceover.mp4`

## ElevenLabs connector for Claude (optional)
Official hosted MCP server: https://api.elevenlabs.io/v1/mcp (OAuth sign-in, no API key).
Claude app: Settings → Connectors → Add custom connector → name "ElevenLabs", URL above → Add → sign in → Authorize.
Claude Code: `claude mcp add --transport http elevenlabs https://api.elevenlabs.io/v1/mcp` (then authenticate with /mcp).
It can generate speech with any voice in the workspace; links expire after ~2 h; each generation uses ElevenLabs credits and returns two takes.
Docs: https://elevenlabs.io/docs/eleven-api/resources/mcp-server

## Instant voice cloning
Needs a real 1–2 minute recording of the voice to clone (your own, or someone who agreed). See VOICE_CLONE_READING_TEXT.md for a text to read.
