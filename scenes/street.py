"""Film 1's street at dawn, seen from the side, shared by the scenes outside. Not a scene itself.

A row of dark buildings across the pavement (nearly every window dark), streetlamps with pools of cold
light, the pavement he runs along (GROUND) and the kerb in front of it. The sky is a little lighter and
greyer low down: it's just before sunrise. The street runs on as far as needed to either side, the same
on every run, so the camera can follow him along it.

    draw_street(canvas, frame, view=(x0, x1))     # draw only what's between x0 and x1 (what the camera sees)
"""
import numpy as np
import skia

from scenes.bedroom import ROOM, box, rounded_rect
from scenes.scroll import glow
from toolkit import GREY, Ink, to_color
from toolkit.rng import rng

GROUND = 860                 # the pavement line he runs on
FACADES = 760                # where the buildings meet the far side of the pavement
KERB = GROUND + 46
SKY_TOP, SKY_LOW = (14, 14, 17), (40, 44, 54)
LAMP_LIGHT = (200, 210, 230)
LAMPS = 1300                 # a streetlamp every this many pixels
START = -2000                # the street begins here...
BUILDINGS_TO = 9000          # ...and runs to here


def _buildings():
    """Every building along the street: (left x, width, height, seed)."""
    g = rng("street.buildings")
    out, x, i = [], START, 0
    while x < BUILDINGS_TO:
        w, h = g.uniform(220, 380), g.uniform(330, 560)
        out.append((x, w, h, i))
        x += w + g.uniform(10, 40)
        i += 1
    return out


BUILDINGS = _buildings()


def draw_street(canvas, frame, view=(-200, 2200)):
    x0, x1 = view
    sky = skia.GradientShader.MakeLinear([skia.Point(0, 132), skia.Point(0, FACADES)],
                                         [to_color(SKY_TOP), to_color(SKY_LOW)])
    canvas.drawRect(skia.Rect(x0 - 400, -400, x1 + 400, FACADES), skia.Paint(Shader=sky))
    far = Ink(canvas, frame, color=(*GREY, 150), width=3.0, prefix="street")
    for left, w, h, i in BUILDINGS:
        if left + w < x0 - 50 or left > x1 + 50:
            continue
        top = FACADES - h
        box(far, [(left, FACADES), (left, top), (left + w, top), (left + w, FACADES)], f"b{i}", fill=(18, 18, 22))
        g = rng("street.windows", i)
        for wx in np.arange(left + 30, left + w - 40, 62):          # windows, nearly all dark
            for wy in np.arange(top + 40, 720, 80):
                fill = (70, 74, 84) if g.random() < 0.06 else (22, 22, 26)
                box(far, rounded_rect(wx, wy, wx + 26, wy + 38, 2), f"w{i}.{wx:.0f}.{wy:.0f}", fill=fill, width=1.6)
    near = Ink(canvas, frame, color=ROOM, width=4.0, prefix="street.near")
    near.floor(FACADES, key="far.edge", width=3.0, x0=x0 - 400, x1=x1 + 400)
    near.floor(GROUND, key="pavement", width=4.0, x0=x0 - 400, x1=x1 + 400)
    near.floor(KERB, key="kerb", width=4.0, x0=x0 - 400, x1=x1 + 400)
    for n in range(int(np.floor((x0 - 600) / LAMPS)), int(np.ceil((x1 + 600) / LAMPS)) + 1):
        draw_lamp(canvas, near, n * LAMPS + 430, f"lamp{n}")


def draw_lamp(canvas, ink, x, key):
    """A streetlamp at the back of the pavement, its cold light pooling on the ground."""
    top = 300
    glow(canvas, (x + 40, GROUND - 40), 360, LAMP_LIGHT, 0.18)
    ink.line((x, GROUND), (x, top), key + ".pole", width=5.0)
    ink.curve((x, top), (x + 10, top - 40), (x + 60, top - 30), key + ".arm", width=4.0)
    box(ink, rounded_rect(x + 44, top - 30, x + 96, top - 14, 6), key + ".head", width=3.0)
    glow(canvas, (x + 70, top - 14), 90, LAMP_LIGHT, 0.5)
