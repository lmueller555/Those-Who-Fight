from typing import Optional, Tuple

from engine.entity_system import InteractionResult, PlayerState
from engine.map_loader import MapData


FACING_OFFSETS = {
    "north": (0, -1),
    "south": (0, 1),
    "west": (-1, 0),
    "east": (1, 0),
}


def get_facing_tile(player: PlayerState) -> Tuple[int, int]:
    dx, dy = FACING_OFFSETS.get(player.facing, (0, -1))
    return player.x + dx, player.y + dy


def interact(map_data: MapData, player: PlayerState) -> InteractionResult:
    target_x, target_y = get_facing_tile(player)
    entity = map_data.get_entity_at(target_x, target_y, entity_types=["door", "npc", "sign"])
    if not entity:
        return InteractionResult(message=None)

    if entity.type == "door":
        if entity.props.get("locked"):
            return InteractionResult(message=entity.props.get("locked_message", "It's locked."))
        return InteractionResult(
            transition_map=entity.props.get("target_map"),
            transition_spawn=entity.props.get("target_spawn"),
        )
    if entity.type == "npc":
        dialogue_id = entity.props.get("dialogue_id", "...")
        return InteractionResult(message=f"NPC says ({dialogue_id}).")
    if entity.type == "sign":
        return InteractionResult(message=entity.props.get("text", ""))

    return InteractionResult(message=None)


def check_trigger(map_data: MapData, player: PlayerState) -> Optional[InteractionResult]:
    trigger = map_data.get_entity_at(player.x, player.y, entity_types=["trigger"])
    if not trigger:
        return None
    on_enter = trigger.props.get("on_enter", {})
    if on_enter.get("action") == "message":
        return InteractionResult(message=on_enter.get("text", ""))
    return None
