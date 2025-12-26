import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

import pygame

from engine.entity_system import PlayerState
from engine.map_loader import MapData, MapLoader
from engine.map_renderer import MapRenderer, TileRenderCommand


WINDOW_TITLE = "Those Who Fight"
FPS = 60

COLOR_BG = (20, 20, 30)
COLOR_PANEL = (40, 40, 55)
COLOR_TEXT = (240, 240, 240)
COLOR_BUTTON = (70, 140, 220)
COLOR_BUTTON_HOVER = (90, 170, 255)


class Button:
    def __init__(self, rect: pygame.Rect, label: str, font: pygame.font.Font) -> None:
        self.rect = rect
        self.label = label
        self.font = font
        self.text_surface = self.font.render(self.label, True, COLOR_TEXT)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def draw(self, surface: pygame.Surface, is_hovered: bool) -> None:
        color = COLOR_BUTTON_HOVER if is_hovered else COLOR_BUTTON
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        surface.blit(self.text_surface, self.text_rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


def create_window() -> pygame.Surface:
    pygame.display.set_caption(WINDOW_TITLE)
    info = pygame.display.Info()
    width, height = info.current_w, info.current_h
    if not width or not height:
        desktop_sizes = getattr(pygame.display, "get_desktop_sizes", lambda: [])()
        if desktop_sizes:
            width, height = desktop_sizes[0]
        else:
            width, height = 1280, 720
    return pygame.display.set_mode((width, height), pygame.SCALED | pygame.NOFRAME)


def find_spawn(map_data: MapData, spawn_id: str = "spawn_south_gate") -> Tuple[int, int]:
    for entity in map_data.entities:
        if entity.type != "spawn":
            continue
        if entity.id == spawn_id:
            return entity.x, entity.y
    for entity in map_data.entities:
        if entity.type == "spawn":
            return entity.x, entity.y
    return 0, 0


def load_map(root: Path, map_name: str) -> Tuple[MapData, MapRenderer, PlayerState]:
    loader = MapLoader(root)
    map_data = loader.load_map(map_name)
    spawn_x, spawn_y = find_spawn(map_data)
    player = PlayerState(x=spawn_x, y=spawn_y)
    renderer = MapRenderer(map_data)
    return map_data, renderer, player


def get_image(cache: Dict[str, pygame.Surface], root: Path, atlas_image: str) -> Optional[pygame.Surface]:
    if not atlas_image:
        return None
    cached = cache.get(atlas_image)
    if cached:
        return cached
    image_path = root / atlas_image
    if not image_path.exists():
        return None
    loaded = pygame.image.load(str(image_path)).convert_alpha()
    cache[atlas_image] = loaded
    return loaded


def draw_tile(
    screen: pygame.Surface,
    command: TileRenderCommand,
    image_cache: Dict[str, pygame.Surface],
    root: Path,
    view_offset: Tuple[int, int],
    tile_size: int,
) -> None:
    if not command.atlas_image or not command.source_rect:
        return
    sprite = get_image(image_cache, root, command.atlas_image)
    if sprite is None:
        return
    dest_x = command.x - view_offset[0] * tile_size
    dest_y = command.y - view_offset[1] * tile_size
    screen.blit(sprite, (dest_x, dest_y), pygame.Rect(command.source_rect))


def render_map(
    screen: pygame.Surface,
    map_data: MapData,
    renderer: MapRenderer,
    player: PlayerState,
    image_cache: Dict[str, pygame.Surface],
    root: Path,
) -> None:
    tile_size = map_data.tile_size
    screen_rect = screen.get_rect()
    view_w = max(1, screen_rect.width // tile_size)
    view_h = max(1, screen_rect.height // tile_size)
    view_x = max(0, min(map_data.width - view_w, player.x - view_w // 2))
    view_y = max(0, min(map_data.height - view_h, player.y - view_h // 2))
    commands = renderer.render_tiles(view_x, view_y, view_w, view_h, include_overhead=True)
    for command in commands:
        draw_tile(
            screen=screen,
            command=command,
            image_cache=image_cache,
            root=root,
            view_offset=(view_x, view_y),
            tile_size=tile_size,
        )


def run() -> None:
    pygame.init()
    clock = pygame.time.Clock()
    screen = create_window()

    font_title = pygame.font.Font(None, 80)
    font_button = pygame.font.Font(None, 48)

    start_button = None
    state = "title"
    map_data = None
    map_renderer = None
    player = None
    image_cache: Dict[str, pygame.Surface] = {}
    root = Path(__file__).resolve().parent

    running = True
    while running:
        delta_time = clock.tick(FPS) / 1000
        _ = delta_time
        screen.fill(COLOR_BG)
        screen_rect = screen.get_rect()

        if state == "title":
            title_surface = font_title.render(WINDOW_TITLE, True, COLOR_TEXT)
            title_rect = title_surface.get_rect(center=(screen_rect.centerx, screen_rect.centery - 120))
            screen.blit(title_surface, title_rect)

            panel_rect = pygame.Rect(0, 0, 480, 180)
            panel_rect.center = (screen_rect.centerx, screen_rect.centery + 40)
            pygame.draw.rect(screen, COLOR_PANEL, panel_rect, border_radius=16)

            button_rect = pygame.Rect(0, 0, 220, 70)
            button_rect.center = panel_rect.center
            if start_button is None:
                start_button = Button(button_rect, "Start Game", font_button)
            else:
                start_button.rect = button_rect
                start_button.text_rect = start_button.text_surface.get_rect(center=button_rect.center)

            mouse_pos = pygame.mouse.get_pos()
            is_hovered = start_button.rect.collidepoint(mouse_pos)
            start_button.draw(screen, is_hovered)
        else:
            if map_data and map_renderer and player:
                render_map(screen, map_data, map_renderer, player, image_cache, root)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if state == "title" and start_button and start_button.handle_event(event):
                map_data, map_renderer, player = load_map(root, "Hearthvale_Town")
                state = "game"

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    run()
