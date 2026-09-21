"""
====================================================================
  FLAPPY LAB — edit THIS file, then run:  python arcade.py
  Change one number at a time. The HUD on screen shows your values.
====================================================================

Teacher tip: pick ONE variable, ask students to predict, then run.
"""

# --------------------------------------------------------------------
# WINDOW
# --------------------------------------------------------------------
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Flappy Bird Clone"

# --------------------------------------------------------------------
# BIRD PHYSICS
# Arcade's Y axis points UP, so gravity is a negative number.
# More negative = falls faster. Try -0.2 (floaty) vs -1.5 (heavy).
# --------------------------------------------------------------------
GRAVITY = -0.5

# How hard the bird jumps when you press SPACE.
# Bigger number = higher flap. Try 4, then 12.
JUMP_SPEED = 8

# Size of the yellow bird square, in pixels.
BIRD_SIZE = 30

# Starting position.
BIRD_START_X = SCREEN_WIDTH // 4
BIRD_START_Y = SCREEN_HEIGHT // 2

# --------------------------------------------------------------------
# PIPES
# --------------------------------------------------------------------
# How fast pipes move left. Bigger = harder.
PIPE_SPEED = 4

PIPE_WIDTH = 70

# Gap the bird flies through. Bigger gap = easier.
# Try 120 (tight) vs 300 (easy).
GAP_SIZE = 200

# Frames between new pipe pairs. Bigger = more space between pipes.
SPAWN_INTERVAL = 100

# Keep the gap away from the floor and ceiling by this many pixels.
GAP_MARGIN = 50

# --------------------------------------------------------------------
# SCORING
# --------------------------------------------------------------------
POINTS_PER_PIPE = 1

# --------------------------------------------------------------------
# CLASSROOM HUD
# --------------------------------------------------------------------
SHOW_HUD = True

# --------------------------------------------------------------------
# PRESETS
# Set ACTIVE_PRESET to "custom", "easy", "normal", "hard", or "moon".
# "custom" uses the numbers you typed above.
# --------------------------------------------------------------------
ACTIVE_PRESET = "custom"

PRESETS = {
    "easy": {
        "GRAVITY": -0.25,
        "JUMP_SPEED": 7,
        "PIPE_SPEED": 3,
        "GAP_SIZE": 280,
        "SPAWN_INTERVAL": 130,
    },
    "normal": {
        "GRAVITY": -0.5,
        "JUMP_SPEED": 8,
        "PIPE_SPEED": 4,
        "GAP_SIZE": 200,
        "SPAWN_INTERVAL": 100,
    },
    "hard": {
        "GRAVITY": -0.8,
        "JUMP_SPEED": 9,
        "PIPE_SPEED": 6,
        "GAP_SIZE": 140,
        "SPAWN_INTERVAL": 80,
    },
    "moon": {
        "GRAVITY": -0.12,
        "JUMP_SPEED": 5,
        "PIPE_SPEED": 2,
        "GAP_SIZE": 260,
        "SPAWN_INTERVAL": 140,
    },
}


def apply_preset():
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

# --- game code below: students usually do not need to edit this ----------

import os
import random
import sys

# This file is named arcade.py, so Python would otherwise import *this* file
# instead of the Arcade library. Put the script folder at the end of sys.path
# so `import arcade` loads the installed package.
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if sys.path and os.path.abspath(sys.path[0] or ".") in {
    _SCRIPT_DIR,
    os.path.abspath(os.getcwd()),
}:
    sys.path.append(sys.path.pop(0))

import arcade


class Pipe(arcade.SpriteSolidColor):
    def __init__(self, width: int, height: int, color) -> None:
        # Arcade 3 needs color= as a keyword. Passing it as the 3rd
        # positional argument would be read as center_x and crash.
        super().__init__(width, height, color=color)
        self.passed = False


class FlappyBird(arcade.Window):
    def __init__(self) -> None:
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.SKY_BLUE)

        self.bird = None
        self.bird_list = None
        self.pipes = None
        self.score = 0
        self.frames = 0
        self.game_over = False

    def setup(self) -> None:
        self.bird_list = arcade.SpriteList()

        self.bird = arcade.SpriteSolidColor(
            BIRD_SIZE,
            BIRD_SIZE,
            color=arcade.color.YELLOW,
        )
        self.bird.center_x = BIRD_START_X
        self.bird.center_y = BIRD_START_Y
        self.bird.change_y = 0
        self.bird_list.append(self.bird)

        self.pipes = arcade.SpriteList()
        self.score = 0
        self.frames = 0
        self.game_over = False
        self.spawn_pipes()

    def on_draw(self) -> None:
        self.clear()
        self.bird_list.draw()
        self.pipes.draw()

        arcade.draw_text(
            f"Score: {int(self.score)}",
            20,
            SCREEN_HEIGHT - 40,
            arcade.color.WHITE,
            24,
            bold=True,
        )

        if SHOW_HUD:
            hud = [
                f"preset: {PRESET_NAME}",
                f"GRAVITY: {GRAVITY}",
                f"JUMP_SPEED: {JUMP_SPEED}",
                f"PIPE_SPEED: {PIPE_SPEED}",
                f"GAP_SIZE: {GAP_SIZE}",
                f"SPAWN_INTERVAL: {SPAWN_INTERVAL}",
            ]
            y = SCREEN_HEIGHT - 70
            for line in hud:
                arcade.draw_text(line, 20, y, arcade.color.DARK_BLUE, 12, bold=True)
                y -= 16

        if self.game_over:
            arcade.draw_text(
                "GAME OVER",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 + 50,
                arcade.color.RED,
                50,
                anchor_x="center",
                bold=True,
            )
            arcade.draw_text(
                "Press SPACE to Restart",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT // 2 - 20,
                arcade.color.WHITE,
                20,
                anchor_x="center",
            )

    def spawn_pipes(self) -> None:
        low = GAP_SIZE + GAP_MARGIN
        high = SCREEN_HEIGHT - GAP_SIZE - GAP_MARGIN
        if high <= low:
            center_y = SCREEN_HEIGHT // 2
        else:
            center_y = random.randint(int(low), int(high))

        bottom_pipe = Pipe(PIPE_WIDTH, SCREEN_HEIGHT, arcade.color.GREEN)
        bottom_pipe.center_x = SCREEN_WIDTH + PIPE_WIDTH // 2
        bottom_pipe.top = center_y - GAP_SIZE // 2
        bottom_pipe.change_x = -PIPE_SPEED
        self.pipes.append(bottom_pipe)

        top_pipe = Pipe(PIPE_WIDTH, SCREEN_HEIGHT, arcade.color.GREEN)
        top_pipe.center_x = SCREEN_WIDTH + PIPE_WIDTH // 2
        top_pipe.bottom = center_y + GAP_SIZE // 2
        top_pipe.change_x = -PIPE_SPEED
        self.pipes.append(top_pipe)

    def on_update(self, delta_time: float) -> None:
        if self.game_over:
            return

        self.bird.change_y += GRAVITY
        self.bird.center_y += self.bird.change_y

        self.pipes.update()

        self.frames += 1
        if self.frames % max(1, int(SPAWN_INTERVAL)) == 0:
            self.spawn_pipes()

        for pipe in self.pipes:
            if pipe.right < 0:
                pipe.remove_from_sprite_lists()
            elif pipe.right < self.bird.left and not pipe.passed:
                pipe.passed = True
                self.score += POINTS_PER_PIPE / 2

        if (
            arcade.check_for_collision_with_list(self.bird, self.pipes)
            or self.bird.bottom < 0
            or self.bird.top > SCREEN_HEIGHT
        ):
            self.game_over = True

    def on_key_press(self, key, modifiers) -> None:
        if key == arcade.key.ESCAPE:
            arcade.close_window()
            return
        if key == arcade.key.SPACE:
            if self.game_over:
                self.setup()
            else:
                self.bird.change_y = JUMP_SPEED


def main() -> None:
    game = FlappyBird()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
