"""
Flappy Lab — a classroom Flappy Bird.
Students: edit config.py, then run this file.
  python main.py
"""
from __future__ import annotations
import os
import sys
import pygame
from pygame.locals import K_ESCAPE, K_SPACE, K_UP, KEYDOWN, QUIT
import config as C
from generate_assets import generate as generate_assets
ROOT = os.path.dirname(os.path.abspath(__file__))
SPRITES = os.path.join(ROOT, "assets", "sprites")
AUDIO = os.path.join(ROOT, "assets", "audio")
def asset(*parts: str) -> str:
    return os.path.join(*parts)
def load_image(name: str, scale: tuple[int, int] | None = None) -> pygame.Surface:
    path = asset(SPRITES, name)
    image = pygame.image.load(path).convert_alpha()
    if scale is not None:
        image = pygame.transform.smoothscale(image, scale)
    return image
def play_sound(sound: pygame.mixer.Sound | None) -> None:
    if sound is not None and C.SOUND_ENABLED:
        sound.play()
class Bird(pygame.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()
        raw = [
            load_image("bird-upflap.png"),
            load_image("bird-midflap.png"),
            load_image("bird-downflap.png"),
        ]
        if C.BIRD_SCALE != 1.0:
            scaled = []
            for img in raw:
                w = max(8, int(img.get_width() * C.BIRD_SCALE))
                h = max(8, int(img.get_height() * C.BIRD_SCALE))
                scaled.append(pygame.transform.smoothscale(img, (w, h)))
            raw = scaled
        self.images = raw
        self.current_image = 0
        self.frame_counter = 0
        self.image = self.images[0]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.reset()
    def reset(self) -> None:
        self.speed = C.JUMP_STRENGTH
        self.rect.x = int(C.BIRD_START_X)
        self.rect.y = int(C.BIRD_START_Y)
        self.current_image = 0
        self.frame_counter = 0
        self.image = self.images[0]
        self.mask = pygame.mask.from_surface(self.image)
    def _flap_visual(self) -> None:
        self.frame_counter += 1
        if self.frame_counter % max(1, int(C.FLAP_EVERY_N_FRAMES)) != 0:
            return
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[self.current_image]
        self.mask = pygame.mask.from_surface(self.image)
    def begin(self) -> None:
        self._flap_visual()
    def bump(self) -> None:
        self.speed = -C.JUMP_STRENGTH
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
        self.image = load_image("pipe.png", (int(C.PIPE_WIDTH), int(C.PIPE_HEIGHT)))
        self.rect = self.image.get_rect()
        self.rect.x = xpos
        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.y = -(self.rect.height - ysize)
        else:
            self.rect.y = C.SCREEN_HEIGHT - ysize
        self.mask = pygame.mask.from_surface(self.image)
        self.scored = inverted  # only the bottom pipe awards points
    def update(self) -> None:  # type: ignore[override]
        self.rect.x -= int(C.GAME_SPEED)
class Ground(pygame.sprite.Sprite):
    def __init__(self, xpos: int) -> None:
        super().__init__()
        width = 2 * C.SCREEN_WIDTH
        self.image = load_image("ground.png", (width, int(C.GROUND_HEIGHT)))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = xpos
        self.rect.y = C.SCREEN_HEIGHT - C.GROUND_HEIGHT
    def update(self) -> None:  # type: ignore[override]
        self.rect.x -= int(C.GAME_SPEED)
def is_off_screen(sprite: pygame.sprite.Sprite) -> bool:
    return sprite.rect.x < -sprite.rect.width
def get_random_pipes(xpos: int) -> tuple[Pipe, Pipe]:
    import random
    low = min(C.PIPE_MIN_HEIGHT, C.PIPE_MAX_HEIGHT)
    high = max(C.PIPE_MIN_HEIGHT, C.PIPE_MAX_HEIGHT)
    size = random.randint(int(low), int(high))
    bottom = Pipe(False, xpos, size)
    top = Pipe(True, xpos, C.SCREEN_HEIGHT - size - C.PIPE_GAP)
    return bottom, top
class FlappyLab:
    def __init__(self) -> None:
        generate_assets()
        pygame.mixer.pre_init(22050, -16, 1, 512)
        pygame.init()
        pygame.display.set_caption(C.WINDOW_TITLE)
        self.screen = pygame.display.set_mode((C.SCREEN_WIDTH, C.SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 22, bold=True)
        self.small = pygame.font.SysFont("arial", 16)
        self.big = pygame.font.SysFont("arial", 42, bold=True)
        self.background = load_image("background.png", (C.SCREEN_WIDTH, C.SCREEN_HEIGHT))
        self.begin_image = load_image("message.png")
        self.gameover_image = load_image("gameover.png")
        self.wing = self._sound("wing.wav")
        self.hit = self._sound("hit.wav")
