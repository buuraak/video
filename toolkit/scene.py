"""How a scene file plugs into the render and contact-sheet scripts.

A scene is a Python file (in scenes/) that defines:

    DURATION = 8.0                    # seconds
    def draw(canvas, t, frame): ...   # the picture: background, characters, camera
    def overlay(canvas, t, frame): ...  # optional: captions, drawn after the film finish
    def soundtrack(): return Mix(...)  # optional: the scene's sound, built from the sound kit
    AUDIO = "audio/my_scene.wav"      # optional: a ready-made sound file instead (e.g. a voiceover)
    FINISH = True                     # optional: set False to skip grain/vignette/bars

Every frame is made the same way: blank dark frame -> draw -> finish -> overlay.
"""
import importlib.util
import sys
from pathlib import Path

from .finish import finish
from .frame import Frame
from .style import FPS


def load(path):
    path = Path(path).resolve()
    spec = importlib.util.spec_from_file_location(f"scene_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.PATH = path
    return module


def frame_count(scene):
    return int(round(scene.DURATION * FPS))


def build_audio(scene, folder="audio"):
    """Make the scene's sound file, if it has one. Returns its path, or None."""
    root = Path(scene.PATH).parent.parent
    if hasattr(scene, "soundtrack"):
        return scene.soundtrack().save(root / folder / f"{Path(scene.PATH).stem}.wav")
    audio = getattr(scene, "AUDIO", None)
    if audio:
        path = Path(audio) if Path(audio).is_absolute() else root / audio
        if path.exists():
            return path
        print(f"Note: sound file {path} not found, continuing without sound")
    return None


def render_frame(scene, frame):
    """Draw one finished frame of a scene."""
    t = frame / FPS
    f = Frame()
    scene.draw(f.canvas, t, frame)
    if getattr(scene, "FINISH", True):
        finish(f, frame)
    overlay = getattr(scene, "overlay", None)
    if overlay is not None:
        overlay(f.canvas, t, frame)
    return f
