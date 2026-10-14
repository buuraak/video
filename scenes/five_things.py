"""Film 1, row 22 of the story: five things. About 12.5 seconds: one shot, then jump cuts as the list grows.
It follows row 21, where he wiped the whole board clean. Still night, faintly red from the clock.

 0-6.2 s     The clean board, closer on its top left. His arm comes up from the bottom left with the pale
             marker and writes TODAY where NEW ME was, then draws the first empty box and writes, letter by
             letter, carefully: Get up when the alarm rings.
 6.2-8.9 s   Jump cuts as the list grows, each landing on the next line being finished: Clean your room /
             Go for a walk / Write 3 lines.
 8.9-12.5 s  The last line, Text one person, finished; he puts the marker back, his arm drops away, and the
             camera pulls back to hold on the whole list: TODAY and five easy things, five empty boxes.

No caption. Sound: the marker squeaking on the board, its click on the tray; otherwise silence.
"""
import math

import numpy as np
import skia

import scenes.new_goals as goals
from scenes import wipe
from scenes.discipline import Discipline
from scenes.door_wall import FIVE, TODAY, box_point, draw_board, draw_marker, draw_today, five_text, \
    word_box
from scenes.new_goals import squeaks
from scenes.scroll import glow
from scenes.the_board import ARM, BOARD_H, CLOSE, GRIP, LONG, on_tray
from toolkit import INK, RED, Camera, Ink, Track, lerp, progress, reach, to_color
from toolkit import sound as sk
from toolkit.rng import rng

PEAK_DB = -12.6          # set so the marker sits at the same level as the sounds in the other scenes
BOARD = dict(wiped=goals.wiped(goals.DURATION), new_goals=goals.written(goals.DURATION),
             cleaned=wipe.cleaned(wipe.DURATION))           # the board as row 21 left it: wiped clean
DAYS = wipe.DAYS
DARKNESS, CLOCK_LIGHT = wipe.DARKNESS, wipe.CLOCK_LIGHT

# -- what he writes, in story time (the jump cuts skip parts of it) -----------------------------------

ARM_IN = 0.5           # his arm rises with nothing in his hand...
GRAB = 1.1             # ...takes the pale marker from the tray
PER_LETTER = 0.11      # carefully
TODAY_LETTERS = 0.14   # TODAY, more carefully still
TODAY_WRITE = (GRAB + 1.0, GRAB + 1.0 + TODAY_LETTERS * len("TODAY"))   # up from the tray, unhurried
TO_BOX, BOX, TO_WORDS = 0.2, 0.5, 0.15


def schedule():
    """For each easy thing: (box start, box end, words start, words end). Going back across the board to the next
    box takes longer after a long line."""
    out, t = [], TODAY_WRITE[1]
    end = word_box(CLOSE, "TODAY", *TODAY)
    for i, text in enumerate(FIVE):
        box0 = t + TO_BOX + math.dist((end[0] + end[2], end[1]), box_point(CLOSE, i, 0.0)) / 1500
        end = five_text(CLOSE, i)
        words0 = box0 + BOX + TO_WORDS
        words1 = words0 + PER_LETTER * len(text)
        out.append((box0, box0 + BOX, words0, words1))
        t = words1
    return out


ITEMS = schedule()
PUT = ITEMS[-1][3] + 0.7       # he puts the marker back...
ARM_OUT = PUT + 0.45           # ...and his arm drops away

# -- the jump cuts: (picture time it starts, story time it shows) ----------------------------------------

SHOT_A = 0.0
CUT_B = ITEMS[0][3] + 0.25                 # after the first thing, cut...
CUTS = [(SHOT_A, 0.0), (CUT_B, ITEMS[1][3] - 0.75)]
for k in (2, 3):                           # ...to each next line being finished
    CUTS.append((CUTS[-1][0] + 0.9, ITEMS[k][3] - 0.75))
CUT_E = CUTS[-1][0] + 0.9
CUTS.append((CUT_E, ITEMS[4][3] - 0.9))
PULL_BACK = (CUT_E + 1.2, CUT_E + 3.0)
DURATION = round(PULL_BACK[1] + 0.9, 2)


def shot(t):
    """Which shot is on screen at picture time t."""
    return max(k for k, (t0, _) in enumerate(CUTS) if t >= t0)


def story(t):
    t0, s0 = CUTS[shot(t)]
    return s0 + (t - t0)


def picture(s):
    """When story time s is on screen (None if a jump cut skips it)."""
    for k, (t0, s0) in enumerate(CUTS):
        t1 = CUTS[k + 1][0] if k + 1 < len(CUTS) else DURATION
        if s0 <= s < s0 + (t1 - t0):
            return t0 + (s - s0)
    return None


# -- the pen ------------------------------------------------------------------------------------------


def _along(text_box, u, letters):
    """The pen's tip partway (u) along a word being written, bobbing up and down with the letters."""
    x, y, w, px = text_box
    return (x + w * u + 0.06 * px * math.sin(2 * math.pi * letters * u + 1.0),
            y - 0.4 * px + 0.3 * px * math.sin(2 * math.pi * letters * u))


def _start(text_box):
    x, y, w, px = text_box
    return (x, y - 0.4 * px)


def _end(text_box):
    x, y, w, px = text_box
    return (x + w, y - 0.4 * px)


TODAY_BOX = word_box(CLOSE, "TODAY", *TODAY)


def pen_tip(s):
    """Where the pale marker's tip is, at story time s, while he holds it."""
    if s < TODAY_WRITE[0]:
        return lerp(on_tray("pale"), _start(TODAY_BOX), progress(s, GRAB, TODAY_WRITE[0], "inout"))
    if s < TODAY_WRITE[1]:
        return _along(TODAY_BOX, progress(s, *TODAY_WRITE, "linear"), len("TODAY") + 1)
    before = _end(TODAY_BOX)
    for i, (box0, box1, words0, words1) in enumerate(ITEMS):
        words = five_text(CLOSE, i)
        if s < box0:
            leave = ITEMS[i - 1][3] if i else TODAY_WRITE[1]
            return lerp(before, box_point(CLOSE, i, 0.0), progress(s, leave, box0, "inout"))
        if s < box1:
            return box_point(CLOSE, i, progress(s, box0, box1, "linear"))
        if s < words0:
            return lerp(box_point(CLOSE, i, 1.0), _start(words), progress(s, box1, words0, "inout"))
        if s < words1:
            return _along(words, progress(s, words0, words1, "linear"), len(FIVE[i]) + 1)
        before = _end(words)
    return lerp(before, on_tray("pale"), progress(s, ITEMS[-1][3], PUT, "inout"))


def shoulder_for(hand):
    return wipe.shoulder_for(hand)       # he still stands left of the middle of the board, as he wiped it


def holding_tip(tip, flat=0.0):
    """His arm from the bottom left holding the pale marker with its tip at `tip`, the marker in line with his
    forearm (flat: 1 while it lies flat on the tray). Returns (shoulder, elbow, hand, marker angle)."""
    angle = 0.0
    for _ in range(3):
        a = math.radians(angle)
        hand = (tip[0] - GRIP * LONG * math.cos(a), tip[1] - GRIP * LONG * math.sin(a))
        elbow, hand, _ = reach(shoulder_for(hand), hand, *ARM, 1)
        angle = lerp(math.degrees(math.atan2(hand[1] - elbow[1], hand[0] - elbow[0])), 0.0, flat)
    a = math.radians(angle)
    hand = (tip[0] - GRIP * LONG * math.cos(a), tip[1] - GRIP * LONG * math.sin(a))
    shoulder = shoulder_for(hand)
    elbow, hand, _ = reach(shoulder, hand, *ARM, 1)
    return shoulder, elbow, hand, angle


def draw_arm(canvas, frame, shoulder, elbow, hand):
    """His stick arm in the board close-up, running on off the bottom of the picture."""
    pen = Ink(canvas, frame, color=INK, width=30.0, prefix="hero.closeup")
    beyond = (shoulder[0] + 0.6 * (shoulder[0] - elbow[0]), shoulder[1] + 0.6 * (shoulder[1] - elbow[1]))
    pen.line(beyond, elbow, "upper_arm", pin_ends=True, taper=0.0)
    pen.line(elbow, hand, "forearm", pin_ends=True, taper=0.1)


def arm(s):
    """(shoulder, elbow, hand, marker angle) at story time s, or None while his arm is out of the picture."""
    if not ARM_IN <= s < ARM_OUT:
        return None
    grip = (on_tray("pale")[0] - GRIP * LONG, on_tray("pale")[1])
    if GRAB <= s < PUT:                              # holding the marker
        flat = 1 - progress(s, GRAB, GRAB + 0.3, "inout") + progress(s, PUT - 0.3, PUT, "inout")
        return holding_tip(pen_tip(s), flat)
    if s < GRAB:                                     # rising from below to the marker
        hand = lerp((520, 1150), grip, progress(s, ARM_IN, GRAB, "out"))
    else:                                            # dropping away
        hand = lerp(grip, (700, 1180), progress(s, PUT, ARM_OUT, "in"))
    shoulder = shoulder_for(hand)
    elbow, hand, _ = reach(shoulder, hand, *ARM, 1)
    return shoulder, elbow, hand, 0.0


def holding(s):
    return GRAB <= s < PUT


def written(s):
    """(TODAY, boxes, lines): how much of each is written by story time s."""
    boxes = [progress(s, a, b, "linear") for a, b, _, _ in ITEMS if s >= a]
    lines = [progress(s, a, b, "linear") for _, _, a, b in ITEMS if s >= a]
    return progress(s, *TODAY_WRITE, "linear"), boxes, lines


# -- the cameras: one per shot -----------------------------------------------------------------------


def _line_camera(k, center, zoom, name):
    t0 = CUTS[k][0]
    t1 = CUTS[k + 1][0] if k + 1 < len(CUTS) else DURATION
    return Camera(x=Track((t0, center[0]), (t1, center[0] + 8, "linear")), y=Track((t0, center[1]), (t1, center[1])),
                  zoom=Track((t0, zoom), (t1, zoom + 0.03, "linear")), name=name)


# Each shot's top edge falls between two lines of writing, so no word is cut in half.
CAMERAS = [_line_camera(0, (820, 430), 1.25, "five.a"),
           _line_camera(1, (700, 480), 1.35, "five.b"),
           _line_camera(2, (660, 610), 1.33, "five.c"),
           _line_camera(3, (700, 640), 1.38, "five.d"),
           Camera(x=Track((CUT_E, 740), (PULL_BACK[0], 746, "linear"), (PULL_BACK[1], 960, "inout")),
                  y=Track((CUT_E, 634), (PULL_BACK[0], 632, "linear"), (PULL_BACK[1], 523, "inout")),
                  zoom=Track((CUT_E, 1.3), (PULL_BACK[0], 1.32, "linear"), (PULL_BACK[1], 1.0, "inout"),
                             (DURATION, 0.99, "linear")), name="five.e")]


def draw(canvas, t, frame):
    s = story(t)
    with CAMERAS[shot(t)].view(canvas, t):
        tray = ["eraser", "red"] + ([] if holding(s) else ["pale"])
        draw_board(canvas, frame, CLOSE, DAYS, key="board", on_tray=tray, **BOARD)
        today, boxes, lines = written(s)
        draw_today(canvas, frame, CLOSE, today, boxes, lines)
        a = arm(s)
        if a is not None:
            shoulder, elbow, hand, angle = a
            if holding(s):
                draw_marker(canvas, frame, pen_tip(s), angle, BOARD_H, "pale", "board")
            draw_arm(canvas, frame, shoulder, elbow, hand)
        canvas.drawPaint(skia.Paint(Color=to_color((4, 3, 5, int(255 * DARKNESS)))))
        glow(canvas, CLOCK_LIGHT, 1400, RED, 0.12)


bar = Discipline()  # still empty: writing a plan isn't doing it


def overlay(canvas, t, frame):
    bar.draw(canvas, t, frame)


def soundtrack():
    mix = sk.Mix(DURATION)
    tray = sk.normalize(sk.eleven_sound("A plastic marker pen put down on a whiteboard's metal tray, one small light "
                                        "click", 0.5, "marker_tray"))
    for s in (GRAB, PUT):
        t = picture(s - 0.2)
        if t is not None:
            mix.add(tray, at=t, gain_db=-20, pan=-0.2, reverb=0.08)
    # the marker: a squeak about every other letter, and one on each side of a box, wherever the picture shows it
    grains = squeaks()
    g = rng("five.squeak")
    strokes = [TODAY_WRITE[0] + (j + 0.3) * TODAY_LETTERS for j in range(0, 5, 2)]
    for i, (box0, box1, words0, words1) in enumerate(ITEMS):
        strokes += [box0 + (k + 0.3) * (box1 - box0) / 4 for k in range(4)]
        n = len(FIVE[i])
        strokes += [words0 + (j + 0.25 + g.uniform(-0.2, 0.2)) * PER_LETTER for j in range(0, n, 2)
                    if g.random() > 0.15]
    for s in strokes:
        t = picture(s)
        if t is not None:
            mix.add(grains[g.integers(len(grains))], at=t, gain_db=-16 + g.uniform(-3, 0), pan=-0.15, reverb=0.08)
    return mix
