"""Hand-drawn lines.

Every stroke wobbles slightly and changes its width a little along its length,
like a real pen. Strokes are re-drawn every BOIL_EVERY frames: within those
frames a stroke looks exactly the same, then it gets a fresh wobble. Each
stroke needs a key (a name like "hero.arm.L") so it keeps its own wobble.

    ink = Ink(canvas, frame)
    ink.line((100, 100), (400, 120), "floor")
    ink.circle((960, 540), 80, "sun")
"""
import math

import numpy as np
import skia

from .rng import rng
from .style import BOIL_EVERY, INK, LINE_WIDTH, WOBBLE


def to_color(c):
    return skia.Color(int(c[0]), int(c[1]), int(c[2]), int(c[3]) if len(c) > 3 else 255)


def boil(frame: int) -> int:
    """Which drawing of the lines this frame uses. Changes every BOIL_EVERY frames."""
    return frame // BOIL_EVERY


def _resample(pts, step):
    p = np.asarray(pts, dtype=float)
    keep = np.concatenate([[True], np.linalg.norm(np.diff(p, axis=0), axis=1) > 1e-9])
    p = p[keep]
    if len(p) < 2:
        return p, 0.0
    seg = np.linalg.norm(np.diff(p, axis=0), axis=1)
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    length = cum[-1]
    n = max(int(length / step), 8)
    s = np.linspace(0.0, length, n + 1)
    return np.stack([np.interp(s, cum, p[:, 0]), np.interp(s, cum, p[:, 1])], axis=1), length


def _normals(p, closed):
    if closed:
        t = np.roll(p, -1, axis=0) - np.roll(p, 1, axis=0)
    else:
        t = np.gradient(p, axis=0)
    t /= np.maximum(np.linalg.norm(t, axis=1, keepdims=True), 1e-9)
    return np.stack([-t[:, 1], t[:, 0]], axis=1)


def _waves(g, u, freqs, closed):
    """A smooth wandering curve over u in 0..1, made of a few sine waves."""
    out = np.zeros_like(u)
    total = 0.0
    for i, (lo, hi) in enumerate(freqs):
        f = float(g.integers(max(1, round(lo)), round(hi) + 1)) if closed else g.uniform(lo, hi)
        w = 0.5 ** i
        out += w * np.sin(2 * math.pi * f * u + g.uniform(0, 2 * math.pi))
        total += w
    return out / total


class Ink:
    """A hand-drawn pen bound to one canvas and one frame."""

    def __init__(self, canvas, frame, color=INK, width=LINE_WIDTH, wobble=1.0, prefix=""):
        self.canvas = canvas
        self.frame = frame
        self.color = color
        self.width = width
        self.wobble = wobble
        self.prefix = prefix

    def _rng(self, key):
        return rng("ink", self.prefix, key, boil(self.frame))

    def _paint(self, color):
        return skia.Paint(AntiAlias=True, Color=to_color(color or self.color))

    # -- strokes -----------------------------------------------------------

    def stroke(self, pts, key, *, closed=False, pin_ends=False, color=None, width=None,
               wobble=None, taper=0.35):
        """Draw a hand-drawn line through the points.

        pin_ends keeps both ends exactly where you put them (used for joints,
        so limbs stay connected and hands land exactly on their targets).
        taper thins the ends of the stroke a little, like a pen.
        """
        width = self.width if width is None else width
        wobble = self.wobble if wobble is None else wobble
        pts = list(pts)
        if closed:
            pts = pts + [pts[0]]
        p, length = _resample(pts, step=4.0)
        if length < 0.5:
            if len(p):
                self.canvas.drawCircle(p[0][0], p[0][1], width / 2, self._paint(color))
            return
        g = self._rng(key)
        u = np.linspace(0.0, 1.0, len(p))
        n = _normals(p[:-1] if closed else p, closed)
        if closed:
            n = np.vstack([n, n[:1]])

        amp = wobble * WOBBLE * min(max((length / 150.0) ** 0.5, 0.5), 2.0)
        offset = amp * _waves(g, u, [(0.6, 1.4), (1.5, 3.0), (3.0, 5.0)], closed)
        if pin_ends and not closed:
            offset *= np.sin(math.pi * u) ** 0.6
        p = p + n * offset[:, None]

        half = width / 2 * g.uniform(0.92, 1.08) * (1 + 0.14 * _waves(g, u, [(0.8, 2.0)], closed))
        if not closed and taper > 0:
            ends = np.minimum(1.0, np.minimum(u, 1 - u) * length / max(min(length * 0.3, 40.0), 1.0))
            half *= (1 - taper) + taper * np.sqrt(ends)

        self._fill_ribbon(p, half, color)

    def _fill_ribbon(self, p, half, color):
        n = _normals(p, closed=False)
        left = p + n * half[:, None]
        right = p - n * half[:, None]
        outline = np.vstack([left, right[::-1]])
        path = skia.Path()
        path.addPoly([skia.Point(float(x), float(y)) for x, y in outline], True)
        paint = self._paint(color)
        self.canvas.drawPath(path, paint)
        for i in (0, -1):
            self.canvas.drawCircle(float(p[i][0]), float(p[i][1]), float(half[i]), paint)

    def line(self, a, b, key, **kw):
        self.stroke([a, b], key, **kw)

    def floor(self, y, key="floor", x0=-600, x1=2520, width=4.0, color=None):
        """A floor line whose top edge stays at y, so feet placed at y stand on it.

        It changes thickness slightly like a pen, but never drifts up or down
        (an ordinary long line would wobble a few pixels and make characters float).
        The default length runs well past the screen edges, for camera moves.
        """
        self.stroke([(x0, y + width / 2), (x1, y + width / 2)], key, width=width,
                    wobble=0.12, taper=0.0, color=color)

    def curve(self, a, ctrl, b, key, **kw):
        """A smooth bend from a to b, pulled toward ctrl."""
        t = np.linspace(0, 1, 24)[:, None]
        a, ctrl, b = (np.asarray(v, dtype=float) for v in (a, ctrl, b))
        pts = (1 - t) ** 2 * a + 2 * (1 - t) * t * ctrl + t ** 2 * b
        self.stroke(pts, key, **kw)

    def circle(self, center, radius, key, *, fill=None, color=None, width=None, wobble=None):
        """A hand-drawn circle: slightly uneven, and the pen overshoots where it meets itself.

        fill paints the inside first (e.g. the background colour, to hide lines behind a head).
        """
        wobble = self.wobble if wobble is None else wobble
        g = self._rng(key)
        cx, cy = center
        start = g.uniform(0, 2 * math.pi)
        overshoot = g.uniform(0.18, 0.4)
        a = np.linspace(0, 2 * math.pi + overshoot, max(int(radius * 0.8), 48))
        amp = wobble * WOBBLE
        r = (radius
             + amp * 0.8 * np.sin(2 * a + g.uniform(0, 6.3))
             + amp * 0.4 * np.sin(3 * a + g.uniform(0, 6.3))
             # the pen drifts in or out over the loop, so the ends overlap visibly
             + amp * g.choice([-1, 1]) * g.uniform(2.5, 4.0) * a / (2 * math.pi))
        pts = np.stack([cx + r * np.cos(a + start), cy + r * np.sin(a + start)], axis=1)
        if fill is not None:
            ring = pts[a < 2 * math.pi]
            path = skia.Path()
            path.addPoly([skia.Point(float(x), float(y)) for x, y in ring], True)
            self.canvas.drawPath(path, self._paint(fill))
        self.stroke(pts, key + ".line", color=color, width=width, wobble=0.0, taper=0.6)

    def blob(self, center, rx, ry, key, *, color=None, rotation=0.0, wobble=None):
        """A filled, slightly uneven oval (eyes, dots)."""
        wobble = self.wobble if wobble is None else wobble
        g = self._rng(key)
        a = np.linspace(0, 2 * math.pi, 28, endpoint=False)
        k = 1 + 0.06 * wobble * np.sin(2 * a + g.uniform(0, 6.3)) + 0.04 * wobble * np.sin(3 * a + g.uniform(0, 6.3))
        x, y = rx * k * np.cos(a), ry * k * np.sin(a)
        c, s = math.cos(rotation), math.sin(rotation)
        pts = np.stack([center[0] + x * c - y * s, center[1] + x * s + y * c], axis=1)
        self.fill(pts, key, color=color, wobble=0.0)

    def fill(self, pts, key, *, color=None, wobble=None):
        """Fill a closed shape, with a slightly wobbly edge."""
        wobble = self.wobble if wobble is None else wobble
        p = np.asarray(pts, dtype=float)
        if wobble > 0:
            p, _ = _resample(np.vstack([p, p[:1]]), step=6.0)
            p = p[:-1]
            g = self._rng(key + ".fill")
            u = np.linspace(0, 1, len(p), endpoint=False)
            p = p + _normals(p, closed=True) * (wobble * WOBBLE * 0.6 * _waves(g, u, [(2, 4), (4, 7)], True))[:, None]
        path = skia.Path()
        path.addPoly([skia.Point(float(x), float(y)) for x, y in p], True)
        self.canvas.drawPath(path, self._paint(color))
