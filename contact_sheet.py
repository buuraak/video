"""Put 12 frames from any stretch of a scene (or a finished video) into one picture.

    .venv/bin/python contact_sheet.py scenes/demo.py
    .venv/bin/python contact_sheet.py scenes/demo.py --start 2 --end 4
    .venv/bin/python contact_sheet.py films/demo.mp4 --start 0 --end 6

The 12 frames are spread evenly from start to end. Each one is labelled with
its time and frame number. Saved to sheets/ unless you give --out.
"""
import argparse
import os
import subprocess
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import skia

from toolkit import FPS, GREY, H, INK, W, report, to_color
from toolkit.frame import Frame
from toolkit.scene import frame_count, load, render_frame

COLS, ROWS = 4, 3
GAP = 16
THUMB_W = (W - GAP * (COLS + 1)) // COLS
THUMB_H = THUMB_W * H // W
LABEL_H = 40
HEADER = 70

_scene = None


def _start_helper(path):
    global _scene
    report.ECHO = False
    _scene = load(path)


def _draw(frame):
    return render_frame(_scene, frame).pixels, report.take()


def _video_frames(path, frames):
    """Pull exact frames (by number) out of a video in one pass."""
    wanted = sorted(set(frames))
    pick = "+".join(f"eq(n,{f})" for f in wanted)
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(path), "-vf", f"select='{pick}'",
                          "-fps_mode", "passthrough", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-"],
                         capture_output=True, check=True).stdout
    size = W * H * 4
    if len(raw) != size * len(wanted):
        raise SystemExit(f"Could only read {len(raw) // size} of {len(wanted)} frames from {path}")
    got = {f: np.frombuffer(raw[i * size:(i + 1) * size], dtype=np.uint8).reshape(H, W, 4)
           for i, f in enumerate(wanted)}
    return [got[f] for f in frames]


def _video_length(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", str(path)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def _text(canvas, text, x, y, size, color):
    f = skia.Font(skia.FontMgr().matchFamilyStyle("Helvetica Neue", skia.FontStyle.Normal()), size)
    canvas.drawString(text, x, y, f, skia.Paint(AntiAlias=True, Color=to_color(color)))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", help="a scene file (scenes/x.py) or a video (films/x.mp4)")
    ap.add_argument("--start", type=float, default=0.0, help="start time in seconds")
    ap.add_argument("--end", type=float, help="end time in seconds (default: the end)")
    ap.add_argument("--out", help="picture to write (default: sheets/<name>_<start>-<end>.png)")
    args = ap.parse_args()

    src = Path(args.source)
    is_video = src.suffix.lower() in (".mp4", ".mov", ".mkv", ".webm")
    total = _video_length(src) if is_video else load(src).DURATION
    end = min(args.end if args.end is not None else total, total)
    last_frame = max(int(round(end * FPS)) - 1, int(round(args.start * FPS)))
    frames = [int(round(x)) for x in np.linspace(args.start * FPS, last_frame, COLS * ROWS)]
    limit = int(round(total * FPS)) if is_video else frame_count(load(src))
    frames = [min(f, limit - 1) for f in frames]

    problems = []
    if is_video:
        images = _video_frames(src, frames)
    else:
        with Pool(min(os.cpu_count(), len(frames)), initializer=_start_helper,
                  initargs=(str(src.resolve()),)) as pool:
            results = pool.map(_draw, frames)
        images = [r[0] for r in results]
        problems = [p for r in results for p in r[1]]

    sheet = Frame(W, HEADER + ROWS * (THUMB_H + LABEL_H) + (ROWS + 1) * GAP - GAP // 2, background=(8, 8, 10))
    c = sheet.canvas
    _text(c, f"{src.name}   {args.start:.2f}s to {end:.2f}s", GAP, 46, 30, INK)
    for i, (frame, pixels) in enumerate(zip(frames, images)):
        x = GAP + (i % COLS) * (THUMB_W + GAP)
        y = HEADER + (i // COLS) * (THUMB_H + LABEL_H + GAP)
        img = skia.Image.fromarray(np.ascontiguousarray(pixels), colorType=skia.kRGBA_8888_ColorType)
        c.drawImageRect(img, skia.Rect.MakeXYWH(x, y, THUMB_W, THUMB_H),
                        skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear))
        _text(c, f"{frame / FPS:6.2f}s   frame {frame}", x + 4, y + THUMB_H + 28, 22, GREY)

    out = Path(args.out or Path("sheets") / f"{src.stem}_{args.start:g}-{end:g}.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    print(f"Saved {out}")
    if problems:
        print(f"{len(problems)} problem(s) found while drawing:")
        for p in problems:
            print("  - " + p)


if __name__ == "__main__":
    main()
