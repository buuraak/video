# Tomorrow

Film 1. 2:40. Stuck in a depressive cycle, unable to start working on yourself.

**Villain:** his own inner voice, "I'll start tomorrow." Shown as a caption only (no spoken voice), with *tomorrow* in red. No enemy figure; the red clock is the enemy.

**Device:** the day resets to 6:00 and the same morning replays, shorter each time. The whiteboard by the bedroom door holds the cycle: a list of huge goals, and a start day he crosses out in red every evening. At the turn he wipes it and writes five easy things; from then on he ticks boxes instead of crossing out days.

**The two lists:**

| At the start: NEW ME (START: MONDAY) | His attempt (row 10, written over the wiped goals) | After the turn: TODAY, five easy things |
|---|---|---|
| Make $1,000,000 | Run 2x a week | Get up when the alarm rings |
| Buy a Bugatti | Go to the gym | Clean your room |
| Own a yacht | Stay sober | Go for a walk |
| Run a marathon | Wake up at 6:00 | Write 3 lines |
| Six-pack by summer |  | Text one person |

**The discipline bar** (the user's idea): a hand-drawn bar like a health bar, labelled DISCIPLINE, in the top black bar, there from the very first scene. It's a smooth fill (the user's pick from `sheets/discipline_options.png`); the code is `scenes/discipline.py`. The rules:

- It fills only when he actually does something he set out to do: one equal notch per action (getting up at the alarm, going out for the run, cleaning, writing, texting someone).
- Feeling motivated or making plans does nothing (the quote, writing goals on the board).
- It empties only when he quits: every "I'll start tomorrow" (crossing out a day) drains it to empty with a red flash. A bad day doesn't empty it.
- It turns green only when it's full, at the end.
- It makes a distinct sound when it fills and when it empties (the user: without one, nobody notices it). Picked from `films/bar_sound_options.mp4`: filling, a tone that rises with the bar and ends on a bright ping; emptying, a buzzy tone falling away like a machine switching off (also on a red flicker).

| Rows | The bar |
|---|---|
| 1-8 (waking up to the reset) | Empty. A red flicker when he crosses out MONDAY (row 6). Still empty after the quote (7b): feeling motivated isn't doing, and this teaches the viewer the rule |
| 9, up at once | +1 when he gets straight up |
| 10, new goals | No change: writing goals is planning |
| 11, too fast | +1 when he goes out running. It stays, even though he fails |
| 12, tomorrow again | Drains to empty with a red flash when he crosses out TUESDAY |
| 13-22 (the grind to the turn) | Empty; a red flicker on each crossed-out day |
| 23-26, practice | +1 per tick, slowly. It never drains: the two-tick day still adds 2 |
| 27-28, the pull and the door | It shakes |
| 29, out | +1 when he opens the door |
| 30, payoff | Fills up and turns green on the run |
| 31, mirror | Full and green |

**His drinking:** empty bottles are in the bedroom from the very first shot (the user's idea), so "Stay sober" on his attempt list makes sense: one tipped over on the nightstand by the clock, one on the floor by the bed.

The big goals match what the muffled reel voices on his phone talk about: the feed sells the dream, and the dream is too big to start.

## Beats

**Wound (0–38 s).** Scene 1: restless sleep, 5:59, the alarm, his eyes open. Scene 2, shortened: the phone, the scrolling, he gets up and walks out. By the bedroom door, the board: NEW ME and the huge goals, START: MONDAY. His hand crosses out MONDAY in red and writes TUESDAY. "I'll start *tomorrow*."

**Stakes (38–47 s).** Night, in bed. His phone lights up: "Sam: you coming tonight?" He turns it face down. 23:59 snaps back to 6:00 with a rewind sound.

**Attempt (47–66 s).** He's up the second the alarm rings, goes to the board, wipes off the huge goals and writes smaller ones, and smiles. He goes outside and sprints, and after a few seconds he's gasping and doubled over while joggers pass him. At the board he crosses out TUESDAY and writes WEDNESDAY. "*Tomorrow*."

**Grind montage (66–85 s).** The loop, shorter each time: the alarm later (7:40, 9:55, 12:20, 14:05), his face in the phone light, Sam's messages unanswered, another day crossed out. Seen from above, the room gets messier each loop: clothes, cups, a pizza box.

**Rock bottom (85–102 s).** The board is a column of red crossed-out days with no room left. 3:47: the phone dies; only the red clock glows; the hum fades. He sits on the floor against the bed, facing the board, and breathes out.

**Turn (102–114 s).** He looks at the huge goals and the wall of red, wipes the whole board clean, and writes the five easy things with an empty box beside each. No date.

**Practice (114–133 s).** Day one: up at the alarm, he cleans the room (the mess goes, seen from above), walks round the block, writes three lines, types "hey" to Sam, deletes it, sends it: ticks. Days after: the walk becomes a jog, then the gym; the notebook fills; Sam replies. One day only two ticks. Weeks after: jogging further; talking with Sam on a bench.

**Final test (133–145 s).** 6:00, rain on the window, the phone lights up with a reel. "I'll start *tomorrow*." the biggest it's been. He walks to the door past the board, hand on the door handle, the phone buzzing behind him, the camera shaking. He opens the door and steps into the rain.

**Payoff (145–151 s).** He runs, the run he failed at the start, and doesn't stop. Sam falls in beside him. The rain thins; the film's first green: trees in the park.

**Mirror ending (151–155 s).** The opening shot from above at 5:59: the room is clean and he's already up, sitting on the edge of the bed in his shoes. The alarm rings and he switches it off at once; the phone stays dark. The board: five ticks in green.

**Title card (155–160 s).** TOMORROW. *You don't need a new you. / Just one small thing, today.*

## Scene table

| # | Scene | Start | End | What happens | Caption |
|---|---|---|---|---|---|
| 1 | Asleep | 0 | 8 | Fade in, restless sleep, 5:59 *(scene 1)* | |
| 2 | Alarm | 8 | 15 | 6:00, beeps, arm presses the button *(scene 1)* | |
| 3 | Eyes open | 15 | 20 | His face from above *(scene 1)* | |
| 4 | The phone | 20 | 26 | Reach, unplug, scroll *(scene 2, shortened)* | |
| 5 | Out of bed | 26 | 32 | Drops the phone, gets up, walks out *(scene 2, shortened)* | |
| 6 | The board | 32 | 42 | NEW ME and the huge goals; crosses out MONDAY in red, writes TUESDAY | "I'll start *tomorrow*." |
| 7 | Night | 38 | 43 | Close-up of the phone from above: Sam's message lights up the lock screen. Cut to the bedroom from above at night: he reaches over and turns it face down; the room goes dark | |
| 7b | The quote | 43 | 48 | Later that night (23:58) he can't sleep and is scrolling again. A reel: a smug stick-figure man in a suit, and under him in big bold words "What are you waiting for?" (no voice: the viewer reads it). His sad face, lit by the phone; the camera zooms in fast with a deep hit and it turns determined | |
| 8 | Reset | 43 | 47 | The clock from the front: 23:59, the numbers race backwards and slam onto 6:00 with a rewind sound; the alarm goes off and keeps ringing into row 9 | |
| 9 | Up at once | 47 | 51 | Still on the clock: his arm shoots in and slams the alarm off at once (the opposite of scene 1's slow press). Cut to above: determined face (eyes wide, brows set, mouth a firm line, still the bags; `sheets/face_options.png`, option 2), blanket off, up and briskly out to the right | |
| 10 | New goals | 51 | 55 | From the side, unhurried: he walks to the board and looks at the huge goals. Close-up: he wipes the goals off with the board's eraser (NEW ME and the start days stay) and writes four new ones in their place: Run 2x a week / Go to the gym / Stay sober / Wake up at 6:00 (the user's wording; still too much for him, the truly tiny five things come at the turn). Not crossed out in red: the user found that made no sense. He steps back, looks at it and smiles, his first smile. Then he goes out of the door. No shoes, no gym bag | |
| 11 | Too fast | 55 | 61 | The street at dawn, from the side: he sprints in from the left, the camera running with him; he fades, staggers to a stop and doubles over, hands on knees, gasping, his breath puffing in the cold. Two grey joggers pass him at an easy pace without looking. He lifts his head, watches them go, and sags | |
| 12 | Tomorrow again | 61 | 66 | He comes back in through the door from the failed run, out of breath, head hanging; the door shuts behind him and he sags at the board. Close-up: his arm comes up from the bottom right (he stands right of the board), crosses out TUESDAY in red (the bar drains) and writes WEDNESDAY | "*Tomorrow*." |
| 13 | Grind 1 | 66 | 71 | From above, as in the opening shot: the clock already says 7:40 (he slept through the alarm) and he's scrolling in bed, the phone's cold light on his face; a T-shirt and jeans lie on the floor. Close-up of his screen: a reel, and Sam's message slides in, "haven't seen you in ages"; his thumb flicks it away and swipes on. The board close up: no hesitation now, his arm crosses out WEDNESDAY (the bar flickers red), and a jump cut, closer, shows him writing THURSDAY (it skips putting the markers back). About 10 s | "*Tomorrow*." |
| 14 | Grind 2 | 71 | 76 | One second on the alarm clock from the front, silent: 9:55. From above: he's scrolling, cups now beside the clothes on the floor; the phone buzzes in his hands (Sam again; we can't read it), the light on his face flares, and he doesn't react. The board close up: one quick red stroke through THURSDAY (the bar flickers red), cut; FRIDAY is already written the next time we see the board. About 6 s | |
| 15 | Grind 3 | 76 | 80 | Row 14's three shots, shorter. Under a second on the alarm clock from the front, silent: 12:20. From above: he's scrolling; an open pizza box now lies on the floor by the bed, crusts and one slice left, beside the clothes and cups (`sheets/pizza_options.png`, option 2). Nothing from Sam this time, only reels: Sam has stopped trying, so later he has to be the one to reach out. The board close up: a careless red slash through FRIDAY, quicker and crooked, running past the end of the word (the bar flickers red). From here on each stroke is sloppier than the last, so the full board (row 18) shows them getting messier down the column. About 4 s | |
| 16 | Grind 4 | 80 | 83 | Two shots now, the bed shot drops out: the days are blurring together. The alarm clock from the front, silent: 14:05. The board close up, SATURDAY already written (the last line with room on it): an even more careless slash through it (the bar flickers red), cut. Where the next days go is decided at the full board (row 18). About 2.5 s | |
| 17 | Grind 5 | 83 | 85 | Only his face in the phone light: the quote's close-up from above again (the shot where he once turned determined), now numb: no frown, flat brows, heavy lids (`sheets/face_light_options.png`, A and 2). He swipes faster and faster, three or four swipes, each one a flash of light on his face, the muffled reel voices cutting each other off: the scrolling has taken over. The grind ends on its fastest beat. About 2 s | |
| 18 | Full board | 85 | 91 | Night, about a month on. The days have run out of the START column, down the middle of the board, under his goals and over them, smaller and more crooked, until his goals are nearly buried in red (`sheets/full_board_options.png`, option 3). Close up: his arm crosses out the last day, squeezed in at the bottom, then lifts the pale marker to write the next one, and there's no room left anywhere: the marker hovers, and he lowers it. Then the camera slowly pulls back to the whole board in the dark. About 9 s | |
| 19 | Dark | 91 | 97 | 3:47. His screen up close (as in row 13): a reel plays, a low-battery warning slides down (1%, a small red battery), and the screen goes black. Cut to the room from above: dark, he slowly lowers the dead phone onto his chest and lies still, staring up, numb. Only the small red clock glows on the nightstand, its faint red light falling on him. The hum fades to silence | |
| 20 | On the floor | 97 | 102 | From behind him (`sheets/floor_options.png`, B): he sits on the floor against the bed, the back of his head and his slumped shoulders big in the foreground, and across the dark room the board with its wall of red, everything faintly lit red by the clock. In the silence, a long, slow breath out: his shoulders drop and his head sinks, then slowly lifts to the board again. Still tired, but no longer frozen: something lets go, the first moment of the turn | |
| 21 | Wipe | 102 | 108 | Straight from row 20 to the board up close, still night, faintly red: his arm comes in with the eraser and wipes the whole board clean, NEW ME too (he isn't trying to become a new person any more: 'You don't need a new you'). Line by line from the top: the first strokes slow and heavy, then steadier and quicker as the red goes. At the end the camera pulls back to the clean board in the dark. About 10 s | |
| 22 | Five things | 108 | 114 | Still night, faintly red, the board up close. At the top, where NEW ME and START: were, he writes TODAY (not a date: the answer to 'tomorrow'). Then the five easy things, each with an empty box before it: he draws the first box and writes 'Get up when the alarm rings' letter by letter, carefully; then quick jump cuts as the list grows, each landing on the next line being finished; then we hold on the full list to read it. About 11 s | |
| 23 | Day one | 114 | 119 | Three tasks, each followed by a quick cut to the board as his arm ticks its box and the bar fills one step with its sound. The alarm at 6:00, as in the loop: this time he gets up calmly (switches it off, lies a moment, gets up; not row 9's burst). Then he cleans the room, sped up, from above, the clock racing: clothes, cups, the pizza box and his empty bottles all go (the bottles going says 'Stay sober' without a word). Then he walks round the block: the street from the side, in the morning, at an easy pace; the same two grey joggers pass him as in row 11, and this time he doesn't try to keep up | |
| 24 | Day one, harder | 119 | 124 | As in row 23, each thing followed by a tick on the board and a step on the bar. His notebook up close, a dark page with pale ink like the board (`sheets/notebook_chat_options.png`, 1): he writes three lines, how he feels: "Still tired. / But I got up. / That's a start." Then his phone up close, Sam's chat: Sam's three unanswered messages, "you coming tonight?", "haven't seen you in ages" and the one he never read in row 14, "miss you man". He types "hey", deletes it, types it again and sends it; "Delivered" appears, he looks at it a moment and puts the phone down. No reply yet: Sam answers in row 25. Then all five boxes ticked | |
| 25 | Days after | 124 | 129 | Three quick days, each opening on the 6:00 clock and closing on the board ticked off in a fast run, the bar stepping up (from 5 to about 17 of its 20 steps). Day 2: he jogs. Day 3, the hard day: at night the board has only two ticks; his hand drifts toward the red marker on the tray, stops, and leaves it: no crossing out, and the bar still gets its two steps. Day 4: one short shot in a simple dark gym (he lifts a dumbbell, steady); his notebook flipped through, pages already full of his lines, landing on today's; and Sam replies: "hey you!! walk tomorrow?" | |
| 26 | Weeks after | 129 | 133 | Jogging further: the same two grey joggers who passed him twice, and now he jogs alongside them at their pace, all three together. Then he and Sam on a bench by the street, from the front, waist up: they talk and both laugh once (no words and no laughter heard, only the street: the user found the laugh's sound ugly). Sam is pale like him, with messy hair (`sheets/sam_options.png`, 3). The board: he ticks "Text one person"; the bar goes from 17 to 18 | |
| 27 | The pull | 133 | 137 | 6:00. His bedroom window up close, from inside: rain running down the glass, the grey dawn outside, the sound of rain. The clean room from above: he sits on the edge of the bed, and his phone, face up on the nightstand, lights up by itself: the smug man's reel plays, muffled, glowing; the old hum creeps back in under the rain. The phone close up, the reel calling. Then the room darkens and the caption fills the picture, the one time it leaves the black bar (`sheets/caption_options.png`, 3); the bar starts to shake | "I'll start *tomorrow*." *(biggest)* |
| 28 | The door | 137 | 142 | No shoes, nothing to put on: from the side, he walks to the door as he is, past the board, and stops at it for a beat: TODAY and five empty boxes. On to the door. His hand on the handle up close, trembling with the camera; behind him the phone buzzes (we hear it over the rain, and its cold light flickers in from the edge with each buzz); his face, eyes closing, a long breath in. The bar trembles, the hum is on. Cut: he opens it in row 29 | |
| 29 | Out | 142 | 145 | His face close (as row 28 ended): his eyes open, steady, no smile yet (the smile is kept for the run). From just behind him: he pushes the door open onto a city street leading away between buildings in the grey rain (not a flat colour: the user's note), and the instant it opens the hum cuts dead, the rain rushes in loud and clear, the bar stops trembling and fills its 19th step. He walks out and away down the street, naturally (the user's note), and outside stands a moment in the rain, face turned up into it, breathing. Cut to the run | |
| 30 | Payoff | 145 | 151 | The street in the thinning rain, from the side, the camera running with him: he runs, steady, the run he failed at the start, and keeps going. Sam waits at a corner ahead, raises a hand, and falls in beside him without stopping (they planned it). He smiles, the first since row 10. They run into the park as the rain stops: the trees' leaves come up a soft, muted green, the film's first green, and the bar fills its last step and turns green with them (grass and everything else stay grey). The film's first music, warm and hopeful (piano, soft strings, from ElevenLabs), starts quietly and swells with the green. Ends on a wide shot: the two of them running away along the park path between the green trees, small, still going | |
| 31 | Mirror | 151 | 155 | The opening shot from above, exactly: 5:59, but the room is clean (no mess, no bottles: they went in row 23), the bed made, and he's already up, sitting on the nightstand side of the bed. 6:00: one beep, and his hand presses it straight away. The phone stays dark. Then a quiet last shot of the board: TODAY and five ticks in green, as the payoff's music fades out. No arm. The bar full and green | |
| 32 | Title card | 155 | 160 | TOMORROW | *You don't need a new you. / Just one small thing, today.* |

Total: 160 seconds. Row 6 grew from 6 to 10 seconds (6 was far too fast), and row 7b (the quote, about 5 s) was added afterwards to give him a reason for his attempt (the user's idea, inspired by a similar video where a quote on a billboard is followed by a fast zoom on the hero's face). So the rows after them start about 9 seconds later and the film runs about 2:49. The user is fine with it running a bit longer: no need to win the time back.

## The film so far, in order

| # | Scene | Rows | File | Runs |
|---|---|---|---|---|
| 1 | Waking up | 1-3 | `scenes/wake_up.py` | 0:00-0:20 |
| 2 | Scrolling | 4-5 | `scenes/scroll.py` | 0:20-0:32 |
| 3 | The board | 6 | `scenes/the_board.py` | 0:32-0:42 |
| 4 | Night | 7 | `scenes/night.py` | 0:42-0:47 |
| 5 | The quote | 7b | `scenes/the_quote.py` | 0:47-0:52 |
| 6 | The reset | 8 | `scenes/reset.py` | 0:52-0:56 |
| 7 | Up at once | 9 | `scenes/up_at_once.py` | 0:56-1:01 |
| 8 | New goals | 10 | `scenes/new_goals.py` | 1:01-1:33 |
| 9 | Too fast | 11 | `scenes/too_fast.py` | 1:33-1:50 |
| 10 | Tomorrow again | 12 | `scenes/tomorrow_again.py` | 1:50-2:03 |
| 11 | Grind 1 | 13 | `scenes/grind_1.py` | 2:03-2:13 |
| 12 | Grind 2 | 14 | `scenes/grind_2.py` | 2:13-2:19 |
| 13 | Grind 3 | 15 | `scenes/grind_3.py` | 2:19-2:23 |
| 14 | Grind 4 | 16 | `scenes/grind_4.py` | 2:23-2:25 |
| 15 | Grind 5 | 17 | `scenes/grind_5.py` | 2:25-2:27 |
| 16 | Full board | 18 | `scenes/full_board.py` | 2:27-2:39 |
| 17 | Dark | 19 | `scenes/dark.py` | 2:39-2:47 |
| 18 | On the floor | 20 | `scenes/on_the_floor.py` | 2:47-2:55 |
| 19 | The wipe | 21 | `scenes/wipe.py` | 2:55-3:09 |
| 20 | Five things | 22 | `scenes/five_things.py` | 3:09-3:23 |
| 21 | Day one | 23 | `scenes/day_one.py` | 3:23-3:48 |
| 22 | Day one, harder | 24 | `scenes/day_one_harder.py` | 3:48-4:08 |
| 23 | Days after | 25 | `scenes/days_after.py` | 4:08-4:31 |
| 24 | Weeks after | 26 | `scenes/weeks_after.py` | 4:31-4:44 |
| 25 | The pull | 27 | `scenes/the_pull.py` | 4:44-4:57 |
| 26 | The door | 28 | `scenes/the_door.py` | 4:57-5:08 |
| 27 | Out | 29 | `scenes/out.py` | 5:08-5:17 |
| 28 | The payoff | 30 | `scenes/payoff.py` | 5:17-5:37 |
| 29 | The mirror | 31 | `scenes/mirror.py` | 5:37-5:48 |

Rows 1-31 were planned at 155 seconds and run 5:48 at the unhurried pace the user asked for; at that pace the whole film will run well past the 2:40 in the table (the user is fine with longer). The table's start and end times are the original plan.

## Where we are

- **Built:** scene 1, `scenes/wake_up.py` (20 s, rows 1-3; video `films/wake_up.mp4`), and scene 2, `scenes/scroll.py` (12 s, rows 4-5; video `films/scroll.mp4`). The user called these tests that will probably be used in the film. Scene 3, the board: `scenes/the_board.py` (10 s, row 6; video `films/the_board.mp4`), approved by the user. Scene 4, night: `scenes/night.py` (5 s, row 7; video `films/night.mp4`), approved by the user. Scene 5, the reset: `scenes/reset.py` (4 s, row 8; video `films/reset.mp4`), approved by the user. The quote: `scenes/the_quote.py` (5 s, row 7b, plays between the night and the reset; video `films/the_quote.mp4`), approved by the user. Scene 6, up at once: `scenes/up_at_once.py` (5 s, row 9; video `films/up_at_once.mp4`), approved by the user. Row 10, new goals: `scenes/new_goals.py` (32 s; video `films/new_goals.mp4`), rebuilt after the first version (shoes at the door) was rejected; approved by the user. Row 11, too fast: `scenes/too_fast.py` (17 s; video `films/too_fast.mp4`), approved by the user. Row 12, tomorrow again: `scenes/tomorrow_again.py` (13 s; video `films/tomorrow_again.mp4`), not yet seen by the user. Row 13, grind 1: `scenes/grind_1.py` (10 s; video `films/grind_1.mp4`), not yet seen by the user. Row 14, grind 2: `scenes/grind_2.py` (6 s; video `films/grind_2.mp4`), not yet seen by the user. Row 15, grind 3: `scenes/grind_3.py` (4.2 s; video `films/grind_3.mp4`), not yet seen by the user. Row 16, grind 4: `scenes/grind_4.py` (2.2 s; video `films/grind_4.mp4`), not yet seen by the user. Row 17, grind 5: `scenes/grind_5.py` (2 s; video `films/grind_5.mp4`), not yet seen by the user. Row 18, the full board: `scenes/full_board.py` (11.5 s; video `films/full_board.mp4`), not yet seen by the user. Row 19, dark: `scenes/dark.py` (8 s; video `films/dark.mp4`), not yet seen by the user. Row 20, on the floor: `scenes/on_the_floor.py` (8 s; video `films/on_the_floor.mp4`), not yet seen by the user. Row 21, the wipe: `scenes/wipe.py` (14 s; video `films/wipe.mp4`), not yet seen by the user. Row 22, five things: `scenes/five_things.py` (13.7 s; video `films/five_things.mp4`), not yet seen by the user. Row 23, day one: `scenes/day_one.py` (25 s; video `films/day_one.mp4`), not yet seen by the user. Row 24, day one, harder: `scenes/day_one_harder.py` (20 s; video `films/day_one_harder.mp4`), not yet seen by the user. Row 25, days after: `scenes/days_after.py` (23.4 s; video `films/days_after.mp4`), not yet seen by the user. Row 26, weeks after: `scenes/weeks_after.py` (12.8 s; video `films/weeks_after.mp4`), not yet seen by the user. Row 27, the pull: `scenes/the_pull.py` (12.6 s; video `films/the_pull.mp4`), not yet seen by the user. Row 28, the door: `scenes/the_door.py` (11.4 s; video `films/the_door.mp4`), not yet seen by the user. Row 29, out: `scenes/out.py` (9 s; video `films/out.mp4`), rebuilt after the user's notes. Row 30, the payoff: `scenes/payoff.py` (20 s; video `films/payoff.mp4`), not yet seen by the user. Row 31, the mirror: `scenes/mirror.py` (11 s; video `films/mirror.mp4`), not yet seen by the user.
- **Not built yet:** row 32 (the title card), and a way to join the scenes into one film.

## Next steps

1. The user to watch the bar with its sounds in the finished scenes (a red flicker as the red line crosses MONDAY; +1 the moment he stands in up at once; +1 a second into the run in too fast) and rows 12 to 31.
2. Build row 32, the title card (TOMORROW; You don't need a new you. / Just one small thing, today.): ask first about anything that could go more than one way.
3. Then join all the scenes into the one film (and smooth the hum across the cuts).
3. Then follow the scene table in order.

## Still open

