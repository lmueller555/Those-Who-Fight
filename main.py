import sys

import pygame


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


def run() -> None:
    pygame.init()
    clock = pygame.time.Clock()
    screen = create_window()

    font_title = pygame.font.Font(None, 80)
    font_button = pygame.font.Font(None, 48)
    font_game = pygame.font.Font(None, 56)

    start_button = None
    state = "title"

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
            game_text = font_game.render("Game running!", True, COLOR_TEXT)
            game_rect = game_text.get_rect(center=screen_rect.center)
            screen.blit(game_text, game_rect)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            if state == "title" and start_button and start_button.handle_event(event):
                state = "game"

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    run()
