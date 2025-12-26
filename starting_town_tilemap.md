# Starting Town Tilemap (Cute_Fantasy)

## Map footprint & structure
- **Overall size:** ~1 screen wide by ~1.5 screens tall (top-down), compact and walkable.
- **Orientation:** north at top, entrance at south edge.
- **Layering order:** ground (grass/farmland/roads) → water/bridge → buildings → props/decor → NPCs.

## Sprite sources used (exact filenames)
### Ground & layout
- Grass base: `Cute_Fantasy/Tiles/Grass/Grass_Tiles_1.png`, `Cute_Fantasy/Tiles/Grass/Grass_Tiles_2.png`
- Road loop + branch paths: `Cute_Fantasy/Tiles/Cobble_Road/Cobble_Road_1.png`, `Cute_Fantasy/Tiles/Cobble_Road/Cobble_Road_2.png`
- Farmland: `Cute_Fantasy/Tiles/FarmLand/FarmLand_Tile.png`

### Water & bridge
- Pond/river water: `Cute_Fantasy/Tiles/Water/Water_Tile_1.png`, `Cute_Fantasy/Tiles/Water/Water_Middle.png`
- Bridge: `Cute_Fantasy/Tiles/Bridge/Bridge_Stone_Horizontal.png`

### Buildings
- Wooden houses (mix variants):
  - `Cute_Fantasy/Buildings/Buildings/Houses/Wood/House_1_Wood_Base_Red.png`
  - `Cute_Fantasy/Buildings/Buildings/Houses/Wood/House_2_Wood_Green_Blue.png`
  - `Cute_Fantasy/Buildings/Buildings/Houses/Wood/House_3_Wood_Red_Black.png`
  - `Cute_Fantasy/Buildings/Buildings/Houses/Wood/House_4_Wood_Base_Blue.png`
  - `Cute_Fantasy/Buildings/Buildings/Houses/Wood/House_5_Wood_Green_Red.png`
- Inn: `Cute_Fantasy/Buildings/Buildings/Unique_Buildings/Inn/Inn_Blue.png`
- Blacksmith: `Cute_Fantasy/Buildings/Buildings/Unique_Buildings/Blacksmith_House/Blacksmith_House_Red.png`
- Barn: `Cute_Fantasy/Buildings/Buildings/Unique_Buildings/Barn/Barn_Base_Red.png`
- Silo: `Cute_Fantasy/Buildings/Buildings/Unique_Buildings/Silo/Silo.png`
- Windmill: `Cute_Fantasy/Buildings/Buildings/Unique_Buildings/Windmill/Windmill.png`
- Market stalls: `Cute_Fantasy/Buildings/Buildings/Unique_Buildings/Stalls/Market_Stalls.png`

### Plaza props & town decor
- Fountain: `Cute_Fantasy/Outdoor decoration/Fountain.png`
- Benches: `Cute_Fantasy/Outdoor decoration/Benches.png`
- Lantern posts: `Cute_Fantasy/Outdoor decoration/Lanter_Posts.png`
- Flowers: `Cute_Fantasy/Outdoor decoration/Flowers.png`
- Barrels: `Cute_Fantasy/Outdoor decoration/barrels.png`
- Well: `Cute_Fantasy/Outdoor decoration/Well.png`
- Signs: `Cute_Fantasy/Outdoor decoration/Signs.png`
- Fences: `Cute_Fantasy/Outdoor decoration/Fences.png`, `Cute_Fantasy/Outdoor decoration/Fence_Big.png`, `Cute_Fantasy/Outdoor decoration/White_Fence.png`
- Picnic area: `Cute_Fantasy/Outdoor decoration/Picnic_Basket.png`, `Cute_Fantasy/Tiles/Picnic_Blankets.png`

### Farm props
- Crops: `Cute_Fantasy/Crops/Crops.png`, `Cute_Fantasy/Crops/Crops_2.png`
- Water trough: `Cute_Fantasy/Outdoor decoration/Water_Troughs.png`
- Hay bales: `Cute_Fantasy/Outdoor decoration/Hay_Bales.png`
- Scarecrow: `Cute_Fantasy/Outdoor decoration/Scarecrows.png`

### Nature & boundaries
- Trees: `Cute_Fantasy/Trees/Big_Oak_Tree.png`, `Cute_Fantasy/Trees/Medium_Birch_Tree.png`, `Cute_Fantasy/Trees/Small_Spruce_Tree.png`

### NPCs
- Farmer: `Cute_Fantasy/NPCs (Premade)/Farmer_Bob.png`
- Fisher: `Cute_Fantasy/NPCs (Premade)/Fisherman_Fin.png`
- Bartender: `Cute_Fantasy/NPCs (Premade)/Bartender_Bruno.png`
- Miner: `Cute_Fantasy/NPCs (Premade)/Miner_Mike.png`
- Chef: `Cute_Fantasy/NPCs (Premade)/Chef_Chloe.png`

## Top-down map description (layout)
### South entrance & main road loop
- **Entrance** sits centered on the **south edge**. The main **cobble road** comes in from the south, heads north to the **central plaza**, then loops east and west around it before returning south, creating a tidy oval.
- **Short branch paths** (cobble) split from the loop to each key building and to the farm area.

### Central plaza (town heart)
- The **plaza** is just north of the town center, a widened cobble square.
- **Fountain** placed in the exact center of the plaza.
- **Benches** on the north and south edges of the plaza, facing the fountain.
- **Lantern posts** at the four corners of the plaza for symmetry.
- **Flowers** sprinkled along the plaza edges and near benches.
- **Barrels** clustered at the east side of the plaza for light activity.

### Buildings along the main loop
- **Inn** on the **east side** of the loop, just southeast of the plaza, entrance facing west toward the road. **Sign** placed by its entrance.
- **Blacksmith** on the **west side** of the loop, slightly southwest of the plaza, entrance facing east. **Sign** placed by its entrance.
- **Market stalls** placed **north of the plaza** on a small cobble pad, facing south so players approach from the loop.
- **Wooden houses** (5 total) arranged:
  - Two on the **northeast** side of the loop near the market.
  - Two on the **northwest** side of the loop near the blacksmith.
  - One on the **southwest** side of the loop near the entrance.
  - All house doors face the cobble road.
- **Well** placed between the northwest houses to create a cozy residential cluster.

### Farm area (southeast)
- **Barn + Silo** placed on the **southeast** edge of the loop with entrances facing the road.
- A **farm plot** just south/east of the barn using **farmland tiles**, with **rows of crops** from both crop sheets.
- **Water trough** and **hay bales** placed beside the barn.
- **Scarecrow** positioned at the far edge of the farm plot.
- **Fence lines** (wood/white) define the farm boundary and guide player movement to the barn path.

### Windmill & water feature
- **Windmill** on the **northeast edge** of town, outside the loop but connected by a short cobble spur; entrance faces the road.
- A **small pond** on the **east side** of town, just south of the windmill spur, with a **stone bridge** crossing a narrow outlet so the road can pass over it.

### Nature, boundaries, and cozy details
- **Trees** (big oak, medium birch, small spruce) frame the town boundary on all sides, denser on the north and west to feel sheltered.
- **Fences** outline house yards and mark the edge of the central plaza’s green.
- **Picnic area** (blanket + basket) on a grassy patch **northwest of the plaza** near the residential cluster.

### NPC placement (5–7 total)
- **Farmer Bob** near the farm plot by the barn.
- **Fisherman Fin** near the pond’s south bank.
- **Bartender Bruno** just outside the inn entrance.
- **Miner Mike** near the blacksmith entrance.
- **Chef Chloe** near the market stalls.
- (Optional) One extra **townsperson** from the NPC set can wander near the plaza if desired.
