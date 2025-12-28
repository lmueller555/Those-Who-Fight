import sys

import pygame

from sprites import (
    SpriteSheet,
    BASE_SCALE,
    BASE_WIDTH,
    BASE_HEIGHT,
    FPS,
    PLAYER_TILE_SIZE,
    PLAYER_SHEET,
)
from town_builder import InteriorMap, TownMap


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
        down_frames = self.sprite_sheet.get_row_frames(0, 6)
        right_frames = self.sprite_sheet.get_row_frames(1, 6)
        up_frames = self.sprite_sheet.get_row_frames(2, 6)
        left_frames = [
            pygame.transform.flip(frame, True, False) for frame in right_frames
        ]
        return {
            "down": down_frames,
            "left": left_frames,
            "right": right_frames,
            "up": up_frames,
        }

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
                new_direction = "right" if self.direction.x > 0 else "left"
            else:
                new_direction = "down" if self.direction.y > 0 else "up"
            if new_direction != self.current_direction:
                self.current_direction = new_direction
                self.frame_index = 0
                self.frame_time = 0.0
                self._set_image()

    def update(
        self, delta_time: float, colliders: list[pygame.Rect]
    ) -> None:
        if self.direction.length_squared() > 0:
            movement = self.direction * self.speed * delta_time
            self._move_axis(movement.x, 0, colliders)
            self._move_axis(0, movement.y, colliders)
            self._animate(delta_time)
        else:
            self.frame_index = 0
            self._set_image()

    def _move_axis(
        self,
        dx: float,
        dy: float,
        colliders: list[pygame.Rect],
    ) -> None:
        if dx == 0 and dy == 0:
            return
        self.rect.centerx += dx
        self.rect.centery += dy
        for collider in colliders:
            if self.rect.colliderect(collider):
                if dx > 0:
                    self.rect.right = collider.left
                elif dx < 0:
                    self.rect.left = collider.right
                if dy > 0:
                    self.rect.bottom = collider.top
                elif dy < 0:
                    self.rect.top = collider.bottom

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



class Camera:
    def __init__(self, screen_size: tuple[int, int], map_size: tuple[int, int]):
        self.screen_width, self.screen_height = screen_size
        self.map_width, self.map_height = map_size
        self.offset = pygame.Vector2(0, 0)

    def update(self, target_rect: pygame.Rect) -> None:
        desired_x = target_rect.centerx - self.screen_width / 2
        desired_y = target_rect.centery - self.screen_height / 2
        if self.map_width <= self.screen_width:
            self.offset.x = -(self.screen_width - self.map_width) / 2
        else:
            max_x = self.map_width - self.screen_width
            self.offset.x = max(0, min(desired_x, max_x))

        if self.map_height <= self.screen_height:
            self.offset.y = -(self.screen_height - self.map_height) / 2
        else:
            max_y = self.map_height - self.screen_height
            self.offset.y = max(0, min(desired_y, max_y))


def _get_scale_factor(screen_size: tuple[int, int]) -> float:
    width, height = screen_size
    width_scale = width / BASE_WIDTH
    height_scale = height / BASE_HEIGHT
    return min(width_scale, height_scale)


def _get_display_size() -> tuple[int, int]:
    info = pygame.display.Info()
    if info.current_w > 0 and info.current_h > 0:
        return info.current_w, info.current_h
    return BASE_WIDTH, BASE_HEIGHT


def main() -> None:
    pygame.init()
    display_size = _get_display_size()
    screen = pygame.display.set_mode(display_size, pygame.FULLSCREEN | pygame.SCALED)
    pygame.display.set_caption("Those Who Fight")
    clock = pygame.time.Clock()
    screen_size = screen.get_size()
    scale_factor = _get_scale_factor(screen_size)

    if not PLAYER_SHEET.exists():
        raise FileNotFoundError(f"Missing sprite sheet: {PLAYER_SHEET}")

    sprite_sheet = SpriteSheet(PLAYER_SHEET, PLAYER_TILE_SIZE, PLAYER_TILE_SIZE)
    town_map = TownMap(scale_factor)
    interior_maps: dict[str, InteriorMap] = {}
    current_map = town_map
    start_position = pygame.Vector2(
        town_map.map_size[0] / 2,
        town_map.map_size[1] - town_map.tile_size * 2,
    )
    player = Player(sprite_sheet, start_position, scale_factor)
    camera = Camera(screen_size, current_map.map_size)
    active_building: str | None = None

    running = True
    while running:
        delta_time = clock.tick(FPS) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        keys = pygame.key.get_pressed()
        player.handle_input(keys)
        player.update(delta_time, current_map.colliders)
        if current_map is town_map:
            entrance = town_map.get_entrance(player.rect)
            if entrance is not None:
                interior_map = interior_maps.get(entrance.building_name)
                if interior_map is None:
                    interior_map = InteriorMap(scale_factor, entrance.building_name)
                    interior_maps[entrance.building_name] = interior_map
                current_map = interior_map
                active_building = entrance.building_name
                player.rect.midbottom = interior_map.entry_spawn
                camera = Camera(screen_size, current_map.map_size)
        else:
            if player.rect.colliderect(current_map.exit_rect) and active_building:
                entrance = next(
                    (item for item in town_map.building_entrances
                     if item.building_name == active_building),
                    None,
                )
                current_map = town_map
                if entrance is not None:
                    player.rect.center = entrance.exterior_spawn
                camera = Camera(screen_size, current_map.map_size)
                active_building = None

        player.rect.clamp_ip(
            pygame.Rect(0, 0, current_map.map_size[0], current_map.map_size[1])
        )
        camera.update(player.rect)

        screen.fill((40, 45, 55))
        current_map.draw(screen, camera.offset)
        screen.blit(
            player.image,
            (player.rect.x - camera.offset.x, player.rect.y - camera.offset.y),
        )
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
