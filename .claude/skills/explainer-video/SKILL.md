---
name: explainer-video
description: Make a newcomer-friendly YouTube-style explainer video of this repository (real-life analogies + code walked line by line, fast voice, no silent gaps) and publish it in the README as a click-to-watch thumbnail. Use when the user asks for a new or updated explainer/walkthrough video of the codebase.
---

# Explainer video playbook

Pattern proven on `media/licenta-explained.mp4` (11:55). One voice track and the code scenes come from
**codebase-video**; the analogy / hook scenes come from **HyperFrames**, rendered silent to the exact scene
times and laid over the codebase-video render by `scripts/stitch.py`.

## Rules (from the user)
- Audience: a total newcomer. Every concept gets an everyday picture BEFORE its real name. At most one new term per ~20 s.
- Code: real code, one line lit at a time, a plain-words note per variable, a small picture that changes as the line runs.
- Pacing: voice speed 1.05 (~165 wpm), no `[pause]`/`[rest]`/`[think]`, `lead`/`pad` ≤ 0.3 s, no `inside` zooms. Target < 1% silence.
- At most 2 spoken numbers per scene, rounded ("about 3 seconds"). Exact values only on screen.
- Subagents: **haiku, effort medium, only**. Write the narration yourself; delegate building and auditing.
- README stays tiny: title, one line, the thumbnail, how to run. The point is that people watch the video.

## Layout
```
.codebase-video/<video>/          (gitignored build workspace)
  STORYBOARD.md                   the plan the user approved
  cv/                             codebase-video workspace (script.json, <key>.js modules, build/, out/)
  hf/                             HyperFrames overlay project (compositions/frames/<scene>.html, renders/)
media/<video>.mp4 + <video>.jpg   what gets pushed; README links them
```
Scripts: `S=.claude/skills/explainer-video/scripts`. Templates: `.claude/skills/explainer-video/templates`.
Engine env for every `CV` call:
```bash
export CODEBASE_VIDEO_HOME=~/.local/share/codebase-video CLAUDE_PLUGIN_ROOT=$PWD/.agents/skills/codebase-video WORKERS=1
CV="node $CLAUDE_PLUGIN_ROOT/engine/cli/Cv.js"   # usage: $CV <video-dir>/cv <step>
```
`WORKERS=1` is required here (Chrome times out with parallel pages).

## Steps
1. **Facts.** Reuse a checked teaching document if one exists (`.codebase-video/*/cv/build/lesson.md`); otherwise run
   codebase-video's explore + verify steps (its `SKILL.md`, steps 1-3) with haiku agents. Every narrated claim traces to it.
2. **Storyboard** → `<video-dir>/STORYBOARD.md`, then get the user's OK. Order: cold open (the payoff first, ~15 s) →
   chapter 1 intuition with no code → chapter 2 the core mechanism through the code, each step = analogy scene then
   code scene → chapter 3 how it reaches the user → one-screen recap of all the analogies.
3. **Script** → `cv/script.json` (copy the shape of `.codebase-video/licenta-explained/cv/script.json`): `title` +
   `card`, scene `intro`, bridges `kN-why` with `"chapter"`, analogy scenes `a<N>-<name>`, code scenes
   `c<N>-`/`d<N>-<name>`, `outro`. Then `$CV <cv> new-long`, `$CV <cv> fill`, `$CV <cv> narrate`.
4. **Placeholders**: `python3 $S/overlay.py placeholders <video-dir>`, then `$CV <cv> check` (errors only for code modules not built yet).
5. **Scene plan** → `cv/build/narration-vs-lesson.md`, starting from `templates/scene-plan-head.md`: per code scene the
   exact code lines, which line glows on which phrase, the callouts, the picture. Split code modules between 2 builders.
6. **Overlay project**: `cp -r templates/hf-skeleton <video-dir>/hf` (rename `VIDEO` in meta/package), copy
   `templates/DESIGN.md` there, run `python3 $S/overlay.py setup <video-dir>`, write `hf/SCENES.md` (per analogy scene:
   what to draw on each sentence).
7. **Build in parallel (haiku/medium)**: 2 code builders (`cv/build/brief-builder.txt` + the scene plan, one module set
   each) and 3-4 HyperFrames builders (DESIGN.md + SCENES.md + `hf/cues.json`, 2-3 scenes each, one file per scene).
8. **Look yourself**: `$CV <cv> sheet <key>` images, and stills of `hf` (`npx --yes hyperframes@0.8.158 snapshot`). Send
   concrete fixes back to the builder that owns the scene (things that went wrong last time: a meter that never moved,
   a cursor that passed the key moment early, a key analogy drawn too small, ugly stick figures).
9. **Render**: `$CV <cv> video` (background, ~15 min) and in `hf/`
   `npx --yes hyperframes@0.8.158 render -o renders/overlays.mp4 -f 30 -w 2 --quiet`.
   Re-run `$CV <cv> video` after any module edit made during a render (it redraws only changed scenes).
10. **Stitch + publish**:
    ```bash
    python3 $S/stitch.py <video-dir> media/<video>.mp4
    python3 $S/poster.py media/<video>.mp4 <seconds-of-best-frame> "" media/<video>.jpg   # "" = no title band
    ```
    Check: duration, `ffmpeg -af silencedetect=noise=-35dB:d=1.2` (expect ~0 gaps), a contact sheet of stills.
    README block: `[![Watch the explainer video](media/<video>.jpg)](media/<video>.mp4)` + one line under it.
    Videos over ~95 MB do not fit in git: attach them to a GitHub release and link that instead.

## Updating one scene later
Narration change: edit `cv/script.json` → `$CV <cv> narrate` → `python3 $S/overlay.py setup <video-dir>` (times moved) →
fix affected modules/frames → render both → stitch. Picture-only change: edit the module or frame → render that side → stitch.
