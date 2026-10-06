"""Making a blank frame to draw on, and saving it."""
import numpy as np
import skia

from .lines import to_color
from .style import BG, H, W


class Frame:
    """A 1920x1080 picture. .canvas is for drawing, .pixels is the same picture as numbers."""

    def __init__(self, width=W, height=H, background=BG):
        self.pixels = np.zeros((height, width, 4), dtype=np.uint8)
        self.surface = skia.Surface(self.pixels)  # draws straight into self.pixels (RGBA)
        self.canvas = self.surface.getCanvas()
        self.canvas.clear(to_color(background))

    def save(self, path):
        self.surface.makeImageSnapshot().save(str(path), skia.kPNG)
