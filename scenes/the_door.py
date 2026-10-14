"""Film 1, row 28 of the story: the door. About 11.4 seconds, three shots joined by hard cuts. It follows row 27,
where "I'll start *tomorrow*." filled the picture and the bar began to tremble.

 0-5.7 s     From the side, the wall by the door, in the grey morning: he walks in from the left as he is
             (nothing to put on) and stops at the board for a beat: TODAY and five empty boxes. He goes on
             toward the door. Behind him, off to the left, the phone buzzes, again and again: its cold light
             flickers in from the edge with each buzz. The camera grows shakier.
 5.7-8.6 s   The door up close: his arm comes in and takes the handle, and trembles there with the camera.
 8.6-11.4 s  His face, from the side, close: his eyes close, and he takes a long breath in.

The bar trembles throughout and the hum stays on; the rain is outside the door. Cut: he opens it in row 29.
"""
import math

import numpy as np

import scenes.five_things as five
from scenes.bedroom import ROOM, box, rounded_rect
from scenes.discipline import Discipline
from scenes.door_wall import DOOR, GROUND, WIDE_BOARD, draw_today, draw_wall, hero
from scenes.new_goals import Walk
from scenes.scroll import glow, light_on_face
from scenes.the_quote import TINT
from toolkit import INK, Camera, Face, Ink, Track, blink, draw_head, lerp, progress
from toolkit import sound as sk
from toolkit.rng import noise

PEAK_DB = -4.2          # set so the sounds sit at the same level as the sounds in the other scenes
TENSE = Face(eyes=0.75, brows=-0.25, mouth="flat", mouth_size=0.5, bags=True)

# -- shot 1: past the board, to the door ---------------------------------------------------------------------

STOP_AT = 640                          # in front of the board, as in the board scenes
DOOR_X = DOOR[0] - 70                  # where he'd stop at the door, as in row 10
to_board = Walk(0.1, -80, STOP_AT, 240, ramp=0.3)
LOOK = (to_board.stop + 0.1, to_board.stop + 0.6)          # he lifts his head to the board...
GO_ON = to_board.stop + 1.4                                  # ...and after a beat goes on to the door
to_door = Walk(GO_ON, STOP_AT, DOOR_X, 240, first="foot_r", ramp=0.4,
               feet0={k: v[0] for k, v in to_board.feet(GO_ON).items()})
HAND_SHOT = round(GO_ON + 0.8, 2)                            # a step or two, and cut to his hand reaching the handle
FACE_SHOT = HAND_SHOT + 2.9                                  # cut to his face
DURATION = round(FACE_SHOT + 2.8, 2)

BUZZES = [1.4, 3.2, 5.0, 6.9, 8.9, 10.6]                     # the phone, behind him, again and again
wide_camera = Camera(x=Track((0, 900), (HAND_SHOT, 1060, "inout")), zoom=1.06,
                     handheld=lambda t: 1.0 + 2.0 * progress(t, 0, HAND_SHOT), name="door.wide")


def buzzing(t):
    """0..1: the phone's light flaring as it buzzes (a short double buzz each time)."""
    out = 0.0
    for at in BUZZES:
        if at <= t < at + 0.5:
            u = (t - at) / 0.5
            out = max(out, math.sin(math.pi * min(1.0, u * 2.2)) if u < 0.45 else math.sin(math.pi * (u - 0.5) / 0.5))
    return out


def his_pose(t):
    face = TENSE.but(eyes=TENSE.eyes * blink(t, "hero.door", every=2.6))
    if t < GO_ON:
        look = progress(t, *LOOK, "inout") * (1 - progress(t, GO_ON - 0.4, GO_ON, "inout"))
        return to_board.pose(t, face, look_up=look)
    return to_door.pose(t, face)


def shot_wide(canvas, t, frame):
    with wide_camera.view(canvas, t):
        draw_wall(canvas, frame, five.DAYS, on_tray=("eraser", "red", "pale"), **five.BOARD)
        draw_today(canvas, frame, WIDE_BOARD, key="door.today")        # a new day: five empty boxes
        glow(canvas, (-260, 560), 1000, TINT, 0.05 + 0.12 * buzzing(t))   # the phone, off to the left, behind him
        hero.draw(canvas, frame, his_pose(t))


# -- shot 2: his hand on the handle --------------------------------------------------------------------------

hand_camera = Camera(zoom=Track((HAND_SHOT, 1.0), (FACE_SHOT, 1.05, "linear")), handheld=lambda t: 3.2, name="door.hand")
ROSE = (900, 560)


def shot_hand(canvas, t, frame):
    with hand_camera.view(canvas, t):
        ink = Ink(canvas, frame, color=ROOM, width=7.0, prefix="door.close")
        box(ink, [(700, 40), (2100, 40), (2100, 1060), (700, 1060)], "door", fill=(22, 22, 26))   # the door...
        ink.line((640, 40), (640, 1060), "frame", width=8.0)                                       # ...its frame
        glow(canvas, (-200, 560), 1200, TINT, 0.05 + 0.15 * buzzing(t))
        ink.circle(ROSE, 46, "rose", fill=(30, 30, 35))                                            # the handle
        box(ink, rounded_rect(ROSE[0] - 10, ROSE[1] - 20, ROSE[0] + 300, ROSE[1] + 20, 18), "lever", fill=(30, 30, 35))
        held = progress(t, HAND_SHOT, HAND_SHOT + 0.6, "out")       # his arm comes in and takes the handle...
        shake = held * 4.0                                              # ...and trembles there
        grip = lerp((-260, 980), (ROSE[0] + 170, ROSE[1] + 4), held)
        grip = (grip[0] + shake * noise(t * 11, "door.tremble", "x"), grip[1] + shake * noise(t * 11, "door.tremble", "y"))
        Ink(canvas, frame, color=INK, width=34.0, prefix="hero.closeup").line((-220, 1150), grip, "forearm",
                                                                             pin_ends=True, taper=0.0)


# -- shot 3: his face: eyes closed, a breath in --------------------------------------------------------------

face_camera = Camera(zoom=Track((FACE_SHOT, 1.0), (DURATION, 1.06, "linear")), handheld=lambda t: 2.4,
                     name="door.face")
HEAD, HEAD_R = (880, 520), 300
CLOSE_EYES = (FACE_SHOT + 0.5, FACE_SHOT + 1.1)
BREATH_IN = (FACE_SHOT + 1.0, FACE_SHOT + 2.6)


def shot_face(canvas, t, frame):
    with face_camera.view(canvas, t):
        ink = Ink(canvas, frame, color=ROOM, width=8.0, prefix="door.face")
        ink.line((1500, 40), (1500, 1060), "door.edge", width=8.0)          # the door, just ahead of him
        rise = 8 * progress(t, *BREATH_IN, "inout")
        head = (HEAD[0], HEAD[1] - rise)
        pen = Ink(canvas, frame, color=INK, width=22.0, prefix="hero.face.side")
        pen.line((head[0] - 20, head[1] + HEAD_R - 6), (head[0] - 40, 1150), "neck", taper=0.0)
        eyes = lerp(0.75, 0.0, progress(t, *CLOSE_EYES, "inout"))
        draw_head(pen, head, HEAD_R, TENSE.but(eyes=eyes), tilt=-3, facing=1)
        glow(canvas, (-200, 560), 1200, TINT, 0.05 + 0.12 * buzzing(t))
        light_on_face(canvas, head, HEAD_R, (-400, 560), TINT, 0.06 + 0.1 * buzzing(t))


# -- the scene ------------------------------------------------------------------------------------------


def draw(canvas, t, frame):
    if t < HAND_SHOT:
        shot_wide(canvas, t, frame)
    elif t < FACE_SHOT:
        shot_hand(canvas, t, frame)
    else:
        shot_face(canvas, t, frame)


bar = Discipline(start=18, shakes=[(-1.0, DURATION + 1.0)])   # trembling all through, on from row 27


def overlay(canvas, t, frame):
    bar.draw(canvas, t, frame)


def soundtrack():
    mix = sk.Mix(DURATION)

    def effect(prompt, seconds, name):            # ElevenLabs effects, all brought to the same level first
        return sk.normalize(sk.eleven_sound(prompt, seconds, name))

    # the hum, on from row 27; the rain outside, muffled by the door, nearer once he's at it
    hum = sk.pad(["A1", "E2"], DURATION, attack=0.05, release=1.0, brightness=0.05, key="hum")
    mix.add(hum, at=0, gain_db=-19, reverb=0.2)
    rain = effect("Heavy steady rain against a bedroom window, heard from inside a quiet room, early morning, "
                  "no thunder", 12.0, "rain_window")
    rain = sk.lowpass(np.concatenate([rain, rain])[:int(DURATION * sk.SR)], 1400)
    nearer = np.interp(np.arange(len(rain)) / sk.SR, [0, to_door.stop, HAND_SHOT], [10 ** (-6 / 20), 1.0, 1.0])
    mix.add(sk.fade_edges(rain * nearer, 0.05, 0.3), at=0, gain_db=-16, pan=0.3, reverb=0.05)
    # the phone, behind him in the bedroom
    buzz = effect("A smartphone on a wooden nightstand vibrating with a new text message, a short double buzz, "
                  "close up, in a quiet room", 1.5, "phone_buzz")
    for at in BUZZES:
        mix.add(sk.fade_edges(sk.lowpass(buzz[:int(0.75 * sk.SR)], 1600), 0.01, 0.05), at=at, gain_db=-14, pan=-0.6,
                reverb=0.15)
    # his steps
    for walk, key in ((to_board, "door.in"), (to_door, "door.on")):
        for n, (lift, land, foot, a, b) in enumerate(walk.steps):
            if land < HAND_SHOT and (walk is to_door or land < GO_ON):
                mix.add(sk.footstep(n, weight=0.55, key=key), at=land, gain_db=-12, pan=(b - 960) / 1400, reverb=0.12)
    # the long breath in: the first part of the sigh recording from row 20 (its breath in)
    sigh = effect("A tired man, alone in a silent room at night, takes a slow breath in through his nose and lets "
                  "out one long, slow, heavy sigh through his mouth. Close up, no other sounds", 5.0, "long_sigh")
    breath = sigh[:int(1.35 * sk.SR)]
    mix.add(sk.fade_edges(breath, 0.05, 0.25), at=BREATH_IN[0], gain_db=-14, reverb=0.1)
    bar.add_sounds(mix)
    return mix
