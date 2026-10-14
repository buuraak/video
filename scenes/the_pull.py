"""Film 1, row 27 of the story: the pull. About 12.6 seconds. Weeks into his new days, the old voice tries once
more. It follows row 26 (the bar at 18 of its 20 steps).

 0-0.9 s     The clock, 6:00, beeping.
 0.9-3.6 s   His bedroom window up close, from inside: rain running down the glass, the grey dawn outside, the
             sound of rain.
 3.6-7.4 s   The clean room from above: he sits on the edge of the bed. His phone, face up on the nightstand,
             lights up by itself: the smug man's reel plays, muffled, glowing, and the old hum creeps back in
             under the rain. He turns toward it.
 7.4-9.6 s   The phone up close on the nightstand: the reel, calling. MY FIRST / MILLION AT 22.
 9.6-12.6 s  The room again, darkened, and over it the caption fills the picture, the one time it leaves the
             black bar (sheets/caption_options.png, 3): "I'll start *tomorrow*." The bar starts to shake.

Sound: the alarm, the rain, the reel, the hum creeping back, a deep hit as the caption lands, the bar's rattle.
"""
import math

import numpy as np
import skia

import scenes.day_one as one
import scenes.scroll as scroll
from scenes.bedroom import PHONE, PHONE_TURN, ROOM, box, draw_bed, draw_blanket, draw_nightstand, hero, rounded_rect
from scenes.discipline import Discipline
from scenes.grind_1 import draw_reel
from scenes.grind_2 import draw_clock
from scenes.scroll import glow, reel_sounds
from scenes.the_quote import C, PL, PW, SCREEN_RECT, TINT
from toolkit import BG, SCREEN, Camera, Ink, Track, lerp, progress, to_color
from toolkit import sound as sk
from toolkit.finish import BAR
from toolkit.rng import noise, rng
from toolkit.text import FADE, draw_text

PEAK_DB = -2.2          # set so the sounds sit at the same level as the sounds in the other scenes
WINDOW = 0.9            # cut to the window
ROOM_SHOT = 3.6         # cut to the room from above
LIGHTS_UP = 4.3         # the phone lights up by itself
TURN = (4.6, 5.6)       # he turns toward it
PHONE_SHOT = 7.4        # cut to the phone close up
CAPTION = 9.6           # back to the room: the caption
DURATION = 12.6

# -- shot 1: the clock --------------------------------------------------------------------------------------

clock_camera = Camera(zoom=1.05, name="pull.clock")


def shot_clock(canvas, t, frame):
    with clock_camera.view(canvas, t):
        draw_clock(canvas, frame, "6:00", on=1.0 if sk.alarm_on(t) else 0.0)


# -- shot 2: rain on the window -------------------------------------------------------------------------------
# From inside: the window frame with a cross of bars, the grey dawn and the dark buildings beyond, rain falling
# outside, and drops on the glass, some running down.

GLASS = (330, 160, 1590, 900)
SKY_TOP, SKY_LOW = (64, 70, 84), (40, 44, 54)
window_camera = Camera(zoom=Track((WINDOW, 1.0), (ROOM_SHOT, 1.04, "linear")), name="pull.window")


def _drops():
    g = rng("pull.drops")
    still = [(g.uniform(GLASS[0], GLASS[2]), g.uniform(GLASS[1], GLASS[3]), g.uniform(3, 7)) for _ in range(70)]
    running = [(g.uniform(GLASS[0] + 20, GLASS[2] - 20), g.uniform(-2.0, 2.0), g.uniform(60, 160), g.uniform(4, 7))
               for _ in range(14)]
    return still, running


STILL_DROPS, RUNNING_DROPS = _drops()


def draw_window(canvas, frame, t):
    x0, y0, x1, y1 = GLASS
    glow(canvas, (960, 530), 1100, (170, 182, 205), 0.1)            # the cold grey light coming in
    sky = skia.GradientShader.MakeLinear([skia.Point(0, y0), skia.Point(0, y1)], [to_color(SKY_TOP), to_color(SKY_LOW)])
    canvas.drawRect(skia.Rect(x0, y0, x1, y1), skia.Paint(Shader=sky))
    canvas.save()
    canvas.clipRect(skia.Rect(x0, y0, x1, y1))
    far = Ink(canvas, frame, color=(70, 74, 86), width=2.5, prefix="pull.far")     # the buildings across the street
    g = rng("pull.buildings")
    x = x0 - 40
    k = 0
    while x < x1:
        w, h = g.uniform(160, 300), g.uniform(260, 470)
        box(far, [(x, y1), (x, y1 - h), (x + w, y1 - h), (x + w, y1)], f"b{k}", fill=(28, 30, 37))
        x += w + g.uniform(10, 30)
        k += 1
    rain = skia.Paint(AntiAlias=True, Color=to_color((180, 190, 210, 70)), StrokeWidth=2.0)   # rain falling outside
    gr = rng("pull.rain")
    for _ in range(140):
        rx, phase, speed = gr.uniform(x0, x1 + 120), gr.uniform(0, 1), gr.uniform(1300, 1700)
        y = y0 - 60 + ((t * speed / (y1 - y0 + 120) + phase) % 1.0) * (y1 - y0 + 120)
        canvas.drawLine(rx, y, rx - 10, y + 46, rain)
    drop = skia.Paint(AntiAlias=True, Color=to_color((200, 208, 225, 95)))
    for dx, dy, r in STILL_DROPS:                                    # drops on the glass
        canvas.drawOval(skia.Rect(dx - r * 0.8, dy - r, dx + r * 0.8, dy + r), drop)
    trail = skia.Paint(AntiAlias=True, Color=to_color((200, 208, 225, 45)), StrokeWidth=3.0, Style=skia.Paint.kStroke_Style)
    for k, (dx, start, speed, r) in enumerate(RUNNING_DROPS):        # ...some running down, leaving a trail
        travelled = max(0.0, (t - WINDOW - start) % 6.0) * speed * (0.8 + 0.4 * noise(t * 2, "pull.run", k))
        top = y0 + (k * 97) % 300
        y = top + travelled
        if y > y1 + 20:
            continue
        path = skia.Path()
        path.moveTo(dx, top)
        for yy in np.linspace(top, y, 12):
            path.lineTo(dx + 5 * math.sin(yy * 0.03 + k), yy)
        canvas.drawPath(path, trail)
        canvas.drawOval(skia.Rect(dx + 5 * math.sin(y * 0.03 + k) - r * 0.8, y - r, dx + 5 * math.sin(y * 0.03 + k) + r * 0.8,
                                  y + r * 1.2), drop)
    canvas.restore()
    ink = Ink(canvas, frame, color=ROOM, width=6.0, prefix="pull.window")     # the frame, its bars, the sill
    frame_pts = [(x0 - 40, y0 - 40), (x1 + 40, y0 - 40), (x1 + 40, y1 + 40), (x0 - 40, y1 + 40)]
    ink.stroke(frame_pts, "outer", closed=True)
    ink.stroke([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], "inner", closed=True, width=4.0)
    for k, ((ax, ay), (bx, by)) in enumerate((((960, y0), (960, y1)), ((x0, 470), (x1, 470)))):
        canvas.drawRect(skia.Rect(min(ax, bx) - 14, min(ay, by) - 14, max(ax, bx) + 14, max(ay, by) + 14),
                        skia.Paint(Color=to_color(BG)))
        ink.line((ax - 14 if ax == bx else ax, ay - 14 if ay == by else ay),
                 (bx - 14 if ax == bx else bx, by - 14 if ay == by else by), f"bar{k}a", width=3.5, taper=0.0)
        ink.line((ax + 14 if ax == bx else ax, ay + 14 if ay == by else ay),
                 (bx + 14 if ax == bx else bx, by + 14 if ay == by else by), f"bar{k}b", width=3.5, taper=0.0)
    box(ink, rounded_rect(x0 - 80, y1 + 40, x1 + 80, y1 + 70, 6), "sill")


def shot_window(canvas, t, frame):
    with window_camera.view(canvas, t):
        draw_window(canvas, frame, t)


# -- shot 3: from above, he sits on the edge of the bed; the phone lights up -----------------------------------

room_camera = Camera(zoom=Track((ROOM_SHOT, 1.0), (PHONE_SHOT, 1.03, "linear")), name="pull.room")
SITTING = scroll.getting_up(scroll.STAND - 0.06, one.LYING_END)    # sitting on the right edge, legs over the side


def lit(t):
    """How bright the phone's screen is: dark, then lighting up by itself, flickering with the reel."""
    return progress(t, LIGHTS_UP, LIGHTS_UP + 0.25, "out") * (0.85 + 0.12 * noise(t * 5, "pull.reel"))


def turned_to_phone(t):
    """His joints, sitting on the edge, his shoulders and head turning back toward the nightstand."""
    j, r, away = SITTING
    hip = j["hip"]
    a = math.radians(-34 * progress(t, *TURN, "inout"))
    c, s = math.cos(a), math.sin(a)
    out = dict(j)
    for k in ("neck", "shoulder", "head", "elbow_l", "hand_l", "elbow_r", "hand_r"):
        x, y = j[k][0] - hip[0], j[k][1] - hip[1]
        out[k] = (hip[0] + x * c - y * s, hip[1] + x * s + y * c)
    return out, r, away


def draw_room(canvas, frame, t):
    room = Ink(canvas, frame, color=ROOM, width=4.0, prefix="bedroom")
    draw_bed(room)
    draw_nightstand(room, canvas, frame, time="6:01", phone="plugged", bottles=())   # clean: no mess, no bottles
    draw_blanket(room, 0.0, 1.0)
    level = lit(t)
    glow(canvas, PHONE, 420, TINT, 0.3 * level)
    scroll.draw_phone(canvas, room, PHONE, 120, 60, PHONE_TURN - 90, "lit" if level > 0.02 else "dark", level=level,
                      tint=TINT)
    j, r, away = turned_to_phone(t)
    pen = scroll.draw_body(canvas, frame, j, ("legs", "arms", "spine", "head"), r)
    scroll.draw_his_face(canvas, pen, j["head"], r, one.CALM, 0.0, 0.0, away)


def shot_room(canvas, t, frame):
    with room_camera.view(canvas, t):
        draw_room(canvas, frame, t)


# -- shot 4: the phone up close on the nightstand -------------------------------------------------------------

WORDS = ((PHONE_SHOT + 0.3, "MY FIRST"), (PHONE_SHOT + 0.6, "MILLION AT 22"))
SMALL = 0.44            # the phone at this size, lying on the nightstand
phone_camera = Camera(zoom=Track((PHONE_SHOT, 1.0), (CAPTION, 1.08, "linear")), name="pull.phone")


def shot_phone(canvas, t, frame):
    with phone_camera.view(canvas, t):
        wood = Ink(canvas, frame, color=ROOM, width=4.0, prefix="pull.wood")      # the nightstand's top
        box(wood, rounded_rect(140, 60, 1780, 1040, 18), "top", fill=(20, 19, 21))
        for k, y in enumerate((260, 470, 690, 880)):                               # its grain, faint
            wood.line((170, y), (1750, y + 6), f"grain{k}", width=1.6, color=(*ROOM[:3], 60))
        glow(canvas, C, 700, TINT, 0.3 * lit(t))
        canvas.save()
        canvas.translate(C[0], C[1])
        canvas.scale(SMALL, SMALL)
        canvas.translate(-C[0], -C[1])
        cable = Ink(canvas, frame, color=ROOM, width=12.0, prefix="pull.cable")    # the charger, plugged in below
        cable.stroke([(C[0], C[1] + PL / 2), (C[0] + 20, C[1] + PL / 2 + 260), (C[0] + 160, C[1] + PL / 2 + 600)],
                     "cable", taper=0.0)
        ink = Ink(canvas, frame, color=ROOM, width=12.0, prefix="quote.phone")
        box(ink, rounded_rect(C[0] - PW / 2, C[1] - PL / 2, C[0] + PW / 2, C[1] + PL / 2, 60), "phone", width=12.0)
        screen = rounded_rect(*SCREEN_RECT, 40)
        path = skia.Path()
        path.addPoly([skia.Point(*q) for q in screen], True)
        canvas.save()
        canvas.clipPath(path, doAntiAlias=True)
        draw_reel(canvas, frame, t, "guru", WORDS)
        canvas.restore()
        ink.stroke(screen, "screen", closed=True, width=5.0)
        canvas.restore()


# -- the scene ------------------------------------------------------------------------------------------


def draw(canvas, t, frame):
    if t < WINDOW:
        shot_clock(canvas, t, frame)
    elif t < ROOM_SHOT:
        shot_window(canvas, t, frame)
    elif t < PHONE_SHOT or t >= CAPTION:
        shot_room(canvas, t, frame)
    else:
        shot_phone(canvas, t, frame)


bar = Discipline(start=18, shakes=[(CAPTION, DURATION + 1.0)])   # it trembles from here, on into row 28


def overlay(canvas, t, frame):
    if t >= CAPTION:            # the room darkens, and the old voice fills the picture
        u = progress(t, CAPTION, CAPTION + FADE)
        canvas.drawRect(skia.Rect(0, BAR, 1920, 1080 - BAR), skia.Paint(Color=to_color((0, 0, 0, int(150 * u)))))
        draw_text(canvas, "I'll start *tomorrow*.", 960, 610, size=228, alpha=u)
    bar.draw(canvas, t, frame)


def soundtrack():
    mix = sk.Mix(DURATION)

    def effect(prompt, seconds, name):            # ElevenLabs effects, all brought to the same level first
        return sk.normalize(sk.eleven_sound(prompt, seconds, name))

    mix.add(sk.fade_edges(sk.alarm(WINDOW), 0.0, 0.01), at=0, gain_db=-7, reverb=0.1)
    rain = effect("Heavy steady rain against a bedroom window, heard from inside a quiet room, early morning, "
                  "no thunder", 12.0, "rain_window")
    loud = np.ones(int((DURATION - WINDOW) * sk.SR))     # closest at the window, further off in the room
    k = int((ROOM_SHOT - WINDOW) * sk.SR)
    loud[k:] = 10 ** (-6 / 20)
    mix.add(sk.fade_edges(rain[:len(loud)] * loud, 0.02, 0.3), at=WINDOW, gain_db=-14, reverb=0.05)
    # the reel playing by itself, muffled: quieter from across the room, nearer in the close-up
    adam = reel_sounds()[0]
    part = adam[:int((DURATION - LIGHTS_UP) * sk.SR)]
    near = np.full(len(part), 10 ** (-7 / 20))
    a, b = int((PHONE_SHOT - LIGHTS_UP) * sk.SR), int((CAPTION - LIGHTS_UP) * sk.SR)
    near[a:b] = 1.0
    mix.add(sk.fade_edges(part * near, 0.05, 0.4), at=LIGHTS_UP, gain_db=-9 + 3.4, pan=-0.2, reverb=0.08)
    # the old hum creeping back in under it all
    hum = sk.pad(["A1", "E2"], DURATION - LIGHTS_UP, attack=4.0, release=1.0, brightness=0.05, key="hum")
    mix.add(hum, at=LIGHTS_UP, gain_db=-19, reverb=0.2)
    mix.add(sk.thud(1.0, key="pull.hit"), at=CAPTION, gain_db=-8, reverb=0.3)       # the caption lands
    bar.add_sounds(mix)
    return mix
