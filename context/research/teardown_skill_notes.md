# The reel's skill: "Teardown" (used as the style reference for the animation)

Reel: https://www.instagram.com/reel/DfLmQwWp5E8/ (guipaulinooo) promotes **Teardown**, a free Claude Code skill by Elvar
(https://github.com/elvarofficial/teardown, MIT). It builds an offline interactive 3D simulator of a machine as one HTML page:
the machine in the middle, panels reading its numbers, a cutaway of the working part, and a self-running tour that can be recorded as a 60 fps video.
Install: `npx skills add elvarofficial/teardown -g -a claude-code`, then `npm install && npx playwright install chromium` in the installed folder (Node 20+, ffmpeg for video, Python 3 for sound).

Rules from its SKILL.md that were applied to the FloodSafe animation:
- Start from a real reference; real numbers only. Every gauge reads the same function that poses the parts (here W.kin(lv): one water level drives model, gauge float and panel bars).
- One input drives everything; nothing keyframed by hand. render(t) pure; frame 0 already shows the machine.
- The working part opens up: cutaway / isolate / close-ups beat orbits.
- Light studio background, ONE accent colour for the part currently working; labels never cover the part they name; nothing within 60 px of an edge.
- Machine fills 60–70% of the viewport; labels ≥34 px at 1080 p; key readout legible at phone width.
- Easing: entrances cubic-bezier(0.16,1,0.3,1); exits half as long; holds 1 s + 0.25 s per word beyond three; something always moves.
- Sound accents events, continuous motion stays silent, one tonal key.

Note: the actual Teardown skill makes three.js pages in Claude Code. The FloodSafe film is NOT made with it: it is a Claude "Motion" artifact
(SVG/CSS scenes driven by time) built in the same visual language (console window, turntable cutaway, live gauges, close-ups).
If you want a real Teardown build, install the skill in Claude Code and ask it for "a simulator of a flood-safe pit latrine upgrade I can take apart",
giving it source/FloodSafe_Sanitation_Draft_v2.docx and the Gambella data folder as the reference.

Sources: https://github.com/elvarofficial/teardown · https://thakicloud.com/tech-blog/en/tutorials/teardown-3d-skill/
