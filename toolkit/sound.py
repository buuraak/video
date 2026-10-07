"""Sound kit made with numpy: piano, soft pads, drums and effects, mixed to a WAV.

Every sound is a numpy array (mono, or 2 rows for stereo) at 48,000 samples a
second. Place them on a timeline with Mix, then save:

    mix = Mix(duration=8)
    mix.add(pad(["A2", "E3", "C4"], 8), at=0, gain_db=-12, reverb=0.4)
    mix.add(piano("E5", 1.5), at=1.0, gain_db=-6, reverb=0.3)
    mix.add(thud(), at=3.5)
    mix.save("audio/scene.wav")

Any noise in a sound is made from a name (the `key`), so the same call always
gives exactly the same sound. Give repeated sounds different keys (or numbers)
when they should vary slightly, like footsteps.
"""
import math
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, fftconvolve, sosfilt

from .rng import rng

SR = 48000
NOTE_NAMES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


# -- basics ----------------------------------------------------------------

def note_freq(note):
    """'A4' -> 440.0. Sharps and flats: 'C#4', 'Bb3'. Numbers pass straight through."""
    if not isinstance(note, str):
        return float(note)
    name, rest = note[0].upper(), note[1:]
    shift = 0
    while rest and rest[0] in "#b":
        shift += 1 if rest[0] == "#" else -1
        rest = rest[1:]
    midi = 12 * (int(rest) + 1) + NOTE_NAMES[name] + shift
    return 440.0 * 2 ** ((midi - 69) / 12)


def times(seconds):
    return np.arange(int(round(seconds * SR))) / SR


def noise(n, *key):
    return rng("sound", *key).standard_normal(n)


def _filter(x, kind, cutoff, order=2):
    sos = butter(order, cutoff, btype=kind, fs=SR, output="sos")
    return sosfilt(sos, x, axis=-1)


def lowpass(x, hz, order=2): return _filter(x, "lowpass", min(hz, SR * 0.45), order)
def highpass(x, hz, order=2): return _filter(x, "highpass", hz, order)
def bandpass(x, lo, hi, order=2): return _filter(x, "bandpass", [lo, min(hi, SR * 0.45)], order)


def decay(t, seconds):
    """Falls away from 1, losing about two-thirds every `seconds`."""
    return np.exp(-t / seconds)


def fade_edges(x, start=0.002, end=0.01):
    """Tiny fades at the start and end so sounds never click."""
    x = np.array(x, dtype=float)
    a, b = int(start * SR), int(end * SR)
    if a:
        x[..., :a] *= np.linspace(0, 1, a)
    if b:
        x[..., -b:] *= np.linspace(1, 0, b)
    return x


def normalize(x, peak=1.0):
    m = np.max(np.abs(x))
    return x * (peak / m) if m > 0 else x


# -- piano -----------------------------------------------------------------

def piano(note, held=1.0, velocity=0.8, key=""):
    """One piano note held for `held` seconds, then released (the sound rings out a little)."""
    f0 = note_freq(note)
    t = times(held + 0.6)
    g = rng("piano", note, key)
    ring = float(np.clip(3.0 * (220.0 / f0) ** 0.5, 0.5, 7.0))
    out = np.zeros_like(t)
    for k in range(1, 16):
        fk = k * f0 * math.sqrt(1 + 0.0004 * k * k)      # piano strings are slightly out of tune with themselves
        if fk > 10000:
            break
        amp = (1 / k ** 1.2) * velocity ** (0.4 + 0.15 * k)
        tk = ring / (1 + 0.55 * (k - 1))
        env = 0.6 * decay(t, tk * 0.15) + 0.4 * decay(t, tk)
        cents = 2 ** (g.uniform(0.3, 1.0) / 1200)
        out += amp * env * 0.5 * (np.sin(2 * np.pi * fk * t + g.uniform(0, 6.3))
                                  + np.sin(2 * np.pi * fk * cents * t + g.uniform(0, 6.3)))
    hammer = lowpass(noise(len(t), "hammer", note, key), 2500) * decay(t, 0.004) * 0.25 * velocity
    out += hammer
    released = np.where(t < held, 1.0, decay(np.maximum(t - held, 0), 0.09))
    return fade_edges(normalize(out * released, 0.9 * velocity))


def piano_chord(notes, held=1.5, velocity=0.7, spread=0.012, key=""):
    """Several notes together, rolled very slightly like a real hand."""
    parts = [piano(n, held, velocity * (0.9 if i else 1.0), key) for i, n in enumerate(notes)]
    length = max(len(p) for p in parts) + int(spread * SR * len(parts))
    out = np.zeros(length)
    for i, p in enumerate(parts):
        s = int(i * spread * SR)
        out[s:s + len(p)] += p
    return normalize(out, 0.9 * velocity)


# -- soft pads -------------------------------------------------------------

def pad(notes, held, attack=1.5, release=2.0, brightness=0.3, key=""):
    """A soft, wide, slowly breathing chord. Stereo."""
    t = times(held + release)
    out = np.zeros((2, len(t)))
    g = rng("pad", tuple(map(str, notes)), key)
    for note in notes:
        f = note_freq(note)
        for cents in (-9, 0, 8):
            ff = f * 2 ** ((cents + g.uniform(-2, 2)) / 1200)
            wobble = 1 + 0.0015 * np.sin(2 * np.pi * g.uniform(0.15, 0.4) * t + g.uniform(0, 6.3))
            phase = np.cumsum(ff * wobble) / SR + g.uniform(0, 1)
            saw = 2 * (phase % 1.0) - 1
            tri = 2 * np.abs(saw) - 1
            voice = 0.35 * saw + 0.65 * tri
            pan = g.uniform(-0.7, 0.7)
            out[0] += voice * math.cos((pan + 1) * math.pi / 4)
            out[1] += voice * math.sin((pan + 1) * math.pi / 4)
    out = lowpass(out, 250 + brightness * 2600, order=4)
    breathe = 1 + 0.08 * np.sin(2 * np.pi * 0.17 * t + g.uniform(0, 6.3))
    rise = np.clip(t / max(attack, 1e-3), 0, 1) ** 2
    fall = np.clip(1 - (t - held) / max(release, 1e-3), 0, 1) ** 2
    return fade_edges(normalize(out * rise * fall * breathe, 0.8))


# -- drums -----------------------------------------------------------------

def kick(velocity=1.0, key=""):
    t = times(0.6)
    freq = 46 + 120 * decay(t, 0.035)
    body = np.sin(2 * np.pi * np.cumsum(freq) / SR) * decay(t, 0.32)
    click = highpass(noise(len(t), "kick", key), 2000) * decay(t, 0.003) * 0.3
    return fade_edges(normalize(np.tanh(1.6 * (body + click)), velocity))


def snare(velocity=1.0, key=""):
    t = times(0.45)
    tone = (np.sin(2 * np.pi * 185 * t) + 0.5 * np.sin(2 * np.pi * 330 * t)) * decay(t, 0.07)
    rattle = bandpass(noise(len(t), "snare", key), 1500, 9000) * decay(t, 0.13)
    return fade_edges(normalize(0.5 * tone + rattle, velocity))


def hihat(open=False, velocity=0.7, key=""):
    t = times(0.5 if open else 0.12)
    metal = sum(np.sign(np.sin(2 * np.pi * f * t)) for f in (205.3, 304.4, 369.6, 522.7, 540.0, 800.0))
    hiss = noise(len(t), "hat", key)
    out = highpass(0.4 * metal + hiss, 7000, order=4) * decay(t, 0.22 if open else 0.03)
    return fade_edges(normalize(out, velocity))


def tom(pitch=110, velocity=0.9, key=""):
    t = times(0.7)
    freq = pitch * (1 + 0.5 * decay(t, 0.05))
    body = np.sin(2 * np.pi * np.cumsum(freq) / SR) * decay(t, 0.22)
    stick = bandpass(noise(len(t), "tom", key), 800, 5000) * decay(t, 0.01) * 0.3
    return fade_edges(normalize(body + stick, velocity))


# -- effects ---------------------------------------------------------------

def footstep(n=0, weight=1.0, key="step"):
    """One step. Pass a different n for each step so they vary like real ones."""
    g = rng("footstep", key, n)
    t = times(0.35)
    heel_f = g.uniform(75, 105)
    heel = (0.45 * np.sin(2 * np.pi * heel_f * t) * decay(t, 0.03)
            + 1.2 * lowpass(noise(len(t), key, n, "heel"), 2200) * decay(t, 0.02))
    toe_at = int(g.uniform(0.04, 0.06) * SR)
    toe = np.zeros_like(t)
    toe[toe_at:] = (lowpass(noise(len(t) - toe_at, key, n, "toe"), 1800) * decay(t[: len(t) - toe_at], 0.015))
    scuff = bandpass(noise(len(t), key, n, "scuff"), 500, 3500) * decay(t, 0.07) * 0.25
    return fade_edges(normalize(heel + 0.5 * toe + scuff, 0.8 * weight * g.uniform(0.85, 1.0)))


def footsteps(count, every=0.55, weight=1.0, key="step"):
    """A walk: `count` steps, one every `every` seconds."""
    out = np.zeros(int((count * every + 0.4) * SR))
    for i in range(count):
        s = footstep(i, weight, key)
        a = int(i * every * SR)
        out[a:a + len(s)] += s * (0.85 if i % 2 else 1.0)
    return out


def whoosh(length=0.9, peak=0.6, low=300, high=3500, key="whoosh"):
    """Air rushing past, sweeping across from left to right. Stereo.

    peak is where the whoosh is loudest, as a share of its length.
    """
    t = times(length)
    u = t / length
    base = noise(len(t), "whoosh", key)
    # where the sound's "pitch" sits over time: rises to the peak, then falls
    centre = np.where(u < peak, low * (high / low) ** (u / peak),
                      high * ((low * 2) / high) ** ((u - peak) / (1 - peak)))
    out = np.zeros_like(t)
    for f in np.geomspace(150, 7000, 14):
        w = np.exp(-((np.log(f) - np.log(centre)) / 0.45) ** 2)
        out += bandpass(base, f / 1.25, f * 1.25) * w
    loud = np.where(u < peak, (u / peak) ** 2, ((1 - u) / (1 - peak)) ** 1.5)
    out *= loud
    pan = -0.8 + 1.6 * u
    stereo = np.vstack([out * np.cos((pan + 1) * np.pi / 4), out * np.sin((pan + 1) * np.pi / 4)])
    return fade_edges(normalize(stereo, 0.9))


def thud(weight=1.0, key="thud"):
    """A heavy impact: something big hitting the ground.

    It has deep boom for headphones, plus a punchy body that small phone and
    laptop speakers can still play.
    """
    t = times(1.4)
    freq = 45 + 50 * decay(t, 0.05)
    boom = np.sin(2 * np.pi * np.cumsum(freq) / SR) * decay(t, 0.22)
    body = (np.sin(2 * np.pi * 120 * t) * decay(t, 0.1) * 1.1
            + np.sin(2 * np.pi * 210 * t) * decay(t, 0.06) * 0.8)
    dirt = lowpass(noise(len(t), "thud", key), 1200) * decay(t, 0.08) * 2.2
    out = np.tanh(1.5 * (boom + body + dirt))
    return fade_edges(normalize(out, 0.95 * weight), end=0.3)


def heartbeat(beats=4, bpm=60, key="heart"):
    """A muffled 'lub-dub' heartbeat."""
    period = 60.0 / bpm
    t = times(beats * period + 0.4)
    out = np.zeros_like(t)

    def thump(at, f, strength, n):
        s = int(at * SR)
        tt = t[: len(t) - s]
        freq = f * (1 + 0.6 * decay(tt, 0.02))
        phase = 2 * np.pi * np.cumsum(freq) / SR
        # the low note plus overtones, so small speakers can still hear the beat
        body = (np.sin(phase) + 0.6 * np.sin(2 * phase) + 0.35 * np.sin(3 * phase))
        body *= decay(tt, 0.08) * np.clip(tt / 0.006, 0, 1)
        body += lowpass(noise(len(tt), "heart", key, n), 300) * decay(tt, 0.04) * 0.8
        out[s:] += strength * body

    for b in range(beats):
        thump(b * period, 52, 1.0, (b, 0))
        thump(b * period + 0.27, 66, 0.65, (b, 1))
    return fade_edges(normalize(lowpass(out, 450, order=2), 0.9))


def tick(tock=False, key="tick"):
    """A clock tick (tock=True for the lower second half of 'tick-tock')."""
    t = times(0.09)
    ping = 2400 if tock else 3300
    click = bandpass(noise(len(t), "tick", key, tock), 2000, 8000) * decay(t, 0.0012)
    ring = np.sin(2 * np.pi * ping * t) * decay(t, 0.006) * 0.4
    body = np.sin(2 * np.pi * 900 * t) * decay(t, 0.018) * 0.25
    return fade_edges(normalize(click + ring + body, 0.7))


def ticking(seconds, key="clock"):
    """A clock ticking once a second for `seconds`."""
    out = np.zeros(int((seconds + 0.1) * SR))
    for i in range(int(seconds)):
        s = tick(tock=bool(i % 2), key=(key, i))
        a = i * SR
        out[a:a + len(s)] += s
    return out


ALARM_BEEPS = 4          # beeps in each burst
ALARM_BEEP = 0.07        # seconds each beep lasts
ALARM_GAP = 0.05         # seconds of silence between beeps in a burst
ALARM_EVERY = 1.0        # a new burst starts every second


def alarm_on(t):
    """True while a burst of alarm beeps is sounding, t seconds after the alarm started.

    Use it to blink a clock's numbers in time with alarm().
    """
    burst = ALARM_BEEPS * (ALARM_BEEP + ALARM_GAP) - ALARM_GAP
    return t >= 0 and (t % ALARM_EVERY) < burst


def alarm(seconds, pitch=2600):
    """A digital alarm clock going off for `seconds`: four sharp beeps, a pause, every second.

    It ends exactly at `seconds`, e.g. when someone presses the button.
    """
    t = times(seconds)
    within_burst = t % ALARM_EVERY
    n = np.floor(within_burst / (ALARM_BEEP + ALARM_GAP))
    within_beep = within_burst - n * (ALARM_BEEP + ALARM_GAP)
    gate = (n < ALARM_BEEPS) & (within_beep < ALARM_BEEP)
    edge = np.clip(np.minimum(within_beep, ALARM_BEEP - within_beep) / 0.002, 0, 1)
    # a hard, buzzy square-ish tone (only odd overtones), like a cheap clock's little speaker
    tone = sum(np.sin(2 * np.pi * pitch * k * t) / k for k in (1, 3, 5))
    return fade_edges(normalize(lowpass(tone * gate * edge, 9000), 0.8), end=0.004)


# -- voices ----------------------------------------------------------------

SPEECH_FOLDER = Path(__file__).resolve().parent.parent / "audio" / "speech"


def speech(text, voice="Samantha", rate=None):
    """A line spoken by one of the Mac's voices (the `say` command), as a mono sound.

    Each line is made once and saved in audio/speech/, so it stays identical on
    every run. `say -v '?'` lists the voices; rate is words per minute.
    """
    import subprocess
    from .rng import seed
    path = SPEECH_FOLDER / f"{voice.split(' ')[0].lower()}_{seed(text, voice, rate):016x}.wav"
    if not path.exists():
        SPEECH_FOLDER.mkdir(parents=True, exist_ok=True)
        aiff = path.with_suffix(".aiff")
        subprocess.run(["say", "-v", voice, "-o", str(aiff)] + (["-r", str(rate)] if rate else []) + [text],
                       check=True)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(aiff), "-ac", "1", "-ar", str(SR),
                        str(path)], check=True)
        aiff.unlink()
    rate_read, data = wavfile.read(path)
    return data.astype(float) / 32768.0


def muffled(x, hz=750):
    """A sound heard muffled, as through a blanket or from a phone held away: no clear words."""
    return lowpass(highpass(x, 110), hz, order=4)


# -- mixing ----------------------------------------------------------------

def _room(seconds=2.2, key="room"):
    t = times(seconds)
    tail = np.vstack([noise(len(t), key, "L"), noise(len(t), key, "R")]) * decay(t, seconds / 6.9)
    tail = lowpass(tail, 5000)
    pre = int(0.018 * SR)
    ir = np.zeros((2, len(t) + pre))
    ir[:, pre:] = tail
    return ir / np.sqrt(np.sum(ir ** 2, axis=1, keepdims=True))


class Mix:
    """A stereo timeline to place sounds on."""

    def __init__(self, duration):
        self.out = np.zeros((2, int(round(duration * SR))))
        self.send = np.zeros_like(self.out)

    def add(self, sound, at=0.0, gain_db=0.0, pan=0.0, reverb=0.0):
        """Place a sound starting at `at` seconds.

        gain_db: louder (+) or quieter (-), in decibels (-6 is about half as loud)
        pan: -1 left ... 0 centre ... 1 right (for mono sounds)
        reverb: 0..1, how much room echo to add
        """
        s = np.asarray(sound, dtype=float)
        if s.ndim == 1:
            s = np.vstack([s * math.cos((pan + 1) * math.pi / 4), s * math.sin((pan + 1) * math.pi / 4)]) * math.sqrt(2)
        s = s * 10 ** (gain_db / 20)
        start = int(round(at * SR))
        if start < 0:
            s, start = s[:, -start:], 0
        end = min(start + s.shape[1], self.out.shape[1])
        if end <= start:
            return self
        self.out[:, start:end] += s[:, : end - start]
        if reverb > 0:
            self.send[:, start:end] += s[:, : end - start] * reverb
        return self

    def render(self, peak_db=-1.0):
        """The finished stereo mix, with room echo added and the loudest moment at peak_db."""
        mix = self.out.copy()
        if np.any(self.send):
            ir = _room()
            wet = np.vstack([fftconvolve(self.send[c], ir[c])[: mix.shape[1]] for c in range(2)])
            mix += wet * 0.5
        mix = np.tanh(mix * 0.9) / 0.9 if np.max(np.abs(mix)) > 1 else mix
        return fade_edges(normalize(mix, 10 ** (peak_db / 20)), 0.0, 0.05)

    def save(self, path, peak_db=-1.0):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = self.render(peak_db)
        wavfile.write(path, SR, (np.clip(data, -1, 1).T * 32767).astype(np.int16))
        return path
