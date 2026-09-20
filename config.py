# WINDOW
# --------------------------------------------------------------------
# Size of the game window in pixels. Bigger window = more space to fly.
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
# Frames drawn per second. Higher = smoother (and a bit harder to think).
# Try 10 (choppy / slow-mo) vs 30 (fast).
FPS = 15
WINDOW_TITLE = "Flappy Bird"
# Window title shown at the top of the window.
WINDOW_TITLE = "Flappy Lab"
# --------------------------------------------------------------------
# BIRD PHYSICS  (the heart of the lab)
# BIRD PHYSICS
# --------------------------------------------------------------------
# How hard the bird jumps when you press SPACE or UP.
# Bigger number = higher jump. Try 10, then 30.
JUMP_STRENGTH = 20
SPEED = 20
# How fast the bird falls each frame. Bigger = heavier bird.
# Try 0.5 (moon gravity) vs 5 (lead bird).
GRAVITY = 2.5
# How fast the bird flaps through its 3 wing pictures.
# 1 = every frame, 2 = every other frame. Higher = slower flapping.
FLAP_EVERY_N_FRAMES = 1
# Starting position. 0 is the left / top of the screen.
BIRD_START_X = SCREEN_WIDTH / 6
BIRD_START_Y = SCREEN_HEIGHT / 2
# Scale of the bird sprite. 1.0 = original size, 2.0 = twice as big.
BIRD_SCALE = 1.0
# --------------------------------------------------------------------
# WORLD SPEED
# --------------------------------------------------------------------
# How fast pipes and ground scroll left. Bigger = harder.
# Try 8 (easy stroll) vs 25 (sprint).
GAME_SPEED = 15
# --------------------------------------------------------------------
# PIPES
# --------------------------------------------------------------------
# Gap the bird must fly through, in pixels. Bigger gap = easier.
# Try 80 (tight) vs 250 (highway).
PIPE_GAP = 150
# How wide each pipe is.
PIPE_WIDTH = 80
# How tall the pipe image is (should be taller than the screen).
PIPE_HEIGHT = 500
# Distance from the right edge before the first pipes appear.
# How far in from the right the first pipes appear.
PIPE_SPAWN_OFFSET = 800
# Horizontal space between pipe pairs.

[3 lines collapsed]

PIPE_MIN_HEIGHT = 100
PIPE_MAX_HEIGHT = 300
# How many pipe pairs are on screen at once.
PIPE_PAIRS = 2
# --------------------------------------------------------------------
# GROUND
# --------------------------------------------------------------------
GROUND_WIDTH = 2 * SCREEN_WIDTH
GROUND_HEIGHT = 100
# How much the looping ground overlaps so you don't see a seam.
GROUND_SEAM_OVERLAP = 20
# --------------------------------------------------------------------
# SCORING
# --------------------------------------------------------------------
# Points added each time the bird passes a pipe pair.
POINTS_PER_PIPE = 1
# --------------------------------------------------------------------
# AUDIO
# --------------------------------------------------------------------
# Master volume from 0.0 (silent) to 1.0 (full).
VOLUME = 0.6
# Set False if you are in a quiet classroom and don't want sound.
SOUND_ENABLED = True
# --------------------------------------------------------------------
# LOOKS
# --------------------------------------------------------------------
# Sky, pipe, ground, and bird colors. Use (Red, Green, Blue) 0–255.
SKY_TOP = (78, 192, 202)
SKY_BOTTOM = (196, 232, 236)
PIPE_COLOR = (73, 168, 56)
PIPE_RIM = (46, 115, 36)
GROUND_COLOR = (222, 216, 149)
GROUND_STRIPE = (198, 176, 88)
BIRD_BODY = (255, 204, 0)
BIRD_WING = (255, 160, 40)
BIRD_BEAK = (240, 120, 40)
BIRD_EYE = (40, 40, 40)
# --------------------------------------------------------------------
# CLASSROOM HUD
# Show the current settings on screen so students can connect
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
# The other names overwrite physics so a whole class can switch difficulty
# with a single word.
# Named presets overwrite SPEED, GRAVITY, GAME_SPEED, PIPE_GAP, and FPS.
# --------------------------------------------------------------------
ACTIVE_PRESET = "custom"
PRESETS = {
    "easy": {
        "JUMP_STRENGTH": 18,
        "SPEED": 18,
        "GRAVITY": 1.6,
        "GAME_SPEED": 10,
        "PIPE_GAP": 220,
        "FPS": 15,
    },
    "normal": {
        "JUMP_STRENGTH": 20,
        "SPEED": 20,
        "GRAVITY": 2.5,
        "GAME_SPEED": 15,
        "PIPE_GAP": 150,
        "FPS": 15,
    },
    "hard": {
        "JUMP_STRENGTH": 22,
        "SPEED": 22,
        "GRAVITY": 3.4,
        "GAME_SPEED": 22,
        "PIPE_GAP": 110,
        "FPS": 18,
    },
    "moon": {
        "JUMP_STRENGTH": 12,
        "SPEED": 12,
        "GRAVITY": 0.6,
        "GAME_SPEED": 8,
        "PIPE_GAP": 200,

[10 lines collapsed]

    if name not in PRESETS:
        raise ValueError(
            f'Unknown ACTIVE_PRESET "{ACTIVE_PRESET}". '
            'Use custom, easy, normal, hard, or moon.'
            "Use custom, easy, normal, hard, or moon."
        )
    for key, value in PRESETS[name].items():
        globals()[key] = value
