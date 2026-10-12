"""Film 1, row 12 of the story: tomorrow again. About 13 seconds, two shots joined by a hard cut.
It follows row 11, where he ran out of breath on the street and watched the joggers go.

 0-4.6 s    From the side, the wall by the door (as in the board scene). He stands in the open doorway,
            the cold early light behind him, back from the run: out of breath, gasping, head hanging. He
            steps in, two heavy steps to the board, and the door swings shut behind him; the light goes.
            He lifts his head to the board (his four new goals; START: MONDAY crossed out, TUESDAY) and sags.
 4.6-13.1 s The board close up. His stick arm comes up from the bottom right (he stands right of the board,
            between it and the door), takes the red marker, hovers over TUESDAY and crosses it out in one
            heavy stroke: the discipline bar drains to empty with a red flash. He puts the marker back,
            takes the pale one and slowly writes WEDNESDAY under it.
            The caption "*Tomorrow*." comes up as he takes the red marker and stays to the end.

Sound: the hum, the street outside until the door shuts, his gasping and steps, the door, the markers
on the tray and on the board, and the bar draining.
"""
import math

import numpy as np

import scenes.new_goals as goals
from scenes.discipline import Discipline
from scenes.door_wall import DOOR, GROUND, cross_line, day_box, draw_board, draw_marker, draw_wall, hero
from scenes.new_goals import Walk
from scenes.the_board import ARM, BOARD_H, CLOSE, GRIP, LONG, on_tray
from toolkit import INK, Camera, Captions, Face, Ink, Track, blink, clamp, lerp, progress, reach
from toolkit import sound as sk
from toolkit.text import FADE

DURATION = 13.1
PEAK_DB = -7.3          # set so the hum matches the other scenes

# The board as he left it in row 10: the huge goals wiped, his four new goals written.
BOARD = dict(wiped=goals.wiped(goals.DURATION), new_goals=goals.written(goals.DURATION))


def days(crossed=0.0, written=0.0):
    return [("MONDAY", 1.0, 1.0), ("TUESDAY", 1.0, crossed), ("WEDNESDAY", written, 0.0)]


# -- shot 1: back through the door ---------------------------------------------------------------------

IN_DOOR = 1440         # where his hips are, standing in the doorway
STOP_AT = 1290         # by the board's right edge, between it and the door


class Trudge(Walk):
    """A heavy, tired walk: slower steps that barely lift."""
    STEP, SWING, LIFT, SLOW = 0.55, 0.72, 7, 0.6


walk_in = Trudge(0.9, IN_DOOR, STOP_AT, 120, first="foot_l", ramp=0.4,
                 feet0={"foot_l": IN_DOOR - 28, "foot_r": IN_DOOR + 30}, facing=-1)
DOOR_SHUT = (1.8, 2.7)                                   # the door swings shut behind him
LOOK = (walk_in.stop + 0.15, walk_in.stop + 0.7)         # he lifts his head to the board...
SAG = (LOOK[1] + 0.45, LOOK[1] + 1.0)                    # ...and sags
CLOSE_UP = round(SAG[1] + 0.3, 2)                        # cut to the board

wide_camera = Camera(x=Track((0, 1170), (CLOSE_UP, 1150, "linear")), zoom=Track((0, 1.12), (CLOSE_UP, 1.16, "linear")),
                     name="again.wide")


def _breaths():
    """When each breath starts: still heavy from the run, slowly calming."""
    out, t = [], -0.3
    while t < DURATION + 2:
        out.append(t)
        t += lerp(0.95, 1.35, clamp(t / 5))
    return out


BREATHS = _breaths()


def breath(t):
    """How far through the current breath (0..1), and its number."""
    n = int(np.searchsorted(BREATHS, t, side="right")) - 1
    return (t - BREATHS[n]) / (BREATHS[n + 1] - BREATHS[n]), n


def his_face(t):
    u, _ = breath(t)
    look = progress(t, *LOOK, "inout")
    sag = progress(t, *SAG, "inout")
    gasp = (0.35 + 0.3 * math.sin(math.pi * u)) * (1 - 0.6 * look)
    eyes = lerp(0.35, 0.5, look) * blink(t, "hero.again", every=2.7)
    if sag > 0.5:
        return Face(eyes=lerp(0.5, 0.42, sag) * blink(t, "hero.again", every=2.7), brows=0.9, mouth="frown",
                    mouth_size=0.55, bags=True)
    return Face(eyes=eyes, brows=0.9, mouth="open", mouth_size=gasp, bags=True)


def his_pose(t):
    u, _ = breath(t)
    look = progress(t, *LOOK, "inout")
    sag = progress(t, *SAG, "inout")
    heave = math.sin(2 * math.pi * u) * (1 - 0.4 * look)
    # head hanging as he comes in, lifted to the board, then dropping a little as he sags
    tilt = lerp(26, -12, look) + 14 * sag
    lean = lerp(9, 3, look) + 4 * sag + 1.5 * heave
    pose = walk_in.pose(t, his_face(t), lean=lean, head_tilt=tilt)
    # his breathing only ever lowers his hips from where the walk puts them (higher, his feet would be out of reach)
    return pose.but(y=pose.y + 1.25 * (1 + heave) + 5 * sag)


def shot_wide(canvas, t, frame):
    with wide_camera.view(canvas, t):
        shut = progress(t, *DOOR_SHUT, "out")
        draw_wall(canvas, frame, days(), door_open=0.85 * (1 - shut), **BOARD)
        hero.draw(canvas, frame, his_pose(t))


# -- shot 2: the board close up --------------------------------------------------------------------

close_camera = Camera(zoom=Track((CLOSE_UP, 1.0), (DURATION, 1.03, "linear")), name="again.close")
BODY = (2400, 1370)    # roughly where his shoulder is, below the bottom right of the picture
BEND = -1              # his elbow hangs down, below the picture (not up beside the board)

ARM_IN = CLOSE_UP + 0.5                         # after a moment to see the board, his arm rises slowly...
GRAB_RED = ARM_IN + 0.75                        # ...takes the red marker
HOVER = GRAB_RED + 0.85                         # holds it by TUESDAY for a moment...
CROSS = (HOVER + 0.45, HOVER + 1.05)            # ...then crosses it out in one heavy stroke
PUT_RED = CROSS[1] + 0.9                        # puts it back
GRAB_PALE = PUT_RED + 0.3                       # takes the pale one
WRITE = (GRAB_PALE + 0.7, GRAB_PALE + 2.55)     # slowly writes WEDNESDAY
PUT_PALE = WRITE[1] + 0.85                      # puts it back
ARM_OUT = PUT_PALE + 0.45                       # and his arm drops away

captions = Captions([(GRAB_RED, DURATION + FADE, "*Tomorrow*.")])


def shoulder_for(hand):
    """His shoulder, below the bottom right of the picture (he stands right of the board, as in the wide
    shot); his body leans a little toward where his hand goes."""
    return (BODY[0] + 0.3 * (hand[0] - 1300), BODY[1] + 0.3 * (hand[1] - 600))


def forearm_angle(hand):
    shoulder = shoulder_for(hand)
    elbow, hand, _ = reach(shoulder, hand, *ARM, BEND)
    return math.degrees(math.atan2(hand[1] - elbow[1], hand[0] - elbow[0]))


def along(point, angle, length):
    a = math.radians(angle)
    return (point[0] + length * math.cos(a), point[1] + length * math.sin(a))


def hand_for_tip(tip):
    """Where his hand is when it holds a marker with its tip at `tip`, the marker in line with his forearm."""
    angle = forearm_angle(along(tip, forearm_angle(tip), -GRIP * LONG))
    for _ in range(4):
        angle = forearm_angle(along(tip, angle, -GRIP * LONG))
    return along(tip, angle, -GRIP * LONG), angle


def grip_on_tray(colour):
    """Where his hand takes a marker lying on the tray: by its cap end."""
    tip = on_tray(colour)
    return (tip[0] - GRIP * LONG, tip[1])


def lifted(colour):
    """His hand just after picking a marker up, the marker turned in line with his forearm: (hand, angle, tip)."""
    g = grip_on_tray(colour)
    hand = (g[0] + 15, g[1] - 45)
    angle = forearm_angle(hand)
    return hand, angle, along(hand, angle, GRIP * LONG)


RISE_FROM = (1300, 1200)   # his hand rises from just below the picture...
DROP_TO = (1480, 1200)     # ...and drops away there at the end


class BoardArm:
    """His arm at the board close up, from the bottom right (he stands right of the board, between it and the
    door): it takes the red marker, crosses out start day number `n` (0 = MONDAY), puts the marker back, takes
    the pale one and writes the next day under it. He picks each marker up by its cap end and turns it in his
    hand. hover: when the red marker stops by the day before the stroke (None: no pause, straight into it)."""

    def __init__(self, n, crossed, written, arm_in, grab_red, hover, cross, put_red, grab_pale, write, put_pale,
                 arm_out, lift=0.3):
        self.arm_in, self.grab_red, self.cross, self.put_red = arm_in, grab_red, cross, put_red
        self.grab_pale, self.write, self.put_pale, self.arm_out, self.lift = grab_pale, write, put_pale, arm_out, lift
        self.a, self.b = cross_line(CLOSE, n, crossed)
        self.wx, self.wy, self.ww, self.wpx = day_box(CLOSE, n + 1, written)
        self.letters = len(written) + 2           # the pen bobs up and down about once a letter
        start = (self.wx + 0.02 * self.wpx, self.wy - 0.4 * self.wpx)
        red_up, pale_up = lifted("red")[2], lifted("pale")[2]
        keys = [(grab_red + lift, red_up)]
        if hover is not None:
            keys.append((hover, (self.a[0] - 14, self.a[1] - 10), "inout"))
        keys += [(cross[0], self.a, "inout"), (cross[1], self.b, "inout"), (put_red - lift, red_up, "inout")]
        self.red_tip = Track(*keys)                # where the red marker's tip goes while he holds it
        self.pale_to = Track((grab_pale + lift, pale_up), (write[0], start, "inout"))
        self.pale_back = Track((write[1], (self.wx + self.ww, start[1])), (put_pale - lift, pale_up, "inout"))
        self.start = start

    def crossed(self, t):
        return progress(t, *self.cross)

    def writing(self, t):
        """0..1: how much of the new day is written."""
        return progress(t, *self.write, "linear")

    def pale_tip(self, t):
        if t < self.write[0]:
            return self.pale_to(t)
        if t < self.write[1]:          # writing: along the word, the pen bobbing up and down with the letters
            u = self.writing(t)
            n = self.letters
            return (self.wx + self.ww * u + 0.06 * self.wpx * math.sin(2 * math.pi * n * u + 1.0),
                    self.start[1] + 0.3 * self.wpx * math.sin(2 * math.pi * n * u))
        return self.pale_back(t)

    def held(self, t):
        if self.grab_red <= t < self.put_red:
            return "red"
        if self.grab_pale <= t < self.put_pale:
            return "pale"
        return None

    def at(self, t):
        """(hand, marker in hand or None, its tip, its angle) at time t."""
        colour = self.held(t)
        if colour is None:      # empty-handed: up from below to the red marker, across to the pale one, away
            if t < self.grab_red:
                u = progress(t, self.arm_in, self.grab_red, "inout")
                return lerp(RISE_FROM, grip_on_tray("red"), u), None, None, 0.0
            if t < self.grab_pale:
                u = progress(t, self.put_red, self.grab_pale, "inout")
                return lerp(grip_on_tray("red"), grip_on_tray("pale"), u), None, None, 0.0
            return lerp(grip_on_tray("pale"), DROP_TO, progress(t, self.put_pale, self.arm_out, "in")), None, None, 0.0
        grab, put = (self.grab_red, self.put_red) if colour == "red" else (self.grab_pale, self.put_pale)
        up_hand, up_angle, _ = lifted(colour)
        if t < grab + self.lift or t >= put - self.lift:      # picking it up / putting it down: it turns in his hand
            if t < grab + self.lift:
                u = progress(t, grab, grab + self.lift, "inout")
            else:
                u = 1 - progress(t, put - self.lift, put, "inout")
            hand = lerp(grip_on_tray(colour), up_hand, u)
            angle = lerp(0.0, up_angle, u)
            return hand, colour, along(hand, angle, GRIP * LONG), angle
        tip = self.red_tip(t) if colour == "red" else self.pale_tip(t)
        hand, angle = hand_for_tip(tip)
        return hand, colour, tip, angle

    def on_tray(self, t):
        return [c for c in ("red", "pale") if c != self.held(t)]

    def draw(self, canvas, frame, t):
        """The marker in his hand and his arm (drawn over the board)."""
        if not self.arm_in <= t < self.arm_out:
            return
        hand, colour, tip, angle = self.at(t)
        shoulder = shoulder_for(hand)
        elbow, hand, _ = reach(shoulder, hand, *ARM, BEND)
        if colour:
            draw_marker(canvas, frame, tip, angle, BOARD_H, colour)
        pen = Ink(canvas, frame, color=INK, width=30.0, prefix="hero.closeup")
        beyond = (shoulder[0] + 0.6 * (shoulder[0] - elbow[0]), shoulder[1] + 0.6 * (shoulder[1] - elbow[1]))
        pen.line(beyond, elbow, "upper_arm", pin_ends=True, taper=0.0)     # runs on off screen
        pen.line(elbow, hand, "forearm", pin_ends=True, taper=0.1)


arm = BoardArm(1, "TUESDAY", "WEDNESDAY", ARM_IN, GRAB_RED, HOVER, CROSS, PUT_RED, GRAB_PALE, WRITE, PUT_PALE,
               ARM_OUT)


def shot_close(canvas, t, frame):
    with close_camera.view(canvas, t):
        draw_board(canvas, frame, CLOSE, days(arm.crossed(t), arm.writing(t)), on_tray=arm.on_tray(t), **BOARD)
        arm.draw(canvas, frame, t)


# -- the scene -------------------------------------------------------------------------------------


def draw(canvas, t, frame):
    if t < CLOSE_UP:
        shot_wide(canvas, t, frame)
    else:
        shot_close(canvas, t, frame)


bar = Discipline(start=2, drains=[CROSS[1] - 0.1])  # he quits: it drains to empty with a red flash


def overlay(canvas, t, frame):
    bar.draw(canvas, t, frame)
    captions.draw(canvas, t)


def soundtrack():
    mix = sk.Mix(DURATION)
    mix.add(sk.pad(["A1", "E2"], DURATION, attack=0.4, release=1.0, brightness=0.05, key="hum"),
            at=0, gain_db=-17, reverb=0.2)

    def effect(prompt, seconds, name):            # ElevenLabs effects, all brought to the same level first
        return sk.normalize(sk.eleven_sound(prompt, seconds, name))

    # the street outside, through the open door, cut off as it shuts
    street = effect("A quiet city street just before sunrise: distant traffic, a faint cold wind, no voices, "
                    "no birds", 17.0, "street_dawn")
    gone = np.ones(len(street))
    a, b = int(DOOR_SHUT[0] * sk.SR), int(DOOR_SHUT[1] * sk.SR)
    gone[a:b] = np.linspace(1, 0.15, b - a) ** 2
    gone[b:] = 0
    mix.add(sk.fade_edges(street * gone, 0.05, 0.05), at=0, gain_db=-29, pan=0.4)
    shut = effect("An apartment door swinging shut by itself and latching with a soft click, indoors, close up",
                  1.5, "door_shut")
    mix.add(sk.fade_edges(shut, 0.005, 0.1), at=DOOR_SHUT[1] - 0.6, gain_db=-14, pan=0.4, reverb=0.12)
    for n, (lift, land, foot, x0, x1) in enumerate(walk_in.steps):          # his heavy steps
        if land < CLOSE_UP:
            mix.add(sk.footstep(n, weight=0.6, key="again.step"), at=land, gain_db=-12, pan=(x1 - 960) / 1400,
                    reverb=0.12)
    # His gasping: single gasps cut out of the ElevenLabs recording (as in row 11), one on each breath out,
    # calming as the scene goes on and quieter in the close-up.
    from scipy.signal import find_peaks
    gasp = effect("A man gasping and panting heavily for breath after an all-out sprint, bent over, close up, "
                  "no other sounds", 10.0, "gasping")
    win = int(0.02 * sk.SR)
    env = np.sqrt(np.convolve(gasp ** 2, np.ones(win) / win, mode="same"))
    peaks, _ = find_peaks(env, height=0.3 * env.max(), distance=int(0.5 * sk.SR))
    grains = [sk.fade_edges(sk.normalize(gasp[max(0, p - int(0.25 * sk.SR)):p + int(0.45 * sk.SR)]), 0.03, 0.15)
              for p in peaks]
    for k, (start, nxt) in enumerate(zip(BREATHS[:-1], BREATHS[1:])):
        at_ = start + 0.35 * (nxt - start)
        if 0 <= at_ < DURATION - 0.5:
            calmer = -9 * clamp(at_ / 8) - (4 if at_ >= CLOSE_UP else 0)
            mix.add(grains[(k + 3) % len(grains)], at=at_ - 0.25, gain_db=-12 + calmer, reverb=0.08)

    mix.add(sk.whoosh(0.5, peak=0.6, low=150, high=700, key="again.arm"), at=ARM_IN, gain_db=-24, reverb=0.1)
    tray = effect("A plastic marker pen put down on a whiteboard's metal tray, one small light click", 0.5,
                  "marker_tray")
    for i, at_ in enumerate((GRAB_RED, PUT_RED, GRAB_PALE, PUT_PALE)):
        mix.add(tray, at=at_ - 0.2, gain_db=-20 - 2 * (i % 2), pan=0.2, reverb=0.08)
    cross = effect("Close-up of one quick squeaky stroke of a dry-erase marker across a whiteboard, "
                   "crossing out a word", 0.8, "marker_cross")
    mix.add(sk.fade_edges(cross[:int((CROSS[1] - CROSS[0] + 0.08) * sk.SR)], 0.005, 0.06), at=CROSS[0],
            gain_db=-15, pan=0.2, reverb=0.08)
    write = effect("Close-up of someone slowly writing one word on a whiteboard with a dry-erase marker, "
                   "slow squeaky strokes", 2.0, "marker_write")
    mix.add(sk.fade_edges(write[:int((WRITE[1] - WRITE[0] + 0.1) * sk.SR)], 0.005, 0.08), at=WRITE[0],
            gain_db=-14, pan=0.2, reverb=0.08)
    bar.add_sounds(mix)
    return mix
