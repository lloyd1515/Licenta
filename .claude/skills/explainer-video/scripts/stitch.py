"""Lay the silent HyperFrames render over the codebase-video render at each overlay scene's start.

usage: python3 stitch.py <video-dir> <out.mp4>

Reads <video-dir>/cv/out/<name>.mp4 (voice + code scenes), <video-dir>/hf/renders/overlays.mp4,
<video-dir>/hf/cues.json and offsets.json, and <video-dir>/cv/build/timing.json.
Each overlay scene is cut into its own clip and fed as a separate input shifted with
-itsoffset, so ffmpeg never buffers the whole overlay stream (reusing one input
eleven times got the process OOM-killed).
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def cut(hf_mp4, start, dur, dest):
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-ss", f"{start:.3f}", "-i", str(hf_mp4), "-t", f"{dur:.3f}",
         "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-pix_fmt", "yuv420p", str(dest)],
        check=True,
    )


def main(video_dir, out_mp4):
    name = json.loads((video_dir / "cv/script.json").read_text())["name"]
    cv_mp4 = video_dir / f"cv/out/{name}.mp4"
    hf_mp4 = video_dir / "hf/renders/overlays.mp4"
    cues = json.loads((video_dir / "hf/cues.json").read_text())
    offsets = json.loads((video_dir / "hf/offsets.json").read_text())
    starts = {s["id"]: s["start"] for s in json.loads((video_dir / "cv/build/timing.json").read_text())["scenes"]}

    with tempfile.TemporaryDirectory() as tmp:
        inputs, chains, base = ["-i", str(cv_mp4)], [], "[0:v]"
        for i, scene in enumerate(cues, start=1):
            clip = Path(tmp) / f"{scene}.mp4"
            cut(hf_mp4, offsets[scene], cues[scene]["dur"], clip)
            inputs += ["-itsoffset", f"{starts[scene]:.3f}", "-i", str(clip)]
            chains.append(f"{base}[{i}:v]overlay=eof_action=pass[v{i}]")
            base = f"[v{i}]"

        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(chains),
             "-map", base, "-map", "0:a", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
             "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", str(out_mp4)],
            check=True,
        )
    print(out_mp4)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())
