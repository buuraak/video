"""Automatic checks for the toolkit. Run after any change:

    .venv/bin/python checks.py

Each check prints PASS or FAIL. Everything should PASS.
"""
import hashlib
import subprocess
import sys
import traceback
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parent
PY = sys.executable
CHECKS = []


def check(fn):
    CHECKS.append(fn)
    return fn


def frame_hash(pixels):
    return hashlib.sha256(np.ascontiguousarray(pixels).tobytes()).hexdigest()


def hash_in_fresh_process(code):
    """Run drawing code in a brand-new Python and return the picture's fingerprint."""
    script = (
        "import hashlib, numpy as np\n"
        "from toolkit import *\n"
        f"{code}\n"
        "print(hashlib.sha256(np.ascontiguousarray(f.pixels).tobytes()).hexdigest())\n"
    )
    out = subprocess.run([PY, "-c", script], cwd=ROOT, capture_output=True, text=True, check=True)
    return out.stdout.strip().splitlines()[-1]


# -- 1. hand-drawn lines ---------------------------------------------------

LINES_CODE = (
    "from previews import doodle\n"
    "f = Frame()\n"
    "doodle(f.canvas, {frame})"
)


@check
def lines_hold_for_three_frames():
    from toolkit import Frame
    from previews import doodle
    hashes = []
    for frame in range(6):
        f = Frame()
        doodle(f.canvas, frame)
        hashes.append(frame_hash(f.pixels))
    assert hashes[0] == hashes[1] == hashes[2], "frames 0-2 should look identical"
    assert hashes[3] == hashes[4] == hashes[5], "frames 3-5 should look identical"
    assert hashes[0] != hashes[3], "frame 3 should be a fresh drawing"


@check
def lines_same_in_every_run():
    a = hash_in_fresh_process(LINES_CODE.format(frame=7))
    b = hash_in_fresh_process(LINES_CODE.format(frame=7))
    assert a == b, "the same frame drew differently in two separate runs"


# -- 2. the character ------------------------------------------------------

@check
def hands_and_feet_land_exactly_on_reachable_targets():
    import math
    from toolkit import Character, report
    from toolkit.rng import rng
    hero = Character("hero")
    g = rng("check", "reach")
    for _ in range(300):
        pose = hero.stand(960, 860)
        j = hero.skeleton(pose)
        a, b = hero.arm
        ang, dist = g.uniform(0, 2 * math.pi), g.uniform(abs(a - b) + 1, a + b - 0.01)
        target = (j["shoulder"][0] + dist * math.cos(ang), j["shoulder"][1] + dist * math.sin(ang))
        j = hero.skeleton(pose.but(hand_r=target))
        assert math.dist(j["hand_r"], target) < 1e-6, f"hand missed {target}"
        assert abs(math.dist(j["shoulder"], j["elbow_r"]) - a) < 1e-6, "upper arm changed length"
        assert abs(math.dist(j["elbow_r"], j["hand_r"]) - b) < 1e-6, "forearm changed length"
    assert report.take() == [], "a reachable target was reported as unreachable"


@check
def standing_feet_stay_on_the_floor_when_the_hips_move():
    from toolkit import Character, report
    report.take()
    hero = Character("hero")
    base = hero.stand(960, 820)
    for dy in (-8, -4, 0, 4, 8, 20):
        j = hero.skeleton(base.but(y=base.y + dy))
        assert j["foot_l"][1] == 820 and j["foot_r"][1] == 820, f"feet left the floor when the hips moved {dy}px"
    assert report.take() == [], "small hip movements should never put the floor out of reach"


@check
def floor_line_top_edge_never_drifts():
    from toolkit import Frame, Ink
    for frame in range(0, 30, 3):
        f = Frame()
        Ink(f.canvas, frame).floor(600)
        lit = f.pixels[:, 100:1820, 0] > 120          # where the line is drawn
        tops = lit.argmax(axis=0)
        assert tops.min() >= 599 and tops.max() <= 601, f"floor edge drifted to {tops.min()}..{tops.max()} on frame {frame}"


@check
def unreachable_targets_are_reported():
    from toolkit import Character, report
    report.ECHO = False
    report.take()
    hero = Character("hero")
    hero.skeleton(hero.stand(960, 860, foot_l=(400, 860), hand_r=(1000, 500)), frame=42)
    problems = report.take()
    report.ECHO = True
    assert len(problems) == 1, f"expected one report, got {problems}"
    assert "frame 42" in problems[0] and "left foot" in problems[0], problems[0]


# -- 3. faces and the enemy ------------------------------------------------

ENEMY_CODE = (
    "enemy = Character('enemy', height=640, color=RED, glow=True, glitch=True)\n"
    "f = Frame()\n"
    "for fr in range(60):\n"
    "    if enemy.is_glitching(fr): break\n"
    "enemy.draw(f.canvas, fr, enemy.stand(960, 900, face=faces.EVIL))"
)


@check
def enemy_glitch_and_glow_same_in_every_run():
    a = hash_in_fresh_process(ENEMY_CODE)
    b = hash_in_fresh_process(ENEMY_CODE)
    assert a == b, "the glitching enemy drew differently in two separate runs"


@check
def blinks_are_short_and_regular():
    from toolkit import blink
    values = [blink(fr / 30) for fr in range(30 * 20)]
    closed = sum(v < 0.2 for v in values)
    assert 3 <= sum(1 for i in range(1, len(values)) if values[i] < 0.2 <= values[i - 1]) <= 8, \
        "expected a blink every few seconds"
    assert closed < len(values) * 0.05, "eyes are closed too often"
    assert values == [blink(fr / 30) for fr in range(30 * 20)], "blinks changed between calls"


# -- 4. the film finish ----------------------------------------------------

FINISH_CODE = "f = Frame()\nfinish(f, {frame})"


@check
def grain_moves_every_frame_but_never_between_runs():
    a = hash_in_fresh_process(FINISH_CODE.format(frame=10))
    b = hash_in_fresh_process(FINISH_CODE.format(frame=10))
    c = hash_in_fresh_process(FINISH_CODE.format(frame=11))
    assert a == b, "the same frame's grain differed between runs"
    assert a != c, "grain should change from one frame to the next"


@check
def bars_are_black():
    from toolkit import BAR, Frame, finish
    f = Frame()
    finish(f, 0)
    assert f.pixels[:BAR, :, :3].max() == 0 and f.pixels[-BAR:, :, :3].max() == 0, "bars aren't pure black"


# -- 5. captions and camera ------------------------------------------------

@check
def camera_at_rest_shows_the_screen_exactly():
    import math
    from toolkit import Camera
    cam = Camera(handheld=0)
    for p in ((0, 0), (960, 540), (1920, 1080), (300, 900)):
        assert math.dist(cam.to_screen(p, 1.0), p) < 1e-9, "a still camera should not move anything"


@check
def camera_shake_is_stable_and_stronger_on_a_jolt():
    import math
    from toolkit import Camera
    cam = Camera().shake(at=2.0, strength=1.0)
    calm = max(math.dist(cam.state(t / 30)[:2], (960, 540)) for t in range(0, 55))
    jolt = max(math.dist(cam.state(2.0 + t / 30)[:2], (960, 540)) for t in range(1, 10))
    assert calm < 20, f"handheld drift too big: {calm:.1f}px"
    assert jolt > calm, "a jolt should shake harder than the handheld drift"
    assert [Camera().state(t / 30) for t in range(90)] == [Camera().state(t / 30) for t in range(90)]


@check
def long_captions_wrap_and_red_words_are_found():
    from toolkit.text import CAPTION_WIDTH, _words, font, wrap
    lines = wrap("This is a much longer caption that will not fit on one single line of the screen "
                 "no matter how hard it tries", font())
    f = font()
    assert len(lines) >= 2, "long caption should wrap"
    for line in lines:
        width = sum(f.measureText(w) for w, _ in line) + f.measureText(" ") * (len(line) - 1)
        assert width <= CAPTION_WIDTH, "a caption line is too wide"
    assert _words("He *failed* again.") == [("He", False), ("failed", True), ("again.", False)]


# -- 6. render and contact sheet --------------------------------------------

@check
def parallel_helpers_draw_identical_frames():
    from multiprocessing import Pool
    import render
    from toolkit.scene import load, render_frame
    path = str(ROOT / "scenes" / "demo.py")
    frames = [0, 100, 122]
    with Pool(3, initializer=render._start_helper, initargs=(path,)) as pool:
        drawn = pool.map(render._draw, frames)
    scene = load(path)
    for frame, data, _ in drawn:
        assert data == render_frame(scene, frame).pixels.tobytes(), f"frame {frame} differed"


# -- 7. the sound kit -------------------------------------------------------

SOUND_CODE = (
    "import hashlib\n"
    "from previews import sound_tour\n"
    "h = hashlib.sha256()\n"
    "for name, s, _ in sound_tour(): h.update(np.ascontiguousarray(s).tobytes())\n"
    "print(h.hexdigest())\n"
    "raise SystemExit"
)


@check
def sounds_are_identical_in_every_run():
    def run():
        out = subprocess.run([PY, "-c", "import numpy as np\n" + SOUND_CODE], cwd=ROOT,
                             capture_output=True, text=True, check=True)
        return out.stdout.strip()
    assert run() == run(), "a sound came out differently in two separate runs"


@check
def mix_saves_a_clean_stereo_wav():
    import tempfile
    from scipy.io import wavfile
    from toolkit import sound as sk
    mix = sk.Mix(3.0)
    mix.add(sk.thud(), at=0.5, reverb=0.3)
    mix.add(sk.piano("A4"), at=1.0, pan=-0.5)
    with tempfile.TemporaryDirectory() as d:
        rate, data = wavfile.read(mix.save(Path(d) / "t.wav"))
    assert rate == 48000 and data.shape == (144000, 2), f"unexpected WAV: {rate} Hz, {data.shape}"
    peak = np.abs(data).max() / 32767
    assert 0.85 < peak < 0.9, f"loudest moment should sit just under full volume, got {peak:.2f}"


@check
def note_names_give_the_right_pitch():
    from toolkit.sound import note_freq
    assert abs(note_freq("A4") - 440) < 1e-9 and abs(note_freq("A3") - 220) < 1e-9
    assert abs(note_freq("C4") - 261.6256) < 1e-3 and abs(note_freq("C#4") - note_freq("Db4")) < 1e-9


if __name__ == "__main__":
    only = sys.argv[1:]
    failed = 0
    for fn in CHECKS:
        if only and not any(o in fn.__name__ for o in only):
            continue
        try:
            fn()
            print(f"PASS  {fn.__name__}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"FAIL  {fn.__name__}: {e}")
            traceback.print_exc()
    print("all checks passed" if not failed else f"{failed} check(s) failed")
    sys.exit(1 if failed else 0)
