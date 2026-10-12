"""Film 1, row 7b of the story: the quote. 5 seconds, three shots joined by hard cuts.
It comes between the night (row 7) and the reset (row 8), and gives him a reason for his attempt.

0-1.4 s    From above, later that night: the clock says 23:58. He can't sleep and is scrolling again,
           holding the phone up over his chest, its cold light on his tired face. One swipe.
1.4-3.2 s  The phone's screen, close up, held in his stick arms: a reel. A smug stick-figure man in a
           suit, and under him, popping up in big bold words: WHAT ARE YOU / WAITING FOR?
3.2-5 s    His face from above, close, lit by the phone: sad. The camera zooms in fast with a deep hit,
           and his face turns determined: eyes wide, brows set, mouth a firm line.

Sound: only the hum, a soft swipe, and a deep hit on the fast zoom (the reel has no voice: we read it).
"""
import math

import skia

from scenes.bedroom import HERO_X, HIP_Y, ROOM, box, draw_bed, draw_blanket, draw_nightstand, hero, rounded_rect
from scenes.discipline import Discipline
from scenes.scroll import CHEST, HOLD_ELBOWS, draw_body, draw_his_face, draw_phone, glow, light_on_face
from toolkit import INK, SCREEN, Camera, Character, Face, Ink, Pose, Track, blink, clamp, draw_head, lerp, progress, to_color
from toolkit import sound as sk
from toolkit.rng import noise
from toolkit.text import font

DURATION = 5.0
PEAK_DB = -1.5         # set so the hum matches the other scenes (the deep hit is the loudest moment)
REEL = 1.4             # cut to the phone's screen
FACE = 3.2             # cut to his face
SWIPE = 0.6            # his thumb flicks to the next reel
WORDS = ((1.6, "WHAT ARE YOU"), (1.9, "WAITING FOR?"))   # each line pops up on the reel
ZOOM = 3.7             # the fast zoom starts...
TURN = (3.75, 3.95)    # ...and his face turns determined
TINT = (172, 202, 255)


def light_level(t):
    """The phone's light: flickering with the video, dipping as he swipes."""
    level = 0.85 * (1 + 0.12 * noise(t * 5, "quote.reel"))
    if SWIPE - 0.06 <= t < SWIPE + 0.16:
        level *= 0.35 + 0.65 * progress(t, SWIPE + 0.02, SWIPE + 0.16, "out")
    return level


def swipe(t):
    """0..1: his thumb flicking up the screen."""
    if SWIPE - 0.09 <= t < SWIPE + 0.2:
        return progress(t, SWIPE - 0.09, SWIPE, "out") * (1 - progress(t, SWIPE, SWIPE + 0.2, "inout"))
    return 0.0


# -- shot 1: from above, scrolling in the dark ---------------------------------------------

bed_camera = Camera(name="quote.bed")


def shot_bed(canvas, t, frame):
    with bed_camera.view(canvas, t):
        room = Ink(canvas, frame, color=ROOM, width=4.0, prefix="bedroom")
        draw_bed(room)
        draw_nightstand(room, canvas, frame, time="23:58", phone=False)

        b = 0.35 * math.sin(2 * math.pi * t / 4.2)
        pose = Pose(x=HERO_X, y=HIP_Y - 3 * b)
        phone_at = (CHEST[0], CHEST[1] - 3 * swipe(t))
        pose = pose.but(hand_l=(phone_at[0] - 29, phone_at[1]), hand_r=(phone_at[0] + 29, phone_at[1] - 16 * swipe(t)))
        j = hero.skeleton(pose, frame)
        j.update(HOLD_ELBOWS)                 # elbows resting on the bed beside him, forearms up to the phone

        pen = draw_body(canvas, frame, j, ("legs", "spine", "head"), hero.head_r)
        draw_blanket(room, b)
        face = Face(eyes=0.45 * blink(t, "hero.quote", every=3.0, length=0.22), brows=0.9, mouth="frown",
                    mouth_size=0.5, bags=True)
        draw_his_face(canvas, pen, j["head"], hero.head_r, face, 0.0, 0.0, 0.12)
        level = light_level(t)
        source = (phone_at[0], phone_at[1] - 40)
        glow(canvas, source, 260, TINT, 0.28 * level)
        near = clamp(1 - math.dist(source, j["head"]) / 330)
        light_on_face(canvas, j["head"], hero.head_r, source, TINT, 0.6 * level * near)
        draw_body(canvas, frame, j, ("arms",), hero.head_r)
        draw_phone(canvas, room, phone_at, 86, 62, 0, "back", level=level, tint=TINT)


# -- shot 2: the reel ------------------------------------------------------------------------

C = (960, 540)           # the phone fills the picture: its top and bottom run off it
PW, PL = 900, 1700
SCREEN_RECT = (C[0] - PW / 2 + 26, C[1] - PL / 2 + 26, C[0] + PW / 2 - 26, C[1] + PL / 2 - 26)
guru = Character("guru", height=620)
GURU_FACE = Face(eyes=0.8, brows=-0.15, mouth="smile", mouth_size=0.8)
BOX_TOP = 600            # the reel's dark caption box
WORD_SIZE = 104

reel_camera = Camera(zoom=Track((REEL, 1.0), (FACE, 1.04, "linear")), name="quote.reel")


def pop(t, at):
    """A caption line popping up: (alpha, scale)."""
    u = progress(t, at, at + 0.12, "out")
    return u, 1.18 - 0.18 * u


def draw_reel(canvas, frame, t):
    """What plays on the screen: the smug man, and the words under him."""
    x0, y0, x1, y1 = SCREEN_RECT
    shade = skia.GradientShader.MakeLinear([skia.Point(0, 132), skia.Point(0, 948)],
                                           [to_color((46, 58, 88)), to_color((16, 20, 32))])
    canvas.drawRect(skia.Rect(x0, y0, x1, y1), skia.Paint(Shader=shade))
    # the man: it's a video, so he sways a little and nods along, pleased with himself
    sway = 6 * math.sin(2 * math.pi * t / 1.7)
    pose = Pose(x=C[0] + sway, y=610 + 3 * math.sin(2 * math.pi * t / 0.85), face=GURU_FACE,
                head_tilt=2.5 * math.sin(2 * math.pi * t / 1.7), ground=None)
    sh = guru.joints(pose)["shoulder"]
    j = guru.draw(canvas, frame, pose.but(hand_l=(sh[0] - 8, sh[1] + 120), hand_r=(sh[0] + 8, sh[1] + 120)))
    pen = Ink(canvas, frame, color=INK, width=6.0, prefix="guru.suit")
    s = j["shoulder"]       # his suit: a tie and the jacket's lapels
    pen.stroke([(s[0], s[1] + 8), (s[0] - 10, s[1] + 60), (s[0], s[1] + 125), (s[0] + 10, s[1] + 60)], "tie",
               closed=True)
    pen.line((s[0] - 60, s[1] + 6), (s[0] - 14, s[1] + 140), "lapel.l")
    pen.line((s[0] + 60, s[1] + 6), (s[0] + 14, s[1] + 140), "lapel.r")
    canvas.drawRect(skia.Rect(x0, BOX_TOP, x1, y1), skia.Paint(Color=to_color((12, 14, 22, 235))))
    f = font(WORD_SIZE)
    for i, (at, line) in enumerate(WORDS):
        alpha, scale = pop(t, at)
        if alpha <= 0:
            continue
        w = f.measureText(line)
        y = 712 + i * WORD_SIZE * 1.15
        canvas.save()
        canvas.translate(C[0], y - WORD_SIZE * 0.35)
        canvas.scale(scale, scale)
        canvas.translate(-C[0], -(y - WORD_SIZE * 0.35))
        canvas.drawString(line, C[0] - w / 2, y + 6, f, skia.Paint(
            AntiAlias=True, Color=to_color((0, 0, 0, int(200 * alpha))),
            MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, WORD_SIZE * 0.08)))
        canvas.drawString(line, C[0] - w / 2, y, f, skia.Paint(AntiAlias=True,
                                                              Color=to_color((240, 242, 248, int(255 * alpha)))))
        canvas.restore()


def shot_reel(canvas, t, frame):
    with reel_camera.view(canvas, t):
        level = light_level(t)
        glow(canvas, C, 900, SCREEN, 0.35 * level)
        ink = Ink(canvas, frame, color=ROOM, width=9.0, prefix="quote.phone")
        body = rounded_rect(C[0] - PW / 2, C[1] - PL / 2, C[0] + PW / 2, C[1] + PL / 2, 60)
        box(ink, body, "phone", width=9.0)
        screen = rounded_rect(*SCREEN_RECT, 40)
        path = skia.Path()
        path.addPoly([skia.Point(*p) for p in screen], True)
        canvas.save()
        canvas.clipPath(path, doAntiAlias=True)
        draw_reel(canvas, frame, t)
        canvas.restore()
        ink.stroke(screen, "screen", closed=True, width=4.0)
        # his stick arms holding it, coming up from his chest below (he lies under it)
        arm = Ink(canvas, frame, color=INK, width=30.0, prefix="hero.closeup")
        for side, sx in (("l", -1), ("r", 1)):
            edge = C[0] + sx * (PW / 2 - 4)
            arm.line((C[0] + sx * 260, 1300), (edge, 840 - 30 * (sx > 0)), "forearm." + side, pin_ends=True,
                     taper=0.0)


# -- shot 3: his face, and the fast zoom ------------------------------------------------------

HEAD, HEAD_R = (960, 520), 330
face_camera = Camera(x=960, y=Track((FACE, 520), (ZOOM, 518, "linear"), (ZOOM + 0.22, 470, "out")),
                     zoom=Track((FACE, 1.0), (ZOOM, 1.03, "linear"), (ZOOM + 0.22, 1.45, "out"),
                                (DURATION, 1.5, "linear")), name="quote.face")
face_camera.shake(at=ZOOM + 0.12, strength=0.5, length=0.4)


def his_face(t):
    """Sad, then determined: eyes wide, brows set, the frown flattening into a firm line."""
    u = progress(t, *TURN, "inout")
    eyes = lerp(0.5, 0.92, u)
    if t < TURN[0]:
        eyes *= blink(t, "hero.quote.face", every=2.5, length=0.24)
    return Face(eyes=eyes, brows=lerp(0.9, -0.6, u), mouth="frown", mouth_size=0.6 * (1 - u), bags=True)


def draw_close_face(canvas, frame, face, level, tilt=-1.5):
    """His face from above, close, on the pillow, lit by the phone (`level`: how bright its light is)."""
    room = Ink(canvas, frame, color=ROOM, width=12.0, prefix="closeup")
    box(room, rounded_rect(120, 110, 1800, 880, 140), "pillow")
    pen = Ink(canvas, frame, color=INK, width=22.0, prefix="hero.face")
    pen.line((HEAD[0], HEAD[1] + HEAD_R - 6), (HEAD[0] + 4, 1100), "neck", taper=0.0)
    draw_head(pen, HEAD, HEAD_R, face, tilt=tilt)
    # the phone's light comes from below: it's held over his chest, out of the picture
    source = (HEAD[0], 1250)
    glow(canvas, (HEAD[0], 1150), 900, TINT, 0.3 * level)
    light_on_face(canvas, HEAD, HEAD_R, source, TINT, 0.45 * level)


def shot_face(canvas, t, frame):
    with face_camera.view(canvas, t):
        draw_close_face(canvas, frame, his_face(t), light_level(t))


# -- the scene ---------------------------------------------------------------------------------


def draw(canvas, t, frame):
    if t < REEL:
        shot_bed(canvas, t, frame)
    elif t < FACE:
        shot_reel(canvas, t, frame)
    else:
        shot_face(canvas, t, frame)


bar = Discipline()  # still empty: feeling motivated isn't doing


def overlay(canvas, t, frame):
    bar.draw(canvas, t, frame)


def soundtrack():
    mix = sk.Mix(DURATION)
    mix.add(sk.pad(["A1", "E2"], DURATION, attack=0.4, release=1.0, brightness=0.05, key="hum"),
            at=0, gain_db=-17, reverb=0.2)
    mix.add(sk.lowpass(sk.tick(key="quote.swipe"), 2500), at=SWIPE - 0.02, gain_db=-24, reverb=0.05)
    mix.add(sk.whoosh(0.32, peak=0.95, low=120, high=900, key="quote.zoom"), at=ZOOM - 0.2, gain_db=-14, reverb=0.1)
    mix.add(sk.thud(1.0, key="quote.hit"), at=ZOOM + 0.1, gain_db=-6, reverb=0.3)
    return mix
