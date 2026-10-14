"""Film 1's wall by the bedroom door, with the whiteboard, shared by its scenes. Not a scene itself.

From the side (the wide view) it holds the floor, the door and the board on the wall. The board
can also be drawn close up from the front. Everything on the board is placed in the board's own
measurements (u across, v down, both 0..1), so the same board looks the same at any size.

The board: NEW ME and the huge goals on the left; on the right, START: and a column of days that
grows down, one for each "I'll start tomorrow". A day is written in pale marker and crossed out
in red when it fails. When the column is full, the days run on wherever there's room (MORE_DAYS).
"""
import math

import skia

from scenes.bedroom import ROOM, box, rounded_rect
from toolkit import BG, GREEN, INK, RED, Character, Ink, boil, to_color
from toolkit.rng import rng
from toolkit.text import typeface

# -- the board's writing ---------------------------------------------------------------

GOALS = ["Make $1,000,000", "Buy a Bugatti", "Own a yacht", "Run a marathon", "Six-pack by summer"]
FILL = (36, 37, 42)              # a whiteboard in a dark room: dark, with a faint shine
MARKER_INK = (226, 223, 214)     # the pale marker, a touch softer than the lines
TITLE = (0.05, 0.16, 0.12)       # "NEW ME": u, v of its baseline, size as a share of the board's height
GOAL = (0.05, 0.30, 0.115, 0.08)  # the first goal's u, v; the step down to the next; size
DAYS = (0.68, 0.16, 0.30, 0.115, 0.08)  # "START:" u, v; the first day's v; the step down; size
TRAY_MARKERS = {"red": 0.70, "pale": 0.84, "green": 0.56}   # where the markers lie on the tray (u); the green one
                                                            # only at the very end (film 1, row 31)
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


# When the START column is full (after SATURDAY, the 6th day), the days run on wherever there's room: down the
# middle of the board, under his goals and then over them, smaller and more crooked, until they nearly bury his
# goals (film 1, row 18; the user's pick, sheets/full_board_options.png option 3). In the order he wrote them,
# as (u, v, size, tilt in degrees).
MORE_DAYS = ([(0.405, 0.16 + i * 0.105, 0.068, tilt)                        # a second column down the middle
              for i, tilt in enumerate((3.8, -4.9, -0.7, 3.1, 1.8, -5.0, -2.7, -3.2))]
             + [(0.05, 0.775, 0.058, -3.2), (0.22, 0.775, 0.058, 4.8),      # under his goals
                (0.05, 0.895, 0.052, 3.2), (0.25, 0.895, 0.052, -6.4)]
             + [(0.06, 0.36, 0.06, -6), (0.2, 0.37, 0.055, 5), (0.04, 0.48, 0.06, 7),   # over his goals
                (0.21, 0.47, 0.055, -5), (0.08, 0.6, 0.06, -3), (0.2, 0.6, 0.05, 8),
                (0.04, 0.7, 0.055, 4), (0.22, 0.69, 0.055, -7),
                (0.29, 0.13, 0.042, -5),                                     # squeezed in beside NEW ME...
                (0.66, 0.955, 0.05, 3), (0.84, 0.955, 0.04, -4)])            # ...and under the column: the last
WEEK = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]


def day_names(count):
    """The first `count` start days, from MONDAY on, week after week."""
    return [WEEK[i % 7] for i in range(count)]


def day_spot(n):
    """Where the n-th start day (0 = the first) is written: (u, v, size, tilt)."""
    if n < 6:
        return DAYS[0], DAYS[2] + n * DAYS[3], DAYS[4], 0.0
    return MORE_DAYS[n - 6]


def day_box(rect, n, text):
    """Where the n-th start day sits, before its tilt: (left x, baseline y, width, size in pixels)."""
    u, v, size, _ = day_spot(n)
    return word_box(rect, text, u, v, size)


def _turned(point, origin, degrees):
    c, s = math.cos(math.radians(degrees)), math.sin(math.radians(degrees))
    dx, dy = point[0] - origin[0], point[1] - origin[1]
    return (origin[0] + dx * c - dy * s, origin[1] + dx * s + dy * c)


def _write(canvas, frame, rect, text, u, v, size, shown=1.0, key="", tilt=0.0):
    """Marker writing; shown 0..1 reveals it left to right, as the pen writes it. tilt turns it about the start
    of its baseline."""
    if shown <= 0:
        return
    x, y, w, px = word_box(rect, text, u, v, size)
    jitter = rng("board.word", key, text, boil(frame)).uniform(-1, 1, 2) * px * 0.012   # it boils with the lines
    canvas.save()
    if tilt:
        canvas.rotate(tilt, x, y)
    if shown < 1:
        canvas.clipRect(skia.Rect(x - px, y - 2 * px, x + w * shown, y + px))
    canvas.drawString(text, x + jitter[0], y + jitter[1], _font(px),
                      skia.Paint(AntiAlias=True, Color=to_color(MARKER_INK)))
    canvas.restore()


def careless(n):
    """How carelessly the n-th day is crossed out, 0..1. MONDAY to THURSDAY get a neat line; from FRIDAY on
    (film 1, row 15) he cares less each day, so each slash is more crooked and runs further past the word."""
    return 1 - 0.5 ** max(0, n - 3)


def _cross_local(rect, n, text):
    """The red line through the n-th day, before the day's tilt."""
    x, y, w, px = day_box(rect, n, text)
    s = careless(n)
    return (x - (0.15 + 0.2 * s) * px, y - (0.3 - 0.4 * s) * px), (x + w + (0.15 + s) * px, y - (0.4 + 0.9 * s) * px)


def cross_line(rect, n, text):
    """The red line through the n-th day: from just before it to just after, rising slightly (a careless
    slash rises more steeply and runs on past the word), turned with the day if it's written crooked."""
    a, b = _cross_local(rect, n, text)
    tilt = day_spot(n)[3]
    if not tilt:
        return a, b
    origin = day_box(rect, n, text)[:2]
    return _turned(a, origin, tilt), _turned(b, origin, tilt)


def _cross(canvas, frame, rect, n, text, crossed, key):
    if crossed <= 0:
        return
    a, b = _cross_local(rect, n, text)
    x, y, _, px = day_box(rect, n, text)
    tilt = day_spot(n)[3]
    canvas.save()
    if tilt:
        canvas.rotate(tilt, x, y)
    if crossed < 1:
        top, bottom = min(a[1], b[1]) - px, max(a[1], b[1]) + px
        canvas.clipRect(skia.Rect(a[0] - px, top, a[0] + (b[0] - a[0]) * crossed, bottom))
    Ink(canvas, frame, color=RED, width=0.15 * px, prefix=f"board.{key}").line(a, b, f"cross.{n}", taper=0.5)
    canvas.restore()


# -- after the turn: TODAY and the five easy things ------------------------------------------------
# Written on the clean board (film 1, row 22): TODAY where NEW ME was, and five easy things, each with an empty
# box before it. In board measurements.

FIVE = ["Get up when the alarm rings", "Clean your room", "Go for a walk", "Write 3 lines", "Text one person"]
TODAY = (0.05, 0.16, 0.12)                # TODAY: u, v of its baseline, size (where NEW ME was)
FIVE_TEXT = (0.135, 0.33, 0.13, 0.085)    # the first thing's u, v; the step down to the next; size
BOX_U, BOX_SIDE = 0.055, 0.064            # each box's left edge (u), and its side as a share of the board's height


def five_text(rect, i):
    """Where the i-th easy thing's words sit: (left x, baseline y, width, size in pixels)."""
    u, v, step, size = FIVE_TEXT
    return word_box(rect, FIVE[i], u, v + i * step, size)


def five_box(rect, i):
    """The i-th empty box, (x0, y0, x1, y1) in pixels: its bottom on the line's baseline."""
    side = BOX_SIDE * (rect[3] - rect[1])
    x = at(rect, BOX_U, 0)[0]
    y = five_text(rect, i)[1]
    return (x, y - side, x + side, y)


def box_point(rect, i, f):
    """The point f (0..1) of the way round the i-th box, drawn clockwise from its top left corner."""
    x0, y0, x1, y1 = five_box(rect, i)
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    side = min(int(f * 4), 3)
    u = f * 4 - side
    (ax, ay), (bx, by) = corners[side], corners[side + 1]
    return (ax + (bx - ax) * u, ay + (by - ay) * u)


def _draw_box(canvas, frame, rect, i, drawn, key):
    """The i-th box, drawn round clockwise from its top left corner as far as `drawn` (0..1)."""
    if drawn <= 0:
        return
    x0, y0, x1, y1 = five_box(rect, i)
    px = FIVE_TEXT[3] * (rect[3] - rect[1])
    pen = Ink(canvas, frame, color=MARKER_INK, width=0.1 * px, prefix=f"{key}.box{i}")
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    for k in range(4):
        shown = min(max(drawn * 4 - k, 0.0), 1.0)
        if shown <= 0:
            break
        (ax, ay), (bx, by) = corners[k], corners[k + 1]
        canvas.save()
        if shown < 1:       # the side being drawn: the whole side, cut off where the pen has got to
            ex, ey = ax + (bx - ax) * shown, ay + (by - ay) * shown
            pad = 0.1 * px
            canvas.clipRect(skia.Rect(min(ax, ex) - pad, min(ay, ey) - pad, max(ax, ex) + pad, max(ay, ey) + pad))
        pen.line((ax, ay), (bx, by), f"side{k}", taper=0.0)
        canvas.restore()


TICK_SHORT = 0.3      # the share of a tick that is its short first stroke, down into the box


def _tick_corners(rect, i):
    """A tick in the i-th box: down from its left into the box, then up past its top right corner."""
    x0, y0, x1, y1 = five_box(rect, i)
    s = x1 - x0
    return (x0 + 0.16 * s, y0 + 0.5 * s), (x0 + 0.42 * s, y0 + 0.86 * s), (x0 + 1.08 * s, y0 - 0.3 * s)


def tick_point(rect, i, f):
    """The point f (0..1) of the way along the tick in the i-th box, as the pen draws it."""
    a, b, c = _tick_corners(rect, i)
    if f < TICK_SHORT:
        return lerp_point(a, b, f / TICK_SHORT)
    return lerp_point(b, c, (f - TICK_SHORT) / (1 - TICK_SHORT))


def lerp_point(a, b, u):
    return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)


def _draw_tick(canvas, frame, rect, i, drawn, colour, key):
    if drawn <= 0:
        return
    a, b, c = _tick_corners(rect, i)
    px = FIVE_TEXT[3] * (rect[3] - rect[1])
    pen = Ink(canvas, frame, color=colour, width=0.13 * px, prefix=f"{key}.tick{i}")
    for k, (p, q, share) in enumerate(((a, b, (0.0, TICK_SHORT)), (b, c, (TICK_SHORT, 1.0)))):
        shown = min(max((drawn - share[0]) / (share[1] - share[0]), 0.0), 1.0)
        if shown <= 0:
            break
        canvas.save()
        if shown < 1:       # the stroke being drawn: the whole stroke, cut off where the pen has got to
            e = lerp_point(p, q, shown)
            pad = 0.15 * px
            canvas.clipRect(skia.Rect(min(p[0], e[0]) - pad, min(p[1], e[1]) - pad, max(p[0], e[0]) + pad,
                                      max(p[1], e[1]) + pad))
        pen.line(p, q, f"stroke{k}", taper=0.3)
        canvas.restore()


def draw_today(canvas, frame, rect, today=1.0, boxes=(), lines=(), ticks=(), tick_colour=MARKER_INK,
               key="board.today"):
    """TODAY and the five easy things, written over the clean board (draw it with draw_board(..., cleaned=...)
    first). today: 0..1, how much of TODAY is written. boxes, lines: for each thing in turn, 0..1, how much of its
    box and of its words are written (things not listed aren't there yet; leave both out for all five written).
    ticks: for each thing in turn, 0..1, how much of its tick is drawn, in tick_colour."""
    if not boxes and not lines:
        boxes = lines = [1.0] * len(FIVE)
    _write(canvas, frame, rect, "TODAY", *TODAY, today, key=key)
    for i, drawn in enumerate(boxes):
        _draw_box(canvas, frame, rect, i, drawn, key)
    u, v, step, size = FIVE_TEXT
    for i, shown in enumerate(lines):
        _write(canvas, frame, rect, FIVE[i], u, v + i * step, size, shown, key=f"{key}.{i}")
    for i, drawn in enumerate(ticks):
        _draw_tick(canvas, frame, rect, i, drawn, tick_colour, key)


# -- the board itself --------------------------------------------------------------------


def _smear(canvas, rect, areas):
    """A wiped whiteboard keeps a faint grey smear (drawn as one layer, so overlaps don't add up)."""
    if not areas:
        return
    x0, y0, x1, y1 = rect
    canvas.saveLayerAlpha(None, 7)
    smear = skia.Paint(AntiAlias=True, Color=skia.ColorWHITE,
                       MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 0.02 * (y1 - y0)))
    for u0, v0, u1, v1 in areas:
        a, b = at(rect, u0, v0 + 0.01), at(rect, u1, v1 - 0.01)
        canvas.drawRoundRect(skia.Rect(a[0], a[1], b[0], b[1]), 0.03 * (y1 - y0), 0.03 * (y1 - y0), smear)
    canvas.restore()


def draw_board(canvas, frame, rect, days, key="board", line_width=4.0, on_tray=("red", "pale"), goals=None,
               wiped=(), new_goals=(), cleaned=()):
    """The whiteboard in `rect` (x0, y0, x1, y1), with its frame, tray and writing.

    days: the start days on it, in order, as (name, written 0..1, crossed out 0..1).
    on_tray: what lies on the tray: "red", "pale" (markers) and "eraser" (one in his hand is drawn
    with draw_marker or draw_eraser).
    goals: the goal list (GOALS unless given). wiped: areas the eraser has wiped, as (u0, v0, u1, v1)
    in board measurements; the writing there is gone, leaving a faint smear. new_goals: goals written
    over the wiped ones, as (text, written 0..1). cleaned: areas wiped later, after everything was written
    (film 1, row 21): everything there is gone, NEW ME, the days and the red too.
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

    canvas.save()
    for u0, v0, u1, v1 in cleaned:
        a, b = at(rect, u0, v0), at(rect, u1, v1)
        canvas.clipRect(skia.Rect(a[0], a[1], b[0], b[1]), skia.ClipOp.kDifference)
    _write(canvas, frame, rect, "NEW ME", *TITLE, key=key)
    u, v, step, size = GOAL
    canvas.save()
    for u0, v0, u1, v1 in wiped:
        a, b = at(rect, u0, v0), at(rect, u1, v1)
        canvas.clipRect(skia.Rect(a[0], a[1], b[0], b[1]), skia.ClipOp.kDifference)
    for i, goal in enumerate(GOALS if goals is None else goals):
        _write(canvas, frame, rect, "- " + goal, u, v + i * step, size, key=key)
    canvas.restore()
    _smear(canvas, rect, wiped)
    for i, (goal, written) in enumerate(new_goals):
        _write(canvas, frame, rect, "- " + goal, u, v + i * step, size, written, key=key + ".new")
    _write(canvas, frame, rect, "START:", DAYS[0], DAYS[1], DAYS[4], key=key)
    for n, (name, written, crossed) in enumerate(days):
        u, v, size, tilt = day_spot(n)
        _write(canvas, frame, rect, name, u, v, size, written, key=f"{key}.{n}" if n >= 6 else key, tilt=tilt)
        _cross(canvas, frame, rect, n, name, crossed, key)
    canvas.restore()
    _smear(canvas, rect, cleaned)

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
    shade = {"red": RED, "green": GREEN}.get(colour, MARKER_INK)
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
