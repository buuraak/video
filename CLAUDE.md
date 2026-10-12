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
- Voices in films come from ElevenLabs, with `eleven_speech()` (see the toolkit). The user found the Mac's `say` voices sounded weird and robotic, even muffled (film 1's reels), so `speech()` is only for quick tests.
- ElevenLabs (the user's Creator plan) makes realistic voices, sound effects and music. Its API key is in `.env` (one line, `ELEVENLABS_API_KEY=...`), which is listed in `.gitignore` so it is never uploaded. The key can make audio, list voices and transcribe audio, but can't read account details or the list of models. The account has 21 ready-made voices (Liam and Laura are social-media creators, Adam is firm, Brian is deep, and so on). Speech uses the `eleven_v3` model, where tags like `[excited]` or `[laughs]` steer the delivery. Our plan gets MP3 back (WAV needs a higher plan), converted with ffmpeg. Sound effects come from `eleven_sound()` (see the toolkit). For music there's no helper yet: call `sound._elevenlabs("/music", {...})` the same way. Save every result in `audio/` and reuse it, like `eleven_speech()` and `eleven_sound()` do, so each sound is made once, paid for once, and stays identical. To check what a voice actually said, ElevenLabs can transcribe it back to text (`POST /v1/speech-to-text`, model `scribe_v1`).
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
- `sound.py`: piano, pads, drums and effects, mixed with `Mix` into a WAV. `alarm(seconds)` is a digital alarm clock; `alarm_on(t)` says when its beeps sound, to blink a clock in time with them. `eleven_speech(text, voice)` speaks a line with a realistic ElevenLabs voice (`voice` is the first word of its name, e.g. "Liam") and saves it in `audio/speech/` (made once, identical every run; a check makes sure saved lines never go back to ElevenLabs). `eleven_sound(prompt, seconds, name)` makes a real-world sound effect from a description (a marker squeaking, rain) and saves it in `audio/effects/` the same way. `speech(text, voice)` speaks with a Mac voice, for quick tests only. `muffled()` makes any sound unclear, like mumbling heard through a blanket.
- `anim.py`: `Track` keyframes and easing. `rng.py`: stable randomness. Never use `random` or `hash()`.

`reference/` holds the approved looks, each with its contact sheet and the scene that made it. `style_v2` is current (the hero faces the enemy). `style_v1` is the earlier version where he faced the viewer. Never overwrite them; try changes on copies. `Pose(facing=1)` or `facing=-1` turns a character side-on toward the right or left.

A film is one or more scene files in `scenes/` that define `DURATION`, `draw(canvas, t, frame)`, and optionally `overlay()` for captions and `soundtrack()` for sound. [scenes/demo.py](scenes/demo.py) is a worked example. A scene can set `PEAK_DB` (normally -1) to make its whole soundtrack quieter, so a sound that runs through several scenes, like the hum, stays the same loudness.

Each film's agreed story and scene table lives in `stories/` (film 1: [stories/tomorrow.md](stories/tomorrow.md)).

Film 1's scenes share one bedroom: [scenes/bedroom.py](scenes/bedroom.py) holds the bed, nightstand, clock, phone, blanket, his empty bottles and the mess that grows on the floor through the grind (`draw_mess`: clothes, then cups, then an open pizza box). It is not a scene itself; [scenes/wake_up.py](scenes/wake_up.py) (scene 1), [scenes/scroll.py](scenes/scroll.py) (scene 2) and [scenes/night.py](scenes/night.py) (story row 7) and [scenes/the_quote.py](scenes/the_quote.py) (row 7b) import from it, and so does [scenes/reset.py](scenes/reset.py) (row 8), which reuses scene 1's close-up of the clock. [scenes/up_at_once.py](scenes/up_at_once.py) (row 9) plays scene 2's getting-up moves on a faster clock (`scene2_time()`), so they don't have to be drawn twice. `draw_wall(..., door_open=0.5)` swings the door by the board open onto cold early light, and the board can be partly wiped with its eraser and given new goals (`wiped=`, `new_goals=`; see `draw_board`). [scenes/new_goals.py](scenes/new_goals.py) (row 10) uses all of it, and holds `Walk`, a side-view walk that speeds up, slows down and keeps his feet in reach: reuse it for walks from the side (`facing=-1` walks him to the left). Outside, [scenes/street.py](scenes/street.py) holds the street at dawn (buildings, streetlamps, the pavement), as long as needed so the camera can follow him; [scenes/too_fast.py](scenes/too_fast.py) (row 11) holds `Gait`, a run from the side (sprinting, jogging, slowing to a stop) for him and the grey joggers. `draw_nightstand(..., phone="plugged")` leaves the phone on its charger for the scene to draw itself (lit up, turned over). Likewise [scenes/door_wall.py](scenes/door_wall.py) holds the wall by the bedroom door: the door, and the whiteboard with its goals and its column of start days, drawn small from the side or close up from the front. [scenes/the_board.py](scenes/the_board.py) (story row 6) and [scenes/tomorrow_again.py](scenes/tomorrow_again.py) (row 12, where he stands right of the board) use it, and so will every later board scene. `BoardArm` in tomorrow_again.py is his close-up arm from the bottom right crossing out a day and writing the next: [scenes/grind_1.py](scenes/grind_1.py) (row 13) reuses it, and holds `draw_scrolling()`, him scrolling in bed from above at any time with any mess, which [scenes/grind_2.py](scenes/grind_2.py) (row 14) reuses too. grind_2.py holds `draw_clock()`, the alarm clock from the front showing any time, which [scenes/grind_3.py](scenes/grind_3.py) (row 15) reuses with the rest, and [scenes/grind_4.py](scenes/grind_4.py) (row 16) too. `draw_close_face()` in the_quote.py is his face from above, close, lit by the phone at any brightness: [scenes/grind_5.py](scenes/grind_5.py) (row 17) reuses it. From FRIDAY on the board's red strokes get sloppier down the column (`careless()` in door_wall.py), so every board scene shows them the same.

Every scene of film 1 draws the discipline bar from [scenes/discipline.py](scenes/discipline.py) in its `overlay()`: `Discipline(start=, fills=[...], drains=[...], flickers=[...])` says how full it is when the scene starts and when it fills, drains or flickers. A new scene starts where the scene before ended.

- Contact sheet (12 frames in one picture): `.venv/bin/python contact_sheet.py scenes/x.py --start 0 --end 5`. Saves to `sheets/`. Also works on a video in `films/`.
- Render: `.venv/bin/python render.py scenes/x.py`. Saves to `films/`. It draws frames in parallel, adds the soundtrack, and lists every reach warning at the end.
- After changing anything in `toolkit/`, run `.venv/bin/python checks.py` (everything must pass) and `.venv/bin/python previews.py` (saves one picture per piece in `previews/`).
