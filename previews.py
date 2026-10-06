"""Draws one picture per toolkit piece into previews/.

    .venv/bin/python previews.py lines      # just one piece
    .venv/bin/python previews.py            # all of them
"""
import math
import sys
from pathlib import Path

import numpy as np
import skia

from toolkit import BG, GREY, INK, RED, Frame, Ink, to_color

OUT = Path(__file__).parent / "previews"
OUT.mkdir(exist_ok=True)


def label(canvas, text, x, y, size=30, color=GREY):
    font = skia.Font(skia.FontMgr().matchFamilyStyle("Helvetica Neue", skia.FontStyle.Normal()), size)
    canvas.drawString(text, x, y, font, skia.Paint(AntiAlias=True, Color=to_color(color)))


def divider(canvas):
    p = skia.Paint(Color=to_color((40, 40, 46)), StrokeWidth=2)
    canvas.drawLine(960, 0, 960, 1080, p)
    canvas.drawLine(0, 540, 1920, 540, p)


# -- 1. hand-drawn lines ---------------------------------------------------

def doodle(canvas, frame, color=INK):
    ink = Ink(canvas, frame, color=color)
    ink.line((70, 440), (890, 450), "ground")
    hills = [(x, 330 + 45 * math.sin(x / 95.0) + 20 * math.sin(x / 37.0)) for x in range(90, 560, 10)]
    ink.stroke(hills, "hills")
    ink.circle((730, 190), 80, "sun")
    ink.curve((150, 160), (260, 260), (380, 150), "arc")
    for i, x in enumerate((160, 230, 300)):
        ink.blob((x, 90), 12, 16, f"dot{i}")


def preview_lines():
    f = Frame()
    c = f.canvas
    panels = [(0, 0, 0), (960, 0, 3), (0, 540, 6)]
    for x, y, frame in panels:
        c.save()
        c.translate(x, y)
        doodle(c, frame)
        label(c, f"frames {frame}-{frame + 2}", 30, 510)
        c.restore()
    # bottom right: the three drawings stacked, to show how the lines "boil"
    c.save()
    c.translate(960, 540)
    for frame, col in ((0, (90, 90, 96)), (3, (160, 158, 150)), (6, INK)):
        doodle(c, frame, col)
    label(c, "all three on top of each other", 30, 510)
    c.restore()
    divider(c)
    f.save(OUT / "01_lines.png")


# -- 2. the character ------------------------------------------------------

def crosshair(canvas, p, color=GREY, size=14):
    paint = skia.Paint(AntiAlias=True, Color=to_color(color), StrokeWidth=3)
    canvas.drawLine(p[0] - size, p[1], p[0] + size, p[1], paint)
    canvas.drawLine(p[0], p[1] - size, p[0], p[1] + size, paint)


def preview_character():
    from toolkit import Character, report
    f = Frame()
    c = f.canvas
    ground = 860
    Ink(c, 0, color=GREY).floor(ground)
    hero = Character("hero")
    report.ECHO = False

    poses = [
        ("resting", hero.stand(200, ground), {}),
        ("waving", hero.stand(560, ground), {"hand_r": (650, 470), "hand_l": (470, 640)}),
        ("walking", hero.stand(930, ground, facing=1, lean=6).but(y=ground - 166),
         {"foot_l": (870, ground), "foot_r": (1000, ground - 10), "hand_l": (1000, 700), "hand_r": (860, 690)}),
        ("crouching", hero.stand(1290, ground).but(y=ground - 120),
         {"foot_l": (1230, ground), "foot_r": (1350, ground), "hand_l": (1215, 740), "hand_r": (1370, 740)}),
        ("can't reach", hero.stand(1650, ground), {"hand_r": (1880, 290)}),
    ]
    for title, pose, targets in poses:
        pose = pose.but(**targets)
        joints = hero.draw(c, 0, pose)
        problems = report.take()
        for limb, target in targets.items():
            missed = any(f"({target[0]:.0f}, {target[1]:.0f})" in p for p in problems)
            crosshair(c, target, RED if missed else GREY)
            if missed:
                end = joints[limb]
                paint = skia.Paint(AntiAlias=True, Color=to_color(RED), StrokeWidth=3,
                                   PathEffect=skia.DashPathEffect.Make([10, 8], 0))
                c.drawLine(end[0], end[1], target[0], target[1], paint)
        label(c, title, pose.x - 60, 940)
        for i, p in enumerate(problems):
            label(c, "reported: " + p.split("it is ")[1], pose.x - 120, 980 + 32 * i, 24, RED)
    f.save(OUT / "02_character.png")


# -- 3. faces, and the hero next to the enemy ------------------------------

def preview_faces():
    from toolkit import Face, draw_head, faces
    f = Frame()
    c = f.canvas
    grid = [
        ("eyes open", Face(eyes=1.0), INK), ("half open", Face(eyes=0.5), INK),
        ("closed", Face(eyes=0.0), INK), ("sad brows", Face(brows="sad"), INK),
        ("angry brows", Face(brows="angry"), INK),
        ("smile", Face(mouth="smile"), INK), ("frown", Face(mouth="frown"), INK),
        ("open", Face(mouth="open"), INK), ("hero: tired", faces.TIRED, INK),
        ("enemy: evil grin", faces.EVIL, RED),
    ]
    for i, (title, face, color) in enumerate(grid):
        cx, cy = 192 + (i % 5) * 384, 250 + (i // 5) * 500
        ink = Ink(c, 0, color=color, width=9, prefix=title)
        draw_head(ink, (cx, cy), 130, face)
        label(c, title, cx - 70, cy + 210)
    f.save(OUT / "03_faces.png")


def preview_cast():
    from toolkit import Character, faces
    f = Frame()
    c = f.canvas
    ground = 900
    Ink(c, 0, color=GREY).floor(ground)
    hero = Character("hero")
    enemy = Character("enemy", height=640, color=RED, glow=True, glitch=True)
    hero.draw(c, 0, hero.stand(480, ground, face=faces.TIRED, head_tilt=-8, lean=-3))
    pose = enemy.stand(1000, ground, face=faces.EVIL, facing=-1, lean=-4,
                       hand_l=(860, 650), hand_r=(1060, 680))
    enemy.draw(c, 0, pose)
    label(c, "hero (tired)", 400, 980)
    label(c, "enemy", 950, 980)
    # the same moment, mid-glitch, as an inset on the right
    glitch_frame = next(fr for fr in range(400) if enemy.is_glitching(fr))
    inset = Frame(560, 600)
    ic = inset.canvas
    ic.scale(0.75, 0.75)
    ic.translate(373 - 1000, 400 - 580)
    enemy.draw(ic, glitch_frame, pose)
    c.drawImage(inset.surface.makeImageSnapshot(), 1320, 240)
    border = skia.Paint(AntiAlias=True, Color=to_color(GREY), Style=skia.Paint.kStroke_Style, StrokeWidth=2)
    c.drawRect(skia.Rect.MakeXYWH(1320, 240, 560, 600), border)
    label(c, f"the enemy mid-glitch (frame {glitch_frame})", 1330, 880, 26)
    f.save(OUT / "04_hero_and_enemy.png")


# -- 4. the film finish ---------------------------------------------------

def cast_scene(canvas, frame):
    from toolkit import Character, faces
    ground = 860
    Ink(canvas, frame, color=GREY).floor(ground)
    hero = Character("hero")
    enemy = Character("enemy", height=640, color=RED, glow=True, glitch=True)
    hero.draw(canvas, frame, hero.stand(640, ground, face=faces.TIRED, head_tilt=-8, lean=-3))
    enemy.draw(canvas, frame, enemy.stand(1240, ground, face=faces.EVIL, facing=-1, lean=-4,
                                          hand_l=(1100, 610), hand_r=(1300, 640)))


def preview_finish():
    from toolkit import finish
    before, after = Frame(), Frame()
    cast_scene(before.canvas, 0)
    cast_scene(after.canvas, 0)
    finish(after, 0)
    out = Frame()
    out.pixels[:, :960] = before.pixels[:, :960]
    out.pixels[:, 960:] = after.pixels[:, 960:]
    c = out.canvas
    c.drawLine(960, 0, 960, 1080, skia.Paint(Color=to_color(GREY), StrokeWidth=2))
    label(c, "before", 40, 60)
    label(c, "after: vignette, grain, bars", 990, 60, color=INK)
    out.save(OUT / "05_finish.png")


# -- 5. captions and camera ------------------------------------------------

def shrink_into(dest_canvas, frame_obj, x, y, scale=0.5):
    img = frame_obj.surface.makeImageSnapshot()
    dest_canvas.drawImageRect(img, skia.Rect.MakeXYWH(x, y, 1920 * scale, 1080 * scale),
                              skia.SamplingOptions(skia.FilterMode.kLinear))


def preview_captions_camera():
    from toolkit import Camera, Track, caption, finish
    shots = [
        ("wide, handheld drift", Camera(), "Every morning felt the same.", 0.0),
        ("zoomed in on the hero", Camera(x=660, y=560, zoom=1.9), "He was *tired* of trying.", 1.0),
        ("moved across to the enemy", Camera(x=1240, y=480, zoom=1.35), "And *it* was always there.", 2.0),
        ("shaking on a thud", Camera(zoom=1.1).shake(at=3.0, strength=1.0), "", 3.05),
    ]
    out = Frame()
    for i, (title, cam, text, t) in enumerate(shots):
        f = Frame()
        frame = int(t * 30)
        with cam.view(f.canvas, t):
            cast_scene(f.canvas, frame)
        if title.startswith("shaking"):
            # stack several moments of the shake faintly to show the jolt
            for k, tt in enumerate((3.0, 3.03, 3.07, 3.1, 3.13)):
                g = Frame()
                with cam.view(g.canvas, tt):
                    cast_scene(g.canvas, frame)
                f.canvas.drawImage(g.surface.makeImageSnapshot(), 0, 0,
                                   skia.SamplingOptions(), skia.Paint(Alphaf=0.35))
        finish(f, frame)
        if text:
            caption(f.canvas, text)
        x, y = (i % 2) * 960, (i // 2) * 540
        shrink_into(out.canvas, f, x, y)
        label(out.canvas, title, x + 24, y + 50, 26, INK)
    divider(out.canvas)
    out.save(OUT / "06_captions_and_camera.png")


# -- 7. the sound kit -----------------------------------------------------

def sound_tour():
    """Each sound in the kit, as (name, sound, mix settings)."""
    from toolkit import sound as sk
    melody = sk.Mix(4.2)
    for i, (n, at) in enumerate([("E5", 0), ("C5", 0.6), ("A4", 1.2), ("B4", 1.8), ("C5", 2.4), ("A4", 3.0)]):
        melody.add(sk.piano(n, 0.5, 0.7, key=i), at=at)
    drums = sk.Mix(2.2)
    for beat in range(8):
        at = beat * 0.25
        drums.add(sk.hihat(key=beat), at=at, gain_db=-12)
        if beat in (0, 3, 4):
            drums.add(sk.kick(), at=at)
        if beat in (2, 6):
            drums.add(sk.snare(key=beat), at=at, gain_db=-3)
    chords = sk.Mix(8.2)
    chords.add(sk.pad(["A2", "E3", "A3", "C4"], 3.0, key="am"), at=0)
    chords.add(sk.pad(["F2", "C3", "A3", "C4"], 3.0, key="f"), at=3.0)
    return [
        ("piano: a sad phrase", melody.render(), dict(reverb=0.35)),
        ("piano: A minor chord", sk.piano_chord(["A3", "C4", "E4", "A4"], 2.0), dict(reverb=0.35)),
        ("soft pads: A minor, then F", chords.render(), dict(gain_db=-4, reverb=0.4)),
        ("drums: kick, snare, hi-hat", drums.render(), dict(gain_db=-3, reverb=0.1)),
        ("footsteps", sk.footsteps(5, 0.5), dict(reverb=0.15)),
        ("whoosh", sk.whoosh(1.0), dict(reverb=0.2)),
        ("thud", sk.thud(), dict(reverb=0.25)),
        ("heartbeat", sk.heartbeat(4, 62), dict()),
        ("clock ticking", sk.ticking(4), dict(reverb=0.2)),
    ]


def waveform(canvas, samples, x, y, w, h, color=INK):
    mono = samples.mean(axis=0) if samples.ndim == 2 else samples
    cols = np.array_split(mono, w)
    paint = skia.Paint(AntiAlias=False, Color=to_color(color), StrokeWidth=1)
    peak = max(np.max(np.abs(mono)), 1e-9)
    for i, chunk in enumerate(cols):
        if len(chunk):
            lo, hi = chunk.min() / peak, chunk.max() / peak
            canvas.drawLine(x + i, y + h / 2 - hi * h / 2, x + i, y + h / 2 - lo * h / 2 + 1, paint)


def preview_sound():
    from toolkit import sound as sk
    items = sound_tour()
    out = Frame()
    c = out.canvas
    tour = sk.Mix(sum(s.shape[-1] / sk.SR + 0.8 for _, s, _ in items) + 1)
    at = 0.5
    for i, (name, samples, settings) in enumerate(items):
        x, y = 40 + (i % 3) * 627, 40 + (i // 3) * 340
        label(c, name, x, y + 30, 28, INK)
        label(c, f"{samples.shape[-1] / sk.SR:.1f} s", x, y + 300, 22)
        waveform(c, samples, x, y + 60, 580, 210, RED if name in ("thud", "heartbeat") else INK)
        tour.add(samples, at=at, **settings)
        at += samples.shape[-1] / sk.SR + 0.8
    tour.save(Path(__file__).parent / "audio" / "sound_kit_tour.wav")
    out.save(OUT / "07_sound_kit.png")


PREVIEWS = {"lines": preview_lines, "character": preview_character, "faces": preview_faces,
            "cast": preview_cast, "finish": preview_finish, "camera": preview_captions_camera,
            "sound": preview_sound}

if __name__ == "__main__":
    names = sys.argv[1:] or list(PREVIEWS)
    for name in names:
        PREVIEWS[name]()
        print(f"saved preview: {name}")
