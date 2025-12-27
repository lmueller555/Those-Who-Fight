# Sprite Usage Guidance

This document defines logical placement rules for generating towns and arranging sprites so layouts are readable, believable, and free of collisions.

## General Placement Rules
- **No overlaps:** sprites must not overlap unless explicitly designed to stack (e.g., grass tufts layered on ground). Use collision/occupied tiles to prevent stacking.
- **Tile alignment:** place sprites on the intended grid and respect sprite footprint sizes.
- **Clear walkable space:** maintain readable walkable paths and avoid blocking entrances.
- **Consistent scale:** do not mix sprites of incompatible scale or perspective in the same scene.
- **No floating objects:** every sprite must be supported by valid ground (road, grass, floor, dock, etc.).

## Buildings & Structures
- **Foundations:** buildings must sit on solid ground tiles (grass, dirt, stone) and not on water, cliffs, or roads.
- **Entrances:** every building entrance must connect to a walkable tile (road, path, plaza). Avoid doors opening into water, cliffs, or walls.
- **Spacing:** allow at least 1 tile of clearance around buildings for readability; avoid tight clustering unless intentional (e.g., market stalls).
- **Roofs & shadows:** ensure roofs do not cover interactive tiles unless intended.

## Roads & Paths
- **Connectivity:** roads must connect meaningful points (buildings, plazas, gates, bridges). No dead-end stubs unless it is a deliberate cul‑de‑sac.
- **Continuity:** avoid abrupt terminations or misaligned segments.
- **Width & flow:** maintain consistent width for main roads; secondary paths can be narrower but should still be continuous.
- **Bridges:** when crossing water, place a bridge and align both banks with the road/path.

## NPCs & Creatures
- **Walkable-only placement:** NPCs must be placed on walkable tiles (roads, grass, plazas, docks) and never on water or impassable terrain.
- **Contextual positioning:** keep NPCs near points of interest (doors, markets, plazas) rather than isolated corners.
- **Spacing:** avoid stacking NPCs on the same tile; keep at least 1 tile between idle NPCs unless intentionally grouped.

## Foliage & Plants
- **Ground-appropriate:** trees, shrubs, and plants belong on grass/dirt and not on roads, water, or building interiors.
- **No path blocking:** do not block entrances or narrow paths with foliage.
- **Natural clustering:** avoid perfect grids; group plants with small variations to feel organic.

## Water & Shorelines
- **Water is impassable:** no NPCs or buildings on water tiles unless using docks/boats.
- **Defined edges:** shoreline tiles should form smooth boundaries; avoid jagged single-tile inlets unless intentional.
- **Access points:** docks or bridges should connect land and water clearly; roads should terminate at docks, not in water.

## Props & Decor
- **Purposeful placement:** props should support the scene (e.g., barrels near buildings, benches in plazas).
- **Avoid clutter:** do not place props that block movement or overlap with other interactables.
- **Orientation:** align props to roads or building fronts where applicable.

## Validation Checklist
- No overlapping sprites.
- All entrances connect to walkable tiles.
- Roads connect meaningful destinations.
- NPCs placed only on walkable tiles.
- No foliage or props blocking movement.
- Water boundaries are continuous and crossed only by bridges/docks.
