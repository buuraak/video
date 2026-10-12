"""Film 1, scene 3: the board (row 6 of the story). 10 seconds, two shots joined by a hard cut.
Everything is slow and heavy: he is tired, and he has done this before.

0-3 s    From the side, the wall by the bedroom door. He shuffles in from the left (scene 2 cut as
         he walked out of the bedroom shot), tired, head drooping, and stops in front of the
         whiteboard: NEW ME, the huge goals, START: MONDAY. He lifts his head to it and sags.
3-10 s   The board from the front, filling the screen, long enough to read the goals. His stick arm
         rises slowly from below and takes the red marker from the tray. The marker hovers over
         MONDAY for a moment, then crosses it out in one heavy stroke. He puts it back, takes the
         pale marker, slowly writes TUESDAY under it and puts that back too.
         The caption "I'll start *tomorrow*." comes up as he takes the red marker and stays to the end.

Sound: the hum, his footsteps, the markers clicking on the tray and squeaking on the board.
"""
import math

from scenes.discipline import Discipline
from scenes.door_wall import (GROUND, TRAY_MARKERS, at, cross_line, day_box, draw_board, draw_marker, draw_wall,
                              hero, marker_size)
from toolkit import INK, Camera, Captions, Ink, Track, blink, faces, lerp, progress, reach
from toolkit import sound as sk
from toolkit.text import FADE

DURATION = 10.0
PEAK_DB = -8.0         # set so the hum matches the other scenes (the bar's sound is the loudest moment)
CLOSE_UP = 3.0         # cut to the board

# -- shot 1: he shuffles in -----------------------------------------------------------------

SPEED = 170            # pixels per second while walking (a tired shuffle)
STOP = 2.0             # he has stopped by now...
SLOW = 0.8             # ...after slowing down over this long
STOP_AT = 640          # where his hips stop, in front of the board
STEP = 0.5             # seconds per step
SWING = 0.8            # share of a step the moving foot is in the air
LIFT = 9               # how high a tired foot lifts
START_X = STOP_AT - SPEED * (STOP - SLOW) - SPEED * SLOW / 2

wide_camera = Camera(x=Track((0, 930), (CLOSE_UP, 955, "linear")), zoom=Track((0, 1.0), (CLOSE_UP, 1.06, "linear")),
                     name="board.wide")


def hip_x(t):
    """Walking at SPEED, then slowing to a stop at STOP_AT."""
    slow_from = STOP - SLOW
    if t < slow_from:
        return START_X + SPEED * t
    s = min(t, STOP) - slow_from
    return START_X + SPEED * slow_from + SPEED * s - SPEED * s * s / (2 * SLOW)


def speed(t):
    return SPEED * (1 - progress(t, STOP - SLOW, STOP, "linear"))


def steps():
    """Every step: (lift-off time, landing time, which foot, from x, to x). The film cuts in mid-step."""
    out, plant = [], {"foot_l": hip_x(0) - 40, "foot_r": hip_x(0) + 30}
    k = 0
    while True:
        lift = -0.15 + k * STEP
        land = lift + SWING * STEP
        if lift > STOP - 0.1:
            return out
        foot = ("foot_l", "foot_r")[k % 2]
        moving = speed(land) / SPEED
        ahead = 0.5 * SPEED * STEP            # a step lands a quarter of a stride ahead of his hips...
        stance = 33 if foot == "foot_r" else -33   # ...and as he stops, his feet settle a little apart
        to = hip_x(land) + lerp(stance, ahead, moving)
        out.append((lift, land, foot, plant[foot], to))
        plant[foot] = to
        k += 1


STEPS = steps()


def feet(t):
    """Where his feet are: planted on the floor, or lifting low in a shuffle."""
    where = {}
    for lift, land, foot, a, b in STEPS:
        if t >= land:
            where[foot] = (b, GROUND)
        elif t >= lift:
            u = (t - lift) / (land - lift)
            where[foot] = (lerp(a, b, u * u * (3 - 2 * u)), GROUND - LIFT * math.sin(math.pi * u))
        elif foot not in where:
            where[foot] = (a, GROUND)
    return where


def shot_wide(canvas, t, frame):
    with wide_camera.view(canvas, t):
        draw_wall(canvas, frame, [("MONDAY", 1.0, 0.0)])
        moving = speed(t) / SPEED
        bob = 3 * abs(math.sin(math.pi * (t + 0.15) / STEP)) * moving
        breath = 2.5 * math.sin(2 * math.pi * t / 3.6) * (1 - moving)
        look_up = progress(t, STOP + 0.05, STOP + 0.4)          # he lifts his tired head to the board...
        sag = progress(t, STOP + 0.5, STOP + 1.0)                # ...and sags, as if it weighs on him
        face = faces.TIRED.but(eyes=lerp(0.4, 0.5, look_up) * blink(t, "hero.board", every=2.6))
        pose = hero.stand(hip_x(t), GROUND, face=face, facing=1, lean=lerp(5, 2, look_up),
                          head_tilt=lerp(16, 7, look_up) + 4 * sag, **feet(t))
        pose = pose.but(y=pose.y - bob + breath + 6 * sag)
        # his arms swing a little with his steps, opposite to his legs
        rest = hero.joints(pose)
        swing = 14 * math.sin(math.pi * (t + 0.15) / STEP) * moving
        pose = pose.but(hand_l=(rest["hand_l"][0] - swing, rest["hand_l"][1]),
                        hand_r=(rest["hand_r"][0] + swing, rest["hand_r"][1]))
        hero.draw(canvas, frame, pose)


# -- shot 2: the board, close up --------------------------------------------------------------

CLOSE = (250, 168, 1670, 878)        # the board, filling the screen
BOARD_H = CLOSE[3] - CLOSE[1]
TRAY_Y = CLOSE[3] + 0.03 * BOARD_H
ARM = (780, 760)                     # upper arm and forearm, at close-up size
LONG, THICK = marker_size(BOARD_H)
GRIP = 0.95                          # he holds a marker by its cap end (how far back from its tip, as a share)
BODY = (250, 1250)                   # roughly where his shoulder is, out of the picture

close_camera = Camera(zoom=Track((CLOSE_UP, 1.0), (DURATION, 1.03, "linear")), name="board.close")


def on_tray(colour):
    """Where a marker's tip is while it lies on the tray (it points right)."""
    x = at(CLOSE, TRAY_MARKERS[colour], 1.0)[0] - 0.09 * BOARD_H
    return (x, TRAY_Y - 0.03 * BOARD_H)


MONDAY_A, MONDAY_B = cross_line(CLOSE, 0, "MONDAY")
TUE_X, TUE_Y, TUE_W, TUE_PX = day_box(CLOSE, 1, "TUESDAY")
TUE_START = (TUE_X + 0.02 * TUE_PX, TUE_Y - 0.4 * TUE_PX)

ARM_IN = 3.8           # his arm rises slowly from below...
GRAB_RED = 4.55        # ...takes the red marker
HOVER = 5.2            # holds it over MONDAY for a moment...
CROSS = (5.65, 6.25)   # ...then crosses it out in one heavy stroke
PUT_RED = 6.75         # puts it back
GRAB_PALE = 7.05       # takes the pale one
WRITE = (7.45, 9.0)    # slowly writes TUESDAY
PUT_PALE = 9.4         # puts it back
ARM_OUT = 9.85         # and his arm drops away

# The caption comes up as he takes the red marker and stays fully up until the cut.
captions = Captions([(GRAB_RED, DURATION + FADE, "I'll start *tomorrow*.")])

# Where the marker tip (or, without a marker, the point it would be) goes, and how flat the
# marker lies (1 = lying on the tray, 0 = held in line with his forearm).
TIP = Track((ARM_IN, (1260, 1140)), (GRAB_RED, on_tray("red"), "out"),
            (HOVER, (MONDAY_A[0] - 14, MONDAY_A[1] - 10), "inout"),
            (CROSS[0], MONDAY_A, "inout"), (CROSS[1], MONDAY_B, "inout"),
            (PUT_RED, on_tray("red"), "inout"), (GRAB_PALE, on_tray("pale"), "inout"),
            (WRITE[0], TUE_START, "inout"))
TIP_AFTER = Track((WRITE[1], (TUE_X + TUE_W, TUE_START[1])), (PUT_PALE, on_tray("pale"), "inout"),
                  (ARM_OUT, (1560, 1180), "in"))
FLAT = Track((ARM_IN, 0.5), (GRAB_RED - 0.2, 1.0), (GRAB_RED, 1.0), (GRAB_RED + 0.3, 0.0, "inout"),
             (PUT_RED - 0.3, 0.0), (PUT_RED, 1.0, "out"), (GRAB_PALE, 1.0), (GRAB_PALE + 0.3, 0.0, "inout"),
             (PUT_PALE - 0.3, 0.0), (PUT_PALE, 1.0, "out"), (ARM_OUT, 0.6))


def writing(t):
    """0..1: how much of TUESDAY is written."""
    return progress(t, *WRITE, "linear")


def tip_at(t):
    if t < WRITE[0]:
        return TIP(t)
    if t < WRITE[1]:          # writing: along the word, the pen bobbing up and down with the letters
        u = writing(t)
        return (TUE_X + TUE_W * u + 0.06 * TUE_PX * math.sin(2 * math.pi * 9 * u + 1.0),
                TUE_START[1] + 0.3 * TUE_PX * math.sin(2 * math.pi * 9 * u))
    return TIP_AFTER(t)


def held(t):
    """Which marker is in his hand, if any."""
    if GRAB_RED <= t < PUT_RED:
        return "red"
    if GRAB_PALE <= t < PUT_PALE:
        return "pale"
    return None


def shoulder_for(hand):
    """His shoulder, below the bottom left of the picture (he stands left of the board, as in the
    wide shot); his body leans a little toward where his hand goes."""
    return (BODY[0] + 0.3 * (hand[0] - 1300), BODY[1] + 0.3 * (hand[1] - 600))


def arm(t):
    """(shoulder, elbow, hand, marker angle in degrees) for the arm at time t."""
    tip = tip_at(t)
    flat = FLAT(t)
    angle = math.degrees(math.atan2(tip[1] - BODY[1], tip[0] - BODY[0]))   # first guess: from his body
    for _ in range(3):                                                   # settle in line with the forearm
        a = math.radians(angle)
        hand = (tip[0] - GRIP * LONG * math.cos(a), tip[1] - GRIP * LONG * math.sin(a))
        shoulder = shoulder_for(hand)
        elbow, hand, _ = reach(shoulder, hand, *ARM, 1)
        forearm = math.degrees(math.atan2(hand[1] - elbow[1], hand[0] - elbow[0]))
        angle = lerp(forearm, 0.0, flat)
    a = math.radians(angle)
    hand = (tip[0] - GRIP * LONG * math.cos(a), tip[1] - GRIP * LONG * math.sin(a))
    shoulder = shoulder_for(hand)
    elbow, hand, _ = reach(shoulder, hand, *ARM, 1)
    return shoulder, elbow, hand, angle


def shot_close(canvas, t, frame):
    with close_camera.view(canvas, t):
        in_hand = held(t)
        crossed = progress(t, *CROSS)
        days = [("MONDAY", 1.0, crossed), ("TUESDAY", writing(t), 0.0)]
        draw_board(canvas, frame, CLOSE, days, on_tray=[c for c in ("red", "pale") if c != in_hand])
        if not ARM_IN <= t < ARM_OUT:
            return
        shoulder, elbow, hand, angle = arm(t)
        if in_hand:
            draw_marker(canvas, frame, tip_at(t), angle, BOARD_H, in_hand)
        pen = Ink(canvas, frame, color=INK, width=30.0, prefix="hero.closeup")
        beyond = (shoulder[0] + 0.6 * (shoulder[0] - elbow[0]), shoulder[1] + 0.6 * (shoulder[1] - elbow[1]))
        pen.line(beyond, elbow, "upper_arm", pin_ends=True, taper=0.0)     # runs on off screen
        pen.line(elbow, hand, "forearm", pin_ends=True, taper=0.1)


# -- the scene -------------------------------------------------------------------------------------


def draw(canvas, t, frame):
    if t < CLOSE_UP:
        shot_wide(canvas, t, frame)
    else:
        shot_close(canvas, t, frame)


bar = Discipline(flickers=[CROSS[1] - 0.1])  # empty: a red flicker as he finishes crossing out MONDAY


def overlay(canvas, t, frame):
    bar.draw(canvas, t, frame)
    captions.draw(canvas, t)


def soundtrack():
    mix = sk.Mix(DURATION)
    mix.add(sk.pad(["A1", "E2"], DURATION, attack=0.4, release=1.0, brightness=0.05, key="hum"),
            at=0, gain_db=-17, reverb=0.2)
    for n, (lift, land, foot, a, b) in enumerate(STEPS):                 # his shuffling feet
        if 0 <= land < CLOSE_UP:
            mix.add(sk.footstep(n, weight=0.45, key="board.step"), at=land, gain_db=-13,
                    pan=(b - 960) / 1400, reverb=0.12)
    mix.add(sk.whoosh(0.5, peak=0.6, low=150, high=700, key="board.arm"), at=ARM_IN, gain_db=-24, reverb=0.1)
    def effect(prompt, seconds, name):            # ElevenLabs effects, all brought to the same level first
        return sk.normalize(sk.eleven_sound(prompt, seconds, name))

    tray = effect("A plastic marker pen put down on a whiteboard's metal tray, one small light click", 0.5,
                  "marker_tray")
    for i, at_ in enumerate((GRAB_RED, PUT_RED, GRAB_PALE, PUT_PALE)):
        mix.add(tray, at=at_ - 0.2, gain_db=-20 - 2 * (i % 2), pan=0.2, reverb=0.08)
    cross = effect("Close-up of one quick squeaky stroke of a dry-erase marker across a whiteboard, "
                   "crossing out a word", 0.8, "marker_cross")
    mix.add(sk.fade_edges(cross[:int((CROSS[1] - CROSS[0] + 0.08) * sk.SR)], 0.005, 0.06), at=CROSS[0],
            gain_db=-15, pan=0.2, reverb=0.08)
    write = effect("Close-up of someone slowly writing one word on a whiteboard with a dry-erase marker, "
                   "slow squeaky strokes", 2.0, "marker_write")
    mix.add(sk.fade_edges(write[:int((WRITE[1] - WRITE[0] + 0.1) * sk.SR)], 0.005, 0.08), at=WRITE[0],
            gain_db=-14, pan=0.2, reverb=0.08)
    bar.add_sounds(mix)
    return mix
