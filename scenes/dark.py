"""Film 1, row 19 of the story: dark. About 8 seconds, two shots joined by a hard cut. It follows row 18, where
he ran out of room on the board. 3:47 at night.

 0-3 s    His screen close up, held in his stick arms (as in row 13): the smug man's reel plays. A low-battery
          warning slides down: 1%, with a small red battery. Then the screen goes black, the reel's voice cut
          dead, and the dead phone is barely there in the dark.
 3-8 s    From above, the opening view, dark: the charger lies unplugged on the nightstand. He slowly lowers the
          dead phone onto his chest and lies still, staring up, numb. Only the small red clock glows, 3:47, its
          faint red light falling on him. The hum fades away to silence.

No caption. Sound: a reel's muffled voice, a low-battery chime, the hum fading out.
"""
import math

import numpy as np
import skia

from scenes.bedroom import HERO_X, HIP_Y, ROOM, box, clock_numbers, draw_bed, draw_blanket, draw_mess, \
    draw_nightstand, hero, rounded_rect
from scenes.discipline import Discipline
from scenes.grind_1 import BANNER_H, BANNER_X0, BANNER_X1, BANNER_Y, draw_reel, light_level
from scenes.grind_5 import NUMB
from scenes.night import BANNER_FILL, DARK_TEXT, text
from scenes.scroll import CHEST, HOLD_ELBOWS, draw_body, draw_his_face, draw_phone, glow, light_on_face, reel_sounds
from scenes.the_quote import C, PL, PW, SCREEN_RECT
from toolkit import INK, RED, SCREEN, Camera, Ink, Pose, Track, blink, clamp, lerp, progress, to_color
from toolkit import sound as sk

DURATION = 8.0
PEAK_DB = -1.7          # set so the hum matches the other scenes
TIME = "3:47"
ABOVE = 3.0            # cut to the room from above

# -- shot 1: his screen; the battery dies ---------------------------------------------------------

WARNING = 0.6          # the low-battery warning slides down...
DIES = 2.2             # ...and the screen goes black
WORDS = ((-5.0, "MY FIRST"), (-5.0, "MILLION AT 22"))      # the reel's words are already up

screen_camera = Camera(zoom=Track((0, 1.0), (ABOVE, 1.04, "linear")), name="dark.screen")


def alive(t):
    """1 while the screen is on, falling to 0 as the phone dies."""
    return 1 - progress(t, DIES, DIES + 0.08, "in")


def draw_warning(canvas, frame, t):
    """The low-battery warning: a pale banner like Sam's messages, with a small red, nearly empty battery."""
    slid = progress(t, WARNING, WARNING + 0.25, "out")
    if slid <= 0:
        return
    canvas.saveLayerAlpha(None, int(255 * slid))
    canvas.translate(0, -60 * (1 - slid))
    ink = Ink(canvas, frame, color=BANNER_FILL, width=3.0, prefix="dark.banner")
    b0, b1, by0 = BANNER_X0, BANNER_X1, BANNER_Y
    box(ink, rounded_rect(b0, by0, b1, by0 + BANNER_H, 38), "banner", fill=BANNER_FILL)
    # the battery: an outline with its little nub, and a thin red sliver of charge
    bx, by = b0 + 34, by0 + 78
    pen = Ink(canvas, frame, color=DARK_TEXT, width=5.0, prefix="dark.battery")
    box(pen, rounded_rect(bx, by, bx + 92, by + 46, 10), "battery", fill=BANNER_FILL)
    box(pen, rounded_rect(bx + 92, by + 14, bx + 102, by + 32, 3), "battery.nub", fill=DARK_TEXT)
    Ink(canvas, frame, color=RED, width=3.0, prefix="dark.battery").fill(
        rounded_rect(bx + 8, by + 8, bx + 18, by + 38, 3), "battery.charge", color=RED, wobble=0)
    text(canvas, "Low Battery", b0 + 146, by0 + 84, 60, DARK_TEXT, align="left")
    text(canvas, "now", b1 - 28, by0 + 78, 38, (90, 98, 115), align="right", bold=False)
    text(canvas, "1% battery remaining", b0 + 146, by0 + 160, 52, DARK_TEXT, align="left")
    canvas.restore()


def shot_screen(canvas, t, frame):
    with screen_camera.view(canvas, t):
        on = alive(t)
        glow(canvas, C, 900, SCREEN, 0.35 * light_level(t, []) * on)
        dim = 0.35 + 0.65 * on            # once it's dead, the phone and his arms are barely there in the dark
        canvas.saveLayerAlpha(None, int(255 * dim))
        ink = Ink(canvas, frame, color=ROOM, width=9.0, prefix="quote.phone")
        box(ink, rounded_rect(C[0] - PW / 2, C[1] - PL / 2, C[0] + PW / 2, C[1] + PL / 2, 60), "phone", width=9.0)
        screen = rounded_rect(*SCREEN_RECT, 40)
        path = skia.Path()
        path.addPoly([skia.Point(*p) for p in screen], True)
        canvas.save()
        canvas.clipPath(path, doAntiAlias=True)
        canvas.drawPaint(skia.Paint(Color=to_color((6, 6, 8))))
        if on > 0:
            canvas.saveLayerAlpha(None, int(255 * on))
            draw_reel(canvas, frame, t, "guru", WORDS)
            draw_warning(canvas, frame, t)
            canvas.restore()
        canvas.restore()
        ink.stroke(screen, "screen", closed=True, width=4.0)
        arm = Ink(canvas, frame, color=INK, width=30.0, prefix="hero.closeup")
        arm.line((C[0] - 260, 1300), (C[0] - PW / 2 + 4, 840), "forearm.l", pin_ends=True, taper=0.0)
        arm.line((C[0] + 260, 1300), (C[0] + PW / 2 - 4, 810), "forearm.r", pin_ends=True, taper=0.0)
        canvas.restore()


# -- shot 2: from above, in the dark ---------------------------------------------------------------

LOWER = (ABOVE + 0.5, ABOVE + 2.0)                     # he slowly lowers the dead phone onto his chest
ON_CHEST = (HERO_X, 600)
RESTING_ELBOWS = {"elbow_l": (844, 516), "elbow_r": (996, 516)}   # where his arms reach the phone lying there
DARKNESS = 0.82                                        # how much of the room the dark swallows
CLOCK_AT = (663, 285)                                  # the small clock's numbers on the nightstand

bed_camera = Camera(zoom=Track((ABOVE, 1.0), (DURATION, 1.04, "linear")), name="dark.bed")


def shot_bed(canvas, t, frame):
    with bed_camera.view(canvas, t):
        room = Ink(canvas, frame, color=ROOM, width=4.0, prefix="bedroom")
        draw_bed(room)
        draw_nightstand(room, canvas, frame, time=TIME, phone=False)     # the charger lies unplugged
        draw_mess(room, ("clothes", "cups", "pizza"))

        b = 0.35 * math.sin(2 * math.pi * t / 4.6)
        u = progress(t, *LOWER, "inout")
        phone_at = lerp(CHEST, ON_CHEST, u)
        pose = Pose(x=HERO_X, y=HIP_Y - 3 * b).but(hand_l=(phone_at[0] - 29, phone_at[1]),
                                                   hand_r=(phone_at[0] + 29, phone_at[1]))
        j = hero.skeleton(pose, frame)
        j.update({k: lerp(HOLD_ELBOWS[k], RESTING_ELBOWS[k], u) for k in HOLD_ELBOWS})
        pen = draw_body(canvas, frame, j, ("legs", "spine", "head"), hero.head_r)
        draw_blanket(room, b)
        face = NUMB.but(eyes=NUMB.eyes * blink(t, "hero.dark", every=4.0, length=0.3))
        draw_his_face(canvas, pen, j["head"], hero.head_r, face, 0.0, 0.0, 0.12)
        draw_body(canvas, frame, j, ("arms",), hero.head_r)
        draw_phone(canvas, room, phone_at, 86, 62, 0, "back", level=0.0)

        # the dark, and in it only the red clock, its faint light falling on him
        canvas.drawPaint(skia.Paint(Color=to_color((4, 3, 5, int(255 * DARKNESS)))))
        # (faint: the side of his face nearest the clock catches a little of it, never a red face)
        glow(canvas, CLOCK_AT, 520, RED, 0.11)
        light_on_face(canvas, j["head"], hero.head_r, CLOCK_AT, RED, 0.08)
        clock_numbers(canvas, frame, TIME, CLOCK_AT, 24, "clock.small")


# -- the scene -------------------------------------------------------------------------------------


def draw(canvas, t, frame):
    if t < ABOVE:
        shot_screen(canvas, t, frame)
    else:
        shot_bed(canvas, t, frame)


bar = Discipline()  # still empty


def overlay(canvas, t, frame):
    bar.draw(canvas, t, frame)


FADE_OUT = (ABOVE + 0.2, DURATION - 1.0)    # the hum fades away to silence


def soundtrack():
    mix = sk.Mix(DURATION)
    hum = sk.pad(["A1", "E2"], DURATION, attack=0.4, release=1.0, brightness=0.05, key="hum")
    t = np.arange(hum.shape[1]) / sk.SR
    fade = 1 - np.clip((t - FADE_OUT[0]) / (FADE_OUT[1] - FADE_OUT[0]), 0, 1)
    mix.add(hum * fade ** 2, at=0, gain_db=-17, reverb=0.2)
    # the smug man's reel, muffled, cut dead as the phone dies
    adam, laura, liam = reel_sounds()
    part = adam[int(1.0 * sk.SR):int((1.0 + DIES) * sk.SR)]
    mix.add(sk.fade_edges(part, 0.01, 0.005), at=0, gain_db=-9 + 3.4, pan=0.05, reverb=0.05)
    # the low-battery chime: two soft notes falling, from the phone's small speaker
    for k, (note, at) in enumerate((("A5", WARNING), ("E5", WARNING + 0.16))):
        chime = sk.lowpass(sk.piano(note, held=0.35, velocity=0.5, key=("dark.chime", k)), 3500)
        mix.add(chime, at=at, gain_db=-20, pan=0.05, reverb=0.06)
    return mix
