# Local changes to the tool submodules

- `diagram-tour.patch`: edits to diagram-tour (apply with `git -C .agents/skills/diagram-tour apply ../../local-changes/diagram-tour.patch`).
- `diagram-tour-bin-dot`: the `bin/dot` shim added next to it.
- `codebase-video-SKILL.md`: the `SKILL.md` used at the root of the codebase-video clone.

Downloaded data (`.data/`, `.local/`) and tool state (`.omc/`) are not included; the tools fetch them again.
