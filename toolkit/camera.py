"""The camera: zoom, move, and shake.

By default it always drifts a little, as if someone is holding it (the style
bible's handheld look). Position, zoom and angle can be fixed numbers or
Tracks that change over time.

    cam = Camera(zoom=Track((0, 1.0), (3, 1.4)), x=Track((0, 960), (3, 700)))
    cam.shake(at=2.5, strength=1.0)          # a jolt, e.g. on a thud
    with cam.view(canvas, t):
        ...draw the scene...

World coordinates match the screen when the camera is at rest: x=960, y=540,
zoom=1 shows exactly the 1920x1080 area.
"""
import math
from contextlib import contextmanager

from .rng import noise
from .style import H, W

HANDHELD_DRIFT = 9.0     # pixels the handheld camera wanders
HANDHELD_TILT = 0.35     # degrees the handheld camera tilts
JOLT = 26.0              # pixels a full-strength shake knocks the camera


def _value(v, t):
    return v(t) if callable(v) else v


class Camera:
    def __init__(self, x=W / 2, y=H / 2, zoom=1.0, angle=0.0, handheld=1.0, name="camera"):
        """handheld: how shaky the held camera feels (0 = locked on a tripod, 1 = normal)."""
        self.x, self.y, self.zoom, self.angle = x, y, zoom, angle
        self.handheld = handheld
        self.name = name
        self.jolts = []

    def shake(self, at, strength=1.0, length=0.5):
        """A sudden shake starting at time `at` (seconds) that dies away over `length` seconds."""
        self.jolts.append((at, strength, length))
        return self

    def state(self, t):
        """Where the camera is at time t: (x, y, zoom, angle in degrees), shake included."""
        h = _value(self.handheld, t)
        n = self.name
        sx = h * HANDHELD_DRIFT * (noise(t * 0.4, n, "x") + 0.3 * noise(t * 1.7, n, "x2"))
        sy = h * HANDHELD_DRIFT * 0.8 * (noise(t * 0.35, n, "y") + 0.3 * noise(t * 1.9, n, "y2"))
        sa = h * HANDHELD_TILT * noise(t * 0.3, n, "angle")
        for i, (at, strength, length) in enumerate(self.jolts):
            if at <= t <= at + length:
                fade = (1 - (t - at) / length) ** 2
                k = strength * JOLT * fade
                sx += k * noise(t * 22, n, "jolt", i, "x")
                sy += k * noise(t * 22, n, "jolt", i, "y")
                sa += strength * 1.2 * fade * noise(t * 18, n, "jolt", i, "a")
        return (_value(self.x, t) - sx, _value(self.y, t) - sy,
                _value(self.zoom, t), _value(self.angle, t) + sa)

    @contextmanager
    def view(self, canvas, t):
        """Everything drawn inside this block is seen through the camera."""
        x, y, zoom, angle = self.state(t)
        canvas.save()
        canvas.translate(W / 2, H / 2)
        canvas.rotate(angle)
        canvas.scale(zoom, zoom)
        canvas.translate(-x, -y)
        try:
            yield
        finally:
            canvas.restore()

    def to_screen(self, point, t):
        """Where a world point ends up on screen at time t."""
        x, y, zoom, angle = self.state(t)
        dx, dy = (point[0] - x) * zoom, (point[1] - y) * zoom
        c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
        return (W / 2 + dx * c - dy * s, H / 2 + dx * s + dy * c)
