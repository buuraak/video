"""Film 1, row 26 of the story: weeks after. About 13 seconds, three shots joined by hard cuts. It follows row
25, where Sam answered his "hey": "hey you!! walk tomorrow?"

 0-4.8 s     The street at dawn, from the side: the same two grey joggers who passed him twice, and now he jogs
             alongside them at their easy pace, all three together, the camera running with them.
 4.8-10.3 s  He and Sam on a bench by the street, from the front, waist up, turned toward each other. Sam is
             pale like him, with messy hair. They talk and both laugh once (no words, no laughter heard:
             only the street).
10.3-12.8 s  The board: four boxes already ticked today; he ticks the fifth, "Text one person". The bar goes from
             17 to 18 of its 20 steps.

No caption, no hum.
"""
import math

import numpy as np

import scenes.day_one as one
import scenes.too_fast as fast
from scenes.bedroom import ROOM, box, rounded_rect
from scenes.discipline import Discipline
from scenes.new_goals import squeaks
from scenes.street import GROUND, draw_street
from toolkit import BG, GREY, INK, Camera, Character, Face, Ink, Track, blink, clamp, lerp, progress
from toolkit import sound as sk
from toolkit.face import draw_face
from toolkit.rng import noise, rng

PEAK_DB = -10.1          # set so the sounds sit at the same level as the sounds in the other scenes
BENCH = 4.8            # cut to the bench
BOARD = 10.3           # cut to the board
DURATION = 12.8

# -- shot 1: jogging with the joggers -----------------------------------------------------------------------

PACE = 330             # their easy jogging pace, and now his
STEADY = Face(eyes=0.8, brows=0.0, mouth="open", mouth_size=0.15, bags=True)


def _jogger(who, x0, ground, phase0):
    return fast.Gait(who, lambda t: PACE, x0, ground, 330, cadence=(2.6, 2.7), stance=(0.24, 0.24), lift=(22, 26),
                     lean=(7, 7), phase0=phase0, until=BENCH + 0.5)


him = _jogger(fast.hero, 760, GROUND, 0.35)
joggers = [_jogger(Character("jogger1", height=404, color=GREY), 1000, fast.JOGGER_GROUND, 0.1),
           _jogger(Character("jogger2", height=418, color=GREY), 520, fast.JOGGER_GROUND, 0.6)]
jog_camera = Camera(x=lambda t: him.hip_x(t) + 20, y=600, zoom=1.15, handheld=lambda t: 1.5, name="weeks.jog")


def shot_jog(canvas, t, frame):
    with jog_camera.view(canvas, t):
        cx = jog_camera.state(t)[0]
        draw_street(canvas, frame, view=(cx - 1100, cx + 1100))
        for jog in joggers:              # further back on the pavement
            jog.who.draw(canvas, frame, jog.pose(t, fast.JOGGER_FACE.but(eyes=0.9 * blink(t, jog.who.name, every=2.7))))
        fast.hero.draw(canvas, frame, him.pose(t, STEADY.but(eyes=0.8 * blink(t, "hero.weeks", every=2.6))))


# -- Sam: pale like him, with messy hair (sheets/sam_options.png, 3) -------------------------------------------


def draw_sam_hair(canvas, frame, head, r, key="sam.hair", tilt=0.0):
    """A few strokes of messy hair sticking up from the top of Sam's head (any size of head)."""
    ink = Ink(canvas, frame, color=INK, width=max(3.0, 0.084 * r), prefix=key)
    for k, a in enumerate(np.linspace(-2.4, -0.7, 6)):
        a += math.radians(tilt)
        base = (head[0] + r * math.cos(a), head[1] + r * math.sin(a))
        tip = (head[0] + 1.32 * r * math.cos(a - 0.15), head[1] + 1.32 * r * math.sin(a - 0.15))
        ink.curve(base, ((base[0] + tip[0]) / 2 + 0.06 * r, (base[1] + tip[1]) / 2 - 0.04 * r), tip, f"h{k}")


# -- shot 2: on the bench --------------------------------------------------------------------------------------

R = 90                 # head size in this closer shot
HEAD_Y = 380
HIS_X, SAMS_X = 730, 1190
SEAT = 700             # the front edge of the bench's seat, where their hips are
# Who's talking when (after the cut): Sam, then him, then Sam again; then both laugh, and settle, smiling.
TALK = [("sam", 0.3, 1.5), ("him", 1.7, 2.9), ("sam", 3.1, 3.7)]
LAUGH = (3.8, 5.0)
bench_camera = Camera(zoom=Track((BENCH, 1.0), (BOARD, 1.04, "linear")), name="weeks.bench")


def talking(who, p):
    """0..1: how open his or her mouth is, talking (a few syllables a second)."""
    for name, a, b in TALK:
        if name == who and a <= p < b:
            env = progress(p, a, a + 0.1) * (1 - progress(p, b - 0.1, b))
            return env * (0.25 + 0.75 * abs(math.sin(2 * math.pi * 3.2 * (p - a) + 0.6 * noise(p * 3, who))))
    return 0.0


def laughing(p):
    """0..1: how much they're laughing."""
    return progress(p, LAUGH[0], LAUGH[0] + 0.15) * (1 - progress(p, LAUGH[1] - 0.4, LAUGH[1], "inout"))


def bench_face(who, p):
    laugh = laughing(p)
    talk = talking(who, p)
    listening = 1 - progress(p, LAUGH[1] - 0.4, LAUGH[1] + 0.3)   # smiling more once they've laughed
    smile = lerp(0.45 if who == "sam" else 0.25, 0.6, 1 - listening)
    eyes = lerp(0.85 if who == "sam" else 0.7, 0.3, laugh) * blink(p, f"weeks.{who}", every=2.4)
    if laugh > 0.05:          # laughing: a big smile, eyes squeezed nearly shut
        return Face(eyes=eyes, brows=0.0, mouth="smile", mouth_size=0.6 + 0.4 * laugh, bags=who == "him")
    if talk > 0.05:
        return Face(eyes=eyes, brows=0.05, mouth="open", mouth_size=0.1 + 0.35 * talk, bags=who == "him")
    return Face(eyes=eyes, brows=0.05, mouth="smile", mouth_size=smile, bags=who == "him")


def seated(canvas, frame, x, p, who, look):
    """Sitting on the bench, from the front: head (turned toward the other by `look`), body, hips on the seat,
    knees forward, hands resting on the knees. Talking nods the head a little; laughing tips it back and shakes
    the shoulders."""
    laugh = laughing(p)
    shake = 5 * laugh * math.sin(2 * math.pi * 6.5 * p)
    nod = 4 * talking(who, p) * math.sin(2 * math.pi * 1.6 * p)
    breath = 2 * math.sin(2 * math.pi * p / 3.4 + (0 if who == "him" else 1.3))
    head = (x + look * 10, HEAD_Y - 12 * laugh + shake * 0.5 + nod + breath)
    neck = (x, HEAD_Y + R + breath)
    sh = (x, neck[1] + 0.46 * R + shake)
    hip = (x, SEAT - 2)
    ink = Ink(canvas, frame, color=INK, width=11, prefix=f"weeks.{who}")
    for side in (-1, 1):                                          # legs: knees toward us, shins down
        knee = (x + side * 44, SEAT + 72)
        ink.line((x + side * 12, hip[1]), knee, f"thigh{side}", taper=0.0)
        ink.line(knee, (x + side * 48, 1000), f"shin{side}", taper=0.0)
    ink.line((head[0], head[1] + R), hip, "spine", taper=0.0)
    for side in (-1, 1):                                          # arms: hands resting on the knees
        hand = (x + side * 34, SEAT + 62)
        elbow = (x + side * 78, (sh[1] + hand[1]) / 2 - 6)
        ink.line(sh, elbow, f"upper{side}", taper=0.0)
        ink.line(elbow, hand, f"fore{side}", taper=0.0)
    ink.circle(head, R, "head", fill=BG)
    draw_face(ink, head, R, bench_face(who, p), -4 * laugh * (1 if who == "him" else -1), look, BG)
    return head


def shot_bench(canvas, t, frame):
    p = t - BENCH
    with bench_camera.view(canvas, t):
        canvas.save()            # the street behind them, closer
        canvas.translate(960, 540)
        canvas.scale(1.6, 1.6)
        canvas.translate(-960, -560)
        draw_street(canvas, frame, view=(0, 1920))
        canvas.restore()
        bench = Ink(canvas, frame, color=ROOM, width=6.0, prefix="weeks.bench")
        for k, y in enumerate((520, 590)):           # the bench: its backrest behind them...
            box(bench, rounded_rect(300, y, 1620, y + 46, 8), f"plank{k}")
        for k, x in enumerate((330, 1590)):
            bench.line((x, 520), (x, 1000), f"post{k}", width=6.5)
        box(bench, rounded_rect(290, SEAT - 14, 1630, SEAT + 22, 8), "seat")    # ...and its seat, under them
        seated(canvas, frame, HIS_X, p, "him", 0.35)
        head = seated(canvas, frame, SAMS_X, p, "sam", -0.35)
        draw_sam_hair(canvas, frame, head, R, "weeks.sam.hair")


# -- shot 3: the fifth tick ------------------------------------------------------------------------------------

ticks = one.Ticks([(BOARD, 4)], done=4)


def draw(canvas, t, frame):
    if t < BENCH:
        shot_jog(canvas, t, frame)
    elif t < BOARD:
        shot_bench(canvas, t, frame)
    else:
        ticks.draw(canvas, t, frame)


bar = Discipline(start=17, fills=ticks.fills())  # 17 -> 18


def overlay(canvas, t, frame):
    bar.draw(canvas, t, frame)


def soundtrack():
    mix = sk.Mix(DURATION)

    def effect(prompt, seconds, name):            # ElevenLabs effects, all brought to the same level first
        return sk.normalize(sk.eleven_sound(prompt, seconds, name))

    street = effect("A quiet city street just before sunrise: distant traffic, a faint cold wind, no voices, "
                    "no birds", 17.0, "street_dawn")
    mix.add(sk.fade_edges(street[:int(BOARD * sk.SR)], 0.05, 0.1), at=0, gain_db=-27)
    for gait, key, gain in [(him, "weeks.him", -13)] + [(j, j.who.name, -17) for j in joggers]:
        for n, (tk, tl, foot, x, h) in enumerate(gait.steps):
            if 0 <= tk < BENCH:
                mix.add(sk.footstep(n, weight=0.45, key=key), at=tk, gain_db=gain,
                        pan=clamp((x - jog_camera.state(tk)[0]) / 960, -1, 1), reverb=0.1)
    grains = squeaks()
    g = rng("weeks.squeak")
    for at in ticks.squeaks():
        mix.add(grains[g.integers(len(grains))], at=at, gain_db=-15, pan=-0.15, reverb=0.08)
    bar.add_sounds(mix)
    return mix
