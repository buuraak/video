"""Film 1, scene 1: waking up. About 20 seconds, three shots joined by hard cuts.

 0-8 s   Fade in from black. From straight above: he sleeps in bed, blanket up to his
         chest, arms on top of it. Left of the pillow, the nightstand with the alarm clock
         (red 5:59) and his phone on its charger. Restless sleep: worried brows, his head
         rolls slowly to one side, uneven breathing with one heavy sigh. The camera creeps in.
 8-15 s  The alarm clock from the front, filling the screen. 5:59, then 6:00: harsh beeps,
         the red numbers blink with them. His stick arm drags in slowly from the right and
         drops heavily onto the button. The beeping stops.
15-20 s  From above, close on his face on the pillow. His eyes open slowly, only halfway.
         Heavy lids, bags, worried brows.

Sound: a low dark hum under everything, the alarm, the click of the button.
"""
import skia

from scenes.bedroom import (HERO_X, HIP_Y, ROOM, belly_hands, box, clock_numbers, draw_bed, draw_blanket,
                            draw_nightstand, hero, rounded_rect)
from toolkit import INK, Camera, Face, Ink, Pose, Track, draw_face, draw_head, lerp, progress
from toolkit import sound as sk
from toolkit.character import reach

DURATION = 20.0
CLOCK_SHOT = 8.0       # cut to the clock
ALARM = 10.0           # 5:59 becomes 6:00 and the alarm goes off
PRESS = 13.85          # his arm lands on the button and the beeping stops
FACE_SHOT = 15.0       # cut to his face
FADE_IN = 2.0          # seconds to fade in from black


def time_shown(t):
    return "5:59" if t < ALARM else "6:00"


def numbers_lit(t):
    """While the alarm beeps, the numbers blink with it. Otherwise they stay lit."""
    if ALARM <= t < PRESS:
        return 1.0 if sk.alarm_on(t - ALARM) else 0.0
    return 1.0


# -- shot 1: from above, he sleeps (the bedroom itself is in bedroom.py) ---------------

bed_camera = Camera(x=Track((0, 960), (CLOCK_SHOT, 930, "linear")),
                    y=Track((0, 540), (CLOCK_SHOT, 505, "linear")),
                    zoom=Track((0, 1.0), (CLOCK_SHOT, 1.07, "linear")), name="bed")

# Uneven breathing: short shallow breaths, then one deep sigh and a long breath out.
BREATH = Track((0, 0.0), (1.3, 0.8), (2.6, -0.2), (3.3, 0.4), (3.9, 0.0), (5.4, 1.6),
               (7.0, -0.6), (8.0, 0.2))
# His head rolls slowly to one side on the pillow, then partly back.
ROLL = Track((0, -0.1), (2.4, -0.1), (3.9, 0.6), (5.6, 0.6), (6.9, 0.2), (8.0, 0.25))


def shot_bed(canvas, t, frame):
    with bed_camera.view(canvas, t):
        room = Ink(canvas, frame, color=ROOM, width=4.0, prefix="bedroom")
        draw_bed(room)
        draw_nightstand(room, canvas, frame)

        b = BREATH(t)
        roll = ROLL(t)
        pose = Pose(x=HERO_X, y=HIP_Y - 3 * b, head_tilt=12 * roll)
        left, right = belly_hands(hero.joints(pose)["shoulder"], max(b, 0))
        pose = pose.but(hand_l=left, hand_r=right)
        j = hero.draw(canvas, frame, pose)          # the blanket then hides his body and legs
        draw_blanket(room, b)

        # his hands rest on his belly, on top of the blanket (same strokes as before, so they match)
        pen = Ink(canvas, frame, color=hero.color, width=hero.line_width, prefix=hero.name)
        for side in ("_l", "_r"):
            pen.line(j["shoulder"], j["elbow" + side], "upper_arm" + side, pin_ends=True, taper=0.15)
            pen.line(j["elbow" + side], j["hand" + side], "forearm" + side, pin_ends=True, taper=0.15)

        # asleep, but not at peace: worried brows, a frown that deepens with the sigh
        sigh = max(b, 0) / 1.6
        face = Face(eyes=0.0, brows=lerp(0.8, 1.0, sigh), mouth="frown",
                    mouth_size=lerp(0.5, 0.75, sigh), bags=True)
        draw_face(pen, j["head"], hero.head_r, face, tilt=pose.head_tilt, facing=0.55 * roll)


# -- shot 2: the alarm clock -------------------------------------------------------

TABLE = 920                       # the nightstand top the clock stands on
CLOCK = (310, 380, 1610, TABLE)   # the clock's body, seen from the front: it fills most of the screen
WINDOW = (400, 460, 1520, 838)    # the dark window the numbers glow in
BUTTON = (1110, 342, 1410, 380)   # the snooze button on top
BUTTON_DOWN = 16                  # how far the button goes in when pressed
ARM = (440, 420)                  # upper arm and forearm, at close-up size
SHOULDER_FROM_HAND = (800, 70)    # his shoulder is just off screen to the right, down at bed height

clock_camera = Camera(name="clock")

# Where the end of his arm is: it drags in slowly from the right, lifts a little,
# then drops heavily onto the button and pushes it in.
ON_BUTTON = (1255, BUTTON[1] - 12)
ARM_END = Track((11.4, (1990, 296)), (13.3, (1262, 296), "inout"), (13.62, (1258, 282), "out"),
                (PRESS, ON_BUTTON, "in"), (PRESS + 0.1, (ON_BUTTON[0], ON_BUTTON[1] + BUTTON_DOWN), "out"))
DIP = Track((PRESS, 0.0), (PRESS + 0.07, 4.0, "out"), (PRESS + 0.35, 0.0, "inout"))


def shot_clock(canvas, t, frame):
    with clock_camera.view(canvas, t):
        ink = Ink(canvas, frame, color=ROOM, width=8.0, prefix="clock")
        ink.floor(TABLE, key="table", width=6.0)
        ink.floor(TABLE + 22, key="table.front", width=5.0)

        dip = DIP(t)
        canvas.save()
        canvas.translate(0, dip)
        pressed = BUTTON_DOWN * progress(t, PRESS, PRESS + 0.1, "out")
        box(ink, rounded_rect(BUTTON[0], BUTTON[1] + pressed, BUTTON[2], BUTTON[3] + 6, 12), "button", width=7.0)
        box(ink, rounded_rect(*CLOCK, 84), "body", width=9.0)
        box(ink, rounded_rect(*WINDOW, 44), "window", width=6.0)
        clock_numbers(canvas, frame, time_shown(t), ((WINDOW[0] + WINDOW[2]) / 2, (WINDOW[1] + WINDOW[3]) / 2 + 2),
                      320, "clock.big", on=numbers_lit(t))
        canvas.restore()

        if t >= ARM_END.keys[0][0]:
            end = ARM_END(t)
            shoulder = (end[0] + SHOULDER_FROM_HAND[0], end[1] + SHOULDER_FROM_HAND[1])
            elbow, end, _ = reach(shoulder, end, *ARM, 1)
            pen = Ink(canvas, frame, color=INK, width=30.0, prefix="hero.closeup")
            beyond = (shoulder[0] + 0.6 * (shoulder[0] - elbow[0]), shoulder[1] + 0.6 * (shoulder[1] - elbow[1]))
            pen.line(beyond, elbow, "upper_arm", pin_ends=True, taper=0.0)     # runs on off screen
            pen.line(elbow, end, "forearm", pin_ends=True, taper=0.1)


# -- shot 3: his face, from above ---------------------------------------------------

face_camera = Camera(name="face")
HEAD = (960, 520)
HEAD_R = 330

# His eyes open slowly, in two heavy goes, and only halfway. Later, one slow blink.
EYES = Track((0, 0.0), (16.0, 0.0), (16.8, 0.22, "inout"), (17.1, 0.2), (17.9, 0.5, "inout"),
             (18.9, 0.5), (19.12, 0.0, "in"), (19.45, 0.5, "out"))
TILT = Track((FACE_SHOT, -4.0), (DURATION, -1.5))


def shot_face(canvas, t, frame):
    with face_camera.view(canvas, t):
        room = Ink(canvas, frame, color=ROOM, width=12.0, prefix="closeup")
        box(room, rounded_rect(120, 110, 1800, 880, 140), "pillow")
        pen = Ink(canvas, frame, color=INK, width=22.0, prefix="hero.face")
        pen.line((HEAD[0], HEAD[1] + HEAD_R - 6), (HEAD[0] + 4, 1100), "neck", taper=0.0)
        face = Face(eyes=EYES(t), brows=lerp(0.85, 1.0, progress(t, 16.0, 17.9)), mouth="frown",
                    mouth_size=0.6, bags=True)
        draw_head(pen, HEAD, HEAD_R, face, tilt=TILT(t))


# -- the scene ------------------------------------------------------------------------


def draw(canvas, t, frame):
    if t < CLOCK_SHOT:
        shot_bed(canvas, t, frame)
    elif t < FACE_SHOT:
        shot_clock(canvas, t, frame)
    else:
        shot_face(canvas, t, frame)


def overlay(canvas, t, frame):
    """Fade in from black at the very start."""
    dark = 1 - progress(t, 0, FADE_IN, "smooth")
    if dark > 0:
        canvas.drawPaint(skia.Paint(Color=skia.Color(0, 0, 0, int(255 * dark))))


def soundtrack():
    mix = sk.Mix(DURATION)
    hum = sk.pad(["A1", "E2"], DURATION, attack=FADE_IN + 1.0, release=1.0, brightness=0.05, key="hum")
    mix.add(hum, at=0, gain_db=-17, reverb=0.2)
    mix.add(sk.alarm(PRESS - ALARM), at=ALARM, gain_db=-5, reverb=0.12)
    mix.add(sk.tick(key="button"), at=PRESS, gain_db=-6, reverb=0.1)
    mix.add(sk.footstep(0, weight=0.6, key="hand"), at=PRESS - 0.01, gain_db=-12, reverb=0.1)
    return mix
