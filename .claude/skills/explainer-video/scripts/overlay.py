"""Glue between the codebase-video workspace (cv/) and the HyperFrames overlay project (hf/).

usage:
  python3 overlay.py placeholders <video-dir>   write a placeholder <key>.js for every overlay module
  python3 overlay.py setup <video-dir>          write hf/cues.json, hf/offsets.json and hf/index.html
                                                from cv/build/timing.json (run after `CV narrate`)

Overlay scenes are the ones whose module key is `intro`, `outro`, or starts with `a`
followed by a digit (a1-pond, a2-eq, ...). Their picture comes from HyperFrames;
every other scene is drawn by codebase-video.
"""
import json
import re
import sys
from pathlib import Path

FONTS = [("Inter", "Inter"), ("JetBrains Mono", "JetBrainsMono")]


def is_overlay(scene_id):
    key = scene_id.split("-")[0]
    return key in ("intro", "outro") or re.fullmatch(r"a\d+", key) is not None


def overlay_scenes(video_dir):
    timing = json.loads((video_dir / "cv/build/timing.json").read_text())
    return [s for s in timing["scenes"] if is_overlay(s["id"])]


def first_words(scene, count=3):
    """The scene's opening words exactly as spoken (hyphens kept), stopping at the first punctuation."""
    words = []
    for token in scene["sentences"][0]["spoken"].split()[:count]:
        words.append(token.rstrip(",.;:!?"))
        if token != words[-1]:
            break
    return " ".join(words)


def placeholders(video_dir):
    by_key = {}
    for scene in overlay_scenes(video_dir):
        by_key.setdefault(scene["id"].split("-")[0], []).append(scene)
    for key, scenes in by_key.items():
        body = "\n".join(
            f'  K.scene("{s["id"]}", () => {{\n'
            f'    K.heading("{s["id"]}", {{ at: "{s["id"]}|{first_words(s)}" }});\n'
            f"  }});"
            for s in scenes
        )
        (video_dir / f"cv/{key}.js").write_text(
            f"// {key}: placeholder stage; a HyperFrames clip is laid over these scenes by stitch.py.\n"
            f'Kit.module("{key}", (K) => {{\n{body}\n}});\n'
        )
        print(f"cv/{key}.js")


def setup(video_dir):
    hf = video_dir / "hf"
    cues, offsets, rows, offset = {}, {}, [], 0.0
    for i, scene in enumerate(overlay_scenes(video_dir)):
        sid, start = scene["id"], scene["start"]
        dur = round(scene["end"] - start, 3)
        cues[sid] = {
            "start": start,
            "dur": dur,
            "sentences": [
                (round(x["start"] - start, 2), round(x["end"] - start, 2), x["text"]) for x in scene["sentences"]
            ],
        }
        offsets[sid] = round(offset, 3)
        rows.append(
            f'      <div id="el-{sid}" class="scene" data-composition-id="{sid}" '
            f'data-composition-src="compositions/frames/{sid}.html" data-start="{offset:.3f}" '
            f'data-duration="{dur}" data-track-index="{i}"></div>'
        )
        offset += dur

    fonts = "".join(
        f'      @font-face {{ font-family: "{family}"; src: url("assets/fonts/{file}-{weight}.woff2") '
        f'format("woff2"); font-weight: {weight}; font-display: block; }}\n'
        for family, file in FONTS
        for weight in (400, 700)
    )
    total = f"{offset:.3f}"
    rows_html = "\n".join(rows)
    (hf / "index.html").write_text(f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js" integrity="sha384-sG0Hv1tP1lZCk9KQmrIbY/XNwi+OY84GQqhMscbnsoBFqAz8KNCil1kvfL3Hbbk2" crossorigin="anonymous"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: #0f1420; }}
      #root {{ position: relative; width: 1920px; height: 1080px; overflow: hidden; background: #0f1420; }}
      .scene {{ position: absolute; inset: 0; width: 100%; height: 100%; }}
{fonts}    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total}" data-width="1920" data-height="1080">
{rows_html}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
      window.__timelines["main"].to({{}}, {{ duration: {total} }}, 0);
    </script>
  </body>
</html>
""")
    (hf / "cues.json").write_text(json.dumps(cues, indent=1))
    (hf / "offsets.json").write_text(json.dumps(offsets, indent=1))
    print(f"{len(cues)} overlay scenes, {total} s -> hf/index.html, hf/cues.json, hf/offsets.json")


if __name__ == "__main__":
    commands = {"placeholders": placeholders, "setup": setup}
    if len(sys.argv) != 3 or sys.argv[1] not in commands:
        sys.exit(__doc__)
    commands[sys.argv[1]](Path(sys.argv[2]).resolve())
