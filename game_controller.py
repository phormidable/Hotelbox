# game_controller.py
import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UIButton, UILabel
import config
from settings_window import SettingsWindow
from game import Game


class ConfirmResetWindow:
    """Small confirmation dialog for game reset."""

    def __init__(self, manager):
        self.window = UIWindow(
            rect=pygame.Rect((150, 180), (300, 180)),
            window_display_title="Confirm Reset",
            manager=manager
        )
        UILabel(relative_rect=pygame.Rect((20, 20), (260, 40)),
                text="Reset the current game?",
                manager=manager, container=self.window)
        self.yes_btn = UIButton(relative_rect=pygame.Rect((50, 100), (80, 35)), text="Yes",
                                manager=manager, container=self.window)
        self.no_btn = UIButton(relative_rect=pygame.Rect((170, 100), (80, 35)), text="No",
                               manager=manager, container=self.window)


class GameController:
    """Owns the Pygame loop, rendering, UI state, and delegates logic to Game."""

    def __init__(self):
        # Pygame initialization
        pygame.init()
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        pygame.display.set_caption("Dots and Boxes")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 36, bold=True)
        self.score_font = pygame.font.SysFont("arial", 28, bold=True)
        self.ui_manager = pygame_gui.UIManager((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))

        # Layout constants
        self.TOP_MARGIN = 90
        self.BOTTOM_MARGIN = 60
        self.SPACING = 0
        self.BOARD_OFFSET_X = 0
        self.BOARD_OFFSET_Y = 0
        self.CLICK_THRESHOLD = 0.0
        self.calculate_layout()

        # Game instance
        self.game = Game(config.GRID_X, config.GRID_Y, config.RULES)

        # UI state
        self.settings_window = None
        self.confirm_window = None

        # Settings button
        self.settings_button = UIButton(
            relative_rect=pygame.Rect((240, 10), (120, 35)),
            text="⚙ Settings",
            manager=self.ui_manager
        )

    def calculate_layout(self):
        """Calculates spacing to keep boxes perfectly square, centered on screen."""
        max_w = (config.WINDOW_WIDTH - 100) // config.GRID_X
        max_h = (config.WINDOW_HEIGHT - self.TOP_MARGIN - self.BOTTOM_MARGIN) // config.GRID_Y
        self.SPACING = min(max_w, max_h)

        board_w = self.SPACING * config.GRID_X
        board_h = self.SPACING * config.GRID_Y
        self.BOARD_OFFSET_X = (config.WINDOW_WIDTH - board_w) // 2
        self.BOARD_OFFSET_Y = self.TOP_MARGIN + (config.WINDOW_HEIGHT - self.TOP_MARGIN - self.BOTTOM_MARGIN - board_h) // 2
        self.CLICK_THRESHOLD = self.SPACING / 2.5

    def draw_board(self):
        """Renders the game board based on current model state."""
        self.screen.fill((240, 240, 240))
        gray = (180, 180, 180)

        # Empty segments
        for r in range(self.game.grid_y + 1):
            for c in range(self.game.grid_x):
                start = (self.BOARD_OFFSET_X + c * self.SPACING, self.BOARD_OFFSET_Y + r * self.SPACING)
                end = (self.BOARD_OFFSET_X + (c + 1) * self.SPACING, self.BOARD_OFFSET_Y + r * self.SPACING)
                pygame.draw.line(self.screen, gray, start, end, 2)

        for r in range(self.game.grid_y):
            for c in range(self.game.grid_x + 1):
                start = (self.BOARD_OFFSET_X + c * self.SPACING, self.BOARD_OFFSET_Y + r * self.SPACING)
                end = (self.BOARD_OFFSET_X + c * self.SPACING, self.BOARD_OFFSET_Y + (r + 1) * self.SPACING)
                pygame.draw.line(self.screen, gray, start, end, 2)

        # Completed squares
        for r in range(self.game.grid_y):
            for c in range(self.game.grid_x):
                square = self.game.squares[r][c]
                if square.completed_by != 0:
                    color = config.PLAYER_COLORS[square.completed_by]
                    box_surface = pygame.Surface((self.SPACING, self.SPACING), pygame.SRCALPHA)
                    faint_color = color + (60,)
                    box_surface.fill(faint_color)
                    self.screen.blit(box_surface, (self.BOARD_OFFSET_X + c * self.SPACING, self.BOARD_OFFSET_Y + r * self.SPACING))

        # Claimed segments
        for r in range(self.game.grid_y + 1):
            for c in range(self.game.grid_x):
                seg = self.game.h_segments[r][c]
                if seg.owner != 0:
                    start = (self.BOARD_OFFSET_X + c * self.SPACING, self.BOARD_OFFSET_Y + r * self.SPACING)
                    end = (self.BOARD_OFFSET_X + (c + 1) * self.SPACING, self.BOARD_OFFSET_Y + r * self.SPACING)
                    pygame.draw.line(self.screen, config.PLAYER_COLORS[seg.owner], start, end, config.LINE_THICKNESS)

        for r in range(self.game.grid_y):
            for c in range(self.game.grid_x + 1):
                seg = self.game.v_segments[r][c]
                if seg.owner != 0:
                    start = (self.BOARD_OFFSET_X + c * self.SPACING, self.BOARD_OFFSET_Y + r * self.SPACING)
                    end = (self.BOARD_OFFSET_X + c * self.SPACING, self.BOARD_OFFSET_Y + (r + 1) * self.SPACING)
                    pygame.draw.line(self.screen, config.PLAYER_COLORS[seg.owner], start, end, config.LINE_THICKNESS)

        # Dots
        for r in range(self.game.grid_y + 1):
            for c in range(self.game.grid_x + 1):
                center = (self.BOARD_OFFSET_X + c * self.SPACING, self.BOARD_OFFSET_Y + r * self.SPACING)
                pygame.draw.circle(self.screen, (50, 50, 50), center, config.DOT_RADIUS)

    def draw_ui(self):
        """Draws the scoreboard, turn indicator, and game-over overlay."""
        score1, score2 = self.game.get_scores()

        p1_text = self.score_font.render(f"{config.PLAYER_NAMES[1]}: {score1}", True, config.PLAYER_COLORS[1])
        self.screen.blit(p1_text, (50, 15))

        p2_text = self.score_font.render(f"{config.PLAYER_NAMES[2]}: {score2}", True, config.PLAYER_COLORS[2])
        p2_rect = p2_text.get_rect(right=config.WINDOW_WIDTH - 50, top=15)
        self.screen.blit(p2_text, p2_rect)

        if not self.game.game_over:
            text_color = config.PLAYER_COLORS[self.game.current_player]
            turn_text = f"{config.PLAYER_NAMES[self.game.current_player]}'s Turn"
            turn_surface = self.font.render(turn_text, True, text_color)
            turn_rect = turn_surface.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT - self.BOTTOM_MARGIN // 2))
            self.screen.blit(turn_surface, turn_rect)

        if self.game.game_over:
            overlay = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (0, 0))

            if score1 > score2:
                win_text = f"{config.PLAYER_NAMES[1]} Wins! ({score1} - {score2})"
                color = config.PLAYER_COLORS[1]
            elif score2 > score1:
                win_text = f"{config.PLAYER_NAMES[2]} Wins! ({score2} - {score1})"
                color = config.PLAYER_COLORS[2]
            else:
                win_text = f"It's a Draw! ({score1} - {score2})"
                color = (255, 255, 255)

            text_surf = self.font.render(win_text, True, color)
            text_rect = text_surf.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 - 30))
            self.screen.blit(text_surf, text_rect)

            restart_surf = self.score_font.render("Press 'R' to Restart", True, (220, 220, 220))
            restart_rect = restart_surf.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 + 30))
            self.screen.blit(restart_surf, restart_rect)

    def apply_settings(self, reset_board: bool = False):
        """Reads settings from the UI and applies them to config and game."""

        def get_dropdown_text(dropdown):
            opt = dropdown.selected_option
            return opt[0] if isinstance(opt, tuple) else opt

        try:
            config.GRID_X = int(self.settings_window.grid_x.get_text())
            config.GRID_Y = int(self.settings_window.grid_y.get_text())
        except ValueError:
            pass

        config.PLAYER_NAMES[1] = self.settings_window.p1_name.get_text()
        config.PLAYER_NAMES[2] = self.settings_window.p2_name.get_text()

        rules_text = get_dropdown_text(self.settings_window.rules)
        config.RULES = "classic" if "Classic" in rules_text else "4_sides"

        p1_color_text = get_dropdown_text(self.settings_window.p1_color)
        p2_color_text = get_dropdown_text(self.settings_window.p2_color)
        config.PLAYER_COLORS[1] = config.PLAYER_COLOR_CHOICES.get(p1_color_text, config.PLAYER_COLORS[1])
        config.PLAYER_COLORS[2] = config.PLAYER_COLOR_CHOICES.get(p2_color_text, config.PLAYER_COLORS[2])

        self.calculate_layout()
        if reset_board:
            self.game.reset(config.GRID_X, config.GRID_Y, config.RULES)

    def handle_events(self) -> bool:
        """Processes all events. Returns False if the game should quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if self.ui_manager.process_events(event):
                pass

            if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                if self.settings_window:
                    self.settings_window.update_color_options()

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.settings_button:
                    self.settings_window = SettingsWindow(self.ui_manager)

                elif self.settings_window and event.ui_element == self.settings_window.accept_button:
                    try:
                        new_x = int(self.settings_window.grid_x.get_text())
                        new_y = int(self.settings_window.grid_y.get_text())
                    except ValueError:
                        new_x, new_y = config.GRID_X, config.GRID_Y

                    rules_opt = self.settings_window.rules.selected_option
                    rules_text = rules_opt[0] if isinstance(rules_opt, tuple) else rules_opt
                    rules_changed = ("Classic" in rules_text) != (config.RULES == "classic")

                    if new_x != config.GRID_X or new_y != config.GRID_Y or rules_changed:
                        self.confirm_window = ConfirmResetWindow(self.ui_manager)
                    else:
                        self.apply_settings(reset_board=False)
                        self.settings_window.window.kill()
                        self.settings_window = None

                elif self.confirm_window and event.ui_element == self.confirm_window.yes_btn:
                    cw = self.confirm_window
                    sw = self.settings_window
                    self.apply_settings(reset_board=True)
                    cw.window.kill()
                    if sw:
                        sw.window.kill()
                    self.confirm_window = None
                    self.settings_window = None

            if event.type == pygame_gui.UI_WINDOW_CLOSE:
                if self.settings_window and event.ui_element == self.settings_window.window:
                    self.settings_window = None
                if self.confirm_window and event.ui_element == self.confirm_window.window:
                    self.confirm_window = None

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game.game_over:
                    self.game.reset(config.GRID_X, config.GRID_Y, config.RULES)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not self.game.game_over and self.settings_window is None and self.confirm_window is None:
                    self.game.handle_click(event.pos, self.BOARD_OFFSET_X, self.BOARD_OFFSET_Y, self.SPACING, self.CLICK_THRESHOLD)

        return True

    def run(self):
        """Main game loop."""
        running = True
        while running:
            time_delta = self.clock.tick(60) / 1000.0

            running = self.handle_events()

            self.draw_board()
            self.draw_ui()

            self.ui_manager.update(time_delta)
            self.ui_manager.draw_ui(self.screen)

            pygame.display.flip()

        pygame.quit()