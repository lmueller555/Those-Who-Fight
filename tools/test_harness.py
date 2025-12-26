import sys
from pathlib import Path

from engine.entity_system import PlayerState
from engine.interactions import check_trigger, interact
from engine.map_loader import MapLoader
from engine.map_renderer import MapRenderer


VIEW_W = 40
VIEW_H = 22


def find_spawn(map_data, spawn_id: str):
    for entity in map_data.entities:
        if entity.type == "spawn" and entity.id == spawn_id:
            return entity
    raise ValueError(f"Spawn '{spawn_id}' not found in map {map_data.name}")


def render(map_data, player: PlayerState):
    renderer = MapRenderer(map_data)
    view_x = max(0, min(map_data.width - VIEW_W, player.x - VIEW_W // 2))
    view_y = max(0, min(map_data.height - VIEW_H, player.y - VIEW_H // 2))
    rows = renderer.render_ascii(view_x, view_y, VIEW_W, VIEW_H)

    overlay = [list(row) for row in rows]
    for entity in map_data.entities:
        ex, ey = entity.x - view_x, entity.y - view_y
        if 0 <= ex < VIEW_W and 0 <= ey < VIEW_H:
            if entity.type == "npc":
                overlay[ey][ex] = "N"
            elif entity.type == "door":
                overlay[ey][ex] = "D"
            elif entity.type == "sign":
                overlay[ey][ex] = "S"
    px, py = player.x - view_x, player.y - view_y
    if 0 <= px < VIEW_W and 0 <= py < VIEW_H:
        overlay[py][px] = "@"
    print("\n".join("".join(row) for row in overlay))
    print(f"Map: {map_data.name} | Position: ({player.x}, {player.y}) Facing: {player.facing}")


def main():
    root = Path(__file__).resolve().parents[1]
    loader = MapLoader(root)
    current_map = loader.load_map("Hearthvale_Town")
    spawn = find_spawn(current_map, "spawn_south_gate")
    player = PlayerState(x=spawn.x, y=spawn.y, facing=spawn.props.get("facing", "north"))

    print("Controls: WASD move, E interact, Q quit.")
    while True:
        render(current_map, player)
        command = input("> ").strip().lower()
        if command == "q":
            break
        if command in {"w", "a", "s", "d"}:
            dx, dy = 0, 0
            if command == "w":
                player.facing = "north"
                dy = -1
            elif command == "s":
                player.facing = "south"
                dy = 1
            elif command == "a":
                player.facing = "west"
                dx = -1
            elif command == "d":
                player.facing = "east"
                dx = 1
            new_x = player.x + dx
            new_y = player.y + dy
            if not current_map.is_solid(new_x, new_y):
                player.x = new_x
                player.y = new_y
                trigger_result = check_trigger(current_map, player)
                if trigger_result and trigger_result.message:
                    print(trigger_result.message)
            else:
                print("Bump! That's solid.")
        elif command == "e":
            result = interact(current_map, player)
            if result.message:
                print(result.message)
            if result.transition_map:
                current_map = loader.load_map(result.transition_map)
                spawn = find_spawn(current_map, result.transition_spawn)
                player.x = spawn.x
                player.y = spawn.y
                player.facing = spawn.props.get("facing", "south")
        else:
            print("Unknown command.")


if __name__ == "__main__":
    sys.exit(main())
