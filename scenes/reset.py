"""Film 1, row 8 of the story: the reset. 4 seconds, one shot.

0-1.3 s    The alarm clock from the front, filling the screen, as in scene 1: 23:59, in the dark.
1.3-2.4 s  The day snaps back. The numbers race backwards through the night and the evening, faster
           and faster, with a tape-rewind whirr that rises as it speeds up...
2.4 s      ...and slam onto 6:00. The camera jolts.
2.55-4 s   The alarm goes off; the numbers blink with its beeps. It keeps ringing into the next scene.

Sound: the hum, the rewind, a thud on the slam, the alarm.
"""
import numpy as np

from scenes.bedroom import ROOM, box, clock_numbers, rounded_rect
from scenes.discipline import Discipline
from scenes.wake_up import BUTTON, CLOCK, TABLE, WINDOW
from toolkit import Camera, Ink, Track
from toolkit import sound as sk

DURATION = 4.0
PEAK_DB = -0.6         # set so the hum matches scenes 1 to 4 (the alarm, just after the thud, is the loudest moment)
REWIND = 1.3           # the numbers start going back...
SLAM = 2.4             # ...and land on 6:00
ALARM = 2.55           # the alarm goes off
START, END = 23 * 60 + 59, 6 * 60        # 23:59 and 6:00, in minutes

camera = Camera(zoom=Track((0, 1.0), (REWIND, 1.02, "linear"), (SLAM, 1.07, "in"), (DURATION, 1.075, "linear")),
                name="reset")
camera.shake(at=SLAM, strength=1.0, length=0.45)


def clock_text(minutes):
    return f"{int(minutes) // 60}:{int(minutes) % 60:02d}"


def minutes_at(t):
    """The time on the clock: slowly at first, then racing, then stopped dead on 6:00."""
    if t < REWIND:
        return START
    if t >= SLAM:
        return END
    u = (t - REWIND) / (SLAM - REWIND)
    return START - (START - END) * u ** 3


def lit(t):
    """While the alarm beeps the numbers blink with it."""
    if t >= ALARM:
        return 1.0 if sk.alarm_on(t - ALARM) else 0.0
    return 1.0


NUMBERS_AT = ((WINDOW[0] + WINDOW[2]) / 2, (WINDOW[1] + WINDOW[3]) / 2 + 2)
NUMBERS_SIZE = 320


def numbers_racing(canvas, t, frame):
    """The numbers, with a fading trail of the times just shown while they race."""
    if REWIND < t < SLAM:
        for k, fade in ((3, 0.12), (2, 0.22), (1, 0.4)):
            clock_numbers(canvas, frame - k, clock_text(minutes_at(t - k / 30)), NUMBERS_AT, NUMBERS_SIZE,
                          "clock.big", on=fade)
    clock_numbers(canvas, frame, clock_text(minutes_at(t)), NUMBERS_AT, NUMBERS_SIZE, "clock.big", on=lit(t))


def draw(canvas, t, frame):
    with camera.view(canvas, t):
        ink = Ink(canvas, frame, color=ROOM, width=8.0, prefix="clock")
        ink.floor(TABLE, key="table", width=6.0)
        ink.floor(TABLE + 22, key="table.front", width=5.0)
        box(ink, rounded_rect(BUTTON[0], BUTTON[1], BUTTON[2], BUTTON[3] + 6, 12), "button", width=7.0)
        box(ink, rounded_rect(*CLOCK, 84), "body", width=9.0)
        box(ink, rounded_rect(*WINDOW, 44), "window", width=6.0)
        numbers_racing(canvas, t, frame)


def rewind_sound():
    """The ElevenLabs tape rewind, played faster and faster so it rises in pitch, cut dead at the slam."""
    tape = sk.normalize(sk.eleven_sound("A cassette tape rewinding very fast in a tape deck, a high mechanical "
                                        "whirr that speeds up and rises in pitch, close up", 1.5, "tape_rewind"))
    n = int((SLAM - REWIND) * sk.SR)
    speed = 0.7 + 1.3 * np.linspace(0, 1, n) ** 2           # from slower than recorded to twice as fast
    pos = np.cumsum(speed)
    pos = pos * min(1.0, (len(tape) - 2) / pos[-1])
    out = np.interp(pos, np.arange(len(tape)), tape)
    out *= np.linspace(0.35, 1.0, n) ** 1.5                  # swelling as it speeds up
    return sk.fade_edges(out, 0.08, 0.004)


bar = Discipline()  # still empty


def overlay(canvas, t, frame):
    bar.draw(canvas, t, frame)


def soundtrack():
    mix = sk.Mix(DURATION)
    mix.add(sk.pad(["A1", "E2"], DURATION, attack=0.4, release=1.0, brightness=0.05, key="hum"),
            at=0, gain_db=-17, reverb=0.2)
    mix.add(rewind_sound(), at=REWIND, gain_db=-9, reverb=0.08)
    mix.add(sk.thud(0.8, key="reset.slam"), at=SLAM, gain_db=-12, reverb=0.15)
    mix.add(sk.alarm(DURATION - ALARM + 0.5), at=ALARM, gain_db=-5, reverb=0.12)
    return mix
