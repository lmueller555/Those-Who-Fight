from dataclasses import dataclass

import pygame

from sprites import BASE_DIR, BASE_SCALE, TILE_SIZE, TOWN_ASSETS_DIR, SpriteSheet


@dataclass(frozen=True)
class BuildingEntrance:
    building_name: str
    door_rect: pygame.Rect
    exterior_spawn: pygame.Vector2


class TownMap:
    def __init__(self, scale_factor: float):
        self.scale_factor = scale_factor
        self.tile_size = int(TILE_SIZE * BASE_SCALE * scale_factor)
        self.ascii_map = self._load_ascii_map()
        self.rows = len(self.ascii_map)
        self.columns = len(self.ascii_map[0])
        self.map_size = (
            self.columns * self.tile_size,
            self.rows * self.tile_size,
        )
        self.surface = pygame.Surface(self.map_size, pygame.SRCALPHA)
        self.building_colliders: list[pygame.Rect] = []
        self.building_entrances: list[BuildingEntrance] = []
        self.building_positions: dict[str, pygame.Rect] = {}
        self.npcs: list[AnimatedNPC] = []
        self._load_assets()
        self._build_map()
        self._spawn_blacksmith()
        self._build_collision_rects()
        self.colliders = self.building_colliders

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

    def _scale_to_tile(self, surface: pygame.Surface) -> pygame.Surface:
        """Scale a surface to exactly fit tile_size x tile_size"""
        return pygame.transform.scale(surface, (self.tile_size, self.tile_size))

    def _scale_to_npc(self, surface: pygame.Surface) -> pygame.Surface:
        return pygame.transform.scale(
            surface,
            (self.tile_size * 4, self.tile_size * 4),
        )

    def _load_ascii_map(self) -> list[str]:
        map_path = BASE_DIR / "starting_town_ascii_map.md"
        if not map_path.exists():
            raise FileNotFoundError(f"Missing ASCII map: {map_path}")
        content = map_path.read_text(encoding="utf-8").splitlines()
        map_lines: list[str] = []
        in_map_block = False
        for line in content:
            stripped = line.strip()
            if stripped.startswith("```"):
                if in_map_block:
                    break
                in_map_block = True
                continue
            if in_map_block:
                if stripped:
                    map_lines.append(line.rstrip("\n"))
        if not map_lines:
            raise ValueError("ASCII map block is missing or empty.")
        width = len(map_lines[0])
        if any(len(row) != width for row in map_lines):
            raise ValueError("ASCII map rows are not a consistent width.")
        return map_lines

    def _load_assets(self) -> None:
        # Load tile images and spritesheets
        grass_tile_image = self._load_image("Tiles/Grass/Grass_1_Middle.png")

        # Load Grass_Tiles_1 which contains path transition tiles as a SpriteSheet
        grass_tiles_sheet = SpriteSheet(
            TOWN_ASSETS_DIR / "Tiles" / "Grass" / "Grass_Tiles_1.png",
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
        blacksmith_sheet = SpriteSheet(
            TOWN_ASSETS_DIR / "NPCs (Premade)" / "Miner_Mike.png",
            64,
            64,
        )

        self.grass_tile = self._scale_to_tile(grass_tile_image)

        # Extract path transition tiles from Grass_Tiles_1 using SpriteSheet
        #
        # HOW TO EXPERIMENT WITH TILE INDICES:
        # - get_frame(column, row) - both start at 0
        # - column: 0 = leftmost, 1 = second from left, 2 = third from left, etc.
        # - row: 0 = topmost, 1 = second from top, 2 = third from top, etc.
        #
        # WHAT EACH TILE SHOULD BE:
        # - "grass_top_left": grass surrounds top-left, path in bottom-right
        # - "grass_top": grass at top, path at bottom
        # - "grass_top_right": grass surrounds top-right, path in bottom-left
        # - "grass_left": grass on left, path on right
        # - "center": pure path/dirt (no grass visible)
        # - "grass_right": grass on right, path on left
        # - "grass_bottom_left": grass surrounds bottom-left, path in top-right
        # - "grass_bottom": grass at bottom, path at top
        # - "grass_bottom_right": grass surrounds bottom-right, path in top-left
        #
        # Dirt/path tiles with grass transitions from Grass_Tiles_1.png
        # Using tan dirt tiles at rows 5-7, columns 0-2
        # Row 5: Top edge tiles (with corner grass tufts)
        # Row 6: Middle tiles (with straight grass edges on left/right)
        # Row 7: Bottom edge tiles (with corner grass tufts)

        self.path_tiles = {
            # Top row of path section (row 5) - used for horizontal paths
            "horizontal_top_left": self._scale_to_tile(grass_tiles_sheet.get_frame(0, 5)),
            "horizontal_top": self._scale_to_tile(grass_tiles_sheet.get_frame(1, 5)),  # grass on top edge
            "horizontal_top_right": self._scale_to_tile(grass_tiles_sheet.get_frame(2, 5)),

            # Middle row of path section (row 6) - used for vertical paths (straight edges)
            "vertical_left": self._scale_to_tile(grass_tiles_sheet.get_frame(0, 6)),  # straight grass on left edge
            "center": self._scale_to_tile(grass_tiles_sheet.get_frame(1, 6)),  # pure dirt center
            "vertical_right": self._scale_to_tile(grass_tiles_sheet.get_frame(2, 6)),  # straight grass on right edge

            # Bottom row of path section (row 7) - used for horizontal paths
            "horizontal_bottom_left": self._scale_to_tile(grass_tiles_sheet.get_frame(0, 7)),
            "horizontal_bottom": self._scale_to_tile(grass_tiles_sheet.get_frame(1, 7)),  # grass on bottom edge
            "horizontal_bottom_right": self._scale_to_tile(grass_tiles_sheet.get_frame(2, 7)),

            # Inner corner tiles (rows 8-9) - for T-intersections
            # These create smooth curved transitions where paths meet at right angles
            "inner_corner_top_left": self._scale_to_tile(grass_tiles_sheet.get_frame(0, 9)),
            "inner_corner_top_right": self._scale_to_tile(grass_tiles_sheet.get_frame(1, 9)),
            "inner_corner_bottom_left": self._scale_to_tile(grass_tiles_sheet.get_frame(0, 8)),
            "inner_corner_bottom_right": self._scale_to_tile(grass_tiles_sheet.get_frame(1, 8)),

            # Keep old names for backwards compatibility with corners
            "grass_top_left": self._scale_to_tile(grass_tiles_sheet.get_frame(0, 5)),
            "grass_top_right": self._scale_to_tile(grass_tiles_sheet.get_frame(2, 5)),
            "grass_left": self._scale_to_tile(grass_tiles_sheet.get_frame(0, 6)),
            "grass_right": self._scale_to_tile(grass_tiles_sheet.get_frame(2, 6)),
            "grass_bottom_left": self._scale_to_tile(grass_tiles_sheet.get_frame(0, 7)),
            "grass_bottom_right": self._scale_to_tile(grass_tiles_sheet.get_frame(2, 7)),
            "grass_top": self._scale_to_tile(grass_tiles_sheet.get_frame(1, 5)),
            "grass_bottom": self._scale_to_tile(grass_tiles_sheet.get_frame(1, 7)),
        }

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

        fountain_sheet = SpriteSheet(
            TOWN_ASSETS_DIR / "Outdoor decoration" / "Fountain.png",
            32,
            80,
        )
        benches_sheet = SpriteSheet(
            TOWN_ASSETS_DIR / "Outdoor decoration" / "Benches.png",
            32,
            32,
        )
        self.props = {
            "fountain": self._scale(fountain_sheet.get_frame(0, 0)),
            "benches": self._scale(benches_sheet.get_frame(1, 0)),
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

        self.blacksmith_frames = [
            self._scale_to_npc(blacksmith_sheet.get_frame(column, 0))
            for column in range(6)
        ]

        trees = {
            "oak": self._scale(self._load_image("Trees/Big_Oak_Tree.png")),
            "birch": self._scale(self._load_image("Trees/Medium_Birch_Tree.png")),
            "spruce": self._scale(self._load_image("Trees/Small_Spruce_Tree.png")),
        }
        self.trees = trees

    def _blit_tile(
        self, tile: pygame.Surface, grid_x: int, grid_y: int, rotation: int = 0
    ) -> None:
        if rotation != 0:
            tile = pygame.transform.rotate(tile, rotation)
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

        tile_mapping = {
            "A": self.path_tiles["horizontal_top_left"],
            "D": self.path_tiles["horizontal_top"],
            "E": self.path_tiles["horizontal_top_right"],
            "H": self.path_tiles["horizontal_bottom_left"],
            "J": self.path_tiles["horizontal_bottom"],
            "K": self.path_tiles["horizontal_bottom_right"],
            "L": self.path_tiles["vertical_left"],
            "R": self.path_tiles["center"],
            "Q": self.path_tiles["vertical_right"],
            "U": self.path_tiles["inner_corner_top_left"],
            "V": self.path_tiles["inner_corner_top_right"],
            "X": self.path_tiles["inner_corner_bottom_left"],
            "Z": self.path_tiles["inner_corner_bottom_right"],
            "P": self.path_tiles["center"],
        }
        object_ground = {
            "F": self.path_tiles["center"],
            "N": self.path_tiles["center"],
            "W": self.path_tiles["center"],
            "b": self.path_tiles["center"],
            "f": self.path_tiles["center"],
            "g": self.path_tiles["center"],
            "p": self.path_tiles["center"],
            "T": self.path_tiles["center"],
            "M": self.path_tiles["center"],
            "C": self.path_tiles["center"],
        }
        for y, row in enumerate(self.ascii_map):
            for x, tile in enumerate(row):
                if tile in tile_mapping:
                    self._blit_tile(tile_mapping[tile], x, y)
                elif tile in object_ground:
                    self._blit_tile(object_ground[tile], x, y)

        building_mapping = {
            "I": ("inn", self.buildings["inn"]),
            "B": ("blacksmith", self.buildings["blacksmith"]),
            "S": ("stalls", self.buildings["stalls"]),
            "1": ("house_1", self.buildings["house_1"]),
            "2": ("house_2", self.buildings["house_2"]),
            "3": ("house_3", self.buildings["house_3"]),
            "4": ("house_4", self.buildings["house_4"]),
            "5": ("house_5", self.buildings["house_5"]),
        }

        object_mapping = {
            "F": self.props["fountain"],
            "N": self.props["benches"],
            "W": self.props["well"],
            "b": self.barrels["brown"],
            "h": self.props["hay_bales"],
            "f": self.props["fences"],
            "g": self.sign_sprite,
            "p": self.flower_pots["red"],
            "T": self.npc_sprites["bartender"],
            "M": self.npc_sprites["miner"],
            "C": self.npc_sprites["chef"],
            "O": self.trees["oak"],
            "r": self.trees["birch"],
            "Y": self.trees["spruce"],
        }
        for y, row in enumerate(self.ascii_map):
            for x, tile in enumerate(row):
                building_entry = building_mapping.get(tile)
                if building_entry is not None:
                    building_name, building_sprite = building_entry
                    self._blit_object(building_sprite, x, y)
                    rect = building_sprite.get_rect()
                    rect.midbottom = (
                        x * self.tile_size + self.tile_size // 2,
                        y * self.tile_size + self.tile_size,
                    )
                    self.building_positions[building_name] = rect
                    continue
                sprite = object_mapping.get(tile)
                if sprite is not None:
                    self._blit_object(sprite, x, y)

    def _spawn_blacksmith(self) -> None:
        building_rect = self.building_positions.get("blacksmith")
        if building_rect is None:
            return
        # Blacksmith house sprite is 10x8 tiles; the anvil sits on tile (8, 6).
        # Place the NPC in front of the anvil, shifted left toward the workbench.
        # Spawn 1 tile south of the original marker.
        npc_tile = pygame.Vector2(7.5, 8.5)
        npc_position = pygame.Vector2(
            building_rect.left + npc_tile.x * self.tile_size,
            building_rect.top + npc_tile.y * self.tile_size,
        )
        self.npcs.append(AnimatedNPC(self.blacksmith_frames, npc_position))

    def _build_collision_rects(self) -> None:
        building_mapping = {
            "I": ("inn", self.buildings["inn"], True),
            "B": ("blacksmith", self.buildings["blacksmith"], True),
            "S": ("stalls", self.buildings["stalls"], False),
            "1": ("house_1", self.buildings["house_1"], True),
            "2": ("house_2", self.buildings["house_2"], True),
            "3": ("house_3", self.buildings["house_3"], True),
            "4": ("house_4", self.buildings["house_4"], True),
            "5": ("house_5", self.buildings["house_5"], True),
        }
        doorway_offsets = {
            "inn": 0,
            "blacksmith": -3,
            "house_1": -1,
            "house_2": -2,
            "house_3": 0,
            "house_4": -1,
            "house_5": 0,
            "stalls": 0,
        }
        doorway_width_tiles = 2
        doorway_depth_tiles = 1
        for y, row in enumerate(self.ascii_map):
            for x, tile in enumerate(row):
                building_entry = building_mapping.get(tile)
                if building_entry is None:
                    continue
                building_name, sprite, has_entrance = building_entry
                rect = sprite.get_rect()
                rect.midbottom = (
                    x * self.tile_size + self.tile_size // 2,
                    y * self.tile_size + self.tile_size,
                )
                visible_rect = sprite.get_bounding_rect()
                collision_rect = visible_rect.move(rect.topleft)
                shrink_by = self.tile_size
                new_width = max(1, collision_rect.width - 2 * shrink_by)
                new_height = max(1, collision_rect.height - 2 * shrink_by)
                shrunken_rect = pygame.Rect(0, 0, new_width, new_height)
                shrunken_rect.center = collision_rect.center
                doorway_offset_tiles = doorway_offsets.get(building_name, 0)
                doorway_center_x = shrunken_rect.centerx + int(
                    doorway_offset_tiles * self.tile_size
                )
                doorway_width = doorway_width_tiles * self.tile_size
                doorway_depth = min(
                    doorway_depth_tiles * self.tile_size, shrunken_rect.height
                )
                doorway_half_width = doorway_width // 2
                doorway_center_x = max(
                    shrunken_rect.left + doorway_half_width,
                    min(doorway_center_x, shrunken_rect.right - doorway_half_width),
                )
                doorway_rect = pygame.Rect(0, 0, doorway_width, doorway_depth)
                doorway_rect.midbottom = (doorway_center_x, shrunken_rect.bottom)

                if has_entrance:
                    exterior_spawn = pygame.Vector2(
                        doorway_rect.centerx,
                        doorway_rect.bottom + (self.tile_size *2),
                    )
                    self.building_entrances.append(
                        BuildingEntrance(
                            building_name=building_name,
                            door_rect=doorway_rect,
                            exterior_spawn=exterior_spawn,
                        )
                    )

                top_height = shrunken_rect.height - doorway_rect.height
                if top_height > 0:
                    top_rect = pygame.Rect(
                        shrunken_rect.left,
                        shrunken_rect.top,
                        shrunken_rect.width,
                        top_height,
                    )
                    self.building_colliders.append(top_rect)

                left_width = doorway_rect.left - shrunken_rect.left
                if left_width > 0:
                    left_rect = pygame.Rect(
                        shrunken_rect.left,
                        doorway_rect.top,
                        left_width,
                        doorway_rect.height,
                    )
                    self.building_colliders.append(left_rect)

                right_width = shrunken_rect.right - doorway_rect.right
                if right_width > 0:
                    right_rect = pygame.Rect(
                        doorway_rect.right,
                        doorway_rect.top,
                        right_width,
                        doorway_rect.height,
                    )
                    self.building_colliders.append(right_rect)

    def get_entrance(self, player_rect: pygame.Rect) -> BuildingEntrance | None:
        for entrance in self.building_entrances:
            if player_rect.colliderect(entrance.door_rect):
                return entrance
        return None

    def update(self, delta_time: float) -> None:
        for npc in self.npcs:
            npc.update(delta_time)

    def draw(self, screen: pygame.Surface, offset: pygame.Vector2) -> None:
        screen.blit(self.surface, (-offset.x, -offset.y))
        for npc in self.npcs:
            npc.draw(screen, offset)


class AnimatedNPC:
    def __init__(self, frames: list[pygame.Surface], position: pygame.Vector2):
        self.frames = frames
        self.frame_index = 0
        self.frame_time = 0.0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(midbottom=position)

    def update(self, delta_time: float) -> None:
        self.frame_time += delta_time
        if self.frame_time >= 0.12:
            self.frame_time = 0.0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)

    def draw(self, screen: pygame.Surface, offset: pygame.Vector2) -> None:
        screen.blit(
            self.image,
            (self.rect.x - offset.x, self.rect.y - offset.y),
        )


class InteriorMap:
    def __init__(self, scale_factor: float, building_name: str):
        self.scale_factor = scale_factor
        self.building_name = building_name
        self.tile_size = int(TILE_SIZE * BASE_SCALE * scale_factor)
        self.columns = 24
        self.rows = 18
        self.map_size = (
            self.columns * self.tile_size,
            self.rows * self.tile_size,
        )
        self.surface = pygame.Surface(self.map_size, pygame.SRCALPHA)
        self.colliders: list[pygame.Rect] = []
        self.furniture_colliders: list[pygame.Rect] = []
        self.exit_rect = pygame.Rect(0, 0, 0, 0)
        self.entry_spawn = pygame.Vector2(0, 0)
        self._load_assets()
        self._build_map()
        self._build_colliders()

    def _scale_to_tile(self, surface: pygame.Surface) -> pygame.Surface:
        return pygame.transform.scale(surface, (self.tile_size, self.tile_size))

    def _load_assets(self) -> None:
        floor_sheet = SpriteSheet(
            TOWN_ASSETS_DIR / "Buildings" / "Houses_Interiors" / "Wood_Floor_Tiles.png",
            TILE_SIZE,
            TILE_SIZE,
        )
        wall_sheet = SpriteSheet(
            TOWN_ASSETS_DIR / "Buildings" / "Houses_Interiors" / "Interior_Walls.png",
            TILE_SIZE,
            TILE_SIZE,
        )
        bed_sheet = SpriteSheet(
            TOWN_ASSETS_DIR / "Buildings" / "House_Decor" / "Beds.png",
            TILE_SIZE,
            TILE_SIZE,
        )
        table_sheet = SpriteSheet(
            TOWN_ASSETS_DIR / "Buildings" / "House_Decor" / "Tables.png",
            TILE_SIZE,
            TILE_SIZE,
        )
        chair_sheet = SpriteSheet(
            TOWN_ASSETS_DIR / "Buildings" / "House_Decor" / "Chairs.png",
            TILE_SIZE,
            TILE_SIZE,
        )
        shelf_sheet = SpriteSheet(
            TOWN_ASSETS_DIR / "Buildings" / "House_Decor" / "BookShelves.png",
            TILE_SIZE,
            TILE_SIZE,
        )
        drawer_sheet = SpriteSheet(
            TOWN_ASSETS_DIR / "Buildings" / "House_Decor" / "Drawers.png",
            TILE_SIZE,
            TILE_SIZE,
        )
        decor_sheet = SpriteSheet(
            TOWN_ASSETS_DIR / "Buildings" / "House_Decor" / "Indoor_Decor.png",
            TILE_SIZE,
            TILE_SIZE,
        )
        planter_sheet = SpriteSheet(
            TOWN_ASSETS_DIR / "Buildings" / "House_Decor" / "Planters.png",
            TILE_SIZE,
            TILE_SIZE,
        )
        lamp_sheet = SpriteSheet(
            TOWN_ASSETS_DIR / "Buildings" / "House_Decor" / "Standing_Lamps.png",
            TILE_SIZE,
            TILE_SIZE,
        )
        furnace_sheet = SpriteSheet(
            TOWN_ASSETS_DIR / "Buildings" / "House_Decor" / "Furnace_Anim.png",
            TILE_SIZE,
            TILE_SIZE,
        )
        anvil_sheet = SpriteSheet(
            TOWN_ASSETS_DIR / "Buildings" / "House_Decor" / "Anvil_Anim.png",
            TILE_SIZE,
            TILE_SIZE,
        )
        chest_sheet = SpriteSheet(
            TOWN_ASSETS_DIR / "Buildings" / "House_Decor" / "Chest_Anim.png",
            TILE_SIZE,
            TILE_SIZE,
        )

        self.floor_tile = self._scale_to_tile(floor_sheet.get_frame(0, 0))
        self.wall_tile = self._scale_to_tile(wall_sheet.get_frame(4, 3))
        self.furniture = {
            "bed_tan": self._build_sprite(bed_sheet, 0, 0, 2, 2),
            "bed_blue": self._build_sprite(bed_sheet, 0, 2, 2, 2),
            "bed_green": self._build_sprite(bed_sheet, 0, 4, 2, 2),
            "bed_pink": self._build_sprite(bed_sheet, 0, 6, 2, 2),
            "bed_yellow": self._build_sprite(bed_sheet, 0, 8, 2, 2),
            "bed_red": self._build_sprite(bed_sheet, 0, 10, 2, 2),
            "table_small": self._build_sprite(table_sheet, 0, 0, 2, 2),
            "table_large": self._build_sprite(table_sheet, 0, 1, 3, 2),
            "chair": self._build_sprite(chair_sheet, 0, 0, 1, 2),
            "stool": self._build_sprite(chair_sheet, 6, 2, 1, 1),
            "shelf_small": self._build_sprite(shelf_sheet, 0, 0, 1, 2),
            "shelf_large": self._build_sprite(shelf_sheet, 1, 0, 2, 2),
            "dresser": self._build_sprite(drawer_sheet, 0, 2, 2, 2),
            "barrel_stack": self._build_sprite(decor_sheet, 0, 8, 2, 2),
            "planter_box": self._build_sprite(planter_sheet, 0, 0, 2, 1),
            "lamp": self._build_sprite(lamp_sheet, 0, 0, 1, 2),
            "furnace": self._build_sprite(furnace_sheet, 0, 0, 1, 2),
            "anvil": self._build_sprite(anvil_sheet, 0, 0, 1, 1),
            "chest": self._build_sprite(chest_sheet, 0, 0, 1, 1),
            "potted_tree": self._build_sprite(decor_sheet, 0, 4, 2, 2),
        }

    def _blit_tile(self, tile: pygame.Surface, grid_x: int, grid_y: int) -> None:
        self.surface.blit(tile, (grid_x * self.tile_size, grid_y * self.tile_size))

    def _build_sprite(
        self,
        sheet: SpriteSheet,
        start_col: int,
        start_row: int,
        width_tiles: int,
        height_tiles: int,
    ) -> pygame.Surface:
        surface = pygame.Surface(
            (width_tiles * self.tile_size, height_tiles * self.tile_size),
            pygame.SRCALPHA,
        )
        for y in range(height_tiles):
            for x in range(width_tiles):
                frame = sheet.get_frame(start_col + x, start_row + y)
                frame = self._scale_to_tile(frame)
                surface.blit(
                    frame,
                    (x * self.tile_size, y * self.tile_size),
                )
        return surface

    def _place_furniture(
        self,
        sprite: pygame.Surface,
        grid_x: int,
        grid_y: int,
        collidable: bool = True,
    ) -> None:
        top_left = (grid_x * self.tile_size, grid_y * self.tile_size)
        self.surface.blit(sprite, top_left)
        if collidable:
            rect = sprite.get_rect(topleft=top_left)
            self.furniture_colliders.append(rect)

    def _build_map(self) -> None:
        # Fill entire interior with floor tiles
        for y in range(self.rows):
            for x in range(self.columns):
                self._blit_tile(self.floor_tile, x, y)

        door_width_tiles = 2
        door_start = (self.columns - door_width_tiles) // 2
        bottom_y = self.rows - 1

        # Top wall - full width with wooden wall tile
        for x in range(self.columns):
            self._blit_tile(self.wall_tile, x, 0)

        # Bottom wall - with 2-tile door opening at center
        for x in range(self.columns):
            if door_start <= x < door_start + door_width_tiles:
                # Door opening - use floor tile for continuity
                self._blit_tile(self.floor_tile, x, bottom_y)
            else:
                self._blit_tile(self.wall_tile, x, bottom_y)

        # Side walls - full height
        for y in range(1, self.rows - 1):
            self._blit_tile(self.wall_tile, 0, y)
            self._blit_tile(self.wall_tile, self.columns - 1, y)

        self._build_furnishings()

    def _build_furnishings(self) -> None:
        self.furniture_colliders.clear()
        if self.building_name == "inn":
            self._layout_inn()
        elif self.building_name == "blacksmith":
            self._layout_blacksmith()
        elif self.building_name == "house_1":
            self._layout_house_one()
        elif self.building_name == "house_2":
            self._layout_house_two()
        elif self.building_name == "house_3":
            self._layout_house_three()
        elif self.building_name == "house_4":
            self._layout_house_four()
        elif self.building_name == "house_5":
            self._layout_house_five()

    def _layout_inn(self) -> None:
        self._place_furniture(self.furniture["table_large"], 2, 2)
        for x in range(2, 5):
            self._place_furniture(self.furniture["stool"], x, 4)
        self._place_furniture(self.furniture["shelf_large"], 18, 2)
        self._place_furniture(self.furniture["barrel_stack"], 18, 5)
        self._place_furniture(self.furniture["chest"], 20, 5)

        self._place_furniture(self.furniture["table_small"], 10, 7)
        for x in range(10, 12):
            self._place_furniture(self.furniture["chair"], x, 6)
            self._place_furniture(self.furniture["chair"], x, 8)
        self._place_furniture(self.furniture["table_small"], 13, 11)
        for x in range(13, 15):
            self._place_furniture(self.furniture["chair"], x, 10)
            self._place_furniture(self.furniture["chair"], x, 12)

        self._place_furniture(self.furniture["lamp"], 2, 13, collidable=False)
        self._place_furniture(self.furniture["lamp"], 21, 13, collidable=False)
        self._place_furniture(self.furniture["planter_box"], 17, 14)
        self._place_furniture(self.furniture["potted_tree"], 4, 11)

    def _layout_blacksmith(self) -> None:
        self._place_furniture(self.furniture["furnace"], 3, 2)
        self._place_furniture(self.furniture["anvil"], 5, 4)
        self._place_furniture(self.furniture["table_large"], 9, 4)
        self._place_furniture(self.furniture["table_small"], 13, 8)
        self._place_furniture(self.furniture["stool"], 13, 9)
        self._place_furniture(self.furniture["shelf_large"], 18, 2)
        self._place_furniture(self.furniture["barrel_stack"], 18, 6)
        self._place_furniture(self.furniture["chest"], 20, 7)
        self._place_furniture(self.furniture["lamp"], 2, 13, collidable=False)

    def _layout_house_one(self) -> None:
        self._place_furniture(self.furniture["bed_green"], 2, 2)
        self._place_furniture(self.furniture["dresser"], 2, 5)
        self._place_furniture(self.furniture["table_small"], 11, 6)
        self._place_furniture(self.furniture["chair"], 11, 5)
        self._place_furniture(self.furniture["chair"], 12, 7)
        self._place_furniture(self.furniture["shelf_small"], 18, 2)
        self._place_furniture(self.furniture["chest"], 17, 6)
        self._place_furniture(self.furniture["planter_box"], 16, 12)
        self._place_furniture(self.furniture["lamp"], 5, 2, collidable=False)

    def _layout_house_two(self) -> None:
        self._place_furniture(self.furniture["bed_blue"], 2, 3)
        self._place_furniture(self.furniture["shelf_small"], 16, 2)
        self._place_furniture(self.furniture["shelf_large"], 18, 2)
        self._place_furniture(self.furniture["table_small"], 11, 6)
        self._place_furniture(self.furniture["chair"], 10, 6)
        self._place_furniture(self.furniture["chair"], 12, 7)
        self._place_furniture(self.furniture["dresser"], 2, 7)
        self._place_furniture(self.furniture["lamp"], 6, 3, collidable=False)
        self._place_furniture(self.furniture["planter_box"], 15, 12)

    def _layout_house_three(self) -> None:
        self._place_furniture(self.furniture["bed_red"], 2, 2)
        self._place_furniture(self.furniture["table_large"], 9, 6)
        self._place_furniture(self.furniture["chair"], 9, 5)
        self._place_furniture(self.furniture["chair"], 10, 9)
        self._place_furniture(self.furniture["chair"], 11, 5)
        self._place_furniture(self.furniture["barrel_stack"], 17, 3)
        self._place_furniture(self.furniture["barrel_stack"], 19, 3)
        self._place_furniture(self.furniture["chest"], 18, 7)
        self._place_furniture(self.furniture["shelf_small"], 20, 2)
        self._place_furniture(self.furniture["lamp"], 5, 2, collidable=False)

    def _layout_house_four(self) -> None:
        self._place_furniture(self.furniture["bed_yellow"], 3, 2)
        self._place_furniture(self.furniture["table_small"], 11, 5)
        self._place_furniture(self.furniture["stool"], 10, 6)
        self._place_furniture(self.furniture["stool"], 13, 6)
        self._place_furniture(self.furniture["dresser"], 3, 6)
        self._place_furniture(self.furniture["barrel_stack"], 17, 5)
        self._place_furniture(self.furniture["shelf_large"], 18, 2)
        self._place_furniture(self.furniture["planter_box"], 16, 12)
        self._place_furniture(self.furniture["lamp"], 6, 2, collidable=False)

    def _layout_house_five(self) -> None:
        self._place_furniture(self.furniture["bed_pink"], 2, 3)
        self._place_furniture(self.furniture["table_large"], 9, 5)
        self._place_furniture(self.furniture["stool"], 9, 7)
        self._place_furniture(self.furniture["stool"], 11, 7)
        self._place_furniture(self.furniture["dresser"], 2, 7)
        self._place_furniture(self.furniture["shelf_small"], 18, 2)
        self._place_furniture(self.furniture["planter_box"], 15, 12)
        self._place_furniture(self.furniture["potted_tree"], 4, 10)
        self._place_furniture(self.furniture["lamp"], 6, 3, collidable=False)

    def _build_colliders(self) -> None:
        door_width_tiles = 2
        door_start = (self.columns - door_width_tiles) // 2
        raw_left = door_start * self.tile_size
        door_right = raw_left + door_width_tiles * self.tile_size
        door_left = max(0, raw_left)
        door_right = min(self.map_size[0], door_right)
        door_width = door_right - door_left
        bottom_y = (self.rows - 1) * self.tile_size
        self.exit_rect = pygame.Rect(door_left, bottom_y, door_width, self.tile_size)
        self.entry_spawn = pygame.Vector2(self.exit_rect.centerx, self.exit_rect.top)

        wall_offset = self.tile_size
        self.colliders.append(
            pygame.Rect(0, -wall_offset, self.map_size[0], self.tile_size)
        )
        self.colliders.append(
            pygame.Rect(-wall_offset, 0, self.tile_size, self.map_size[1])
        )
        self.colliders.append(
            pygame.Rect(
                self.map_size[0],
                0,
                self.tile_size,
                self.map_size[1],
            )
        )
        if door_left > 0:
            self.colliders.append(
                pygame.Rect(0, bottom_y + wall_offset, door_left, self.tile_size)
            )
        right_start = door_right
        if right_start < self.map_size[0]:
            self.colliders.append(
                pygame.Rect(
                    right_start,
                    bottom_y + wall_offset,
                    self.map_size[0] - right_start,
                    self.tile_size,
                )
            )
        self.colliders.extend(self.furniture_colliders)

    def draw(self, screen: pygame.Surface, offset: pygame.Vector2) -> None:
        screen.blit(self.surface, (-offset.x, -offset.y))


class InnInteriorMap:
    """Two-floor interior map for the Inn building."""

    def __init__(self, scale_factor: float):
        self.scale_factor = scale_factor
        self.tile_size = int(TILE_SIZE * BASE_SCALE * scale_factor)
        self.columns = 24
        self.rows = 18
        self.map_size = (
            self.columns * self.tile_size,
            self.rows * self.tile_size,
        )
        self.current_floor = 0  # 0 = ground floor, 1 = second floor
        self.floors: list[pygame.Surface] = []
        self.floor_colliders: list[list[pygame.Rect]] = [[], []]
        self.furniture_colliders: list[list[pygame.Rect]] = [[], []]

        # Transition rects
        self.exit_rect = pygame.Rect(0, 0, 0, 0)  # Exit to town (ground floor only)
        self.stair_up_rect = pygame.Rect(0, 0, 0, 0)  # Go to second floor
        self.stair_down_rect = pygame.Rect(0, 0, 0, 0)  # Go to ground floor
        self.entry_spawn = pygame.Vector2(0, 0)
        self.stair_up_spawn = pygame.Vector2(0, 0)  # Spawn point on second floor
        self.stair_down_spawn = pygame.Vector2(0, 0)  # Spawn point on ground floor

        self._load_assets()
        self._build_floors()
        self._build_colliders()

    def _scale_to_tile(self, surface: pygame.Surface) -> pygame.Surface:
        return pygame.transform.scale(surface, (self.tile_size, self.tile_size))

    def _load_assets(self) -> None:
        floor_sheet = SpriteSheet(
            TOWN_ASSETS_DIR / "Buildings" / "Houses_Interiors" / "Wood_Floor_Tiles.png",
            TILE_SIZE,
            TILE_SIZE,
        )
        wall_sheet = SpriteSheet(
            TOWN_ASSETS_DIR / "Buildings" / "Houses_Interiors" / "Interior_Walls.png",
            TILE_SIZE,
            TILE_SIZE,
        )
        stair_sheet = SpriteSheet(
            TOWN_ASSETS_DIR / "Buildings" / "Houses_Interiors" / "Wood_Stairs.png",
            TILE_SIZE,
            TILE_SIZE,
        )

        self.floor_tile = self._scale_to_tile(floor_sheet.get_frame(0, 0))
        self.wall_tile = self._scale_to_tile(wall_sheet.get_frame(4, 3))
        # Stair tiles - the sprite appears to be 4 tiles wide x 1 tile tall
        self.stair_tiles = [
            self._scale_to_tile(stair_sheet.get_frame(col, 0)) for col in range(4)
        ]

    def _blit_tile(
        self, surface: pygame.Surface, tile: pygame.Surface, grid_x: int, grid_y: int
    ) -> None:
        surface.blit(tile, (grid_x * self.tile_size, grid_y * self.tile_size))

    def _build_floors(self) -> None:
        # Build ground floor (floor 0)
        ground_floor = pygame.Surface(self.map_size, pygame.SRCALPHA)
        self._build_ground_floor(ground_floor)
        self.floors.append(ground_floor)

        # Build second floor (floor 1)
        second_floor = pygame.Surface(self.map_size, pygame.SRCALPHA)
        self._build_second_floor(second_floor)
        self.floors.append(second_floor)

    def _build_ground_floor(self, surface: pygame.Surface) -> None:
        """Build the ground floor with entrance door and stairs going up."""
        # Fill with floor tiles
        for y in range(self.rows):
            for x in range(self.columns):
                self._blit_tile(surface, self.floor_tile, x, y)

        door_width_tiles = 2
        door_start = (self.columns - door_width_tiles) // 2
        bottom_y = self.rows - 1

        # Top wall
        for x in range(self.columns):
            self._blit_tile(surface, self.wall_tile, x, 0)

        # Bottom wall with door opening
        for x in range(self.columns):
            if door_start <= x < door_start + door_width_tiles:
                self._blit_tile(surface, self.floor_tile, x, bottom_y)
            else:
                self._blit_tile(surface, self.wall_tile, x, bottom_y)

        # Side walls
        for y in range(1, self.rows - 1):
            self._blit_tile(surface, self.wall_tile, 0, y)
            self._blit_tile(surface, self.wall_tile, self.columns - 1, y)

        # Staircase going up on the right side (4 tiles wide, positioned against wall)
        stair_x = self.columns - 6  # Position stairs 1 tile from right wall
        stair_y = 2  # Near top wall
        stair_width = 4
        stair_height = 3

        # Draw stair tiles (repeated vertically for depth)
        for row in range(stair_height):
            for col in range(stair_width):
                self._blit_tile(surface, self.stair_tiles[col], stair_x + col, stair_y + row)

    def _build_second_floor(self, surface: pygame.Surface) -> None:
        """Build the second floor with stairs going down (no exterior door)."""
        # Fill with floor tiles
        for y in range(self.rows):
            for x in range(self.columns):
                self._blit_tile(surface, self.floor_tile, x, y)

        # All four walls (no door opening on second floor)
        # Top wall
        for x in range(self.columns):
            self._blit_tile(surface, self.wall_tile, x, 0)

        # Bottom wall (complete, no door)
        for x in range(self.columns):
            self._blit_tile(surface, self.wall_tile, x, self.rows - 1)

        # Side walls
        for y in range(1, self.rows - 1):
            self._blit_tile(surface, self.wall_tile, 0, y)
            self._blit_tile(surface, self.wall_tile, self.columns - 1, y)

        # Staircase going down on the right side (same position as ground floor)
        stair_x = self.columns - 6
        stair_y = 2
        stair_width = 4
        stair_height = 3

        # Draw stair tiles
        for row in range(stair_height):
            for col in range(stair_width):
                self._blit_tile(surface, self.stair_tiles[col], stair_x + col, stair_y + row)

    def _build_colliders(self) -> None:
        """Build collision rects for both floors."""
        door_width_tiles = 2
        door_start = (self.columns - door_width_tiles) // 2
        raw_left = door_start * self.tile_size
        door_right = raw_left + door_width_tiles * self.tile_size
        door_left = max(0, raw_left)
        door_right = min(self.map_size[0], door_right)
        door_width = door_right - door_left
        bottom_y = (self.rows - 1) * self.tile_size

        # Exit rect (ground floor only)
        self.exit_rect = pygame.Rect(door_left, bottom_y, door_width, self.tile_size)
        self.entry_spawn = pygame.Vector2(self.exit_rect.centerx, self.exit_rect.top)

        # Staircase transition zones
        stair_x = self.columns - 6
        stair_y = 2
        stair_width = 4
        stair_height = 3

        stair_rect_x = stair_x * self.tile_size
        stair_rect_y = stair_y * self.tile_size
        stair_rect_w = stair_width * self.tile_size
        stair_rect_h = stair_height * self.tile_size

        # Stair up trigger (on ground floor)
        self.stair_up_rect = pygame.Rect(stair_rect_x, stair_rect_y, stair_rect_w, stair_rect_h)
        # Spawn point on second floor (in front of stairs)
        self.stair_up_spawn = pygame.Vector2(
            stair_rect_x + stair_rect_w // 2,
            stair_rect_y + stair_rect_h + self.tile_size,
        )

        # Stair down trigger (on second floor, same position)
        self.stair_down_rect = pygame.Rect(stair_rect_x, stair_rect_y, stair_rect_w, stair_rect_h)
        # Spawn point on ground floor (in front of stairs)
        self.stair_down_spawn = pygame.Vector2(
            stair_rect_x + stair_rect_w // 2,
            stair_rect_y + stair_rect_h + self.tile_size,
        )

        # Build wall colliders for both floors
        wall_offset = self.tile_size

        # Ground floor colliders (floor 0)
        ground_colliders = []
        # Top wall
        ground_colliders.append(
            pygame.Rect(0, -wall_offset, self.map_size[0], self.tile_size)
        )
        # Left wall
        ground_colliders.append(
            pygame.Rect(-wall_offset, 0, self.tile_size, self.map_size[1])
        )
        # Right wall
        ground_colliders.append(
            pygame.Rect(self.map_size[0], 0, self.tile_size, self.map_size[1])
        )
        # Bottom wall segments (around door)
        if door_left > 0:
            ground_colliders.append(
                pygame.Rect(0, bottom_y + wall_offset, door_left, self.tile_size)
            )
        right_start = door_right
        if right_start < self.map_size[0]:
            ground_colliders.append(
                pygame.Rect(
                    right_start,
                    bottom_y + wall_offset,
                    self.map_size[0] - right_start,
                    self.tile_size,
                )
            )
        self.floor_colliders[0] = ground_colliders

        # Second floor colliders (floor 1)
        second_colliders = []
        # Top wall
        second_colliders.append(
            pygame.Rect(0, -wall_offset, self.map_size[0], self.tile_size)
        )
        # Left wall
        second_colliders.append(
            pygame.Rect(-wall_offset, 0, self.tile_size, self.map_size[1])
        )
        # Right wall
        second_colliders.append(
            pygame.Rect(self.map_size[0], 0, self.tile_size, self.map_size[1])
        )
        # Bottom wall (complete, no door)
        second_colliders.append(
            pygame.Rect(0, bottom_y + wall_offset, self.map_size[0], self.tile_size)
        )
        self.floor_colliders[1] = second_colliders

    @property
    def colliders(self) -> list[pygame.Rect]:
        """Return colliders for current floor."""
        return self.floor_colliders[self.current_floor] + self.furniture_colliders[self.current_floor]

    def check_stair_transition(self, player_rect: pygame.Rect) -> int | None:
        """Check if player should transition floors. Returns new floor number or None."""
        if self.current_floor == 0:
            if player_rect.colliderect(self.stair_up_rect):
                return 1
        elif self.current_floor == 1:
            if player_rect.colliderect(self.stair_down_rect):
                return 0
        return None

    def transition_to_floor(self, new_floor: int) -> pygame.Vector2:
        """Transition to new floor and return spawn position."""
        self.current_floor = new_floor
        if new_floor == 1:
            return self.stair_up_spawn
        else:
            return self.stair_down_spawn

    def draw(self, screen: pygame.Surface, offset: pygame.Vector2) -> None:
        screen.blit(self.floors[self.current_floor], (-offset.x, -offset.y))
