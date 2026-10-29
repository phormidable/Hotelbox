# main.py
import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UIButton, UILabel
import sys
import config
from settings_window import SettingsWindow
from game import Game

# --- Initialization ---
pygame.init()
screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
pygame.display.set_caption("Dots and Boxes")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 36, bold=True)
score_font = pygame.font.SysFont("arial", 28, bold=True)

ui_manager = pygame_gui.UIManager((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))

# --- Layout Calculations ---
TOP_MARGIN = 90
BOTTOM_MARGIN = 60


def calculate_layout():
    global SPACING, BOARD_OFFSET_X, BOARD_OFFSET_Y, CLICK_THRESHOLD
    max_w = (config.WINDOW_WIDTH - 100) // config.GRID_X
    max_h = (config.WINDOW_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN) // config.GRID_Y
    SPACING = min(max_w, max_h)

    board_w = SPACING * config.GRID_X
    board_h = SPACING * config.GRID_Y
    BOARD_OFFSET_X = (config.WINDOW_WIDTH - board_w) // 2
    BOARD_OFFSET_Y = TOP_MARGIN + (config.WINDOW_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN - board_h) // 2
    CLICK_THRESHOLD = SPACING / 2.5


calculate_layout()

# --- Game Instance ---
game = Game(config.GRID_X, config.GRID_Y, config.RULES)

# --- UI State ---
settings_window = None
confirm_window = None

settings_button = UIButton(
    relative_rect=pygame.Rect((240, 10), (120, 35)),
    text="⚙ Settings",
    manager=ui_manager
)


class ConfirmResetWindow:
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


# --- Drawing Function ---
def draw_board(screen, game, offset_x, offset_y, spacing):
    screen.fill((240, 240, 240))
    gray = (180, 180, 180)

    # Empty segments
    for r in range(game.grid_y + 1):
        for c in range(game.grid_x):
            start = (offset_x + c * spacing, offset_y + r * spacing)
            end = (offset_x + (c + 1) * spacing, offset_y + r * spacing)
            pygame.draw.line(screen, gray, start, end, 2)
    for r in range(game.grid_y):
        for c in range(game.grid_x + 1):
            start = (offset_x + c * spacing, offset_y + r * spacing)
            end = (offset_x + c * spacing, offset_y + (r + 1) * spacing)
            pygame.draw.line(screen, gray, start, end, 2)

    # Completed boxes
    for r in range(game.grid_y):
        for c in range(game.grid_x):
            if game.boxes[r][c] != 0:
                color = config.PLAYER_COLORS[game.boxes[r][c]]
                box_surface = pygame.Surface((spacing, spacing), pygame.SRCALPHA)
                faint_color = color + (60,)
                box_surface.fill(faint_color)
                screen.blit(box_surface, (offset_x + c * spacing, offset_y + r * spacing))

    # Claimed segments
    for r in range(game.grid_y + 1):
        for c in range(game.grid_x):
            if game.h_lines[r][c] != 0:
                start = (offset_x + c * spacing, offset_y + r * spacing)
                end = (offset_x + (c + 1) * spacing, offset_y + r * spacing)
                pygame.draw.line(screen, config.PLAYER_COLORS[game.h_lines[r][c]], start, end, config.LINE_THICKNESS)
    for r in range(game.grid_y):
        for c in range(game.grid_x + 1):
            if game.v_lines[r][c] != 0:
                start = (offset_x + c * spacing, offset_y + r * spacing)
                end = (offset_x + c * spacing, offset_y + (r + 1) * spacing)
                pygame.draw.line(screen, config.PLAYER_COLORS[game.v_lines[r][c]], start, end, config.LINE_THICKNESS)

    # Dots
    for r in range(game.grid_y + 1):
        for c in range(game.grid_x + 1):
            center = (offset_x + c * spacing, offset_y + r * spacing)
            pygame.draw.circle(screen, (50, 50, 50), center, config.DOT_RADIUS)


# --- Apply Settings Helper ---
def apply_settings(reset_board=False):
    def get_dropdown_text(dropdown):
        opt = dropdown.selected_option
        return opt[0] if isinstance(opt, tuple) else opt

    try:
        config.GRID_X = int(settings_window.grid_x.get_text())
        config.GRID_Y = int(settings_window.grid_y.get_text())
    except ValueError:
        pass

    config.PLAYER_NAMES[1] = settings_window.p1_name.get_text()
    config.PLAYER_NAMES[2] = settings_window.p2_name.get_text()

    rules_text = get_dropdown_text(settings_window.rules)
    config.RULES = "classic" if "Classic" in rules_text else "4_sides"

    p1_color_text = get_dropdown_text(settings_window.p1_color)
    p2_color_text = get_dropdown_text(settings_window.p2_color)
    config.PLAYER_COLORS[1] = config.PLAYER_COLOR_CHOICES.get(p1_color_text, config.PLAYER_COLORS[1])
    config.PLAYER_COLORS[2] = config.PLAYER_COLOR_CHOICES.get(p2_color_text, config.PLAYER_COLORS[2])

    calculate_layout()
    if reset_board:
        game.reset(config.GRID_X, config.GRID_Y, config.RULES)


# --- Main Game Loop ---
running = True
while running:
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if ui_manager.process_events(event):
            pass

        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if settings_window:
                settings_window.update_color_options()

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == settings_button:
                settings_window = SettingsWindow(ui_manager)

            elif settings_window and event.ui_element == settings_window.accept_button:
                try:
                    new_x = int(settings_window.grid_x.get_text())
                    new_y = int(settings_window.grid_y.get_text())
                except ValueError:
                    new_x, new_y = config.GRID_X, config.GRID_Y

                rules_opt = settings_window.rules.selected_option
                rules_text = rules_opt[0] if isinstance(rules_opt, tuple) else rules_opt
                rules_changed = ("Classic" in rules_text) != (config.RULES == "classic")

                if new_x != config.GRID_X or new_y != config.GRID_Y or rules_changed:
                    confirm_window = ConfirmResetWindow(ui_manager)
                else:
                    apply_settings(reset_board=False)
                    settings_window.window.kill()
                    settings_window = None

            elif confirm_window and event.ui_element == confirm_window.yes_btn:
                cw = confirm_window
                sw = settings_window
                apply_settings(reset_board=True)
                cw.window.kill()
                if sw:
                    sw.window.kill()
                confirm_window = None
                settings_window = None

        if event.type == pygame_gui.UI_WINDOW_CLOSE:
            if settings_window and event.ui_element == settings_window.window:
                settings_window = None
            if confirm_window and event.ui_element == confirm_window.window:
                confirm_window = None

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game.game_over:
                game.reset(config.GRID_X, config.GRID_Y, config.RULES)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and not game.game_over and settings_window is None and confirm_window is None:
                line_clicked, boxes_completed = game.handle_click(event.pos, BOARD_OFFSET_X, BOARD_OFFSET_Y, SPACING, CLICK_THRESHOLD)
                if line_clicked:
                    if boxes_completed == 0:
                        game.switch_turn()

                    # Robust end-game check
                    if not game.has_free_segments():
                        game.game_over = True

    # --- Drawing ---
    draw_board(screen, game, BOARD_OFFSET_X, BOARD_OFFSET_Y, SPACING)

    score1, score2 = game.get_scores()

    p1_text = score_font.render(f"{config.PLAYER_NAMES[1]}: {score1}", True, config.PLAYER_COLORS[1])
    screen.blit(p1_text, (50, 15))

    p2_text = score_font.render(f"{config.PLAYER_NAMES[2]}: {score2}", True, config.PLAYER_COLORS[2])
    p2_rect = p2_text.get_rect(right=config.WINDOW_WIDTH - 50, top=15)
    screen.blit(p2_text, p2_rect)

    if not game.game_over:
        text_color = config.PLAYER_COLORS[game.current_player]
        turn_text = f"{config.PLAYER_NAMES[game.current_player]}'s Turn"
        turn_surface = font.render(turn_text, True, text_color)
        turn_rect = turn_surface.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT - BOTTOM_MARGIN // 2))
        screen.blit(turn_surface, turn_rect)

    if game.game_over:
        overlay = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        if score1 > score2:
            win_text = f"{config.PLAYER_NAMES[1]} Wins! ({score1} - {score2})"
            color = config.PLAYER_COLORS[1]
        elif score2 > score1:
            win_text = f"{config.PLAYER_NAMES[2]} Wins! ({score2} - {score1})"
            color = config.PLAYER_COLORS[2]
        else:
            win_text = f"It's a Draw! ({score1} - {score2})"
            color = (255, 255, 255)

        text_surf = font.render(win_text, True, color)
        text_rect = text_surf.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 - 30))
        screen.blit(text_surf, text_rect)

        restart_surf = score_font.render("Press 'R' to Restart", True, (220, 220, 220))
        restart_rect = restart_surf.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2 + 30))
        screen.blit(restart_surf, restart_rect)

    ui_manager.update(time_delta)
    ui_manager.draw_ui(screen)
    pygame.display.flip()

pygame.quit()
sys.exit()