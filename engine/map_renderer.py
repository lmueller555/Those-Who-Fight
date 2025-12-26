from dataclasses import dataclass
from typing import List, Optional, Tuple

from engine.map_loader import MapData


@dataclass(frozen=True)
class TileRenderCommand:
    tile_id: int
    layer: str
    x: int
    y: int
    sprite_key: Optional[str]
    atlas_image: Optional[str]
    source_rect: Optional[Tuple[int, int, int, int]]


class MapRenderer:
    LAYER_ORDER = ("ground", "details", "structures", "overhead")

    def __init__(self, map_data: MapData):
        self.map = map_data

    def composite_tile(self, x: int, y: int, include_overhead: bool = True) -> int:
        tile_id = 0
        for layer_name in self.LAYER_ORDER:
            if not include_overhead and layer_name == "overhead":
                continue
            layer = self.map.layers.get(layer_name)
            if not layer or not layer.visible:
                continue
            candidate = layer.data[self.map.index(x, y)]
            if candidate != 0:
                tile_id = candidate
        return tile_id

    def render_ascii(self, view_x: int, view_y: int, view_w: int, view_h: int, include_overhead: bool = True) -> List[str]:
        rows = []
        for y in range(view_y, view_y + view_h):
            row_chars = []
            for x in range(view_x, view_x + view_w):
                if not (0 <= x < self.map.width and 0 <= y < self.map.height):
                    row_chars.append(" ")
                    continue
                tile_id = self.composite_tile(x, y, include_overhead=include_overhead)
                row_chars.append(self.map.tileset.glyph(tile_id))
            rows.append("".join(row_chars))
        return rows

    def render_tiles(self, view_x: int, view_y: int, view_w: int, view_h: int, include_overhead: bool = True) -> List[TileRenderCommand]:
        commands: List[TileRenderCommand] = []
        tile_size = self.map.tile_size
        for layer_name in self.LAYER_ORDER:
            if not include_overhead and layer_name == "overhead":
                continue
            layer = self.map.layers.get(layer_name)
            if not layer or not layer.visible:
                continue
            for y in range(view_y, view_y + view_h):
                if not (0 <= y < self.map.height):
                    continue
                for x in range(view_x, view_x + view_w):
                    if not (0 <= x < self.map.width):
                        continue
                    tile_id = layer.data[self.map.index(x, y)]
                    if tile_id == 0:
                        continue
                    sprite = self.map.tileset.sprite(tile_id)
                    source_rect = None
                    if sprite.atlas_image and sprite.uv:
                        source_rect = (
                            sprite.uv[0] * tile_size,
                            sprite.uv[1] * tile_size,
                            tile_size,
                            tile_size,
                        )
                    commands.append(
                        TileRenderCommand(
                            tile_id=tile_id,
                            layer=layer_name,
                            x=x * tile_size,
                            y=y * tile_size,
                            sprite_key=sprite.sprite_key,
                            atlas_image=sprite.atlas_image,
                            source_rect=source_rect,
                        )
                    )
        return commands
