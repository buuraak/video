"""Timing helpers: easing curves and keyframe tracks."""
import bisect
import math


def clamp(x, lo=0.0, hi=1.0):
    return lo if x < lo else hi if x > hi else x


def lerp(a, b, u):
    """Blend from a to b. Works on numbers and on tuples like (x, y)."""
    if isinstance(a, (tuple, list)):
        return tuple(lerp(x, y, u) for x, y in zip(a, b))
    return a + (b - a) * u


def ease(u, kind="inout"):
    """Shape a 0..1 progress value. kind: linear, in, out, inout, smooth."""
    u = clamp(u)
    if kind == "linear":
        return u
    if kind == "in":
        return u * u * u
    if kind == "out":
        return 1 - (1 - u) ** 3
    if kind == "smooth":
        return u * u * (3 - 2 * u)
    return 4 * u * u * u if u < 0.5 else 1 - (-2 * u + 2) ** 3 / 2


def progress(t, start, end, kind="inout"):
    """Eased 0..1 progress of time t through the window start..end."""
    if end <= start:
        return 1.0 if t >= end else 0.0
    return ease((t - start) / (end - start), kind)


class Track:
    """A value that changes over time through keyframes.

    Track((0, 1.0), (2, 1.4, "out"), (5, 1.4)) holds 1.0, eases to 1.4 by
    2 seconds, then stays. The easing named on a key shapes the move INTO it.
    Values can be numbers or tuples.
    """

    def __init__(self, *keys):
        self.keys = sorted(keys, key=lambda k: k[0])
        self.times = [k[0] for k in self.keys]

    def __call__(self, t):
        keys = self.keys
        if t <= keys[0][0]:
            return keys[0][1]
        if t >= keys[-1][0]:
            return keys[-1][1]
        i = bisect.bisect_right(self.times, t)
        k0, k1 = keys[i - 1], keys[i]
        kind = k1[2] if len(k1) > 2 else "inout"
        return lerp(k0[1], k1[1], progress(t, k0[0], k1[0], kind))


def pulse(t, rate=1.0):
    """Gentle 0..1..0 breathing cycle, rate in cycles per second."""
    return 0.5 - 0.5 * math.cos(2 * math.pi * rate * t)
