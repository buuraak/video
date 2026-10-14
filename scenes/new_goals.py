"""Film 1, row 10 of the story: new goals. About 32 seconds, four shots joined by hard cuts. Unhurried.
It follows row 9, where he walked briskly out of the bedroom to the right.

 0-5 s    From the side, the wall by the door (as in the board scene). He walks in from the left, upright
          and determined, stops in front of the board and looks up at the huge goals.
 5-23 s   The board close up. A moment to read it. His stick arm comes up from below left and takes the
          eraser from the tray, and wipes the five huge goals away, line by line (a faint smear stays).
          He puts the eraser back, takes the pale marker and writes four new goals in their place, letter
          by letter: Run 2x a week / Go to the gym / Stay sober / Wake up at 6:00. NEW ME and the start
          days (MONDAY crossed out, TUESDAY) stay. He puts the marker back; we hold on the board to read it.
23-27 s   Closer on him from the side, the board's corner beside him. He steps back, looks at it, and
          slowly smiles: his first smile in the film.
27-32 s   Wide again: he walks to the door, pushes it open onto the cold early light and steps into it.

Sound: the hum, his steps, the eraser, the markers on the tray and on the board, the door.
"""
import math

import numpy as np

from scenes.discipline import Discipline
from scenes.door_wall import (DOOR, GOAL, GOALS, GROUND, at, draw_board, draw_eraser, draw_marker, draw_wall,
                              eraser_on_tray, eraser_size, hero, word_box)
from scenes.the_board import ARM, BOARD_H, CLOSE, GRIP, LONG, on_tray, shoulder_for
from toolkit import INK, Camera, Face, Ink, Track, blink, lerp, progress, reach
from toolkit import sound as sk
from toolkit.rng import rng

DURATION = 32.0
PEAK_DB = -5.1         # set so the hum matches the other scenes (the door latch is the loudest moment)
NEW = ["Run 2x a week", "Go to the gym", "Stay sober", "Wake up at 6:00"]
DAYS = [("MONDAY", 1.0, 1.0), ("TUESDAY", 1.0, 0.0)]
TRAY = ("eraser", "red", "pale")    # what lies on the tray in the wide shots (the eraser from here on)
DETERMINED = Face(eyes=0.92, brows=-0.6, mouth="frown", mouth_size=0.0, bags=True)

CLOSE_UP = 5.0         # cut to the board
SMILE_SHOT = 23.0      # cut to him, closer
DOOR_SHOT = 27.0       # cut to the wide view, and out of the door

# -- walking, seen from the side ---------------------------------------------------------------------


class Walk:
    """A walk along the floor: from `x0` at time `t0`, at `speed`, slowing to a stop at `x1` (to either side).
    facing: which way he faces, 1 right or -1 left (facing right while walking left is stepping back).
    ramp: seconds to get up to speed from standing (0 = already walking as it starts). feet0: where his feet
    are at the start."""

    STEP, SWING, LIFT, SLOW = 0.4, 0.75, 12, 0.5

    def __init__(self, t0, x0, x1, speed, first="foot_l", ramp=0.0, feet0=None, facing=1):
        self.t0, self.x0, self.x1, self.speed, self.ramp, self.facing = t0, x0, x1, speed, ramp, facing
        self.d = 1 if x1 >= x0 else -1
        self.stop = t0 + abs(x1 - x0) / speed + ramp / 2 + self.SLOW / 2      # when he stands still
        self.feet0 = feet0 or {"foot_l": x0 - 32, "foot_r": x0 + 32}
        self.steps = self._steps(first)

    def hip_x(self, t):
        dt = min(max(t - self.t0, 0.0), self.stop - self.t0)
        cruise_end = self.stop - self.t0 - self.SLOW
        dist = self.speed * min(dt, self.ramp) ** 2 / (2 * self.ramp) if self.ramp > 0 else 0.0
        if dt > self.ramp:
            dist += self.speed * (min(dt, cruise_end) - self.ramp)
        if dt > cruise_end:
            s = dt - cruise_end
            dist += self.speed * (s - s * s / (2 * self.SLOW))
        return self.x0 + self.d * dist

    def moving(self, t):
        """How fast he's going, as a share of full speed."""
        if t < self.t0 or t > self.stop:
            return 0.0
        up = progress(t, self.t0, self.t0 + self.ramp, "linear") if self.ramp > 0 else 1.0
        return up * (1 - progress(t, self.stop - self.SLOW, self.stop, "linear"))

    def _steps(self, first):
        feet = ("foot_l", "foot_r") if first == "foot_l" else ("foot_r", "foot_l")
        plant = dict(self.feet0)
        out, k = [], 0
        while True:
            lift = self.t0 - 0.05 + k * self.STEP
            land = lift + self.SWING * self.STEP
            if lift > self.stop - 0.1:
                return out
            foot = feet[k % 2]
            stance = 26 if foot == "foot_r" else -26
            # a foot lands midway between where his hips are as it lands and where they'll be when it lifts
            # again (so it's as far ahead then as it is behind later, even while he speeds up or slows down);
            # standing still, his feet settle a little apart
            later = lift + 2 * self.STEP
            to = 0.5 * (self.hip_x(land) + self.hip_x(later)) + stance * (1 - self.moving(min(later, self.stop)))
            out.append((lift, land, foot, plant[foot], to))
            plant[foot] = to
            k += 1

    def feet(self, t):
        where = {}
        for lift, land, foot, a, b in self.steps:
            if t >= land:
                where[foot] = (b, GROUND)
            elif t >= lift:
                u = (t - lift) / (land - lift)
                where[foot] = (lerp(a, b, u * u * (3 - 2 * u)), GROUND - self.LIFT * math.sin(math.pi * u))
            elif foot not in where:
                where[foot] = (a, GROUND)
        return where

    def _hip_y(self, t, straight):
        """How high his hips can be with his legs `straight` (a share of their full length) to every foot."""
        leg = straight * sum(hero.leg)
        x = self.hip_x(t)
        return max(f[1] - math.sqrt(max(leg ** 2 - (f[0] - x) ** 2, 0)) for f in self.feet(t).values())

    def pose(self, t, face, look_up=0.0, lean=1.0, head_tilt=None):
        """Upright, not hunched: the leg he stands on is almost straight, so his hips ride up over it and dip a
        little between steps (a foot coming down takes over gradually, so they never drop in one frame). His
        arms hang nearly straight from the shoulder and swing against his legs. lean and head_tilt are toward
        the way he faces (head_tilt, if given, replaces looking up: positive droops his head forward)."""
        feet = self.feet(t)
        tilt = -2 - 14 * look_up if head_tilt is None else head_tilt
        pose = hero.stand(self.hip_x(t), GROUND, face=face, facing=self.facing, lean=self.facing * lean,
                          head_tilt=self.facing * tilt, **feet)
        # the rise and dip, smoothed over a tenth of a second either side, but never higher than his legs reach
        smooth = sum(self._hip_y(t + d, 0.975) for d in np.linspace(-0.1, 0.1, 9)) / 9
        pose = pose.but(y=max(smooth, self._hip_y(t, 0.995)))
        j = hero.joints(pose)
        arm, moving = 0.975 * sum(hero.arm), self.moving(t)
        hands = {}
        for hand, other, apart in (("hand_l", "foot_r", -5), ("hand_r", "foot_l", 5)):
            angle = math.radians(max(-24, min(24, 0.32 * (feet[other][0] - pose.x)))) * moving
            hands[hand] = (j["shoulder"][0] + apart + arm * math.sin(angle), j["shoulder"][1] + arm * math.cos(angle))
        return pose.but(**hands)


STOP_AT = 640                         # in front of the board, as in the board scene
walk_in = Walk(0.0, -10, STOP_AT, 230)
LOOK = (walk_in.stop + 0.2, walk_in.stop + 0.7)     # he lifts his head to the board

# -- shot 1: he walks in and looks at the board --------------------------------------------------------

wide_camera = Camera(x=Track((0, 930), (CLOSE_UP, 955, "linear")), zoom=Track((0, 1.0), (CLOSE_UP, 1.06, "linear")),
                     name="goals.wide")


def shot_walk_in(canvas, t, frame):
    with wide_camera.view(canvas, t):
        draw_wall(canvas, frame, DAYS, on_tray=TRAY)
        face = DETERMINED.but(eyes=0.92 * blink(t, "hero.goals", every=2.8))
        look = progress(t, *LOOK, "inout")
        breath = 2.5 * math.sin(2 * math.pi * t / 3.2) * (1 - walk_in.moving(t))
        pose = walk_in.pose(t, face, look_up=look)
        hero.draw(canvas, frame, pose.but(y=pose.y + breath))


# -- shot 2: the board close up: wiping and writing ---------------------------------------------------

close_camera = Camera(zoom=Track((CLOSE_UP, 1.0), (SMILE_SHOT, 1.05, "linear")), name="goals.close")
U, V, STEP_V, SIZE = GOAL
BOARD_W = CLOSE[2] - CLOSE[0]
ER_LONG, ER_HIGH = eraser_size(BOARD_H)

ARM_IN = 6.4           # after a moment to read the board, his arm rises...
GRAB_ERASER = 7.2      # ...and takes the eraser
WIPE_START = 7.6       # wipes the goals away, a sweep along each line, moving down between them
SWEEP, DOWN = 0.7, 0.18
PUT_ERASER = 12.4      # puts it back
GRAB_PALE = 13.0       # takes the pale marker
WRITE_START = 13.45    # writes the new goals, one after another
PER_LETTER, BETWEEN = 0.1, 0.35
SWEEP_U = (0.075, 0.47)  # where the eraser's middle runs along each line (it never reaches START:)


def line_v(i):
    """The middle of goal line i, in board measurements (its baseline is a little lower)."""
    return V + i * STEP_V - 0.022


def wipe_path():
    """The eraser's moves while it wipes: (start time, end time, from (u, v), to (u, v))."""
    out, t = [], WIPE_START
    for i in range(len(GOALS)):
        a, b = SWEEP_U if i % 2 == 0 else SWEEP_U[::-1]
        out.append((t, t + SWEEP, (a, line_v(i)), (b, line_v(i))))
        t += SWEEP
        if i < len(GOALS) - 1:
            out.append((t, t + DOWN, (b, line_v(i)), (b, line_v(i + 1))))
            t += DOWN
    return out


WIPES = wipe_path()
WIPE_END = WIPES[-1][1]


def eraser_box(uv):
    """The area the eraser's felt covers, in board measurements, with its middle at uv."""
    du, dv = ER_LONG / 2 / BOARD_W, ER_HIGH / 2 / BOARD_H
    return (uv[0] - du, uv[1] - dv, uv[0] + du, uv[1] + dv)


def wiped(t):
    """Everything the eraser has wiped by time t."""
    out = []
    for t0, t1, a, b in WIPES:
        if t <= t0:
            break
        now = lerp(a, b, progress(t, t0, t1, "inout"))
        ba, bn = eraser_box(a), eraser_box(now)
        # a little taller than the felt, so the strips of neighbouring lines overlap and no tips of letters
        # are left between them
        out.append((min(ba[0], bn[0]), min(ba[1], bn[1]) - 0.02, max(ba[2], bn[2]), max(ba[3], bn[3]) + 0.02))
    return out


def writing_lines():
    """For each new goal: (start time, end time)."""
    out, t = [], WRITE_START
    for text in NEW:
        d = PER_LETTER * len("- " + text)
        out.append((t, t + d))
        t += d + BETWEEN
    return out


LINES = writing_lines()
WRITE_END = LINES[-1][1]
PUT_PALE = WRITE_END + 0.6
ARM_OUT = PUT_PALE + 0.5


def written(t):
    return [(text, progress(t, a, b, "linear")) for text, (a, b) in zip(NEW, LINES) if t >= a]


def line_start(i):
    x, y, w, px = word_box(CLOSE, "- " + NEW[i], U, V + i * STEP_V, SIZE)
    return x, y, w, px


def pen_tip(t):
    """Where the pale marker's tip is while he writes (and between lines)."""
    for i, (a, b) in enumerate(LINES):
        x, y, w, px = line_start(i)
        if t < a:          # moving from the end of the line before (or from the tray) to this line's start
            if i == 0:
                return lerp(on_tray("pale"), (x, y - 0.4 * px), progress(t, GRAB_PALE, a, "inout"))
            px0, py0, pw0, ppx0 = line_start(i - 1)
            return lerp((px0 + pw0, py0 - 0.4 * ppx0), (x, y - 0.4 * px), progress(t, LINES[i - 1][1], a, "inout"))
        if t < b:          # along the words, bobbing up and down with the letters
            u = progress(t, a, b, "linear")
            n = len("- " + NEW[i])
            return (x + w * u + 0.06 * px * math.sin(2 * math.pi * n * u + 1.0),
                    y - 0.4 * px + 0.3 * px * math.sin(2 * math.pi * n * u))
    x, y, w, px = line_start(len(NEW) - 1)
    return lerp((x + w, y - 0.4 * px), on_tray("pale"), progress(t, WRITE_END, PUT_PALE, "inout"))


def eraser_at(t):
    """Where the eraser's middle is while it's off the tray."""
    rest = eraser_on_tray(CLOSE)
    first = at(CLOSE, *WIPES[0][2])
    if t < WIPE_START:
        return lerp(rest, first, progress(t, GRAB_ERASER, WIPE_START, "inout"))
    for t0, t1, a, b in WIPES:
        if t < t1:
            u = progress(t, t0, t1, "inout")
            p = at(CLOSE, *lerp(a, b, u))
            return (p[0], p[1] + 0.004 * BOARD_H * math.sin(2 * math.pi * 7 * (t - t0)))   # scrubbing
    last = at(CLOSE, *WIPES[-1][3])
    return lerp(last, rest, progress(t, WIPE_END, PUT_ERASER, "inout"))


def holding(t):
    if GRAB_ERASER <= t < PUT_ERASER:
        return "eraser"
    if GRAB_PALE <= t < PUT_PALE:
        return "pale"
    return None


def hand_at(t):
    """Where the end of his arm is, and the held marker's angle."""
    held = holding(t)
    if held == "eraser":
        e = eraser_at(t)
        return (e[0], e[1] - ER_HIGH / 2), 0.0
    if held == "pale":
        tip = pen_tip(t)
        flat = 1 - progress(t, GRAB_PALE, GRAB_PALE + 0.3, "inout") + progress(t, PUT_PALE - 0.3, PUT_PALE, "inout")
        angle = 0.0
        for _ in range(3):               # in line with his forearm, unless it's lying flat on the tray
            a = math.radians(angle)
            hand = (tip[0] - GRIP * LONG * math.cos(a), tip[1] - GRIP * LONG * math.sin(a))
            elbow, hand, _ = reach(shoulder_for(hand), hand, *ARM, 1)
            angle = lerp(math.degrees(math.atan2(hand[1] - elbow[1], hand[0] - elbow[0])), 0.0, flat)
        a = math.radians(angle)
        return (tip[0] - GRIP * LONG * math.cos(a), tip[1] - GRIP * LONG * math.sin(a)), angle
    # empty-handed: rising from below to the eraser, across to the marker, and away at the end
    eraser_top = (eraser_on_tray(CLOSE)[0], eraser_on_tray(CLOSE)[1] - ER_HIGH / 2)
    marker = on_tray("pale")
    marker_hand = (marker[0] - GRIP * LONG, marker[1])
    if t < GRAB_ERASER:
        return lerp((520, 1150), eraser_top, progress(t, ARM_IN, GRAB_ERASER, "out")), 0.0
    if t < GRAB_PALE:
        return lerp(eraser_top, marker_hand, progress(t, PUT_ERASER, GRAB_PALE, "inout")), 0.0
    return lerp(marker_hand, (1500, 1180), progress(t, PUT_PALE, ARM_OUT, "in")), 0.0


def shot_board(canvas, t, frame):
    with close_camera.view(canvas, t):
        held = holding(t)
        tray = [c for c in ("eraser", "red", "pale") if c != held]
        new = written(t)
        draw_board(canvas, frame, CLOSE, DAYS, key="board.close", line_width=6.0, on_tray=tray, wiped=wiped(t),
                   new_goals=new)
        if not ARM_IN <= t < ARM_OUT:
            return
        hand, angle = hand_at(t)
        shoulder = shoulder_for(hand)
        elbow, hand, _ = reach(shoulder, hand, *ARM, 1)
        if held == "eraser":
            draw_eraser(canvas, frame, eraser_at(t), 0.0, BOARD_H, "board.close")
        elif held == "pale":
            draw_marker(canvas, frame, pen_tip(t), angle, BOARD_H, "pale", "board.close")
        pen = Ink(canvas, frame, color=INK, width=30.0, prefix="hero.closeup")
        beyond = (shoulder[0] + 0.6 * (shoulder[0] - elbow[0]), shoulder[1] + 0.6 * (shoulder[1] - elbow[1]))
        pen.line(beyond, elbow, "upper_arm", pin_ends=True, taper=0.0)     # runs on off screen
        pen.line(elbow, hand, "forearm", pin_ends=True, taper=0.1)


# -- shot 3: closer on him: he steps back, looks, and smiles -------------------------------------------

smile_camera = Camera(x=Track((SMILE_SHOT, 720), (DOOR_SHOT, 705, "linear")), y=560,
                      zoom=Track((SMILE_SHOT, 2.15), (DOOR_SHOT, 2.25, "linear")), name="goals.smile")
step_back = Walk(SMILE_SHOT + 0.5, STOP_AT, STOP_AT - 40, 120, first="foot_l", ramp=0.2,
                 feet0={k: v[0] for k, v in walk_in.feet(CLOSE_UP).items()})
SMILE = (SMILE_SHOT + 1.3, SMILE_SHOT + 2.6)     # the smile grows, slowly


def smiling(t):
    """How far his smile has come (0..1)."""
    return progress(t, *SMILE, "inout") if t < DOOR_SHOT else 1.0


def his_face(t):
    s = smiling(t)
    return Face(eyes=lerp(0.92, 0.8, s) * blink(t, "hero.goals.smile", every=3.2), brows=lerp(-0.6, 0.1, s),
                mouth="smile", mouth_size=0.85 * s, bags=True)


def shot_smile(canvas, t, frame):
    with smile_camera.view(canvas, t):
        draw_wall(canvas, frame, DAYS, on_tray=TRAY, wiped=wiped(DURATION), new_goals=written(DURATION))
        breath = 2.0 * math.sin(2 * math.pi * (t - SMILE_SHOT) / 3.0) * (1 - step_back.moving(t))
        pose = step_back.pose(t, his_face(t), look_up=1.0)
        hero.draw(canvas, frame, pose.but(y=pose.y + breath))


# -- shot 4: out of the door ---------------------------------------------------------------------------

DOOR_X = DOOR[0] - 70                  # where his hips stop, at the door
walk_out = Walk(DOOR_SHOT + 0.3, STOP_AT - 40, DOOR_X, 230, first="foot_l", ramp=0.5,
                feet0={k: v[0] for k, v in step_back.feet(DOOR_SHOT).items()})
HANDLE = (DOOR[0] + 26, GROUND - 0.47 * (DOOR[3] - DOOR[1]))
PUSH = (walk_out.stop - 0.1, walk_out.stop + 0.8)      # he pushes the door open...
INTO = (PUSH[1] - 0.2, DURATION)                        # ...and steps into the light

door_camera = Camera(x=Track((DOOR_SHOT, 960), (DURATION, 1020, "linear")), zoom=1.06, name="goals.door")


def shot_door(canvas, t, frame):
    with door_camera.view(canvas, t):
        opening = progress(t, *PUSH, "inout")
        draw_wall(canvas, frame, DAYS, on_tray=TRAY, wiped=wiped(DURATION), new_goals=written(DURATION),
                  door_open=0.85 * opening)
        face = his_face(t).but(mouth_size=0.45)
        into = progress(t, *INTO, "inout")
        pose = walk_out.pose(t, face)
        if into > 0:      # a last stride into the doorway (his arms hang at rest)
            pose = pose.but(x=pose.x + 140 * into, foot_l=(DOOR_X - 30 + 170 * into, GROUND - 14 * math.sin(math.pi * into)),
                            foot_r=(DOOR_X + 30 + 110 * progress(into, 0.3, 1.0), GROUND), hand_l=None, hand_r=None)
        rest = hero.joints(pose)
        reach_out = progress(t, PUSH[0] - 0.3, PUSH[0], "inout") * (1 - progress(t, *INTO))
        handle = (HANDLE[0] + (DOOR[2] - DOOR[0]) * 0.3 * opening, HANDLE[1])
        hand = lerp(rest["hand_r"], handle, reach_out)
        d, longest = math.dist(rest["shoulder"], hand), 0.97 * sum(hero.arm)   # he lets go as the door swings away
        if d > longest:
            hand = lerp(rest["shoulder"], hand, longest / d)
        hero.draw(canvas, frame, pose.but(hand_r=hand))


# -- the scene ------------------------------------------------------------------------------------------


def draw(canvas, t, frame):
    if t < CLOSE_UP:
        shot_walk_in(canvas, t, frame)
    elif t < SMILE_SHOT:
        shot_board(canvas, t, frame)
    elif t < DOOR_SHOT:
        shot_smile(canvas, t, frame)
    else:
        shot_door(canvas, t, frame)


def squeaks():
    """Single marker squeaks, cut out of the ElevenLabs marker recordings, each brought to the same level."""
    from scipy.signal import find_peaks
    recordings = [
        sk.eleven_sound("Close-up of one quick squeaky stroke of a dry-erase marker across a whiteboard, "
                        "crossing out a word", 0.8, "marker_cross"),
        sk.eleven_sound("Continuous close-up of a dry-erase marker squeaking steadily as someone writes a word on a "
                        "whiteboard, quick squeaky strokes with no pauses", 2.5, "marker_squeak", influence=0.7),
        sk.eleven_sound("Close-up of someone slowly writing one word on a whiteboard with a dry-erase marker, "
                        "slow squeaky strokes", 2.0, "marker_write"),
    ]
    out = []
    for x in recordings:
        win = int(0.01 * sk.SR)
        env = np.sqrt(np.convolve(x ** 2, np.ones(win) / win, mode="same"))
        peaks, _ = find_peaks(env, height=0.35 * env.max(), distance=int(0.15 * sk.SR))
        for p in peaks:
            grain = x[max(0, p - int(0.04 * sk.SR)):p + int(0.12 * sk.SR)]
            out.append(sk.fade_edges(sk.normalize(grain), 0.01, 0.05))
    return out


bar = Discipline(start=1)  # writing goals is planning: no change


def overlay(canvas, t, frame):
    bar.draw(canvas, t, frame)


def soundtrack():
    mix = sk.Mix(DURATION)
    mix.add(sk.pad(["A1", "E2"], DURATION, attack=0.4, release=1.0, brightness=0.05, key="hum"),
            at=0, gain_db=-17, reverb=0.2)

    def steps(walk, until, key, gain=-12):
        for n, (lift, land, foot, a, b) in enumerate(walk.steps):
            if land < until:
                mix.add(sk.footstep(n, weight=0.55, key=key), at=land, gain_db=gain, pan=(b - 960) / 1400,
                        reverb=0.12)

    steps(walk_in, CLOSE_UP, "goals.in")
    steps(step_back, DOOR_SHOT, "goals.back", gain=-15)
    steps(walk_out, DURATION, "goals.out")

    def effect(prompt, seconds, name):            # ElevenLabs effects, all brought to the same level first
        return sk.normalize(sk.eleven_sound(prompt, seconds, name))

    tray = effect("A plastic marker pen put down on a whiteboard's metal tray, one small light click", 0.5,
                  "marker_tray")
    for i, at_ in enumerate((GRAB_ERASER, PUT_ERASER, GRAB_PALE, PUT_PALE)):
        mix.add(tray, at=at_ - 0.2, gain_db=-20 - 2 * (i % 2), pan=-0.1, reverb=0.08)
    wipe = effect("Close-up of a felt whiteboard eraser wiping a whiteboard clean in firm back-and-forth strokes",
                  5.0, "eraser_wipe")
    mix.add(sk.fade_edges(wipe[:int((WIPE_END - WIPE_START + 0.1) * sk.SR)], 0.02, 0.15), at=WIPE_START,
            gain_db=-14, pan=-0.15, reverb=0.08)
    # The writing: ElevenLabs gives a few squeaks with long gaps between them, so the real squeaks are cut out
    # of its marker recordings and placed on his pen strokes, about one every other letter.
    grains = squeaks()
    for i, (a, b) in enumerate(LINES):
        n = len("- " + NEW[i])
        g = rng("goals.squeak", i)
        for j in range(0, n, 2):
            if g.random() < 0.15:
                continue
            at_ = a + (j + 0.25 + g.uniform(-0.2, 0.2)) / n * (b - a)
            mix.add(grains[g.integers(len(grains))], at=at_, gain_db=-15 + g.uniform(-3, 0), pan=-0.1, reverb=0.08)
    door = effect("A door handle pressed down and an apartment door pushed open quickly, the latch clicking, "
                  "close up", 1.2, "door_open")
    latch = int(0.45 * sk.SR)            # the recording's latch clicks 0.6 s in: start just before it
    mix.add(sk.fade_edges(door[latch:], 0.005, 0.1), at=PUSH[0], gain_db=-10, pan=0.3, reverb=0.12)
    return mix
