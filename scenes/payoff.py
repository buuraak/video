"""Film 1, row 30 of the story: the payoff. About 20 seconds, four shots joined by hard cuts. It follows row 29,
where he walked out into the rain.

 0-6.0 s     The street in the thinning rain, from the side, the camera running with him: he runs, steady, the run
             he failed at the start, and keeps going. Sam waits at a corner ahead, raises a hand, and falls in
             beside him without stopping (they planned it).
 6.0-8.4 s   Closer on the two of them running side by side, the rain nearly gone: he smiles, the first since
             row 10.
 8.4-14.0 s  The park, from the side, as the rain stops: they run along the path past the trees, and the trees'
             leaves come up a soft, muted green: the film's first green. The bar fills its last step and turns
             green with them. Grass and everything else stay grey.
14.0-20.0 s  Wide, from behind, in depth: the park path leading away between the green trees, the two of them
             running away along it, smaller and smaller, still going.

Sound: the rain thinning away, their steps, birds once in the park, and the film's first music (ElevenLabs):
a warm, hopeful piece, quiet at first, swelling with the green.
"""
import math

import numpy as np
import skia

import scenes.out as out
import scenes.too_fast as fast
from scenes.bedroom import ROOM, box
from scenes.discipline import Discipline
from scenes.scroll import glow
from scenes.street import GROUND, draw_street
from scenes.weeks_after import draw_sam_hair
from toolkit import BG, GREEN, INK, Camera, Character, Face, Ink, Track, blink, clamp, lerp, progress, to_color
from toolkit import sound as sk
from toolkit.rng import rng

PEAK_DB = -4.1          # set so the sounds sit at the same level as the sounds in the other scenes
CLOSER = 6.0            # cut closer on the two of them
PARK = 8.4              # cut to the park
AWAY = 14.0             # cut to the wide shot from behind
DURATION = 20.0
GREENING = (9.6, 11.8)  # the trees' leaves come up green
LAST_STEP = 10.6        # the bar fills its last step (and turns green as it does)

LEAF_GREEN = (74, 124, 88)       # a soft, muted green for the leaves
LEAF_LINE = (120, 170, 130)

# -- the two runners, from the side ---------------------------------------------------------------------------

V = 480                 # their running pace: steady, not row 11's sprint
X0 = 200
him = fast.Gait(fast.hero, lambda t: V, X0, GROUND, 760, until=DURATION)
sam = Character("sam", height=430)
SAM_GROUND = GROUND - 40                    # further back on the pavement, beside him
GO = 4.0                                    # Sam sets off as he comes up
RAMP = 1.0                                  # ...and is up to his pace this fast


def _sam_gait(x0):
    return fast.Gait(sam, lambda gt: V * min(1.0, 0.15 + 0.85 * gt / RAMP), x0, SAM_GROUND, 760, phase0=0.15,
                     until=DURATION - GO)


_trial = _sam_gait(0.0)
GAP = 140                                   # he stays a little ahead of Sam, so they don't overlap
sam_run = _sam_gait(him.hip_x(GO + 3.0) - GAP - _trial.hip_x(3.0))   # so that, once running, Sam is beside him
SAM_WAITS = sam_run.hip_x(0.0)
WAVE = (2.6, 3.8)                           # Sam raises a hand as he comes, and lowers it to go

RUNNING = Face(eyes=0.8, brows=-0.15, mouth="open", mouth_size=0.25, bags=True)
SAM_FACE = Face(eyes=0.85, brows=0.0, mouth="smile", mouth_size=0.6)
SMILE = (CLOSER + 0.5, CLOSER + 1.5)


def his_face(t):
    s = progress(t, *SMILE, "inout")
    eyes = 0.8 * blink(t, "hero.payoff", every=2.7)
    if s <= 0:
        return RUNNING.but(eyes=eyes)
    return Face(eyes=eyes, brows=lerp(-0.15, 0.0, s), mouth="smile", mouth_size=0.7 * s, bags=True)


def sam_pose(t):
    """Waiting at the corner (raising a hand as he comes), then running beside him."""
    face = SAM_FACE.but(eyes=0.85 * blink(t, "sam.payoff", every=2.5))
    if t < GO:
        pose = sam_run.pose(0.0, face)
        sh = sam.joints(pose)["shoulder"]
        up = progress(t, WAVE[0], WAVE[0] + 0.4, "out") * (1 - progress(t, WAVE[1] - 0.3, WAVE[1], "inout"))
        if up > 0:
            hand = lerp(pose.hand_r, (sh[0] + 40 + 18 * math.sin(2 * math.pi * 2.2 * t), sh[1] - 125), up)
            pose = pose.but(hand_r=hand, bend_hand_r=-1)
        return pose
    return sam_run.pose(t - GO, face)


def draw_runners(canvas, frame, t):
    j = sam.draw(canvas, frame, sam_pose(t))                       # Sam first: further back on the pavement
    draw_sam_hair(canvas, frame, j["head"], sam.head_r, "payoff.sam.hair")
    fast.hero.draw(canvas, frame, him.pose(t, his_face(t)))


# -- shot 1: the street, the rain thinning; Sam joins ----------------------------------------------------------

street_camera = Camera(x=lambda t: him.hip_x(t) + 280, y=560, handheld=lambda t: 1.6, name="payoff.street")


def rain_amount(t):
    return 1 - progress(t, 0.0, PARK - 0.6, "in")


def shot_street(canvas, t, frame):
    with street_camera.view(canvas, t):
        cx = street_camera.state(t)[0]
        draw_street(canvas, frame, view=(cx - 1100, cx + 1100))
        canvas.drawPaint(skia.Paint(Color=to_color((10, 12, 16, int(70 * rain_amount(t))))))
        draw_runners(canvas, frame, t)
        out.draw_rain(canvas, t, (cx - 1100, -100, cx + 1100, GROUND + 40), "payoff.street", count=320,
                      alpha=int(70 * rain_amount(t)))


# -- shot 2: closer, his smile -------------------------------------------------------------------------------

closer_camera = Camera(x=lambda t: him.hip_x(t) + 10, y=Track((CLOSER, 520), (PARK, 515, "linear")),
                       zoom=Track((CLOSER, 1.75), (PARK, 1.85, "linear")), handheld=lambda t: 1.4, name="payoff.closer")


def shot_closer(canvas, t, frame):
    with closer_camera.view(canvas, t):
        cx = closer_camera.state(t)[0]
        draw_street(canvas, frame, view=(cx - 700, cx + 700))
        canvas.drawPaint(skia.Paint(Color=to_color((10, 12, 16, int(70 * rain_amount(t))))))
        draw_runners(canvas, frame, t)
        out.draw_rain(canvas, t, (cx - 700, 0, cx + 700, GROUND + 40), "payoff.closer", count=140,
                      alpha=int(70 * rain_amount(t)))


# -- shot 3: the park, from the side; the green comes -----------------------------------------------------------

TREE_BASE = GROUND - 70          # the trees stand on the grass behind the path


def _trees():
    out_, g, x = [], rng("payoff.trees"), -2000.0
    while x < 14000:
        out_.append((x, g.uniform(300, 430), g.uniform(110, 160), g.integers(1000)))
        x += g.uniform(360, 520)
    return out_


TREES = _trees()


def greening(t):
    return progress(t, *GREENING, "inout")


def draw_tree(canvas, frame, x, height, r, seed, green, key):
    """A tree from the side: a trunk with two branches, and a round canopy of a few overlapping blobs."""
    ink = Ink(canvas, frame, color=ROOM, width=4.5, prefix=key)
    top = (x, TREE_BASE - height)
    ink.line((x, TREE_BASE), top, "trunk", width=6.0, taper=0.3)
    g = rng("payoff.tree", seed)
    for k, side in enumerate((-1, 1)):
        y = TREE_BASE - height * g.uniform(0.55, 0.7)
        ink.line((x, y), (x + side * r * 0.5, y - r * 0.4), f"branch{k}", width=3.5, taper=0.4)
    fill = lerp((34, 36, 40), LEAF_GREEN, green)
    line = lerp(ROOM[:3], LEAF_LINE, green)
    leaves = Ink(canvas, frame, color=(*[int(c) for c in line], 210), width=3.5, prefix=key + ".leaves")
    for k in range(4):
        cx = x + g.uniform(-0.6, 0.6) * r
        cy = top[1] + g.uniform(-0.5, 0.3) * r
        leaves.circle((cx, cy), r * g.uniform(0.55, 0.8), f"blob{k}", fill=tuple(int(c) for c in fill))


def draw_park(canvas, frame, t, view):
    """The park from the side: a pale sky (the rain has stopped), a low line of far trees, the trees along the
    path, the grass and the path they run on."""
    x0, x1 = view
    sky = skia.GradientShader.MakeLinear([skia.Point(0, 132), skia.Point(0, TREE_BASE)],
                                         [to_color((44, 47, 54)), to_color((84, 88, 96))])
    canvas.drawRect(skia.Rect(x0 - 400, -400, x1 + 400, TREE_BASE), skia.Paint(Shader=sky))
    far = Ink(canvas, frame, color=(70, 74, 80), width=2.5, prefix="payoff.far")
    pts, g = [], rng("payoff.far")
    for x in np.arange(x0 - 400, x1 + 400, 90):
        pts.append((x, TREE_BASE - 120 - 40 * math.sin(x * 0.004) - g.uniform(0, 25)))
    far.fill(pts + [(x1 + 400, TREE_BASE), (x0 - 400, TREE_BASE)], "hills.fill", color=(36, 38, 44), wobble=0)
    far.stroke(pts, "hills", taper=0.0)
    canvas.drawRect(skia.Rect(x0 - 400, TREE_BASE, x1 + 400, 1200), skia.Paint(Color=to_color((26, 27, 30))))
    green = greening(t)
    for i, (x, height, r, seed) in enumerate(TREES):
        if x0 - 300 < x < x1 + 300:
            draw_tree(canvas, frame, x, height, r, seed, green, f"payoff.tree{i}")
    near = Ink(canvas, frame, color=ROOM, width=4.0, prefix="payoff.path")
    near.floor(TREE_BASE, key="grass.back", width=3.0, x0=x0 - 400, x1=x1 + 400)
    near.floor(GROUND, key="path", width=4.0, x0=x0 - 400, x1=x1 + 400)
    near.floor(GROUND + 46, key="path.edge", width=3.5, x0=x0 - 400, x1=x1 + 400)


park_camera = Camera(x=lambda t: him.hip_x(t) + 120, y=Track((PARK, 560), (AWAY, 555, "linear")),
                     zoom=Track((PARK, 1.05), (AWAY, 1.12, "linear")), handheld=lambda t: 1.2, name="payoff.park")


def shot_park(canvas, t, frame):
    with park_camera.view(canvas, t):
        cx = park_camera.state(t)[0]
        draw_park(canvas, frame, t, (cx - 1100, cx + 1100))
        glow(canvas, (cx + 300, 260), 1300, (210, 212, 205), 0.06 * greening(t))      # the light lifting
        draw_runners(canvas, frame, t)


# -- shot 4: wide, from behind, in depth: running away along the park path --------------------------------------

project = out.project
HEIGHT = out.HEIGHT
RUN_SPEED = 2.4 / 1.8 * HEIGHT          # 2.4 metres a second, in world pixels
STRIDE = 0.62 * HEIGHT                  # one running step
START_Z = 1.0 * out.F
SAM_HEIGHT = 430 / 440 * HEIGHT


def _park_trees():
    trees, g = [], rng("payoff.depth.trees")
    for side in (-1, 1):
        z = g.uniform(2.4, 3.2) * out.F
        while z < 22 * out.F:
            trees.append((side * g.uniform(1250, 1450), z, g.uniform(1.4, 1.65) * HEIGHT, g.uniform(0.34, 0.42) * HEIGHT,
                          g.integers(1000)))
            z += g.uniform(2.3, 3.0) * out.F
    return sorted(trees, key=lambda tr: -tr[1])          # far ones first


PARK_TREES = _park_trees()


def draw_park_depth(canvas, frame):
    sky = skia.GradientShader.MakeLinear([skia.Point(0, 132), skia.Point(0, out.HORIZON)],
                                         [to_color((48, 51, 58)), to_color((92, 96, 104))])
    canvas.drawRect(skia.Rect(-400, -400, 2320, out.HORIZON + 2), skia.Paint(Shader=sky))
    canvas.drawRect(skia.Rect(-400, out.HORIZON, 2320, 1300), skia.Paint(Color=to_color((26, 27, 30))))
    hills = Ink(canvas, frame, color=(70, 74, 80), width=2.0, prefix="payoff.depth.hills")
    pts = [(x, out.HORIZON - 26 - 14 * math.sin(x * 0.006)) for x in np.arange(-400, 2400, 80)]
    hills.fill(pts + [(2400, out.HORIZON), (-400, out.HORIZON)], "fill", color=(36, 38, 44), wobble=0)
    path = Ink(canvas, frame, color=(110, 112, 118), width=3.0, prefix="payoff.depth.path")
    far = 30 * out.F
    pts = [project(-out.PATH_W, 0, 0.6 * out.F)[0], project(-out.PATH_W, 0, far)[0], project(out.PATH_W, 0, far)[0],
           project(out.PATH_W, 0, 0.6 * out.F)[0]]
    p = skia.Path()
    p.addPoly([skia.Point(*q) for q in pts], True)
    canvas.drawPath(p, skia.Paint(AntiAlias=True, Color=to_color((40, 41, 46))))
    for side in (-1, 1):
        path.line(project(side * out.PATH_W, 0, 0.6 * out.F)[0], project(side * out.PATH_W, 0, far)[0], f"edge{side}",
                  taper=0.9)
    for i, (x, z, height, r, seed) in enumerate(PARK_TREES):
        (bx, by), k = project(x, 0, z)
        (tx, ty), _ = project(x, height, z)
        ink = Ink(canvas, frame, color=ROOM, width=max(2.0, 22 * k), prefix=f"payoff.depth.tree{i}")
        ink.line((bx, by), (tx, ty), "trunk", taper=0.3)
        g = rng("payoff.depth.tree", seed)
        leaves = Ink(canvas, frame, color=(*LEAF_LINE, 210), width=max(1.2, 4 * k), prefix=f"payoff.depth.leaves{i}")
        for b in range(4):          # a round crown of a few blobs, close together
            (cx, cy), _ = project(x + g.uniform(-0.45, 0.45) * r, height + g.uniform(-0.15, 0.35) * r, z)
            leaves.circle((cx, cy), r * k * g.uniform(0.6, 0.8), f"blob{b}", fill=LEAF_GREEN)


def runner_joints(t, x, height, phase0):
    """A runner seen from behind, running away from us: joints in the world, and his depth."""
    s = t - AWAY
    d = RUN_SPEED * s
    z = START_Z + d
    phase = math.pi * d / (STRIDE * height / HEIGHT) + phase0
    leg, spine, head_r = 0.42 * height, 0.30 * height, 0.13 * height
    hip_y = 0.95 * leg + 0.03 * height * abs(math.sin(phase))
    A = 0.5 * STRIDE * height / HEIGHT
    j = {"hip": (x, hip_y, z), "neck": (x, hip_y + spine, z), "shoulder": (x, hip_y + spine - 0.06 * height, z),
         "head": (x, hip_y + spine + head_r, z)}
    sh = j["shoulder"]
    for name, side, sign in (("l", -1, 1), ("r", 1, -1)):
        along = sign * A * math.cos(phase)
        kick = 0.17 * height * max(0.0, sign * -math.sin(phase))              # the heel kicks up behind
        j["foot_" + name] = (x + side * 0.03 * height, kick, z + along)
        swing = -sign * math.cos(phase)                                          # arms against the legs
        j["elbow_" + name] = (x + side * 0.1 * height, sh[1] - 0.15 * height, z - 0.1 * height * swing)
        j["hand_" + name] = (x + side * 0.06 * height, sh[1] - 0.24 * height + 0.07 * height * max(0.0, swing),
                             z + 0.18 * height * swing)
    return j, head_r


def draw_runner_from_behind(canvas, frame, j, head_r, key, sam_hair=False):
    p = {name: project(*v) for name, v in j.items()}
    k = p["hip"][1]
    width = 7.0 * HEIGHT / 440 * k
    pen = Ink(canvas, frame, color=INK, width=width, prefix=key)
    bone = dict(pin_ends=True, taper=0.15)
    for side in ("_l", "_r"):
        pen.line(p["hip"][0], p["foot" + side][0], "leg" + side, width=width, **bone)
    pen.line(p["hip"][0], p["neck"][0], "spine", width=width, **bone)
    head, r = p["head"][0], head_r * p["head"][1]
    pen.circle(head, r, "head", fill=BG, width=width)
    if sam_hair:
        draw_sam_hair(canvas, frame, head, r, key + ".hair")
    for side in ("_l", "_r"):
        pen.line(p["shoulder"][0], p["elbow" + side][0], "upper" + side, width=width, **bone)
        pen.line(p["elbow" + side][0], p["hand" + side][0], "fore" + side, width=width, **bone)


away_camera = Camera(zoom=Track((AWAY, 1.0), (DURATION, 1.04, "linear")), handheld=lambda t: 0.8, name="payoff.away")


def shot_away(canvas, t, frame):
    with away_camera.view(canvas, t):
        draw_park_depth(canvas, frame)
        js, sr = runner_joints(t, 150, SAM_HEIGHT, 1.3)          # Sam on the right
        jh, hr = runner_joints(t, -150, HEIGHT, 0.0)
        draw_runner_from_behind(canvas, frame, js, sr, "payoff.sam.back", sam_hair=True)
        draw_runner_from_behind(canvas, frame, jh, hr, "payoff.hero.back")


# -- the scene ------------------------------------------------------------------------------------------


def draw(canvas, t, frame):
    if t < CLOSER:
        shot_street(canvas, t, frame)
    elif t < PARK:
        shot_closer(canvas, t, frame)
    elif t < AWAY:
        shot_park(canvas, t, frame)
    else:
        shot_away(canvas, t, frame)


bar = Discipline(start=19, fills=[LAST_STEP])     # the last step: full, and green


def overlay(canvas, t, frame):
    bar.draw(canvas, t, frame)


MUSIC = ("A warm, hopeful, cinematic piece for the end of a short film: a gentle solo piano melody that begins "
         "quietly and alone, then soft strings join and it slowly swells, uplifting but not triumphant, no drums, "
         "no vocals")


def soundtrack():
    mix = sk.Mix(DURATION)

    def effect(prompt, seconds, name):            # ElevenLabs effects, all brought to the same level first
        return sk.normalize(sk.eleven_sound(prompt, seconds, name))

    # the film's first music: quiet at first, swelling with the green (it carries on into the ending)
    music = sk.normalize(sk.eleven_music(MUSIC, 30, "payoff"))[:int(DURATION * sk.SR)]
    tt = np.arange(len(music)) / sk.SR
    level = np.interp(tt, [0, 2.0, PARK, GREENING[0], GREENING[1], DURATION], [0, 0.32, 0.45, 0.6, 1.0, 1.0])
    mix.add(music * level, at=0, gain_db=-8, reverb=0.1)
    # the rain, thinning away; birds once in the park
    rain = effect("Heavy steady rain against a bedroom window, heard from inside a quiet room, early morning, "
                  "no thunder", 12.0, "rain_window")[:int(PARK * sk.SR)]
    rain = rain * (1 - np.clip(np.arange(len(rain)) / (PARK * sk.SR), 0, 1)) ** 1.5
    mix.add(sk.fade_edges(rain, 0.05, 0.2), at=0, gain_db=-14, reverb=0.05)
    birds = effect("Birds singing gently in a city park just after the rain has stopped, early morning, a few "
                   "birds, no people", 12.0, "park_birds")
    mix.add(sk.fade_edges(birds[:int((DURATION - PARK) * sk.SR)], 1.5, 1.0), at=PARK, gain_db=-22, reverb=0.1)
    # their steps, from the side, then quieter as they run away from us
    for gait, offset, key, gain in ((him, 0.0, "payoff.him", -13), (sam_run, GO, "payoff.sam", -16)):
        for n, (tk, tl, foot, x, h) in enumerate(gait.steps):
            at = tk + offset
            if 0 <= at < AWAY:
                mix.add(sk.footstep(n, weight=0.5, key=key), at=at, gain_db=gain, reverb=0.1)
    n = 0
    for at in np.arange(AWAY, DURATION, STRIDE / RUN_SPEED):
        n += 1
        mix.add(sk.footstep(n, weight=0.45, key="payoff.away"), at=float(at), gain_db=-15 - 1.3 * n, reverb=0.15)
    bar.add_sounds(mix)
    return mix
