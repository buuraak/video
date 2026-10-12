"""Film 1, row 17 of the story: grind 5, the last loop of the grind. 2 seconds, one shot. It follows row 16,
where he slashed SATURDAY.

 0-2 s   Only his face in the phone light: the quote's close-up from above again, the shot where he once
         turned determined. Now he's numb: no frown, flat brows, heavy lids. He swipes faster and faster
         (four swipes, out of the picture below), each one a dip and a flash of light on his face, the
         muffled reel voices cutting each other off. The scrolling has taken over; the grind ends on its
         fastest beat.

No caption. Sound: the hum, the reels' muffled voices, a swipe on each cut between them.
"""
from scenes.discipline import Discipline
from scenes.scroll import reel_sounds
from scenes.the_quote import draw_close_face
from toolkit import Camera, Face, Track, progress
from toolkit import sound as sk
from toolkit.rng import noise

DURATION = 2.0
PEAK_DB = -2.3          # set so the hum matches the other scenes
SWIPES = (0.5, 0.98, 1.36, 1.66)       # faster and faster
BRIGHT = (0.8, 0.95, 0.75, 1.0, 0.85)  # each reel lights his face a little differently
NUMB = Face(eyes=0.4, brows=0.1, mouth="flat", bags=True)   # sheets/face_light_options.png, 2

camera = Camera(zoom=Track((0, 1.0), (DURATION, 1.05, "linear")), name="grind5.face")


def light_level(t):
    """The phone's light: flickering with the video; on each swipe it dips as the reel slides away, then
    flashes up as the next one comes in."""
    n = sum(1 for s in SWIPES if s <= t)
    level = BRIGHT[n] * (1 + 0.12 * noise(t * 5, "grind5.reel", n))
    for s in SWIPES:
        if s - 0.06 <= t < s + 0.08:
            level *= 0.35 + 0.65 * progress(t, s + 0.01, s + 0.08, "out")
        level *= 1 + 0.6 * progress(t, s + 0.03, s + 0.09, "out") * (1 - progress(t, s + 0.1, s + 0.4, "inout"))
    return level


def draw(canvas, t, frame):
    with camera.view(canvas, t):
        draw_close_face(canvas, frame, NUMB, light_level(t), tilt=-1.5 + 0.5 * t / DURATION)


bar = Discipline()  # still empty


def overlay(canvas, t, frame):
    bar.draw(canvas, t, frame)


def soundtrack():
    mix = sk.Mix(DURATION)
    mix.add(sk.pad(["A1", "E2"], DURATION, attack=0.4, release=1.0, brightness=0.05, key="hum"),
            at=0, gain_db=-17, reverb=0.2)
    # the reels, muffled, each cut off by the next swipe; a little nearer than from above (the phone is just
    # below the picture), evened as in scene 2; each starts mid-sentence
    adam, laura, liam = reel_sounds()
    cuts = (0.0,) + SWIPES + (DURATION,)
    for (clip, offset, even), a, b in zip(((liam, 6.25, 3.3), (adam, 0.9, 3.4), (laura, 5.1, 0.4), (liam, 14.0, 3.3),
                                            (adam, 2.9, 3.4)), cuts, cuts[1:]):
        part = clip[int(offset * sk.SR):int((offset + b - a) * sk.SR)]
        mix.add(sk.fade_edges(part, 0.004, 0.01), at=a, gain_db=-9 + even, pan=0.05, reverb=0.05)
    for s in SWIPES:
        mix.add(sk.lowpass(sk.tick(key=("grind5.swipe", s)), 2500), at=s - 0.02, gain_db=-22, reverb=0.05)
    return mix
