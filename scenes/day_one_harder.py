"""Film 1, row 24 of the story: day one, harder. About 20 seconds: the last two small things, each followed by a
tick on the board and a step on the bar, as in row 23 (which this follows).

 0-7.9 s     His notebook up close, open: a dark page with pale ink, like the board. His stick arm comes in
             from the bottom right with a pen and writes three lines, how he feels, slowly, with a pause before
             the last: Still tired. / But I got up. / That's a start.
 7.9-9.7 s   The board: he ticks "Write 3 lines". The bar fills a step.
 9.7-16.9 s  His phone up close, Sam's chat: Sam's three unanswered messages, "you coming tonight?", "haven't
             seen you in ages", "miss you man". He types "hey", deletes it, waits, types it again and sends it.
             "Delivered". He looks at it a moment and puts the phone down. No reply yet.
16.9-19.9 s  The board: he ticks "Text one person": all five ticked, his first whole day. The bar fills a step.

No caption. No hum: the pen on paper, the keys, the message going, the marker and the bar.
"""
import math

import numpy as np
import skia

from scenes.bedroom import ROOM, box, rounded_rect
from scenes.day_one import Ticks
from scenes.discipline import Discipline
from scenes.door_wall import MARKER_INK
from scenes.new_goals import squeaks
from scenes.night import text
from scenes.scroll import glow
from scenes.the_quote import C, PL, PW, SCREEN_RECT
from toolkit import BG, INK, SCREEN, Camera, Ink, Track, boil, lerp, progress, to_color
from toolkit import sound as sk
from toolkit.rng import rng
from toolkit.text import font

PEAK_DB = -10.1          # set so his sounds sit at the same level as the sounds in the other scenes
TICK_4 = 7.9
PHONE = 9.7
TICK_5 = 16.9
DURATION = 19.9

# -- his notebook --------------------------------------------------------------------------------------------
# Open, seen from above, filling the picture: a dark page with faint ruled lines and pale ink, like the board
# (the user's pick, sheets/notebook_chat_options.png 1). Shared with the days after (row 25).

PAGE, RULE = (32, 33, 38), (58, 60, 68)
LEFT_PAGE, RIGHT_PAGE = (170, 120, 955, 1010), (965, 120, 1750, 1010)
RULE_TOP, RULE_STEP = 250, 78
TEXT_X, TEXT_SIZE = 1040, 64
LINES = ["Still tired.", "But I got up.", "That's a start."]


def line_box(k, x=TEXT_X):
    """Where line k of the right page is written: (left x, baseline y, width)."""
    return x, RULE_TOP + RULE_STEP * (k + 1) - 12, font(TEXT_SIZE).measureText(LINES[k])


def draw_notebook(canvas, frame, lines, key="notebook"):
    """The open notebook; lines: what's written on the right page, as (text, shown 0..1)."""
    pen = Ink(canvas, frame, color=ROOM, width=5.0, prefix=key)
    box(pen, rounded_rect(*LEFT_PAGE, 14), "left", fill=PAGE)
    box(pen, rounded_rect(*RIGHT_PAGE, 14), "right", fill=PAGE)
    pen.line((960, LEFT_PAGE[1]), (960, LEFT_PAGE[3]), "spine", width=4.0)
    rules = Ink(canvas, frame, color=RULE, width=2.0, prefix=key + ".rule")
    for k, y in enumerate(range(RULE_TOP, 980, RULE_STEP)):
        rules.line((LEFT_PAGE[0] + 30, y), (LEFT_PAGE[2] - 25, y), f"l{k}", taper=0.0)
        rules.line((RIGHT_PAGE[0] + 25, y), (RIGHT_PAGE[2] - 30, y), f"r{k}", taper=0.0)
    f = font(TEXT_SIZE)
    for k, (line, shown) in enumerate(lines):
        if shown <= 0:
            continue
        x, y = TEXT_X, RULE_TOP + RULE_STEP * (k + 1) - 12
        w = f.measureText(line)
        jitter = rng("notebook.word", key, k, boil(frame)).uniform(-1, 1, 2) * TEXT_SIZE * 0.012
        canvas.save()
        if shown < 1:
            canvas.clipRect(skia.Rect(x - TEXT_SIZE, y - 2 * TEXT_SIZE, x + w * shown, y + TEXT_SIZE))
        canvas.drawString(line, x + jitter[0], y + jitter[1], f, skia.Paint(AntiAlias=True, Color=to_color(MARKER_INK)))
        canvas.restore()


def draw_pen(canvas, frame, tip, angle, key="notebook.pen"):
    """A pen held with its tip at `tip`, pointing along `angle` degrees: a slim dark body, a pale point."""
    ink = Ink(canvas, frame, color=ROOM, width=3.0, prefix=key)
    canvas.save()
    canvas.translate(*tip)
    canvas.rotate(angle)
    box(ink, rounded_rect(-170, -9, -14, 9, 6), "body", fill=BG)
    ink.fill([(-14, -6), (0, -1.5), (0, 1.5), (-14, 6)], "point", color=MARKER_INK, wobble=0)
    canvas.restore()


def draw_writing_arm(canvas, frame, tip):
    """His stick arm from the bottom right, holding the pen with its tip at `tip`: the pen in line with it."""
    reach_to = (tip[0] + 420, 1500)                  # where his arm runs off the bottom of the picture
    angle = math.degrees(math.atan2(tip[1] - reach_to[1], tip[0] - reach_to[0]))
    hand = (tip[0] - 120 * math.cos(math.radians(angle)), tip[1] - 120 * math.sin(math.radians(angle)))
    draw_pen(canvas, frame, tip, angle)
    Ink(canvas, frame, color=INK, width=30.0, prefix="hero.closeup").line(reach_to, hand, "forearm", pin_ends=True,
                                                                          taper=0.0)


# -- shot 1: three lines ----------------------------------------------------------------------------------

PER_LETTER = 0.12
APPROACH = (0.4, 1.0)
WRITE = []                     # (start, end) of each line: a short pause between the first two, longer before the last
_t = APPROACH[1]
for _k, _pause in enumerate((0.0, 0.45, 0.85)):
    _t += _pause
    WRITE.append((_t, _t + PER_LETTER * len(LINES[_k])))
    _t = WRITE[-1][1]
LIFT = (WRITE[-1][1], WRITE[-1][1] + 0.4)

notebook_camera = Camera(zoom=Track((0, 1.0), (TICK_4, 1.04, "linear")), name="dayone2.notebook")


def pen_tip(t):
    """Where the pen's point is: in from the bottom right, along each line bobbing with the letters, across to
    the next, and lifted at the end."""
    start = (line_box(0)[0], line_box(0)[1] - 0.3 * TEXT_SIZE)
    if t < APPROACH[1]:
        return lerp((1500, 1250), start, progress(t, *APPROACH, "out"))
    for k, (a, b) in enumerate(WRITE):
        x, y, w = line_box(k)
        if t < a:          # across to this line
            px, py, pw = line_box(k - 1)
            return lerp((px + pw, py - 0.3 * TEXT_SIZE), (x, y - 0.3 * TEXT_SIZE), progress(t, WRITE[k - 1][1], a, "inout"))
        if t < b:
            u = progress(t, a, b, "linear")
            n = len(LINES[k]) + 1
            return (x + w * u + 0.05 * TEXT_SIZE * math.sin(2 * math.pi * n * u + 1.0),
                    y - 0.3 * TEXT_SIZE + 0.25 * TEXT_SIZE * math.sin(2 * math.pi * n * u))
    x, y, w = line_box(2)
    return lerp((x + w, y - 0.3 * TEXT_SIZE), (x + w + 40, y - 0.3 * TEXT_SIZE + 30), progress(t, *LIFT, "out"))


def shot_notebook(canvas, t, frame):
    with notebook_camera.view(canvas, t):
        draw_notebook(canvas, frame, [(line, progress(t, a, b, "linear")) for line, (a, b) in zip(LINES, WRITE)])
        if t >= APPROACH[0]:
            draw_writing_arm(canvas, frame, pen_tip(t))


# -- shot 3: Sam's chat ---------------------------------------------------------------------------------------

CHAT_BG, THEIRS, MINE, GREY_TEXT = (14, 16, 22), (52, 55, 64), (64, 112, 214), (130, 136, 150)
SAM = ["you coming tonight?", "haven't seen you in ages", "miss you man"]
# when, after the cut to the phone, each key is pressed: "hey", deleted, a wait, "hey" again
TYPING = [(1.0, "h"), (1.3, "e"), (1.6, "y"), (2.4, "<"), (2.6, "<"), (2.8, "<"), (3.8, "h"), (4.0, "e"), (4.2, "y")]
SEND, DELIVERED, PUT_DOWN = 4.7, 5.2, (6.2, 6.9)
phone_camera = Camera(zoom=Track((PHONE, 1.0), (TICK_5, 1.03, "linear")), name="dayone2.phone")


def typed(p):
    """What's in the box he types in, p seconds after the cut to the phone."""
    out = ""
    for at, key in TYPING:
        if p >= at:
            out = out[:-1] if key == "<" else out + key
    return "" if p >= SEND else out


def bubble(canvas, frame, s, x, y, colour, text_colour, side, key):
    """A message bubble: its top at y, against the left edge x (side "left") or the right edge x ("right")."""
    f = font(46, bold=False)
    w = f.measureText(s)
    x0 = x if side == "left" else x - w - 60
    box(Ink(canvas, frame, color=colour, width=2.0, prefix=key), rounded_rect(x0, y, x0 + w + 60, y + 84, 38), key,
        fill=colour)
    canvas.drawString(s, x0 + 30, y + 56, f, skia.Paint(AntiAlias=True, Color=to_color(text_colour)))


def draw_chat(canvas, frame, p, mine=None, sent=0.0, delivered=False, field="", cursor=True, label="Today 18:40",
              status="Delivered", reply=None, replied=0.0, reply_label="Today 7:12"):
    """Sam's chat on his screen. mine: his message, slid up into place as `sent` goes 0..1, with its time
    (`label`) above it and `status` under it once `delivered`. reply: Sam's answer, coming in as `replied` goes
    0..1: the chat scrolls up to make room for it (row 25)."""
    x0, y0, x1, y1 = SCREEN_RECT
    canvas.drawRect(skia.Rect(x0, y0, x1, y1), skia.Paint(Color=to_color(CHAT_BG)))
    canvas.save()
    if replied > 0:          # the chat scrolls up under the box he types in, to make room for the reply
        canvas.clipRect(skia.Rect(x0, y0, x1, 830))
        canvas.translate(0, -210 * replied)
    Ink(canvas, frame, color=(150, 160, 180), width=3.0, prefix="chat.avatar").circle((C[0], 190), 40, "avatar",
                                                                                      fill=(150, 160, 180))
    text(canvas, "S", C[0], 206, 46, (24, 28, 38))
    text(canvas, "Sam", C[0], 276, 40, (220, 224, 232), bold=False)
    Ink(canvas, frame, color=(40, 44, 54), width=2.0, prefix="chat.divider").line((x0, 300), (x1, 300), "d", taper=0.0)
    for k, message in enumerate(SAM):
        bubble(canvas, frame, message, x0 + 34, 330 + 100 * k, THEIRS, (225, 228, 236), "left", f"chat.sam{k}")
    if mine and sent > 0:
        text(canvas, label, C[0], 650, 32, GREY_TEXT, bold=False)
        canvas.saveLayerAlpha(None, int(255 * sent))
        bubble(canvas, frame, mine, x1 - 34, 680 + 150 * (1 - sent), MINE, (240, 244, 255), "right", "chat.mine")
        canvas.restore()
        if delivered:
            text(canvas, status, x1 - 40, 800, 30, GREY_TEXT, align="right", bold=False)
    if reply and replied > 0:
        text(canvas, reply_label, C[0], 870, 32, GREY_TEXT, bold=False)
        canvas.saveLayerAlpha(None, int(255 * replied))
        bubble(canvas, frame, reply, x0 + 34, 900 + 60 * (1 - replied), THEIRS, (225, 228, 236), "left", "chat.reply")
        canvas.restore()
    canvas.restore()
    # the box he types in, with a blinking cursor, and the send button once there's something to send
    edge = Ink(canvas, frame, color=(60, 64, 76), width=3.0, prefix="chat.field")
    box(edge, rounded_rect(x0 + 30, 840, x1 - 30, 910, 34), "field", fill=CHAT_BG)
    f = font(46, bold=False)
    canvas.drawString(field, x0 + 64, 890, f, skia.Paint(AntiAlias=True, Color=to_color((235, 238, 245))))
    if cursor and (p * 1.6) % 1 < 0.6:
        cx = x0 + 66 + f.measureText(field)
        canvas.drawRect(skia.Rect(cx, 852, cx + 4, 898), skia.Paint(Color=to_color((110, 150, 235))))
    if field:
        Ink(canvas, frame, color=MINE, width=2.0, prefix="chat.send").circle((x1 - 66, 875), 26, "send", fill=MINE)
        arrow = Ink(canvas, frame, color=(240, 244, 255), width=5.0, prefix="chat.arrow")
        arrow.line((x1 - 66, 888), (x1 - 66, 862), "up", taper=0.0)
        arrow.line((x1 - 78, 873), (x1 - 66, 862), "l", taper=0.0)
        arrow.line((x1 - 54, 873), (x1 - 66, 862), "r", taper=0.0)


def thumb(p):
    """Where the end of his right arm is: at the phone's edge, down over the keys for each tap, on the send
    button to send it."""
    edge = (C[0] + PW / 2 - 4, 840)
    keys = (C[0] + 90, 975)
    send = (SCREEN_RECT[2] - 66, 880)
    if p < TYPING[0][0] - 0.3:
        return edge
    if p < SEND - 0.25:
        tap = max([math.exp(-((p - at) / 0.06) ** 2) for at, _ in TYPING])
        return (keys[0] + 20 * math.sin(p * 5), keys[1] - 18 * tap)
    if p < SEND + 0.15:
        return lerp(keys, send, progress(p, SEND - 0.25, SEND, "inout"))
    return lerp(send, edge, progress(p, SEND + 0.15, SEND + 0.6, "inout"))


def shot_phone(canvas, t, frame):
    p = t - PHONE
    down = progress(p, *PUT_DOWN, "in")          # he puts it down: it drops away out of the picture
    with phone_camera.view(canvas, t):
        glow(canvas, C, 900, SCREEN, 0.3 * (1 - down))
        canvas.save()
        canvas.translate(0, 1100 * down)
        ink = Ink(canvas, frame, color=ROOM, width=9.0, prefix="quote.phone")
        box(ink, rounded_rect(C[0] - PW / 2, C[1] - PL / 2, C[0] + PW / 2, C[1] + PL / 2, 60), "phone", width=9.0)
        screen = rounded_rect(*SCREEN_RECT, 40)
        path = skia.Path()
        path.addPoly([skia.Point(*q) for q in screen], True)
        canvas.save()
        canvas.clipPath(path, doAntiAlias=True)
        draw_chat(canvas, frame, p, mine="hey", sent=progress(p, SEND, SEND + 0.2, "out"), delivered=p >= DELIVERED,
                  field=typed(p), cursor=p < SEND)
        canvas.restore()
        ink.stroke(screen, "screen", closed=True, width=4.0)
        arm = Ink(canvas, frame, color=INK, width=30.0, prefix="hero.closeup")
        arm.line((C[0] - 260, 1300), (C[0] - PW / 2 + 4, 860), "forearm.l", pin_ends=True, taper=0.0)
        arm.line((C[0] + 260, 1300), thumb(p), "forearm.r", pin_ends=True, taper=0.0)
        canvas.restore()


# -- the scene ------------------------------------------------------------------------------------------

ticks = Ticks([(TICK_4, 3), (TICK_5, 4)], done=3)


def draw(canvas, t, frame):
    if t < TICK_4:
        shot_notebook(canvas, t, frame)
    elif t < PHONE:
        ticks.draw(canvas, t, frame)
    elif t < TICK_5:
        shot_phone(canvas, t, frame)
    else:
        ticks.draw(canvas, t, frame)


bar = Discipline(start=3, fills=ticks.fills())  # +1 for each tick: five steps by the end of his first day


def overlay(canvas, t, frame):
    bar.draw(canvas, t, frame)


def scratch_sound():
    """A pen writing on paper, as long as needed. ElevenLabs gives scratching with gaps in it, so only the
    scratching is kept, joined up into one continuous stretch."""
    recording = sk.normalize(sk.eleven_sound("Close-up of a pen writing slowly on paper in a notebook, soft "
                                             "continuous scratching, no other sounds", 6.0, "pen_writing"))
    win = int(0.05 * sk.SR)
    loud = [i for i in range(0, len(recording) - win, win)
            if np.sqrt(np.mean(recording[i:i + win] ** 2)) > 10 ** (-40 / 20)]
    pieces = [sk.fade_edges(recording[i:i + win + int(0.01 * sk.SR)], 0.01, 0.01) for i in loud]
    scratch = np.zeros(len(pieces) * win + int(0.01 * sk.SR))
    for k, piece in enumerate(pieces):          # overlapping by a hundredth of a second, so there are no clicks
        scratch[k * win:k * win + len(piece)] += piece
    while len(scratch) < 6 * sk.SR:
        scratch = np.concatenate([scratch, scratch])
    return scratch


def soundtrack():
    mix = sk.Mix(DURATION)

    def effect(prompt, seconds, name):            # ElevenLabs effects, all brought to the same level first
        return sk.normalize(sk.eleven_sound(prompt, seconds, name))

    # the pen on paper, while each line is written
    scratch = scratch_sound()
    offset = 0.0
    for a, b in WRITE:
        part = scratch[int(offset * sk.SR):int((offset + b - a) * sk.SR)]
        mix.add(sk.fade_edges(part, 0.04, 0.08), at=a, gain_db=-17, pan=0.2, reverb=0.06)
        offset += b - a
    # the ticks
    grains = squeaks()
    g = rng("dayone2.squeak")
    for at in ticks.squeaks():
        mix.add(grains[g.integers(len(grains))], at=at, gain_db=-15, pan=-0.15, reverb=0.08)
    # the keys, the message going, the phone put down
    for at, key in TYPING:
        mix.add(sk.lowpass(sk.tick(key=("dayone2.key", at)), 3000), at=PHONE + at, gain_db=-24 if key == "<" else -22,
                reverb=0.04)
    mix.add(sk.lowpass(sk.tick(key="dayone2.sendkey"), 3000), at=PHONE + SEND - 0.02, gain_db=-22, reverb=0.04)
    mix.add(sk.whoosh(0.3, peak=0.4, low=900, high=5000, key="dayone2.sent"), at=PHONE + SEND, gain_db=-20, reverb=0.08)
    mix.add(sk.thud(0.3, key="dayone2.down"), at=PHONE + PUT_DOWN[1] - 0.05, gain_db=-20, reverb=0.08)
    bar.add_sounds(mix)
    return mix
