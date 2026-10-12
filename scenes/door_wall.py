"""Film 1's wall by the bedroom door, with the whiteboard, shared by its scenes. Not a scene itself.

From the side (the wide view) it holds the floor, the door and the board on the wall. The board
can also be drawn close up from the front. Everything on the board is placed in the board's own
measurements (u across, v down, both 0..1), so the same board looks the same at any size.

The board: NEW ME and the huge goals on the left; on the right, START: and a column of days that
grows down, one for each "I'll start tomorrow". A day is written in pale marker and crossed out
in red when it fails.
"""
import math

import skia

from scenes.bedroom import ROOM, box, rounded_rect
from toolkit import BG, INK, RED, Character, Ink, boil, to_color
from toolkit.rng import rng
from toolkit.text import typeface

# -- the board's writing ---------------------------------------------------------------

GOALS = ["Make $1,000,000", "Buy a Bugatti", "Own a yacht", "Run a marathon", "Six-pack by summer"]
FILL = (36, 37, 42)              # a whiteboard in a dark room: dark, with a faint shine
MARKER_INK = (226, 223, 214)     # the pale marker, a touch softer than the lines
TITLE = (0.05, 0.16, 0.12)       # "NEW ME": u, v of its baseline, size as a share of the board's height
GOAL = (0.05, 0.30, 0.115, 0.08)  # the first goal's u, v; the step down to the next; size
DAYS = (0.68, 0.16, 0.30, 0.115, 0.08)  # "START:" u, v; the first day's v; the step down; size
TRAY_MARKERS = {"red": 0.70, "pale": 0.84}   # where the markers lie on the tray (u)
TRAY_ERASER = 0.22                           # where the eraser lies on the tray (u), when the board has one


def at(rect, u, v):
    """A point on the board, from board measurements."""
    x0, y0, x1, y1 = rect
    return (x0 + u * (x1 - x0), y0 + v * (y1 - y0))


def _font(size):
    f = skia.Font(typeface(), size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    return f


def word_box(rect, text, u, v, size):
    """Where a word sits on the board: (left x, baseline y, width, size in pixels)."""
    px = size * (rect[3] - rect[1])
    x, y = at(rect, u, v)
    return x, y, _font(px).measureText(text), px


def day_box(rect, n, text):
    """Where the n-th start day (0 = the first) sits."""
    u, _, v, step, size = DAYS
    return word_box(rect, text, u, v + n * step, size)


def _write(canvas, frame, rect, text, u, v, size, shown=1.0, key=""):
    """Marker writing; shown 0..1 reveals it left to right, as the pen writes it."""
    if shown <= 0:
        return
    x, y, w, px = word_box(rect, text, u, v, size)
    jitter = rng("board.word", key, text, boil(frame)).uniform(-1, 1, 2) * px * 0.012   # it boils with the lines
    canvas.save()
    if shown < 1:
        canvas.clipRect(skia.Rect(x - px, y - 2 * px, x + w * shown, y + px))
    canvas.drawString(text, x + jitter[0], y + jitter[1], _font(px),
                      skia.Paint(AntiAlias=True, Color=to_color(MARKER_INK)))
    canvas.restore()


def cross_line(rect, n, text):
    """The red line through the n-th day: from just before it to just after, rising slightly."""
    x, y, w, px = day_box(rect, n, text)
    return (x - 0.15 * px, y - 0.3 * px), (x + w + 0.15 * px, y - 0.4 * px)


def _cross(canvas, frame, rect, n, text, crossed, key):
    if crossed <= 0:
        return
    a, b = cross_line(rect, n, text)
    px = day_box(rect, n, text)[3]
    canvas.save()
    if crossed < 1:
        canvas.clipRect(skia.Rect(a[0] - px, a[1] - px, a[0] + (b[0] - a[0]) * crossed, a[1] + px))
    Ink(canvas, frame, color=RED, width=0.15 * px, prefix=f"board.{key}").line(a, b, f"cross.{n}", taper=0.5)
    canvas.restore()


# -- the board itself --------------------------------------------------------------------


def draw_board(canvas, frame, rect, days, key="board", line_width=4.0, on_tray=("red", "pale"), goals=None,
               wiped=(), new_goals=()):
    """The whiteboard in `rect` (x0, y0, x1, y1), with its frame, tray and writing.

    days: the start days on it, in order, as (name, written 0..1, crossed out 0..1).
    on_tray: what lies on the tray: "red", "pale" (markers) and "eraser" (one in his hand is drawn
    with draw_marker or draw_eraser).
    goals: the goal list (GOALS unless given). wiped: areas the eraser has wiped, as (u0, v0, u1, v1)
    in board measurements; the writing there is gone, leaving a faint smear. new_goals: goals written
    over the wiped ones, as (text, written 0..1).
    """
    x0, y0, x1, y1 = rect
    ink = Ink(canvas, frame, color=ROOM, width=line_width, prefix=key)
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    ink.fill(corners, "fill", color=FILL, wobble=0)
    sheen = skia.GradientShader.MakeLinear(
        [skia.Point(x0, y0), skia.Point(x1, y1)],
        [to_color((255, 255, 255, 0)), to_color((255, 255, 255, 14)), to_color((255, 255, 255, 0))],
        [0.25, 0.45, 0.65])
    canvas.drawRect(skia.Rect(x0, y0, x1, y1), skia.Paint(Shader=sheen))
    ink.stroke(corners, "frame", closed=True)

    _write(canvas, frame, rect, "NEW ME", *TITLE, key=key)
    u, v, step, size = GOAL
    canvas.save()
    for u0, v0, u1, v1 in wiped:
        a, b = at(rect, u0, v0), at(rect, u1, v1)
        canvas.clipRect(skia.Rect(a[0], a[1], b[0], b[1]), skia.ClipOp.kDifference)
    for i, goal in enumerate(GOALS if goals is None else goals):
        _write(canvas, frame, rect, "- " + goal, u, v + i * step, size, key=key)
    canvas.restore()
    if wiped:      # a wiped whiteboard keeps a faint grey smear (drawn as one layer, so overlaps don't add up)
        canvas.saveLayerAlpha(None, 7)
        smear = skia.Paint(AntiAlias=True, Color=skia.ColorWHITE,
                           MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 0.02 * (y1 - y0)))
        for u0, v0, u1, v1 in wiped:
            a, b = at(rect, u0, v0 + 0.01), at(rect, u1, v1 - 0.01)
            canvas.drawRoundRect(skia.Rect(a[0], a[1], b[0], b[1]), 0.03 * (y1 - y0), 0.03 * (y1 - y0), smear)
        canvas.restore()
    for i, (goal, written) in enumerate(new_goals):
        _write(canvas, frame, rect, "- " + goal, u, v + i * step, size, written, key=key + ".new")
    _write(canvas, frame, rect, "START:", DAYS[0], DAYS[1], DAYS[4], key=key)
    for n, (name, written, crossed) in enumerate(days):
        _write(canvas, frame, rect, name, DAYS[0], DAYS[2] + n * DAYS[3], DAYS[4], written, key=key)
        _cross(canvas, frame, rect, n, name, crossed, key)

    # the tray along the bottom, and the markers lying on it
    h = y1 - y0
    tray = y1 + 0.03 * h
    ink.line((x0 + 0.06 * (x1 - x0), tray), (x1 - 0.06 * (x1 - x0), tray), "tray", width=line_width * 1.25)
    for colour in on_tray:
        if colour == "eraser":
            draw_eraser(canvas, frame, eraser_on_tray(rect), 0.0, h, key)
            continue
        tip = at(rect, TRAY_MARKERS[colour], 1.0)
        draw_marker(canvas, frame, (tip[0] - 0.09 * h, tray - 0.03 * h), 0.0, h, colour, key)


def eraser_size(board_h):
    """A whiteboard eraser's length and height, for a board this tall."""
    return 0.22 * board_h, 0.095 * board_h


def eraser_on_tray(rect):
    """Where the eraser's middle is while it lies on the tray, felt side down."""
    h = rect[3] - rect[1]
    x = at(rect, TRAY_ERASER, 1.0)[0]
    return (x, rect[3] + 0.03 * h - eraser_size(h)[1] / 2)


def draw_eraser(canvas, frame, center, angle, board_h, key="board"):
    """A whiteboard eraser, its middle at `center`, turned by `angle` degrees: a dark block with a grey
    felt pad along its bottom."""
    length, height = eraser_size(board_h)
    ink = Ink(canvas, frame, color=ROOM, width=max(1.2, 0.006 * board_h), prefix=f"{key}.eraser")
    canvas.save()
    canvas.translate(*center)
    canvas.rotate(angle)
    box(ink, rounded_rect(-length / 2, -height / 2, length / 2, height * 0.18, height * 0.25), "block", fill=BG)
    box(ink, rounded_rect(-length / 2 + 2, height * 0.18, length / 2 - 2, height / 2, height * 0.12), "felt",
        fill=(78, 78, 82))
    canvas.restore()


def marker_size(board_h):
    """A marker's length and thickness, for a board this tall."""
    return 0.2 * board_h, 0.037 * board_h


def draw_marker(canvas, frame, tip, angle, board_h, colour, key="board"):
    """A whiteboard marker with its tip at `tip`, pointing along `angle` degrees (0 = right).

    The body is dark and outlined; the cap end and the tip show the ink colour.
    """
    length, thick = marker_size(board_h)
    ink = Ink(canvas, frame, color=ROOM, width=max(1.2, 0.006 * board_h), prefix=f"{key}.marker.{colour}")
    shade = RED if colour == "red" else MARKER_INK
    canvas.save()
    canvas.translate(*tip)
    canvas.rotate(angle)
    # along -x from the tip: the tip, the body, the cap
    box(ink, rounded_rect(-length, -thick / 2, -0.12 * length, thick / 2, thick * 0.35), "body", fill=BG)
    box(ink, rounded_rect(-length - 0.02 * length, -thick * 0.56, -0.72 * length, thick * 0.56, thick * 0.3),
        "cap", fill=shade)
    ink.fill([(-0.12 * length, -thick * 0.3), (0, -thick * 0.1), (0, thick * 0.1), (-0.12 * length, thick * 0.3)],
             "tip", color=shade, wobble=0)
    canvas.restore()


# -- the wall, seen from the side ------------------------------------------------------------

GROUND = 860                                    # the floor line in the wide view
WIDE_BOARD = (780, GROUND - 452, 1232, GROUND - 226)   # 1.8 m by 0.9 m, its bottom 0.9 m up
DOOR = (1350, GROUND - 515, 1570, GROUND)
hero = Character("hero")                        # at wide-view size


OUTSIDE = (150, 162, 186)        # the cold, grey early light through the open door


def draw_wall(canvas, frame, days, on_tray=("red", "pale"), door_open=0.0, **board):
    """The wide view: the floor, the skirting along the wall, the board and the door.

    door_open: 0 = shut, 1 = swung right open, away from us on its hinges (on the right), letting in
    the cold early light from outside. Anything else (goals, wiped, new_goals) goes to draw_board.
    """
    room = Ink(canvas, frame, color=ROOM, width=4.0, prefix="doorwall")
    room.floor(GROUND, key="floor")
    skirting = (*ROOM[:3], 110)
    room.stroke([(-600, GROUND - 26), (DOOR[0] - 14, GROUND - 26)], "skirting", width=3.0, color=skirting, taper=0.0)
    room.stroke([(DOOR[2] + 14, GROUND - 26), (2520, GROUND - 26)], "skirting.r", width=3.0, color=skirting, taper=0.0)
    # the door: its frame, the door itself, and the handle on the board's side
    x0, y0, x1, y1 = DOOR
    room.stroke([(x0 - 14, y1), (x0 - 14, y0 - 14), (x1 + 14, y0 - 14), (x1 + 14, y1)], "door.frame")
    if door_open <= 0:
        room.stroke([(x0, y1), (x0, y0), (x1, y0), (x1, y1)], "door", width=3.4)
        handle = (x0 + 26, y1 - 0.47 * (y1 - y0))
        room.circle(handle, 6, "door.knob", width=3.0)
        room.line(handle, (handle[0] + 34, handle[1]), "door.handle", width=5.0)
    else:
        _draw_open_door(canvas, room, door_open)
    draw_board(canvas, frame, WIDE_BOARD, days, key="board.wide", line_width=3.0, on_tray=on_tray, **board)



def _draw_open_door(canvas, room, door_open):
    """The doorway with the early light coming in, and the door swung away on its hinges."""
    x0, y0, x1, y1 = DOOR
    light = min(1.0, door_open * 1.6)
    canvas.drawRect(skia.Rect(x0, y0, x1, y1), skia.Paint(Color=to_color((*OUTSIDE, int(120 * light)))))
    # the light falling in across the floor in front of the door
    spill = skia.Path()
    spill.addPoly([skia.Point(x0, y1), skia.Point(x1, y1), skia.Point(x1 + 60, y1 + 70), skia.Point(x0 - 90, y1 + 70)], True)
    canvas.drawPath(spill, skia.Paint(AntiAlias=True, Color=to_color((*OUTSIDE, int(45 * light)))))
    # the door, seen at an angle: its free edge swings toward the hinges and away from us (so it looks shorter)
    turn = door_open * math.pi / 2 * 0.92
    edge = x1 - (x1 - x0) * math.cos(turn)
    shrink = 0.06 * (y1 - y0) * math.sin(turn)
    leaf = [(x1, y1), (x1, y0), (edge, y0 + shrink), (edge, y1 - shrink)]
    room.fill(leaf, "door.leaf", color=BG, wobble=0)
    room.stroke(leaf, "door", closed=True, width=3.4)
    handle = (edge + 26 * math.cos(turn), y1 - 0.47 * (y1 - y0))
    room.circle(handle, 6, "door.knob", width=3.0)
