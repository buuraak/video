"""Render a scene to a video.

    .venv/bin/python render.py scenes/demo.py
    .venv/bin/python render.py scenes/demo.py --start 2 --end 5 --out films/test.mp4

Frames are drawn in parallel (one helper per processor core) and streamed
straight into ffmpeg, so no image files pile up. If the scene has a
soundtrack (or an AUDIO file), it goes under the picture. Any problems (like
a hand that can't reach) are listed at the end.
"""
import argparse
import os
import subprocess
import sys
import time
from multiprocessing import Pool
from pathlib import Path

from toolkit import FPS, H, W, report
from toolkit.scene import build_audio, frame_count, load, render_frame

_scene = None


def _start_helper(path):
    global _scene
    report.ECHO = False
    _scene = load(path)


def _draw(frame):
    f = render_frame(_scene, frame)
    return frame, f.pixels.tobytes(), report.take()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scene", help="the scene file, e.g. scenes/demo.py")
    ap.add_argument("--out", help="video file to write (default: films/<scene name>.mp4)")
    ap.add_argument("--start", type=float, default=0.0, help="start time in seconds")
    ap.add_argument("--end", type=float, help="end time in seconds (default: the whole scene)")
    ap.add_argument("--workers", type=int, default=os.cpu_count(), help="how many frames to draw at once")
    ap.add_argument("--no-audio", action="store_true", help="leave the soundtrack out")
    args = ap.parse_args()

    scene = load(args.scene)
    first = int(round(args.start * FPS))
    last = min(frame_count(scene), int(round(args.end * FPS)) if args.end is not None else frame_count(scene))
    frames = range(first, last)
    out = Path(args.out or Path("films") / f"{Path(args.scene).stem}.mp4")
    out.parent.mkdir(parents=True, exist_ok=True)

    audio = None if args.no_audio else build_audio(scene)

    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
    if audio:
        cmd += ["-ss", f"{first / FPS:.3f}", "-i", str(audio), "-map", "0:v", "-map", "1:a",
                "-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-tune", "grain", "-crf", "18",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)]

    print(f"Rendering {len(frames)} frames ({len(frames) / FPS:.1f}s) of {args.scene} "
          f"with {args.workers} helpers -> {out}")
    ffmpeg = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    problems = []
    began = time.perf_counter()
    with Pool(args.workers, initializer=_start_helper, initargs=(str(Path(args.scene).resolve()),)) as pool:
        for i, (frame, data, found) in enumerate(pool.imap(_draw, frames, chunksize=2), 1):
            ffmpeg.stdin.write(data)
            problems += found
            if i % FPS == 0 or i == len(frames):
                speed = i / (time.perf_counter() - began)
                print(f"  {i}/{len(frames)} frames  ({speed:.1f} frames per second)", flush=True)
    ffmpeg.stdin.close()
    if ffmpeg.wait() != 0:
        sys.exit("ffmpeg failed: the video was not written")

    print(f"Done in {time.perf_counter() - began:.1f}s: {out}")
    if problems:
        print(f"\n{len(problems)} problem(s) found while drawing:")
        for p in problems[:40]:
            print("  - " + p)
        if len(problems) > 40:
            print(f"  ...and {len(problems) - 40} more")


if __name__ == "__main__":
    main()
