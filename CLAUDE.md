# Animated short films

Animated short films where every frame is drawn with Python code, then joined into a video with sound (a voice track only when a film calls for one; film 1 uses captions only).

The user is not a developer. Explain anything you need from them in plain words, without jargon.

## The three living documents

Read all three before starting work on any film.

- [style-bible.md](style-bible.md): what our films look like and why (colours, the character, the villain, fonts, captions, camera movement). Keep it to one page.
- [method.md](method.md): the steps we follow for every film, the checks we always run, and every mistake that cost time.
- [film-list.md](film-list.md): every film we've made, with its theme, big visual idea, what worked and what viewers said.

## Keep them up to date

After every decision we make, update the right file in the same session. Don't wait until the end.

- A decision about how films look goes in the style bible.
- A decision about how we work, a check worth always running, or a mistake that cost time goes in the method.
- A finished film, or feedback on one, goes in the film list.
- A change to the tools or setup goes in this file.

Only record what the user has agreed to, not suggestions that are still open. After each update, tell the user in one line which file changed and what was added. When the style bible grows past a page, tighten it instead of adding more.

## Setup

- Python: always run `.venv/bin/python`. It's a virtual environment (Python 3.13) with skia-python, numpy and scipy. Don't use the system `python3`, which is Apple's old 3.9. The uploaded `.venv/` relies on Homebrew's Python 3.13, so on another computer run `brew install python@3.13` and it works as is. Don't rebuild it there: that rewrites about 2,900 uploaded files. Only if it's broken beyond that: `python3.13 -m venv .venv && .venv/bin/pip install -r requirements.txt`.
- Git: the code is on GitHub at https://github.com/buuraak/video (branch `main`). Commits in this project use the email bubaykara@outlook.com (set for this folder only). Everything is uploaded, including `.venv/`, contact sheets (`sheets/`) and sound (`audio/`). Left out: Python cache files, `.DS_Store`, the private `.env` key file, and the videos in `films/`, which are too big for GitHub (it refuses files over 100 MB, and 20 seconds with our film grain is over that) and can always be re-made with `render.py`. Push only when the user asks.
- ffmpeg and ffprobe come from Homebrew, at `/opt/homebrew/bin`.
- Voice: the macOS `say` command, e.g. `say -v Samantha -o line.aiff "text"`, then convert with ffmpeg. Only the basic voices are installed. The user can download Enhanced or Premium voices in System Settings → Accessibility → Spoken Content → System Voice → Manage Voices.
- ElevenLabs (the user's Creator plan) makes realistic voices, sound effects and music. Its API key is in `.env` (one line, `ELEVENLABS_API_KEY=...`), which is listed in `.gitignore` so it is never uploaded. The key can make audio but can't read account details. There's no toolkit helper for it yet: call the web API with Python's `urllib` (no extra package needed), e.g. `POST https://api.elevenlabs.io/v1/sound-generation` for sound effects or `/v1/music` for music, with the key in the `xi-api-key` header. Save every result in `audio/` and reuse it, like `speech()` does, so each sound is made once and stays identical.
- [test_frame.py](test_frame.py) draws `test.png` and is a minimal working example of drawing with skia. `tts_check/` holds the voice test clip.

## The toolkit

Everything for making films lives in `toolkit/`. Each file's docstring explains how to use it.

- `style.py`: format, colours, line width, font. Change the look here.
- `lines.py`: `Ink`, the hand-drawn pen. Every stroke needs a stable key so its wobble holds for 3 frames. Always draw floors with `ink.floor(y)`, never `ink.line()`: an ordinary long line drifts and makes characters float.
- `character.py`: `Character` and `Pose`. Place characters with `stand(x, ground)` so their feet stay planted while the hips move; to move the hips, use `pose.but(y=pose.y + offset)`. Hands and feet reach exact targets. Place targets relative to `character.joints(pose)`, never by guessing pixels. The enemy is `Character(..., color=RED, glow=True, glitch=True)`, bigger than the hero.
- `face.py`: `Face` and ready-made faces (`faces.TIRED`, `faces.EVIL`, …), plus `blink(t)`. `draw_face()` takes a fractional `facing` (e.g. 0.3) to turn the face slightly, like a head rolling on a pillow.
- `camera.py`: `Camera` with zoom, move, `shake()` and the handheld drift. Draw the scene inside `with camera.view(canvas, t):`.
- `text.py`: `caption()` and `Captions`. Captions sit inside the bottom bar, so they must be drawn after `finish()`. `*word*` makes a word red.
- `finish.py`: grain, vignette and bars.
- `sound.py`: piano, pads, drums and effects, mixed with `Mix` into a WAV. `alarm(seconds)` is a digital alarm clock; `alarm_on(t)` says when its beeps sound, to blink a clock in time with them. `speech(text, voice)` speaks a line with a Mac voice and saves it in `audio/speech/` (made once, identical every run); `muffled()` makes any sound unclear, like mumbling heard through a blanket.
- `anim.py`: `Track` keyframes and easing. `rng.py`: stable randomness. Never use `random` or `hash()`.

`reference/` holds the approved looks, each with its contact sheet and the scene that made it. `style_v2` is current (the hero faces the enemy). `style_v1` is the earlier version where he faced the viewer. Never overwrite them; try changes on copies. `Pose(facing=1)` or `facing=-1` turns a character side-on toward the right or left.

A film is one or more scene files in `scenes/` that define `DURATION`, `draw(canvas, t, frame)`, and optionally `overlay()` for captions and `soundtrack()` for sound. [scenes/demo.py](scenes/demo.py) is a worked example. A scene can set `PEAK_DB` (normally -1) to make its whole soundtrack quieter, so a sound that runs through several scenes, like the hum, stays the same loudness.

Each film's agreed story and scene table lives in `stories/` (film 1: [stories/tomorrow.md](stories/tomorrow.md)).

Film 1's scenes share one bedroom: [scenes/bedroom.py](scenes/bedroom.py) holds the bed, nightstand, clock, phone and blanket. It is not a scene itself; [scenes/wake_up.py](scenes/wake_up.py) (scene 1) and [scenes/scroll.py](scenes/scroll.py) (scene 2) import from it.

- Contact sheet (12 frames in one picture): `.venv/bin/python contact_sheet.py scenes/x.py --start 0 --end 5`. Saves to `sheets/`. Also works on a video in `films/`.
- Render: `.venv/bin/python render.py scenes/x.py`. Saves to `films/`. It draws frames in parallel, adds the soundtrack, and lists every reach warning at the end.
- After changing anything in `toolkit/`, run `.venv/bin/python checks.py` (everything must pass) and `.venv/bin/python previews.py` (saves one picture per piece in `previews/`).
