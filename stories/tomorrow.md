# Tomorrow

Film 1. 2:40. Stuck in a depressive cycle, unable to start working on yourself.

**Villain:** his own inner voice, "I'll start tomorrow." Shown as a caption only (no spoken voice), with *tomorrow* in red. No enemy figure; the red clock is the enemy.

**Device:** the day resets to 6:00 and the same morning replays, shorter each time. The whiteboard by the bedroom door holds the cycle: a list of huge goals, and a start day he crosses out in red every evening. At the turn he wipes it and writes five easy things; from then on he ticks boxes instead of crossing out days.

**The two lists:**

| At the start: NEW ME (START: MONDAY) | His attempt (row 10, written over the wiped goals) | After the turn: five easy things |
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

**Final test (133–145 s).** 6:00, rain on the window, the phone lights up with a reel. "I'll start *tomorrow*." the biggest it's been. Shoes on, hand on the door handle, the phone buzzing behind him, the camera shaking. He opens the door and steps into the rain.

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
| 18 | Full board | 85 | 91 | Night: a column of red crossed-out days, no room left | |
| 19 | Dark | 91 | 97 | 3:47, the phone dies, only the red clock glows, the hum fades | |
| 20 | On the floor | 97 | 102 | He sits against the bed facing the board, lit red, breathes out | |
| 21 | Wipe | 102 | 108 | He erases the whole board; the red is gone | |
| 22 | Five things | 108 | 114 | Writes the five easy things with empty boxes, no date | |
| 23 | Day one | 114 | 119 | Up at the alarm / cleans the room (from above) / walks round the block: ticks | |
| 24 | Day one, harder | 119 | 124 | Writes three lines / texts "hey" to Sam, deletes, sends: ticks | |
| 25 | Days after | 124 | 129 | Walk becomes jog, then the gym; notebook fills; Sam replies; one day only two ticks | |
| 26 | Weeks after | 129 | 133 | Jogging further; talking with Sam on a bench | |
| 27 | The pull | 133 | 137 | 6:00, rain on the window, the phone lights up with a reel | "I'll start *tomorrow*." *(biggest)* |
| 28 | The door | 137 | 142 | Shoes on, hand on the handle, the phone buzzing behind him, camera shaking | |
| 29 | Out | 142 | 145 | He opens the door and steps into the rain | |
| 30 | Payoff | 145 | 151 | He runs and keeps going; Sam joins him; the first green: trees | |
| 31 | Mirror | 151 | 155 | Opening shot: clean room, already up, alarm off at once, phone dark; the board: five green ticks | |
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

Rows 1-17 were planned at 85 seconds and run 2:27 at the unhurried pace the user asked for; at that pace the whole film will run well past the 2:40 in the table (the user is fine with longer). The table's start and end times are the original plan.

## Where we are

- **Built:** scene 1, `scenes/wake_up.py` (20 s, rows 1-3; video `films/wake_up.mp4`), and scene 2, `scenes/scroll.py` (12 s, rows 4-5; video `films/scroll.mp4`). The user called these tests that will probably be used in the film. Scene 3, the board: `scenes/the_board.py` (10 s, row 6; video `films/the_board.mp4`), approved by the user. Scene 4, night: `scenes/night.py` (5 s, row 7; video `films/night.mp4`), approved by the user. Scene 5, the reset: `scenes/reset.py` (4 s, row 8; video `films/reset.mp4`), approved by the user. The quote: `scenes/the_quote.py` (5 s, row 7b, plays between the night and the reset; video `films/the_quote.mp4`), approved by the user. Scene 6, up at once: `scenes/up_at_once.py` (5 s, row 9; video `films/up_at_once.mp4`), approved by the user. Row 10, new goals: `scenes/new_goals.py` (32 s; video `films/new_goals.mp4`), rebuilt after the first version (shoes at the door) was rejected; approved by the user. Row 11, too fast: `scenes/too_fast.py` (17 s; video `films/too_fast.mp4`), approved by the user. Row 12, tomorrow again: `scenes/tomorrow_again.py` (13 s; video `films/tomorrow_again.mp4`), not yet seen by the user. Row 13, grind 1: `scenes/grind_1.py` (10 s; video `films/grind_1.mp4`), not yet seen by the user. Row 14, grind 2: `scenes/grind_2.py` (6 s; video `films/grind_2.mp4`), not yet seen by the user. Row 15, grind 3: `scenes/grind_3.py` (4.2 s; video `films/grind_3.mp4`), not yet seen by the user. Row 16, grind 4: `scenes/grind_4.py` (2.2 s; video `films/grind_4.mp4`), not yet seen by the user. Row 17, grind 5: `scenes/grind_5.py` (2 s; video `films/grind_5.mp4`), not yet seen by the user.
- **Not built yet:** everything from row 18 on, and a way to join the scenes into one film.

## Next steps

1. The user to watch the bar with its sounds in the finished scenes (a red flicker as the red line crosses MONDAY; +1 the moment he stands in up at once; +1 a second into the run in too fast) and rows 12 to 17.
2. Build row 18, the full board (night, a column of red crossed-out days, no room left). The days after SATURDAY have to go somewhere: draw options. Ask first about anything else that could go more than one way.
3. Then follow the scene table in order.

## Still open

- "Wake up at 6:00" (his attempt) is close to the turn's "Get up when the alarm rings": maybe reword one at the turn.
- How Sam looks (the joggers are grey, see the style bible).
- The rain in the final test.
- Row 28 still says "Shoes on", but the shoes were dropped (row 10).
- Maybe no bottles in the clean room of the mirror ending (row 31).
- Sound: ElevenLabs for real-world sound effects (rain, the front door, the street, the gym; the marker on the board is done) and for music under the final run. The hum, alarm and clicks come from our own sound kit.
