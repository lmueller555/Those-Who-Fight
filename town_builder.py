import pygame

from sprites import SpriteSheet, BASE_SCALE, TILE_SIZE, TOWN_ASSETS_DIR, BASE_DIR


class TownMap:
    def __init__(self, scale_factor: float):
        self.scale_factor = scale_factor
        self.tile_size = int(TILE_SIZE * BASE_SCALE * scale_factor)
        self.columns = 50  # Doubled from 25 to account for 16x16 tiles instead of 32x32
        self.rows = 54  # Doubled from 27 to account for 16x16 tiles instead of 32x32
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

    def _scale_to_tile(self, surface: pygame.Surface) -> pygame.Surface:
        """Scale a surface to exactly fit tile_size x tile_size"""
        return pygame.transform.scale(surface, (self.tile_size, self.tile_size))

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

        # Main road oval loop (all coordinates doubled for 16x16 tiles)
        # Paths are 3 tiles wide, using the full 3x3 tileset
        loop_left, loop_right = 12, 36  # Was 6, 18
        loop_top, loop_bottom = 16, 38  # Was 8, 19

        # Top horizontal section (3 tiles wide - using horizontal tiles from 3x3 grid)
        # Top-left corner (3x3 block) - horizontal path going left-right
        self._blit_tile(self.path_tiles["horizontal_top_left"], loop_left, loop_top)
        self._blit_tile(self.path_tiles["horizontal_top"], loop_left, loop_top + 1)
        self._blit_tile(self.path_tiles["horizontal_bottom_left"], loop_left, loop_top + 2)
        # Top horizontal run - full 3-tile height
        for x in range(loop_left + 1, loop_right):
            self._blit_tile(self.path_tiles["horizontal_top"], x, loop_top)
            self._blit_tile(self.path_tiles["center"], x, loop_top + 1)
            self._blit_tile(self.path_tiles["horizontal_bottom"], x, loop_top + 2)
        # Top-right corner (3x3 block) - horizontal path going left-right
        self._blit_tile(self.path_tiles["horizontal_top_right"], loop_right, loop_top)
        self._blit_tile(self.path_tiles["horizontal_top"], loop_right, loop_top + 1)
        self._blit_tile(self.path_tiles["horizontal_bottom_right"], loop_right, loop_top + 2)

        # Bottom horizontal section (3 tiles wide - using horizontal tiles from 3x3 grid)
        # Bottom-left corner (3x3 block) - horizontal path going left-right
        self._blit_tile(self.path_tiles["horizontal_top_left"], loop_left, loop_bottom - 2)
        self._blit_tile(self.path_tiles["horizontal_top"], loop_left, loop_bottom - 1)
        self._blit_tile(self.path_tiles["horizontal_bottom_left"], loop_left, loop_bottom)
        # Bottom horizontal run - full 3-tile height
        for x in range(loop_left + 1, loop_right):
            self._blit_tile(self.path_tiles["horizontal_top"], x, loop_bottom - 2)
            self._blit_tile(self.path_tiles["center"], x, loop_bottom - 1)
            self._blit_tile(self.path_tiles["horizontal_bottom"], x, loop_bottom)
        # Bottom-right corner (3x3 block) - horizontal path going left-right
        self._blit_tile(self.path_tiles["horizontal_top_right"], loop_right, loop_bottom - 2)
        self._blit_tile(self.path_tiles["horizontal_top"], loop_right, loop_bottom - 1)
        self._blit_tile(self.path_tiles["horizontal_bottom_right"], loop_right, loop_bottom)

        # Vertical sections (3 tiles wide - using middle row of 3x3 grid)
        for y in range(loop_top + 3, loop_bottom - 2):
            # Left side - full 3-tile width (using middle row: left edge, center, right edge)
            self._blit_tile(self.path_tiles["vertical_left"], loop_left, y)
            self._blit_tile(self.path_tiles["center"], loop_left + 1, y)
            self._blit_tile(self.path_tiles["vertical_right"], loop_left + 2, y)
            # Right side - full 3-tile width (using middle row: left edge, center, right edge)
            self._blit_tile(self.path_tiles["vertical_left"], loop_right - 2, y)
            self._blit_tile(self.path_tiles["center"], loop_right - 1, y)
            self._blit_tile(self.path_tiles["vertical_right"], loop_right, y)

        # South entrance road (vertical, 3 tiles wide - using middle row)
        center_x = self.columns // 2
        for y in range(loop_bottom + 1, self.rows):
            self._blit_tile(self.path_tiles["vertical_left"], center_x - 1, y)
            self._blit_tile(self.path_tiles["center"], center_x, y)
            self._blit_tile(self.path_tiles["vertical_right"], center_x + 1, y)

        # Connection where south entrance meets bottom horizontal path
        # Bottom left corner uses bottom-right inner corner, bottom right corner uses bottom-left inner corner
        self._blit_tile(self.path_tiles["inner_corner_bottom_right"], center_x - 1, loop_bottom)
        self._blit_tile(self.path_tiles["center"], center_x, loop_bottom)
        self._blit_tile(self.path_tiles["inner_corner_bottom_left"], center_x + 1, loop_bottom)
        # Fill the intersection area with center tiles
        self._blit_tile(self.path_tiles["center"], center_x - 1, loop_bottom - 1)
        self._blit_tile(self.path_tiles["center"], center_x, loop_bottom - 1)
        self._blit_tile(self.path_tiles["center"], center_x + 1, loop_bottom - 1)

        # Central plaza (10x10 square) - all center tiles (pure path)
        plaza_left, plaza_top = 20, 22  # Was 10, 11
        for y in range(plaza_top, plaza_top + 10):  # Was +5
            for x in range(plaza_left, plaza_left + 10):  # Was +5
                self._blit_tile(self.path_tiles["center"], x, y)

        # North branch to market stalls (vertical, 3 tiles wide - using middle row)
        for y in range(loop_top - 6, loop_top):  # Was loop_top - 3
            self._blit_tile(self.path_tiles["vertical_left"], center_x - 1, y)
            self._blit_tile(self.path_tiles["center"], center_x, y)
            self._blit_tile(self.path_tiles["vertical_right"], center_x + 1, y)

        # Connection where north branch meets top horizontal path
        # Top left corner uses top-right inner corner, top right corner uses top-left inner corner
        self._blit_tile(self.path_tiles["inner_corner_top_right"], center_x - 1, loop_top)
        self._blit_tile(self.path_tiles["center"], center_x, loop_top)
        self._blit_tile(self.path_tiles["inner_corner_top_left"], center_x + 1, loop_top)
        # Fill the intersection area with center tiles
        self._blit_tile(self.path_tiles["center"], center_x - 1, loop_top + 1)
        self._blit_tile(self.path_tiles["center"], center_x, loop_top + 1)
        self._blit_tile(self.path_tiles["center"], center_x + 1, loop_top + 1)

        # West branch to blacksmith (horizontal, 3 tiles wide)
        for x in range(loop_left - 6, loop_left):  # Was loop_left - 3
            self._blit_tile(self.path_tiles["horizontal_top"], x, 24)
            self._blit_tile(self.path_tiles["center"], x, 25)
            self._blit_tile(self.path_tiles["horizontal_bottom"], x, 26)

        # L-intersection where west branch meets left vertical path
        # Complete the 3-tile wide vertical path with 3-tile tall horizontal branch
        # Top row of L
        self._blit_tile(self.path_tiles["horizontal_top"], loop_left, 24)
        self._blit_tile(self.path_tiles["center"], loop_left + 1, 24)
        self._blit_tile(self.path_tiles["horizontal_top_right"], loop_left + 2, 24)
        # Middle row of L
        self._blit_tile(self.path_tiles["center"], loop_left, 25)
        self._blit_tile(self.path_tiles["center"], loop_left + 1, 25)
        self._blit_tile(self.path_tiles["vertical_right"], loop_left + 2, 25)
        # Bottom row of L
        self._blit_tile(self.path_tiles["horizontal_bottom"], loop_left, 26)
        self._blit_tile(self.path_tiles["horizontal_bottom"], loop_left + 1, 26)
        self._blit_tile(self.path_tiles["horizontal_bottom_right"], loop_left + 2, 26)

        # East branches for houses (horizontal, 3 tiles wide)
        for x in range(loop_right + 1, loop_right + 6):  # Was loop_right + 3
            self._blit_tile(self.path_tiles["horizontal_top"], x, 16)
            self._blit_tile(self.path_tiles["center"], x, 17)
            self._blit_tile(self.path_tiles["horizontal_bottom"], x, 18)

        # L-intersection where east branch meets right vertical path
        # Complete the 3-tile wide vertical path with 3-tile tall horizontal branch
        # Top row of L
        self._blit_tile(self.path_tiles["horizontal_top_left"], loop_right - 2, 16)
        self._blit_tile(self.path_tiles["horizontal_top"], loop_right - 1, 16)
        self._blit_tile(self.path_tiles["horizontal_top"], loop_right, 16)
        # Middle row of L
        self._blit_tile(self.path_tiles["vertical_left"], loop_right - 2, 17)
        self._blit_tile(self.path_tiles["center"], loop_right - 1, 17)
        self._blit_tile(self.path_tiles["center"], loop_right, 17)
        # Bottom row of L
        self._blit_tile(self.path_tiles["horizontal_bottom_left"], loop_right - 2, 18)
        self._blit_tile(self.path_tiles["horizontal_bottom"], loop_right - 1, 18)
        self._blit_tile(self.path_tiles["horizontal_bottom"], loop_right, 18)

        # South residential path (vertical, 3 tiles wide - using middle row)
        for y in range(loop_bottom + 1, loop_bottom + 8):  # Was loop_bottom + 4
            self._blit_tile(self.path_tiles["vertical_left"], 14, y)
            self._blit_tile(self.path_tiles["center"], 15, y)
            self._blit_tile(self.path_tiles["vertical_right"], 16, y)

        # Buildings - placed strategically around the loop (coordinates doubled)
        self._blit_object(self.buildings["inn"], 36, 26)  # Was 18, 13
        self._blit_object(self.buildings["blacksmith"], 12, 26)  # Was 6, 13
        self._blit_object(self.buildings["stalls"], 24, 10)  # Was 12, 5

        # Houses - arranged for a cozy residential feel with road access (coordinates doubled)
        self._blit_object(self.buildings["house_1"], 40, 18)  # Was 20, 9
        self._blit_object(self.buildings["house_2"], 32, 18)  # Was 16, 9
        self._blit_object(self.buildings["house_3"], 8, 26)  # Was 4, 13
        self._blit_object(self.buildings["house_4"], 16, 44)  # Was 8, 22
        self._blit_object(self.buildings["house_5"], 16, 18)  # Was 8, 9

        # Well in residential area (coordinates doubled)
        self._blit_object(self.props["well"], 8, 24)  # Was 4, 12

        # Plaza decorations - fountain centerpiece with benches (coordinates doubled)
        self._blit_object(self.props["fountain"], 24, 26)  # Was 12, 13
        self._blit_object(self.props["benches"], 22, 24)  # Was 11, 12
        self._blit_object(self.props["benches"], 26, 28)  # Was 13, 14

        # Additional town decorations - create a lived-in feeling (coordinates doubled)
        self._blit_object(self.barrels["brown"], 38, 24)  # Was 19, 12
        self._blit_object(self.barrels["dark"], 10, 24)  # Was 5, 12
        self._blit_object(self.barrels["red"], 14, 28)  # Was 7, 14
        self._blit_object(self.props["hay_bales"], 18, 42)  # Was 9, 21
        self._blit_object(self.props["hay_bales"], 14, 42)  # Was 7, 21
        self._blit_object(self.props["fences"], 42, 20)  # Was 21, 10
        self._blit_object(self.props["fences"], 6, 20)  # Was 3, 10

        # Flower pots - sprinkled along plaza edges and near buildings (coordinates doubled)
        # Plaza edge decorations
        self._blit_object(self.flower_pots["red"], 20, 22)  # Was 10, 11
        self._blit_object(self.flower_pots["blue"], 28, 22)  # Was 14, 11
        self._blit_object(self.flower_pots["yellow"], 20, 30)  # Was 10, 15
        self._blit_object(self.flower_pots["pink"], 28, 30)  # Was 14, 15
        # Near benches
        self._blit_object(self.flower_pots["purple"], 20, 24)  # Was 10, 12
        self._blit_object(self.flower_pots["red"], 28, 28)  # Was 14, 14
        # Near inn entrance
        self._blit_object(self.flower_pots["blue"], 36, 28)  # Was 18, 14
        self._blit_object(self.flower_pots["yellow"], 34, 28)  # Was 17, 14
        # Near blacksmith entrance
        self._blit_object(self.flower_pots["pink"], 12, 28)  # Was 6, 14
        self._blit_object(self.flower_pots["purple"], 10, 28)  # Was 5, 14
        # Near houses for cozy residential feel
        self._blit_object(self.flower_pots["red"], 40, 20)  # Was 20, 10
        self._blit_object(self.flower_pots["blue"], 32, 20)  # Was 16, 10
        self._blit_object(self.flower_pots["yellow"], 8, 28)  # Was 4, 14
        self._blit_object(self.flower_pots["pink"], 16, 46)  # Was 8, 23

        # Road intersection decorations - signs at key intersections (coordinates doubled)
        # South entrance where road meets the oval loop
        self._blit_object(self.sign_sprite, 26, 38)  # Was 13, 19
        # North intersection where market branch meets the loop
        self._blit_object(self.sign_sprite, 22, 16)  # Was 11, 8
        # West intersection at blacksmith
        self._blit_object(self.sign_sprite, 12, 24)  # Was 6, 12
        # East intersection at housing area
        self._blit_object(self.sign_sprite, 36, 20)  # Was 18, 10

        # NPCs - placed near their workplaces (coordinates doubled)
        self._blit_object(self.npc_sprites["bartender"], 38, 28)  # Was 19, 14
        self._blit_object(self.npc_sprites["miner"], 10, 28)  # Was 5, 14
        self._blit_object(self.npc_sprites["chef"], 24, 14)  # Was 12, 7

        # Trees - frame the town boundaries for a sheltered feel (coordinates doubled)
        tree_positions = [
            # North boundary - dense tree line
            (4, 6, "oak"),  # Was (2, 3)
            (10, 4, "birch"),  # Was (5, 2)
            (16, 6, "oak"),  # Was (8, 3)
            (22, 4, "oak"),  # Was (11, 2)
            (30, 6, "birch"),  # Was (15, 3)
            (36, 4, "oak"),  # Was (18, 2)
            (42, 6, "spruce"),  # Was (21, 3)
            (46, 8, "birch"),  # Was (23, 4)
            # West boundary
            (2, 14, "birch"),  # Was (1, 7)
            (4, 22, "oak"),  # Was (2, 11)
            (2, 30, "birch"),  # Was (1, 15)
            (4, 38, "oak"),  # Was (2, 19)
            (2, 46, "spruce"),  # Was (1, 23)
            # East boundary
            (46, 16, "spruce"),  # Was (23, 8)
            (44, 24, "birch"),  # Was (22, 12)
            (46, 32, "oak"),  # Was (23, 16)
            (44, 40, "spruce"),  # Was (22, 20)
            (46, 48, "birch"),  # Was (23, 24)
            # South boundary - lighter
            (12, 48, "birch"),  # Was (6, 24)
            (36, 48, "spruce"),  # Was (18, 24)
        ]
        for x, y, tree in tree_positions:
            self._blit_object(self.trees[tree], x, y)

    def draw(self, screen: pygame.Surface, offset: pygame.Vector2) -> None:
        screen.blit(self.surface, (-offset.x, -offset.y))
