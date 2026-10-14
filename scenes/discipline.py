"""Film 1's discipline bar: a hand-drawn bar labelled DISCIPLINE in the top black bar, in every scene.

It fills only when he actually does something he set out to do, one equal step per action, sliding up
smoothly. It drains to empty with a red flash when he quits ("I'll start tomorrow"); when it's already
empty, quitting only makes it flicker red. It turns green only as its last step fills, at the end, with a warm chord. The rules,
scene by scene, are in stories/tomorrow.md; the look was picked from sheets/discipline_options.png.

Each scene says where its bar starts and what happens to it, and draws it in overlay(), after the film
finish (the bar sits in the black bar, so it isn't moved by the camera):

    bar = Discipline(start=1, fills=[3.35])       # 1 step full when the scene starts, +1 at 3.35 s
    bar = Discipline(flickers=[6.0])               # empty, a red flicker at 6 s
    bar = Discipline(start=2, drains=[5.0])        # drains to empty with a red flash at 5 s
    bar = Discipline(start=18, shakes=[(9.6, 12.6)])  # trembling (with a low rattle) from 9.6 s to 12.6 s

    def overlay(canvas, t, frame):
        bar.draw(canvas, t, frame)

It has its own sounds, or nobody notices it change: a tone rising with the bar as it fills, ending on a bright
ping, and a buzzy tone falling away as it drains, like a machine switching off (also played when it
flickers). Add them to a scene's soundtrack with `bar.add_sounds(mix)`. Picked from films/bar_sound_options.mp4.
"""
import numpy as np
import skia

from toolkit import BAR, GREEN, INK, RED, Ink, progress, to_color
from toolkit import sound as sk
from toolkit.rng import noise
from toolkit.text import font

STEPS = 20             # equal steps from empty to full
FILL = 0.7             # seconds one step takes to slide up
DRAIN = 0.6            # seconds it takes to drain to empty
LABEL = "DISCIPLINE"
LABEL_SIZE = 30
WIDTH, HEIGHT = 560, 34
GAP = 24               # between the label and the bar
PAD = 5                # between the outline and the fill
MIDDLE = BAR / 2       # the middle of the top black bar
OUTLINE = 3.6          # pen width of the outline
SOUND_DB = -12         # how loud its sounds are in a scene's mix: clearly above the scene, well below the alarm
SHAKE = 7.0            # pixels: how far it trembles at most

# A flicker: red on and off a few times, like a failing light. (seconds after it starts, red or not)
FLICKER = [(0.0, 1), (0.09, 0), (0.16, 1), (0.30, 0), (0.37, 1), (0.55, 0)]


def _mix(a, b, u):
    return tuple(int(round(x + (y - x) * u)) for x, y in zip(a, b))


class Discipline:
    """How full the bar is through one scene, and how to draw it.

    start: steps full when the scene starts. fills: times he does something (+1 step each).
    drains: times he quits with something in the bar (it drains to empty, flashing red).
    flickers: times he quits with the bar already empty (a red flicker, nothing to drain).
    shakes: (start, end) times it trembles, as the old pull tugs at him (film 1, rows 27-28).
    """

    def __init__(self, start=0, fills=(), drains=(), flickers=(), shakes=()):
        self.start = start
        self.shakes = list(shakes)
        self.events = sorted([(at, "fill") for at in fills] + [(at, "drain") for at in drains])
        self.drains = sorted(drains)
        self.flickers = sorted(flickers)

    def level(self, t):
        """How many steps are full at time t (fractional while it slides)."""
        value = self.start
        for at, kind in self.events:
            if kind == "fill":
                value += progress(t, at, at + FILL, "inout")
            else:
                value *= 1 - progress(t, at, at + DRAIN, "in")
        return min(value, STEPS)

    def red(self, t):
        """0..1, how red the bar is at time t."""
        out = 0.0
        for at in self.drains:            # flashes red at once, stays red while it drains, then fades back
            if at <= t:
                out = max(out, 1 - progress(t, at + DRAIN, at + DRAIN + 0.5, "inout"))
        for at in self.flickers:
            for (a, on), (b, _) in zip(FLICKER, FLICKER[1:] + [(float("inf"), 0)]):
                if at + a <= t < at + b:
                    out = max(out, on)
        return out

    def shaking(self, t):
        """0..1: how hard it trembles at time t (easing in and out of each shake)."""
        out = 0.0
        for a, b in self.shakes:
            out = max(out, progress(t, a, a + 0.4, "inout") * (1 - progress(t, b - 0.3, b, "inout")))
        return out

    def draw(self, canvas, t, frame):
        s = self.shaking(t)
        if s <= 0:
            draw_bar(canvas, frame, self.level(t), red=self.red(t))
            return
        canvas.save()
        canvas.translate(SHAKE * s * noise(t * 22, "discipline.shake", "x"), 0.6 * SHAKE * s * noise(t * 22, "discipline.shake", "y"))
        draw_bar(canvas, frame, self.level(t), red=self.red(t))
        canvas.restore()

    def full_at(self):
        """When the bar becomes full (the fill that reaches the last step), or None."""
        value = self.start
        for at, kind in self.events:
            value = value + 1 if kind == "fill" else 0
            if value >= STEPS:
                return at
        return None

    def add_sounds(self, mix):
        """Put the bar's sounds on a scene's soundtrack, right where it fills, drains or flickers."""
        for at, kind in self.events:
            mix.add(fill_sound() if kind == "fill" else drain_sound(), at=at, gain_db=SOUND_DB)
        full = self.full_at()
        if full is not None:            # the last step: a warm chord rings out as it turns green
            mix.add(full_sound(), at=full + FILL - 0.05, gain_db=SOUND_DB - 2, reverb=0.25)
        for at in self.flickers:
            mix.add(drain_sound(), at=at, gain_db=SOUND_DB)
        for a, b in self.shakes:
            mix.add(rattle_sound(b - a), at=a, gain_db=SOUND_DB - 6)


def layout():
    """Where the label starts and where the bar starts: the two together sit centred in the top black bar."""
    label_w = font(LABEL_SIZE).measureText(LABEL)
    x0 = 960 - (label_w + GAP + WIDTH) / 2
    return x0, x0 + label_w + GAP


def draw_bar(canvas, frame, level, *, red=0.0):
    """The bar with `level` steps full (out of STEPS). red: 0..1, how strongly it flashes red."""
    lx, bx = layout()
    top, bottom = MIDDLE - HEIGHT / 2, MIDDLE + HEIGHT / 2
    green = progress(level, STEPS - 0.4, STEPS, "inout")     # it turns green only as the last step fills
    colour = _mix(_mix(INK, GREEN, green), RED, red)
    canvas.drawString(LABEL, lx, MIDDLE + LABEL_SIZE * 0.36, font(LABEL_SIZE),
                      skia.Paint(AntiAlias=True, Color=to_color(colour)))
    ink = Ink(canvas, frame, prefix="discipline")
    if level > 0.01:
        # the fill is drawn full length (so its wobble only changes with the lines' boil), then cut off
        # where it has got to
        right = bx + PAD + (WIDTH - 2 * PAD) * level / STEPS
        canvas.save()
        canvas.clipRect(skia.Rect(bx, top, right, bottom))
        ink.fill([(bx + PAD, top + PAD), (bx + WIDTH - PAD, top + PAD), (bx + WIDTH - PAD, bottom - PAD),
                  (bx + PAD, bottom - PAD)], "fill", color=colour, wobble=0.5)
        canvas.restore()
    ink.stroke([(bx, top), (bx + WIDTH, top), (bx + WIDTH, bottom), (bx, bottom)], "outline", closed=True,
               width=OUTLINE, color=colour, wobble=1.3, taper=0.0)


# -- its sounds ----------------------------------------------------------------------------------------------

def _bell(freq, length=1.2, bright=0.6):
    """A soft glass ping: a few slightly out-of-tune partials ringing out."""
    t = sk.times(length)
    out = np.zeros_like(t)
    for ratio, amp, ring in ((1.0, 1.0, 0.9), (2.0, 0.35 * bright, 0.5), (3.01, 0.18 * bright, 0.3),
                             (4.17, 0.08 * bright, 0.18)):
        out += amp * np.sin(2 * np.pi * freq * ratio * t) * sk.decay(t, ring)
    return sk.fade_edges(sk.normalize(out * np.clip(t / 0.003, 0, 1), 0.9))


def fill_sound():
    """A clean tone that rises with the bar as it slides up (following its easing), ending on a bright ping."""
    t = sk.times(FILL)
    u = t / FILL
    shape = np.where(u < 0.5, 4 * u ** 3, 1 - (-2 * u + 2) ** 3 / 2)
    phase = 2 * np.pi * np.cumsum(330 * 3 ** shape) / sk.SR          # from E4 up to B5
    tone = (np.sin(phase) + 0.3 * np.sin(2 * phase) + 0.12 * np.sin(3 * phase)) * (0.25 + 0.75 * u)
    ping = _bell(990)
    out = np.zeros(len(t) + len(ping))
    out[:len(t)] += sk.fade_edges(tone, 0.02, 0.03) * 0.55
    start = int((FILL - 0.04) * sk.SR)
    out[start:start + len(ping)] += ping
    return sk.normalize(out, 0.9)


def drain_sound():
    """A buzzy tone falling away as the bar drains, like a machine switching off, ending in a low knock."""
    t = sk.times(DRAIN + 0.25)
    u = np.clip(t / DRAIN, 0, 1)
    phase = 2 * np.pi * np.cumsum(440 * (55 / 440) ** (u ** 1.6)) / sk.SR
    buzz = sum(np.sin(k * phase) / k for k in (1, 3, 5, 7))
    buzz = sk.lowpass(buzz, 3000) * (1 - np.clip((t - DRAIN) / 0.25, 0, 1))
    out = np.zeros(int(1.6 * sk.SR))
    out[:len(buzz)] += sk.fade_edges(buzz, 0.004, 0.02) * 0.7
    knock = sk.thud(0.6, key="bar.down")
    start = int((DRAIN - 0.05) * sk.SR)
    out[start:] += knock[:len(out) - start] * 0.6
    return sk.normalize(out, 0.9)


def rattle_sound(seconds):
    """A low, uneasy rattle while the bar trembles: a dull buzz shuddering, easing in and out."""
    t = sk.times(seconds)
    shudder = 0.6 + 0.4 * np.sin(2 * np.pi * 17 * t) * np.sin(2 * np.pi * 0.7 * t + 1.0)
    buzz = sk.lowpass(sum(np.sin(2 * np.pi * 70 * k * t) / k for k in (1, 2, 3)) + 0.4 * sk.noise(len(t), "rattle"), 400)
    env = np.clip(t / 0.4, 0, 1) * np.clip((seconds - t) / 0.3, 0, 1)
    return sk.normalize(buzz * shudder * env, 0.9)


def full_sound():
    """The bar full at last: a warm major chord of soft glass pings, ringing out."""
    out = np.zeros(int(2.4 * sk.SR))
    for k, freq in enumerate((523.25, 659.25, 783.99, 1046.5)):      # C, E, G, C
        ping = _bell(freq, length=2.2, bright=0.4)
        start = int(0.05 * k * sk.SR)
        out[start:start + len(ping)] += ping * (0.9 - 0.12 * k)
    return sk.normalize(out, 0.9)
