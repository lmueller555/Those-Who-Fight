import json
from pathlib import Path

TILESET = "overworld_tileset_v1"
TILE_SIZE = 16

TILES = {
    "empty": 0,
    "grass": 1,
    "road": 2,
    "dirt": 3,
    "water": 4,
    "fence": 5,
    "wall": 6,
    "roof": 7,
    "door": 8,
    "path_edge": 9,
    "plaza": 10,
    "flower": 11,
    "tree_trunk": 12,
    "tree_canopy": 13,
    "bridge": 14,
    "statue": 15,
    "grass_variant": 16,
    "interior_floor": 20,
    "interior_wall": 21,
    "interior_rug": 22,
    "cathedral_wall": 23,
    "cathedral_roof": 24,
    "cathedral_steps": 25,
}


def blank_layer(width, height, fill):
    return [fill] * (width * height)


def index(width, x, y):
    return y * width + x


def fill_rect(layer, width, x, y, w, h, tile_id):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            layer[index(width, xx, yy)] = tile_id


def outline_rect(layer, width, x, y, w, h, tile_id):
    for xx in range(x, x + w):
        layer[index(width, xx, y)] = tile_id
        layer[index(width, xx, y + h - 1)] = tile_id
    for yy in range(y, y + h):
        layer[index(width, x, yy)] = tile_id
        layer[index(width, x + w - 1, yy)] = tile_id


def place_building(layers, width, x, y, w, h, door_x, wall_tile=None, roof_tile=None):
    structures = layers["structures"]
    overhead = layers["overhead"]
    wall_tile = wall_tile or TILES["wall"]
    roof_tile = roof_tile or TILES["roof"]
    outline_rect(structures, width, x, y, w, h, wall_tile)
    fill_rect(overhead, width, x, y, w, h, roof_tile)
    structures[index(width, door_x, y + h - 1)] = TILES["door"]


def add_tree(layers, width, x, y):
    layers["structures"][index(width, x, y)] = TILES["tree_trunk"]
    layers["overhead"][index(width, x, y - 1)] = TILES["tree_canopy"]


def generate_town():
    width = height = 128
    layers = {
        "ground": blank_layer(width, height, TILES["grass"]),
        "details": blank_layer(width, height, TILES["empty"]),
        "structures": blank_layer(width, height, TILES["empty"]),
        "overhead": blank_layer(width, height, TILES["empty"]),
    }

    road_x = width // 2 - 2
    plaza_x, plaza_y = 54, 62
    plaza_w, plaza_h = 20, 20
    fill_rect(layers["ground"], width, plaza_x, plaza_y, plaza_w, plaza_h, TILES["plaza"])
    fill_rect(layers["ground"], width, road_x, plaza_y + plaza_h, 4, height - (plaza_y + plaza_h), TILES["road"])

    fountain_x, fountain_y = width // 2 - 2, plaza_y + 4
    fill_rect(layers["details"], width, fountain_x, fountain_y, 4, 4, TILES["water"])

    inn = (36, 52, 16, 12)
    place_building(layers, width, *inn, door_x=inn[0] + inn[2] // 2)

    item_shop = (24, 68, 10, 8)
    place_building(layers, width, *item_shop, door_x=item_shop[0] + item_shop[2] // 2)

    weapon_shop = (94, 68, 10, 8)
    place_building(layers, width, *weapon_shop, door_x=weapon_shop[0] + weapon_shop[2] // 2)

    cathedral = (50, 28, 28, 20)
    place_building(
        layers,
        width,
        *cathedral,
        door_x=cathedral[0] + cathedral[2] // 2,
        wall_tile=TILES["cathedral_wall"],
        roof_tile=TILES["cathedral_roof"],
    )

    fence_x = cathedral[0] - 3
    fence_y = cathedral[1] - 3
    fence_w = cathedral[2] + 6
    fence_h = cathedral[3] + 10
    outline_rect(layers["structures"], width, fence_x, fence_y, fence_w, fence_h, TILES["fence"])
    gate_x = cathedral[0] + cathedral[2] // 2
    layers["structures"][index(width, gate_x, fence_y + fence_h - 1)] = TILES["empty"]
    layers["structures"][index(width, gate_x + 1, fence_y + fence_h - 1)] = TILES["empty"]
    steps_y = cathedral[1] + cathedral[3]
    fill_rect(layers["details"], width, gate_x - 1, steps_y, 4, 2, TILES["cathedral_steps"])
    fill_rect(layers["ground"], width, road_x, fence_y + fence_h, 4, plaza_y - (fence_y + fence_h), TILES["road"])
    layers["structures"][index(width, cathedral[0] + 3, cathedral[1] + cathedral[3] + 1)] = TILES["statue"]
    layers["structures"][index(width, cathedral[0] + cathedral[2] - 4, cathedral[1] + cathedral[3] + 1)] = TILES["statue"]

    houses = [
        (8, 20, 8, 6),
        (104, 20, 8, 6),
        (8, 48, 8, 6),
        (104, 48, 8, 6),
        (8, 88, 8, 6),
        (104, 88, 8, 6),
    ]
    for house in houses:
        place_building(layers, width, *house, door_x=house[0] + house[2] // 2)

    for x in range(20, 108, 8):
        add_tree(layers, width, x, 110)
    for x in range(20, 108, 10):
        add_tree(layers, width, x, 18)

    for x, y in [(50, 78), (72, 78), (30, 72), (98, 72)]:
        layers["details"][index(width, x, y)] = TILES["flower"]

    entities = [
        {
            "id": "spawn_south_gate",
            "type": "spawn",
            "x": width // 2,
            "y": 120,
            "props": {"facing": "north"},
        },
        {
            "id": "door_inn_exterior",
            "type": "door",
            "x": inn[0] + inn[2] // 2,
            "y": inn[1] + inn[3] - 1,
            "props": {"target_map": "Hearthvale_Inn", "target_spawn": "spawn_inn_entry", "transition": "fade"},
        },
        {
            "id": "door_item_shop_exterior",
            "type": "door",
            "x": item_shop[0] + item_shop[2] // 2,
            "y": item_shop[1] + item_shop[3] - 1,
            "props": {"target_map": "Hearthvale_ItemShop", "target_spawn": "spawn_itemshop_entry", "transition": "fade"},
        },
        {
            "id": "door_weapon_shop_exterior",
            "type": "door",
            "x": weapon_shop[0] + weapon_shop[2] // 2,
            "y": weapon_shop[1] + weapon_shop[3] - 1,
            "props": {"target_map": "Hearthvale_WeaponShop", "target_spawn": "spawn_weaponshop_entry", "transition": "fade"},
        },
        {
            "id": "door_cathedral_exterior",
            "type": "door",
            "x": cathedral[0] + cathedral[2] // 2,
            "y": cathedral[1] + cathedral[3] - 1,
            "w": 2,
            "props": {"target_map": "Hearthvale_Cathedral", "target_spawn": "spawn_cathedral_entry", "transition": "fade"},
        },
        {
            "id": "spawn_inn_exit",
            "type": "spawn",
            "x": inn[0] + inn[2] // 2,
            "y": inn[1] + inn[3],
            "props": {"facing": "south"},
        },
        {
            "id": "spawn_itemshop_exit",
            "type": "spawn",
            "x": item_shop[0] + item_shop[2] // 2,
            "y": item_shop[1] + item_shop[3],
            "props": {"facing": "south"},
        },
        {
            "id": "spawn_weaponshop_exit",
            "type": "spawn",
            "x": weapon_shop[0] + weapon_shop[2] // 2,
            "y": weapon_shop[1] + weapon_shop[3],
            "props": {"facing": "south"},
        },
        {
            "id": "spawn_cathedral_exit",
            "type": "spawn",
            "x": cathedral[0] + cathedral[2] // 2,
            "y": cathedral[1] + cathedral[3],
            "props": {"facing": "south"},
        },
    ]

    for idx, house in enumerate(houses, start=1):
        entities.append(
            {
                "id": f"door_house_{idx:02d}",
                "type": "door",
                "x": house[0] + house[2] // 2,
                "y": house[1] + house[3] - 1,
                "props": {
                    "target_map": f"Hearthvale_House_{idx:02d}",
                    "target_spawn": "spawn_house_entry",
                    "transition": "fade",
                },
            }
        )
        entities.append(
            {
                "id": f"spawn_house_{idx:02d}_exit",
                "type": "spawn",
                "x": house[0] + house[2] // 2,
                "y": house[1] + house[3],
                "props": {"facing": "south"},
            }
        )

    entities += [
        {
            "id": "sign_inn",
            "type": "sign",
            "x": inn[0] - 2,
            "y": inn[1] + inn[3] - 1,
            "props": {"text": "Hearthvale Inn - Warm beds and hot stew."},
        },
        {
            "id": "npc_greeter",
            "type": "npc",
            "x": width // 2,
            "y": 118,
            "props": {"sprite": "npc_villager_01", "facing": "south", "dialogue_id": "town_greeter"},
        },
        {
            "id": "npc_guard_north",
            "type": "npc",
            "x": width // 2,
            "y": 14,
            "props": {"sprite": "npc_guard_01", "facing": "south", "dialogue_id": "north_gate_guard"},
        },
        {
            "id": "npc_cathedral_attendant",
            "type": "npc",
            "x": cathedral[0] + cathedral[2] // 2 - 2,
            "y": cathedral[1] + cathedral[3] + 2,
            "props": {"sprite": "npc_cleric_01", "facing": "south", "dialogue_id": "cathedral_attendant"},
        },
        {
            "id": "npc_wanderer_01",
            "type": "npc",
            "x": 60,
            "y": 90,
            "props": {
                "sprite": "npc_villager_02",
                "facing": "east",
                "dialogue_id": "wanderer_one",
                "wander": {"mode": "loop", "bounds": {"x": 56, "y": 86, "w": 10, "h": 8}, "speed": 1},
            },
        },
        {
            "id": "npc_wanderer_02",
            "type": "npc",
            "x": 70,
            "y": 90,
            "props": {
                "sprite": "npc_villager_03",
                "facing": "west",
                "dialogue_id": "wanderer_two",
                "wander": {"mode": "loop", "bounds": {"x": 68, "y": 86, "w": 10, "h": 8}, "speed": 1},
            },
        },
        {
            "id": "npc_innkeeper_outside",
            "type": "npc",
            "x": inn[0] + inn[2] - 2,
            "y": inn[1] + inn[3] + 1,
            "props": {"sprite": "npc_innkeeper_01", "facing": "south", "dialogue_id": "innkeeper_greeting"},
        },
        {
            "id": "npc_item_shop",
            "type": "npc",
            "x": item_shop[0] + 2,
            "y": item_shop[1] + item_shop[3] + 1,
            "props": {"sprite": "npc_merchant_01", "facing": "south", "dialogue_id": "item_shop_pitch"},
        },
        {
            "id": "npc_weapon_shop",
            "type": "npc",
            "x": weapon_shop[0] + weapon_shop[2] - 2,
            "y": weapon_shop[1] + weapon_shop[3] + 1,
            "props": {"sprite": "npc_blacksmith_01", "facing": "south", "dialogue_id": "weapon_shop_pitch"},
        },
        {
            "id": "npc_house_neighbor_01",
            "type": "npc",
            "x": houses[0][0] + 3,
            "y": houses[0][1] + houses[0][3] + 1,
            "props": {"sprite": "npc_villager_04", "facing": "south", "dialogue_id": "neighbor_chat"},
        },
        {
            "id": "npc_house_neighbor_02",
            "type": "npc",
            "x": houses[3][0] + 3,
            "y": houses[3][1] + houses[3][3] + 1,
            "props": {"sprite": "npc_villager_05", "facing": "south", "dialogue_id": "neighbor_chat_2"},
        },
        {
            "id": "npc_plaza_kid",
            "type": "npc",
            "x": plaza_x + 3,
            "y": plaza_y + 6,
            "props": {"sprite": "npc_child_01", "facing": "west", "dialogue_id": "plaza_kid"},
        },
    ]

    entities.append(
        {
            "id": "trigger_north_exit_blocked",
            "type": "trigger",
            "x": width // 2 - 2,
            "y": 10,
            "w": 4,
            "h": 1,
            "props": {
                "on_enter": {
                    "action": "message",
                    "text": "The northern pass is closed for now. The guard shakes his head.",
                }
            },
        }
    )

    return {
        "format": "TWF_MAP_V1",
        "name": "Hearthvale_Town",
        "tile_size": TILE_SIZE,
        "width": width,
        "height": height,
        "tileset": TILESET,
        "layers": [
            {"name": "ground", "type": "tile", "data": layers["ground"]},
            {"name": "details", "type": "tile", "data": layers["details"]},
            {"name": "structures", "type": "tile", "data": layers["structures"]},
            {"name": "overhead", "type": "tile", "data": layers["overhead"]},
        ],
        "entities": entities,
    }


def generate_interior(
    name,
    width=24,
    height=18,
    npc_id="npc_interior",
    spawn_id=None,
    return_map="Hearthvale_Town",
    return_spawn="spawn_south_gate",
):
    layers = {
        "ground": blank_layer(width, height, TILES["interior_floor"]),
        "details": blank_layer(width, height, TILES["empty"]),
        "structures": blank_layer(width, height, TILES["empty"]),
        "overhead": blank_layer(width, height, TILES["empty"]),
    }
    outline_rect(layers["structures"], width, 0, 0, width, height, TILES["interior_wall"])
    door_x = width // 2
    layers["structures"][index(width, door_x, height - 1)] = TILES["door"]
    fill_rect(layers["details"], width, 5, 4, 6, 3, TILES["interior_rug"])

    spawn_key = spawn_id or f"spawn_{name.lower()}_entry"
    entities = [
        {
            "id": spawn_key,
            "type": "spawn",
            "x": width // 2,
            "y": height - 2,
            "props": {"facing": "north"},
        },
        {
            "id": f"{npc_id}",
            "type": "npc",
            "x": width // 2,
            "y": 4,
            "props": {"sprite": "npc_interior_01", "facing": "south", "dialogue_id": f"{name.lower()}_greeting"},
        },
        {
            "id": f"door_exit_{name.lower()}",
            "type": "door",
            "x": door_x,
            "y": height - 1,
            "props": {"target_map": return_map, "target_spawn": return_spawn, "transition": "fade"},
        },
    ]

    return {
        "format": "TWF_MAP_V1",
        "name": name,
        "tile_size": TILE_SIZE,
        "width": width,
        "height": height,
        "tileset": TILESET,
        "layers": [
            {"name": "ground", "type": "tile", "data": layers["ground"]},
            {"name": "details", "type": "tile", "data": layers["details"]},
            {"name": "structures", "type": "tile", "data": layers["structures"]},
            {"name": "overhead", "type": "tile", "data": layers["overhead"]},
        ],
        "entities": entities,
    }


def main():
    root = Path(__file__).resolve().parents[1]
    maps_dir = root / "data" / "maps"
    maps_dir.mkdir(parents=True, exist_ok=True)

    town = generate_town()
    (maps_dir / "Hearthvale_Town.json").write_text(json.dumps(town, indent=2))

    interiors = [
        ("Hearthvale_Inn", "spawn_inn_entry", "spawn_inn_exit"),
        ("Hearthvale_ItemShop", "spawn_itemshop_entry", "spawn_itemshop_exit"),
        ("Hearthvale_WeaponShop", "spawn_weaponshop_entry", "spawn_weaponshop_exit"),
        ("Hearthvale_Cathedral", "spawn_cathedral_entry", "spawn_cathedral_exit"),
    ]
    for name, spawn_id, return_spawn in interiors:
        interior = generate_interior(name, spawn_id=spawn_id, return_spawn=return_spawn)
        (maps_dir / f"{name}.json").write_text(json.dumps(interior, indent=2))

    for idx in range(1, 7):
        name = f"Hearthvale_House_{idx:02d}"
        interior = generate_interior(
            name,
            width=20,
            height=14,
            npc_id=f"npc_house_{idx:02d}",
            spawn_id="spawn_house_entry",
            return_spawn=f"spawn_house_{idx:02d}_exit",
        )
        (maps_dir / f"{name}.json").write_text(json.dumps(interior, indent=2))


if __name__ == "__main__":
    main()
