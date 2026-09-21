"""
Flappy Lab — Arcade classroom clone.

Students: edit config.py, then run:
  python main.py

This is the Arcade version of the game (yellow bird, green pipes).
"""

from __future__ import annotations

import random

import arcade

import config as C


class Pipe(arcade.SpriteSolidColor):
    def __init__(self, width: int, height: int, color) -> None:
        # Arcade 3 needs color= as a keyword. Passing it as the 3rd
        # positional argument would be read as center_x and crash.
        super().__init__(width, height, color=color)
        self.passed = False


class FlappyBird(arcade.Window):
    def __init__(self) -> None:
        super().__init__(C.SCREEN_WIDTH, C.SCREEN_HEIGHT, C.SCREEN_TITLE)
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
            C.BIRD_SIZE,
            C.BIRD_SIZE,
            color=arcade.color.YELLOW,
        )
        self.bird.center_x = C.BIRD_START_X
        self.bird.center_y = C.BIRD_START_Y
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
            C.SCREEN_HEIGHT - 40,
            arcade.color.WHITE,
            24,
            bold=True,
        )

        if C.SHOW_HUD:
            hud = [
                f"preset: {C.PRESET_NAME}",
                f"GRAVITY: {C.GRAVITY}",
                f"JUMP_SPEED: {C.JUMP_SPEED}",
                f"PIPE_SPEED: {C.PIPE_SPEED}",
                f"GAP_SIZE: {C.GAP_SIZE}",
                f"SPAWN_INTERVAL: {C.SPAWN_INTERVAL}",
            ]
            y = C.SCREEN_HEIGHT - 70
            for line in hud:
                arcade.draw_text(line, 20, y, arcade.color.DARK_BLUE, 12, bold=True)
                y -= 16

        if self.game_over:
            arcade.draw_text(
                "GAME OVER",
                C.SCREEN_WIDTH // 2,
                C.SCREEN_HEIGHT // 2 + 50,
                arcade.color.RED,
                50,
                anchor_x="center",
                bold=True,
            )
            arcade.draw_text(
                "Press SPACE to Restart",
                C.SCREEN_WIDTH // 2,
                C.SCREEN_HEIGHT // 2 - 20,
                arcade.color.WHITE,
                20,
                anchor_x="center",
            )

    def spawn_pipes(self) -> None:
        low = C.GAP_SIZE + C.GAP_MARGIN
        high = C.SCREEN_HEIGHT - C.GAP_SIZE - C.GAP_MARGIN
        if high <= low:
            center_y = C.SCREEN_HEIGHT // 2
        else:
            center_y = random.randint(int(low), int(high))

        bottom_pipe = Pipe(C.PIPE_WIDTH, C.SCREEN_HEIGHT, arcade.color.GREEN)
        bottom_pipe.center_x = C.SCREEN_WIDTH + C.PIPE_WIDTH // 2
        bottom_pipe.top = center_y - C.GAP_SIZE // 2
        bottom_pipe.change_x = -C.PIPE_SPEED
        self.pipes.append(bottom_pipe)

        top_pipe = Pipe(C.PIPE_WIDTH, C.SCREEN_HEIGHT, arcade.color.GREEN)
        top_pipe.center_x = C.SCREEN_WIDTH + C.PIPE_WIDTH // 2
        top_pipe.bottom = center_y + C.GAP_SIZE // 2
        top_pipe.change_x = -C.PIPE_SPEED
        self.pipes.append(top_pipe)

    def on_update(self, delta_time: float) -> None:
        if self.game_over:
            return

        self.bird.change_y += C.GRAVITY
        self.bird.center_y += self.bird.change_y

        self.pipes.update()

        self.frames += 1
        if self.frames % max(1, int(C.SPAWN_INTERVAL)) == 0:
            self.spawn_pipes()

        for pipe in self.pipes:
            if pipe.right < 0:
                pipe.remove_from_sprite_lists()
            elif pipe.right < self.bird.left and not pipe.passed:
                pipe.passed = True
                # Two pipes per gap, so each pipe is worth half a pair.
                self.score += C.POINTS_PER_PIPE / 2

        if (
            arcade.check_for_collision_with_list(self.bird, self.pipes)
            or self.bird.bottom < 0
            or self.bird.top > C.SCREEN_HEIGHT
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
                self.bird.change_y = C.JUMP_SPEED


def main() -> None:
    game = FlappyBird()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
