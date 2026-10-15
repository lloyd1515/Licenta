"""README thumbnail: a frame of the video, darkened, with the title, a play button and the length.

usage: python3 poster.py <video.mp4> <seconds> "<title or empty>" <out.jpg>

An empty title leaves the frame's own top uncovered (use it when the frame carries the hook).
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT_DIRS = [Path.home() / ".local/share/fonts", Path("/usr/share/fonts")]
WIDTH = 1280


def font(size, bold=False):
    names = ["Inter-Bold.ttf", "Inter-SemiBold.ttf"] if bold else ["Inter-Medium.ttf", "Inter-Regular.ttf"]
    for name in names + ["DejaVuSans-Bold.ttf", "DejaVuSans.ttf"]:
        for root in FONT_DIRS:
            found = next(root.rglob(name), None)
            if found:
                return ImageFont.truetype(str(found), size)
    return ImageFont.load_default(size)


def duration_label(video):
    seconds = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
        capture_output=True, text=True, check=True,
    ).stdout)
    return f"{int(seconds // 60)}:{int(seconds % 60):02d}"


def main(video, at, title, out):
    with tempfile.TemporaryDirectory() as tmp:
        frame = Path(tmp) / "frame.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", at, "-i", str(video), "-frames:v", "1", str(frame)], check=True)
        image = Image.open(frame).convert("RGB")
    image = image.resize((WIDTH, round(image.height * WIDTH / image.width)))
    w, h = image.size
    image = Image.blend(image, Image.new("RGB", image.size, (8, 11, 18)), 0.45)
    draw = ImageDraw.Draw(image)

    cx, cy, r = w // 2, h // 2, 78
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 255))
    draw.polygon([(cx - 24, cy - 38), (cx - 24, cy + 38), (cx + 42, cy)], fill=(15, 20, 32))

    if title:
        draw.rectangle((0, 0, w, 150), fill=(15, 20, 32))
        draw.text((w // 2, 75), title, font=font(64, bold=True), fill=(238, 241, 247), anchor="mm")
    label = f"▶ Watch · {duration_label(video)}"
    draw.rounded_rectangle((w // 2 - 150, h - 120, w // 2 + 150, h - 56), radius=32, fill=(138, 184, 255))
    draw.text((w // 2, h - 88), label, font=font(34, bold=True), fill=(15, 20, 32), anchor="mm")
    image.save(out, quality=90)
    print(out)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    main(Path(sys.argv[1]), sys.argv[2], sys.argv[3], Path(sys.argv[4]))
