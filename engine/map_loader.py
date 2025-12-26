import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from engine.entity_system import Entity


@dataclass
class TilesetTile:
    tile_id: int
    name: str
    solid: bool
    glyph: str
    tags: List[str]
    atlas_image: Optional[str] = None
    uv: Optional[Tuple[int, int]] = None
    sprite_key: Optional[str] = None


@dataclass(frozen=True)
class TileSprite:
    atlas_image: Optional[str]
    uv: Optional[Tuple[int, int]]
    sprite_key: Optional[str]


@dataclass
class Tileset:
    tileset_id: str
    tile_size: int
    tiles: Dict[int, TilesetTile]

    def is_solid(self, tile_id: int) -> bool:
        tile = self.tiles.get(tile_id)
        if tile is None:
            return False
        return tile.solid

    def glyph(self, tile_id: int) -> str:
        tile = self.tiles.get(tile_id)
        if tile is None:
            return "?"
        return tile.glyph

    def sprite(self, tile_id: int) -> TileSprite:
        tile = self.tiles.get(tile_id)
        if tile is None:
            return TileSprite(atlas_image=None, uv=None, sprite_key=None)
        return TileSprite(
            atlas_image=tile.atlas_image,
            uv=tile.uv,
            sprite_key=tile.sprite_key,
        )


@dataclass
class TileLayer:
    name: str
    data: List[int]
    visible: bool = True


@dataclass
class MapData:
    name: str
    width: int
    height: int
    tile_size: int
    tileset: Tileset
    layers: Dict[str, TileLayer]
    entities: List[Entity]

    def index(self, x: int, y: int) -> int:
        return y * self.width + x

    def get_tile(self, layer_name: str, x: int, y: int) -> int:
        layer = self.layers.get(layer_name)
        if layer is None:
            raise KeyError(f"Unknown layer '{layer_name}'")
        if not (0 <= x < self.width and 0 <= y < self.height):
            return 0
        return layer.data[self.index(x, y)]

    def is_solid(self, x: int, y: int) -> bool:
        if not (0 <= x < self.width and 0 <= y < self.height):
            return True
        collision_layer = self.layers.get("collision")
        if collision_layer:
            return collision_layer.data[self.index(x, y)] != 0
        for layer in self.layers.values():
            tile_id = layer.data[self.index(x, y)]
            if tile_id != 0 and self.tileset.is_solid(tile_id):
                return True
        return False

    def get_entities_by_type(self, entity_type: str) -> List[Entity]:
        return [entity for entity in self.entities if entity.type == entity_type]

    def get_entity_at(self, x: int, y: int, entity_types: Optional[List[str]] = None) -> Optional[Entity]:
        for entity in self.entities:
            if entity_types and entity.type not in entity_types:
                continue
            if entity.covers_tile(x, y):
                return entity
        return None


class MapLoader:
    REQUIRED_FIELDS = {"format", "name", "tile_size", "width", "height", "tileset", "layers", "entities"}

    def __init__(self, root: Path):
        self.root = root

    def load_tileset(self, tileset_id: str) -> Tileset:
        tileset_path = self.root / "data" / "tilesets" / f"{tileset_id}.json"
        data = json.loads(tileset_path.read_text())
        tile_size = int(data["tile_size"])
        tiles = {}
        tiles_data = data["tiles"]
        if isinstance(tiles_data, dict):
            tile_items = tiles_data.items()
        else:
            tile_items = [(tile["id"], tile) for tile in tiles_data]
        for tile_id_raw, tile in tile_items:
            tile_id = int(tile_id_raw)
            uv = tile.get("uv")
            if uv is not None:
                uv = (int(uv[0]), int(uv[1]))
            tile_name = tile.get("name") or tile.get("key") or f"tile_{tile_id}"
            tiles[tile_id] = TilesetTile(
                tile_id=tile_id,
                name=tile_name,
                solid=bool(tile.get("solid", False)),
                glyph=tile.get("glyph", "?"),
                tags=list(tile.get("tags", [])),
                atlas_image=tile.get("atlas_image"),
                uv=uv,
                sprite_key=tile.get("sprite_key"),
            )
        return Tileset(tileset_id=tileset_id, tile_size=tile_size, tiles=tiles)

    def load_map(self, map_name: str) -> MapData:
        map_path = self.root / "data" / "maps" / f"{map_name}.json"
        if not map_path.exists():
            raise FileNotFoundError(f"Map file not found: {map_path}")
        data = json.loads(map_path.read_text())
        missing = self.REQUIRED_FIELDS - data.keys()
        if missing:
            raise ValueError(f"Map missing required fields: {sorted(missing)}")
        if data["format"] != "TWF_MAP_V1":
            raise ValueError(f"Unsupported map format: {data['format']}")

        width = int(data["width"])
        height = int(data["height"])
        tileset = self.load_tileset(data["tileset"])
        if int(data["tile_size"]) != tileset.tile_size:
            raise ValueError("Map tile_size does not match tileset tile_size")

        layers = {}
        for layer in data["layers"]:
            if layer.get("type") != "tile":
                raise ValueError(f"Unsupported layer type: {layer.get('type')}")
            layer_name = layer.get("name")
            if not layer_name:
                raise ValueError("Layer missing name")
            layer_data = list(layer.get("data", []))
            expected_len = width * height
            if len(layer_data) != expected_len:
                raise ValueError(
                    f"Layer '{layer_name}' has length {len(layer_data)}; expected {expected_len}"
                )
            layers[layer_name] = TileLayer(
                name=layer_name,
                data=layer_data,
                visible=bool(layer.get("visible", True)),
            )

        entities = []
        entity_ids = set()
        for entity in data["entities"]:
            entity_id = entity.get("id")
            if not entity_id:
                raise ValueError("Entity missing id")
            if entity_id in entity_ids:
                raise ValueError(f"Duplicate entity id: {entity_id}")
            entity_ids.add(entity_id)
            entities.append(Entity.from_dict(entity))

        return MapData(
            name=data["name"],
            width=width,
            height=height,
            tile_size=int(data["tile_size"]),
            tileset=tileset,
            layers=layers,
            entities=entities,
        )
