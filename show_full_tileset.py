import pygame
from pathlib import Path

pygame.init()

# Load the full tileset
tileset_path = Path(r"c:\Users\lmueller\Desktop\Game Development\Those Who Fight\Those-Who-Fight\Cute_Fantasy\Tiles\Grass\Grass_Tiles_1.png")
tileset = pygame.image.load(tileset_path)

# Get dimensions
width, height = tileset.get_size()
print(f"Tileset size: {width}x{height}")
print(f"At 16x16 tiles: {width//16} columns x {height//16} rows")

# Scale up 4x for visibility and save
scaled = pygame.transform.scale(tileset, (width * 4, height * 4))
pygame.image.save(scaled, "full_tileset_scaled.png")
print("Saved full_tileset_scaled.png")

# Also create a grid overlay version showing row and column numbers
TILE_SIZE = 16
cols = width // TILE_SIZE
rows = height // TILE_SIZE

# Create a version with grid lines
grid_surface = scaled.copy()
font = pygame.font.Font(None, 20)

# Draw grid lines and labels
for row in range(rows + 1):
    y = row * TILE_SIZE * 4
    pygame.draw.line(grid_surface, (255, 0, 0), (0, y), (width * 4, y), 2)

for col in range(cols + 1):
    x = col * TILE_SIZE * 4
    pygame.draw.line(grid_surface, (255, 0, 0), (x, 0), (x, height * 4), 2)

# Add row and column numbers
for row in range(rows):
    text = font.render(f"R{row}", True, (255, 255, 0))
    grid_surface.blit(text, (5, row * TILE_SIZE * 4 + 5))

for col in range(cols):
    text = font.render(f"C{col}", True, (255, 255, 0))
    grid_surface.blit(text, (col * TILE_SIZE * 4 + 5, 5))

pygame.image.save(grid_surface, "full_tileset_grid.png")
print("Saved full_tileset_grid.png with row/column labels")
