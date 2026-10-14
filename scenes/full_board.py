"""Film 1, row 18 of the story: the full board. About 11.5 seconds, one shot. Night, about a month after row 17.

The days have run out of the START column, down the middle of the board, under his goals and over them,
smaller and more crooked, until his goals are nearly buried in red (door_wall.MORE_DAYS).

 0-8.2 s    Close up on the bottom right of the board, where the last day, MONDAY, is squeezed in small under
            the column. His arm comes up from the bottom right, takes the red marker and slashes MONDAY out
            (the empty discipline bar flickers red). He puts it back and lifts the pale marker to write the
            next day, and there's no room left anywhere: its tip goes to the gap beside MONDAY, up beside
            SATURDAY, across under the middle column, and stops. It hangs there; he puts it back, and his arm
            drops away.
 7.8-11.5 s The camera slowly pulls back to show the whole board in the dark: a wall of red.

No caption. Sound: the hum, the markers on the tray, the slash, the bar's flicker, and then nothing.
"""
import scenes.new_goals as goals
from scenes.discipline import Discipline
from scenes.door_wall import at, day_names, draw_board
from scenes.the_board import CLOSE
from scenes.tomorrow_again import BoardArm
from toolkit import Camera, Track
from toolkit import sound as sk

PEAK_DB = -7.4          # set so the hum matches the other scenes
LAST = 28               # the last day: MONDAY, squeezed in under the column
NAMES = day_names(LAST + 1)

BOARD = dict(wiped=goals.wiped(goals.DURATION), new_goals=goals.written(goals.DURATION))


def days(crossed=0.0):
    return [(name, 1.0, 1.0 if n < LAST else crossed) for n, name in enumerate(NAMES)]


# Where the pale marker goes looking for room for the next day, each a gap that turns out to be too small:
# beside MONDAY, up beside SATURDAY, across under the middle column.
BESIDE_MONDAY = at(CLOSE, 0.955, 0.94)
BESIDE_SATURDAY = at(CLOSE, 0.96, 0.8)
UNDER_THE_MIDDLE = at(CLOSE, 0.565, 0.94)

ARM_IN = 0.6                                    # after a moment to take in the crowded corner, his arm rises
GRAB_RED = ARM_IN + 0.75                        # takes the red marker...
CROSS = (GRAB_RED + 0.8, GRAB_RED + 1.0)        # ...and slashes MONDAY out, quickly, without looking
PUT_RED = CROSS[1] + 0.85
GRAB_PALE = PUT_RED + 0.35                      # takes the pale one to write the next day...
LIFTED = GRAB_PALE + 0.3
SEARCH = [(LIFTED + 0.5, BESIDE_MONDAY), (LIFTED + 0.85, BESIDE_MONDAY),        # ...no room beside it...
          (LIFTED + 1.35, BESIDE_SATURDAY), (LIFTED + 1.7, BESIDE_SATURDAY),    # ...nor up there...
          (LIFTED + 2.3, UNDER_THE_MIDDLE), (LIFTED + 3.0, UNDER_THE_MIDDLE)]   # ...nor here. It hangs there.
PUT_PALE = SEARCH[-1][0] + 0.8                  # he puts it back
ARM_OUT = PUT_PALE + 0.5                        # and his arm drops away
PULL_BACK = (PUT_PALE + 0.1, PUT_PALE + 2.8)    # the camera slowly pulls back to the whole board
DURATION = round(PULL_BACK[1] + 1.0, 2)         # and holds on it

# The close-up's top edge falls between two rows of days, so no word is cut in half.

arm = BoardArm(LAST, NAMES[LAST], None, ARM_IN, GRAB_RED, None, CROSS, PUT_RED, GRAB_PALE, None, PUT_PALE, ARM_OUT,
               lift=0.3, search=SEARCH)

camera = Camera(x=Track((0, 1300), (PULL_BACK[0], 1290, "linear"), (PULL_BACK[1], 960, "inout")),
                y=Track((0, 708), (PULL_BACK[0], 706, "linear"), (PULL_BACK[1], 523, "inout")),
                zoom=Track((0, 1.7), (PULL_BACK[0], 1.72, "linear"), (PULL_BACK[1], 0.97, "inout"),
                           (DURATION, 0.95, "linear")),
                name="fullboard")


def draw(canvas, t, frame):
    with camera.view(canvas, t):
        draw_board(canvas, frame, CLOSE, days(arm.crossed(t)), on_tray=arm.on_tray(t), **BOARD)
        arm.draw(canvas, frame, t)


bar = Discipline(flickers=[CROSS[1] - 0.1])  # empty: a red flicker as he slashes the last day


def overlay(canvas, t, frame):
    bar.draw(canvas, t, frame)


def soundtrack():
    mix = sk.Mix(DURATION)
    mix.add(sk.pad(["A1", "E2"], DURATION, attack=0.4, release=1.0, brightness=0.05, key="hum"),
            at=0, gain_db=-17, reverb=0.2)

    def effect(prompt, seconds, name):            # ElevenLabs effects, all brought to the same level first
        return sk.normalize(sk.eleven_sound(prompt, seconds, name))

    mix.add(sk.whoosh(0.5, peak=0.6, low=150, high=700, key="fullboard.arm"), at=ARM_IN, gain_db=-24, reverb=0.1)
    tray = effect("A plastic marker pen put down on a whiteboard's metal tray, one small light click", 0.5,
                  "marker_tray")
    for i, at_ in enumerate((GRAB_RED, PUT_RED, GRAB_PALE, PUT_PALE)):
        mix.add(tray, at=at_ - 0.2, gain_db=-20 - 2 * (i % 2), pan=0.2, reverb=0.08)
    cross = effect("Close-up of one quick squeaky stroke of a dry-erase marker across a whiteboard, "
                   "crossing out a word", 0.8, "marker_cross")
    mix.add(sk.fade_edges(cross[:int((CROSS[1] - CROSS[0] + 0.08) * sk.SR)], 0.005, 0.05), at=CROSS[0],
            gain_db=-16, pan=0.2, reverb=0.08)
    bar.add_sounds(mix)
    return mix
