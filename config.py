"""
====================================================================
  FLAPPY LAB — STUDENT CONFIG (game mechanics only)
  Change the numbers in this file, then run:  python main.py
  Watch the game (and the on-screen HUD) to see what changed.
====================================================================

Teacher tip: pick ONE variable at a time. Ask students to predict
what will happen before they press Play.

Pictures and sounds live in assets/ and are not generated.
Students should not need to touch those files.
"""

# --------------------------------------------------------------------
# WINDOW
# --------------------------------------------------------------------
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 15
WINDOW_TITLE = "Flappy Bird"

# --------------------------------------------------------------------
# BIRD PHYSICS
# --------------------------------------------------------------------
# How hard the bird jumps when you press SPACE or UP.
# Bigger number = higher jump. Try 10, then 30.
SPEED = 20

# How fast the bird falls each frame. Bigger = heavier bird.
# Try 0.5 (moon gravity) vs 5 (lead bird).
GRAVITY = 2.5

# Starting position. 0 is the left / top of the screen.
BIRD_START_X = SCREEN_WIDTH / 6
BIRD_START_Y = SCREEN_HEIGHT / 2

# --------------------------------------------------------------------
# WORLD SPEED
# --------------------------------------------------------------------
# How fast pipes and ground scroll left. Bigger = harder.
GAME_SPEED = 15

# --------------------------------------------------------------------
# PIPES
# --------------------------------------------------------------------
# Gap the bird must fly through, in pixels. Bigger gap = easier.
PIPE_GAP = 150
PIPE_WIDTH = 80
PIPE_HEIGHT = 500

# How far in from the right the first pipes appear.
PIPE_SPAWN_OFFSET = 800

# Horizontal space between pipe pairs.
PIPE_SPACING = SCREEN_WIDTH

# Random height of the bottom pipe (min and max, in pixels).
PIPE_MIN_HEIGHT = 100
PIPE_MAX_HEIGHT = 300

PIPE_PAIRS = 2

# --------------------------------------------------------------------
# GROUND
# --------------------------------------------------------------------
GROUND_WIDTH = 2 * SCREEN_WIDTH
GROUND_HEIGHT = 100
GROUND_SEAM_OVERLAP = 20

# --------------------------------------------------------------------
# SCORING
# --------------------------------------------------------------------
POINTS_PER_PIPE = 1

# --------------------------------------------------------------------
# CLASSROOM HUD
# Show live mechanics on screen so students can connect
# "I changed GRAVITY" with "the bird falls faster".
# --------------------------------------------------------------------
SHOW_HUD = True
SHOW_START_SETTINGS = True

# Quiet classroom: set SOUND_ENABLED to False.
SOUND_ENABLED = True
VOLUME = 0.6

# --------------------------------------------------------------------
# PRESETS
# Set ACTIVE_PRESET to one of: "custom", "easy", "normal", "hard", "moon"
# "custom" uses ALL the values you typed above.
# Named presets overwrite SPEED, GRAVITY, GAME_SPEED, PIPE_GAP, and FPS.
# --------------------------------------------------------------------
ACTIVE_PRESET = "custom"

PRESETS = {
    "easy": {
        "SPEED": 18,
        "GRAVITY": 1.6,
        "GAME_SPEED": 10,
        "PIPE_GAP": 220,
        "FPS": 15,
    },
    "normal": {
        "SPEED": 20,
        "GRAVITY": 2.5,
        "GAME_SPEED": 15,
        "PIPE_GAP": 150,
        "FPS": 15,
    },
    "hard": {
        "SPEED": 22,
        "GRAVITY": 3.4,
        "GAME_SPEED": 22,
        "PIPE_GAP": 110,
        "FPS": 18,
    },
    "moon": {
        "SPEED": 12,
        "GRAVITY": 0.6,
        "GAME_SPEED": 8,
        "PIPE_GAP": 200,
        "FPS": 15,
    },
}


def apply_preset():
    """Overwrite this module's physics when a named preset is selected."""
    name = (ACTIVE_PRESET or "custom").strip().lower()
    if name == "custom":
        return "custom"
    if name not in PRESETS:
        raise ValueError(
            f'Unknown ACTIVE_PRESET "{ACTIVE_PRESET}". '
            "Use custom, easy, normal, hard, or moon."
        )
    for key, value in PRESETS[name].items():
        globals()[key] = value
    return name


PRESET_NAME = apply_preset()
