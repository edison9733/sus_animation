# Agent skills

| Skill | Source | Licence | Used in | How |
|---|---|---|---|---|
| Anatomy | github.com/wheresryan22/anatomy | MIT (see `anatomy/LICENSE`) | v3.1, scene 7 | A copy is in `anatomy/`. To install it for Claude Code, copy it to `~/.claude/skills/anatomy`. `animation/anatomy-scene7/build.mjs` imports the kit from this folder |
| Teardown | elvarofficial/teardown | — | v2, v3 (style reference only) | Not copied here. Notes are in `context/research/teardown_skill_notes.md` |
| Motion | Claude app animation artifact | — | v1, v2, v3 | Built into the Claude app, so there is nothing to copy. The film's source snapshot is in `animation/motion-v3/` |

The Anatomy copy here is taken from `main` of wheresryan22/anatomy as of 19 Nov 2026. The large example HTML and PDF outputs are left out: rebuild them with `node examples/<name>/build.mjs`.
