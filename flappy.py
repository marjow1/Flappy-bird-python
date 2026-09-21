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

# Bird width in pixels. Height follows the sprite's real aspect ratio
# (do not squash it into a square). Native art is 34px wide.
BIRD_SIZE = 34

# Starting position.
BIRD_START_X = SCREEN_WIDTH // 4
BIRD_START_Y = SCREEN_HEIGHT // 2

# --------------------------------------------------------------------
# PIPES
# --------------------------------------------------------------------
# How fast pipes move left. Bigger = harder.
PIPE_SPEED = 4

# Native pipe art is 52x320. These sizes keep that ratio (~80x500).
PIPE_WIDTH = 80
PIPE_HEIGHT = 500

# Gap the bird flies through. Bigger gap = easier.
# Try 120 (tight) vs 300 (easy).
GAP_SIZE = 200

# Frames between new pipe pairs. Bigger = more space between pipes.
SPAWN_INTERVAL = 100

# Keep the gap away from the floor and ceiling by this many pixels.
GAP_MARGIN = 50

# --------------------------------------------------------------------
# GROUND
# Same tiling size as the original pygame clone.
# --------------------------------------------------------------------
GROUND_WIDTH = 2 * SCREEN_WIDTH
GROUND_HEIGHT = 100

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

_SPRITES = os.path.join(_SCRIPT_DIR, "assets", "sprites")


def _load_sprite(name: str) -> arcade.Texture:
    return arcade.load_texture(os.path.join(_SPRITES, name))


def _cover_rect(texture: arcade.Texture, width: float, height: float):
    scale = max(width / texture.width, height / texture.height)
    draw_w = texture.width * scale
    draw_h = texture.height * scale
    return arcade.LBWH((width - draw_w) / 2, (height - draw_h) / 2, draw_w, draw_h)


def _box_hit_box(sprite: arcade.Sprite) -> None:
    hw, hh = sprite.width / 2, sprite.height / 2
    sprite.hit_box = arcade.hitbox.HitBox(
        ((-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)),
        position=sprite.position,
    )


class Pipe(arcade.Sprite):
    def __init__(self, texture: arcade.Texture) -> None:
        super().__init__(
            texture,
            scale=(PIPE_WIDTH / texture.width, PIPE_HEIGHT / texture.height),
        )
        _box_hit_box(self)
        self.passed = False


class Ground(arcade.Sprite):
    def __init__(self, texture: arcade.Texture, left: float) -> None:
        scale = GROUND_HEIGHT / texture.height
        super().__init__(texture, scale=(GROUND_WIDTH / texture.width, scale))
        self.left = left
        self.bottom = 0
        self.change_x = -PIPE_SPEED
        _box_hit_box(self)


class FlappyBird(arcade.Window):
    def __init__(self) -> None:
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        self.background = _load_sprite("background-day.png")
        self.background_rect = _cover_rect(self.background, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.pipe_texture = _load_sprite("pipe-green.png")
        self.pipe_texture_top = self.pipe_texture.flip_top_bottom()
        self.ground_texture = _load_sprite("base.png")
        self.bird_textures = [
            _load_sprite("bluebird-upflap.png"),
            _load_sprite("bluebird-midflap.png"),
            _load_sprite("bluebird-downflap.png"),
        ]
        self.gameover_texture = _load_sprite("gameover.png")

        self.bird = None
        self.bird_list = None
        self.pipes = None
        self.grounds = None
        self.score = 0
        self.frames = 0
        self.flap_index = 0
        self.flap_timer = 0.0
        self.game_over = False

    def setup(self) -> None:
        self.bird_list = arcade.SpriteList()

        tex = self.bird_textures[0]
        scale = BIRD_SIZE / tex.width
        self.bird = arcade.Sprite(tex, scale=scale)
        self.bird.center_x = BIRD_START_X
        self.bird.center_y = BIRD_START_Y
        self.bird.change_y = 0
        _box_hit_box(self.bird)
        self.bird_list.append(self.bird)

        self.pipes = arcade.SpriteList()
        self.grounds = arcade.SpriteList()
        for i in range(2):
            self.grounds.append(Ground(self.ground_texture, GROUND_WIDTH * i))
        self.score = 0
        self.frames = 0
        self.flap_index = 0
        self.flap_timer = 0.0
        self.game_over = False
        self.spawn_pipes()

    def on_draw(self) -> None:
        self.clear()
        arcade.draw_texture_rect(
            self.background,
            self.background_rect,
            pixelated=True,
        )
        self.pipes.draw(pixelated=True)
        self.bird_list.draw(pixelated=True)
        self.grounds.draw(pixelated=True)

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
            go = self.gameover_texture
            arcade.draw_texture_rect(
                go,
                arcade.XYWH(
                    SCREEN_WIDTH / 2,
                    SCREEN_HEIGHT / 2 + 50,
                    go.width,
                    go.height,
                ),
                pixelated=True,
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
        low = GROUND_HEIGHT + GAP_SIZE + GAP_MARGIN
        high = SCREEN_HEIGHT - GAP_SIZE - GAP_MARGIN
        if high <= low:
            center_y = (GROUND_HEIGHT + SCREEN_HEIGHT) // 2
        else:
            center_y = random.randint(int(low), int(high))

        bottom_pipe = Pipe(self.pipe_texture)
        bottom_pipe.center_x = SCREEN_WIDTH + PIPE_WIDTH // 2
        bottom_pipe.top = center_y - GAP_SIZE // 2
        bottom_pipe.change_x = -PIPE_SPEED
        self.pipes.append(bottom_pipe)

        top_pipe = Pipe(self.pipe_texture_top)
        top_pipe.center_x = SCREEN_WIDTH + PIPE_WIDTH // 2
        top_pipe.bottom = center_y + GAP_SIZE // 2
        top_pipe.change_x = -PIPE_SPEED
        self.pipes.append(top_pipe)

    def on_update(self, delta_time: float) -> None:
        if self.game_over:
            return

        self.bird.change_y += GRAVITY
        self.bird.center_y += self.bird.change_y

        self.flap_timer += delta_time
        if self.flap_timer >= 0.1:
            self.flap_timer = 0.0
            self.flap_index = (self.flap_index + 1) % len(self.bird_textures)
            self.bird.texture = self.bird_textures[self.flap_index]

        self.pipes.update()
        self.grounds.update()

        if self.grounds and self.grounds[0].right < 0:
            last_right = self.grounds[-1].right
            self.grounds[0].remove_from_sprite_lists()
            self.grounds.append(Ground(self.ground_texture, last_right - 20))

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
            or arcade.check_for_collision_with_list(self.bird, self.grounds)
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
