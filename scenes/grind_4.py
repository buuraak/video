"""Film 1, row 16 of the story: grind 4, the fourth loop of the grind. About 2 seconds, two shots joined by a
hard cut: the bed shot drops out now, the days are blurring together. It follows row 15, where he slashed
FRIDAY.

 0-0.7 s    The alarm clock from the front, silent: 14:05. Later again.
 0.7-2.2 s  The board close up, a little wider than before so the whole column fits, SATURDAY already written
            on the last line with room: an even more careless slash through it (the empty discipline bar
            flickers red), and cut.

No caption. Sound: the hum, the marker, the bar's flicker.
"""
import scenes.new_goals as goals
from scenes.discipline import Discipline
from scenes.door_wall import draw_board
from scenes.grind_2 import draw_clock
from scenes.the_board import CLOSE
from scenes.tomorrow_again import BoardArm
from toolkit import Camera, Track
from toolkit import sound as sk

DURATION = 2.2
PEAK_DB = -7.3          # set so the hum matches the other scenes
TIME = "14:05"
BOARD_SHOT = 0.7       # cut to the board

BOARD = dict(wiped=goals.wiped(goals.DURATION), new_goals=goals.written(goals.DURATION))


def days(crossed=0.0):
    return [("MONDAY", 1.0, 1.0), ("TUESDAY", 1.0, 1.0), ("WEDNESDAY", 1.0, 1.0), ("THURSDAY", 1.0, 1.0),
            ("FRIDAY", 1.0, 1.0), ("SATURDAY", 1.0, crossed)]


# -- shot 1: the clock, 14:05 --------------------------------------------------------------------

clock_camera = Camera(zoom=Track((0, 1.0), (BOARD_SHOT, 1.015, "linear")), name="grind4.clock")


def shot_clock(canvas, t, frame):
    with clock_camera.view(canvas, t):
        draw_clock(canvas, frame, TIME)


# -- shot 2: an even more careless slash ---------------------------------------------------------------
# The board shot runs in its own time, and starts with the red marker already on its way to SATURDAY. The
# slash itself (door_wall.cross_line) is more crooked than FRIDAY's, and quicker still.

arm = BoardArm(5, "SATURDAY", "SUNDAY", arm_in=0.0, grab_red=0.4, hover=None, cross=(0.85, 1.03), put_red=1.7,
               grab_pale=2.0, write=(2.5, 3.6), put_pale=4.3, arm_out=4.7, lift=0.2)
OFFSET = 0.62 - BOARD_SHOT     # story time = t + OFFSET

# like rows 14 and 15's board, but a little wider and lower, so the whole column fits: START: at the top,
# SATURDAY near the bottom, the markers on the tray just out of the picture
board_camera = Camera(x=Track((BOARD_SHOT, 1190), (DURATION, 1196, "linear")),
                      y=Track((BOARD_SHOT, 532), (DURATION, 530, "linear")),
                      zoom=Track((BOARD_SHOT, 1.26), (DURATION, 1.29, "linear")), name="grind4.board")


def shot_board(canvas, t, frame):
    s = t + OFFSET
    with board_camera.view(canvas, t):
        draw_board(canvas, frame, CLOSE, days(arm.crossed(s)), on_tray=arm.on_tray(s), **BOARD)
        arm.draw(canvas, frame, s)


# -- the scene -------------------------------------------------------------------------------------


def draw(canvas, t, frame):
    if t < BOARD_SHOT:
        shot_clock(canvas, t, frame)
    else:
        shot_board(canvas, t, frame)


bar = Discipline(flickers=[arm.cross[1] - 0.1 - OFFSET])  # empty: a red flicker as he slashes SATURDAY


def overlay(canvas, t, frame):
    bar.draw(canvas, t, frame)


def soundtrack():
    mix = sk.Mix(DURATION)
    mix.add(sk.pad(["A1", "E2"], DURATION, attack=0.4, release=1.0, brightness=0.05, key="hum"),
            at=0, gain_db=-17, reverb=0.2)
    cross = sk.normalize(sk.eleven_sound("Close-up of one quick squeaky stroke of a dry-erase marker across a "
                                         "whiteboard, crossing out a word", 0.8, "marker_cross"))
    a, b = arm.cross
    mix.add(sk.fade_edges(cross[:int((b - a + 0.08) * sk.SR)], 0.005, 0.05), at=a - OFFSET, gain_db=-15, pan=0.2,
            reverb=0.08)
    bar.add_sounds(mix)
    return mix
