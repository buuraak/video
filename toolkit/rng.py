"""Randomness that never changes between runs.

Every random choice is made from a name (like "hero.arm.L" plus a frame
number), so the same frame always looks the same, on any run and in any
process. Never use Python's hash() or an unseeded random for this: hash() of
text changes every time Python starts.
"""
import hashlib
import math

import numpy as np


def seed(*parts) -> int:
    """A stable 64-bit number made from any mix of names and numbers."""
    digest = hashlib.blake2b(repr(parts).encode(), digest_size=8).digest()
    return int.from_bytes(digest, "little")


def rng(*parts) -> np.random.Generator:
    """A numpy random generator that always gives the same numbers for the same parts."""
    return np.random.default_rng(seed(*parts))


def rand(*parts) -> float:
    """One stable number between 0 and 1."""
    return seed(*parts) / 2.0**64


def noise(x: float, *parts, octaves: int = 3) -> float:
    """Smooth wandering value between about -1 and 1, e.g. for handheld camera drift."""
    total, amp, norm, freq = 0.0, 1.0, 0.0, 1.0
    for octave in range(octaves):
        xf = x * freq
        i = math.floor(xf)
        f = xf - i
        f = f * f * f * (f * (f * 6 - 15) + 10)  # smootherstep
        a = rand(*parts, octave, i) * 2 - 1
        b = rand(*parts, octave, i + 1) * 2 - 1
        total += amp * (a + (b - a) * f)
        norm += amp
        amp *= 0.5
        freq *= 2.0
    return total / norm
