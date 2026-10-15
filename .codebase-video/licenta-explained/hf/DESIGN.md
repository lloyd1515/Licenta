# Overlay scenes: design + contract

These HyperFrames scenes are rendered SILENT and laid over a codebase-video render at exact times. The voice already exists; your animation must land on the spoken words, using the sentence times in `cues.json` (seconds, relative to the scene start; key = scene id).

## Frame contract (HyperFrames)
- One file per scene: `compositions/frames/<scene-id>.html` (e.g. `a1-pond.html`), a `<template>` like `REFERENCE-frame.html` (copy its structure: `<template>`, `<style>`, `#root` div with `data-composition-id="<scene-id>"`, `data-start="0"`, `data-duration="<dur from cues.json>"`, width 1920, height 1080; a GSAP timeline `gsap.timeline({ paused: true })` registered as `window.__timelines["<scene-id>"]`, padded with `tl.to({}, { duration: <dur> }, 0)`).
- Every timed element: `class="clip"`, `data-start`, `data-duration`, unique `data-track-index` within the file.
- Element ids and classes: prefix with the scene id letters, starting with a LETTER (e.g. `p1-`, never `01-`).
- Deterministic only: no Math.random (use a seeded LCG if needed), no Date, no network. GSAP is loaded by the index; do not add other libraries. Inline SVG is encouraged for drawings (waves, figures, arrows, charts).
- Read `/home/vlads4r4/.claude/skills/hyperframes-core/SKILL.md` (composition contract) before writing. Optional for motion ideas: `/home/vlads4r4/.claude/skills/hyperframes-animation/SKILL.md`.

## Look (must match the codebase-video frames it sits between)
- Full-bleed background `#0f1420` (a full-frame `.clip` ground div, opaque, the whole duration).
- Cards `#182133`, border `#2a3448`, radius 16px.
- Text `#eef1f7`; secondary `#a9b3c6`; faint `#5d6a82`.
- Accent blue `#8ab8ff` (the main highlight), cyan `#7fd6e6`, violet `#c3b1f2` (radio boards / hardware), green `#8fd6a8` (good), red `#ff8f87` (fall / alarm / bad only), amber `#f5c16c` (caution), pink `#f2a7cf`.
- Font: `Inter` (400/700) for all text, `JetBrains Mono` for code/numbers. Use `@font-face` with `url("../../assets/fonts/Inter-400.woff2")` etc. like the reference does.
- Text ≥ 44px (headline 72-110px). At most ~12 words on screen at once. Safe area x 80-1840, y 80-1000.
- Keep the top-left corner clear-ish: nothing important in x<700, y<90.

## Motion rules (YouTube explainer feel)
- Something visibly changes at least every 3-4 s. Nothing pops: ease in/out 0.4-0.8 s.
- Each visual beat starts on the sentence that says it (use the cue start, + up to 0.3 s).
- Show, don't caption: a drawing that moves beats text. A short label (1-4 words) may name what the drawing shows.
- The scene's LAST 0.4 s: hold (no exit animation); the next scene cuts in.
- Scene-specific numbers must match exactly what is spoken. Do not invent other numbers.

## Verify before reporting
Run from the project folder `/home/vlads4r4/dev/Licenta/.codebase-video/hf/videos/licenta-remake-overlays`:
`npx --yes hyperframes@0.8.158 lint` must show no errors for your files. Then snapshot your frames at 3 times each, e.g.
`npx --yes hyperframes@0.8.158 snapshot --help` to learn the flags (snapshot a single composition file if supported; otherwise ask the lead in your report). Look at the images and fix overlaps, clipping, empty stages.
