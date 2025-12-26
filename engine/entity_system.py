from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class Entity:
    id: str
    type: str
    x: int
    y: int
    w: int = 1
    h: int = 1
    props: Dict = field(default_factory=dict)

    def covers_tile(self, tile_x: int, tile_y: int) -> bool:
        return self.x <= tile_x < self.x + self.w and self.y <= tile_y < self.y + self.h

    @staticmethod
    def from_dict(raw: Dict) -> "Entity":
        return Entity(
            id=raw["id"],
            type=raw["type"],
            x=int(raw["x"]),
            y=int(raw["y"]),
            w=int(raw.get("w", 1)),
            h=int(raw.get("h", 1)),
            props=dict(raw.get("props", {})),
        )


@dataclass
class PlayerState:
    x: int
    y: int
    facing: str = "north"


@dataclass
class InteractionResult:
    message: Optional[str] = None
    transition_map: Optional[str] = None
    transition_spawn: Optional[str] = None
