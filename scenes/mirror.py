"""Film 1, row 31 of the story: the mirror ending. About 11 seconds, two shots joined by a hard cut. It follows
row 30, the run in the park, and mirrors the film's first shot.

 0-6.4 s     The opening shot from above, exactly as in scene 1 (the same slow creep in): 5:59. But the room is
             clean, the bed made, and he's already up, sitting on the nightstand side of the bed, calm. 6:00: the
             alarm, and he leans over and presses it straight away, on its first burst of beeps. The phone stays
             dark on its charger.
 6.4-11 s    A quiet last shot of the board: TODAY and five ticks in green, the green marker on the tray. No arm.

The bar is full and green. Sound: the payoff's music carrying on and fading out, the one burst of the alarm and
its button.
"""
import math

import numpy as np

import scenes.five_things as five
import scenes.scroll as scroll
from scenes.bedroom import ROOM, draw_bed, draw_blanket, draw_nightstand, hero
from scenes.discipline import Discipline
from scenes.door_wall import draw_board, draw_today
from scenes.payoff import DURATION as PAYOFF_LENGTH
from scenes.payoff import MUSIC
from scenes.the_board import CLOSE
from toolkit import GREEN, Camera, Ink, Track, lerp, progress, reach
from toolkit import sound as sk

PEAK_DB = -3.2          # set so the sounds sit at the same level as the sounds in the other scenes
SIX = 3.0               # 5:59 becomes 6:00 and the alarm goes off
PRESS = SIX + 0.32      # he presses it, two beeps in
BOARD_SHOT = 6.4
DURATION = 11.0

# -- shot 1: from above, the opening shot ----------------------------------------------------------------------

bed_camera = Camera(x=Track((0, 960), (BOARD_SHOT, 936, "linear")),       # scene 1's slow creep in
                    y=Track((0, 540), (BOARD_SHOT, 512, "linear")),
                    zoom=Track((0, 1.0), (BOARD_SHOT, 1.056, "linear")), name="bed")

HIP = (842, 488)                         # sitting on the bed's left edge, by the nightstand, legs over the side
BUTTON = (676, 238)                      # the clock's button, seen from above
REACH = (SIX + 0.02, PRESS)              # his hand goes straight to it...
BACK = (PRESS + 0.35, PRESS + 1.0)       # ...and back to his knee
LEAN = 110                                # he leans toward the nightstand to reach it


def _at_rest():
    """Sitting on the edge, from above, facing left: his feet a little forward on the floor, his hands resting on
    his knees, so his arms and legs show beyond his head."""
    j = scroll._rotated(scroll._offsets_sitting(0.45), HIP, 90)
    knee_l, knee_r = j["knee_l"], j["knee_r"]
    j["hand_l"], j["hand_r"] = (knee_l[0] + 14, knee_l[1] - 6), (knee_r[0] + 14, knee_r[1] + 6)
    j["elbow_l"], j["elbow_r"] = (HIP[0] - 40, HIP[1] - 64), (HIP[0] - 40, HIP[1] + 64)
    return j


REST = _at_rest()


def sitting(t):
    """His joints from above, sitting on the edge facing left (the floor by the nightstand), leaning over to the
    clock and back. Returns (joints, head size)."""
    j = dict(REST)
    breath = 1.5 * math.sin(2 * math.pi * t / 3.6)
    lean = progress(t, REACH[0], REACH[0] + 0.2, "out") * (1 - progress(t, *BACK, "inout"))
    toward = (BUTTON[0] - HIP[0], BUTTON[1] - HIP[1])
    d = math.hypot(*toward)
    shift = (toward[0] / d * LEAN * lean, toward[1] / d * LEAN * lean + breath)
    for k in ("neck", "shoulder", "head", "elbow_l", "elbow_r"):
        j[k] = (j[k][0] + shift[0], j[k][1] + shift[1])
    # his left hand (on the nightstand side): from his knee to the button, and back
    out_ = progress(t, *REACH, "inout") * (1 - progress(t, *BACK, "inout"))
    hand = lerp(REST["hand_l"], BUTTON, out_)
    if out_ > 0:
        sh = j["shoulder"]
        up, fore = hero.arm
        # the elbow on the outside, away from his head
        elbow = max((reach(sh, hand, up, fore, b)[0] for b in (1, -1)), key=lambda e: math.dist(e, j["head"]))
        j["hand_l"], j["elbow_l"] = hand, lerp(j["elbow_l"], elbow, min(1.0, out_ * 3))
    return j, hero.head_r * 1.1


def shot_bed(canvas, t, frame):
    with bed_camera.view(canvas, t):
        room = Ink(canvas, frame, color=ROOM, width=4.0, prefix="bedroom")
        draw_bed(room)
        ringing = SIX <= t < PRESS
        draw_nightstand(room, canvas, frame, time="5:59" if t < SIX else "6:00", phone=True, bottles=(),
                        on=1.0 if not ringing or sk.alarm_on(t - SIX) else 0.0)
        draw_blanket(room, 0.0, 0.0, made=True)            # the bed made, smooth
        j, r = sitting(t)
        scroll.draw_body(canvas, frame, j, ("legs", "arms", "spine", "head"), r)    # seen from above: the top of
        # his head (sitting up, his face is turned away from us)


# -- shot 2: the board, five green ticks -----------------------------------------------------------------------

board_camera = Camera(x=Track((BOARD_SHOT, 790), (DURATION, 800, "linear")), y=Track((BOARD_SHOT, 535), (DURATION, 535, "linear")),
                      zoom=Track((BOARD_SHOT, 1.08), (DURATION, 1.12, "linear")), name="mirror.board")


def shot_board(canvas, t, frame):
    with board_camera.view(canvas, t):
        draw_board(canvas, frame, CLOSE, five.DAYS, key="board", on_tray=("eraser", "green", "red", "pale"),
                   **five.BOARD)
        draw_today(canvas, frame, CLOSE, ticks=[1.0] * 5, tick_colour=GREEN)


def draw(canvas, t, frame):
    if t < BOARD_SHOT:
        shot_bed(canvas, t, frame)
    else:
        shot_board(canvas, t, frame)


bar = Discipline(start=20)      # full, and green


def overlay(canvas, t, frame):
    bar.draw(canvas, t, frame)


def soundtrack():
    mix = sk.Mix(DURATION)
    # the payoff's music carries on from where row 30 left it, and fades away
    music = sk.normalize(sk.eleven_music(MUSIC, 30, "payoff"))[int(PAYOFF_LENGTH * sk.SR):]
    music = music[:int(DURATION * sk.SR)]
    fade = np.interp(np.arange(len(music)) / sk.SR, [0, DURATION - 2.0, DURATION], [1.0, 1.0, 0.0])
    mix.add(music * fade, at=0, gain_db=-8, reverb=0.1)
    mix.add(sk.alarm(PRESS - SIX), at=SIX, gain_db=-9, reverb=0.12)       # one burst, cut short
    mix.add(sk.tick(key="mirror.button"), at=PRESS, gain_db=-10, reverb=0.1)
    mix.add(sk.whoosh(0.3, peak=0.5, low=200, high=1200, key="mirror.reach"), at=REACH[0], gain_db=-24)
    return mix
