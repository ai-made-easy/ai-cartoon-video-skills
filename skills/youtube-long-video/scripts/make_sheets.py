#!/usr/bin/env python3
"""make_sheets.py: one frame every 3 seconds, tiled into contact sheets of 30 frames (6 x 5) with time labels.

  python3 make_sheets.py --video reference.mp4 --out sheets/ref [--start 0] [--end 900] [--every 3]

Writes sheets/ref/frames/0001.jpg ... and sheets/ref/sheet-00.jpg, sheet-01.jpg ... (each sheet = 90 s at the default
3 s step; every tile has its time in the corner, for example 1:27). Open each sheet with your image viewer (Claude
Code can read the JPG files) and tag every tile with one code from references/labels.md.

Needs: python 3.9+, Pillow (pip install pillow), ffmpeg on the PATH.
"""
import argparse
import glob
import os
import shutil
import subprocess
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Pillow is required: pip install pillow   (or: uv run --with pillow python make_sheets.py ...)")

COLS, ROWS, TW, TH = 6, 5, 320, 180


def font(size):
    for name in ("DejaVuSans-Bold.ttf", "Arial Bold.ttf", "Arial.ttf", "Helvetica.ttc"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--video", required=True)
    ap.add_argument("--out", required=True, help="output folder")
    ap.add_argument("--start", type=float, default=0, help="first second (default 0)")
    ap.add_argument("--end", type=float, default=0, help="last second (default: end of the video)")
    ap.add_argument("--every", type=float, default=3.0, help="seconds between frames (default 3)")
    a = ap.parse_args()
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg not found on the PATH")
    fdir = os.path.join(a.out, "frames")
    os.makedirs(fdir, exist_ok=True)
    cmd = ["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", str(a.start)]
    if a.end:
        cmd += ["-t", str(a.end - a.start)]
    # fps=1/N with round=down: frame k shows t = start + N*k
    cmd += ["-i", a.video, "-vf", f"fps=1/{a.every}:round=down,scale={TW * 2}:-2", "-q:v", "6", os.path.join(fdir, "%04d.jpg")]
    subprocess.run(cmd, check=True)
    files = sorted(glob.glob(os.path.join(fdir, "*.jpg")))
    f = font(18)
    per = COLS * ROWS
    for g in range(0, len(files), per):
        img = Image.new("RGB", (COLS * TW, ROWS * TH), "white")
        d = ImageDraw.Draw(img)
        for k, p in enumerate(files[g:g + per]):
            t = int(a.start + a.every * (g + k))
            x, y = (k % COLS) * TW, (k // COLS) * TH
            img.paste(Image.open(p).convert("RGB").resize((TW, TH)), (x, y))
            s = f"{t // 60}:{t % 60:02d}"
            bb = d.textbbox((x + 4, y + TH - 28), s, font=f)
            d.rectangle((bb[0] - 3, bb[1] - 2, bb[2] + 3, bb[3] + 2), fill="black")
            d.text((x + 4, y + TH - 28), s, fill="yellow", font=f)
            d.rectangle((x, y, x + TW - 1, y + TH - 1), outline="white")
        out = os.path.join(a.out, f"sheet-{g // per:02d}.jpg")
        img.save(out, quality=78)
    n = (len(files) + per - 1) // per
    print(f"{len(files)} frames, {n} sheets in {a.out}")


if __name__ == "__main__":
    main()
