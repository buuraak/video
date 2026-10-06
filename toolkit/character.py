"""The stick figure: round head, body, arms and legs that bend at elbows and knees.

Give hands and feet exact points to reach; the elbows and knees work out
where to bend. If a hand or foot can't reach its point, it stretches as far
as it can toward it and the problem is reported (see report.py).

"left" and "right" always mean the left and right side of the SCREEN.

    hero = Character("hero")
    pose = hero.stand(x=960, ground=900, hand_r=(1100, 400))
    hero.draw(canvas, frame, pose)

The enemy is the same figure, drawn red and bigger, with a glow and glitches:

    enemy = Character("enemy", height=640, color=RED, glow=True, glitch=True)
"""
import math
from dataclasses import dataclass, replace

import skia

from . import report
from .anim import pulse
from .lines import Ink, to_color
from .rng import rand, rng
from .style import BG, FPS, H, INK, LINE_WIDTH, RED_DARK, W

# Body proportions, as fractions of the character's full height.
HEAD_R = 0.13
SPINE = 0.30
SHOULDER_DROP = 0.06   # how far below the neck the arms start
UPPER_ARM = 0.17
FOREARM = 0.16
THIGH = 0.21
SHIN = 0.21
REST_HAND = (0.10, 0.29)   # where hands hang, from the shoulder (sideways, down)
REST_FOOT = (0.08, 0.39)   # where feet stand, from the hip (sideways, down); knees keep a little bend
REST_HAND_SIDE = (0.045, 0.025, 0.31)   # side view: hands slightly forward, near/far apart, down
REST_FOOT_SIDE = 0.075     # side view: how far the feet stand forward and back of the hip

LIMBS = ("hand_l", "hand_r", "foot_l", "foot_r")
LIMB_WORDS = {"hand_l": "left hand", "hand_r": "right hand", "foot_l": "left foot", "foot_r": "right foot"}


@dataclass
class Pose:
    """Where the character is and what it's doing on one frame.

    x, y      position of the hips
    lean      body tilt in degrees (positive leans right)
    head_tilt extra head tilt in degrees
    facing    -1 looking left, 0 facing us, 1 looking right
    hand_l... points for hands and feet to reach; None means a relaxed rest position
    bend_*    which way elbows/knees bend: 1 or -1, None picks a natural default
    face      a Face (see face.py), or None for a blank head
    ground    the floor line: feet without their own targets stay planted on it,
              so when the hips move (breathing, sinking) the knees bend instead.
              None lets resting feet hang below the hips (for jumping or floating).
    """
    x: float = 960.0
    y: float = 640.0
    lean: float = 0.0
    head_tilt: float = 0.0
    facing: int = 0
    hand_l: tuple = None
    hand_r: tuple = None
    foot_l: tuple = None
    foot_r: tuple = None
    bend_hand_l: int = None
    bend_hand_r: int = None
    bend_foot_l: int = None
    bend_foot_r: int = None
    face: object = None
    ground: float = None

    def but(self, **changes):
        """A copy of this pose with some things changed."""
        return replace(self, **changes)


def reach(root, target, a, b, bend):
    """Two-bone reach from root toward target with bones of length a and b.

    Returns (joint, end, problem). problem is None when the end lands exactly on
    the target, otherwise how many pixels too far (positive) or too close (negative).
    """
    rx, ry = root
    dx, dy = target[0] - rx, target[1] - ry
    d = math.hypot(dx, dy)
    ux, uy = (dx / d, dy / d) if d > 1e-9 else (0.0, 1.0)
    problem = None
    if d > a + b + 1e-6:
        problem, d = d - (a + b), a + b
    elif d < abs(a - b) - 1e-6:
        problem, d = d - abs(a - b), abs(a - b)
    cos_a = max(-1.0, min(1.0, (a * a + d * d - b * b) / (2 * a * max(d, 1e-9))))
    sin_a = math.sqrt(1 - cos_a * cos_a)
    px, py = -uy, ux
    joint = (rx + a * (cos_a * ux + sin_a * bend * px), ry + a * (cos_a * uy + sin_a * bend * py))
    end = (target[0], target[1]) if problem is None else (rx + ux * d, ry + uy * d)
    return joint, end, problem


def _rotate(vx, vy, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return vx * c - vy * s, vx * s + vy * c


class Character:
    def __init__(self, name, height=440.0, color=INK, line_width=None, head_fill=BG,
                 glow=False, glow_color=None, glitch=False, glitch_often=0.14):
        """glow: a soft coloured haze around the figure (the enemy's red/dark glow).
        glitch: now and then the outline tears sideways for a few frames.
        glitch_often: roughly what share of moments glitch (0.14 is about once a second).
        """
        self.name = name
        self.height = height
        self.color = color
        self.line_width = line_width or LINE_WIDTH * height / 440.0
        self.head_fill = head_fill
        self.glow = glow
        self.glow_color = glow_color or color
        self.glitch = glitch
        self.glitch_often = glitch_often

    # -- sizes in pixels ---------------------------------------------------
    @property
    def head_r(self): return HEAD_R * self.height
    @property
    def arm(self): return (UPPER_ARM * self.height, FOREARM * self.height)
    @property
    def leg(self): return (THIGH * self.height, SHIN * self.height)

    def stand(self, x, ground, **pose):
        """A pose with the feet planted on the floor line at height `ground`.

        Move the hips afterwards (e.g. pose.but(y=...)) and the feet stay put.
        """
        return Pose(x=x, y=ground - REST_FOOT[1] * self.height, ground=ground, **pose)

    def _bend(self, pose, limb):
        given = getattr(pose, "bend_" + limb)
        if given is not None:
            return given
        side = 1 if limb.endswith("_l") else -1      # front-facing: bend outward
        if pose.facing == 0:
            return side
        if limb.startswith("hand"):
            return pose.facing                         # elbows point backward
        return -pose.facing                            # knees point forward

    def joints(self, pose):
        """Where the body's joints are for a pose, with relaxed arms and legs.

        Use it to place hand and foot targets relative to the body, e.g.
        sh = hero.joints(pose)["shoulder"]; pose = pose.but(hand_r=(sh[0] + 80, sh[1] - 60))
        """
        return self.skeleton(pose.but(hand_l=None, hand_r=None, foot_l=None, foot_r=None))

    def skeleton(self, pose, frame=None):
        """Work out every joint position for a pose. Reports any limb that can't reach."""
        h = self.height
        hip = (pose.x, pose.y)
        sx, sy = _rotate(0, -SPINE * h, pose.lean)
        neck = (hip[0] + sx, hip[1] + sy)
        dx, dy = _rotate(0, -SHOULDER_DROP * h, pose.lean)
        shoulder = (neck[0] - dx, neck[1] - dy)
        hx, hy = _rotate(0, -self.head_r, pose.lean + pose.head_tilt)
        head = (neck[0] + hx, neck[1] + hy)

        j = {"hip": hip, "neck": neck, "shoulder": shoulder, "head": head}
        roots = {"hand_l": shoulder, "hand_r": shoulder, "foot_l": hip, "foot_r": hip}
        for limb in LIMBS:
            is_hand = limb.startswith("hand")
            root = roots[limb]
            a, b = self.arm if is_hand else self.leg
            target = getattr(pose, limb)
            if target is None:
                side = -1 if limb.endswith("_l") else 1
                if is_hand:
                    if pose.facing:   # side view: arms hang almost straight, one just ahead of the other
                        across = (pose.facing * REST_HAND_SIDE[0] + side * REST_HAND_SIDE[1]) * h
                        target = (root[0] + across, root[1] + REST_HAND_SIDE[2] * h)
                    else:
                        target = (root[0] + side * REST_HAND[0] * h, root[1] + REST_HAND[1] * h)
                else:                 # side view: feet a natural step apart, one forward, one back
                    spread = REST_FOOT_SIDE if pose.facing else REST_FOOT[0]
                    down = pose.ground if pose.ground is not None else root[1] + REST_FOOT[1] * h
                    target = (root[0] + side * spread * h, down)
            joint, end, problem = reach(root, target, a, b, self._bend(pose, limb))
            j[("elbow" if is_hand else "knee") + limb[-2:]] = joint
            j[limb] = end
            if problem is not None:
                when = f"frame {frame}: " if frame is not None else ""
                how = (f"{problem:.0f} px too far away" if problem > 0
                       else f"{-problem:.0f} px too close to bend to")
                report.problem(f"{when}{self.name}'s {LIMB_WORDS[limb]} can't reach "
                               f"({target[0]:.0f}, {target[1]:.0f}): it is {how}")
        return j

    def draw(self, canvas, frame, pose, opacity=1.0):
        """Draw the character. Returns the joint positions it used.

        opacity below 1 fades the whole figure (0 = invisible).
        """
        if opacity < 1.0:
            canvas.saveLayerAlpha(None, int(255 * max(opacity, 0.0)))
            try:
                return self.draw(canvas, frame, pose)
            finally:
                canvas.restore()
        j = self.skeleton(pose, frame)
        if not (self.glow or self.glitch):
            self._draw_lines(canvas, frame, pose, j)
            return j
        # Record the drawing once, then reuse it for the glow and the glitch.
        recorder = skia.PictureRecorder()
        rc = recorder.beginRecording(skia.Rect(-W, -H, 2 * W, 2 * H))
        self._draw_lines(rc, frame, pose, j)
        picture = recorder.finishRecordingAsPicture()
        if self.glow:
            self._draw_glow(canvas, picture, frame)
        if self.glitch and self.is_glitching(frame):
            self._draw_glitched(canvas, picture, frame, j)
        else:
            canvas.drawPicture(picture)
        return j

    def _draw_lines(self, canvas, frame, pose, j):
        ink = Ink(canvas, frame, color=self.color, width=self.line_width, prefix=self.name)
        bone = dict(pin_ends=True, taper=0.15)
        for side in ("_l", "_r"):
            ink.line(j["hip"], j["knee" + side], "thigh" + side, **bone)
            ink.line(j["knee" + side], j["foot" + side], "shin" + side, **bone)
        ink.line(j["hip"], j["neck"], "spine", **bone)
        ink.circle(j["head"], self.head_r, "head", fill=self.head_fill)
        if pose.face is not None:
            from .face import draw_face
            draw_face(ink, j["head"], self.head_r, pose.face, pose.lean + pose.head_tilt,
                      pose.facing, self.head_fill)
        for side in ("_l", "_r"):
            ink.line(j["shoulder"], j["elbow" + side], "upper_arm" + side, **bone)
            ink.line(j["elbow" + side], j["hand" + side], "forearm" + side, **bone)

    # -- the enemy's glow and glitch -----------------------------------------

    def _draw_glow(self, canvas, picture, frame):
        breathe = 0.85 + 0.15 * pulse(frame / FPS, rate=0.5)
        scale = self.height / 640.0
        for color, sigma, alpha in ((RED_DARK, 80, 1.0), (self.glow_color, 26, 0.7), (self.glow_color, 9, 0.8)):
            paint = skia.Paint(
                ImageFilter=skia.ImageFilters.Blur(sigma * scale, sigma * scale),
                ColorFilter=skia.ColorFilters.Blend(
                    to_color((*color, int(255 * alpha * breathe))), skia.BlendMode.kSrcIn))
            canvas.drawPicture(picture, None, paint)

    def is_glitching(self, frame):
        """Glitches come in short bursts of 4 frames, at stable but irregular moments."""
        return rand("glitch", self.name, frame // 4) < self.glitch_often

    def _draw_glitched(self, canvas, picture, frame, j):
        g = rng("glitch", self.name, frame)
        pad = self.head_r + self.line_width * 2
        xs = [p[0] for p in j.values()]
        ys = [p[1] for p in j.values()]
        top, bottom = min(ys) - pad, max(ys) + pad
        reach = self.height * 0.06
        # a faint dark-red ghost, knocked sideways
        ghost = skia.Paint(ColorFilter=skia.ColorFilters.Blend(
            to_color((*RED_DARK, 200)), skia.BlendMode.kSrcIn))
        canvas.save()
        canvas.translate(g.choice([-1, 1]) * g.uniform(0.3, 0.8) * reach, 0)
        canvas.drawPicture(picture, None, ghost)
        canvas.restore()
        # the figure itself, cut into horizontal slices that slip sideways
        cuts = sorted(g.uniform(top, bottom, size=g.integers(3, 7)))
        edges = [top - H] + list(cuts) + [bottom + H]
        for y0, y1 in zip(edges[:-1], edges[1:]):
            dx = 0.0 if g.random() < 0.4 else g.uniform(-1, 1) * reach
            canvas.save()
            canvas.clipRect(skia.Rect(min(xs) - W, y0, max(xs) + W, y1))
            canvas.translate(dx, 0)
            canvas.drawPicture(picture)
            canvas.restore()
