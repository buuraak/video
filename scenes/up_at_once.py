"""Film 1, row 9 of the story: up at once. About 5 seconds, two shots joined by a hard cut.
It follows the reset (row 8), where the alarm went off at 6:00 and kept ringing.

0-1.15 s   Still on the alarm clock from the front, beeping, the numbers blinking. His stick arm shoots in
           from the right and slams the button, hard and at once: the opposite of scene 1's slow, heavy
           press. The beeping stops; the clock jolts.
1.15-1.65 s From above, the opening view: 6:00, the phone dark on its charger. He lies with his eyes wide
           open and a determined face, and takes a sharp breath in.
1.65-4.95 s He throws the blanket off, sits up, shuffles across the empty half, swings out on the right,
           stands and walks briskly out to the right: the same moves as scene 2, about twice as fast.

Sound: the alarm, the slam on the button, the blanket, his quick steps, the hum.
"""
import math

import numpy as np

import scenes.scroll as scroll
from scenes.bedroom import (HERO_X, HIP_Y, ROOM, belly_hands, box, clock_numbers, draw_bed, draw_blanket,
                            draw_nightstand, hero, rounded_rect, smooth)
from scenes.discipline import Discipline
from scenes.wake_up import ARM, BUTTON, BUTTON_DOWN, CLOCK, TABLE, WINDOW
from toolkit import INK, Camera, Face, Ink, Pose, Track, clamp, progress, reach
from toolkit import sound as sk

DURATION = 4.95
PEAK_DB = -2.2         # set so the hum (and the alarm, carrying on from the reset) match the other scenes
ABOVE = 1.15           # cut from the clock to the view from above
RINGING = 1.45         # the alarm has been ringing this long when the scene starts (it began in the reset)
SLAM = 0.70            # his arm hits the button two beeps into a burst: the beeping stops
THROW = 1.65           # he grabs the blanket and throws it off
SIT, SCOOT, SWING, STAND, WALK = 2.15, 2.55, 3.0, 3.35, 3.6   # the same moves as scene 2, about twice as fast
FASTER = 1.7           # and he walks this much faster than in scene 2

# -- shot 1: he slams the alarm off ------------------------------------------------------------

# The reset's camera carries on (same wobble, its time running on from the reset's end), so the cut between
# the two scenes doesn't jump.
RESET_END = 4.0
clock_camera = Camera(zoom=1.075, name="reset")
clock_camera.shake(at=RESET_END + SLAM, strength=0.8, length=0.4)
ON_BUTTON = (1255, BUTTON[1] - 12)
# Where the end of his arm is: in from the right, fast, and straight down onto the button. His shoulder is
# lower than in scene 1 (he's lying flat, about to spring up), which keeps the elbow well inside the picture.
SHOULDER = (740, 220)  # from the end of his arm
ARM_END = Track((0.3, (1990, 360)), (0.6, (1262, 300), "out"), (SLAM, ON_BUTTON, "in"),
                (SLAM + 0.05, (ON_BUTTON[0], ON_BUTTON[1] + BUTTON_DOWN), "out"))
DIP = Track((SLAM, 0.0), (SLAM + 0.05, 7.0, "out"), (SLAM + 0.35, 0.0, "inout"))


def lit(t):
    """The numbers blink with the beeps until he hits the button."""
    if t < SLAM:
        return 1.0 if sk.alarm_on(t + RINGING) else 0.0
    return 1.0


def shot_clock(canvas, t, frame):
    with clock_camera.view(canvas, RESET_END + t):
        ink = Ink(canvas, frame, color=ROOM, width=8.0, prefix="clock")
        ink.floor(TABLE, key="table", width=6.0)
        ink.floor(TABLE + 22, key="table.front", width=5.0)
        canvas.save()
        canvas.translate(0, DIP(t))
        pressed = BUTTON_DOWN * progress(t, SLAM, SLAM + 0.05, "out")
        box(ink, rounded_rect(BUTTON[0], BUTTON[1] + pressed, BUTTON[2], BUTTON[3] + 6, 12), "button", width=7.0)
        box(ink, rounded_rect(*CLOCK, 84), "body", width=9.0)
        box(ink, rounded_rect(*WINDOW, 44), "window", width=6.0)
        clock_numbers(canvas, frame, "6:00", ((WINDOW[0] + WINDOW[2]) / 2, (WINDOW[1] + WINDOW[3]) / 2 + 2), 320,
                      "clock.big", on=lit(t))
        canvas.restore()
        if t >= ARM_END.keys[0][0]:
            end = ARM_END(t)
            shoulder = (end[0] + SHOULDER[0], end[1] + SHOULDER[1])
            elbow, end, _ = reach(shoulder, end, *ARM, 1)
            pen = Ink(canvas, frame, color=INK, width=30.0, prefix="hero.closeup")
            beyond = (shoulder[0] + 0.6 * (shoulder[0] - elbow[0]), shoulder[1] + 0.6 * (shoulder[1] - elbow[1]))
            pen.line(beyond, elbow, "upper_arm", pin_ends=True, taper=0.0)     # runs on off screen
            pen.line(elbow, end, "forearm", pin_ends=True, taper=0.1)


# -- shot 2: from above, up and out ----------------------------------------------------------------

bed_camera = Camera(name="up.bed")
DETERMINED = Face(eyes=0.92, brows=-0.6, mouth="frown", mouth_size=0.0, bags=True)
# a sharp breath in before he moves, then quick breathing
BREATH = Track((ABOVE, 0.0), (1.45, 1.1, "out"), (THROW, 0.6), (SIT, 0.2))

# Scene 2's getting-up moves, played on a faster clock: our time -> scene 2's time.
_KEYS = [(SIT, scroll.SIT), (SCOOT, scroll.SCOOT), (SWING, scroll.SWING), (STAND, scroll.STAND), (WALK, scroll.WALK)]


def scene2_time(t):
    if t >= WALK:
        return scroll.WALK + FASTER * (t - WALK)
    return float(np.interp(t, [a for a, _ in _KEYS], [b for _, b in _KEYS]))


def our_time(t2):
    """The other way round: when a moment of scene 2's walk happens here."""
    if t2 >= scroll.WALK:
        return WALK + (t2 - scroll.WALK) / FASTER
    return float(np.interp(t2, [b for _, b in _KEYS], [a for a, _ in _KEYS]))


# His right hand grabs the blanket low on the empty side and flings it across his belly toward the
# nightstand, in one smooth curve. Routed low, the elbow stays down by his side, never up by his face,
# and never snaps over as the hand passes under his shoulder.
GRAB, ACROSS, END = (1095, 540), (950, 630), (800, 580)
FLING = (THROW - 0.2, SIT - 0.1)


def _fling_path(rest):
    pts = np.array(smooth([rest, GRAB, ACROSS, END, (840, 560)], per_segment=30))
    along = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(pts, axis=0).T))])
    along /= along[-1]
    share = [along[np.argmin(np.hypot(*(pts - p).T))] for p in (GRAB, END)]
    return pts, along, share


def fling(t, rest):
    """Where his right hand is, and how far the blanket has been thrown (0..1)."""
    pts, along, (grab, end) = _fling_path(rest)
    s = progress(t, *FLING, "inout")
    hand = (float(np.interp(s, along, pts[:, 0])), float(np.interp(s, along, pts[:, 1])))
    return hand, progress(s, grab, end)


def lying_pose(t):
    """Lying, determined, hands on his belly; then the fling. Returns (pose, breath, blanket thrown)."""
    b = BREATH(t)
    pose = Pose(x=HERO_X, y=HIP_Y - 3 * b)
    left, right = belly_hands(hero.joints(pose)["shoulder"], max(b, 0))
    thrown = 0.0
    if t >= FLING[0]:
        right, thrown = fling(t, right)
    return pose.but(hand_l=left, hand_r=right), b, thrown


_lying_end = None


def lying_end():
    global _lying_end
    if _lying_end is None:
        _lying_end = hero.skeleton(lying_pose(SIT)[0])
    return _lying_end


def shot_bed(canvas, t, frame):
    with bed_camera.view(canvas, t):
        room = Ink(canvas, frame, color=ROOM, width=4.0, prefix="bedroom")
        draw_bed(room)
        draw_nightstand(room, canvas, frame, time="6:00")
        if t < SIT:      # lying: body, then the blanket over it, then the face and his arms on top
            pose, b, thrown = lying_pose(t)
            j = hero.skeleton(pose, frame)
            pen = scroll.draw_body(canvas, frame, j, ("legs", "spine", "head"), hero.head_r)
            draw_blanket(room, b, thrown)
            scroll.draw_his_face(canvas, pen, j["head"], hero.head_r, DETERMINED, 0.0, 0.0, 0.0)
            scroll.draw_body(canvas, frame, j, ("arms",), hero.head_r)
        else:            # getting up, seen from above: his head is on top of everything else
            j, head_r, away = scroll.getting_up(scene2_time(t), lying_end())
            draw_blanket(room, 0.0, 1.0)
            pen = scroll.draw_body(canvas, frame, j, ("legs", "arms", "spine", "head"), head_r)
            scroll.draw_his_face(canvas, pen, j["head"], head_r, DETERMINED, 0.0, 0.0, away)


# -- the scene ---------------------------------------------------------------------------------------


def draw(canvas, t, frame):
    if t < ABOVE:
        shot_clock(canvas, t, frame)
    else:
        shot_bed(canvas, t, frame)


bar = Discipline(fills=[STAND])  # +1 the moment he's up on his feet


def overlay(canvas, t, frame):
    bar.draw(canvas, t, frame)


def soundtrack():
    mix = sk.Mix(DURATION)
    mix.add(sk.pad(["A1", "E2"], DURATION, attack=0.4, release=1.0, brightness=0.05, key="hum"),
            at=0, gain_db=-17, reverb=0.2)
    # the alarm carries on from the reset, in step with its beeps, until he hits it
    ringing = sk.alarm(RINGING + SLAM)[int(RINGING * sk.SR):]
    mix.add(ringing, at=0, gain_db=-5, reverb=0.12)
    mix.add(sk.tick(key="up.button"), at=SLAM, gain_db=-4, reverb=0.1)
    mix.add(sk.thud(0.5, key="up.slam"), at=SLAM, gain_db=-12, reverb=0.12)
    mix.add(sk.whoosh(0.25, peak=0.6, low=200, high=1200, key="up.arm"), at=SLAM - 0.3, gain_db=-20)
    mix.add(sk.whoosh(0.45, peak=0.4, low=180, high=1400, key="up.blanket"), at=THROW + 0.1, gain_db=-12, reverb=0.15)
    mix.add(sk.whoosh(0.5, peak=0.5, low=150, high=900, key="up.sit"), at=SIT, gain_db=-18, reverb=0.15)
    for i, (a, _) in enumerate(scroll.PUSHES):
        mix.add(sk.whoosh(0.25, peak=0.4, low=150, high=800, key=("up.scoot", i)), at=our_time(a), gain_db=-20,
                reverb=0.1)
    mix.add(sk.footstep(9, weight=0.6, key="up.floor"), at=our_time(scroll.STAND + 0.35), gain_db=-13, pan=0.35,
            reverb=0.1)
    for n, (at, x) in enumerate(scroll.footstep_times()):
        pan = clamp((x - 960) / 960, -1, 1)
        fade = -6 * clamp((x - 1800) / 200)
        mix.add(sk.footstep(n, weight=0.8, key="up.step"), at=our_time(at), gain_db=-10 + fade, pan=pan, reverb=0.12)
    bar.add_sounds(mix)
    return mix
