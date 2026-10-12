"""Film 1, row 15 of the story: grind 3, the third loop of the grind. About 4 seconds: row 14's three shots,
shorter, joined by hard cuts. It follows row 14, where he crossed out THURSDAY.

 0-0.8 s    The alarm clock from the front, silent: 12:20. Later again.
 0.8-2.8 s  From above, the opening view: he's scrolling in bed, his face in the phone's cold light. An open
            pizza box now lies on the floor by the bed, crusts and one slice left, beside the clothes and
            cups. One swipe. Nothing from Sam this time, only reels: Sam has stopped trying.
 2.8-4.2 s  The board close up, on the column of start days (FRIDAY already written): a careless red slash
            through FRIDAY, quicker and crooked, running past the end of the word (the empty discipline bar
            flickers red), and cut.

No caption. Sound: the hum, the reels' muffled voices, a swipe, the marker, the bar's flicker.
"""
import scenes.new_goals as goals
from scenes.discipline import Discipline
from scenes.door_wall import draw_board
from scenes.grind_1 import draw_scrolling, light_level, swiping
from scenes.grind_2 import draw_clock
from scenes.scroll import reel_sounds
from scenes.the_board import CLOSE
from scenes.tomorrow_again import BoardArm
from toolkit import Camera, Track
from toolkit import sound as sk

DURATION = 4.2
PEAK_DB = -6.2          # set so the hum matches the other scenes
TIME = "12:20"
ABOVE = 0.8            # cut to the view from above
BOARD_SHOT = 2.8       # cut to the board

BOARD = dict(wiped=goals.wiped(goals.DURATION), new_goals=goals.written(goals.DURATION))


def days(crossed=0.0):
    return [("MONDAY", 1.0, 1.0), ("TUESDAY", 1.0, 1.0), ("WEDNESDAY", 1.0, 1.0), ("THURSDAY", 1.0, 1.0),
            ("FRIDAY", 1.0, crossed)]


# -- shot 1: the clock, 12:20 --------------------------------------------------------------------

clock_camera = Camera(zoom=Track((0, 1.0), (ABOVE, 1.015, "linear")), name="grind3.clock")


def shot_clock(canvas, t, frame):
    with clock_camera.view(canvas, t):
        draw_clock(canvas, frame, TIME)


# -- shot 2: from above, scrolling; the pizza box --------------------------------------------------

SWIPE = ABOVE + 0.95   # one swipe; nothing comes from Sam
bed_camera = Camera(name="grind3.bed")


def shot_bed(canvas, t, frame):
    with bed_camera.view(canvas, t):
        draw_scrolling(canvas, frame, t, TIME, ("clothes", "cups", "pizza"), swiping(t, SWIPE),
                       light_level(t, [SWIPE], key="grind3.reel"), key="grind3")


# -- shot 3: a careless slash --------------------------------------------------------------------------
# The board shot runs in its own time, and starts with the red marker already on its way to FRIDAY. The
# slash itself (door_wall.cross_line) is more crooked than the days before, and quicker.

arm = BoardArm(4, "FRIDAY", "SATURDAY", arm_in=0.0, grab_red=0.45, hover=None, cross=(0.95, 1.17), put_red=1.9,
               grab_pale=2.2, write=(2.7, 3.9), put_pale=4.6, arm_out=5.0, lift=0.2)
OFFSET = 0.7 - BOARD_SHOT      # story time = t + OFFSET

# the same framing as row 14's board, one day further down the column
board_camera = Camera(x=Track((BOARD_SHOT, 1190), (DURATION, 1196, "linear")),
                      y=Track((BOARD_SHOT, 506), (DURATION, 502, "linear")),
                      zoom=Track((BOARD_SHOT, 1.42), (DURATION, 1.46, "linear")), name="grind3.board")


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


bar = Discipline(flickers=[arm.cross[1] - 0.1 - OFFSET])  # empty: a red flicker as he slashes FRIDAY


def overlay(canvas, t, frame):
    bar.draw(canvas, t, frame)


def soundtrack():
    mix = sk.Mix(DURATION)
    mix.add(sk.pad(["A1", "E2"], DURATION, attack=0.4, release=1.0, brightness=0.05, key="hum"),
            at=0, gain_db=-17, reverb=0.2)
    # a reel's muffled voice from above (the first-million man, then the Bugatti man after the swipe), evened
    # as in scene 2
    adam, laura, liam = reel_sounds()
    for clip, a, b, offset, even in ((adam, ABOVE, SWIPE, 4.0, 3.4), (liam, SWIPE, BOARD_SHOT, 12.0, 3.3)):
        part = clip[int(offset * sk.SR):int((offset + b - a) * sk.SR)]
        mix.add(sk.fade_edges(part, 0.01, 0.01), at=a, gain_db=-10 + even, pan=0.1, reverb=0.05)
    mix.add(sk.lowpass(sk.tick(key="grind3.swipe"), 2500), at=SWIPE - 0.02, gain_db=-24, reverb=0.05)

    cross = sk.normalize(sk.eleven_sound("Close-up of one quick squeaky stroke of a dry-erase marker across a "
                                         "whiteboard, crossing out a word", 0.8, "marker_cross"))
    a, b = arm.cross
    mix.add(sk.fade_edges(cross[:int((b - a + 0.08) * sk.SR)], 0.005, 0.05), at=a - OFFSET, gain_db=-15, pan=0.2,
            reverb=0.08)
    bar.add_sounds(mix)
    return mix
