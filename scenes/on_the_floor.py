"""Film 1, row 20 of the story: on the floor. About 8 seconds, one shot. It follows row 19, where his phone died
at 3:47 and the hum faded to silence.

From behind him (the user's pick, sheets/floor_options.png B): he sits on the floor against the bed, the back of
his head and his slumped shoulders big in the foreground above the edge of the mattress; across the dark room,
the board with its wall of red. Everything faintly lit red by the clock, off to the left.

 0-1 s      Still. Only his slow breathing.
 1-4.4 s    A breath in, then a long, slow breath out: his shoulders drop and his head sinks.
 4.4-5.2 s  He stays there, head down.
 5.2-6.9 s  Slowly, his head lifts to the board again, a little straighter than before: still tired, but no
            longer frozen. Something has let go: the first moment of the turn.
 6.9-8.2 s  He looks at the board.

No caption. Sound: silence (the hum is gone), and his breath.
"""
import math

import skia

import scenes.new_goals as goals
from scenes.bedroom import ROOM, box, rounded_rect, smooth
from scenes.discipline import Discipline
from scenes.door_wall import day_names, draw_wall
from scenes.scroll import glow
from toolkit import BG, INK, RED, Camera, Ink, Track, progress, to_color
from toolkit import sound as sk

DURATION = 8.2
PEAK_DB = -8.9          # set so his breath sits at the same level as the sounds in the other scenes
BOARD = dict(wiped=goals.wiped(goals.DURATION), new_goals=goals.written(goals.DURATION))
DAYS = [(name, 1.0, 1.0) for name in day_names(29)]       # the full board, as row 18 left it

# timed to the sigh recording: its breath in runs 0-1.3 s, its long breath out 1.55-3.4 s
SIGH_AT = 1.0
BREATH_IN = (SIGH_AT, SIGH_AT + 1.3)
BREATH_OUT = (SIGH_AT + 1.55, SIGH_AT + 3.4)
LIFT = (BREATH_OUT[1] + 0.8, BREATH_OUT[1] + 2.5)
DARKNESS = 0.6
CLOCK_LIGHT = (-150, 500)       # the red clock is off to the left, by the head of the bed

camera = Camera(zoom=Track((0, 1.0), (DURATION, 1.05, "linear")), name="floor")

# his head and shoulders, from behind (picture coordinates)
HEAD, HEAD_R = (600, 560), 125
NECK_LENGTH = 60
WIDTH = 14.0


def slump(t):
    """How he sits: (shoulders down, head down) in pixels."""
    rise = progress(t, *BREATH_IN, "inout") * (1 - progress(t, *BREATH_OUT, "inout"))     # the breath in
    out = progress(t, *BREATH_OUT, "inout")                                              # the long breath out
    up = progress(t, *LIFT, "inout")                                                      # his head lifts again
    calm = 2.5 * math.sin(2 * math.pi * t / 4.4)                                          # slow breathing
    shoulders = -7 * rise + 16 * out - 4 * up + calm * (1 - out * 0.5)
    head = -6 * rise + 80 * out - 92 * up + calm * 0.6
    return shoulders, head


def draw_him(canvas, frame, t):
    """The back of his head, his slumped shoulders and the tops of his arms, above the edge of the mattress."""
    drop, sink = slump(t)
    droop = 0.6 * max(drop, 0)          # the ends of his shoulders fall a little further than the middle
    pen = Ink(canvas, frame, color=INK, width=WIDTH, prefix="floor.hero")
    sh = (HEAD[0] + 4, HEAD[1] + HEAD_R + NECK_LENGTH + drop)
    head = (HEAD[0], HEAD[1] + sink)
    pen.line((head[0] + 2, head[1] + HEAD_R - 4), sh, "neck", taper=0.0)
    pen.stroke(smooth([(sh[0] - 175, sh[1] + 85 + droop), (sh[0] - 120, sh[1] + 12), sh, (sh[0] + 120, sh[1] + 12),
                       (sh[0] + 175, sh[1] + 85 + droop)]), "shoulders", taper=0.0)
    for side, sx in (("l", -1), ("r", 1)):
        pen.line((sh[0] + sx * 175, sh[1] + 85 + droop), (sh[0] + sx * 185, 1000), "arm." + side, taper=0.0)
    pen.circle(head, HEAD_R, "head", fill=BG)
    room = Ink(canvas, frame, color=ROOM, width=7.0, prefix="floor.bed")
    box(room, rounded_rect(-100, 900, 2100, 1300, 20), "mattress")
    room.stroke(smooth([(-80, 912), (700, 902), (1400, 910), (2080, 904)]), "blanket", width=5.0)


def draw(canvas, t, frame):
    with camera.view(canvas, t):
        canvas.save()             # the door wall across the room: the board, the door
        canvas.translate(960, 500)
        canvas.scale(1.3, 1.3)
        canvas.translate(-1060, -620)
        draw_wall(canvas, frame, DAYS, on_tray=("eraser", "red", "pale"), **BOARD)
        canvas.restore()
        draw_him(canvas, frame, t)
        canvas.drawPaint(skia.Paint(Color=to_color((4, 3, 5, int(255 * DARKNESS)))))
        glow(canvas, CLOCK_LIGHT, 1200, RED, 0.14)


bar = Discipline()  # still empty


def overlay(canvas, t, frame):
    bar.draw(canvas, t, frame)


def soundtrack():
    mix = sk.Mix(DURATION)
    sigh = sk.normalize(sk.eleven_sound("A tired man, alone in a silent room at night, takes a slow breath in "
                                        "through his nose and lets out one long, slow, heavy sigh through his "
                                        "mouth. Close up, no other sounds", 5.0, "long_sigh"))
    mix.add(sk.fade_edges(sigh, 0.05, 0.3), at=SIGH_AT, gain_db=-12, reverb=0.1)
    return mix

