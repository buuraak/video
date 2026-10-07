# Method

The steps we follow for every film, the checks we always run, and every mistake that cost us time, so it never happens twice.

## Steps for every film

1. **Ask before building.** Go through the scene description and ask about anything that could go more than one way (camera angle, what a word like "red eyes" means, timing, sound). Don't guess.
   When a choice is about how something looks, or feedback is vague ("looks a bit weird"), draw the options side by side in one picture and let the user pick (it worked for the red eyes and his upper body: `sheets/eye_options.png`, `sheets/body_options.png`).
2. **Build the scene.**
3. **Look at it.** Make a contact sheet of the whole scene, look at it yourself and fix what's wrong, then show the user.

## Checks we always run

- The same frame always looks the same. Nothing random may change between runs.
- Any hand or foot that can't reach its target is reported.
- A sound that runs through several scenes (the hum) measures the same loudness in each.

## Mistakes that cost time

For each one: what happened, what it cost, and what we do now to avoid it.

- **Hand and foot targets guessed in screen pixels.** Three times while building the toolkit, targets were out of reach and the pose had to be redone. Now: place targets relative to the body (`character.joints(pose)["shoulder"]` or `["hip"]`), and never ignore a "can't reach" warning.
- **A close-up arm's elbow went off the top of the picture** (film 1, clock shot), twice: it looked fine resting, but rose out of frame when the arm lifted. Now: check the highest point of a moving limb across its whole move, and make a contact sheet of just that stretch (`--start`/`--end`).
- **Curved lines around a head read as cartoon "shaking" lines or a halo** (film 1, pillow creases), twice. Now: don't draw arcs around a character's head unless they're meant to show movement.
- **Seen from above, his arm crossed his face** (film 1, scene 2), three times: tilting his body to reach, an elbow bending upward, and the phone's path passing over his head. Now: in overhead shots, bend elbows down toward the bed and route his hands and anything he carries below his head. If an elbow has to switch sides, ease it over while the arm is almost straight, or it jumps.
- **The dark eyelid patches showed as black bars once light fell on his face** (film 1, scene 2). Now: draw the face first, then add light over it.
- **The hum got louder from scene 1 to scene 2**, because each scene's sound is turned up until its loudest moment hits the top, and scene 2's loudest sound is quieter than scene 1's alarm. Now: measure the hum in each scene (about -26 dB) and set the scene's `PEAK_DB` until it matches.
- **The hero floated a few pixels above the floor** (you spotted it in the demo). His resting feet moved with his breathing hips, and the hand-drawn floor line drifted up to 4 px every 3 frames. Now: `stand()` keeps feet planted on the floor, and floors are drawn with `ink.floor(y)`, which never drifts. Checks guard both.
