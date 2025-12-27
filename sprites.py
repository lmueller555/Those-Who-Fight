from pathlib import Path

import pygame

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "Cute_Fantasy_Free" / "Player"
PLAYER_SHEET = ASSETS_DIR / "Player.png"
TOWN_ASSETS_DIR = BASE_DIR / "Cute_Fantasy"

BASE_WIDTH = 800
BASE_HEIGHT = 600
FPS = 60
TILE_SIZE = 32
BASE_SCALE = 2


class SpriteSheet:
    def __init__(self, image_path: Path, frame_width: int, frame_height: int):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.columns = self.image.get_width() // frame_width
        self.rows = self.image.get_height() // frame_height

    def get_frame(self, column: int, row: int) -> pygame.Surface:
        rect = pygame.Rect(
            column * self.frame_width,
            row * self.frame_height,
            self.frame_width,
            self.frame_height,
        )
        frame = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
        frame.blit(self.image, (0, 0), rect)
        return frame

    def get_row_frames(self, row: int, count: int) -> list[pygame.Surface]:
        return [self.get_frame(column, row) for column in range(count)]
