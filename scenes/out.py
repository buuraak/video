"""Film 1, row 29 of the story: out. About 9 seconds, three shots joined by hard cuts. It follows row 28, where
he stood with his hand on the handle, eyes closed, and took a long breath in.

 0-1.6 s    His face in profile, close (as row 28 ended): his eyes open, steady. No smile yet.
 1.6-6.0 s  From just behind him: he pushes the door open, and through it the grey, rainy morning: a path leading
            away between city buildings. The instant it opens the hum cuts dead, the rain rushes in loud and
            clear, the bar stops trembling and fills its 19th step. He walks out and away down the path.
 6.0-9.0 s  Outside, from the side, the street in the rain: he stands a moment, face turned up into it, breathing.

No caption. Sound: the hum and the muffled rain until the door opens; then the rain, clear, and the bar's ping.
"""
import math

import numpy as np
import skia

import scenes.too_fast as fast
from scenes.bedroom import ROOM, box, rounded_rect
from scenes.discipline import Discipline
from scenes.scroll import glow, light_on_face
from scenes.street import GROUND, draw_street
from scenes.the_quote import TINT
from toolkit import INK, Camera, Face, Ink, Track, draw_head, lerp, progress, to_color
from toolkit import sound as sk
from toolkit.rng import rng

PEAK_DB = -6.4          # set so the sounds sit at the same level as the sounds in the other scenes
BEHIND = 1.6            # cut to behind him
OPEN = (2.3, 3.1)       # he pushes the door open; the hum cuts as it opens
OPENS = OPEN[0] + 0.12  # the moment it opens: the latch gives
WALK_OUT = (3.3, 6.0)   # he walks out through the doorway and away down the path
OUTSIDE_SHOT = 6.0      # cut to outside
DURATION = 9.0

STEADY = Face(eyes=0.85, brows=-0.15, mouth="flat", mouth_size=0.5, bags=True)

# -- shot 1: his eyes open ---------------------------------------------------------------------------------

face_camera = Camera(zoom=Track((0, 1.06), (BEHIND, 1.08, "linear")), handheld=lambda t: 2.4, name="door.face")
HEAD, HEAD_R = (880, 512), 300          # as row 28 left him (his breath in has lifted his head a little)


def shot_face(canvas, t, frame):
    with face_camera.view(canvas, t):
        ink = Ink(canvas, frame, color=ROOM, width=8.0, prefix="door.face")
        ink.line((1500, 40), (1500, 1060), "door.edge", width=8.0)
        pen = Ink(canvas, frame, color=INK, width=22.0, prefix="hero.face.side")
        pen.line((HEAD[0] - 20, HEAD[1] + HEAD_R - 6), (HEAD[0] - 40, 1150), "neck", taper=0.0)
        eyes = lerp(0.0, STEADY.eyes, progress(t, 0.3, 0.8, "inout"))
        draw_head(pen, HEAD, HEAD_R, STEADY.but(eyes=eyes), tilt=-3, facing=1)
        glow(canvas, (-200, 560), 1200, TINT, 0.05)
        light_on_face(canvas, HEAD, HEAD_R, (-400, 560), TINT, 0.06)


# -- shot 2: from behind him, the door opens, and he walks out ----------------------------------------------
# Seen in true depth, from just behind him at his eye height: everything is placed in the world (X across, Y up
# from the floor, Z away from us) and drawn smaller the further away it is. Through the doorway: a path leading
# away between city buildings, in the grey, rainy morning. From behind, he is drawn without a face, and his legs
# are straight lines to his feet (seen from behind, a leg stepping forward just looks shorter).

VP_X, HORIZON = 960, 630        # straight ahead: where everything far away meets, at his eye height
F = 1500                        # how far away (in world pixels) something is drawn at its own size
HEIGHT = 980                    # his height, in world pixels
EYE = 0.85 * HEIGHT             # the camera's height: his eye level
LEG, SPINE, BACK_HEAD_R = 0.42 * HEIGHT, 0.30 * HEIGHT, 0.13 * HEIGHT
UPPER, FORE = 0.17 * HEIGHT, 0.16 * HEIGHT
LINE = 7.0 * HEIGHT / 440       # his pen width, at his own size
DOOR_Z = 1.0 * F                # the door's distance: close, it fills the picture
DOOR_W, DOOR_H = 530, 1.2 * HEIGHT
DOOR_X0 = -DOOR_W / 2           # its hinges (left)
HANDLE_X, HANDLE_Y = DOOR_W / 2 - 50, 0.47 * DOOR_H
START_Z = 0.93 * F              # where he stands, just in front of the door
START_X = -40
SPEED = 1.5 / 1.8 * HEIGHT      # an easy walk: 1.5 metres a second
STEP = 0.39 * HEIGHT            # one step: 0.7 metres
OUTSIDE_GREY = (168, 172, 180)  # the grey light from outside


def project(x, y, z):
    """Where a point in the world appears in the picture, and how big things are drawn there."""
    k = F / z
    return (VP_X + x * k, HORIZON + (EYE - y) * k), k


behind_camera = Camera(zoom=Track((BEHIND, 1.0), (OUTSIDE_SHOT, 1.03, "linear")),
                       handheld=lambda t: 1.6 - 0.8 * progress(t, *OPEN), name="out.behind")


def door_open(t):
    return progress(t, *OPEN, "inout")


def doorway_light(t):
    return progress(t, OPENS - 0.05, OPEN[1], "out")


def draw_rain(canvas, t, area, key, count=160, alpha=80, length=46):
    """Rain falling in an area (x0, y0, x1, y1): thin streaks, slanting a little."""
    x0, y0, x1, y1 = area
    paint = skia.Paint(AntiAlias=True, Color=to_color((185, 190, 200, alpha)), StrokeWidth=2.0)
    g = rng("out.rain", key)
    for _ in range(count):
        rx, phase, speed = g.uniform(x0, x1 + 60), g.uniform(0, 1), g.uniform(1300, 1700)
        y = y0 - length + ((t * speed / (y1 - y0 + length) + phase) % 1.0) * (y1 - y0 + length)
        canvas.drawLine(rx, y, rx - 8, y + length, paint)


def doorway():
    """The door opening in the picture: (x0, y0, x1, y1)."""
    (x0, y1), _ = project(DOOR_X0, 0, DOOR_Z)
    (x1, y0), _ = project(DOOR_X0 + DOOR_W, DOOR_H, DOOR_Z)
    return x0, y0, x1, y1


# The city outside, in the world: buildings along both sides of the path, and more across the far end.
PATH_W = 420                    # half the path's width
SIDE_X = 760                    # where the buildings along the path stand


def _side_buildings():
    out, g = [], rng("out.city")
    for side in (-1, 1):
        z = 2.1 * F
        while z < 16 * F:
            depth, height = g.uniform(1.2, 2.6) * F, g.uniform(1.8, 4.0) * HEIGHT
            out.append((side, z, z + depth, height))
            z += depth + g.uniform(0.05, 0.3) * F
    return out


SIDE_BUILDINGS = _side_buildings()
FAR_BUILDINGS = [(x, g_w, g_h) for x, g_w, g_h in
                 ((-2600, 900, 3.6), (-1700, 700, 2.4), (-950, 800, 4.4), (-200, 600, 3.0), (380, 900, 3.9),
                  (1250, 700, 2.7), (1900, 1000, 3.4))]
FAR_Z = 17 * F


def quad(canvas, pts, colour):
    path = skia.Path()
    path.addPoly([skia.Point(*q) for q in pts], True)
    canvas.drawPath(path, skia.Paint(AntiAlias=True, Color=to_color(colour)))


def draw_city(canvas, frame, t):
    """What's outside the door: the sky, the city, the path leading away, a streetlamp, the rain."""
    x0, y0, x1, y1 = doorway()
    sky = skia.GradientShader.MakeLinear([skia.Point(0, y0), skia.Point(0, HORIZON)],
                                         [to_color((58, 61, 69)), to_color((92, 96, 105))])
    canvas.drawRect(skia.Rect(x0, y0, x1, HORIZON + 2), skia.Paint(Shader=sky))
    canvas.drawRect(skia.Rect(x0, HORIZON, x1, y1), skia.Paint(Color=to_color((30, 31, 35))))
    far_ink = Ink(canvas, frame, color=(96, 98, 106), width=1.6, prefix="out.city.far")
    for i, (x, w, h) in enumerate(FAR_BUILDINGS):                  # across the far end
        (a, b), _ = project(x, h * HEIGHT, FAR_Z)
        (c, d), _ = project(x + w, 0, FAR_Z)
        corners = [(a, d), (a, b), (c, b), (c, d)]
        quad(canvas, corners, (40, 42, 48))
        far_ink.stroke(corners, f"far{i}", closed=True)
    near_ink = Ink(canvas, frame, color=(104, 106, 112), width=2.2, prefix="out.city.near")
    for i, (side, za, zb, h) in sorted(enumerate(SIDE_BUILDINGS), key=lambda e: -e[1][1]):   # far ones first
        x = side * SIDE_X
        corners = [project(x, 0, za)[0], project(x, h, za)[0], project(x, h, zb)[0], project(x, 0, zb)[0]]
        quad(canvas, corners, (36, 38, 44))
        near_ink.stroke(corners, f"side{i}", closed=True, width=2.2 * F / za)
        g = rng("out.windows", i)
        for wz in np.arange(za + 0.25 * F, zb - 0.3 * F, 0.55 * F):     # windows along the facade
            for wy in np.arange(0.5 * HEIGHT, h - 0.3 * HEIGHT, 0.7 * HEIGHT):
                pts = [project(x, wy, wz)[0], project(x, wy + 0.32 * HEIGHT, wz)[0],
                       project(x, wy + 0.32 * HEIGHT, wz + 0.22 * F)[0], project(x, wy, wz + 0.22 * F)[0]]
                quad(canvas, pts, (74, 77, 86) if g.random() < 0.1 else (26, 27, 32))
    # the path: its edges running away to the far end, the paving joints across it, faint
    path_ink = Ink(canvas, frame, color=(110, 112, 118), width=3.0, prefix="out.path")
    quad(canvas, [project(-PATH_W, 0, DOOR_Z)[0], project(-PATH_W, 0, FAR_Z)[0], project(PATH_W, 0, FAR_Z)[0],
                  project(PATH_W, 0, DOOR_Z)[0]], (40, 41, 46))
    for side in (-1, 1):
        path_ink.line(project(side * PATH_W, 0, DOOR_Z)[0], project(side * PATH_W, 0, FAR_Z)[0], f"edge{side}",
                      taper=0.9)
    for k, z in enumerate(np.arange(DOOR_Z + 0.45 * F, 9 * F, 0.45 * F)):
        path_ink.line(project(-PATH_W, 0, z)[0], project(PATH_W, 0, z)[0], f"joint{k}", width=2.4 * F / z,
                      color=(80, 82, 88))
    for k, lz in enumerate((3.2 * F, 7.5 * F)):                    # streetlamps by the path, on the right
        (bx, by), sc = project(PATH_W + 120, 0, lz)
        (tx, ty), _ = project(PATH_W + 120, 2.3 * HEIGHT, lz)
        path_ink.line((bx, by), (tx, ty), f"lamp{k}", width=max(1.5, 5 * sc))
        glow(canvas, (tx, ty), 160 * sc, (200, 204, 212), 0.45)
    draw_rain(canvas, t, (x0, y0, x1, y1), "doorway", count=120, alpha=70)


def draw_doorway(canvas, frame, t):
    """The doorway (the city outside once the door opens), its frame, and the door swinging away. Returns
    where the handle is in the world."""
    x0, y0, x1, y1 = doorway()
    light = doorway_light(t)
    if light > 0:
        canvas.save()
        canvas.clipRect(skia.Rect(x0, y0, x1, y1))
        canvas.saveLayerAlpha(None, int(255 * light))
        draw_city(canvas, frame, t)
        canvas.restore()
        canvas.restore()
        glow(canvas, ((x0 + x1) / 2, (y0 + y1) / 2), 1100, OUTSIDE_GREY, 0.1 * light)   # its light in the room
    room = Ink(canvas, frame, color=ROOM, width=6.0, prefix="out.door")
    room.stroke([(x0 - 26, 1200), (x0 - 26, y0 - 26), (x1 + 26, y0 - 26), (x1 + 26, 1200)], "frame", width=7.0)
    # the door, swinging away from us on its hinges (left)
    a = door_open(t) * math.radians(80)
    edge_x, edge_z = DOOR_X0 + DOOR_W * math.cos(a), DOOR_Z + DOOR_W * math.sin(a)
    leaf = [project(DOOR_X0, 0, DOOR_Z)[0], project(DOOR_X0, DOOR_H, DOOR_Z)[0], project(edge_x, DOOR_H, edge_z)[0],
            project(edge_x, 0, edge_z)[0]]
    room.fill(leaf, "leaf.fill", color=(20, 20, 24), wobble=0)
    room.stroke(leaf, "leaf", closed=True, width=5.0)
    r = HANDLE_X - DOOR_X0
    handle = (DOOR_X0 + r * math.cos(a), HANDLE_Y, DOOR_Z + r * math.sin(a) - 30)    # it sticks out toward us
    lever_end = (handle[0] - 70 * math.cos(a), HANDLE_Y, handle[2] - 70 * math.sin(a))
    (hx, hy), k = project(*handle)
    room.circle((hx, hy), 13 * k, "knob", width=4.0)
    room.line((hx, hy), project(*lever_end)[0], "lever", width=8.0 * k)
    return handle


def walked(t):
    """How far he has walked from the door (world pixels), speeding up from standing over his first step."""
    s = max(0.0, t - WALK_OUT[0])
    ramp = 0.45
    return SPEED * (s * s / (2 * ramp) if s < ramp else s - ramp / 2)


def his_joints(t, handle):
    """His joints in the world, walking away from us (Z grows), and how much he is in his stride."""
    d = walked(t)
    moving = min(1.0, d / (0.5 * STEP)) if d > 0 else 0.0
    z = START_Z + d
    phase = math.pi * d / STEP                          # each step is half a cycle
    x = START_X + 6 * math.sin(phase) * moving          # a little sway over each foot
    hip_y = 0.985 * LEG - 10 * abs(math.sin(phase)) * moving
    A = STEP / 2 * moving
    j = {"hip": (x, hip_y, z)}
    j["neck"] = (x, hip_y + SPINE, z)
    j["shoulder"] = (x, hip_y + SPINE - 0.06 * HEIGHT, z)
    j["head"] = (x, hip_y + SPINE + BACK_HEAD_R, z)
    for name, side, sign in (("l", -1, 1), ("r", 1, -1)):
        along = sign * A * math.cos(phase)                                  # forward (+) or back of his hips
        lift = 0.06 * HEIGHT * max(0.0, sign * -math.sin(phase)) * moving   # the foot swinging forward lifts
        j["foot_" + name] = (x + side * 32, lift, z + along)
        swing = -sign * 0.5 * A * math.cos(phase)                           # arms swing against the legs
        hang = (x + side * 0.1 * HEIGHT, j["shoulder"][1] - 0.97 * (UPPER + FORE) + 12 * abs(swing) / max(A, 1), z + swing)
        j["hand_" + name] = hang
    # at the door: his right hand on the handle, pushing it as the door opens, then letting go
    reach_ = progress(t, BEHIND - 0.5, OPEN[0], "inout") * (1 - progress(t, OPEN[1] - 0.1, OPEN[1] + 0.4, "inout"))
    if reach_ > 0:
        j["hand_r"] = tuple(lerp(j["hand_r"], handle, reach_))
    for name, side in (("l", -1), ("r", 1)):            # elbows: halfway down the arm, a little out to the side
        sh, hand = j["shoulder"], j["hand_" + name]
        j["elbow_" + name] = ((sh[0] + hand[0]) / 2 + side * 18, (sh[1] + hand[1]) / 2, (sh[2] + hand[2]) / 2)
    return j


def draw_him_from_behind(canvas, frame, t, handle):
    j = his_joints(t, handle)
    p = {k: project(*v) for k, v in j.items()}
    k_body = p["hip"][1]
    beyond = j["hip"][2] > DOOR_Z                      # through the door: the wall hides anything outside it
    canvas.save()
    if beyond:
        x0, y0, x1, y1 = doorway()
        canvas.clipRect(skia.Rect(x0, y0, x1, y1))
    pen = Ink(canvas, frame, color=INK, width=LINE * k_body, prefix="hero.back")
    bone = dict(pin_ends=True, taper=0.15)
    for side in ("_l", "_r"):                          # legs: straight to the feet
        pen.line(p["hip"][0], p["foot" + side][0], "leg" + side, width=LINE * k_body, **bone)
    pen.line(p["hip"][0], p["neck"][0], "spine", width=LINE * k_body, **bone)
    pen.circle(p["head"][0], BACK_HEAD_R * p["head"][1], "head", fill=(14, 14, 17), width=LINE * k_body)
    for side in ("_l", "_r"):
        pen.line(p["shoulder"][0], p["elbow" + side][0], "upper_arm" + side, width=LINE * k_body, **bone)
        pen.line(p["elbow" + side][0], p["hand" + side][0], "forearm" + side, width=LINE * k_body, **bone)
    canvas.restore()


def shot_behind(canvas, t, frame):
    with behind_camera.view(canvas, t):
        handle = draw_doorway(canvas, frame, t)
        draw_him_from_behind(canvas, frame, t, handle)


# -- shot 3: outside, in the rain -----------------------------------------------------------------------------

STAND_X = 960
outside_camera = Camera(x=STAND_X + 40, y=Track((OUTSIDE_SHOT, 600), (DURATION, 590, "linear")),
                        zoom=Track((OUTSIDE_SHOT, 1.3), (DURATION, 1.38, "linear")), name="out.outside")
UP = (OUTSIDE_SHOT + 0.3, OUTSIDE_SHOT + 1.3)      # he turns his face up into the rain


def shot_outside(canvas, t, frame):
    with outside_camera.view(canvas, t):
        draw_street(canvas, frame, view=(STAND_X - 1100, STAND_X + 1100))
        canvas.drawPaint(skia.Paint(Color=to_color((10, 12, 16, 70))))      # darker: the rain
        breath = math.sin(2 * math.pi * (t - OUTSIDE_SHOT) / 3.2)
        up = progress(t, *UP, "inout")
        face = STEADY.but(eyes=lerp(0.85, 0.15, up), brows=lerp(-0.15, 0.2, up))
        pose = fast.hero.stand(STAND_X, GROUND, facing=1, face=face, head_tilt=-26 * up, lean=-2 * up)
        fast.hero.draw(canvas, frame, pose.but(y=pose.y + 1.0 + breath))
        draw_rain(canvas, t, (STAND_X - 1100, -100, STAND_X + 1100, GROUND + 40), "street", count=320, alpha=70)


# -- the scene ------------------------------------------------------------------------------------------


def draw(canvas, t, frame):
    if t < BEHIND:
        shot_face(canvas, t, frame)
    elif t < OUTSIDE_SHOT:
        shot_behind(canvas, t, frame)
    else:
        shot_outside(canvas, t, frame)


bar = Discipline(start=18, fills=[OPENS], shakes=[(-1.0, OPENS + 0.3)])   # +1 as the door opens; still at last


def overlay(canvas, t, frame):
    bar.draw(canvas, t, frame)


def soundtrack():
    mix = sk.Mix(DURATION)

    def effect(prompt, seconds, name):            # ElevenLabs effects, all brought to the same level first
        return sk.normalize(sk.eleven_sound(prompt, seconds, name))

    # the hum, on from row 28, cut dead as the door opens
    hum = sk.pad(["A1", "E2"], OPENS + 0.5, attack=0.05, release=0.01, brightness=0.05, key="hum")
    hum = sk.fade_edges(hum[:, :int(OPENS * sk.SR)], 0.0, 0.03)
    mix.add(hum, at=0, gain_db=-19, reverb=0.05)
    # the rain: muffled behind the door, then clear and loud the moment it opens
    rain = effect("Heavy steady rain against a bedroom window, heard from inside a quiet room, early morning, "
                  "no thunder", 12.0, "rain_window")
    rain = rain[:int(DURATION * sk.SR)]
    muffled = sk.lowpass(rain, 1400)
    k = int(OPENS * sk.SR)
    blend = np.clip((np.arange(len(rain)) - k) / (0.15 * sk.SR), 0, 1)
    clear = muffled * (1 - blend) * 10 ** (-0 / 20) + rain * blend * 10 ** (6 / 20)
    mix.add(sk.fade_edges(clear, 0.05, 0.3), at=0, gain_db=-16, reverb=0.05)
    door = effect("A door handle pressed down and an apartment door pushed open quickly, the latch clicking, "
                  "close up", 1.2, "door_open")
    latch = int(0.45 * sk.SR)
    mix.add(sk.fade_edges(door[latch:], 0.005, 0.1), at=OPEN[0], gain_db=-10, reverb=0.12)
    # his steps, walking away (a foot lands every STEP he walks), quieter as he goes
    n, t = 1, WALK_OUT[0]
    while t < OUTSIDE_SHOT:
        if walked(t) >= (n - 0.5) * STEP:
            mix.add(sk.footstep(n, weight=0.5, key="out.steps"), at=t, gain_db=-13 - 2.5 * n, reverb=0.15)
            n += 1
        t += 0.005
    bar.add_sounds(mix)
    return mix
