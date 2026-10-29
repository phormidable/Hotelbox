import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UIButton, UILabel
import config
from settings_window import SettingsWindow
from game import Game

class ConfirmResetWindow:
    def __init__(self, manager):
        self.window = UIWindow(rect=pygame.Rect((150, 180), (300, 180)), window_display_title="Confirm Reset", manager=manager)
        UILabel(relative_rect=pygame.Rect((20, 20), (260, 40)), text="Reset the current game?", manager=manager, container=self.window)
        self.yes_btn = UIButton(relative_rect=pygame.Rect((50, 100), (80, 35)), text="Yes", manager=manager, container=self.window)
        self.no_btn = UIButton(relative_rect=pygame.Rect((170, 100), (80, 35)), text="No", manager=manager, container=self.window)

class GameController:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        pygame.display.set_caption("Dots and Boxes")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 36, bold=True)
        self.score_font = pygame.font.SysFont("arial", 28, bold=True)
        self.ui_manager = pygame_gui.UIManager((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))

        self.grid_x = config.GRID_DEFAULT_X
        self.grid_y = config.GRID_DEFAULT_Y
        self.rules = config.DEFAULT_RULES
        self.extra_turn_on_square = config.DEFAULT_EXTRA_TURN
        self.player_names = config.DEFAULT_PLAYER_NAMES.copy()
        self.player_colors = config.DEFAULT_PLAYER_COLORS.copy()

        self.spacing = 0
        self.board_offset_x = 0
        self.board_offset_y = 0
        self.click_threshold = 0.0
        self.calculate_layout()

        self.game = Game(self.grid_x, self.grid_y, self.rules, self.extra_turn_on_square)
        self.settings_window = None
        self.confirm_window = None

        self.settings_button = UIButton(relative_rect=pygame.Rect((240, 10), (120, 35)), text="⚙ Settings", manager=self.ui_manager)

    def calculate_layout(self):
        max_w = (config.WINDOW_WIDTH - 100) // self.grid_x
        max_h = (config.WINDOW_HEIGHT - config.TOP_MARGIN - config.BOTTOM_MARGIN) // self.grid_y
        self.spacing = min(max_w, max_h)

        board_w = self.spacing * self.grid_x
        board_h = self.spacing * self.grid_y
        self.board_offset_x = (config.WINDOW_WIDTH - board_w) // 2
        self.board_offset_y = config.TOP_MARGIN + (config.WINDOW_HEIGHT - config.TOP_MARGIN - config.BOTTOM_MARGIN - board_h) // 2
        self.click_threshold = self.spacing / 2.5

    def _get_box_surface(self, color: tuple, sp: int) -> pygame.Surface:
        if not hasattr(self, '_box_cache'):
            self._box_cache = {}
        key = (color, sp)
        if key not in self._box_cache:
            surf = pygame.Surface((sp, sp), pygame.SRCALPHA)
            surf.fill(color + (60,))
            self._box_cache[key] = surf
        return self._box_cache[key]

    def draw_board(self):
        self.screen.fill((240, 240, 240))
        ox, oy, sp = self.board_offset_x, self.board_offset_y, self.spacing
        shrink = config.DOT_RADIUS
        thickness = config.LINE_THICKNESS

        # 1. Draw ALL segments (empty and claimed)
        for row in self.game.model.h_segments:
            for seg in row:
                p1, p2 = seg.get_shortened_pixels(ox, oy, sp, shrink)
                pygame.draw.line(self.screen, self.player_colors[seg.owner], p1, p2, thickness)

        for row in self.game.model.v_segments:
            for seg in row:
                p1, p2 = seg.get_shortened_pixels(ox, oy, sp, shrink)
                pygame.draw.line(self.screen, self.player_colors[seg.owner], p1, p2, thickness)

        # 2. Draw completed squares
        for r, row in enumerate(self.game.model.squares):
            for c, square in enumerate(row):
                if square.completed_by != 0:
                    color = self.player_colors[square.completed_by]
                    self.screen.blit(self._get_box_surface(color, sp), (ox + c * sp, oy + r * sp))

        # 3. Draw hovered segment
        if not self.game.is_over and not self.settings_window and not self.confirm_window:
            hovered = self.game.get_hovered_segment(pygame.mouse.get_pos(), ox, oy, sp, self.click_threshold)
            if hovered:
                is_h, r, c = hovered
                seg = self.game.model.h_segments[r][c] if is_h else self.game.model.v_segments[r][c]
                p1, p2 = seg.get_shortened_pixels(ox, oy, sp, shrink)
                pygame.draw.line(self.screen, config.HOVER_COLOR, p1, p2, thickness + 2)

        # 4. Draw dots as 4 smaller diamonds (squares rotated 45 degrees)
        dot_color = config.DOT_COLOR
        half_rd = config.DOT_RADIUS / 2.0

        for r, row in enumerate(self.game.model.points):
            for c, point in enumerate(row):
                x, y = point.to_pixel(ox, oy, sp)
                rd = config.DOT_RADIUS

                # Main diamond vertices
                top_pt = (x, y - rd)
                right_pt = (x + rd, y)
                bottom_pt = (x, y + rd)
                left_pt = (x - rd, y)

                # Midpoints of the main diamond edges (these form the inner corners of the small diamonds)
                tr_pt = (x + half_rd, y - half_rd)
                br_pt = (x + half_rd, y + half_rd)
                bl_pt = (x - half_rd, y + half_rd)
                tl_pt = (x - half_rd, y - half_rd)

                # Draw base diamond first to prevent any 1px gaps between the smaller diamonds
                base_diamond = [top_pt, right_pt, bottom_pt, left_pt]
                pygame.draw.polygon(self.screen, dot_color, base_diamond)

                # Define the 4 smaller diamonds
                top_diamond = [(x, y), tl_pt, top_pt, tr_pt]
                bottom_diamond = [(x, y), bl_pt, bottom_pt, br_pt]
                left_diamond = [(x, y), tl_pt, left_pt, bl_pt]
                right_diamond = [(x, y), tr_pt, right_pt, br_pt]

                # Determine colors based on adjacent segments
                # Top small diamond points UP -> connects to vertical segment ABOVE
                v_top_owner = self.game.model.v_segments[r - 1][c].owner if r > 0 else 0
                top_color = self.player_colors[v_top_owner] if v_top_owner != 0 else dot_color

                # Bottom small diamond points DOWN -> connects to vertical segment BELOW
                v_bottom_owner = self.game.model.v_segments[r][c].owner if r < self.game.model.grid_y else 0
                bottom_color = self.player_colors[v_bottom_owner] if v_bottom_owner != 0 else dot_color

                # Left small diamond points LEFT -> connects to horizontal segment LEFT
                h_left_owner = self.game.model.h_segments[r][c - 1].owner if c > 0 else 0
                left_color = self.player_colors[h_left_owner] if h_left_owner != 0 else dot_color

                # Right small diamond points RIGHT -> connects to horizontal segment RIGHT
                h_right_owner = self.game.model.h_segments[r][c].owner if c < self.game.model.grid_x else 0
                right_color = self.player_colors[h_right_owner] if h_right_owner != 0 else dot_color

                # Draw the colored smaller diamonds over the base diamond
                pygame.draw.polygon(self.screen, top_color, top_diamond)
                pygame.draw.polygon(self.screen, bottom_color, bottom_diamond)
                pygame.draw.polygon(self.screen, left_color, left_diamond)
                pygame.draw.polygon(self.screen, right_color, right_diamond)

    def draw_ui(self):
        score1, score2 = self.game.model.get_scores()

        p1_text = self.score_font.render(f"{self.player_names[1]}: {score1}", True, self.player_colors[1])
        self.screen.blit(p1_text, (50, 15))

        p2_text = self.score_font.render(f"{self.player_names[2]}: {score2}", True, self.player_colors[2])
        p2_rect = p2_text.get_rect(right=config.WINDOW_WIDTH - 50, top=15)
        self.screen.blit(p2_text, p2_rect)

        if not self.game.is_over:
            text_color = self.player_colors[self.game.model.current_player]
            turn_text = f"{self.player_names[self.game.model.current_player]}'s Turn"
            turn_surface = self.font.render(turn_text, True, text_color)
            turn_rect = turn_surface.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT - config.BOTTOM_MARGIN // 2))
            self.screen.blit(turn_surface, turn_rect)

        if self.game.is_over:
            overlay = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            self.screen.blit(overlay, (0, 0))

            if score1 > score2:
                win_text, color = f"{self.player_names[1]} Wins! ({score1} - {score2})", self.player_colors[1]
            elif score2 > score1:
                win_text, color = f"{self.player_names[2]} Wins! ({score2} - {score1})", self.player_colors[2]
            else:
                win_text, color = f"It's a Draw! ({score1} - {score2})", (255, 255, 255)

            text_surf = self.font.render(win_text, True, color)
            text_rect = text_surf.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 - 30))
            self.screen.blit(text_surf, text_rect)

            restart_surf = self.score_font.render("Press 'R' to Restart", True, (220, 220, 220))
            restart_rect = restart_surf.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 + 30))
            self.screen.blit(restart_surf, restart_rect)

    def _apply_settings(self, reset_board: bool = False):
        try:
            self.grid_x = int(self.settings_window.grid_x.get_text())
            self.grid_y = int(self.settings_window.grid_y.get_text())
        except ValueError:
            pass

        self.player_names[1] = self.settings_window.p1_name.get_text()
        self.player_names[2] = self.settings_window.p2_name.get_text()

        rules_text = self.settings_window.rules.selected_option
        self.rules = "classic" if "Classic" in rules_text else "4_sides"

        # Read the checkbox state
        extra_turn_text = self.settings_window.extra_turn.selected_option
        self.extra_turn_on_square = (extra_turn_text == 'Extra turn')

        p1_color = self.settings_window.p1_color.selected_option
        p2_color = self.settings_window.p2_color.selected_option
        self.player_colors[1] = config.PLAYER_COLOR_CHOICES.get(p1_color, self.player_colors[1])
        self.player_colors[2] = config.PLAYER_COLOR_CHOICES.get(p2_color, self.player_colors[2])

        self.calculate_layout()
        if reset_board:
            self.game.reset(self.grid_x, self.grid_y, self.rules, self.extra_turn_on_square)
        else:
            # If not resetting the board, still update the rules in the model
            self.game.model.rules = self.rules
            self.game.model.extra_turn_on_square = self.extra_turn_on_square

    def _handle_settings_accept(self):
        try:
            new_x = int(self.settings_window.grid_x.get_text())
            new_y = int(self.settings_window.grid_y.get_text())
        except ValueError:
            new_x, new_y = self.grid_x, self.grid_y

        rules_text = self.settings_window.rules.selected_option
        rules_changed = ("Classic" in rules_text) != (self.rules == "classic")

        # Check if the extra turn rule was toggled
        extra_turn_text = self.settings_window.extra_turn.selected_option
        extra_turn_changed = (extra_turn_text == 'Extra turn') != self.extra_turn_on_square

        # Prompt to reset if ANY major rule/size changed
        if new_x != self.grid_x or new_y != self.grid_y or rules_changed or extra_turn_changed:
            self.confirm_window = ConfirmResetWindow(self.ui_manager)
        else:
            self._apply_settings(reset_board=False)
            self.settings_window.window.kill()
            self.settings_window = None

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            self.ui_manager.process_events(event)

            if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED and self.settings_window:
                self.settings_window.update_color_options()

            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == self.settings_button:
                    self.settings_window = SettingsWindow(
                        self.ui_manager, self.grid_x, self.grid_y, self.rules,
                        self.player_names[1], self.player_names[2],
                        self.player_colors[1], self.player_colors[2],
                        self.extra_turn_on_square
                    )
                elif self.settings_window and event.ui_element == self.settings_window.accept_button:
                    self._handle_settings_accept()
                elif self.confirm_window and event.ui_element == self.confirm_window.yes_btn:
                    self._apply_settings(reset_board=True)
                    self.confirm_window.window.kill()
                    self.settings_window.window.kill()
                    self.confirm_window = None
                    self.settings_window = None

            elif event.type == pygame_gui.UI_WINDOW_CLOSE:
                if self.settings_window and event.ui_element == self.settings_window.window:
                    self.settings_window = None
                elif self.confirm_window and event.ui_element == self.confirm_window.window:
                    self.confirm_window = None

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game.is_over:
                    self.game.reset(self.grid_x, self.grid_y, self.rules)

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not self.game.is_over and not self.settings_window and not self.confirm_window:
                    self.game.handle_click(event.pos, self.board_offset_x, self.board_offset_y, self.spacing, self.click_threshold)

        return True

    def run(self):
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