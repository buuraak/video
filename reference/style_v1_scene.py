"""Demo scene: a toolkit test, not a real film.

The tired hero stands breathing. The enemy glitches into existence, stomps,
the camera jolts, and the hero sinks a little further.
"""
import math

from toolkit import GREY, RED, Camera, Captions, Character, Ink, Track, blink, faces, lerp, progress
from toolkit import sound as sk
from toolkit.rng import rand

DURATION = 7.0

GROUND = 820
STOMP = 3.5            # the moment the enemy's foot hits the ground

hero = Character("hero")
enemy = Character("enemy", height=640, color=RED, glow=True, glitch=True)
camera = Camera(
    x=Track((0, 960), (STOMP + 0.2, 960), (7.0, 900)),
    y=Track((0, 540), (STOMP + 0.2, 540), (7.0, 470)),
    zoom=Track((0, 1.0), (STOMP + 0.2, 1.0), (7.0, 1.3)),
).shake(at=STOMP, strength=1.0, length=0.6)

captions = Captions([
    (0.4, 2.3, "Another morning."),
    (2.6, 4.6, "*It* was already waiting."),
    (4.9, 6.9, "He didn't even look up."),
])


def enemy_visible(t, frame):
    """The enemy flickers into existence between 1.8s and 2.5s."""
    if t < 1.8:
        return 0.0
    if t < 2.5:
        return 1.0 if rand("enemy-in", frame // 2) < (t - 1.8) / 0.7 else 0.0
    return 1.0


def draw(canvas, t, frame):
    with camera.view(canvas, t):
        Ink(canvas, frame, color=GREY).floor(GROUND)

        # hero: breathing, flinching at the stomp, then sinking
        breathe = 3 * math.sin(2 * math.pi * t / 3.2)
        sink = progress(t, STOMP, STOMP + 1.5, "out")
        flinch = math.exp(-max(t - STOMP, 0) * 6) if t >= STOMP else 0.0
        face = faces.TIRED.but(eyes=lerp(0.5, 0.35, sink) * blink(t, "hero") * (1 - 0.9 * flinch))
        if t > STOMP:
            face = face.but(brows=lerp(1.0, 1.0, sink), mouth_size=lerp(0.55, 0.9, sink))
        pose = hero.stand(700, GROUND, face=face,
                          head_tilt=lerp(-8, -18, sink) - 10 * flinch,
                          lean=lerp(-3, -6, sink) - 4 * flinch)
        hero.draw(canvas, frame, pose.but(y=pose.y + breathe + 6 * sink))   # feet stay on the floor

        # enemy: appears, then stomps
        lift = progress(t, STOMP - 0.45, STOMP - 0.15, "out") * (1 - progress(t, STOMP - 0.15, STOMP, "in"))
        x = 1330
        pose = enemy.stand(x, GROUND, face=faces.EVIL, facing=-1, lean=-4 + 3 * lift,
                           foot_l=(x - 60, GROUND), foot_r=(x + 50, GROUND - 90 * lift))
        sh = enemy.joints(pose)["shoulder"]
        pose = pose.but(hand_l=(sh[0] - 150, sh[1] + 120 - 20 * lift), hand_r=(sh[0] + 50, sh[1] + 190))
        enemy.draw(canvas, frame, pose, opacity=enemy_visible(t, frame))


def overlay(canvas, t, frame):
    captions.draw(canvas, t)


def soundtrack():
    mix = sk.Mix(DURATION)
    mix.add(sk.pad(["A2", "E3", "C4"], DURATION, attack=1.5, key="demo"), at=0, gain_db=-14, reverb=0.4)
    mix.add(sk.ticking(2), at=0.0, gain_db=-16, reverb=0.2)
    mix.add(sk.piano("E5", 0.7, 0.6, key=1), at=0.4, gain_db=-10, reverb=0.45)
    mix.add(sk.piano("C5", 0.7, 0.55, key=2), at=1.2, gain_db=-10, reverb=0.45)
    mix.add(sk.whoosh(1.0, peak=0.6), at=1.6, gain_db=-8, reverb=0.3)
    mix.add(sk.heartbeat(4, bpm=70), at=2.4, gain_db=-6)
    mix.add(sk.thud(), at=STOMP, gain_db=0, reverb=0.3)
    mix.add(sk.piano("A2", 2.0, 0.8, key=3), at=STOMP, gain_db=-9, reverb=0.4)
    for i, (note, at) in enumerate([("C5", 5.0), ("B4", 5.7), ("A4", 6.3)]):
        mix.add(sk.piano(note, 0.6, 0.5, key=10 + i), at=at, gain_db=-11, reverb=0.45)
    return mix
