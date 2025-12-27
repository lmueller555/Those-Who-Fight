import sys
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


class TownMap:
    def __init__(self, scale_factor: float):
        self.scale_factor = scale_factor
        self.tile_size = int(TILE_SIZE * BASE_SCALE * scale_factor)
        self.columns = 25
        self.rows = 27
        self.map_size = (
            self.columns * self.tile_size,
            self.rows * self.tile_size,
        )
        self.surface = pygame.Surface(self.map_size, pygame.SRCALPHA)
        self._load_assets()
        self._build_map()

    def _load_image(self, relative_path: str) -> pygame.Surface:
        image_path = TOWN_ASSETS_DIR / relative_path
        if not image_path.exists():
            raise FileNotFoundError(f"Missing town asset: {image_path}")
        return pygame.image.load(image_path).convert_alpha()

    def _scale(self, surface: pygame.Surface) -> pygame.Surface:
        return pygame.transform.scale(
            surface,
            (
                int(surface.get_width() * BASE_SCALE * self.scale_factor),
                int(surface.get_height() * BASE_SCALE * self.scale_factor),
            ),
        )

    def _load_assets(self) -> None:
        grass_tiles = SpriteSheet(
            TOWN_ASSETS_DIR / "Tiles" / "Grass" / "Grass_Tiles_1.png",
            TILE_SIZE,
            TILE_SIZE,
        )
        cobble_tiles = SpriteSheet(
            TOWN_ASSETS_DIR / "Tiles" / "Cobble_Road" / "Cobble_Road_1.png",
            TILE_SIZE,
            TILE_SIZE,
        )
        water_tiles = SpriteSheet(
            TOWN_ASSETS_DIR / "Tiles" / "Water" / "Water_Tile_1.png",
            TILE_SIZE,
            TILE_SIZE,
        )
        sign_sheet = SpriteSheet(
            TOWN_ASSETS_DIR / "Outdoor decoration" / "Signs.png",
            TILE_SIZE,
            TILE_SIZE,
        )
        flower_sheet = SpriteSheet(
            TOWN_ASSETS_DIR / "Outdoor decoration" / "Flowers.png",
            TILE_SIZE,
            TILE_SIZE,
        )
        barrel_sheet = SpriteSheet(
            TOWN_ASSETS_DIR / "Outdoor decoration" / "barrels.png",
            16,  # Each barrel sprite is 16 pixels wide
            32,  # Each barrel sprite is 32 pixels tall
        )
        bartender_sheet = SpriteSheet(
            TOWN_ASSETS_DIR / "NPCs (Premade)" / "Bartender_Bruno.png",
            TILE_SIZE,
            TILE_SIZE,
        )
        miner_sheet = SpriteSheet(
            TOWN_ASSETS_DIR / "NPCs (Premade)" / "Miner_Mike.png",
            TILE_SIZE,
            TILE_SIZE,
        )
        chef_sheet = SpriteSheet(
            TOWN_ASSETS_DIR / "NPCs (Premade)" / "Chef_Chloe.png",
            TILE_SIZE,
            TILE_SIZE,
        )
        self.grass_tile = self._scale(grass_tiles.get_frame(0, 0))
        self.road_tile = self._scale(cobble_tiles.get_frame(0, 0))
        self.water_tile = self._scale(water_tiles.get_frame(0, 0))
        self.bridge = self._scale(
            self._load_image("Tiles/Bridge/Bridge_Stone_Horizontal.png")
        )
        self.sign_sprite = self._scale(sign_sheet.get_frame(0, 0))

        self.buildings = {
            "inn": self._scale(
                self._load_image(
                    "Buildings/Buildings/Unique_Buildings/Inn/Inn_Blue.png"
                )
            ),
            "blacksmith": self._scale(
                self._load_image(
                    "Buildings/Buildings/Unique_Buildings/Blacksmith_House/"
                    "Blacksmith_House_Red.png"
                )
            ),
            "house_1": self._scale(
                self._load_image(
                    "Buildings/Buildings/Houses/Wood/House_1_Wood_Base_Red.png"
                )
            ),
            "house_2": self._scale(
                self._load_image(
                    "Buildings/Buildings/Houses/Wood/House_2_Wood_Green_Blue.png"
                )
            ),
            "house_3": self._scale(
                self._load_image(
                    "Buildings/Buildings/Houses/Wood/House_3_Wood_Red_Black.png"
                )
            ),
            "house_4": self._scale(
                self._load_image(
                    "Buildings/Buildings/Houses/Wood/House_4_Wood_Base_Blue.png"
                )
            ),
            "house_5": self._scale(
                self._load_image(
                    "Buildings/Buildings/Houses/Wood/House_5_Wood_Green_Red.png"
                )
            ),
            "stalls": self._scale(
                self._load_image(
                    "Buildings/Buildings/Unique_Buildings/Stalls/Market_Stalls.png"
                )
            ),
        }

        self.props = {
            "fountain": self._scale(
                self._load_image("Outdoor decoration/Fountain.png")
            ),
            "benches": self._scale(
                self._load_image("Outdoor decoration/Benches.png")
            ),
            "lantern": self._scale(
                self._load_image("Outdoor decoration/Lanter_Posts.png")
            ),
            "well": self._scale(self._load_image("Outdoor decoration/Well.png")),
            "hay_bales": self._scale(
                self._load_image("Outdoor decoration/Hay_Bales.png")
            ),
            "fences": self._scale(
                self._load_image("Outdoor decoration/Fences.png")
            ),
        }

        # Extract individual barrel sprites from the sprite sheet
        # Top row (0): wooden barrels, Bottom row (1): flower pots in barrels
        self.barrels = {
            "brown": self._scale(barrel_sheet.get_frame(0, 0)),
            "dark": self._scale(barrel_sheet.get_frame(1, 0)),
            "red": self._scale(barrel_sheet.get_frame(2, 0)),
            "blue": self._scale(barrel_sheet.get_frame(3, 0)),
            "green": self._scale(barrel_sheet.get_frame(4, 0)),
            "purple": self._scale(barrel_sheet.get_frame(5, 0)),
        }

        # Extract individual flower pot sprites from the sprite sheet
        self.flower_pots = {
            "red": self._scale(flower_sheet.get_frame(0, 0)),
            "blue": self._scale(flower_sheet.get_frame(1, 0)),
            "yellow": self._scale(flower_sheet.get_frame(2, 0)),
            "pink": self._scale(flower_sheet.get_frame(3, 0)),
            "purple": self._scale(flower_sheet.get_frame(4, 0)),
        }

        self.npc_sprites = {
            "bartender": self._scale(bartender_sheet.get_frame(0, 0)),
            "miner": self._scale(miner_sheet.get_frame(0, 0)),
            "chef": self._scale(chef_sheet.get_frame(0, 0)),
        }

        trees = {
            "oak": self._scale(self._load_image("Trees/Big_Oak_Tree.png")),
            "birch": self._scale(self._load_image("Trees/Medium_Birch_Tree.png")),
            "spruce": self._scale(self._load_image("Trees/Small_Spruce_Tree.png")),
        }
        self.trees = trees

    def _blit_tile(self, tile: pygame.Surface, grid_x: int, grid_y: int) -> None:
        self.surface.blit(tile, (grid_x * self.tile_size, grid_y * self.tile_size))

    def _blit_object(
        self,
        sprite: pygame.Surface,
        grid_x: int,
        grid_y: int,
        anchor: str = "midbottom",
    ) -> None:
        x = grid_x * self.tile_size + self.tile_size // 2
        y = grid_y * self.tile_size + self.tile_size
        rect = sprite.get_rect()
        setattr(rect, anchor, (x, y))
        self.surface.blit(sprite, rect.topleft)

    def _build_map(self) -> None:
        # Ground layer - grass everywhere
        for y in range(self.rows):
            for x in range(self.columns):
                self._blit_tile(self.grass_tile, x, y)

        # Main road oval loop
        loop_left, loop_right = 6, 18
        loop_top, loop_bottom = 8, 19
        for x in range(loop_left, loop_right + 1):
            self._blit_tile(self.road_tile, x, loop_top)
            self._blit_tile(self.road_tile, x, loop_bottom)
        for y in range(loop_top, loop_bottom + 1):
            self._blit_tile(self.road_tile, loop_left, y)
            self._blit_tile(self.road_tile, loop_right, y)

        # South entrance road
        center_x = self.columns // 2
        for y in range(loop_bottom + 1, self.rows):
            self._blit_tile(self.road_tile, center_x, y)

        # Central plaza (5x5 cobble square)
        plaza_left, plaza_top = 10, 11
        for y in range(plaza_top, plaza_top + 5):
            for x in range(plaza_left, plaza_left + 5):
                self._blit_tile(self.road_tile, x, y)

        # North branch to market stalls
        for y in range(loop_top - 3, loop_top):
            self._blit_tile(self.road_tile, center_x, y)

        # West branch to blacksmith
        for x in range(loop_left - 3, loop_left):
            self._blit_tile(self.road_tile, x, 13)

        # East branches for houses
        for x in range(loop_right + 1, loop_right + 3):
            self._blit_tile(self.road_tile, x, 9)

        # South residential path
        for y in range(loop_bottom + 1, loop_bottom + 4):
            self._blit_tile(self.road_tile, 8, y)

        # Buildings - placed strategically around the loop
        self._blit_object(self.buildings["inn"], 18, 13)
        self._blit_object(self.buildings["blacksmith"], 6, 13)
        self._blit_object(self.buildings["stalls"], 12, 5)

        # Houses - arranged for a cozy residential feel with road access
        self._blit_object(self.buildings["house_1"], 20, 9)
        self._blit_object(self.buildings["house_2"], 16, 9)
        self._blit_object(self.buildings["house_3"], 4, 13)
        self._blit_object(self.buildings["house_4"], 8, 22)
        self._blit_object(self.buildings["house_5"], 8, 9)

        # Well in residential area
        self._blit_object(self.props["well"], 4, 12)

        # Plaza decorations - fountain centerpiece with benches
        self._blit_object(self.props["fountain"], 12, 13)
        self._blit_object(self.props["benches"], 11, 12)
        self._blit_object(self.props["benches"], 13, 14)

        # Additional town decorations - create a lived-in feeling
        self._blit_object(self.barrels["brown"], 19, 12)
        self._blit_object(self.barrels["dark"], 5, 12)
        self._blit_object(self.barrels["red"], 7, 14)
        self._blit_object(self.props["hay_bales"], 9, 21)
        self._blit_object(self.props["hay_bales"], 7, 21)
        self._blit_object(self.props["fences"], 21, 10)
        self._blit_object(self.props["fences"], 3, 10)

        # Flower pots - sprinkled along plaza edges and near buildings
        # Plaza edge decorations
        self._blit_object(self.flower_pots["red"], 10, 11)
        self._blit_object(self.flower_pots["blue"], 14, 11)
        self._blit_object(self.flower_pots["yellow"], 10, 15)
        self._blit_object(self.flower_pots["pink"], 14, 15)
        # Near benches
        self._blit_object(self.flower_pots["purple"], 10, 12)
        self._blit_object(self.flower_pots["red"], 14, 14)
        # Near inn entrance
        self._blit_object(self.flower_pots["blue"], 18, 14)
        self._blit_object(self.flower_pots["yellow"], 17, 14)
        # Near blacksmith entrance
        self._blit_object(self.flower_pots["pink"], 6, 14)
        self._blit_object(self.flower_pots["purple"], 5, 14)
        # Near houses for cozy residential feel
        self._blit_object(self.flower_pots["red"], 20, 10)
        self._blit_object(self.flower_pots["blue"], 16, 10)
        self._blit_object(self.flower_pots["yellow"], 4, 14)
        self._blit_object(self.flower_pots["pink"], 8, 23)

        # Road intersection decorations - signs at key intersections
        # South entrance where road meets the oval loop
        self._blit_object(self.sign_sprite, 13, 19)
        # North intersection where market branch meets the loop
        self._blit_object(self.sign_sprite, 11, 8)
        # West intersection at blacksmith
        self._blit_object(self.sign_sprite, 6, 12)
        # East intersection at housing area
        self._blit_object(self.sign_sprite, 18, 10)

        # NPCs - placed near their workplaces
        self._blit_object(self.npc_sprites["bartender"], 19, 14)
        self._blit_object(self.npc_sprites["miner"], 5, 14)
        self._blit_object(self.npc_sprites["chef"], 12, 7)

        # Trees - frame the town boundaries for a sheltered feel
        tree_positions = [
            # North boundary - dense tree line
            (2, 3, "oak"),
            (5, 2, "birch"),
            (8, 3, "oak"),
            (11, 2, "oak"),
            (15, 3, "birch"),
            (18, 2, "oak"),
            (21, 3, "spruce"),
            (23, 4, "birch"),
            # West boundary
            (1, 7, "birch"),
            (2, 11, "oak"),
            (1, 15, "birch"),
            (2, 19, "oak"),
            (1, 23, "spruce"),
            # East boundary
            (23, 8, "spruce"),
            (22, 12, "birch"),
            (23, 16, "oak"),
            (22, 20, "spruce"),
            (23, 24, "birch"),
            # South boundary - lighter
            (6, 24, "birch"),
            (18, 24, "spruce"),
        ]
        for x, y, tree in tree_positions:
            self._blit_object(self.trees[tree], x, y)

    def draw(self, screen: pygame.Surface, offset: pygame.Vector2) -> None:
        screen.blit(self.surface, (-offset.x, -offset.y))


class Camera:
    def __init__(self, screen_size: tuple[int, int], map_size: tuple[int, int]):
        self.screen_width, self.screen_height = screen_size
        self.map_width, self.map_height = map_size
        self.offset = pygame.Vector2(0, 0)

    def update(self, target_rect: pygame.Rect) -> None:
        desired_x = target_rect.centerx - self.screen_width / 2
        desired_y = target_rect.centery - self.screen_height / 2
        max_x = max(0, self.map_width - self.screen_width)
        max_y = max(0, self.map_height - self.screen_height)
        self.offset.x = max(0, min(desired_x, max_x))
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

    sprite_sheet = SpriteSheet(PLAYER_SHEET, TILE_SIZE, TILE_SIZE)
    town_map = TownMap(scale_factor)
    start_position = pygame.Vector2(
        town_map.map_size[0] / 2,
        town_map.map_size[1] - town_map.tile_size * 2,
    )
    player = Player(sprite_sheet, start_position, scale_factor)
    camera = Camera(screen_size, town_map.map_size)

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
        player.update(delta_time)
        player.rect.clamp_ip(
            pygame.Rect(0, 0, town_map.map_size[0], town_map.map_size[1])
        )
        camera.update(player.rect)

        screen.fill((40, 45, 55))
        town_map.draw(screen, camera.offset)
        screen.blit(
            player.image,
            (player.rect.x - camera.offset.x, player.rect.y - camera.offset.y),
        )
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
