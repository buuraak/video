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


# His empty bottles (the user's choice, sheets/bottle_options.png option 2): one tipped over on the nightstand
# by the clock, one on the floor by the bed. As (middle, angle in degrees, length, thickness).
BOTTLES = [((759, 268), 95, 88, 15), ((690, 485), -12, 92, 15)]


def draw_bottle(ink, middle, angle, key, length=88, r=15):
    """An empty bottle lying on its side, seen from above: body with a label, round shoulder, long neck."""
    x, y = middle
    body_end = x + length * 0.12
    body = rounded_rect(x - length / 2, y - r, body_end, y + r, r * 0.45)
    shoulder = [(body_end - 2, y - r * 0.92), (body_end + r * 0.9, y - r * 0.42), (body_end + r * 0.9, y + r * 0.42),
                (body_end - 2, y + r * 0.92)]
    neck = rounded_rect(body_end + r * 0.85, y - r * 0.38, x + length / 2, y + r * 0.38, 3)
    box(ink, turned(body, middle, angle), key, width=3.0)
    box(ink, turned(shoulder, middle, angle), key + ".shoulder", width=2.6)
    box(ink, turned(neck, middle, angle), key + ".neck", width=2.6)
    for i, lx in enumerate((x - length * 0.3, x - length * 0.05)):     # the label
        ink.line(*turned([(lx, y - r + 2), (lx, y + r - 2)], middle, angle), f"{key}.label{i}", width=2.0)


# The mess on the floor, which grows with each loop of the grind (film 1, rows 13-17): his clothes first.
# Each piece as (middle, angle in degrees). Seen from above, crumpled, in the room's dim lines.
TSHIRT = ((1335, 812), 24)
JEANS = ((1372, 452), -14)
CUPS = [((622, 392), 30), ((706, 640), 150), ((1292, 640), -60)]    # (middle, which way the handle points)
PIZZA = ((470, 760), -10)        # the open box's bottom half; its lid lies flat behind it, toward the wall
STAIN = (34, 32, 29)             # grease soaked into cardboard


def _crumpled(points, key, amount=6.0):
    """Points pushed about a little (the same every run), so a piece of clothing looks crumpled, not ironed."""
    from toolkit.rng import rng
    g = rng("mess", key)
    return [(x + g.uniform(-amount, amount), y + g.uniform(-amount, amount)) for x, y in points]


def draw_tshirt(ink, middle, angle, key="tshirt"):
    """A T-shirt dropped on the floor: body, sleeves, the neckline, and a couple of folds."""
    x, y = middle
    shape = [(-24, -70), (-58, -60), (-98, -30), (-80, 0), (-54, -16), (-50, 72), (54, 70), (50, -16), (80, 2),
             (96, -34), (58, -62), (24, -70), (12, -56), (-10, -55)]
    pts = _crumpled([(x + dx, y + dy) for dx, dy in shape], key)
    box(ink, turned(pts, middle, angle), key, width=3.0)
    for i, ((ax, ay), (bx, by)) in enumerate((((-36, 6), (8, 30)), ((14, -30), (36, 40)))):   # folds
        ink.line(*turned([(x + ax, y + ay), (x + bx, y + by)], middle, angle), f"{key}.fold{i}", width=2.0)


def draw_jeans(ink, middle, angle, key="jeans"):
    """Jeans kicked off on the floor: the waistband, one leg straight, the other bent over to the side."""
    x, y = middle
    shape = [(-58, -96), (58, -96), (62, -78), (66, -14), (122, 34), (146, 84), (110, 104), (86, 58), (30, 16),
             (8, 4), (-6, 108), (-62, 108), (-62, -78)]
    pts = _crumpled([(x + dx, y + dy) for dx, dy in shape], key, 4.0)
    box(ink, turned(pts, middle, angle), key, width=3.0)
    for i, ((ax, ay), (bx, by)) in enumerate((((-60, -78), (62, -78)), ((0, -78), (2, -30)),     # waistband, fly
                                              ((-48, -70), (-30, -50)), ((48, -70), (30, -50)))):  # pockets
        ink.line(*turned([(x + ax, y + ay), (x + bx, y + by)], middle, angle), f"{key}.line{i}", width=2.0)


def draw_cup(ink, middle, angle, key="cup", r=21):
    """A used mug seen from above: its rim, the dried coffee ring inside, and the handle."""
    x, y = middle
    handle = turned(rounded_rect(x + r - 4, y - 7, x + r + 15, y + 7, 6), middle, angle)
    box(ink, handle, key + ".handle", width=2.6)
    ink.circle(middle, r, key, fill=BG, width=3.0)
    ink.circle(middle, r * 0.68, key + ".ring", fill=(40, 38, 36), width=1.6)


def draw_slice(ink, middle, angle, size, key, width=2.2):
    """A slice of pizza, `size` long: a wide triangle, its crust along the wide end, three pepperoni."""
    x, y = middle

    def arc(r):
        return [(x + r * math.sin(math.radians(a)), y - size * 0.5 + r * math.cos(math.radians(a)))
                for a in np.linspace(-30, 30, 7)]

    ink.stroke(turned([(x, y - size * 0.5)] + arc(size), middle, angle), key, closed=True, width=width)
    ink.stroke(turned(arc(size * 0.82)[1:-1], middle, angle), key + ".crust", width=width * 0.8)
    for i, (dx, dy) in enumerate(((-0.11, 0.12), (0.12, 0.2), (0.0, -0.06))):
        ink.circle(turned([(x + dx * size, y + dy * size)], middle, angle)[0], size * 0.075, f"{key}.pep{i}",
                   width=width * 0.8)


def _grease(ink, middle, r, angle, key):
    """A grease spot soaked into the cardboard: a soft round patch."""
    pts = [(middle[0] + r * math.cos(a) * (1 + 0.08 * math.sin(3 * a)), middle[1] + r * 0.8 * math.sin(a))
           for a in np.linspace(0, 2 * math.pi, 16, endpoint=False)]
    ink.fill(turned(pts, middle, angle), key, color=STAIN, wobble=0)


def draw_pizza_box(ink, middle, angle, key="pizza", size=136):
    """An open pizza box seen from above (the user's pick, sheets/pizza_options.png option 2): the lid lies
    flat behind it, toward the wall; inside, grease spots, two crusts and one slice left."""
    x, y = middle
    s = size / 2
    for part, (y0, y1) in (("lid", (y - 3 * s, y - s)), ("base", (y - s, y + s))):
        box(ink, turned(rounded_rect(x - s, y0, x + s, y1, 5), middle, angle), f"{key}.{part}", width=3.0)
        ink.stroke(turned(rounded_rect(x - s + 9, y0 + 9, x + s - 9, y1 - 9, 3), middle, angle), f"{key}.{part}.in",
                   closed=True, width=1.6)
    _grease(ink, turned([(x - 18, y - size + 10)], middle, angle)[0], 15, angle, key + ".lid.stain")
    _grease(ink, turned([(x - 20, y + 16)], middle, angle)[0], 22, angle, key + ".stain")
    for i, (c, r, a0, a1) in enumerate((((x - 10, y - 2), 44, 200, 265), ((x + 6, y + 4), 40, 25, 95))):
        outer = [(c[0] + r * math.cos(math.radians(a)), c[1] + r * math.sin(math.radians(a)))
                 for a in np.linspace(a0, a1, 9)]
        inner = [(c[0] + (r - 9) * math.cos(math.radians(a)), c[1] + (r - 9) * math.sin(math.radians(a)))
                 for a in np.linspace(a1, a0, 9)]
        box(ink, turned(outer + inner, middle, angle), f"{key}.crust{i}", width=2.2)     # a crust, left
    draw_slice(ink, turned([(x + 24, y - 6)], middle, angle)[0], angle + 150, 62, key + ".slice")


def draw_mess(ink, items):
    """The mess on the floor: any of "clothes", "cups" and "pizza"."""
    if "clothes" in items:
        draw_jeans(ink, *JEANS)
        draw_tshirt(ink, *TSHIRT)
    if "cups" in items:
        for i, (middle, angle) in enumerate(CUPS):
            draw_cup(ink, middle, angle, f"cup{i}")
    if "pizza" in items:
        draw_pizza_box(ink, *PIZZA)


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
    """The nightstand: the alarm clock showing `time`, the phone on its charger, and his empty bottles
    (one on the nightstand, one on the floor beside it).

    phone=False: the phone has been taken, and the unplugged charger cable lies loose.
    phone="plugged": it's on the charger, but the scene draws the phone itself (lit up, turned over).
    """
    box(ink, rounded_rect(*NIGHTSTAND, 8), "nightstand")
    # the alarm clock, its top with the button, and its front with the red numbers
    box(ink, rounded_rect(*CLOCK_TOP, 8), "clock.top", width=3.2)
    box(ink, rounded_rect(650, 230, 700, 246, 5), "clock.button", width=2.4)
    box(ink, rounded_rect(*CLOCK_FRONT, 8), "clock.front", width=3.2)
    box(ink, rounded_rect(608, 268, 718, 302, 5), "clock.window", width=2.0)
    clock_numbers(canvas, frame, time, (663, 285), 24, "clock.small")
    plugged = isinstance(phone, str) and phone == "plugged"
    if phone and not plugged:
        draw_phone_on_table(ink)
    elif not phone:   # the plug at the loose end of the cable
        ink.line((PORT[0] + 12, PORT[1] - 1), (PORT[0] - 2, PORT[1] + 1), "cable.plug", width=6.0, taper=0.0)
    # the charging cable: off the nightstand, across the floor, up to the socket on the wall
    cable = smooth([PORT, (PORT[0] - 22, PORT[1] + 6), (NIGHTSTAND[0] - 4, 404), (548, 396),
                    (528, 350), (520, 280), (519, 216)])
    ink.stroke(cable, "cable", width=2.6, taper=0.0)
    box(ink, rounded_rect(507, WALL, 531, 216, 3), "plug", width=2.4)
    for i, (middle, angle, length, r) in enumerate(BOTTLES):      # his empty bottles
        draw_bottle(ink, middle, angle, f"bottle{i}", length, r)


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
