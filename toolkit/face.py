"""Faces: eyes that open and close, eyebrows, mouths, and tired eye bags.

    Face(eyes=0.5, brows="sad", mouth="frown", bags=True)

eyes    1 = wide open, 0 = closed (anything between is a heavy, droopy lid)
brows   None, "flat", "sad", "angry", or a number from -1 (angry) to 1 (sad)
mouth   "flat", "smile", "frown", "open", or "grin" (the enemy's evil grin)
mouth_size  how strong the mouth shape is, 0..1 (lets a smile grow in)
bags    tired bags under the eyes
"""
import math
from dataclasses import dataclass, replace

import numpy as np

from .anim import clamp
from .rng import rand
from .style import BG

BROWS = {"flat": 0.0, "sad": 1.0, "angry": -1.0}


@dataclass
class Face:
    eyes: float = 1.0
    brows: object = None
    mouth: str = "flat"
    mouth_size: float = 1.0
    bags: bool = False

    def but(self, **changes):
        return replace(self, **changes)


# Ready-made faces
NEUTRAL = Face()
TIRED = Face(eyes=0.5, brows="sad", mouth="frown", mouth_size=0.55, bags=True)
SAD = Face(eyes=0.8, brows="sad", mouth="frown")
ANGRY = Face(eyes=0.75, brows="angry", mouth="frown", mouth_size=0.5)
SHOCKED = Face(eyes=1.0, brows="sad", mouth="open")
HAPPY = Face(eyes=1.0, brows="flat", mouth="smile")
EVIL = Face(eyes=0.7, brows="angry", mouth="grin")


def blink(t, name="hero", every=3.5, length=0.16):
    """How open the eyes are at time t (seconds): 1, dipping to 0 for natural blinks.

    Multiply a face's eyes by this. Blink timing is stable for each name.
    """
    slot = math.floor(t / every)
    best = 1.0
    for s in (slot - 1, slot, slot + 1):
        at = s * every + rand("blink", name, s) * (every - length)
        d = abs(t - at) / (length / 2)
        best = min(best, clamp(d))
    return best


def draw_face(ink, center, r, face, tilt=0.0, facing=0, head_fill=BG):
    """Draw a face inside a head of radius r centred at `center`."""
    c, s = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
    shift = 0.26 * facing
    w = ink.width

    def at(x, y):
        x += shift
        return (center[0] + r * (x * c - y * s), center[1] + r * (x * s + y * c))

    def pts(arr):
        return [at(x, y) for x, y in arr]

    def bend(a, ctrl, b, n=20):
        t = np.linspace(0, 1, n)[:, None]
        a, ctrl, b = (np.asarray(v, dtype=float) for v in (a, ctrl, b))
        return (1 - t) ** 2 * a + 2 * (1 - t) * t * ctrl + t ** 2 * b

    eye_y, eye_dx = -0.05, 0.36
    rx, ry = 0.11, 0.155
    e = clamp(face.eyes)

    for side, sx in (("_l", -1), ("_r", 1)):
        ex = sx * eye_dx
        # eye: a dark oval, with the upper lid coming down over it
        lid = eye_y - ry + 2 * ry * (1 - e)
        if e > 0.08:
            ink.blob(at(ex, eye_y), rx * r, ry * r, "eye" + side, rotation=math.radians(tilt))
        if e < 0.97:
            if e > 0.08:
                cover = [(ex - rx * 1.6, eye_y - ry * 1.5), (ex + rx * 1.6, eye_y - ry * 1.5),
                         (ex + rx * 1.6, lid), (ex - rx * 1.6, lid)]
                ink.fill(pts(cover), "lidcover" + side, color=head_fill, wobble=0)
            sag = 0.04 if e > 0.08 else 0.07
            ink.curve(at(ex - rx * 1.5, lid), at(ex, lid + sag), at(ex + rx * 1.5, lid),
                      "lid" + side, width=w * 0.8)
        if face.bags:
            by = eye_y + ry + 0.08
            ink.curve(at(ex - rx * 1.3, by), at(ex, by + 0.12), at(ex + rx * 1.3, by),
                      "bag" + side, width=w * 0.5)
        # brows: sad lifts the inner ends, angry pushes them down
        if face.brows is not None:
            b = BROWS.get(face.brows, face.brows) if isinstance(face.brows, str) else face.brows
            by = eye_y - 0.33
            inner, outer = ex - sx * 0.14, ex + sx * 0.17
            ink.line(at(outer, by + 0.05 * b), at(inner, by - 0.15 * b), "brow" + side, width=w * 0.85)

    m = clamp(face.mouth_size)
    my = 0.47
    if face.mouth in ("flat", "smile", "frown"):
        curve = {"flat": 0.0, "smile": 0.28, "frown": -0.24}[face.mouth] * m
        half = 0.22
        ink.curve(at(-half, my - curve * 0.3), at(0, my + curve), at(half, my - curve * 0.3), "mouth")
    elif face.mouth == "open":
        mw, mh = 0.13 * r * (0.6 + 0.4 * m), 0.16 * r * m + w * 0.6
        ink.blob(at(0, my + 0.03), mw + w / 2, mh + w / 2, "mouth.out", rotation=math.radians(tilt))
        ink.blob(at(0, my + 0.03), max(mw - w / 2, 1), max(mh - w / 2, 1), "mouth.in",
                 color=head_fill, rotation=math.radians(tilt), wobble=0)
    elif face.mouth == "grin":
        half, corner_y = 0.48 * (0.7 + 0.3 * m), 0.22
        upper = bend((-half, corner_y), (0, 0.42), (half, corner_y))
        lower = bend((-half, corner_y), (0, 0.42 + 0.5 * m), (half, corner_y))
        ink.fill(pts(np.vstack([upper, lower[::-1]])), "grin.inside", color=head_fill, wobble=0)
        # sharp teeth hanging from the upper lip
        teeth = []
        n = 7
        for i in range(n * 2 + 1):
            u = 0.07 + 0.86 * i / (n * 2)          # position along the lip, inset from the corners
            y_lip = corner_y + 2 * u * (1 - u) * (0.42 - corner_y) + 0.01
            teeth.append((-half + 2 * half * u, y_lip + (0.13 * m if i % 2 else 0.0)))
        ink.stroke(pts(teeth), "grin.teeth", width=w * 0.55, taper=0.0)
        ink.stroke(pts(upper), "grin.upper", width=w * 0.9)
        ink.stroke(pts(lower), "grin.lower", width=w * 0.9)


def draw_head(ink, center, r, face=None, tilt=0.0, facing=0, head_fill=BG, key="head"):
    """A head on its own (handy for close-ups)."""
    ink.circle(center, r, key, fill=head_fill)
    if face is not None:
        draw_face(ink, center, r, face, tilt, facing, head_fill)
