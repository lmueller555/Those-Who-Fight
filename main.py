import sys
from pathlib import Path

import pygame

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "Cute_Fantasy_Free" / "Player"
PLAYER_SHEET = ASSETS_DIR / "Player.png"

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


class Player(pygame.sprite.Sprite):
    def __init__(
        self,
        sprite_sheet: SpriteSheet,
        position: pygame.Vector2,
        scale_factor: float,
    ):
        super().__init__()
        self.sprite_sheet = sprite_sheet
        self.animations = self._load_animations()
        self.direction = pygame.Vector2(0, 0)
        self.scale_factor = scale_factor
        self.speed = 120 * scale_factor
        self.current_direction = "down"
        self.frame_index = 0
        self.frame_time = 0.0
        self.image = self.animations[self.current_direction][self.frame_index]
        self.image = pygame.transform.scale(
            self.image,
            (
                int(self.image.get_width() * BASE_SCALE * self.scale_factor),
                int(self.image.get_height() * BASE_SCALE * self.scale_factor),
            ),
        )
        self.rect = self.image.get_rect(center=position)

    def _load_animations(self) -> dict[str, list[pygame.Surface]]:
        animations = {
            "down": self.sprite_sheet.get_row_frames(0, 6),
            "left": self.sprite_sheet.get_row_frames(1, 6),
            "right": self.sprite_sheet.get_row_frames(2, 6),
            "up": self.sprite_sheet.get_row_frames(3, 6),
        }
        return animations

    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        self.direction.update(0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.direction.y = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.direction.y = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.direction.x = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.direction.x = 1

        if self.direction.length_squared() > 0:
            self.direction = self.direction.normalize()
            if abs(self.direction.x) > abs(self.direction.y):
                self.current_direction = "right" if self.direction.x > 0 else "left"
            else:
                self.current_direction = "down" if self.direction.y > 0 else "up"

    def update(self, delta_time: float) -> None:
        if self.direction.length_squared() > 0:
            movement = self.direction * self.speed * delta_time
            self.rect.centerx += movement.x
            self.rect.centery += movement.y
            self._animate(delta_time)
        else:
            self.frame_index = 0
            self._set_image()

    def _animate(self, delta_time: float) -> None:
        self.frame_time += delta_time
        if self.frame_time >= 0.1:
            self.frame_time = 0.0
            self.frame_index = (self.frame_index + 1) % len(
                self.animations[self.current_direction]
            )
            self._set_image()

    def _set_image(self) -> None:
        frame = self.animations[self.current_direction][self.frame_index]
        self.image = pygame.transform.scale(
            frame,
            (
                int(frame.get_width() * BASE_SCALE * self.scale_factor),
                int(frame.get_height() * BASE_SCALE * self.scale_factor),
            ),
        )
        self.rect = self.image.get_rect(center=self.rect.center)


def _get_scale_factor(screen_size: tuple[int, int]) -> float:
    width, height = screen_size
    width_scale = width / BASE_WIDTH
    height_scale = height / BASE_HEIGHT
    return min(width_scale, height_scale)


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.SCALED)
    pygame.display.set_caption("Those Who Fight")
    clock = pygame.time.Clock()
    screen_size = screen.get_size()
    scale_factor = _get_scale_factor(screen_size)

    if not PLAYER_SHEET.exists():
        raise FileNotFoundError(f"Missing sprite sheet: {PLAYER_SHEET}")

    sprite_sheet = SpriteSheet(PLAYER_SHEET, TILE_SIZE, TILE_SIZE)
    player = Player(
        sprite_sheet,
        pygame.Vector2(screen_size[0] / 2, screen_size[1] / 2),
        scale_factor,
    )
    all_sprites = pygame.sprite.Group(player)

    running = True
    while running:
        delta_time = clock.tick(FPS) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player.handle_input(keys)
        all_sprites.update(delta_time)

        screen.fill((40, 45, 55))
        all_sprites.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
