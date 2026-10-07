"""Film 1, scene 2: scrolling. About 17 seconds, one shot from straight above that never moves.

 0-1 s    Hard cut back to the wide view of scene 1's start. He lies awake on the nightstand side
          of the bed, hands on his belly, tired. 6:00.
 1-3 s    His arm reaches over, takes the phone off the nightstand (unplugging it), and he holds
          it up over his chest. We see the back of the phone; its cold light comes on.
 3-8 s    Reels: three swipes. The light on his face flickers and changes with each one, and the
          muffled sound of each clip (someone mumbling, sometimes music) cuts and changes with it.
 8-9 s    He drops the phone on the empty half of the bed. It keeps playing, screen up.
 9-14 s   He throws the blanket toward the nightstand, sits up (his face turns away from us),
          shuffles across the empty half, swings his legs out to the right and stands up.
14-17 s   He walks out the right edge, seen from above: the top of his head, arms and feet
          poking out. The empty bed and the glowing phone stay behind.
"""
import math

import numpy as np
import skia

from scenes.bedroom import (HERO_X, HIP_Y, PHONE, PHONE_TURN, ROOM, belly_hands, box, draw_bed, draw_blanket,
                            draw_nightstand, hero, rounded_rect, turned)
from toolkit import BG, SCREEN, Camera, Face, Ink, Pose, blink, clamp, draw_face, lerp, progress, to_color
from toolkit import sound as sk
from toolkit.rng import noise

DURATION = 17.0
PEAK_DB = -3.5         # keeps the hum exactly as loud as in scene 1 (this scene's loudest sound is quieter)
REACH = 1.0            # he starts reaching for the phone
GRAB = 2.0             # his hand is on it
UNPLUG = 2.1           # he pulls it off the charger
WAKE = 2.75            # the screen comes on
HOLD = 3.0             # phone up over his chest, the first reel plays
SWIPES = (4.4, 5.6, 6.9)
PUT_DOWN = 8.0         # he takes it to the side...
DROP = 8.55            # ...lets go of it...
LAND = 8.67            # ...and it lands on the empty half of the bed, screen up
THROW = 9.2            # he throws the blanket back
SIT = 9.9              # he sits up
SCOOT = 10.9           # he shuffles across the empty half of the bed
SWING = 12.0           # he swings his legs out to the right
STAND = 12.9           # he stands up beside the bed
WALK = 14.0            # he walks out to the right

camera = Camera(name="scroll")       # holds its position: only the gentle handheld wobble

CHEST = (HERO_X, 494)                # where he holds the phone, over his chest
BESIDE = (1082, 342)                 # where it lands: on the empty half of the bed, beside the pillow
GRIP = turned([(PHONE[0] + 56, PHONE[1] + 16)], PHONE, PHONE_TURN)[0]  # the phone's corner nearest him
GRIP_OFFSET = (GRIP[0] - PHONE[0], GRIP[1] - PHONE[1])

# -- the phone's light ---------------------------------------------------------------

# Each reel has its own brightness and a slightly different cold tint.
REELS = [(HOLD, 0.9, (178, 208, 255)), (4.4, 0.62, (160, 192, 255)), (5.6, 1.0, (205, 224, 255)),
         (6.9, 0.8, (178, 208, 255))]


def reel_at(t):
    i = max(k for k, r in enumerate(REELS) if r[0] <= t) if t >= HOLD else 0
    return i, REELS[i]


def light_level(t):
    """How bright the phone's light is (0..1), and its colour."""
    if t < WAKE:
        return 0.0, SCREEN
    i, (start, level, tint) = reel_at(t)
    level *= 1 + 0.12 * noise(t * 5, "reel", i)                 # the video itself flickers
    for s in SWIPES:                                            # a swipe: a quick dip between videos
        if s - 0.06 <= t < s + 0.16:
            level *= 0.35 + 0.65 * progress(t, s + 0.02, s + 0.16, "out")
    return level * progress(t, WAKE, WAKE + 0.2, "out"), tint


def glow(canvas, center, radius, tint, alpha):
    """Soft light falling around a point (adds light, never darkens)."""
    if alpha <= 0.003:
        return
    shader = skia.GradientShader.MakeRadial(
        skia.Point(*center), radius,
        [to_color((*tint, int(255 * clamp(alpha)))), to_color((*tint, int(255 * clamp(alpha) * 0.35))),
         to_color((*tint, 0))], [0.0, 0.45, 1.0])
    canvas.drawCircle(center[0], center[1], radius, skia.Paint(AntiAlias=True, Shader=shader,
                                                               BlendMode=skia.BlendMode.kScreen))


def light_on_face(canvas, head, r, source, tint, alpha):
    """The side of his face nearest the phone lights up most."""
    if alpha <= 0.003:
        return
    dx, dy = source[0] - head[0], source[1] - head[1]
    d = math.hypot(dx, dy) or 1.0
    near = (head[0] + dx / d * r, head[1] + dy / d * r)
    far = (head[0] - dx / d * r, head[1] - dy / d * r)
    shader = skia.GradientShader.MakeLinear(
        [skia.Point(*near), skia.Point(*far)],
        [to_color((*tint, int(255 * clamp(alpha)))), to_color((*tint, int(255 * clamp(alpha) * 0.2)))])
    canvas.save()
    canvas.clipPath(skia.Path().addCircle(head[0], head[1], r - 2), doAntiAlias=True)
    canvas.drawPaint(skia.Paint(AntiAlias=True, Shader=shader, BlendMode=skia.BlendMode.kScreen))
    canvas.restore()


# -- the phone -----------------------------------------------------------------------


def phone_shape(center, length, width, angle, r=9):
    """A phone-shaped rounded box; angle 0 means its top points up the screen."""
    x, y = center
    return turned(rounded_rect(x - width / 2, y - length / 2, x + width / 2, y + length / 2, r), center, angle)


def draw_phone(canvas, ink, center, length, width, angle, look, level=0.0, tint=SCREEN):
    """look: "dark" (screen up, off), "back" (held up, screen facing him) or "lit" (screen up, playing)."""
    if width < 2:
        return
    body = phone_shape(center, length, width, angle)
    if look == "back":
        # light leaking out around the edges, from the screen facing him
        path = skia.Path()
        path.addPoly([skia.Point(*p) for p in body], True)
        canvas.drawPath(path, skia.Paint(AntiAlias=True, Color=to_color((*tint, int(200 * level))),
                                         MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 9)))
        box(ink, body, "phone", width=3.2, fill=(26, 26, 30))
        # the camera bump, near the top corner
        cam = (center[0] - width * 0.22, center[1] - length * 0.3)
        box(ink, phone_shape(turned([cam], center, angle)[0], length * 0.24, width * 0.34, angle, r=5),
            "phone.camera", width=2.2, fill=(26, 26, 30))
        return
    if look == "lit":
        glow(canvas, center, 120, tint, 0.55 * level)
    box(ink, body, "phone", width=3.2)
    screen = phone_shape(center, length * 0.86, width * 0.8, angle, r=5)
    if look == "lit":
        ink.fill(screen, "phone.light", color=(*tint, int(235 * clamp(0.35 + 0.65 * level))), wobble=0)
    ink.stroke(screen, "phone.screen", closed=True, width=1.8)


def phone_state(t):
    """Where the phone is: (center, length, width, angle, look), or None while it's on the nightstand."""
    if t < UNPLUG:
        return None
    if t < HOLD:      # off the nightstand, turned over, up to his chest
        u = progress(t, UNPLUG, HOLD)
        flip = progress(t, 2.35, 2.65, "linear")             # turned over: narrows, then widens again
        width = lerp(60, 62, u) * abs(math.cos(math.pi * flip))
        center = lerp(lerp(PHONE, (790, 500), u), lerp((790, 500), CHEST, u), u)
        return (center, lerp(120, 86, u), width, lerp(PHONE_TURN - 90, 0, u),
                "dark" if flip < 0.5 else "back")
    if t < PUT_DOWN:  # held up, jolting slightly with each swipe
        return ((CHEST[0], CHEST[1] - 3 * swipe(t)), 86, 62, 0, "back")
    if t < DROP:      # taken over beside his head, and turned screen up
        u = progress(t, PUT_DOWN, DROP)
        flip = progress(t, PUT_DOWN + 0.22, PUT_DOWN + 0.42, "linear")
        width = lerp(62, 58, u) * abs(math.cos(math.pi * flip))
        return (lerp(CHEST, (BESIDE[0] - 4, BESIDE[1] + 6), u), lerp(86, 112, u), width,
                lerp(0, 8, u), "back" if flip < 0.5 else "lit")
    # dropped: falls the last bit (a touch bigger while it's nearer us), lands, then lies there playing
    fall = progress(t, DROP, LAND, "in")
    size = 1.0 + 0.05 * (1 - fall)
    center = lerp((BESIDE[0] - 4, BESIDE[1] + 6), BESIDE, fall)
    return (center, 112 * size, 58 * size, 8, "lit")


def swipe(t):
    """0..1: his thumb flicking up the screen, a moment around each swipe."""
    for s in SWIPES:
        if s - 0.09 <= t < s + 0.2:
            return progress(t, s - 0.09, s, "out") * (1 - progress(t, s, s + 0.2, "inout"))
    return 0.0


# -- him, lying down: where his hands and head go -------------------------------------

# While he holds the phone up, his elbows rest on the bed beside him and his forearms point
# up at us (so they look short from above).
HOLD_ELBOWS = {"elbow_l": (HERO_X - 82, 508), "elbow_r": (HERO_X + 82, 508)}


def holding(t):
    """How much each elbow is in its phone-holding place (0..1)."""
    left = progress(t, UNPLUG + 0.3, HOLD) * (1 - progress(t, PUT_DOWN, PUT_DOWN + 0.4))
    right = progress(t, 2.55, HOLD) * (1 - progress(t, PUT_DOWN, PUT_DOWN + 0.3))
    return {"elbow_l": left, "elbow_r": right}



def lying_pose(t):
    """His pose while lying in bed (up to the moment he sits up)."""
    breath = 0.35 * math.sin(2 * math.pi * t / 4.2) * (1 - progress(t, THROW, SIT))
    pose = Pose(x=HERO_X, y=HIP_Y - 3 * breath)          # he lies near enough: only his arm moves
    left, right = belly_hands(hero.joints(pose)["shoulder"], max(breath, 0))
    phone = phone_state(t)

    # his left hand: reaches for the phone, then holds it until he takes it to the side
    if t < GRAB:
        left = path_through(t, [(REACH, left), (REACH + 0.5, (748, 530)), (GRAB, GRIP)])
    elif t < UNPLUG:
        left = GRIP
    elif t < PUT_DOWN:
        u = progress(t, UNPLUG, HOLD)
        c = phone[0]
        left = lerp((c[0] + GRIP_OFFSET[0], c[1] + GRIP_OFFSET[1]), (c[0] - 29, c[1]), u)
    else:
        u = progress(t, PUT_DOWN, PUT_DOWN + 0.5)
        left = lerp((CHEST[0] - 29, CHEST[1]), left, u)

    # his right hand: joins on the phone, swipes, takes it to the side, then throws off the blanket
    if t < 2.55:
        pass
    elif t < PUT_DOWN:
        c = phone[0]
        held = (c[0] + 29, c[1] - 16 * swipe(t))
        right = lerp(right, held, progress(t, 2.55, HOLD))
    elif t < DROP:
        c = phone[0]
        right = (c[0] - 4, c[1] + 44 * progress(t, PUT_DOWN, DROP))
    elif t < THROW:
        right = lerp((BESIDE[0] - 8, BESIDE[1] + 50), right, progress(t, DROP, DROP + 0.5))
    else:   # grabs the blanket on the empty side and throws it over toward the nightstand
        right = path_through(t, [(THROW, right), (THROW + 0.22, (1090, 488)), (THROW + 0.6, (790, 515)),
                                 (SIT, (840, 545))])

    # where he looks: at the nightstand while reaching, then down at the phone
    look_side = -0.45 * progress(t, REACH, GRAB) * (1 - progress(t, UNPLUG, 2.7))
    look_down = 0.12 * progress(t, UNPLUG, HOLD) * (1 - progress(t, PUT_DOWN, PUT_DOWN + 0.4))
    # elbows bend down toward the bed, never up across his face
    pose = pose.but(hand_l=left, hand_r=right, bend_hand_r=1 if PUT_DOWN <= t < THROW else None)
    return pose, breath, look_side, look_down


def path_through(t, keys):
    """Ease through a list of (time, point) keys."""
    for (t0, p0), (t1, p1) in zip(keys[:-1], keys[1:]):
        if t < t1:
            return lerp(p0, p1, progress(t, t0, t1))
    return keys[-1][1]


# -- him, getting up: drawn truly from above ---------------------------------------------

STAND_AT = (1325, 606)                # where he stands, beside the bed on the right
STRIDE = 150                          # pixels per step
SPEED = 300                           # pixels per second once walking


def _offsets_sitting(shin):
    """Sitting up in bed facing the foot of the bed, relative to his hips. shin: how much of the
    shins we see (1 = lying along the bed, 0 = hanging straight down off its edge)."""
    return {"neck": (0, 8), "shoulder": (0, 10), "head": (0, 14),
            "elbow_l": (-58, -6), "hand_l": (-100, -20), "elbow_r": (58, -6), "hand_r": (100, -20),
            "knee_l": (-24, 125), "foot_l": (-24 - 10 * shin, 125 + 120 * shin + 12 * (1 - shin)),
            "knee_r": (24, 125), "foot_r": (24 + 10 * shin, 125 + 120 * shin + 12 * (1 - shin))}


def _rotated(offsets, hip, degrees):
    c, s = math.cos(math.radians(degrees)), math.sin(math.radians(degrees))
    j = {k: (hip[0] + x * c - y * s, hip[1] + x * s + y * c) for k, (x, y) in offsets.items()}
    j["hip"] = hip
    return j


def _blend(a, b, u):
    return {k: lerp(a[k], b[k], u) for k in a}


def walking(t):
    """Joints while standing and walking right, seen from above: (joints, head size)."""
    if t < WALK:
        dist = 0.0
    else:
        ramp = 0.5
        dt = t - WALK
        dist = SPEED * (dt * dt / (2 * ramp) if dt < ramp else dt - ramp / 2)
    phi = math.pi * dist / STRIDE
    step, sway = math.sin(phi), math.sin(phi) * min(dist / 40, 1)
    hip = (STAND_AT[0] + dist, STAND_AT[1] + 5 * sway)
    r = hero.head_r * 1.15 * (1 + 0.015 * math.cos(2 * phi) * min(dist / 40, 1))
    lean = 26 * min(dist / 60, 1)              # walking, his head goes ahead of his hips
    swing, stride = 72 * step, 140 * step
    side = r + 34
    head = (hip[0] + 10 + lean, hip[1])
    j = {"hip": hip, "neck": (head[0] - 4, hip[1]), "shoulder": (head[0] - 2, hip[1]), "head": head,
         "elbow_l": (head[0] - 6 - swing * 0.35, hip[1] + r + 4), "hand_l": (head[0] - 14 - swing, hip[1] + side),
         "elbow_r": (head[0] - 6 + swing * 0.35, hip[1] - r - 4), "hand_r": (head[0] - 14 + swing, hip[1] - side),
         # the feet step around his hips, behind his head: the back foot shows most
         "foot_l": (hip[0] - 10 + stride, hip[1] + 22), "knee_l": (hip[0] - 4 + stride * 0.55, hip[1] + 20),
         "foot_r": (hip[0] - 10 - stride, hip[1] - 22), "knee_r": (hip[0] - 4 - stride * 0.55, hip[1] - 20)}
    return j, r


def getting_up(t, lying_end):
    """Joints from sitting up to walking away: (joints, head size, how far his face has turned away)."""
    hip0 = lying_end["hip"]
    sit = _rotated(_offsets_sitting(1.0), (HERO_X, 600), 0)
    if t < SCOOT:     # sitting up: the body rises toward us, so his head slides down over his hips
        u = progress(t, SIT, SCOOT - 0.1)
        a = math.radians(90 * u)
        j = {}
        for k in lying_end:
            if k in ("neck", "shoulder", "head"):
                lie = (lying_end[k][0] - hip0[0], lying_end[k][1] - hip0[1])
                up = (sit[k][0] - sit["hip"][0], sit[k][1] - sit["hip"][1])
                hip = lerp(hip0, sit["hip"], u)
                j[k] = (hip[0] + lie[0] * math.cos(a) + up[0] * math.sin(a),
                        hip[1] + lie[1] * math.cos(a) + up[1] * math.sin(a))
            else:
                j[k] = lerp(lying_end[k], sit[k], u)
        return j, hero.head_r * lerp(1.0, 1.1, u), progress(t, SIT, SIT + 0.75)
    if t < SWING:     # shuffling across the empty half of the bed, two pushes
        x = HERO_X + 90 * progress(t, SCOOT + 0.05, SCOOT + 0.45) + 90 * progress(t, SCOOT + 0.55, SCOOT + 0.95)
        return _rotated(_offsets_sitting(1.0), (x, 600), 0), hero.head_r * 1.1, 1.0
    if t < STAND:     # swinging round to sit on the right edge, legs over the side
        u = progress(t, SWING, STAND - 0.05)
        shin = 1 - progress(u, 0.35, 0.85)
        hip = lerp((HERO_X + 180, 600), (1180, 602), u)
        return _rotated(_offsets_sitting(shin), hip, -90 * u), hero.head_r * 1.1, 1.0
    edge = _rotated(_offsets_sitting(0.0), (1180, 602), -90)
    stand, r = walking(t)
    u = progress(t, STAND, STAND + 0.85)
    return _blend(edge, stand, u), lerp(hero.head_r * 1.1, r, u), 1.0


# -- drawing him ----------------------------------------------------------------------

BONE = dict(pin_ends=True, taper=0.15)


def draw_body(canvas, frame, j, parts, head_r):
    """Draw parts of him from his joint positions, with the same strokes as Character.draw."""
    pen = Ink(canvas, frame, color=hero.color, width=hero.line_width, prefix=hero.name)
    for part in parts:
        if part == "legs":
            for side in ("_l", "_r"):
                pen.line(j["hip"], j["knee" + side], "thigh" + side, **BONE)
                pen.line(j["knee" + side], j["foot" + side], "shin" + side, **BONE)
        elif part == "spine":
            pen.line(j["hip"], j["neck"], "spine", **BONE)
        elif part == "head":
            pen.circle(j["head"], head_r, "head", fill=BG)
        elif part == "arms":
            for side in ("_l", "_r"):
                pen.line(j["shoulder"], j["elbow" + side], "upper_arm" + side, **BONE)
                pen.line(j["elbow" + side], j["hand" + side], "forearm" + side, **BONE)
    return pen


def draw_his_face(canvas, pen, head, r, face, tilt, look_side, away):
    """His face; `away` 0..1 turns it away from us (toward his feet) as he sits up."""
    if away >= 0.97:
        return
    canvas.save()
    canvas.clipPath(skia.Path().addCircle(head[0], head[1], r - pen.width * 0.6), doAntiAlias=True)
    canvas.translate(head[0], head[1] + 0.95 * r * away)
    canvas.scale(1.0, 1.0 - away)
    canvas.translate(-head[0], -head[1])
    draw_face(pen, head, r, face, tilt=tilt, facing=look_side)
    canvas.restore()


# -- the scene ---------------------------------------------------------------------------

_lying_end = None


def lying_end():
    """His joints at the moment he starts to sit up (where the sitting-up move starts from)."""
    global _lying_end
    if _lying_end is None:
        _lying_end = hero.skeleton(lying_pose(SIT)[0])
    return _lying_end


def draw(canvas, t, frame):
    with camera.view(canvas, t):
        room = Ink(canvas, frame, color=ROOM, width=4.0, prefix="bedroom")
        draw_bed(room)
        draw_nightstand(room, canvas, frame, time="6:00", phone=t < UNPLUG)
        level, tint = light_level(t)
        phone = phone_state(t)
        on_bed = phone is not None and t >= DROP
        if on_bed:       # lying on the bed beside his head, screen up, still playing
            glow(canvas, phone[0], 300, tint, 0.3 * level)
            draw_phone(canvas, room, *phone, level=level, tint=tint)

        eyes = 0.45 * blink(t, "hero.scroll", every=3.0, length=0.22)
        face = Face(eyes=eyes, brows=0.9, mouth="frown", mouth_size=0.5, bags=True)
        if t < SIT:      # lying in bed: body, then the blanket over it, then his arms on top
            pose, breath, look_side, look_down = lying_pose(t)
            j = hero.skeleton(pose, frame)
            for k, w in holding(t).items():
                j[k] = lerp(j[k], HOLD_ELBOWS[k], w)
            # reaching: his hand slides out low across the bed with the arm almost straight; there
            # the left elbow eases over to point down toward the bed, then the hand rises to the phone
            if REACH + 0.4 <= t < HOLD:
                low = hero.skeleton(pose.but(bend_hand_l=-1))["elbow_l"]
                j["elbow_l"] = lerp(j["elbow_l"], low, progress(t, REACH + 0.4, REACH + 0.6))
            # after letting go of the phone, his right elbow eases back to its usual side
            settle = progress(t, DROP + 0.1, DROP + 0.6)
            if pose.bend_hand_r == 1 and settle > 0:
                j["elbow_r"] = lerp(j["elbow_r"], hero.skeleton(pose.but(bend_hand_r=None))["elbow_r"], settle)
            head_r, away, tilt = hero.head_r, look_down, pose.lean + pose.head_tilt
            pen = draw_body(canvas, frame, j, ("legs", "spine", "head"), head_r)
            draw_blanket(room, breath, progress(t, THROW + 0.2, THROW + 0.6))
        else:            # getting up: seen from above, his head is on top of everything else
            j, head_r, away = getting_up(t, lying_end())
            look_side, tilt = 0.0, 0.0
            draw_blanket(room, 0.0, 1.0)
            pen = draw_body(canvas, frame, j, ("legs", "arms", "spine", "head"), head_r)
        draw_his_face(canvas, pen, j["head"], head_r, face, tilt, look_side, away)

        # the phone's light on the bed and on his face
        if phone is not None and level > 0:
            source = phone[0] if on_bed else (phone[0][0], phone[0][1] - 40)
            if not on_bed:
                glow(canvas, source, 260, tint, 0.28 * level)
            near = clamp(1 - math.dist(source, j["head"]) / 330)
            light_on_face(canvas, j["head"], head_r, source, tint, (0.45 if on_bed else 0.6) * level * near)

        if t < SIT:
            draw_body(canvas, frame, j, ("arms",), head_r)
        if phone is not None and not on_bed:
            draw_phone(canvas, room, *phone, level=level, tint=tint)


# -- sound ----------------------------------------------------------------------------------


def beat(seconds, bpm, kicks, snares, hats, key, hat_gain=-12):
    """A drum loop: lists of steps (16 per bar) for each drum."""
    mix = sk.Mix(seconds + 0.6)
    step = 60 / bpm / 4
    for n in range(int(seconds / step) + 1):
        at, s = n * step, n % 16
        if s in kicks:
            mix.add(sk.kick(key=(key, n)), at=at)
        if s in snares:
            mix.add(sk.snare(key=(key, n)), at=at, gain_db=-3)
        if s in hats:
            mix.add(sk.hihat(key=(key, n)), at=at, gain_db=hat_gain)
    return mix


def tune(mix, notes, start, every, held=0.25, gain_db=-4, key="tune"):
    for i, n in enumerate(notes):
        if n:
            mix.add(sk.piano(n, held, 0.75, key=(key, i)), at=start + i * every, gain_db=gain_db)
    return mix


# Who talks in each reel. Muffled, the words can't be made out; only the voices and their rhythm come through.
TALK = [
    ("Daniel", "Okay so this is literally the best morning routine I have ever tried, you just wake up and"),
    ("Karen", "No because why did nobody tell me this sooner, I am actually obsessed with it"),
    ("Moira", "And that is when I realised, wait, this changes everything, you guys"),
    ("Eddy (English (US))", "Here are three habits that completely changed my life. Number one, I stopped wasting "
     "my mornings in bed. Number two, I get up the second my alarm goes off. Number three, I go outside "
     "before I look at a single screen. Try it for one week and tell me how you feel."),
]


def reel_sounds():
    """Four clips, as heard muffled from the phone: someone talking, with quiet music under some."""
    music = [beat(2.0, 124, (0, 4, 8, 12), (4, 12), (2, 6, 10, 14), "r1"),
             None,
             tune(sk.Mix(2.0), ["A4", "C5", "E5", "A5", "E5", "C5"] * 2, 0.0, 0.14, key="r3"),
             beat(10.6, 96, (0, 8), (4, 12), (2, 6, 10, 14), "r4", hat_gain=-16)]
    clips = []
    for (voice, line), bed in zip(TALK, music):
        talk = sk.speech(line, voice)
        clip = np.zeros(len(talk) if bed is None else max(len(talk), bed.out.shape[1]))
        clip[:len(talk)] += talk
        if bed is not None:
            under = bed.render().mean(axis=0)
            clip[:len(under)] += 0.22 * under / (np.max(np.abs(under)) + 1e-9)
        clip = sk.muffled(clip)
        clips.append(clip / (np.max(np.abs(clip)) + 1e-9))
    return clips


def footstep_times():
    """When his feet land while he walks out (when a stride reaches its longest)."""
    times, k = [], 0
    while True:
        dist = STRIDE * (k + 0.5)
        # invert the walking() distance: ramp of 0.5 s, then steady SPEED
        ramp = 0.5
        dt = math.sqrt(2 * ramp * dist / SPEED) if dist < SPEED * ramp / 2 else dist / SPEED + ramp / 2
        if STAND_AT[0] + dist > 2000:
            return times
        times.append((WALK + dt, STAND_AT[0] + dist))
        k += 1


def soundtrack():
    mix = sk.Mix(DURATION)
    mix.add(sk.pad(["A1", "E2"], DURATION, attack=0.4, release=1.0, brightness=0.05, key="hum"),
            at=0, gain_db=-17, reverb=0.2)
    mix.add(sk.tick(key="unplug"), at=UNPLUG, gain_db=-12, pan=-0.35, reverb=0.1)

    # the reels: each clip plays until the next swipe, which cuts it off
    clips = reel_sounds()
    starts = [r[0] for r in REELS] + [DURATION]
    evened = (0, 0, 0, 3)                                 # the last voice is a little quieter
    for clip, a, b, even in zip(clips, starts[:-1], starts[1:], evened):
        length = int((b - a - 0.04) * sk.SR)
        part = sk.fade_edges(clip[:length], 0.004, 0.006)
        mix.add(part, at=a, gain_db=-10 + even, pan=0.1, reverb=0.05)

    mix.add(sk.lowpass(sk.footstep(0, weight=0.4, key="phone"), 900), at=LAND, gain_db=-16, pan=0.2)
    mix.add(sk.whoosh(0.7, peak=0.4, low=180, high=1400, key="blanket"), at=THROW + 0.12, gain_db=-14, reverb=0.15)
    mix.add(sk.whoosh(0.9, peak=0.5, low=150, high=900, key="sit"), at=SIT, gain_db=-20, reverb=0.15)
    for i, at in enumerate((SCOOT + 0.05, SCOOT + 0.55)):         # shuffling across the bed
        mix.add(sk.whoosh(0.45, peak=0.4, low=150, high=800, key=("scoot", i)), at=at, gain_db=-21, reverb=0.1)
    mix.add(sk.footstep(9, weight=0.5, key="floor"), at=STAND + 0.35, gain_db=-14, pan=0.35, reverb=0.1)
    for n, (at, x) in enumerate(footstep_times()):
        pan = clamp((x - 960) / 960, -1, 1)
        fade = -6 * clamp((x - 1800) / 200)                     # quieter as he leaves the picture
        mix.add(sk.footstep(n, weight=0.7), at=at, gain_db=-11 + fade, pan=pan, reverb=0.12)
    return mix
