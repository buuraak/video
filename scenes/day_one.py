"""Film 1, row 23 of the story: day one. About 25 seconds: three small things, each followed by a quick cut to
the board as his arm ticks its box and the discipline bar fills one step. It follows row 22, where he wrote
TODAY and the five easy things on the clean board.

 0-1.9 s     The alarm clock from the front: 6:00, beeping, as in the loop. His arm comes in from the right and
             presses the button: not a slow, heavy press, not a slam.
 1.9-7.6 s   From above, the opening view: he lies awake a moment, breathes in, throws the blanket off and gets
             up, calmly (scene 2's moves, a little brisker), and walks out to the right.
 7.6-9.4 s   The board: he ticks "Get up when the alarm rings". The bar fills one step.
 9.4-14.1 s  From above, sped up, the clock racing: he cleans the room. The clothes, the cups, the pizza box
             and his empty bottles go, one after another.
14.1-15.9 s  The board: he ticks "Clean your room". The bar fills another step.
15.9-22.4 s  The street at dawn, from the side: he walks at an easy pace. The same two grey joggers as in
             row 11 come up from behind and pass him; this time he doesn't try to keep up.
22.4-25 s    The board: he ticks "Go for a walk". The bar fills a third step; we hold on three ticks.

No caption. No hum: only the alarm, his steps, the room, the street, the marker and the bar.
"""
import math

import scenes.five_things as five
import scenes.new_goals as goals
import scenes.scroll as scroll
import scenes.too_fast as fast
import scenes.up_at_once as up
from scenes import wipe
from scenes.bedroom import (BOTTLES, HERO_X, HIP_Y, ROOM, belly_hands, box, clock_numbers, draw_bed, draw_blanket,
                            draw_mess, draw_nightstand, hero, rounded_rect)
from scenes.discipline import Discipline
from scenes.door_wall import draw_board, draw_marker, draw_today, five_box, tick_point
from scenes.door_wall import hero as side_hero        # at the size of the side views
from scenes.new_goals import Walk, squeaks
from scenes.street import GROUND, draw_street
from scenes.the_board import BOARD_H, CLOSE
from scenes.wake_up import ARM, BUTTON, BUTTON_DOWN, CLOCK, TABLE, WINDOW
from toolkit import GREY, Camera, Character, Face, Ink, Pose, Track, blink, clamp, lerp, progress, reach
from toolkit import sound as sk
from toolkit.rng import rng

PEAK_DB = -2.4          # set so his sounds sit at the same level as the sounds in the other scenes

BED = 1.9              # cut to the room from above
TICK_1 = 7.6           # cut to the board: the first tick
CLEAN = 9.4            # cut to the room: cleaning, sped up
TICK_2 = 14.1          # the second tick
WALK = 15.9            # cut to the street
TICK_3 = 22.4          # the third tick
TICK_LENGTH = 1.8      # each tick shot (the last holds on longer)
DURATION = 25.0

CALM = Face(eyes=0.6, brows=0.3, mouth="flat", mouth_size=0.5, bags=True)     # awake, tired, not frozen

# -- shot 1: the alarm, pressed --------------------------------------------------------------------------

PRESS = 1.3            # his hand presses the button, in the middle of a burst of beeps (sk.alarm_on)
ON_BUTTON = (1255, BUTTON[1] - 12)
SHOULDER = (760, 200)  # from the end of his arm, just off screen to the right
ARM_END = Track((0.5, (1990, 330)), (1.05, (1262, 296), "inout"), (PRESS, ON_BUTTON, "inout"),
                (PRESS + 0.06, (ON_BUTTON[0], ON_BUTTON[1] + BUTTON_DOWN), "out"),
                (PRESS + 0.3, (1262, 290), "inout"), (BED, (1500, 330), "in"))
clock_camera = Camera(zoom=1.075, name="dayone.clock")


def shot_clock(canvas, t, frame):
    with clock_camera.view(canvas, t):
        ink = Ink(canvas, frame, color=ROOM, width=8.0, prefix="clock")
        ink.floor(TABLE, key="table", width=6.0)
        ink.floor(TABLE + 22, key="table.front", width=5.0)
        pressed = BUTTON_DOWN * progress(t, PRESS, PRESS + 0.06, "out") * (1 - progress(t, PRESS + 0.15, PRESS + 0.3))
        box(ink, rounded_rect(BUTTON[0], BUTTON[1] + pressed, BUTTON[2], BUTTON[3] + 6, 12), "button", width=7.0)
        box(ink, rounded_rect(*CLOCK, 84), "body", width=9.0)
        box(ink, rounded_rect(*WINDOW, 44), "window", width=6.0)
        lit = 1.0 if t >= PRESS or sk.alarm_on(t) else 0.0
        clock_numbers(canvas, frame, "6:00", ((WINDOW[0] + WINDOW[2]) / 2, (WINDOW[1] + WINDOW[3]) / 2 + 2), 320,
                      "clock.big", on=lit)
        if t >= ARM_END.keys[0][0]:
            end = ARM_END(t)
            shoulder = (end[0] + SHOULDER[0], end[1] + SHOULDER[1])
            elbow, end, _ = reach(shoulder, end, *ARM, 1)
            five.draw_arm(canvas, frame, shoulder, elbow, end)


# -- shot 2: from above, he gets up ------------------------------------------------------------------------

THROW = BED + 1.1                      # a moment lying awake, a breath in, then he throws the blanket off
SIT = THROW + (up.SIT - up.THROW)      # row 9's fling, at the same speed
PACE = 1.25                            # then scene 2's getting-up moves, a little brisker than tired
BREATH = Track((BED, 0.0), (BED + 0.6, 0.9, "inout"), (THROW, 0.3), (SIT, 0.1))
bed_camera = Camera(name="dayone.bed")


def scene2_time(t):
    return scroll.SIT + (t - SIT) * PACE


def our_time(t2):
    return SIT + (t2 - scroll.SIT) / PACE


def lying_pose(t):
    """Lying awake, hands on his belly; then the fling (row 9's, moved to our time)."""
    b = BREATH(t)
    pose = Pose(x=HERO_X, y=HIP_Y - 3 * b)
    left, right = belly_hands(hero.joints(pose)["shoulder"], max(b, 0))
    thrown = 0.0
    if t >= THROW - 0.2:
        right, thrown = up.fling(t - (THROW - up.THROW), right)
    return pose.but(hand_l=left, hand_r=right), b, thrown


LYING_END = hero.skeleton(lying_pose(SIT)[0])


def shot_bed(canvas, t, frame):
    with bed_camera.view(canvas, t):
        room = Ink(canvas, frame, color=ROOM, width=4.0, prefix="bedroom")
        draw_bed(room)
        draw_nightstand(room, canvas, frame, time="6:00")
        draw_mess(room, ("clothes", "cups", "pizza"))
        if t < SIT:
            pose, b, thrown = lying_pose(t)
            j = hero.skeleton(pose, frame)
            pen = scroll.draw_body(canvas, frame, j, ("legs", "spine", "head"), hero.head_r)
            draw_blanket(room, b, thrown)
            face = CALM.but(eyes=CALM.eyes * blink(t, "hero.dayone", every=2.6, length=0.22))
            scroll.draw_his_face(canvas, pen, j["head"], hero.head_r, face, 0.0, 0.0, 0.0)
            scroll.draw_body(canvas, frame, j, ("arms",), hero.head_r)
        else:
            j, head_r, away = scroll.getting_up(scene2_time(t), LYING_END)
            draw_blanket(room, 0.0, 1.0)
            pen = scroll.draw_body(canvas, frame, j, ("legs", "arms", "spine", "head"), head_r)
            scroll.draw_his_face(canvas, pen, j["head"], head_r, CALM, 0.0, 0.0, away)


# -- the ticks: the board close up, his arm ticks a box --------------------------------------------------

BOARD = five.BOARD                     # wiped clean in row 21
DAYS = five.DAYS
TO_TICK, TICKING, AWAY = (0.0, 0.45), (0.45, 0.75), (0.8, 1.35)   # within a tick shot


class Ticks:
    """The tick shots: the board close up, his arm with the pale marker ticking a box, and the bar filling a
    step as the tick is done. shots: (when the shot starts, which box), in order. done: how many boxes were
    already ticked before this scene (the ticks go top to bottom)."""

    camera = Camera(x=720, y=530, zoom=1.25, name="dayone.tick")  # TODAY and the whole list in view

    def __init__(self, shots, done=0):
        self.shots, self.done = shots, done

    def shot(self, t):
        """Which tick shot is on screen, and how far into it we are."""
        k = max(i for i, (t0, _) in enumerate(self.shots) if t >= t0)
        return self.shots[k][1], t - self.shots[k][0]

    def tip(self, box_i, u):
        """Where the pale marker's tip is, u seconds into the tick shot for box box_i: up from below, the
        tick, away."""
        below = (five_box(CLOSE, box_i)[0] - 40, 1180)
        gone = (five_box(CLOSE, box_i)[0] + 260, 1200)
        if u < TICKING[0]:
            return lerp(below, tick_point(CLOSE, box_i, 0.0), progress(u, *TO_TICK, "out"))
        if u < TICKING[1]:
            return tick_point(CLOSE, box_i, progress(u, *TICKING, "inout"))
        end = tick_point(CLOSE, box_i, 1.0)
        lifted = (end[0] + 30, end[1] - 20)
        if u < AWAY[0]:
            return lerp(end, lifted, progress(u, TICKING[1], AWAY[0], "out"))
        return lerp(lifted, gone, progress(u, *AWAY, "in"))

    def ticked(self, t):
        """How much of each box's tick is drawn at time t."""
        return [1.0] * self.done + [progress(t, t0 + TICKING[0], t0 + TICKING[1], "inout")
                                    for t0, _ in self.shots if t >= t0]

    def fills(self):
        """When the bar fills a step: as each tick is done."""
        return [t0 + TICKING[1] for t0, _ in self.shots]

    def squeaks(self):
        """When the marker squeaks: twice on each tick."""
        return [t0 + TICKING[0] + d for t0, _ in self.shots for d in (0.02, 0.14)]

    def draw(self, canvas, t, frame):
        box_i, u = self.shot(t)
        with self.camera.view(canvas, t):
            draw_board(canvas, frame, CLOSE, DAYS, key="board", on_tray=("eraser", "red"), **BOARD)
            draw_today(canvas, frame, CLOSE, ticks=self.ticked(t))
            if u < AWAY[1]:
                tip = self.tip(box_i, u)
                shoulder, elbow, hand, angle = five.holding_tip(tip)
                draw_marker(canvas, frame, tip, angle, BOARD_H, "pale", "board")
                five.draw_arm(canvas, frame, shoulder, elbow, hand)


ticks = Ticks([(TICK_1, 0), (TICK_2, 1), (TICK_3, 2)])


# -- shot 4: cleaning the room, sped up ---------------------------------------------------------------------
# Seen truly from above (his head on top, his arms and feet poking out as he walks). He comes in from the
# right, goes round the room and the foot of the bed, and each piece goes as he stops by it.

SPEED = 1100           # pixels per second, sped up
STOP, MAKE = 0.22, 0.55        # seconds he stops to pick a piece up; to pull the blanket back over the bed
# His way round: (where he stops, what he clears there). "bed": he makes the bed, which uncovers the cup
# that lay under the thrown-off blanket.
ROUTE = [((2050, 560), ()), ((1430, 470), ("jeans",)), ((1350, 655), ("cup2",)), ((1395, 800), ("tshirt",)),
         ((1300, 985), ()), ((720, 990), ()), ((560, 805), ("pizza",)), ((745, 760), ("bed",)),
         ((725, 690), ("cup1",)), ((710, 545), ("bottle1", "cup0", "bottle0"))]


def _route():
    """Each stretch of his way round the room: (start time, end time, from, to, what goes at the end, how long
    he stops there)."""
    out, t = [], CLEAN + 0.15
    for (a, _), (b, take) in zip(ROUTE[:-1], ROUTE[1:]):
        d = math.dist(a, b) / SPEED
        dwell = MAKE if "bed" in take else STOP if take else 0.0
        out.append((t, t + d, a, b, take, dwell))
        t += d + dwell
    return out


LEGS = _route()


def cleaner(t):
    """(hips, heading in degrees, how far he's walked, moving 0..1, picking up 0..1) at time t."""
    walked, heading, dwell = 0.0, None, STOP
    for t0, t1, a, b, take, stay in LEGS:
        if t < t0:          # stopped where the last stretch ended, picking something up and turning to go on
            u = clamp((t - (t0 - dwell)) / dwell)
            if heading is None:
                return a, _heading(a, b), walked, 0.0, 0.0
            turn = (_heading(a, b) - heading + 180) % 360 - 180
            return a, heading + turn * u * u * (3 - 2 * u), walked, 0.0, math.sin(math.pi * u)
        heading, dwell = _heading(a, b), stay
        if t < t1:
            share = progress(t, t0, t1, "linear")
            u = _cruise(share)
            moving = min(share / 0.25, (1 - share) / 0.25, 1.0)         # in step with his speed
            return lerp(a, b, u), heading, walked + math.dist(a, b) * u, moving, 0.0
        walked += math.dist(a, b)
    return LEGS[-1][3], heading, walked, 0.0, math.sin(math.pi * clamp((t - LEGS[-1][1]) / STOP))


def _cruise(s, ramp=0.25):
    """Along a stretch: speeding up over its first quarter, steady, slowing down over its last quarter (a gentler
    top speed than easing in and out the whole way)."""
    if s < ramp:
        return s * s / (2 * ramp * (1 - ramp))
    if s < 1 - ramp:
        return (s - ramp / 2) / (1 - ramp)
    return 1 - (1 - s) ** 2 / (2 * ramp * (1 - ramp))


def _heading(a, b):
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))


def striding(t):
    """0..1: how much his legs and arms swing, from how fast he's really going, smoothed (so a short stretch
    between two stops is a couple of small steps, and they never stop dead)."""
    out = []
    for d in (-0.06, -0.03, 0.0, 0.03, 0.06):
        a, b = cleaner(t + d - 0.01)[0], cleaner(t + d + 0.01)[0]
        out.append(clamp(math.dist(a, b) / 0.02 / SPEED))
    return sum(out) / len(out)


def turning(t):
    """His heading, turning smoothly from one stretch to the next rather than snapping."""
    angles = [cleaner(t + d)[1] for d in (-0.1, -0.05, 0.0, 0.05, 0.1)]
    base = angles[2]
    unwrapped = [base + ((a - base + 180) % 360 - 180) for a in angles]
    return sum(unwrapped) / len(unwrapped)


def gone_by(t):
    """Every piece cleared away by time t."""
    out = set()
    for t0, t1, a, b, take, stay in LEGS:
        if t >= t1 + stay / 2:
            out.update(take)
    return out


def bed_made(t):
    """0..1: how far he has pulled the blanket back over the bed."""
    for t0, t1, a, b, take, stay in LEGS:
        if "bed" in take:
            return progress(t, t1 + 0.05, t1 + stay - 0.05, "inout")
    return 0.0


GLIDE = 700            # pixels per step while sped up: his legs swing slower than he moves, or they'd flicker


def overhead_joints(hip, heading, walked, moving, pick, stride_length=scroll.STRIDE):
    """Him standing or walking, seen from straight above: (joints, head size). Walking along `heading`; as he
    picks something up he bends forward, his head going ahead and his hands coming together in front of him."""
    r = hero.head_r * 1.15
    phase = math.pi * walked / stride_length
    swing, stride = 72 * math.sin(phase) * moving, 140 * math.sin(phase) * moving
    lean = 26 * moving + 30 * pick
    side = r + 34
    local = {"hip": (0, 0), "neck": (6 + lean, 0), "shoulder": (8 + lean, 0), "head": (10 + lean, 0),
             "elbow_l": (4 + lean - swing * 0.35, r + 4), "hand_l": (-4 + lean - swing, side),
             "elbow_r": (4 + lean + swing * 0.35, -r - 4), "hand_r": (-4 + lean + swing, -side),
             "foot_l": (-10 + stride, 22), "knee_l": (-4 + stride * 0.55, 20),
             "foot_r": (-10 - stride, -22), "knee_r": (-4 - stride * 0.55, -20)}
    for hand, elbow, sy in (("hand_l", "elbow_l", 1), ("hand_r", "elbow_r", -1)):   # reaching down in front
        local[hand] = lerp(local[hand], (lean + r + 26, sy * 20), pick)
        local[elbow] = lerp(local[elbow], (lean + r * 0.6, sy * (r - 4)), pick)
    c, s = math.cos(math.radians(heading)), math.sin(math.radians(heading))
    return {k: (hip[0] + x * c - y * s, hip[1] + x * s + y * c) for k, (x, y) in local.items()}, r


def clean_clock(t):
    """The clock racing while he cleans: from 6:12 to 6:41."""
    m = int(round(lerp(12, 41, progress(t, CLEAN, TICK_2, "linear"))))
    return f"6:{m:02d}"


clean_camera = Camera(name="dayone.clean")


def shot_clean(canvas, t, frame):
    with clean_camera.view(canvas, t):
        gone = gone_by(t)
        room = Ink(canvas, frame, color=ROOM, width=4.0, prefix="bedroom")
        draw_bed(room)
        draw_nightstand(room, canvas, frame, time=clean_clock(t),
                        bottles=[i for i in range(len(BOTTLES)) if f"bottle{i}" not in gone])
        draw_mess(room, ("clothes", "cups", "pizza"), gone=gone)
        draw_blanket(room, 0.0, 1.0 - bed_made(t), made=True)
        hip, _, walked, _, pick = cleaner(t)
        j, r = overhead_joints(hip, turning(t), walked, striding(t), pick, GLIDE)
        scroll.draw_body(canvas, frame, j, ("legs", "arms", "spine", "head"), r)


# -- shot 6: the walk round the block ---------------------------------------------------------------------

EASY = 170             # pixels per second: an easy walking pace
walk = Walk(WALK - 0.6, 200, 200 + 3000, EASY, ramp=0.0)
JOGGERS = []
for name, height, speed, behind in (("jogger1", 404, 380, 760), ("jogger2", 418, 360, 1000)):
    who = Character(name, height=height, color=GREY)
    x0 = walk.hip_x(WALK) - behind
    JOGGERS.append(fast.Gait(who, lambda t, s=speed: s, x0, fast.JOGGER_GROUND, 330, cadence=(2.6, 2.7),
                             stance=(0.24, 0.24), lift=(22, 26), lean=(7, 7),
                             phase0=0.1 if name == "jogger1" else 0.6, until=DURATION))
STREET_T0 = WALK       # the joggers' clocks start with the shot


def jog_time(t):
    return t - STREET_T0


street_camera = Camera(x=lambda t: walk.hip_x(t) + 160, y=560, name="dayone.street")


def shot_walk(canvas, t, frame):
    with street_camera.view(canvas, t):
        cx = street_camera.state(t)[0]
        draw_street(canvas, frame, view=(cx - 1100, cx + 1100))
        for jog in JOGGERS:              # further back on the pavement, behind him
            tj = jog_time(t)
            if cx - 1200 < jog.hip_x(tj) < cx + 1200:
                jog.who.draw(canvas, frame, jog.pose(tj, fast.JOGGER_FACE.but(eyes=0.9 * blink(t, jog.who.name, every=2.7))))
        face = CALM.but(eyes=0.7 * blink(t, "hero.dayone.walk", every=2.9), brows=0.15)
        side_hero.draw(canvas, frame, walk.pose(t, face, head_tilt=-1))


# -- the scene ------------------------------------------------------------------------------------------


def draw(canvas, t, frame):
    if t < BED:
        shot_clock(canvas, t, frame)
    elif t < TICK_1:
        shot_bed(canvas, t, frame)
    elif t < CLEAN:
        ticks.draw(canvas, t, frame)
    elif t < TICK_2:
        shot_clean(canvas, t, frame)
    elif t < WALK:
        ticks.draw(canvas, t, frame)
    elif t < TICK_3:
        shot_walk(canvas, t, frame)
    else:
        ticks.draw(canvas, t, frame)


bar = Discipline(fills=ticks.fills())  # +1 for each tick


def overlay(canvas, t, frame):
    bar.draw(canvas, t, frame)


def soundtrack():
    mix = sk.Mix(DURATION)

    def effect(prompt, seconds, name):            # ElevenLabs effects, all brought to the same level first
        return sk.normalize(sk.eleven_sound(prompt, seconds, name))

    # the alarm, until he presses it
    mix.add(sk.alarm(PRESS), at=0, gain_db=-5, reverb=0.12)
    mix.add(sk.tick(key="dayone.button"), at=PRESS, gain_db=-6, reverb=0.1)
    mix.add(sk.whoosh(0.4, peak=0.6, low=150, high=900, key="dayone.arm"), at=0.6, gain_db=-22)
    # getting up
    mix.add(sk.whoosh(0.45, peak=0.4, low=180, high=1400, key="dayone.blanket"), at=THROW + 0.1, gain_db=-14,
            reverb=0.15)
    mix.add(sk.whoosh(0.5, peak=0.5, low=150, high=900, key="dayone.sit"), at=SIT, gain_db=-20, reverb=0.15)
    for i, (a, _) in enumerate(scroll.PUSHES):
        mix.add(sk.whoosh(0.25, peak=0.4, low=150, high=800, key=("dayone.scoot", i)), at=our_time(a), gain_db=-22,
                reverb=0.1)
    mix.add(sk.footstep(9, weight=0.5, key="dayone.floor"), at=our_time(scroll.STAND + 0.35), gain_db=-14, pan=0.35,
            reverb=0.1)
    for n, (at, x) in enumerate(scroll.footstep_times()):
        when = our_time(at)
        if when < TICK_1:
            mix.add(sk.footstep(n, weight=0.6, key="dayone.step"), at=when, gain_db=-12,
                    pan=clamp((x - 960) / 960, -1, 1), reverb=0.12)
    # the ticks: two squeaks of the marker each
    grains = squeaks()
    g = rng("dayone.squeak")
    for at in ticks.squeaks():
        mix.add(grains[g.integers(len(grains))], at=at, gain_db=-15, pan=-0.15, reverb=0.08)
    # cleaning, sped up: quick light steps, and each piece picked up
    k, last = 0, 0.0
    for f in range(int(CLEAN * 100), int(TICK_2 * 100)):
        t = f / 100
        walked = cleaner(t)[2]
        if walked - last >= GLIDE:
            last = walked
            mix.add(sk.footstep(k, weight=0.35, key="dayone.clean"), at=t, gain_db=-19, reverb=0.08)
            k += 1
    for t0, t1, a, b, take, stay in LEGS:
        for i, piece in enumerate(take):
            at = t1 + stay / 2 + 0.03 * i
            if piece == "bed":                               # the blanket, pulled straight
                mix.add(sk.whoosh(0.45, peak=0.4, low=180, high=1400, key="dayone.made"), at=t1, gain_db=-16,
                        reverb=0.12)
            elif piece.startswith(("cup", "bottle")):        # a clink
                mix.add(sk.highpass(sk.tick(key=("dayone.clink", piece)), 1500), at=at, gain_db=-16, reverb=0.1)
            elif piece == "pizza":                           # cardboard
                mix.add(sk.thud(0.3, key="dayone.box"), at=at, gain_db=-18, reverb=0.08)
            else:                                            # cloth
                mix.add(sk.whoosh(0.2, peak=0.5, low=300, high=2500, key=("dayone.cloth", piece)), at=at,
                        gain_db=-20, reverb=0.08)
    # the street: its quiet sound, his easy steps, the joggers'
    street = effect("A quiet city street just before sunrise: distant traffic, a faint cold wind, no voices, "
                    "no birds", 17.0, "street_dawn")
    mix.add(sk.fade_edges(street[:int((TICK_3 - WALK) * sk.SR)], 0.05, 0.05), at=WALK, gain_db=-27)
    for n, (lift, land, foot, a, b) in enumerate(walk.steps):
        if WALK <= land < TICK_3:
            mix.add(sk.footstep(n, weight=0.5, key="dayone.walk"), at=land, gain_db=-13,
                    pan=clamp((b - street_camera.state(land)[0]) / 960, -1, 1), reverb=0.1)
    for jog in JOGGERS:
        for n, (tk, tl, foot, x, h) in enumerate(jog.steps):
            at = tk + STREET_T0
            if WALK <= at < TICK_3:
                mix.add(sk.footstep(n, weight=0.4, key=jog.who.name), at=at, gain_db=-17,
                        pan=clamp((x - street_camera.state(at)[0]) / 960, -1, 1), reverb=0.1)
    bar.add_sounds(mix)
    return mix
