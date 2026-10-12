"""Film 1, row 11 of the story: too fast. About 17 seconds, one shot along the street at dawn.
It follows row 10, where he stepped out of the door, smiling, into the early light.

 0-3.4 s    He sprints in from the left along the pavement, the camera running with him: long strides,
            leaning forward, arms pumping, determined.
 3.4-7 s    He fades: shorter strides, his face straining, his mouth open; he slows to a stagger and stops.
 7-13 s     He doubles over, hands on his knees, gasping, his breath puffing in the cold air.
 9-15 s     Two grey joggers come up from behind and pass him at an easy, steady pace, without a look.
13-17 s     He lifts his head and watches them go; his determined face sags back to tired.

Sound: the hum, the quiet street, his running steps, his gasping, the joggers' steady steps.
"""
import math

import numpy as np
import skia

from scenes.discipline import Discipline
from scenes.street import GROUND, draw_street
from toolkit import GREY, Camera, Character, Face, Ink, Pose, blink, clamp, lerp, progress, reach
from toolkit import sound as sk
from toolkit.rng import rng

DURATION = 17.0
PEAK_DB = -3.7         # set so the hum matches the other scenes (a gasp is the loudest moment)
DT = 1 / 600           # time step for working out positions from speeds

hero = Character("hero")
DETERMINED = Face(eyes=0.92, brows=-0.6, mouth="frown", mouth_size=0.0, bags=True)

# -- his run: sprinting, fading, stopping -------------------------------------------------------------

V_SPRINT, V_JOG = 760, 280          # pixels per second
FADE = (3.4, 6.0)                   # from a sprint down to a struggling jog...
STAGGER = (6.0, 7.0)                # ...a stagger, and he stops
BEND = (7.0, 7.8)                   # he doubles over
LOOK_UP = (13.0, 14.2)              # he lifts his head to watch the joggers go
SAG = (15.0, 16.4)                  # and his face sags


def his_speed(t):
    if t < FADE[0]:
        return V_SPRINT
    if t < FADE[1]:
        return lerp(V_SPRINT, V_JOG, progress(t, *FADE, "inout"))
    if t < STAGGER[1]:
        return V_JOG * (1 - progress(t, *STAGGER, "linear")) ** 1.5
    return 0.0


class Gait:
    """Running (or jogging) from the side: feet stay planted while on the ground, each landing so it's
    as far ahead of the hips as it will be behind them when it lifts; in between, they swing forward
    with the knee up. speed(t) in pixels per second; the cadence, ground time and how high the feet
    lift follow from how fast he's going (`full` = the speed at which they're at their sprinting values)."""

    def __init__(self, who, speed, x0, ground, full, cadence=(1.7, 3.2), stance=(0.32, 0.12), lift=(14, 75),
                 lean=(6, 22), phase0=0.3, until=DURATION):
        self.who, self.speed, self.ground, self.full, self.lean = who, speed, ground, full, lean
        self.cadence, self.stance, self.lift = cadence, stance, lift
        self.t = np.arange(-2.0, until + 1.0, DT)
        v = np.array([speed(max(t, 0.0)) for t in self.t])
        self.v = v
        self.x = np.cumsum(v) * DT
        self.x += x0 - np.interp(0.0, self.t, self.x)      # at x0 when the scene starts
        share = (v / full) ** 0.8
        steps_per_s = cadence[0] + (cadence[1] - cadence[0]) * share
        phase = np.cumsum(steps_per_s) * DT
        phase += phase0 - np.interp(0.0, self.t, phase)
        self.phase = phase          # whole numbers: a foot lands (even: the left, odd: the right)
        self.steps = []
        k = math.ceil(phase[0])
        while True:
            i = np.searchsorted(phase, k)
            if i >= len(self.t):
                break
            tk = self.t[i]
            if v[i] < 25:
                break
            ts = stance[1] + (stance[0] - stance[1]) * (1 - v[i] / full)
            land = self.hip_x(tk) + 0.5 * (self.hip_x(tk + ts) - self.hip_x(tk))
            self.steps.append((tk, tk + ts, "foot_l" if k % 2 == 0 else "foot_r", land, lift[0] + (lift[1] - lift[0]) * v[i] / full))
            k += 1
        # when he stops, his last two steps settle a natural stance apart under his hips
        if self.steps and v[-1] < 25:
            end = self.hip_x(until)
            for n, side in ((-2, -1), (-1, 1)):
                if len(self.steps) >= 2:
                    tk, tl, foot, land, h = self.steps[n]
                    self.steps[n] = (tk, tl, foot, end + 26 * (1 if foot == "foot_r" else -1), h)

    def hip_x(self, t):
        return float(np.interp(t, self.t, self.x))

    def speed_at(self, t):
        return float(np.interp(t, self.t, self.v))

    def feet(self, t):
        """Where each foot is, and how far it is through a planted stance (0..1, None in the air)."""
        where = {}
        by_foot = {"foot_l": [], "foot_r": []}
        for s in self.steps:
            by_foot[s[2]].append(s)
        for foot, steps in by_foot.items():
            for n, (tk, tl, _, land, h) in enumerate(steps):
                nxt = steps[n + 1] if n + 1 < len(steps) else None
                if t < tk and n == 0:
                    where[foot] = ((land, self.ground), 0.0)
                    break
                if tk <= t < tl or (nxt is None and t >= tk):
                    where[foot] = ((land, self.ground), progress(t, tk, tl, "linear"))
                    break
                if nxt and tl <= t < nxt[0]:      # swinging forward to the next landing
                    u = (t - tl) / (nxt[0] - tl)
                    # the heel kicks up behind first (it rises before it moves forward), then the knee
                    # drives forward and the foot comes down ahead
                    ahead = u * u * (3 - 2 * u)
                    x = lerp(land, nxt[3], ahead ** 1.35)
                    y = self.ground - nxt[4] * math.sin(math.pi * u ** 0.62)
                    where[foot] = ((x, y), None)
                    break
        return where

    def pose(self, t, face, lean_extra=0.0):
        v = self.speed_at(t)
        share = v / self.full
        feet = self.feet(t)
        stand = self.who.stand(self.hip_x(t), self.ground, face=face, facing=1,
                               lean=self.lean[0] + (self.lean[1] - self.lean[0]) * share + lean_extra,
                               **{k: p for k, (p, _) in feet.items()})
        # hips: a little higher in the air between steps, lower as a leg takes his weight; never out of reach
        bend = max([math.sin(math.pi * s) for _, s in feet.values() if s is not None] + [0.0])
        y = stand.y - 5 * share + 9 * share * bend
        leg = 0.99 * sum(self.who.leg)
        lowest = max(p[1] - math.sqrt(max(leg ** 2 - (p[0] - stand.x) ** 2, 0)) for p, _ in feet.values())
        pose = stand.but(y=max(y, lowest))
        # arms bent and pumping against the legs while running: the upper arm swings from the shoulder, the
        # forearm points forward (the front hand at chest height, the back one behind his hip); hanging as he stops
        j = self.who.joints(pose)
        sh, h = j["shoulder"], self.who.height
        upper, fore = self.who.arm
        hands, bends = {}, {}
        cycle = math.cos(math.pi * float(np.interp(t, self.t, self.phase)))
        for hand, swing in (("hand_l", -cycle), ("hand_r", cycle)):
            # swing: 1 = all the way forward (as the other leg lands ahead), -1 = all the way back; it follows
            # his stride smoothly, so an arm never stops at either end
            forward = (swing + 1) / 2
            reach_ = 0.5 + 0.5 * share
            a = math.radians(lerp(-50, 28, forward) * reach_ + pose.lean * 0.5)    # the upper arm, from straight down
            b = a + math.radians(lerp(35, 75, forward))       # the forearm: bent more as it comes forward
            elbow = (sh[0] + upper * math.sin(a), sh[1] + upper * math.cos(a))
            pumping = (elbow[0] + 0.95 * fore * math.sin(b), elbow[1] + 0.95 * fore * math.cos(b))
            hanging = (sh[0] + 6 * swing, sh[1] + 0.31 * h)
            hands[hand] = lerp(hanging, pumping, clamp(share * 2.5))
            # bend the arm the way that puts the elbow low and behind, where it was worked out above (the
            # other way puts it out in front, like a T-rex)
            bends["bend_" + hand] = min((1, -1), key=lambda b: math.dist(reach(sh, hands[hand], upper, fore, b)[0], elbow))
        return pose.but(**hands, **bends)


X0 = -260                      # where his hips are as the scene starts: just off the left of the picture
run = Gait(hero, his_speed, X0, GROUND, V_SPRINT)
X_STOP = run.hip_x(DURATION)

# -- the camera: running with him, then holding ------------------------------------------------------


def _camera_path():
    """Where the camera looks: ahead of him while he runs, settling with him a little left of the
    middle when he stops (room for the joggers to pass). Smoothed so it never jerks."""
    t = run.t
    share = run.v / V_SPRINT
    target = np.maximum(960.0, run.x + 180 + 60 * (1 - share))
    sigma = int(0.35 / DT)
    kernel = np.exp(-0.5 * (np.arange(-3 * sigma, 3 * sigma + 1) / sigma) ** 2)
    kernel /= kernel.sum()
    padded = np.concatenate([np.full(3 * sigma, target[0]), target, np.full(3 * sigma, target[-1])])
    return t, np.convolve(padded, kernel, mode="valid")


CAM_T, CAM_X = _camera_path()
camera = Camera(x=lambda t: float(np.interp(t, CAM_T, CAM_X)), y=560,
                zoom=lambda t: 1.0 + 0.1 * progress(t, BEND[0], 14.0, "inout"),
                handheld=lambda t: 1.0 + 0.8 * (run.speed_at(t) / V_SPRINT), name="fast")

# -- the joggers --------------------------------------------------------------------------------------

JOGGER_GROUND = GROUND - 44     # they run further back on the pavement, behind him (a little smaller there)
joggers = []
for name, height, speed, passes in (("jogger1", 404, 330, 10.6), ("jogger2", 418, 300, 12.3)):
    who = Character(name, height=height, color=GREY)
    x0 = X_STOP - speed * passes       # they reach his spot at `passes` seconds
    joggers.append(Gait(who, lambda t, s=speed: s, x0, JOGGER_GROUND, 330, cadence=(2.6, 2.7), stance=(0.24, 0.24),
                        lift=(22, 26), lean=(7, 7), phase0=0.1 if name == "jogger1" else 0.6))
JOGGER_FACE = Face(eyes=0.9, brows=0.0, mouth="flat", mouth_size=0.5)

# -- him, after the run --------------------------------------------------------------------------------

def _breaths():
    """When each gasping breath starts: quick at first, slowing as he gets his breath back."""
    out, t = [], BEND[1]
    while t < DURATION + 2:
        out.append(t)
        t += lerp(0.8, 1.2, clamp((t - BEND[1]) / 8))
    return out


BREATHS = _breaths()


def gasps(t):
    """How far through the current breath (0..1), and the breath's number (-1 before he gasps)."""
    if t < BEND[1]:
        return 0.0, -1
    n = int(np.searchsorted(BREATHS, t, side="right")) - 1
    return (t - BREATHS[n]) / (BREATHS[n + 1] - BREATHS[n]), n


def his_face(t):
    """Determined, then straining, gasping, and at last sagging back to tired."""
    strain = progress(t, *FADE, "inout")
    if t < STAGGER[1]:
        return Face(eyes=lerp(0.92, 0.6, strain) * blink(t, "hero.fast", every=3.0), brows=lerp(-0.6, 0.6, strain),
                    mouth="open" if strain > 0.25 else "frown", mouth_size=lerp(0.0, 0.6, strain), bags=True)
    u, _ = gasps(t)
    gasp = 0.5 + 0.4 * math.sin(math.pi * u)
    look = progress(t, *LOOK_UP, "inout")
    sag = progress(t, *SAG, "inout")
    if sag > 0.5:
        return Face(eyes=0.45 * blink(t, "hero.fast.sag", every=3.0), brows=0.9, mouth="frown",
                    mouth_size=lerp(0.3, 0.55, sag), bags=True)
    return Face(eyes=lerp(0.3, 0.5, look), brows=0.9, mouth="open", mouth_size=lerp(gasp, 0.35, look), bags=True)


def his_pose(t):
    face = his_face(t)
    if t < STAGGER[1]:
        return run.pose(t, face)
    stop = run.pose(STAGGER[1], face)
    bend = progress(t, *BEND, "inout")
    look = progress(t, *LOOK_UP, "inout")
    sag = progress(t, *SAG, "inout")
    u, n = gasps(t)
    heave = math.sin(2 * math.pi * u) * (1 - 0.5 * look)
    lean = lerp(stop.lean, 66, bend) - 24 * look + 8 * sag + 2.5 * heave * bend
    tilt = lerp(0, -28, bend) - 12 * look + 18 * sag
    pose = stop.but(lean=lean, head_tilt=tilt, y=stop.y + 6 * bend + 2 * heave * bend)
    j = hero.joints(pose.but(hand_l=None, hand_r=None))
    # hands on his knees; as he straightens up they slide up his thighs (never further than his arms reach)
    longest = 0.97 * sum(hero.arm)
    hands = {}
    for hand, knee in (("hand_l", "knee_l"), ("hand_r", "knee_r")):
        target = lerp(getattr(stop, hand), (j[knee][0] + 6, j[knee][1] - 6), bend)
        d = math.dist(j["shoulder"], target)
        if d > longest:
            target = lerp(j["hip"], target, 1 - (d - longest) / max(math.dist(j["hip"], target), 1) * 1.05)
        hands[hand] = target
    return pose.but(**hands)


def puffs(t):
    """His breath clouding in the cold air: (age 0..1, breath number) for each puff still visible.
    Each comes out a third of the way into a breath and lasts 1.4 s; they stop as his face sags."""
    out = []
    for k, start in enumerate(BREATHS[:-1]):
        exhale = start + 0.35 * (BREATHS[k + 1] - start)
        age = (t - exhale) / 1.4
        if 0 <= age < 1 and exhale < SAG[1]:
            out.append((age, k))
    return out


def draw_puffs(canvas, t, j):
    head, r = j["head"], hero.head_r
    pose = his_pose(t)
    a = math.radians(pose.lean + pose.head_tilt)
    mouth = (head[0] + r * 0.95 * math.cos(a), head[1] + r * 0.95 * math.sin(a) + r * 0.3)
    for age, k in puffs(t):
        g = rng("fast.puff", k)
        alpha = 0.16 * (1 - age) ** 1.5
        for c in range(3):
            dx, dy = g.uniform(30, 90) * age + c * 10, -g.uniform(10, 40) * age - c * 6
            rad = 8 + 30 * age + 6 * c
            p = skia.Paint(AntiAlias=True, Color=skia.Color(225, 230, 240, int(255 * alpha)),
                           MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 4 + 10 * age))
            canvas.drawCircle(mouth[0] + dx, mouth[1] + dy, rad, p)


# -- the scene ------------------------------------------------------------------------------------------


def draw(canvas, t, frame):
    with camera.view(canvas, t):
        cx = camera.state(t)[0]
        draw_street(canvas, frame, view=(cx - 1100, cx + 1100))
        for jog in joggers:              # behind him on the pavement
            if cx - 1200 < jog.hip_x(t) < cx + 1200:
                jog.who.draw(canvas, frame, jog.pose(t, JOGGER_FACE.but(eyes=0.9 * blink(t, jog.who.name, every=2.7))))
        j = hero.draw(canvas, frame, his_pose(t))
        draw_puffs(canvas, t, j)


bar = Discipline(start=1, fills=[1.0])  # +1 as he goes out running (it stays, though he fails)


def overlay(canvas, t, frame):
    bar.draw(canvas, t, frame)


def soundtrack():
    mix = sk.Mix(DURATION)
    mix.add(sk.pad(["A1", "E2"], DURATION, attack=0.4, release=1.0, brightness=0.05, key="hum"),
            at=0, gain_db=-17, reverb=0.2)

    def effect(prompt, seconds, name):            # ElevenLabs effects, all brought to the same level first
        return sk.normalize(sk.eleven_sound(prompt, seconds, name))

    street = effect("A quiet city street just before sunrise: distant traffic, a faint cold wind, no voices, "
                    "no birds", 17.0, "street_dawn")
    mix.add(sk.fade_edges(street, 0.5, 1.0), at=0, gain_db=-27)

    def pan(x, t):
        return clamp((x - camera.state(t)[0]) / 960, -1, 1)

    for n, (tk, tl, foot, x, h) in enumerate(run.steps):      # his running steps, lighter as he fades
        if 0 <= tk < DURATION:
            weight = 0.5 + 0.5 * run.speed_at(tk) / V_SPRINT
            mix.add(sk.footstep(n, weight=weight, key="fast.run"), at=tk, gain_db=-10, pan=pan(x, tk), reverb=0.1)
    for jog in joggers:                                        # theirs: steady, easy
        for n, (tk, tl, foot, x, h) in enumerate(jog.steps):
            if 0 <= tk < DURATION:
                mix.add(sk.footstep(n, weight=0.4, key=jog.who.name), at=tk, gain_db=-17, pan=pan(x, tk), reverb=0.1)
    # His gasping: the single gasps are cut out of the ElevenLabs recording and placed on his breaths (the
    # heaving and the puffs), a few heavy ones as he fades, then one a breath, quieter as he recovers.
    from scipy.signal import find_peaks
    gasp = effect("A man gasping and panting heavily for breath after an all-out sprint, bent over, close up, "
                  "no other sounds", 10.0, "gasping")
    win = int(0.02 * sk.SR)
    env = np.sqrt(np.convolve(gasp ** 2, np.ones(win) / win, mode="same"))
    peaks, _ = find_peaks(env, height=0.3 * env.max(), distance=int(0.5 * sk.SR))
    grains = [sk.fade_edges(sk.normalize(gasp[max(0, p - int(0.25 * sk.SR)):p + int(0.45 * sk.SR)]), 0.03, 0.15)
              for p in peaks]
    fading = [FADE[0] + 2.2, FADE[0] + 3.2, STAGGER[0] + 0.4, STAGGER[1] - 0.1]
    exhales = [b + 0.35 * (n - b) for b, n in zip(BREATHS[:-1], BREATHS[1:]) if b < DURATION]
    for k, at_ in enumerate(fading + exhales):
        calmer = -6 * clamp((at_ - BEND[1]) / 9)
        mix.add(grains[k % len(grains)], at=at_ - 0.25, gain_db=-11 + calmer, reverb=0.08)
    bar.add_sounds(mix)
    return mix
