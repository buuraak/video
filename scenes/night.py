"""Film 1, row 7 of the story: night. 5 seconds, two shots joined by a hard cut.

0-2.3 s  Close on his phone from above, lying on the nightstand in the dark. It buzzes twice and
         the lock screen lights up: 22:47, and a message slides in from Sam: "you coming tonight?"
2.3-5 s  The bedroom from above, as at the start of the film, but at night: the clock says 22:47.
         He lies awake in the phone's cold light, looking at it. He reaches over slowly, turns it
         face down, and the room goes dark. His hand stays on it; he looks back up at the ceiling.

Sound: the hum, the phone buzzing on the wood, the soft knock as it's turned face down.
"""
import math

import numpy as np
import skia

from scenes.bedroom import (HERO_X, HIP_Y, PHONE, PHONE_TURN, ROOM, belly_hands, box, draw_bed, draw_blanket,
                            draw_nightstand, hero, rounded_rect, smooth, turned)
from scenes.discipline import Discipline
from scenes.scroll import GRIP, draw_body, draw_his_face, draw_phone, glow, light_on_face, phone_shape
from toolkit import BG, INK, SCREEN, Camera, Face, Ink, Pose, Track, lerp, progress, to_color
from toolkit import sound as sk
from toolkit.rng import noise
from toolkit.text import font

DURATION = 5.0
PEAK_DB = -6.9         # set so the hum matches scenes 1 to 3 (the buzz is this scene's loudest sound)
WIDE = 2.3             # cut from the phone to the bedroom
PULSES = ((0.40, 0.75), (0.92, 1.27))   # the phone buzzes twice
LIGHT_UP = 0.40        # the screen comes on with the first buzz...
BANNER = (0.48, 0.72)  # ...and Sam's message slides in
REACH = 2.6            # he starts reaching for the phone
GRAB = REACH + 1.0     # his hand slides out low across the bed, arm almost straight, then up onto the phone
LOW = (742, 536)       # the low point it passes, where the elbow can switch sides without a jump
FLIP = (3.7, 4.1)      # he turns it face down
LAND = FLIP[1]         # it lies face down: the knock
LOOK_BACK = (4.3, 4.9)  # he turns his face back up to the ceiling
TIME = "22:47"

# -- the lock screen -----------------------------------------------------------------
# Drawn in the phone's own measurements (the close-up size, screen 548 x 1048, its middle at 0, 0),
# so the same screen can be drawn big in the close-up or tiny on the nightstand in the wide shot.

SW, SL = 548, 1048
DARK_TEXT = (24, 28, 38)
BANNER_FILL = (214, 226, 246)


def text(canvas, s, x, y, size, color, align="center", bold=True):
    f = font(size, bold=bold)
    w = f.measureText(s)
    canvas.drawString(s, x - {"left": 0, "center": w / 2, "right": w}[align], y, f,
                      skia.Paint(AntiAlias=True, Color=to_color(color)))


def lock_screen(canvas, frame, level, banner):
    """The lit screen: the time, and Sam's message. level: how bright (0..1); banner: 0..1 slid in."""
    if level <= 0.003:
        return
    sx0, sy0, sx1 = -SW / 2, -SL / 2, SW / 2
    screen = skia.Path()
    screen.addPoly([skia.Point(*p) for p in rounded_rect(sx0, sy0, sx1, -sy0, 40)], True)
    shade = skia.GradientShader.MakeLinear([skia.Point(0, sy0), skia.Point(0, sy0 + 800)],
                                           [to_color((*SCREEN, int(255 * 0.42))), to_color((18, 22, 34, 255))])
    canvas.saveLayerAlpha(None, int(255 * min(level, 1.0)))
    canvas.drawPath(screen, skia.Paint(AntiAlias=True, Shader=shade))
    text(canvas, TIME, 0, sy0 + 165, 130, (*INK, 230), bold=False)
    if banner > 0:
        canvas.saveLayerAlpha(None, int(255 * banner))
        canvas.translate(0, -40 * (1 - banner))
        ink = Ink(canvas, frame, color=BANNER_FILL, width=3.0, prefix="night.banner")
        b0, b1, by0 = sx0 + 18, sx1 - 18, sy0 + 225
        box(ink, rounded_rect(b0, by0, b1, by0 + 150, 28), "banner", fill=BANNER_FILL)
        Ink(canvas, frame, color=DARK_TEXT, width=3.0, prefix="night.avatar").circle(
            (b0 + 52, by0 + 75), 32, "avatar", fill=(150, 160, 180))
        text(canvas, "S", b0 + 52, by0 + 89, 38, DARK_TEXT)
        text(canvas, "Sam", b0 + 104, by0 + 62, 44, DARK_TEXT, align="left")
        text(canvas, "now", b1 - 20, by0 + 58, 28, (90, 98, 115), align="right", bold=False)
        text(canvas, "you coming tonight?", b0 + 104, by0 + 120, 40, DARK_TEXT, align="left")
        canvas.restore()
    canvas.restore()


def buzzing(t):
    """1 while the phone buzzes, else 0."""
    return 1.0 if any(a <= t < b for a, b in PULSES) else 0.0


# -- shot 1: close on the phone ----------------------------------------------------------

CLOSE = (960, 700)       # the phone's middle: its bottom runs off the picture
CLOSE_TURN = -4          # it lies a little crooked
PW, PL = 600, 1100       # its size at close-up

phone_camera = Camera(zoom=Track((0, 1.0), (WIDE, 1.035, "linear")), name="night.phone")


def shot_phone(canvas, t, frame):
    with phone_camera.view(canvas, t):
        level = progress(t, LIGHT_UP, LIGHT_UP + 0.12, "out")
        glow(canvas, (CLOSE[0], CLOSE[1] - PL / 2 + 300), 900, SCREEN, 0.42 * level)
        shake = 2.5 * buzzing(t)
        canvas.save()
        canvas.translate(shake * noise(t * 45, "night.buzz", "x"), shake * noise(t * 45, "night.buzz", "y"))
        canvas.rotate(CLOSE_TURN, *CLOSE)
        ink = Ink(canvas, frame, color=ROOM, width=9.0, prefix="night.close")
        x0, y0 = CLOSE[0] - PW / 2, CLOSE[1] - PL / 2
        box(ink, rounded_rect(x0, y0, x0 + PW, y0 + PL, 60), "phone", width=9.0)
        screen = rounded_rect(x0 + 26, y0 + 26, x0 + PW - 26, y0 + PL - 26, 40)
        ink.fill(screen, "screen.dark", color=(20, 20, 24), wobble=0)
        canvas.save()
        canvas.translate(*CLOSE)
        lock_screen(canvas, frame, level, progress(t, *BANNER, "out"))
        canvas.restore()
        ink.stroke(screen, "screen", closed=True, width=4.0)
        canvas.restore()


# -- shot 2: the bedroom from above ------------------------------------------------------

bed_camera = Camera(name="night.bed")      # holds the opening view: only the gentle handheld wobble

TOP_RIGHT = PHONE_TURN + 90                # on the nightstand the phone's top points toward the bed
ON_BACK = turned([(PHONE[0] + 56, PHONE[1] + 6)], PHONE, PHONE_TURN)[0]   # his hand, resting on it after
SHIFT = 8                                  # he shifts toward the nightstand as he reaches (pixels)

# Breathing: slow and shallow while he looks at the phone, then one long breath out after.
BREATH = Track((WIDE, 0.1), (3.2, 0.35), (LAND, 0.0), (4.55, 0.9, "inout"), (DURATION, -0.3, "inout"))
LOOK = Track((WIDE, -0.42), (LOOK_BACK[0], -0.42), (LOOK_BACK[1], -0.05, "inout"))
EYES = Track((WIDE, 0.5), (4.5, 0.5), (4.62, 0.0, "in"), (4.85, 0.45, "out"))


def flip(t):
    """0 = screen up, 0.5 = standing on its edge, 1 = face down."""
    return progress(t, *FLIP, "inout")


def light(t):
    """How bright the phone lights the room (0..1): it goes as the screen turns away."""
    if t < FLIP[0]:
        return 1.0
    return max(0.0, math.cos(math.pi * flip(t)))


def _reach_path():
    """One smooth curve from his resting hand, out low, and up to the phone: points, and the share
    of the way along it where the low point is."""
    rest = belly_hands(hero.joints(Pose(x=HERO_X, y=HIP_Y - 3 * BREATH(REACH)))["shoulder"],
                       max(BREATH(REACH), 0))[0]
    pts = np.array(smooth([rest, LOW, GRIP], per_segment=40))
    along = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(pts, axis=0).T))])
    low = along[np.argmin(np.hypot(*(pts - LOW).T))] / along[-1]
    return pts, along / along[-1], low


REACH_PATH, REACH_SHARE, LOW_SHARE = _reach_path()
# when his hand passes the low point (the reach eases in and out)
PASS_LOW = REACH + (GRAB - REACH) * next(u for u in np.linspace(0, 1, 2001)
                                         if progress(REACH + u * (GRAB - REACH), REACH, GRAB, "inout") >= LOW_SHARE)


def left_hand(t, rest):
    """Reaches out low across the bed, up onto the phone, turns it over, and stays on it."""
    if t < REACH:
        return rest
    if t < GRAB:
        u = progress(t, REACH, GRAB, "inout")
        return (float(np.interp(u, REACH_SHARE, REACH_PATH[:, 0])), float(np.interp(u, REACH_SHARE, REACH_PATH[:, 1])))
    if t < FLIP[0]:
        return GRIP
    return lerp(GRIP, ON_BACK, progress(t, *FLIP, "inout"))


def his_joints(t, frame=None):
    """Where his joints are, lying in bed: only his left arm and his breathing move."""
    b = BREATH(t)
    pose = Pose(x=HERO_X - SHIFT * progress(t, REACH, GRAB, "inout"), y=HIP_Y - 3 * b)
    rest_l, rest_r = belly_hands(hero.joints(pose)["shoulder"], max(b, 0))
    pose = pose.but(hand_l=left_hand(t, rest_l), hand_r=rest_r)
    j = hero.skeleton(pose, frame)
    # once his hand is out low with the arm almost straight, the elbow eases over to point down
    # toward the bed, so it never rises across his face
    down = hero.skeleton(pose.but(bend_hand_l=-1))["elbow_l"]
    j["elbow_l"] = lerp(j["elbow_l"], down, progress(t, PASS_LOW - 0.3, PASS_LOW + 0.3))
    return j


def draw_table_phone(canvas, room, frame, t):
    f = flip(t)
    width = 60 * abs(math.cos(math.pi * f))
    if f < 0.5:     # screen up, lit: the lock screen at nightstand size
        level = light(t)
        glow(canvas, PHONE, 300, SCREEN, 0.3 * level)
        body = phone_shape(PHONE, 120, width, TOP_RIGHT)
        box(room, body, "phone", width=3.2)
        if width > 4:
            canvas.save()
            canvas.translate(*PHONE)
            canvas.rotate(TOP_RIGHT)
            canvas.scale(width * 0.8 / SW, 120 * 0.86 / SL)     # fills the screen inside its edge
            lock_screen(canvas, frame, level, 1.0)
            canvas.restore()
        room.stroke(phone_shape(PHONE, 120 * 0.86, width * 0.8, TOP_RIGHT, r=5), "phone.screen", closed=True,
                    width=1.8)
    else:           # face down: for a moment the still-lit screen leaks light around its edges
        leak = 0.6 * (1 - progress(t, LAND + 0.1, LAND + 0.6))
        draw_phone(canvas, room, PHONE, 120, width, TOP_RIGHT, "back", level=leak)


def shot_bed(canvas, t, frame):
    with bed_camera.view(canvas, t):
        room = Ink(canvas, frame, color=ROOM, width=4.0, prefix="bedroom")
        draw_bed(room)
        draw_nightstand(room, canvas, frame, time=TIME, phone="plugged")
        draw_table_phone(canvas, room, frame, t)

        b = BREATH(t)
        j = his_joints(t, frame)
        look = LOOK(t)
        pen = draw_body(canvas, frame, j, ("legs", "spine", "head"), hero.head_r)
        draw_blanket(room, b)
        face = Face(eyes=EYES(t), brows=0.9, mouth="frown", mouth_size=0.5, bags=True)
        draw_his_face(canvas, pen, j["head"], hero.head_r, face, 12 * look, look, 0.0)
        level = light(t)
        if level > 0:     # the cold light on the side of his face nearest the phone
            light_on_face(canvas, j["head"], hero.head_r, PHONE, SCREEN, 0.5 * level)
        draw_body(canvas, frame, j, ("arms",), hero.head_r)


# -- the scene ---------------------------------------------------------------------------


def draw(canvas, t, frame):
    if t < WIDE:
        shot_phone(canvas, t, frame)
    else:
        shot_bed(canvas, t, frame)


bar = Discipline()  # still empty


def overlay(canvas, t, frame):
    bar.draw(canvas, t, frame)


def soundtrack():
    mix = sk.Mix(DURATION)
    mix.add(sk.pad(["A1", "E2"], DURATION, attack=0.4, release=1.0, brightness=0.05, key="hum"),
            at=0, gain_db=-17, reverb=0.2)
    # one long buzz from ElevenLabs, cut into the two short buzzes of a text message
    buzz = sk.normalize(sk.eleven_sound("A smartphone on a wooden nightstand vibrating with a new text message, "
                                        "a short double buzz, close up, in a quiet room", 1.5, "phone_buzz"))
    for (a, b), cut in zip(PULSES, (0.05, 0.6)):
        part = buzz[int(cut * sk.SR):int((cut + b - a) * sk.SR)]
        mix.add(sk.fade_edges(part, 0.01, 0.04), at=a, gain_db=-12, reverb=0.08)
    knock = sk.normalize(sk.eleven_sound("A smartphone turned over and laid face down on a wooden nightstand, "
                                         "one soft dull knock, close up, quiet room", 0.6, "phone_face_down"))
    mix.add(knock, at=LAND - 0.02, gain_db=-11, pan=-0.3, reverb=0.1)
    mix.add(sk.whoosh(0.8, peak=0.5, low=150, high=800, key="night.reach"), at=REACH, gain_db=-23, pan=-0.15,
            reverb=0.1)
    return mix
