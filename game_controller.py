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

        # Current game state (mutable, initialized from defaults)
        self.grid_x = config.GRID_DEFAULT_X
        self.grid_y = config.GRID_DEFAULT_Y
        self.rules = config.DEFAULT_RULES
        self.player_names = config.DEFAULT_PLAYER_NAMES.copy()
        self.player_colors = config.DEFAULT_PLAYER_COLORS.copy()

        # Computed layout values
        self.spacing = 0
        self.board_offset_x = 0
        self.board_offset_y = 0
        self.click_threshold = 0.0
        self.calculate_layout()

        # Game instance
        self.game = Game(self.grid_x, self.grid_y, self.rules)

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
        max_w = (config.WINDOW_WIDTH - 100) // self.grid_x
        max_h = (config.WINDOW_HEIGHT - config.TOP_MARGIN - config.BOTTOM_MARGIN) // self.grid_y
        self.spacing = min(max_w, max_h)

        board_w = self.spacing * self.grid_x
        board_h = self.spacing * self.grid_y
        self.board_offset_x = (config.WINDOW_WIDTH - board_w) // 2
        self.board_offset_y = config.TOP_MARGIN + (config.WINDOW_HEIGHT - config.TOP_MARGIN - config.BOTTOM_MARGIN - board_h) // 2
        self.click_threshold = self.spacing / 2.5

    def draw_board(self):
        """Renders the game board based on current model state."""
        self.screen.fill((240, 240, 240))
        gray = (180, 180, 180)
        ox, oy, sp = self.board_offset_x, self.board_offset_y, self.spacing

        # Draw empty segments (gray)
        for row in self.game.h_segments:
            for seg in row:
                pygame.draw.line(self.screen, gray, seg.start.to_pixel(ox, oy, sp), seg.end.to_pixel(ox, oy, sp), 2)

        for row in self.game.v_segments:
            for seg in row:
                pygame.draw.line(self.screen, gray, seg.start.to_pixel(ox, oy, sp), seg.end.to_pixel(ox, oy, sp), 2)

        # Draw completed squares
        for r, row in enumerate(self.game.squares):
            for c, square in enumerate(row):
                if square.completed_by != 0:
                    color = self.player_colors[square.completed_by]
                    box_surface = pygame.Surface((sp, sp), pygame.SRCALPHA)
                    box_surface.fill(color + (60,))
                    self.screen.blit(box_surface, (ox + c * sp, oy + r * sp))

        # Draw claimed segments (player colors)
        for row in self.game.h_segments:
            for seg in row:
                if seg.owner != 0:
                    pygame.draw.line(self.screen, self.player_colors[seg.owner],
                                     seg.start.to_pixel(ox, oy, sp), seg.end.to_pixel(ox, oy, sp), config.LINE_THICKNESS)

        for row in self.game.v_segments:
            for seg in row:
                if seg.owner != 0:
                    pygame.draw.line(self.screen, self.player_colors[seg.owner],
                                     seg.start.to_pixel(ox, oy, sp), seg.end.to_pixel(ox, oy, sp), config.LINE_THICKNESS)

        # Draw dots
        for row in self.game.points:
            for point in row:
                pygame.draw.circle(self.screen, (50, 50, 50), point.to_pixel(ox, oy, sp), config.DOT_RADIUS)

    def draw_ui(self):
        """Draws the scoreboard, turn indicator, and game-over overlay."""
        score1, score2 = self.game.get_scores()

        p1_text = self.score_font.render(f"{self.player_names[1]}: {score1}", True, self.player_colors[1])
        self.screen.blit(p1_text, (50, 15))

        p2_text = self.score_font.render(f"{self.player_names[2]}: {score2}", True, self.player_colors[2])
        p2_rect = p2_text.get_rect(right=config.WINDOW_WIDTH - 50, top=15)
        self.screen.blit(p2_text, p2_rect)

        if not self.game.game_over:
            text_color = self.player_colors[self.game.current_player]
            turn_text = f"{self.player_names[self.game.current_player]}'s Turn"
            turn_surface = self.font.render(turn_text, True, text_color)
            turn_rect = turn_surface.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT - config.BOTTOM_MARGIN // 2))
            self.screen.blit(turn_surface, turn_rect)

        if self.game.game_over:
            overlay = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (0, 0))

            if score1 > score2:
                win_text = f"{self.player_names[1]} Wins! ({score1} - {score2})"
                color = self.player_colors[1]
            elif score2 > score1:
                win_text = f"{self.player_names[2]} Wins! ({score2} - {score1})"
                color = self.player_colors[2]
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
        """Reads settings from the UI and applies them to controller state."""

        def get_dropdown_text(dropdown):
            opt = dropdown.selected_option
            return opt[0] if isinstance(opt, tuple) else opt

        try:
            self.grid_x = int(self.settings_window.grid_x.get_text())
            self.grid_y = int(self.settings_window.grid_y.get_text())
        except ValueError:
            pass

        self.player_names[1] = self.settings_window.p1_name.get_text()
        self.player_names[2] = self.settings_window.p2_name.get_text()

        rules_text = get_dropdown_text(self.settings_window.rules)
        self.rules = "classic" if "Classic" in rules_text else "4_sides"

        p1_color_text = get_dropdown_text(self.settings_window.p1_color)
        p2_color_text = get_dropdown_text(self.settings_window.p2_color)
        self.player_colors[1] = config.PLAYER_COLOR_CHOICES.get(p1_color_text, self.player_colors[1])
        self.player_colors[2] = config.PLAYER_COLOR_CHOICES.get(p2_color_text, self.player_colors[2])

        self.calculate_layout()
        if reset_board:
            self.game.reset(self.grid_x, self.grid_y, self.rules)

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
                    self.settings_window = SettingsWindow(self.ui_manager,
                        self.grid_x,self.grid_y, self.rules,
                        self.player_names[1], self.player_names[2],
                        self.player_colors[1], self.player_colors[2])

                elif self.settings_window and event.ui_element == self.settings_window.accept_button:
                    try:
                        new_x = int(self.settings_window.grid_x.get_text())
                        new_y = int(self.settings_window.grid_y.get_text())
                    except ValueError:
                        new_x, new_y = self.grid_x, self.grid_y

                    rules_opt = self.settings_window.rules.selected_option
                    rules_text = rules_opt[0] if isinstance(rules_opt, tuple) else rules_opt
                    rules_changed = ("Classic" in rules_text) != self.rules

                    if new_x != self.grid_x or new_y != self.grid_y or rules_changed:
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
                    self.game.reset(self.grid_x, self.grid_y, self.rules)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not self.game.game_over and self.settings_window is None and self.confirm_window is None:
                    self.game.handle_click(event.pos, self.board_offset_x, self.board_offset_y, self.spacing, self.click_threshold)

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