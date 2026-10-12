"""Film 1, row 13 of the story: grind 1, the first loop of the grind. About 10 seconds, three shots joined by
hard cuts, and a jump cut in the last. It follows row 12, where he crossed out TUESDAY and wrote WEDNESDAY.

 0-2.9 s     From above, the opening view: the clock already says 7:40 (he slept through the alarm). He lies
             in bed scrolling, the phone held up over his chest, its cold light on his tired face. One swipe.
             The first mess: a T-shirt and jeans on the floor.
 2.9-6.5 s   His phone's screen, close up: a reel, the smug man from the quote: MY FIRST / MILLION AT 22.
             The phone buzzes and Sam's message slides down over it: "haven't seen you in ages". It stays
             long enough to read; then the end of his stick arm flicks it away and swipes on to the next
             reel: a grinning man flexing, SIX-PACK / IN 30 DAYS.
 6.5-10.2 s  The board close up. No hesitation now: his arm comes up from the bottom right, takes the red
             marker and crosses out WEDNESDAY in one stroke (the empty discipline bar flickers red). A jump
             cut, closer: he's writing THURSDAY under it.
             The caption "*Tomorrow*." comes up as he takes the red marker and stays to the end.

Sound: the hum, the reels' muffled voices, a soft swipe, the phone's buzz, the markers, the bar's flicker.
"""
import math

import numpy as np
import skia

import scenes.new_goals as goals
from scenes.bedroom import HERO_X, HIP_Y, ROOM, box, draw_bed, draw_blanket, draw_mess, draw_nightstand, hero, rounded_rect
from scenes.discipline import Discipline
from scenes.door_wall import draw_board
from scenes.night import BANNER_FILL, DARK_TEXT, text
from scenes.scroll import CHEST, HOLD_ELBOWS, draw_body, draw_his_face, draw_phone, glow, light_on_face, reel_sounds
from scenes.the_board import CLOSE
from scenes.the_quote import BOX_TOP, C, GURU_FACE, PL, PW, SCREEN_RECT, TINT, WORD_SIZE, guru, pop
from scenes.tomorrow_again import BoardArm
from toolkit import (INK, SCREEN, Camera, Captions, Character, Face, Ink, Pose, Track, blink, clamp, lerp, progress,
                     to_color)
from toolkit import sound as sk
from toolkit.rng import noise
from toolkit.text import FADE, font

DURATION = 10.2
PEAK_DB = -1.3          # set so the hum matches the other scenes
TIME = "7:40"
REEL = 2.9             # cut to his phone's screen
BOARD_SHOT = 6.5       # cut to the board

# The board as it is now: his four new goals, MONDAY and TUESDAY crossed out, WEDNESDAY to cross out today.
BOARD = dict(wiped=goals.wiped(goals.DURATION), new_goals=goals.written(goals.DURATION))


def days(crossed=0.0, written=0.0):
    return [("MONDAY", 1.0, 1.0), ("TUESDAY", 1.0, 1.0), ("WEDNESDAY", 1.0, crossed), ("THURSDAY", written, 0.0)]


# -- shot 1: from above, scrolling at 7:40 ---------------------------------------------------------

SWIPE_1 = 1.2          # one swipe in bed
bed_camera = Camera(name="grind1.bed")


def swiping(t, at):
    """0..1: his thumb flicking, a moment around a swipe."""
    if at - 0.09 <= t < at + 0.2:
        return progress(t, at - 0.09, at, "out") * (1 - progress(t, at, at + 0.2, "inout"))
    return 0.0


def light_level(t, swipes, key="grind1.reel"):
    """The phone's light: flickering with the video, dipping as he swipes."""
    level = 0.85 * (1 + 0.12 * noise(t * 5, key))
    for s in swipes:
        if s - 0.06 <= t < s + 0.16:
            level *= 0.35 + 0.65 * progress(t, s + 0.02, s + 0.16, "out")
    return level


def draw_scrolling(canvas, frame, t, time, mess, swipe, level, buzz=0.0, key="grind1"):
    """From above, the opening view: the clock says `time` and he lies in bed scrolling, the phone held up
    over his chest, its cold light on his tired face. mess: what lies on the floor (see draw_mess). swipe:
    0..1, his thumb flicking. level: the phone's light. buzz: 0..1, the phone buzzing in his hands."""
    room = Ink(canvas, frame, color=ROOM, width=4.0, prefix="bedroom")
    draw_bed(room)
    draw_nightstand(room, canvas, frame, time=time, phone=False)
    draw_mess(room, mess)                 # after the nightstand: some of it lies on top

    b = 0.35 * math.sin(2 * math.pi * t / 4.2)
    pose = Pose(x=HERO_X, y=HIP_Y - 3 * b)
    phone_at = (CHEST[0], CHEST[1] - 3 * swipe)
    if buzz > 0:
        phone_at = (phone_at[0] + 2 * buzz * noise(t * 45, key, "buzz.x"), phone_at[1] + 2 * buzz * noise(t * 45, key, "buzz.y"))
    pose = pose.but(hand_l=(phone_at[0] - 29, phone_at[1]), hand_r=(phone_at[0] + 29, phone_at[1] - 16 * swipe))
    j = hero.skeleton(pose, frame)
    j.update(HOLD_ELBOWS)                 # elbows resting on the bed beside him, forearms up to the phone

    pen = draw_body(canvas, frame, j, ("legs", "spine", "head"), hero.head_r)
    draw_blanket(room, b)
    face = Face(eyes=0.42 * blink(t, "hero." + key, every=3.0, length=0.22), brows=0.9, mouth="frown",
                mouth_size=0.5, bags=True)
    draw_his_face(canvas, pen, j["head"], hero.head_r, face, 0.0, 0.0, 0.12)
    source = (phone_at[0], phone_at[1] - 40)
    glow(canvas, source, 260, TINT, 0.28 * level)
    near = clamp(1 - math.dist(source, j["head"]) / 330)
    light_on_face(canvas, j["head"], hero.head_r, source, TINT, 0.6 * level * near)
    draw_body(canvas, frame, j, ("arms",), hero.head_r)
    draw_phone(canvas, room, phone_at, 86, 62, 0, "back", level=level, tint=TINT)


def shot_bed(canvas, t, frame):
    with bed_camera.view(canvas, t):
        draw_scrolling(canvas, frame, t, TIME, ("clothes",), swiping(t, SWIPE_1), light_level(t, [SWIPE_1]))


# -- shot 2: his screen: a reel, Sam's message, flicked away -----------------------------------------

WORDS_A = ((REEL + 0.15, "MY FIRST"), (REEL + 0.4, "MILLION AT 22"))
BUZZ = REEL + 0.9      # the phone buzzes and Sam's message slides down...
BANNER_IN = 0.25
FLICK = REEL + 2.55    # ...he reads it (or doesn't), and his arm flicks it away...
SWIPE_2 = REEL + 3.05  # ...and swipes on to the next reel
WORDS_B = ((SWIPE_2 + 0.15, "SIX-PACK"), (SWIPE_2 + 0.4, "IN 30 DAYS"))
MESSAGE = "haven't seen you in ages"

reel_camera = Camera(zoom=Track((REEL, 1.0), (BOARD_SHOT, 1.04, "linear")), name="grind1.reel")
flexer = Character("flexer", height=600)
FLEX_FACE = Face(eyes=0.9, brows=-0.2, mouth="smile", mouth_size=1.0)


def caption_words(canvas, t, words):
    """The reel's big words, each line popping up under the video."""
    f = font(WORD_SIZE)
    for i, (at, line) in enumerate(words):
        alpha, scale = pop(t, at)
        if alpha <= 0:
            continue
        w = f.measureText(line)
        y = 712 + i * WORD_SIZE * 1.15
        canvas.save()
        canvas.translate(C[0], y - WORD_SIZE * 0.35)
        canvas.scale(scale, scale)
        canvas.translate(-C[0], -(y - WORD_SIZE * 0.35))
        canvas.drawString(line, C[0] - w / 2, y + 6, f, skia.Paint(
            AntiAlias=True, Color=to_color((0, 0, 0, int(200 * alpha))),
            MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, WORD_SIZE * 0.08)))
        canvas.drawString(line, C[0] - w / 2, y, f, skia.Paint(AntiAlias=True,
                                                              Color=to_color((240, 242, 248, int(255 * alpha)))))
        canvas.restore()


def reel_guru(canvas, frame, t):
    """Reel A: the smug man in the suit from the quote, selling his first million."""
    sway = 6 * math.sin(2 * math.pi * t / 1.7)
    pose = Pose(x=C[0] + sway, y=610 + 3 * math.sin(2 * math.pi * t / 0.85), face=GURU_FACE,
                head_tilt=2.5 * math.sin(2 * math.pi * t / 1.7), ground=None)
    sh = guru.joints(pose)["shoulder"]
    j = guru.draw(canvas, frame, pose.but(hand_l=(sh[0] - 8, sh[1] + 120), hand_r=(sh[0] + 8, sh[1] + 120)))
    pen = Ink(canvas, frame, color=INK, width=6.0, prefix="guru.suit")
    s = j["shoulder"]       # his suit: a tie and the jacket's lapels
    pen.stroke([(s[0], s[1] + 8), (s[0] - 10, s[1] + 60), (s[0], s[1] + 125), (s[0] + 10, s[1] + 60)], "tie",
               closed=True)
    pen.line((s[0] - 60, s[1] + 6), (s[0] - 14, s[1] + 140), "lapel.l")
    pen.line((s[0] + 60, s[1] + 6), (s[0] + 14, s[1] + 140), "lapel.r")


def reel_flexer(canvas, frame, t):
    """Reel B: a grinning man flexing both arms, pumping them to the beat."""
    pump = 0.5 + 0.5 * math.sin(2 * math.pi * t / 0.48)
    pose = Pose(x=C[0], y=640 + 4 * pump, face=FLEX_FACE, ground=None)
    sh = flexer.joints(pose)["shoulder"]
    lift, out = 80 + 15 * pump, 100 - 5 * pump      # upper arms out to the sides, fists up beside his head
    flexer.draw(canvas, frame, pose.but(hand_l=(sh[0] - out, sh[1] - lift), hand_r=(sh[0] + out, sh[1] - lift),
                                        bend_hand_l=-1, bend_hand_r=1))


def draw_reel(canvas, frame, t, which, words, shift=0.0):
    """One reel on the screen, moved up by `shift` pixels as it's swiped away (or in)."""
    x0, y0, x1, y1 = SCREEN_RECT
    canvas.save()
    canvas.translate(0, shift)
    shade = skia.GradientShader.MakeLinear([skia.Point(0, 132), skia.Point(0, 948)],
                                           [to_color((46, 58, 88) if which == "guru" else (70, 52, 46)),
                                            to_color((16, 20, 32))])
    canvas.drawRect(skia.Rect(x0, y0, x1, y1), skia.Paint(Shader=shade))
    (reel_guru if which == "guru" else reel_flexer)(canvas, frame, t)
    canvas.drawRect(skia.Rect(x0, BOX_TOP, x1, y1), skia.Paint(Color=to_color((12, 14, 22, 235))))
    caption_words(canvas, t, words)
    canvas.restore()


BANNER_X0, BANNER_X1, BANNER_Y = SCREEN_RECT[0] + 28, SCREEN_RECT[2] - 28, 168
BANNER_H = 200


def banner(t):
    """Sam's message: (how far it has slid in 0..1, how far it has been flicked away 0..1)."""
    return progress(t, BUZZ, BUZZ + BANNER_IN, "out"), progress(t, FLICK, FLICK + 0.22, "in")


def draw_banner(canvas, frame, t):
    slid, gone = banner(t)
    if slid <= 0 or gone >= 1:
        return
    canvas.saveLayerAlpha(None, int(255 * slid * (1 - gone)))
    canvas.translate(0, -60 * (1 - slid) - 420 * gone)
    ink = Ink(canvas, frame, color=BANNER_FILL, width=3.0, prefix="grind1.banner")
    b0, b1, by0 = BANNER_X0, BANNER_X1, BANNER_Y
    box(ink, rounded_rect(b0, by0, b1, by0 + BANNER_H, 38), "banner", fill=BANNER_FILL)
    Ink(canvas, frame, color=DARK_TEXT, width=4.0, prefix="grind1.avatar").circle(
        (b0 + 74, by0 + 100), 44, "avatar", fill=(150, 160, 180))
    text(canvas, "S", b0 + 74, by0 + 119, 52, DARK_TEXT)
    text(canvas, "Sam", b0 + 146, by0 + 84, 60, DARK_TEXT, align="left")
    text(canvas, "now", b1 - 28, by0 + 78, 38, (90, 98, 115), align="right", bold=False)
    text(canvas, MESSAGE, b0 + 146, by0 + 160, 52, DARK_TEXT, align="left")
    canvas.restore()


# Where the end of his right arm is: holding the phone's edge, then up onto the message to flick it away,
# down onto the reel to swipe it, and back to the edge.
EDGE_R = (C[0] + PW / 2 - 4, 810)
TOUCH = (1318, BANNER_Y + 128)        # the message's right end, clear of its words
ARM_R = Track((FLICK - 0.4, EDGE_R), (FLICK, TOUCH, "inout"), (FLICK + 0.16, (1300, BANNER_Y - 60), "out"),
              (SWIPE_2 - 0.12, (1200, 760), "inout"), (SWIPE_2 + 0.12, (1190, 430), "out"),
              (SWIPE_2 + 0.5, EDGE_R, "inout"))


def shot_reel(canvas, t, frame):
    with reel_camera.view(canvas, t):
        level = light_level(t, [SWIPE_2])
        glow(canvas, C, 900, SCREEN, 0.35 * level)
        buzz = 2.5 * (1.0 if BUZZ <= t < BUZZ + 0.35 else 0.0)        # it buzzes in his hands
        canvas.save()
        canvas.translate(buzz * noise(t * 45, "grind1.buzz", "x"), buzz * noise(t * 45, "grind1.buzz", "y"))
        ink = Ink(canvas, frame, color=ROOM, width=9.0, prefix="quote.phone")
        body = rounded_rect(C[0] - PW / 2, C[1] - PL / 2, C[0] + PW / 2, C[1] + PL / 2, 60)
        box(ink, body, "phone", width=9.0)
        screen = rounded_rect(*SCREEN_RECT, 40)
        path = skia.Path()
        path.addPoly([skia.Point(*p) for p in screen], True)
        canvas.save()
        canvas.clipPath(path, doAntiAlias=True)
        height = SCREEN_RECT[3] - SCREEN_RECT[1]
        u = progress(t, SWIPE_2 - 0.02, SWIPE_2 + 0.22, "inout")      # the swipe: A slides up, B comes up after it
        if u < 1:
            draw_reel(canvas, frame, t, "guru", WORDS_A, -height * u)
        if u > 0:
            draw_reel(canvas, frame, t, "flexer", WORDS_B, height * (1 - u))
        draw_banner(canvas, frame, t)
        canvas.restore()
        ink.stroke(screen, "screen", closed=True, width=4.0)
        canvas.restore()
        # his stick arms coming up from his chest below (he lies under the phone); the right one leaves the
        # phone's edge to flick and swipe
        arm = Ink(canvas, frame, color=INK, width=30.0, prefix="hero.closeup")
        arm.line((C[0] - 260, 1300), (C[0] - PW / 2 + 4, 840), "forearm.l", pin_ends=True, taper=0.0)
        arm.line((C[0] + 260, 1300), ARM_R(t), "forearm.r", pin_ends=True, taper=0.0)


# -- shot 3: the board, close up, no hesitation now -----------------------------------------------------
# The board shot runs in its own time ("story time"), and the jump cut skips the moment he puts the red marker
# back and takes the pale one: from JUMP on, the picture shows story time SKIP seconds later.

B = BOARD_SHOT
arm = BoardArm(2, "WEDNESDAY", "THURSDAY", arm_in=B + 0.1, grab_red=B + 0.65, hover=None, cross=(B + 1.25, B + 1.65),
               put_red=B + 2.35, grab_pale=B + 2.65, write=(B + 3.15, B + 4.6), put_pale=B + 5.3, arm_out=B + 5.7,
               lift=0.25)
JUMP = B + 2.0         # the jump cut, as the red marker leaves the board
SKIP = 1.2             # story time skipped: after it, he's just begun writing THURSDAY

board_camera = Camera(zoom=Track((B, 1.0), (JUMP, 1.02, "linear")), name="grind1.board")
# after the jump cut: closer, on the column of start days
jump_camera = Camera(x=Track((JUMP, 1180), (DURATION, 1190, "linear")), y=Track((JUMP, 512), (DURATION, 508, "linear")),
                     zoom=Track((JUMP, 1.42), (DURATION, 1.46, "linear")), name="grind1.jump")


def story(t):
    return t + SKIP if t >= JUMP else t


def shot_board(canvas, t, frame):
    s = story(t)
    with (board_camera if t < JUMP else jump_camera).view(canvas, t):
        draw_board(canvas, frame, CLOSE, days(arm.crossed(s), arm.writing(s)), on_tray=arm.on_tray(s), **BOARD)
        arm.draw(canvas, frame, s)


# -- the scene -------------------------------------------------------------------------------------


def draw(canvas, t, frame):
    if t < REEL:
        shot_bed(canvas, t, frame)
    elif t < BOARD_SHOT:
        shot_reel(canvas, t, frame)
    else:
        shot_board(canvas, t, frame)


bar = Discipline(flickers=[arm.cross[1] - 0.1])  # empty: a red flicker as he crosses out WEDNESDAY
captions = Captions([(arm.grab_red, DURATION + FADE, "*Tomorrow*.")])


def overlay(canvas, t, frame):
    bar.draw(canvas, t, frame)
    captions.draw(canvas, t)


def soundtrack():
    mix = sk.Mix(DURATION)
    mix.add(sk.pad(["A1", "E2"], DURATION, attack=0.4, release=1.0, brightness=0.05, key="hum"),
            at=0, gain_db=-17, reverb=0.2)

    # the reels, muffled as in scene 2: the Bugatti man until his swipe in bed, then the first-million man
    # (the reel we see), then the six-pack woman after the last swipe; quiet from above, nearer in the close-up
    clips = reel_sounds()
    adam, laura, liam = clips
    even = {id(adam): 3.4, id(laura): 0.4, id(liam): 3.3}    # as in scene 2: makes the three voices equally loud
    for clip, a, b, offset, gain in ((liam, 0.0, SWIPE_1, 4.0, -10), (adam, SWIPE_1, REEL, 0.0, -10),
                                     (adam, REEL, SWIPE_2, REEL - SWIPE_1, -9), (laura, SWIPE_2, BOARD_SHOT, 0.0, -9)):
        part = clip[int(offset * sk.SR):int((offset + b - a) * sk.SR)]
        mix.add(sk.fade_edges(part, 0.004, 0.01), at=a, gain_db=gain + even[id(clip)], pan=0.1, reverb=0.05)
    for at in (SWIPE_1, SWIPE_2):
        mix.add(sk.lowpass(sk.tick(key=("grind1.swipe", at)), 2500), at=at - 0.02, gain_db=-24, reverb=0.05)
    mix.add(sk.whoosh(0.25, peak=0.6, low=200, high=1600, key="grind1.flick"), at=FLICK - 0.05, gain_db=-26)

    def effect(prompt, seconds, name):            # ElevenLabs effects, all brought to the same level first
        return sk.normalize(sk.eleven_sound(prompt, seconds, name))

    buzz = effect("A smartphone on a wooden nightstand vibrating with a new text message, a short double buzz, "
                  "close up, in a quiet room", 1.5, "phone_buzz")
    mix.add(sk.fade_edges(sk.lowpass(buzz[int(0.05 * sk.SR):int(0.4 * sk.SR)], 1800), 0.01, 0.04), at=BUZZ,
            gain_db=-16, reverb=0.06)          # one buzz, softer in his hands than on the wood

    # the board: no pause now; the jump cut skips the clicks of putting one marker back and taking the other
    def board_time(s):
        """When something at story time s is heard (None if the jump cut skips it)."""
        if s < JUMP:
            return s
        return s - SKIP if s - SKIP >= JUMP else None

    mix.add(sk.whoosh(0.4, peak=0.6, low=150, high=700, key="grind1.arm"), at=arm.arm_in, gain_db=-24, reverb=0.1)
    tray = effect("A plastic marker pen put down on a whiteboard's metal tray, one small light click", 0.5,
                  "marker_tray")
    mix.add(tray, at=arm.grab_red - 0.2, gain_db=-20, pan=0.2, reverb=0.08)
    cross = effect("Close-up of one quick squeaky stroke of a dry-erase marker across a whiteboard, "
                   "crossing out a word", 0.8, "marker_cross")
    a, b = arm.cross
    mix.add(sk.fade_edges(cross[:int((b - a + 0.08) * sk.SR)], 0.005, 0.06), at=a, gain_db=-15, pan=0.2, reverb=0.08)
    write = effect("Close-up of someone slowly writing one word on a whiteboard with a dry-erase marker, "
                   "slow squeaky strokes", 2.0, "marker_write")
    a, b = arm.write
    shown = JUMP + SKIP - a                       # he's this far into writing when the jump cut shows him
    mix.add(sk.fade_edges(write[int(shown * sk.SR):int((b - a + 0.1) * sk.SR)], 0.01, 0.08), at=board_time(a + shown),
            gain_db=-14, pan=0.2, reverb=0.08)
    bar.add_sounds(mix)
    return mix
