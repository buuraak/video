"""Film 1's bedroom, seen from straight above, shared by its scenes. Not a scene itself.

Holds the bed, the nightstand with the alarm clock and the phone, the blanket,
the hero at bedroom size, and small drawing helpers (rounded boxes, smooth
curves, the clock's red numbers).
"""
import math

import numpy as np
import skia

from toolkit import BG, GREY, RED, RED_DARK, Character, Ink, to_color

# -- drawing helpers -------------------------------------------------------------


def rounded_rect(x0, y0, x1, y1, r, steps=7):
    """The corner points of a rectangle with rounded corners, clockwise from the top."""
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for a in np.linspace(a0, a0 + 90, steps):
            pts.append((cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))))
    return pts


def turned(pts, center, degrees):
    c, s = math.cos(math.radians(degrees)), math.sin(math.radians(degrees))
    return [(center[0] + (x - center[0]) * c - (y - center[1]) * s,
             center[1] + (x - center[0]) * s + (y - center[1]) * c) for x, y in pts]


def box(ink, pts, key, fill=BG, **kw):
    """A closed hand-drawn shape, filled first so it hides whatever is behind it."""
    if fill is not None:
        ink.fill(pts, key + ".fill", color=fill, wobble=0)
    ink.stroke(pts, key, closed=True, **kw)


def smooth(points, per_segment=10):
    """A smooth curve through the points (Catmull-Rom)."""
    p = np.asarray(points, dtype=float)
    p = np.vstack([p[0], p, p[-1]])
    out = []
    for i in range(1, len(p) - 2):
        a, b, c, d = p[i - 1], p[i], p[i + 1], p[i + 2]
        for u in np.linspace(0, 1, per_segment, endpoint=False):
            out.append(0.5 * ((2 * b) + (-a + c) * u + (2 * a - 5 * b + 4 * c - d) * u ** 2
                              + (-a + 3 * b - 3 * c + d) * u ** 3))
    out.append(p[-2])
    return out


# The clock's numbers: straight bars, like a real digital clock, drawn with the wobbly pen.
BARS = {"a": ((0, 0), (1, 0)), "b": ((1, 0), (1, 1)), "c": ((1, 1), (1, 2)), "d": ((0, 2), (1, 2)),
        "e": ((0, 1), (0, 2)), "f": ((0, 0), (0, 1)), "g": ((0, 1), (1, 1))}
DIGITS = {"0": "abcdef", "1": "bc", "2": "abged", "3": "abgcd", "4": "fgbc", "5": "afgcd",
          "6": "afgedc", "7": "abc", "8": "abcdefg", "9": "abcdfg"}
SLANT = 0.08           # the numbers lean slightly forward, like real clock numbers


def clock_numbers(canvas, frame, text, center, height, key, on=1.0):
    """Red glowing clock numbers like "5:59", `height` pixels tall. on: 0 = dark, 1 = lit."""
    if on <= 0:
        return
    dw, bar = height * 0.5, height * 0.1
    gap, space = bar * 0.75, height * 0.2
    widths = [bar if ch == ":" else dw for ch in text]
    x = center[0] - (sum(widths) + space * (len(text) - 1)) / 2
    top = center[1] - height / 2

    def at(px, py):     # lean the top of each number forward
        return (px + (top + height - py) * SLANT, py)

    recorder = skia.PictureRecorder()
    rc = recorder.beginRecording(skia.Rect(-2000, -2000, 4000, 4000))
    pen = Ink(rc, frame, color=RED, width=bar, prefix=key)
    for i, (ch, w) in enumerate(zip(text, widths)):
        if ch == ":":
            for k, fy in enumerate((0.32, 0.72)):
                pen.blob(at(x + w / 2, top + fy * height), bar * 0.62, bar * 0.62, f"colon{k}")
        else:
            for name in DIGITS[ch]:
                (ax, ay), (bx, by) = BARS[name]
                p0 = np.array((x + ax * dw, top + ay * height / 2))
                p1 = np.array((x + bx * dw, top + by * height / 2))
                d = (p1 - p0) / np.linalg.norm(p1 - p0)
                pen.line(at(*(p0 + d * gap)), at(*(p1 - d * gap)), f"{i}{name}", taper=0.25)
        x += w + space
    picture = recorder.finishRecordingAsPicture()

    # the red glow of the lit numbers, then the numbers themselves
    for color, sigma, alpha in ((RED_DARK, height * 0.22, 1.0), (RED, height * 0.07, 0.55)):
        paint = skia.Paint(ImageFilter=skia.ImageFilters.Blur(sigma, sigma),
                           ColorFilter=skia.ColorFilters.Blend(to_color((*color, int(255 * alpha * on))),
                                                               skia.BlendMode.kSrcIn))
        canvas.drawPicture(picture, None, paint)
    if on < 1:
        canvas.saveLayerAlpha(None, int(255 * on))
    canvas.drawPicture(picture)
    if on < 1:
        canvas.restore()


# -- the room, seen from straight above --------------------------------------------

hero = Character("hero", height=600)

WALL = 196                       # where the floor meets the wall behind the bed
BED = (805, WALL, 1235, 905)
HEAD_BOARD = WALL + 34
PILLOW = (814, 240, 1030, 428)   # one pillow, under his head; the other half of the bed is empty
HERO_X = 920                     # he lies on the nightstand side of the bed
HIP_Y = 592                      # puts his head in the middle of the pillow
BLANKET_TOP = 474                # the blanket reaches his chest
ROOM = (*GREY, 185)              # the room's lines, a little dimmer than usual: it's dark
NIGHTSTAND = (575, WALL, 785, 440)
CLOCK_TOP = (598, 220, 728, 262)       # the clock seen from above: its top...
CLOCK_FRONT = (598, 262, 728, 308)     # ...and the face with the numbers
PHONE = (680, 382)                     # where the phone lies on the nightstand, on its side
PHONE_TURN = -6                        # degrees
PORT = turned([(PHONE[0] - 60, PHONE[1] + 1)], PHONE, PHONE_TURN)[0]   # where the charger plugs in


def belly_hands(shoulder, breath=0.0):
    """Where his hands rest, together on his belly on top of the blanket (left, right)."""
    apart = 16 + 2 * breath
    return ((shoulder[0] - apart, shoulder[1] + 142 + breath), (shoulder[0] + apart, shoulder[1] + 142 + breath))


def draw_phone_on_table(ink):
    """The phone lying screen up on the nightstand, dark."""
    body = turned(rounded_rect(PHONE[0] - 60, PHONE[1] - 30, PHONE[0] + 60, PHONE[1] + 30, 10),
                  PHONE, PHONE_TURN)
    screen = turned(rounded_rect(PHONE[0] - 48, PHONE[1] - 23, PHONE[0] + 52, PHONE[1] + 23, 5),
                    PHONE, PHONE_TURN)
    box(ink, body, "phone", width=3.2)
    ink.stroke(screen, "phone.screen", closed=True, width=1.8)


def draw_nightstand(ink, canvas, frame, time="5:59", phone=True):
    """The nightstand: the alarm clock showing `time`, and the phone on its charger.

    phone=False: the phone has been taken, and the unplugged charger cable lies loose.
    """
    box(ink, rounded_rect(*NIGHTSTAND, 8), "nightstand")
    # the alarm clock, its top with the button, and its front with the red numbers
    box(ink, rounded_rect(*CLOCK_TOP, 8), "clock.top", width=3.2)
    box(ink, rounded_rect(650, 230, 700, 246, 5), "clock.button", width=2.4)
    box(ink, rounded_rect(*CLOCK_FRONT, 8), "clock.front", width=3.2)
    box(ink, rounded_rect(608, 268, 718, 302, 5), "clock.window", width=2.0)
    clock_numbers(canvas, frame, time, (663, 285), 24, "clock.small")
    if phone:
        draw_phone_on_table(ink)
    else:   # the plug at the loose end of the cable
        ink.line((PORT[0] + 12, PORT[1] - 1), (PORT[0] - 2, PORT[1] + 1), "cable.plug", width=6.0, taper=0.0)
    # the charging cable: off the nightstand, across the floor, up to the socket on the wall
    cable = smooth([PORT, (PORT[0] - 22, PORT[1] + 6), (NIGHTSTAND[0] - 4, 404), (548, 396),
                    (528, 350), (520, 280), (519, 216)])
    ink.stroke(cable, "cable", width=2.6, taper=0.0)
    box(ink, rounded_rect(507, WALL, 531, 216, 3), "plug", width=2.4)


def draw_bed(ink):
    ink.floor(WALL, key="wall", width=3.0)
    box(ink, rounded_rect(*BED, 10), "bed")
    ink.line((BED[0] + 4, HEAD_BOARD), (BED[2] - 4, HEAD_BOARD), "headboard", width=3.5)
    box(ink, rounded_rect(BED[0] + 12, HEAD_BOARD + 10, BED[2] - 12, BED[3] - 10, 16), "mattress",
        width=2.6)
    box(ink, rounded_rect(*PILLOW, 40), "pillow", width=3.5)


def _faded(alpha):
    return (*ROOM[:3], int(ROOM[3] * alpha))


def draw_blanket(ink, b, thrown=0.0):
    """The blanket from his chest down. b is the breath: his chest rises under it.

    thrown: 0 = covering him, 1 = thrown back toward the nightstand, half off the bed.
    """
    top = BLANKET_TOP - 6 * b
    left, right, bottom = BED[0] - 14, BED[2] + 14, BED[3] + 14
    covering = [(left + 4, top + 8), (HERO_X, top - 2 - 2 * b), (right - 4, top + 6), (right, 640),
                (right + 2, bottom), (left - 2, bottom), (left, 640)]
    bunched = [(left - 100, top + 36), (left - 30, top + 22), (left + 30, top + 44), (left + 40, 650),
               (left + 26, bottom - 34), (left - 108, bottom - 14), (left - 116, 650)]
    u = thrown * thrown * (3 - 2 * thrown)
    pts = [(x0 + (x1 - x0) * u, y0 + (y1 - y0) * u) for (x0, y0), (x1, y1) in zip(covering, bunched)]
    ink.fill(smooth(pts, per_segment=8), "blanket.fill", color=BG, wobble=0)
    ink.stroke(smooth([pts[6], pts[0], pts[1], pts[2], pts[3]]), "blanket.edge", width=3.5)
    ink.line(pts[3], pts[4], "blanket.side.r", width=3.2)
    ink.line(pts[6], pts[5], "blanket.side.l", width=3.2)

    # the details of the blanket lying over him fade as it's thrown off...
    a = max(0.0, 1 - 2.5 * thrown)
    if a > 0:
        kw = {} if a == 1 else {"color": _faded(a)}
        # the turned-down fold across his chest: its middle lifts as his chest rises
        ink.stroke(smooth([(left + 6, top + 50), (HERO_X - 110, top + 46 - 4 * b), (HERO_X + 100, top + 47 - 4 * b),
                           (right - 6, top + 52)]), "blanket.fold", width=2.6, **kw)
        # underneath: a soft ridge along each leg, and the bumps of his feet
        for side in (-1, 1):
            ridge = smooth([(HERO_X + side * 14, 640), (HERO_X + side * 30, 730), (HERO_X + side * 52, 812)])
            ink.stroke(ridge, f"blanket.leg{side}", width=2.0, taper=0.8, **kw)
            foot = HERO_X + side * 50
            ink.curve((foot - 24, 846), (foot, 812), (foot + 24, 846), f"blanket.foot{side}", width=2.4, **kw)
        # a few creases toward the sides
        for i, (x0, y0, x1, y1) in enumerate(((left + 40, 560, left + 95, 610), (left + 30, 760, left + 80, 735),
                                              (right - 36, 590, right - 88, 640), (right - 46, 800, right - 96, 790))):
            ink.curve((x0, y0), ((x0 + x1) / 2, (y0 + y1) / 2 + 10), (x1, y1), f"blanket.crease{i}",
                      width=2.0, **kw)
    # ...and the folds of the bunched-up blanket appear
    if thrown > 0.4:
        kw = {"color": _faded(min(1.0, (thrown - 0.4) / 0.4))}
        for i, (x, y0, y1, sway) in enumerate(((left - 70, top + 60, 660, 14), (left - 30, top + 52, 720, -12),
                                               (left + 4, 600, 800, 10), (left - 52, 700, bottom - 40, -14),
                                               (left - 14, 820, bottom - 30, 8))):
            ink.curve((x, y0), (x + sway, (y0 + y1) / 2), (x - sway / 2, y1), f"blanket.bunch{i}", width=2.2, **kw)
