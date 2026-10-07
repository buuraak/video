"""Film-wide settings and colours. Change a look here and every film follows.

The words behind these numbers live in style-bible.md.
"""

# Format
W, H = 1920, 1080
FPS = 30

# Colours, as (red, green, blue) from 0 to 255.
BG = (14, 14, 17)            # the dark world
INK = (232, 228, 218)        # pale chalk-white lines
GREY = (110, 108, 104)       # quiet details
RED = (210, 32, 40)          # the one accent colour: failure, the enemy
RED_DARK = (95, 8, 14)       # the enemy's dark glow
SCREEN = (178, 208, 255)     # cold blue-white light from screens (his phone)
GREEN = (90, 200, 120)       # a positive colour: only allowed at the end of a film

# Lines
LINE_WIDTH = 7.0             # pen width for the character, in pixels
WOBBLE = 1.6                 # how far hand-drawn lines drift, in pixels
BOIL_EVERY = 3               # lines are re-drawn every 3 frames

# Text
FONT_FAMILY = "Noteworthy"
