import pygame
from pathlib import Path

# Initialize pygame
pygame.init()

# Load the tileset
TILE_SIZE = 16
tileset_path = Path(r"c:\Users\lmueller\Desktop\Game Development\Those Who Fight\Those-Who-Fight\Cute_Fantasy\Tiles\Grass\Grass_Tiles_1.png")
tileset = pygame.image.load(tileset_path)

# Create output surface - show the 3x3 grid we're using
output_width = 3 * TILE_SIZE * 4  # 3 tiles wide, 4x scale for visibility
output_height = 3 * TILE_SIZE * 4  # 3 tiles tall, 4x scale
output = pygame.Surface((output_width, output_height))

# Extract and label the 3x3 grid at rows 4-6, columns 0-2
for row in range(3):
    for col in range(3):
        # Extract the tile
        source_rect = pygame.Rect(
            col * TILE_SIZE,  # column * tile_width
            (row + 4) * TILE_SIZE,  # (row + 4) * tile_height (rows 4, 5, 6)
            TILE_SIZE,
            TILE_SIZE
        )
        tile = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        tile.blit(tileset, (0, 0), source_rect)

        # Scale up for visibility
        tile_scaled = pygame.transform.scale(tile, (TILE_SIZE * 4, TILE_SIZE * 4))

        # Blit to output
        output.blit(tile_scaled, (col * TILE_SIZE * 4, row * TILE_SIZE * 4))

        print(f"Tile at grid ({col}, {row}) = tileset ({col}, {row + 4})")

# Save the output
pygame.image.save(output, "debug_3x3_grid.png")
print("\nSaved debug_3x3_grid.png")
print("Grid layout:")
print("  Column 0 | Column 1 | Column 2")
print("  Row 4    | Row 4    | Row 4")
print("  Row 5    | Row 5    | Row 5")
print("  Row 6    | Row 6    | Row 6")
