# Method

The steps we follow for every film, the checks we always run, and every mistake that cost us time, so it never happens twice.

## Steps for every film

_Not decided yet._

## Checks we always run

- The same frame always looks the same. Nothing random may change between runs.
- Any hand or foot that can't reach its target is reported.

## Mistakes that cost time

For each one: what happened, what it cost, and what we do now to avoid it.

- **Hand and foot targets guessed in screen pixels.** Three times while building the toolkit, targets were out of reach and the pose had to be redone. Now: place targets relative to the body (`character.joints(pose)["shoulder"]` or `["hip"]`), and never ignore a "can't reach" warning.
- **The hero floated a few pixels above the floor** (you spotted it in the demo). His resting feet moved with his breathing hips, and the hand-drawn floor line drifted up to 4 px every 3 frames. Now: `stand()` keeps feet planted on the floor, and floors are drawn with `ink.floor(y)`, which never drifts. Checks guard both.
