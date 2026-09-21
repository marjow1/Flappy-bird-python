"""
Flappy Lab — a classroom Flappy Bird.

Students: edit config.py, then run this file.
  python main.py
"""

from __future__ import annotations

import os
import random
import sys

import pygame
from pygame.locals import K_ESCAPE, K_SPACE, K_UP, KEYDOWN, QUIT

import config as C

ROOT = os.path.dirname(os.path.abspath(__file__))
SPRITES = os.path.join(ROOT, "assets", "sprites")
AUDIO = os.path.join(ROOT, "assets", "audio")


def load_image(name: str, scale: tuple[int, int] | None = None) -> pygame.Surface:
    image = pygame.image.load(os.path.join(SPRITES, name)).convert_alpha()
    if scale is not None:
        image = pygame.transform.scale(image, scale)
    return image


def play_sound(sound: pygame.mixer.Sound | None) -> None:
    if sound is not None and C.SOUND_ENABLED:
        sound.play()


class Bird(pygame.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()
        self.images = [
            load_image("bluebird-upflap.png"),
            load_image("bluebird-midflap.png"),
            load_image("bluebird-downflap.png"),
        ]
        self.current_image = 0
        self.image = self.images[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.reset()

    def reset(self) -> None:
        self.speed = C.SPEED
        self.rect.x = int(C.BIRD_START_X)
        self.rect.y = int(C.BIRD_START_Y)
        self.current_image = 0
        self.image = self.images[0]
        self.mask = pygame.mask.from_surface(self.image)

    def _flap_visual(self) -> None:
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]
        self.mask = pygame.mask.from_surface(self.image)

    def begin(self) -> None:
        self._flap_visual()

    def bump(self) -> None:
        self.speed = -C.SPEED

    def update(self) -> None:  # type: ignore[override]
        self._flap_visual()
        self.speed += C.GRAVITY
        self.rect.y += int(self.speed)
        if self.rect.top < 0:
            self.rect.top = 0
            self.speed = 0


class Pipe(pygame.sprite.Sprite):
    def __init__(self, inverted: bool, xpos: int, ysize: int) -> None:
        super().__init__()
        self.image = load_image("pipe-green.png", (int(C.PIPE_WIDTH), int(C.PIPE_HEIGHT)))
        self.rect = self.image.get_rect()
        self.rect.x = xpos
        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.y = -(self.rect.height - ysize)
        else:
            self.rect.y = C.SCREEN_HEIGHT - ysize
        self.mask = pygame.mask.from_surface(self.image)
        self.scored = inverted

    def update(self) -> None:  # type: ignore[override]
        self.rect.x -= int(C.GAME_SPEED)


class Ground(pygame.sprite.Sprite):
    def __init__(self, xpos: int) -> None:
        super().__init__()
        self.image = load_image("base.png", (int(C.GROUND_WIDTH), int(C.GROUND_HEIGHT)))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = xpos
        self.rect.y = C.SCREEN_HEIGHT - C.GROUND_HEIGHT

    def update(self) -> None:  # type: ignore[override]
        self.rect.x -= int(C.GAME_SPEED)


def is_off_screen(sprite: pygame.sprite.Sprite) -> bool:
    return sprite.rect.x < -sprite.rect.width


def get_random_pipes(xpos: int) -> tuple[Pipe, Pipe]:
    low = min(C.PIPE_MIN_HEIGHT, C.PIPE_MAX_HEIGHT)
    high = max(C.PIPE_MIN_HEIGHT, C.PIPE_MAX_HEIGHT)
    size = random.randint(int(low), int(high))
    bottom = Pipe(False, xpos, size)
    top = Pipe(True, xpos, C.SCREEN_HEIGHT - size - C.PIPE_GAP)
    return bottom, top


class FlappyLab:
    def __init__(self) -> None:
        pygame.mixer.pre_init(22050, -16, 1, 512)
        pygame.init()
        pygame.display.set_caption(C.WINDOW_TITLE)
        self.screen = pygame.display.set_mode((C.SCREEN_WIDTH, C.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 22, bold=True)
        self.small = pygame.font.SysFont("arial", 16)
        self.big = pygame.font.SysFont("arial", 42, bold=True)

        self.background = load_image("background-day.png", (C.SCREEN_WIDTH, C.SCREEN_HEIGHT))
        self.begin_image = load_image("message.png")
        self.gameover_image = load_image("gameover.png")

        self.wing = self._sound("wing.wav")
        self.hit = self._sound("hit.wav")
        self.point = self._sound("point.wav")

        self.bird_group = pygame.sprite.Group()
        self.ground_group = pygame.sprite.Group()
        self.pipe_group = pygame.sprite.Group()
        self.bird = Bird()
        self.bird_group.add(self.bird)

        self.score = 0
        self.best = 0
        self.state = "ready"
        self._build_world()

    def _sound(self, name: str) -> pygame.mixer.Sound | None:
        if not C.SOUND_ENABLED:
            return None
        sound = pygame.mixer.Sound(os.path.join(AUDIO, name))
        sound.set_volume(C.VOLUME)
        return sound

    def _build_world(self) -> None:
        self.ground_group.empty()
        self.pipe_group.empty()
        for i in range(2):
            self.ground_group.add(Ground(C.GROUND_WIDTH * i))
        for i in range(int(C.PIPE_PAIRS)):
            bottom, top = get_random_pipes(int(C.PIPE_SPAWN_OFFSET + C.PIPE_SPACING * i))
            self.pipe_group.add(bottom, top)

    def reset_round(self) -> None:
        self.score = 0
        self.bird.reset()
        self._build_world()
        self.state = "playing"
        play_sound(self.wing)
        self.bird.bump()

    def recycle_ground(self) -> None:
        sprites = self.ground_group.sprites()
        if not sprites:
            return
        if is_off_screen(sprites[0]):
            self.ground_group.remove(sprites[0])
            last = self.ground_group.sprites()[-1]
            self.ground_group.add(Ground(last.rect.x + last.rect.width - int(C.GROUND_SEAM_OVERLAP)))

    def recycle_pipes(self) -> None:
        sprites = self.pipe_group.sprites()
        if len(sprites) < 2:
            return
        if is_off_screen(sprites[0]):
            self.pipe_group.remove(sprites[0])
            self.pipe_group.remove(self.pipe_group.sprites()[0])
            last_x = max(p.rect.x for p in self.pipe_group.sprites()) if self.pipe_group else C.SCREEN_WIDTH
            bottom, top = get_random_pipes(last_x + int(C.PIPE_SPACING))
            self.pipe_group.add(bottom, top)

    def award_score(self) -> None:
        for pipe in self.pipe_group.sprites():
            if not pipe.scored and pipe.rect.right < self.bird.rect.left:
                pipe.scored = True
                self.score += int(C.POINTS_PER_PIPE)
                self.best = max(self.best, self.score)
                play_sound(self.point)

    def collided(self) -> bool:
        if pygame.sprite.groupcollide(
            self.bird_group, self.ground_group, False, False, pygame.sprite.collide_mask
        ):
            return True
        if pygame.sprite.groupcollide(
            self.bird_group, self.pipe_group, False, False, pygame.sprite.collide_mask
        ):
            return True
        if self.bird.rect.bottom >= C.SCREEN_HEIGHT - C.GROUND_HEIGHT:
            return True
        return False

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return False
                if event.key in (K_SPACE, K_UP):
                    if self.state == "ready":
                        self.reset_round()
                    elif self.state == "playing":
                        self.bird.bump()
                        play_sound(self.wing)
                    elif self.state == "dead":
                        self.state = "ready"
                        self.score = 0
                        self.bird.reset()
                        self._build_world()
        return True

    def update(self) -> None:
        if self.state == "ready":
            self.bird.begin()
            self.ground_group.update()
            self.recycle_ground()
            return
        if self.state == "playing":
            self.bird_group.update()
            self.ground_group.update()
            self.pipe_group.update()
            self.recycle_ground()
            self.recycle_pipes()
            self.award_score()
            if self.collided():
                play_sound(self.hit)
                self.state = "dead"
                self.best = max(self.best, self.score)

    def draw_hud(self) -> None:
        if not C.SHOW_HUD:
            return
        lines = [
            f"preset: {C.PRESET_NAME}",
            f"gravity: {C.GRAVITY}",
            f"jump SPEED: {C.SPEED}",
            f"GAME_SPEED: {C.GAME_SPEED}",
            f"PIPE_GAP: {C.PIPE_GAP}",
            f"FPS: {C.FPS}",
        ]
        y = 8
        for line in lines:
            text = self.small.render(line, True, (20, 40, 50))
            bg = pygame.Surface((text.get_width() + 8, text.get_height() + 2), pygame.SRCALPHA)
            bg.fill((255, 255, 255, 160))
            self.screen.blit(bg, (8, y))
            self.screen.blit(text, (12, y + 1))
            y += text.get_height() + 4

    def draw_score(self) -> None:
        label = self.big.render(str(self.score), True, (255, 255, 255))
        shadow = self.big.render(str(self.score), True, (40, 40, 40))
        x = C.SCREEN_WIDTH // 2 - label.get_width() // 2
        self.screen.blit(shadow, (x + 2, 42))
        self.screen.blit(label, (x, 40))

    def draw_start(self) -> None:
        msg = self.begin_image
        mx = C.SCREEN_WIDTH // 2 - msg.get_width() // 2
        self.screen.blit(msg, (mx, 130))
        if C.SHOW_START_SETTINGS:
            box_h = 118
            box = pygame.Surface((C.SCREEN_WIDTH - 40, box_h), pygame.SRCALPHA)
            box.fill((20, 30, 40, 170))
            self.screen.blit(box, (20, C.SCREEN_HEIGHT - C.GROUND_HEIGHT - box_h - 16))
            settings = [
                "Your current config.py values:",
                f"GRAVITY={C.GRAVITY}   SPEED={C.SPEED}   GAME_SPEED={C.GAME_SPEED}",
                f"PIPE_GAP={C.PIPE_GAP}   FPS={C.FPS}   preset={C.PRESET_NAME}",
                "Change one number, save, run python main.py again.",
            ]
            y = C.SCREEN_HEIGHT - C.GROUND_HEIGHT - box_h - 8
            for line in settings:
                text = self.small.render(line, True, (250, 250, 240))
                self.screen.blit(text, (32, y))
                y += 24

    def draw(self) -> None:
        self.screen.blit(self.background, (0, 0))
        if self.state != "ready":
            self.pipe_group.draw(self.screen)
        self.bird_group.draw(self.screen)
        self.ground_group.draw(self.screen)
        if self.state == "ready":
            self.draw_start()
        if self.state in ("playing", "dead"):
            self.draw_score()
        if self.state == "dead":
            go = self.gameover_image
            gx = C.SCREEN_WIDTH // 2 - go.get_width() // 2
            self.screen.blit(go, (gx, 160))
            best = self.font.render(f"Score {self.score}   Best {self.best}", True, (50, 40, 30))
            self.screen.blit(best, (C.SCREEN_WIDTH // 2 - best.get_width() // 2, 300))
        self.draw_hud()
        pygame.display.update()

    def run(self) -> None:
        running = True
        while running:
            self.clock.tick(max(1, int(C.FPS)))
            running = self.handle_events()
            self.update()
            self.draw()
        pygame.quit()
        sys.exit(0)


def main() -> None:
    FlappyLab().run()


if __name__ == "__main__":
    main()
