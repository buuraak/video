"""Film 1, row 14 of the story: grind 2, the second loop of the grind. About 6 seconds, three shots joined by
hard cuts. It follows row 13, where he crossed out WEDNESDAY and wrote THURSDAY.

 0-1.2 s    The alarm clock from the front, as in scene 1, silent: 9:55. Later again.
 1.2-4.2 s  From above, the opening view: he's scrolling in bed, his face in the phone's cold light. The mess
            has grown: cups now, beside the clothes. The phone buzzes in his hands (Sam again; we can't read it)
            and its light flares on his face. He doesn't react, and swipes on.
 4.2-5.8 s  The board close up, on the column of start days: one quick red stroke through THURSDAY (the empty
            discipline bar flickers red), and cut. FRIDAY is already written the next time we see the board.

No caption. Sound: the hum, a reel's muffled voice, the buzz, a swipe, the marker, the bar's flicker.
"""
import math

import scenes.new_goals as goals
from scenes.bedroom import ROOM, box, clock_numbers, rounded_rect
from scenes.discipline import Discipline
from scenes.door_wall import draw_board
from scenes.grind_1 import draw_scrolling, light_level, swiping
from scenes.scroll import reel_sounds
from scenes.the_board import CLOSE
from scenes.tomorrow_again import BoardArm
from scenes.wake_up import BUTTON, CLOCK, TABLE, WINDOW
from toolkit import Camera, Ink, Track, progress
from toolkit import sound as sk

DURATION = 5.8
PEAK_DB = -5.0          # set so the hum matches the other scenes
TIME = "9:55"
ABOVE = 1.2            # cut to the view from above
BOARD_SHOT = 4.2       # cut to the board

BOARD = dict(wiped=goals.wiped(goals.DURATION), new_goals=goals.written(goals.DURATION))


def days(crossed=0.0):
    return [("MONDAY", 1.0, 1.0), ("TUESDAY", 1.0, 1.0), ("WEDNESDAY", 1.0, 1.0), ("THURSDAY", 1.0, crossed)]


# -- shot 1: the clock, 9:55 ---------------------------------------------------------------------

clock_camera = Camera(zoom=Track((0, 1.0), (ABOVE, 1.02, "linear")), name="grind2.clock")


def draw_clock(canvas, frame, time, on=1.0):
    """The alarm clock from the front, as in scene 1, showing `time` (the grind's later and later mornings
    start on it). on: the numbers lit (1) or dark (0), to blink them with the alarm's beeps."""
    ink = Ink(canvas, frame, color=ROOM, width=8.0, prefix="clock")
    ink.floor(TABLE, key="table", width=6.0)
    ink.floor(TABLE + 22, key="table.front", width=5.0)
    box(ink, rounded_rect(BUTTON[0], BUTTON[1], BUTTON[2], BUTTON[3] + 6, 12), "button", width=7.0)
    box(ink, rounded_rect(*CLOCK, 84), "body", width=9.0)
    box(ink, rounded_rect(*WINDOW, 44), "window", width=6.0)
    clock_numbers(canvas, frame, time, ((WINDOW[0] + WINDOW[2]) / 2, (WINDOW[1] + WINDOW[3]) / 2 + 2), 320,
                  "clock.big", on=on)


def shot_clock(canvas, t, frame):
    with clock_camera.view(canvas, t):
        draw_clock(canvas, frame, TIME)


# -- shot 2: from above, scrolling; a message he ignores ---------------------------------------------

BUZZ = ABOVE + 0.9     # the phone buzzes: Sam again
SWIPE = ABOVE + 2.3    # he swipes on, as if nothing came
bed_camera = Camera(name="grind2.bed")


def flare(t):
    """0..1: the message lighting the screen up brighter for a moment."""
    return progress(t, BUZZ, BUZZ + 0.08, "out") * (1 - progress(t, BUZZ + 0.35, BUZZ + 1.1, "inout"))


def shot_bed(canvas, t, frame):
    with bed_camera.view(canvas, t):
        level = light_level(t, [SWIPE], key="grind2.reel") * (1 + 0.7 * flare(t))
        buzzing = 1.0 if BUZZ <= t < BUZZ + 0.35 else 0.0
        draw_scrolling(canvas, frame, t, TIME, ("clothes", "cups"), swiping(t, SWIPE), level, buzz=buzzing,
                       key="grind2")


# -- shot 3: one red stroke ---------------------------------------------------------------------------
# The board shot runs in its own time: it starts with the red marker already on its way to THURSDAY.

arm = BoardArm(3, "THURSDAY", "FRIDAY", arm_in=0.0, grab_red=0.55, hover=None, cross=(1.15, 1.5), put_red=2.2,
               grab_pale=2.5, write=(3.0, 4.2), put_pale=4.9, arm_out=5.3, lift=0.25)
OFFSET = 0.9 - BOARD_SHOT      # story time = t + OFFSET

board_camera = Camera(x=Track((BOARD_SHOT, 1190), (DURATION, 1196, "linear")),
                      y=Track((BOARD_SHOT, 506), (DURATION, 502, "linear")),
                      zoom=Track((BOARD_SHOT, 1.42), (DURATION, 1.46, "linear")), name="grind2.board")


def shot_board(canvas, t, frame):
    s = t + OFFSET
    with board_camera.view(canvas, t):
        draw_board(canvas, frame, CLOSE, days(arm.crossed(s)), on_tray=arm.on_tray(s), **BOARD)
        arm.draw(canvas, frame, s)


# -- the scene -------------------------------------------------------------------------------------


def draw(canvas, t, frame):
    if t < ABOVE:
        shot_clock(canvas, t, frame)
    elif t < BOARD_SHOT:
        shot_bed(canvas, t, frame)
    else:
        shot_board(canvas, t, frame)


bar = Discipline(flickers=[arm.cross[1] - 0.1 - OFFSET])  # empty: a red flicker as he crosses out THURSDAY


def overlay(canvas, t, frame):
    bar.draw(canvas, t, frame)


def soundtrack():
    mix = sk.Mix(DURATION)
    mix.add(sk.pad(["A1", "E2"], DURATION, attack=0.4, release=1.0, brightness=0.05, key="hum"),
            at=0, gain_db=-17, reverb=0.2)
    # a reel's muffled voice from above (the six-pack woman, then the Bugatti man after the swipe), evened as
    # in scene 2
    adam, laura, liam = reel_sounds()
    for clip, a, b, offset, even in ((laura, ABOVE, SWIPE, 2.0, 0.4), (liam, SWIPE, BOARD_SHOT, 9.0, 3.3)):
        part = clip[int(offset * sk.SR):int((offset + b - a) * sk.SR)]
        mix.add(sk.fade_edges(part, 0.01, 0.01), at=a, gain_db=-10 + even, pan=0.1, reverb=0.05)
    mix.add(sk.lowpass(sk.tick(key="grind2.swipe"), 2500), at=SWIPE - 0.02, gain_db=-24, reverb=0.05)

    def effect(prompt, seconds, name):            # ElevenLabs effects, all brought to the same level first
        return sk.normalize(sk.eleven_sound(prompt, seconds, name))

    buzz = effect("A smartphone on a wooden nightstand vibrating with a new text message, a short double buzz, "
                  "close up, in a quiet room", 1.5, "phone_buzz")
    mix.add(sk.fade_edges(sk.lowpass(buzz[int(0.05 * sk.SR):int(0.4 * sk.SR)], 1800), 0.01, 0.04), at=BUZZ,
            gain_db=-16, reverb=0.06)          # one buzz, in his hands, as in row 13
    cross = effect("Close-up of one quick squeaky stroke of a dry-erase marker across a whiteboard, "
                   "crossing out a word", 0.8, "marker_cross")
    a, b = arm.cross
    mix.add(sk.fade_edges(cross[:int((b - a + 0.08) * sk.SR)], 0.005, 0.06), at=a - OFFSET, gain_db=-15, pan=0.2,
            reverb=0.08)
    bar.add_sounds(mix)
    return mix
