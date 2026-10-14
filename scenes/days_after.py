"""Film 1, row 25 of the story: days after. About 23.5 seconds: three quick days, each opening on the 6:00 clock
and closing on the board, the discipline bar stepping up with every tick (from 5 to 17 of its 20 steps). It
follows row 24, his first whole day.

Day 2
 0-0.7 s      The clock, 6:00, beeping.
 0.7-3.5 s    The street at dawn: the walk has become a jog, easy and steady.
 3.5-6.3 s    The board: all five ticked off in a quick run, a step on the bar with each.
Day 3, the hard day
 6.3-7.0 s    The clock, 6:00, beeping.
 7.0-8.4 s    The board: he ticks "Get up when the alarm rings".
 8.4-12.6 s   That night, the board in the dark, faintly red: he ticks "Write 3 lines" and puts the marker back.
              Two ticks, no more. His hand drifts toward the red marker on the tray, stops above it, and leaves
              it: no crossing out. The bar keeps its steps.
Day 4
12.6-13.3 s   The clock, 6:00, beeping.
13.3-15.5 s   A simple dark gym, from the side: he lifts a dumbbell, steady, two slow curls.
15.5-17.4 s   His notebook flipped through, pages already full of his lines, landing on today's.
17.4-20.4 s   His phone: under his "hey", Delivered becomes Read; it buzzes, and Sam answers: "hey you!! walk
              tomorrow?"
20.4-23.4 s   The board: all five ticked off in a quick run.

No caption, no hum.
"""
import math

import numpy as np
import skia

import scenes.day_one as one
import scenes.day_one_harder as harder
import scenes.five_things as five
import scenes.too_fast as fast
from scenes import wipe
from scenes.bedroom import ROOM, box, rounded_rect
from scenes.discipline import Discipline
from scenes.door_wall import MARKER_INK, draw_board, draw_marker, draw_today, five_box, tick_point
from scenes.grind_2 import draw_clock
from scenes.new_goals import squeaks
from scenes.scroll import glow
from scenes.street import GROUND, draw_street
from scenes.the_board import ARM, BOARD_H, CLOSE, GRIP, LONG, on_tray
from scenes.the_quote import C, PL, PW, SCREEN_RECT
from toolkit import BG, INK, RED, SCREEN, Camera, Character, Face, Ink, Track, blink, clamp, lerp, progress, reach, \
    to_color
from toolkit import sound as sk
from toolkit.rng import noise, rng

PEAK_DB = -2.4          # set so his sounds sit at the same level as the sounds in the other scenes

CLOCK_2, JOG, RUN_2 = 0.0, 0.7, 3.5
CLOCK_3, MORNING_3, NIGHT_3 = 6.3, 7.0, 8.4
CLOCK_4, GYM, FLIP, REPLY, RUN_4 = 12.6, 13.3, 15.5, 17.4, 20.4
DURATION = 23.4

CALM = Face(eyes=0.7, brows=0.15, mouth="flat", mouth_size=0.5, bags=True)


# -- the clock, each morning -------------------------------------------------------------------------------

clock_camera = Camera(zoom=1.05, name="days.clock")


def shot_clock(canvas, t, frame, t0):
    with clock_camera.view(canvas, t):
        draw_clock(canvas, frame, "6:00", on=1.0 if sk.alarm_on(t - t0) else 0.0)


# -- day 2: the jog -----------------------------------------------------------------------------------------

EASY_JOG = 300          # pixels per second: an easy, steady jog
jog = fast.Gait(fast.hero, lambda t: EASY_JOG, 300, GROUND, 330, cadence=(2.6, 2.7), stance=(0.24, 0.24),
                lift=(22, 26), lean=(7, 7), phase0=0.3, until=RUN_2 - JOG + 0.5)
jog_camera = Camera(x=lambda t: jog.hip_x(t - JOG) + 140, y=560, name="days.jog")


def shot_jog(canvas, t, frame):
    s = t - JOG
    with jog_camera.view(canvas, t):
        cx = jog_camera.state(t)[0]
        draw_street(canvas, frame, view=(cx - 1100, cx + 1100))
        face = CALM.but(eyes=0.75 * blink(t, "hero.days.jog", every=2.6), mouth="open", mouth_size=0.2)
        fast.hero.draw(canvas, frame, jog.pose(s, face))


# -- the board: a quick run of ticks -------------------------------------------------------------------------

APPROACH, TICK, BETWEEN = 0.35, 0.22, 0.16      # up to the first box; each tick; across to the next box


class QuickRun:
    """All five boxes ticked one after another, quickly, starting at t0 (a new day: no ticks before)."""

    def __init__(self, t0):
        self.t0 = t0
        self.ticks = [(t0 + APPROACH + k * (TICK + BETWEEN), t0 + APPROACH + k * (TICK + BETWEEN) + TICK)
                      for k in range(5)]
        self.end = self.ticks[-1][1]

    def tip(self, t):
        below = (five_box(CLOSE, 0)[0] - 40, 1180)
        if t < self.ticks[0][0]:
            return lerp(below, tick_point(CLOSE, 0, 0.0), progress(t, self.t0, self.ticks[0][0], "out"))
        for k, (a, b) in enumerate(self.ticks):
            if t < a:
                return lerp(tick_point(CLOSE, k - 1, 1.0), tick_point(CLOSE, k, 0.0),
                            progress(t, self.ticks[k - 1][1], a, "inout"))
            if t < b:
                return tick_point(CLOSE, k, progress(t, a, b, "inout"))
        end = tick_point(CLOSE, 4, 1.0)
        return lerp(end, (end[0] + 280, 1200), progress(t, self.end, self.end + 0.5, "in"))

    def ticked(self, t):
        return [progress(t, a, b, "inout") for a, b in self.ticks]

    def fills(self):
        return [b for _, b in self.ticks]

    def draw(self, canvas, t, frame):
        with one.Ticks.camera.view(canvas, t):
            draw_board(canvas, frame, CLOSE, one.DAYS, key="board", on_tray=("eraser", "red"), **one.BOARD)
            draw_today(canvas, frame, CLOSE, ticks=self.ticked(t))
            if t < self.end + 0.5:
                tip = self.tip(t)
                shoulder, elbow, hand, angle = five.holding_tip(tip)
                draw_marker(canvas, frame, tip, angle, BOARD_H, "pale", "board")
                five.draw_arm(canvas, frame, shoulder, elbow, hand)


run_2, run_4 = QuickRun(RUN_2), QuickRun(RUN_4)
morning_3 = one.Ticks([(MORNING_3, 0)])

# -- day 3, night: two ticks, and the red marker left where it lies ------------------------------------------

N = NIGHT_3
NIGHT_TICK = (N + 0.45, N + 0.75)            # he ticks "Write 3 lines"...
PUT_BACK = (N + 0.85, N + 1.75)              # ...puts the pale marker back on the tray...
TOWARD_RED = (N + 1.9, N + 2.8)              # ...his empty hand drifts toward the red marker...
HOVER_END = N + 3.6                          # ...stops above it...
LEAVE = (HOVER_END, N + 4.2)                 # ...and leaves it
night_camera = Camera(x=860, y=590, zoom=1.05, name="days.night")


def _grip(colour):
    tip = on_tray(colour)
    return (tip[0] - GRIP * LONG, tip[1])


ABOVE_RED = (_grip("red")[0] + 10, _grip("red")[1] - 70)   # where his hand stops, just above the red marker


def night_ticks(t):
    return [1.0, 0.0, 0.0, progress(t, *NIGHT_TICK, "inout")]


def night_arm(t):
    """(holding the pale marker?, its tip, flat, his hand) at time t, or None while his arm is away."""
    if t < N or t >= LEAVE[1]:
        return None
    if t < NIGHT_TICK[0]:
        tip = lerp((five_box(CLOSE, 3)[0] - 40, 1180), tick_point(CLOSE, 3, 0.0), progress(t, N, NIGHT_TICK[0], "out"))
        return True, tip, 0.0, None
    if t < NIGHT_TICK[1]:
        return True, tick_point(CLOSE, 3, progress(t, *NIGHT_TICK, "inout")), 0.0, None
    if t < PUT_BACK[1]:
        tip = lerp(tick_point(CLOSE, 3, 1.0), on_tray("pale"), progress(t, NIGHT_TICK[1], PUT_BACK[1], "inout"))
        return True, tip, progress(t, PUT_BACK[1] - 0.3, PUT_BACK[1], "inout"), None
    if t < TOWARD_RED[0]:
        return False, None, 0.0, _grip("pale")
    if t < HOVER_END:          # drifting over, slowing, and stopping just above it; a faint tremble
        hand = lerp(_grip("pale"), ABOVE_RED, progress(t, *TOWARD_RED, "out"))
        still = progress(t, TOWARD_RED[1] - 0.2, HOVER_END)
        return False, None, 0.0, (hand[0] + 1.5 * still * noise(t * 9, "days.tremble"), hand[1])
    return False, None, 0.0, lerp(ABOVE_RED, (ABOVE_RED[0] - 200, 1250), progress(t, *LEAVE, "in"))


def shot_night(canvas, t, frame):
    with night_camera.view(canvas, t):
        arm = night_arm(t)
        holding = arm is not None and arm[0]
        tray = ["eraser", "red"] + ([] if holding else ["pale"])
        draw_board(canvas, frame, CLOSE, one.DAYS, key="board", on_tray=tray, **one.BOARD)
        draw_today(canvas, frame, CLOSE, ticks=night_ticks(t))
        if arm is not None:
            if holding:
                shoulder, elbow, hand, angle = five.holding_tip(arm[1], arm[2])
                draw_marker(canvas, frame, arm[1], angle, BOARD_H, "pale", "board")
            else:
                hand = arm[3]
                shoulder = wipe.shoulder_for(hand)
                elbow, hand, _ = reach(shoulder, hand, *ARM, 1)
            five.draw_arm(canvas, frame, shoulder, elbow, hand)
        canvas.drawPaint(skia.Paint(Color=to_color((4, 3, 5, int(255 * wipe.DARKNESS)))))
        glow(canvas, wipe.CLOCK_LIGHT, 1400, RED, 0.12)


# -- day 4: the gym -------------------------------------------------------------------------------------------

GYM_GROUND = 860
gym_camera = Camera(x=Track((GYM, 930), (FLIP, 940, "linear")), y=560, zoom=Track((GYM, 1.12), (FLIP, 1.16, "linear")),
                    name="days.gym")
FOCUSED = Face(eyes=0.8, brows=-0.3, mouth="flat", mouth_size=0.5, bags=True)
side_hero = fast.hero
REP = 1.1              # seconds for one slow curl, up and down


def draw_gym(canvas, frame):
    """A simple dark gym from the side: the floor, a long mirror on the wall, a rack of dumbbells, a bench,
    and a cold light overhead."""
    glow(canvas, (960, 120), 900, (190, 200, 220), 0.1)
    ink = Ink(canvas, frame, color=ROOM, width=4.0, prefix="gym")
    ink.floor(GYM_GROUND, key="floor")
    ink.stroke([(180, GYM_GROUND - 120), (180, 230), (1740, 230), (1740, GYM_GROUND - 120)], "mirror", width=3.0)
    for k, x in enumerate((1300, 1400, 1500, 1600)):          # the rack: a low shelf, dumbbells in pairs
        for d in (-22, 22):
            ink.circle((x + d, GYM_GROUND - 150), 17, f"bell{k}{d}", fill=BG, width=3.0)
    ink.line((1240, GYM_GROUND - 128), (1660, GYM_GROUND - 128), "rack.shelf", width=5.0)
    for k, x in enumerate((1260, 1640)):
        ink.line((x, GYM_GROUND - 128), (x, GYM_GROUND), f"rack.leg{k}", width=4.0)
    box(ink, rounded_rect(300, GYM_GROUND - 120, 640, GYM_GROUND - 90, 8), "bench")       # the bench
    for k, x in enumerate((340, 600)):
        ink.line((x, GYM_GROUND - 90), (x, GYM_GROUND), f"bench.leg{k}", width=4.0)


def draw_dumbbell(canvas, frame, hand, key):
    """A dumbbell in his hand, seen from the side: its round plate facing us."""
    ink = Ink(canvas, frame, color=ROOM, width=3.5, prefix=key)
    ink.circle(hand, 19, "plate", fill=(40, 40, 46))
    ink.circle(hand, 7, "hub", width=2.5)


def gym_pose(t):
    """Standing side-on, facing right; the near arm curls the dumbbell up and slowly down, the elbow at his side."""
    s = t - GYM
    curl = 0.5 - 0.5 * math.cos(2 * math.pi * max(s - 0.2, 0.0) / REP)
    breath = 1.5 * math.sin(2 * math.pi * s / REP)
    pose = side_hero.stand(900, GYM_GROUND, facing=1, face=FOCUSED.but(eyes=0.8 * blink(t, "hero.gym", every=2.8)))
    pose = pose.but(y=pose.y + 1.0 + breath * 0.5)
    sh = side_hero.joints(pose)["shoulder"]
    upper, fore = side_hero.arm
    elbow = (sh[0] + 8, sh[1] + upper * 0.98)
    a = lerp(0.12, 2.45, curl)                       # the forearm swings up from hanging, round the elbow
    hand = (elbow[0] + fore * 0.98 * math.sin(a), elbow[1] + fore * 0.98 * math.cos(a))
    bend = min((1, -1), key=lambda b: math.dist(reach(sh, hand, upper, fore, b)[0], elbow))
    hang = (sh[0] - 6, sh[1] + 0.3 * side_hero.height)
    return pose.but(hand_r=hand, bend_hand_r=bend, hand_l=hang), curl


def shot_gym(canvas, t, frame):
    with gym_camera.view(canvas, t):
        draw_gym(canvas, frame)
        pose, curl = gym_pose(t)
        j = side_hero.draw(canvas, frame, pose)
        draw_dumbbell(canvas, frame, j["hand_l"], "gym.bell.l")
        draw_dumbbell(canvas, frame, j["hand_r"], "gym.bell.r")


# -- day 4: the notebook, flipped through -----------------------------------------------------------------

FLIPS = [FLIP + 0.15 + 0.28 * k for k in range(3)]     # each page turns in 0.28 s
FLIP_TIME = 0.28
TURNING_PAGE = (44, 45, 52)
LANDED = FLIPS[-1] + FLIP_TIME
TODAY_LINE = (LANDED + 0.15, FLIP + 1.75)               # he's finishing today's third line
notebook_camera = Camera(zoom=Track((FLIP, 1.0), (REPLY, 1.03, "linear")), name="days.notebook")


def scribble_lines(seed, lines=None):
    """A page full of his handwriting, too small and quick to read: (row, start x share, length share) for each
    written line."""
    g = rng("notebook.page", seed)
    rows = range(lines) if lines is not None else range(9)
    return [(k, g.uniform(0.0, 0.04), g.uniform(0.45, 0.92)) for k in rows]


def draw_scribbles(canvas, frame, page, lines, key, squeeze=1.0, origin=None, shown=None):
    """Lines of pale handwriting on a page rect, squeezed sideways toward `origin` (the spine) while it turns.
    shown: how much of the last line is written (0..1), for the line being written."""
    x0, y0, x1, y1 = page
    width = x1 - x0 - 110
    ink = Ink(canvas, frame, color=MARKER_INK, width=3.2, prefix=key)
    for n, (k, start, length) in enumerate(lines):
        y = harder.RULE_TOP + harder.RULE_STEP * (k + 1) - 22
        share = length if shown is None or n < len(lines) - 1 else length * shown
        if share <= 0.01:
            continue
        xs = np.linspace(x0 + 55 + start * width, x0 + 55 + (start + share) * width, max(4, int(40 * share)))
        g = rng("notebook.hand", key, k)
        phase = g.uniform(0, 6)
        pts = [(x, y + 7 * math.sin(0.09 * x + phase) + 4 * math.sin(0.23 * x)) for x in xs]
        if origin is not None:
            pts = [(origin + (x - origin) * squeeze, py) for x, py in pts]
        ink.stroke(pts, f"line{k}", width=3.2, taper=0.2)


def page_polygon(angle):
    """The turning page, hinged on the spine: angle 0 = lying on the right, pi = lying on the left. Its free edge
    rises toward us as it stands up, so it looks a little taller then."""
    x0, y0, x1, y1 = harder.RIGHT_PAGE
    edge = 960 + (x1 - 960) * math.cos(angle)
    lift = 45 * math.sin(angle)
    return [(960, y0), (edge, y0 - lift), (edge, y1 + lift), (960, y1)], math.cos(angle)


def shot_flip(canvas, t, frame):
    with notebook_camera.view(canvas, t):
        k = sum(1 for f in FLIPS if t >= f + FLIP_TIME)          # pages turned so far
        turning = next((i for i, f in enumerate(FLIPS) if f <= t < f + FLIP_TIME), None)
        harder.draw_notebook(canvas, frame, [])
        # the left page shows the last page turned (written on); the right one the next page (today's at the end)
        draw_scribbles(canvas, frame, harder.LEFT_PAGE, scribble_lines(("back", k)), f"left{k}")
        right = k + (1 if turning is not None else 0)
        if right < len(FLIPS):
            draw_scribbles(canvas, frame, harder.RIGHT_PAGE, scribble_lines(("front", right)), f"right{right}")
        else:     # today's page: two lines written, the third being finished
            shown = progress(t, *TODAY_LINE, "linear")
            draw_scribbles(canvas, frame, harder.RIGHT_PAGE, scribble_lines("today", 3), "today", shown=shown)
        if turning is not None:
            u = progress(t, FLIPS[turning], FLIPS[turning] + FLIP_TIME, "inout")
            poly, squeeze = page_polygon(math.pi * u)
            ink = Ink(canvas, frame, color=ROOM, width=4.5, prefix=f"flip{turning}")
            box(ink, poly, "page", fill=TURNING_PAGE)          # lifted toward the light, a touch lighter
            if abs(squeeze) > 0.15:   # the writing on it, squeezed toward the spine as it stands up: its front
                # (laid out like a right page) on the way up, its back (like a left page) on the way down
                if squeeze > 0:
                    draw_scribbles(canvas, frame, harder.RIGHT_PAGE, scribble_lines(("front", turning)),
                                   f"flip{turning}.w", squeeze=squeeze, origin=960)
                else:
                    draw_scribbles(canvas, frame, harder.LEFT_PAGE, scribble_lines(("back", turning + 1)),
                                   f"flip{turning}.b", squeeze=-squeeze, origin=960)
        if t >= LANDED:               # his pen finishing today's third line
            x0 = harder.RIGHT_PAGE[0]
            lines = scribble_lines("today", 3)
            row, start, length = lines[-1]
            width = harder.RIGHT_PAGE[2] - x0 - 110
            u = progress(t, *TODAY_LINE, "linear")
            x = x0 + 55 + (start + length * u) * width
            y = harder.RULE_TOP + harder.RULE_STEP * (row + 1) - 22
            harder.draw_writing_arm(canvas, frame, (x, y + 7 * math.sin(0.09 * x) - 4))


# -- day 4: Sam answers -------------------------------------------------------------------------------------

READ, BUZZ = 0.45, 0.75          # after the cut to the phone: Delivered becomes Read; then it buzzes, and his answer
SAM_SAYS = "hey you!! walk tomorrow?"
phone_camera = Camera(zoom=Track((REPLY, 1.0), (RUN_4, 1.03, "linear")), name="days.phone")


def shot_reply(canvas, t, frame):
    p = t - REPLY
    buzz = 3.0 if BUZZ <= p < BUZZ + 0.35 else 0.0
    with phone_camera.view(canvas, t):
        glow(canvas, C, 900, SCREEN, 0.3)
        canvas.save()
        canvas.translate(buzz * noise(t * 45, "days.buzz", "x"), buzz * noise(t * 45, "days.buzz", "y"))
        ink = Ink(canvas, frame, color=ROOM, width=9.0, prefix="quote.phone")
        box(ink, rounded_rect(C[0] - PW / 2, C[1] - PL / 2, C[0] + PW / 2, C[1] + PL / 2, 60), "phone", width=9.0)
        screen = rounded_rect(*SCREEN_RECT, 40)
        path = skia.Path()
        path.addPoly([skia.Point(*q) for q in screen], True)
        canvas.save()
        canvas.clipPath(path, doAntiAlias=True)
        harder.draw_chat(canvas, frame, p, mine="hey", sent=1.0, delivered=True, label="Mon 18:40",
                         status="Read" if p >= READ else "Delivered", reply=SAM_SAYS,
                         replied=progress(p, BUZZ, BUZZ + 0.3, "out"), reply_label="Today 7:12", cursor=False)
        canvas.restore()
        ink.stroke(screen, "screen", closed=True, width=4.0)
        arm = Ink(canvas, frame, color=INK, width=30.0, prefix="hero.closeup")
        arm.line((C[0] - 260, 1300), (C[0] - PW / 2 + 4, 860), "forearm.l", pin_ends=True, taper=0.0)
        arm.line((C[0] + 260, 1300), (C[0] + PW / 2 - 4, 840), "forearm.r", pin_ends=True, taper=0.0)
        canvas.restore()


# -- the scene ------------------------------------------------------------------------------------------


def draw(canvas, t, frame):
    if t < JOG:
        shot_clock(canvas, t, frame, CLOCK_2)
    elif t < RUN_2:
        shot_jog(canvas, t, frame)
    elif t < CLOCK_3:
        run_2.draw(canvas, t, frame)
    elif t < MORNING_3:
        shot_clock(canvas, t, frame, CLOCK_3)
    elif t < NIGHT_3:
        morning_3.draw(canvas, t, frame)
    elif t < CLOCK_4:
        shot_night(canvas, t, frame)
    elif t < GYM:
        shot_clock(canvas, t, frame, CLOCK_4)
    elif t < FLIP:
        shot_gym(canvas, t, frame)
    elif t < REPLY:
        shot_flip(canvas, t, frame)
    elif t < RUN_4:
        shot_reply(canvas, t, frame)
    else:
        run_4.draw(canvas, t, frame)


# +1 for every tick: five on day 2, two on the hard day, five on day 4 (from 5 to 17 steps). It never drains.
bar = Discipline(start=5, fills=run_2.fills() + morning_3.fills() + [NIGHT_TICK[1]] + run_4.fills())


def overlay(canvas, t, frame):
    bar.draw(canvas, t, frame)


def soundtrack():
    mix = sk.Mix(DURATION)

    def effect(prompt, seconds, name):            # ElevenLabs effects, all brought to the same level first
        return sk.normalize(sk.eleven_sound(prompt, seconds, name))

    for t0, t1 in ((CLOCK_2, JOG), (CLOCK_3, MORNING_3), (CLOCK_4, GYM)):    # each morning's alarm, cut by the next shot
        mix.add(sk.fade_edges(sk.alarm(t1 - t0), 0.0, 0.01), at=t0, gain_db=-7, reverb=0.1)
    # day 2: the street, his jogging steps
    street = effect("A quiet city street just before sunrise: distant traffic, a faint cold wind, no voices, "
                    "no birds", 17.0, "street_dawn")
    mix.add(sk.fade_edges(street[:int((RUN_2 - JOG) * sk.SR)], 0.05, 0.05), at=JOG, gain_db=-27)
    for n, (tk, tl, foot, x, h) in enumerate(jog.steps):
        if JOG <= tk + JOG < RUN_2:
            mix.add(sk.footstep(n, weight=0.45, key="days.jog"), at=tk + JOG, gain_db=-14, reverb=0.1)
    # the marker: two squeaks on every tick; the pale marker put back on the hard night
    grains = squeaks()
    g = rng("days.squeak")
    for a, b in run_2.ticks + run_4.ticks + [NIGHT_TICK]:
        for at in (a + 0.01, a + 0.1):
            mix.add(grains[g.integers(len(grains))], at=at, gain_db=-16, pan=-0.15, reverb=0.08)
    for at in morning_3.squeaks():
        mix.add(grains[g.integers(len(grains))], at=at, gain_db=-15, pan=-0.15, reverb=0.08)
    tray = effect("A plastic marker pen put down on a whiteboard's metal tray, one small light click", 0.5,
                  "marker_tray")
    mix.add(tray, at=PUT_BACK[1] - 0.2, gain_db=-20, pan=0.2, reverb=0.08)
    # day 4: the dumbbell, the pages, the pen, the phone
    for k in range(2):
        mix.add(sk.highpass(sk.tick(key=("days.bell", k)), 1200), at=GYM + 0.2 + k * REP, gain_db=-24, reverb=0.15)
    for f in FLIPS:
        mix.add(sk.whoosh(0.22, peak=0.5, low=600, high=4000, key=("days.page", f)), at=f, gain_db=-20, reverb=0.06)
    scratch = harder.scratch_sound()
    a, b = TODAY_LINE
    mix.add(sk.fade_edges(scratch[:int((b - a) * sk.SR)], 0.04, 0.08), at=a, gain_db=-17, pan=0.2, reverb=0.06)
    buzz = effect("A smartphone on a wooden nightstand vibrating with a new text message, a short double buzz, "
                  "close up, in a quiet room", 1.5, "phone_buzz")
    mix.add(sk.fade_edges(sk.lowpass(buzz[int(0.05 * sk.SR):int(0.4 * sk.SR)], 1800), 0.01, 0.04), at=REPLY + BUZZ,
            gain_db=-16, reverb=0.06)
    bar.add_sounds(mix)
    return mix
