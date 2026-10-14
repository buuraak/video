"""Film 1, row 21 of the story: the wipe. About 14 seconds, one shot. It follows row 20, where he sat on the floor,
breathed out, and lifted his head to the board again. Still night, faintly red from the clock.

 0-2.5 s     The board close up, the wall of red. His arm comes up from the bottom left (he sat left of the
             board), takes the eraser from the tray and sets it on the top left corner. A moment.
 2.5-10.6 s  He wipes the whole board clean, NEW ME too, line by line from the top: the first strokes slow
             and heavy, then steadier and quicker as the red goes. A faint smear stays.
 10.4-14.2 s He puts the eraser back and his arm drops away; the camera slowly pulls back to the clean board
             in the dark.

No caption. Sound: the eraser, its knocks on the tray, and otherwise silence (the hum is still gone).
"""
import math

import numpy as np
import skia

import scenes.new_goals as goals
from scenes.discipline import Discipline
from scenes.door_wall import at, day_names, draw_board, draw_eraser, eraser_on_tray, eraser_size
from scenes.scroll import glow
from scenes.the_board import ARM, BOARD_H, CLOSE
from toolkit import INK, RED, Camera, Ink, Track, lerp, progress, reach, to_color
from toolkit import sound as sk

PEAK_DB = -12.9          # set so the eraser sits at the same level as the sounds in the other scenes
BOARD = dict(wiped=goals.wiped(goals.DURATION), new_goals=goals.written(goals.DURATION))
DAYS = [(name, 1.0, 1.0) for name in day_names(29)]       # the full board, as row 18 left it
BOARD_W = CLOSE[2] - CLOSE[0]
ER_LONG, ER_HIGH = eraser_size(BOARD_H)
DARKNESS = 0.5
CLOCK_LIGHT = (-300, 500)       # the red clock is off to the left, as in row 20

# -- the wipe ---------------------------------------------------------------------------------------

ARM_IN = 0.8           # after a moment on the board, his arm rises...
GRAB = 1.6             # ...and takes the eraser from the tray
ON_BOARD = 2.2         # it reaches the top left corner...
WIPE_START = 2.5       # ...rests there a moment, and he starts
ROWS = [0.1 + 0.1 * k for k in range(9)]                       # the middle of each stroke, top to bottom
SWEEPS = [1.1, 0.95, 0.85, 0.76, 0.7, 0.65, 0.62, 0.6, 0.6]   # slow and heavy, then steadier and quicker
DOWN = 0.16                                                    # down to the next line
SWEEP_U = (0.075, 0.925)                                       # where the eraser's middle runs, edge to edge


def wipe_path():
    """The eraser's moves while it wipes: (start time, end time, from (u, v), to (u, v))."""
    out, t = [], WIPE_START
    for i, (v, sweep) in enumerate(zip(ROWS, SWEEPS)):
        a, b = SWEEP_U if i % 2 == 0 else SWEEP_U[::-1]
        out.append((t, t + sweep, (a, v), (b, v)))
        t += sweep
        if i < len(ROWS) - 1:
            out.append((t, t + DOWN, (b, v), (b, ROWS[i + 1])))
            t += DOWN
    return out


WIPES = wipe_path()
WIPE_END = WIPES[-1][1]
PUT = WIPE_END + 0.7               # he puts the eraser back on the tray...
ARM_OUT = PUT + 0.45               # ...and his arm drops away
PULL_BACK = (WIPE_END - 0.2, WIPE_END + 2.6)
DURATION = round(PULL_BACK[1] + 1.0, 2)


def eraser_box(uv):
    """The area the eraser's felt covers, in board measurements, with its middle at uv."""
    du, dv = ER_LONG / 2 / BOARD_W, ER_HIGH / 2 / BOARD_H
    return (uv[0] - du, uv[1] - dv, uv[0] + du, uv[1] + dv)


def cleaned(t):
    """Everything the eraser has wiped by time t (a little taller than the felt, so neighbouring strokes
    overlap and nothing is left between them)."""
    out = []
    for t0, t1, a, b in WIPES:
        if t <= t0:
            break
        now = lerp(a, b, progress(t, t0, t1, "inout"))
        ba, bn = eraser_box(a), eraser_box(now)
        out.append((min(ba[0], bn[0]), min(ba[1], bn[1]) - 0.02, max(ba[2], bn[2]), max(ba[3], bn[3]) + 0.02))
    return out


def eraser_at(t):
    """Where the eraser's middle is while it's in his hand."""
    rest = eraser_on_tray(CLOSE)
    first = at(CLOSE, *WIPES[0][2])
    if t < WIPE_START:
        return lerp(rest, first, progress(t, GRAB, ON_BOARD, "inout"))
    for t0, t1, a, b in WIPES:
        if t < t1:
            p = at(CLOSE, *lerp(a, b, progress(t, t0, t1, "inout")))
            return (p[0], p[1] + 0.004 * BOARD_H * math.sin(2 * math.pi * 7 * (t - t0)))   # scrubbing
    return lerp(at(CLOSE, *WIPES[-1][3]), rest, progress(t, WIPE_END, PUT, "inout"))


def shoulder_for(hand):
    """His shoulder, well below the picture; to wipe the whole board he shifts along it with his hand. Low
    enough that his arm reaches up almost straight to the top of the board, and bends below the picture
    lower down."""
    return (0.5 * hand[0] + 100, 1560)


def hand_at(t):
    """Where the end of his arm is: on top of the eraser while he holds it."""
    top = lambda e: (e[0], e[1] - ER_HIGH / 2)      # noqa: E731
    if t < GRAB:
        return lerp((520, 1150), top(eraser_on_tray(CLOSE)), progress(t, ARM_IN, GRAB, "out"))
    if t < PUT:
        return top(eraser_at(t))
    return lerp(top(eraser_on_tray(CLOSE)), (700, 1180), progress(t, PUT, ARM_OUT, "in"))


camera = Camera(zoom=Track((0, 1.0), (PULL_BACK[0], 1.02, "linear"), (PULL_BACK[1], 0.78, "inout"),
                           (DURATION, 0.77, "linear")),
                y=Track((0, 523), (DURATION, 523)), name="wipe")


def draw(canvas, t, frame):
    with camera.view(canvas, t):
        holding = GRAB <= t < PUT
        tray = ["red", "pale"] if holding else ["eraser", "red", "pale"]
        draw_board(canvas, frame, CLOSE, DAYS, key="board", on_tray=tray, cleaned=cleaned(t), **BOARD)
        if ARM_IN <= t < ARM_OUT:
            hand = hand_at(t)
            shoulder = shoulder_for(hand)
            elbow, hand, _ = reach(shoulder, hand, *ARM, 1)
            if holding:
                draw_eraser(canvas, frame, eraser_at(t), 0.0, BOARD_H, "board")
            pen = Ink(canvas, frame, color=INK, width=30.0, prefix="hero.closeup")
            beyond = (shoulder[0] + 0.6 * (shoulder[0] - elbow[0]), shoulder[1] + 0.6 * (shoulder[1] - elbow[1]))
            pen.line(beyond, elbow, "upper_arm", pin_ends=True, taper=0.0)     # runs on off screen
            pen.line(elbow, hand, "forearm", pin_ends=True, taper=0.1)
        canvas.drawPaint(skia.Paint(Color=to_color((4, 3, 5, int(255 * DARKNESS)))))
        glow(canvas, CLOCK_LIGHT, 1400, RED, 0.12)


bar = Discipline()  # still empty: wiping the board is planning, not doing


def overlay(canvas, t, frame):
    bar.draw(canvas, t, frame)


def soundtrack():
    mix = sk.Mix(DURATION)

    def effect(prompt, seconds, name):            # ElevenLabs effects, all brought to the same level first
        return sk.normalize(sk.eleven_sound(prompt, seconds, name))

    tray = effect("A plastic marker pen put down on a whiteboard's metal tray, one small light click", 0.5,
                  "marker_tray")
    for at_ in (GRAB, PUT):
        mix.add(tray, at=at_ - 0.2, gain_db=-21, pan=-0.2, reverb=0.08)
    # the eraser: row 10's recording, played twice over and swelling and fading with how fast the eraser
    # moves, so its sound follows each stroke
    wipe = effect("Close-up of a felt whiteboard eraser wiping a whiteboard clean in firm back-and-forth strokes",
                  5.0, "eraser_wipe")
    length = WIPE_END - WIPE_START + 0.1
    n = int(length * sk.SR)
    loop = np.concatenate([wipe, wipe[::-1]])[:n]
    step = 0.01
    ts = np.arange(WIPE_START, WIPE_START + length, step)
    speed = np.array([math.dist(eraser_at(a), eraser_at(a + step)) / step for a in ts])
    level = 0.25 + 0.75 * speed / speed.max()
    env = np.interp(np.arange(n) / sk.SR, ts - WIPE_START, level)
    mix.add(sk.fade_edges(loop * env, 0.05, 0.15), at=WIPE_START, gain_db=-14, pan=-0.15, reverb=0.08)
    return mix
