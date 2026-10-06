"""Captions and other text, in the film's font (Noteworthy Bold).

    caption(canvas, "He tried *again*.", t=2.0, start=1.0, end=4.0)

Captions sit bottom centre, inside the bottom black bar, so they never cover
the drawing. Draw them AFTER finish(), or the bar will paint over them. Long
captions wrap onto more lines, growing upward. Words wrapped in *asterisks* are drawn red (red = failure).
With t/start/end given, the caption fades in and out.

For a whole film, list the lines once and draw them every frame:

    lines = Captions([(0.5, 3.0, "Another morning."), (3.2, 6.0, "Another *failure*.")])
    lines.draw(canvas, t)
"""
from functools import lru_cache

import skia

from .anim import clamp
from .finish import BAR
from .lines import to_color
from .style import FONT_FAMILY, H, INK, RED, W

CAPTION_SIZE = 54
CAPTION_WIDTH = 1500      # longest a caption line may get before wrapping
FADE = 0.25               # seconds to fade in and out


@lru_cache(maxsize=None)
def typeface(family=FONT_FAMILY, bold=True):
    style = skia.FontStyle.Bold() if bold else skia.FontStyle.Normal()
    tf = skia.FontMgr().matchFamilyStyle(family, style)
    if tf is None:
        raise RuntimeError(f"The font '{family}' isn't installed on this computer")
    return tf


def font(size=CAPTION_SIZE, family=FONT_FAMILY, bold=True):
    f = skia.Font(typeface(family, bold), size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    return f


def _words(text):
    """Split text into (word, is_red) pairs. Words between *asterisks* are red."""
    out, in_red = [], False
    for word in text.split():
        if word.startswith("*"):
            in_red, word = True, word[1:]
        red = in_red
        core = word.rstrip(".,!?;:'\")")
        if core.endswith("*"):
            word = core[:-1] + word[len(core):]
            in_red = False
        out.append((word, red))
    return out


def wrap(text, f, max_width=CAPTION_WIDTH):
    """Break text into lines no wider than max_width. Returns lists of (word, is_red)."""
    space = f.measureText(" ")
    lines, line, width = [], [], 0.0
    for word, red in _words(text):
        w = f.measureText(word)
        if line and width + space + w > max_width:
            lines.append(line)
            line, width = [], 0.0
        width += (space if line else 0) + w
        line.append((word, red))
    if line:
        lines.append(line)
    return lines


def draw_text(canvas, text, x, y, *, size=CAPTION_SIZE, color=INK, accent=RED, align="center",
              alpha=1.0, max_width=None, shadow=True, line_height=1.25):
    """Draw text with its LAST line's baseline at y. align: left, center or right."""
    if alpha <= 0:
        return
    f = font(size)
    lines = wrap(text, f, max_width or 10 ** 6)
    space = f.measureText(" ")
    a = int(255 * clamp(alpha))
    top = y - (len(lines) - 1) * size * line_height
    for i, line in enumerate(lines):
        widths = [f.measureText(w) for w, _ in line]
        total = sum(widths) + space * (len(line) - 1)
        lx = x - {"left": 0, "center": total / 2, "right": total}[align]
        ly = top + i * size * line_height
        for (word, red), w in zip(line, widths):
            if shadow:
                p = skia.Paint(AntiAlias=True, Color=skia.Color(0, 0, 0, int(a * 0.85)),
                               MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, size * 0.12))
                canvas.drawString(word, lx, ly + size * 0.05, f, p)
            paint = skia.Paint(AntiAlias=True, Color=to_color((*(accent if red else color), a)))
            canvas.drawString(word, lx, ly, f, paint)
            lx += w + space


def caption_alpha(t, start, end, fade=FADE):
    if t is None or start is None:
        return 1.0
    end = float("inf") if end is None else end
    return clamp(min((t - start) / fade, (end - t) / fade)) if start <= t <= end else 0.0


def caption(canvas, text, t=None, start=None, end=None, **kw):
    """A caption at the bottom centre of the screen, in the black bar."""
    alpha = caption_alpha(t, start, end) * kw.pop("alpha", 1.0)
    size = kw.pop("size", CAPTION_SIZE)
    baseline = H - BAR / 2 + size * 0.33        # one line sits centred in the bar
    draw_text(canvas, text, W / 2, baseline, size=size, alpha=alpha,
              max_width=kw.pop("max_width", CAPTION_WIDTH), **kw)


class Captions:
    """A film's captions: a list of (start seconds, end seconds, text)."""

    def __init__(self, lines):
        self.lines = sorted(lines)

    def draw(self, canvas, t, **kw):
        for start, end, text in self.lines:
            if start <= t <= end:
                caption(canvas, text, t, start, end, **kw)
