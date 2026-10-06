"""The film finish: soft vignette, film grain, black bars top and bottom.

Apply it last, after the scene and captions are drawn:

    finish(frame_obj, frame_number)
"""
import numpy as np
import skia

from .rng import rng
from .style import H, W

BAR = 132          # bar height in pixels: leaves a 2.35:1 cinema picture
GRAIN = 5.0        # grain strength (brightness wobble, out of 255)
VIGNETTE = 0.6     # how dark the corners get, 0..1


def vignette(canvas, strength=VIGNETTE, width=W, height=H):
    """Darken the edges and corners softly."""
    radius = float(np.hypot(width / 2, height / 2))
    shader = skia.GradientShader.MakeRadial(
        skia.Point(width / 2, height / 2), radius,
        [skia.Color(0, 0, 0, 0), skia.Color(0, 0, 0, 0), skia.Color(0, 0, 0, int(255 * strength))],
        [0.0, 0.45, 1.0])
    canvas.drawRect(skia.Rect(0, 0, width, height), skia.Paint(Shader=shader))


def grain(pixels, frame, amount=GRAIN):
    """Add film grain to the picture. Different on every frame, identical on every run."""
    h, w = pixels.shape[:2]
    noise = rng("grain", frame).standard_normal((h + 1, w + 1), dtype=np.float32)
    # average neighbouring specks so grains are a little softer and bigger than one pixel
    noise = (noise[:-1, :-1] + noise[1:, :-1] + noise[:-1, 1:] + noise[1:, 1:]) * (0.5 * amount)
    rgb = pixels[..., :3].astype(np.int16)
    rgb += noise.astype(np.int16)[..., None]
    np.clip(rgb, 0, 255, out=rgb)
    pixels[..., :3] = rgb


def bars(canvas, height=BAR, width=W, frame_height=H):
    """Black bars at the top and bottom."""
    black = skia.Paint(Color=skia.ColorBLACK)
    canvas.drawRect(skia.Rect(0, 0, width, height), black)
    canvas.drawRect(skia.Rect(0, frame_height - height, width, frame_height), black)


def finish(frame_obj, frame, *, use_vignette=True, use_grain=True, use_bars=True):
    """Apply the whole finish to a Frame, in the right order."""
    if use_vignette:
        vignette(frame_obj.canvas)
    if use_grain:
        grain(frame_obj.pixels, frame)
    if use_bars:
        bars(frame_obj.canvas)
