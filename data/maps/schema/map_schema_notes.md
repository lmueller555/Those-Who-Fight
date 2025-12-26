# TWF Map Schema v1 ("TWF_MAP_V1")

This document describes the JSON schema for TWF maps used by the runtime loader.

## Top-level Map Fields (Required)

| Field | Type | Description |
| --- | --- | --- |
| `format` | string | Must be `"TWF_MAP_V1"`. |
| `name` | string | Human-readable map name. |
| `tile_size` | int | Tile size in pixels. Must match tileset `tile_size`. |
| `width` | int | Map width in tiles. |
| `height` | int | Map height in tiles. |
| `tileset` | string | Tileset id (file name without extension). |
| `layers` | array | Tile layers. Row-major flat arrays, length `width * height`. |
| `entities` | array | Entity list. |

### Layer Object

| Field | Type | Description |
| --- | --- | --- |
| `name` | string | Layer name (e.g., `ground`, `details`, `structures`, `overhead`). |
| `type` | string | Must be `"tile"`. |
| `data` | array[int] | Flat tile id array (row-major). Length = `width * height`. |
| `visible` | bool | Optional. Defaults to `true`. |

### Entity Object

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | Unique entity id. |
| `type` | string | One of `spawn`, `door`, `npc`, `trigger`, `sign`. |
| `x` | int | Tile x coordinate. |
| `y` | int | Tile y coordinate. |
| `w` | int | Optional. Tile width of entity trigger. Defaults to `1`. |
| `h` | int | Optional. Tile height of entity trigger. Defaults to `1`. |
| `props` | object | Type-specific properties. |

### Door Props (Required)

| Field | Type | Description |
| --- | --- | --- |
| `target_map` | string | Map name to load. |
| `target_spawn` | string | Spawn id to place player. |
| `transition` | string | Transition key (e.g., `"fade"`). |
| `locked` | bool | Optional. If `true`, door is locked. |
| `locked_message` | string | Optional. Message when locked. |

### NPC Props (Required)

| Field | Type | Description |
| --- | --- | --- |
| `sprite` | string | Sprite key (data-driven). |
| `facing` | string | `north`, `south`, `east`, `west`. |
| `dialogue_id` | string | Dialogue lookup key. |
| `wander` | object | Optional. See examples. |

### Trigger Props (Required)

| Field | Type | Description |
| --- | --- | --- |
| `on_enter` | object | Action definition (v1 supports message). |

### Sign Props (Required)

| Field | Type | Description |
| --- | --- | --- |
| `text` | string | Message displayed on interact. |

## Examples

### Spawn

```json
{
  "id": "spawn_south_gate",
  "type": "spawn",
  "x": 64,
  "y": 120,
  "props": { "facing": "north" }
}
```

### Door

```json
{
  "id": "door_inn_exterior",
  "type": "door",
  "x": 60,
  "y": 70,
  "w": 2,
  "h": 1,
  "props": {
    "target_map": "Hearthvale_Inn",
    "target_spawn": "spawn_inn_entry",
    "transition": "fade"
  }
}
```

### NPC

```json
{
  "id": "npc_greeter",
  "type": "npc",
  "x": 64,
  "y": 118,
  "props": {
    "sprite": "npc_villager_01",
    "facing": "south",
    "dialogue_id": "town_greeter",
    "wander": {
      "mode": "loop",
      "bounds": { "x": 60, "y": 114, "w": 8, "h": 6 },
      "speed": 1
    }
  }
}
```

### Trigger (message)

```json
{
  "id": "trigger_north_exit_blocked",
  "type": "trigger",
  "x": 64,
  "y": 8,
  "w": 4,
  "h": 1,
  "props": {
    "on_enter": {
      "action": "message",
      "text": "The northern pass is closed by order of the guard captain."
    }
  }
}
```

### Sign

```json
{
  "id": "sign_inn",
  "type": "sign",
  "x": 57,
  "y": 70,
  "props": {
    "text": "Hearthvale Inn - Warm beds and hot stew."
  }
}
```
