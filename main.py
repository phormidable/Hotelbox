# main.py
import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UIButton, UILabel
import sys
import math
import config
from settings_window import SettingsWindow

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
DOT_RADIUS = 6
LINE_THICKNESS = 5


def calculate_layout():
    """Calculates spacing to keep boxes perfectly square, centered on screen."""
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


# --- Game State ---
def init_game_state():
    # REMOVED: settings_window and confirm_window from the global list
    global h_lines, v_lines, boxes, current_player, game_over

    h_lines = [[0 for _ in range(config.GRID_X)] for _ in range(config.GRID_Y + 1)]
    v_lines = [[0 for _ in range(config.GRID_X + 1)] for _ in range(config.GRID_Y)]
    boxes = [[0 for _ in range(config.GRID_X)] for _ in range(config.GRID_Y)]

    current_player = 1
    game_over = False

init_game_state()

settings_window = None
confirm_window = None


# --- UI Elements ---
settings_button = UIButton(
    relative_rect=pygame.Rect((240, 10), (120, 35)),  # Moved down slightly
    text="⚙ Settings",
    manager=ui_manager
)


# --- Confirmation Dialog Class ---
class ConfirmResetWindow:
    def __init__(self, manager):
        self.window = UIWindow(
            rect=pygame.Rect((150, 180), (300, 180)),  # CHANGED: Increased width to 300
            window_display_title="Confirm Reset",
            manager=manager
        )
        # CHANGED: Shortened text and widened the label to 260
        UILabel(relative_rect=pygame.Rect((20, 20), (260, 40)),
                text="Reset the current game?",
                manager=manager, container=self.window)

        # Adjusted button positions slightly for the wider window
        self.yes_btn = UIButton(relative_rect=pygame.Rect((50, 100), (80, 35)), text="Yes",
                                manager=manager, container=self.window)
        self.no_btn = UIButton(relative_rect=pygame.Rect((170, 100), (80, 35)), text="No",
                               manager=manager, container=self.window)


# --- Helper Functions ---
def get_midpoint(is_horizontal, row, col):
    if is_horizontal:
        x = BOARD_OFFSET_X + col * SPACING + SPACING // 2
        y = BOARD_OFFSET_Y + row * SPACING
    else:
        x = BOARD_OFFSET_X + col * SPACING
        y = BOARD_OFFSET_Y + row * SPACING + SPACING // 2
    return x, y


def distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def is_box_complete(r, c):
    top = h_lines[r][c]
    bottom = h_lines[r + 1][c]
    left = v_lines[r][c]
    right = v_lines[r][c + 1]

    # UPDATED: Handle both rule sets
    if config.RULES == "classic":
        return top != 0 and bottom != 0 and left != 0 and right != 0
    else:  # 4_sides
        return top != 0 and top == bottom == left == right


def check_completed_boxes(is_horizontal, r, c):
    completed_count = 0
    if is_horizontal:
        if r > 0 and is_box_complete(r - 1, c):
            if boxes[r - 1][c] == 0:
                boxes[r - 1][c] = current_player
                completed_count += 1
        if r < config.GRID_Y and is_box_complete(r, c):
            if boxes[r][c] == 0:
                boxes[r][c] = current_player
                completed_count += 1
    else:
        if c > 0 and is_box_complete(r, c - 1):
            if boxes[r][c - 1] == 0:
                boxes[r][c - 1] = current_player
                completed_count += 1
        if c < config.GRID_X and is_box_complete(r, c):
            if boxes[r][c] == 0:
                boxes[r][c] = current_player
                completed_count += 1
    return completed_count


def handle_click(mouse_pos):
    global current_player
    for r in range(config.GRID_Y + 1):
        for c in range(config.GRID_X):
            if h_lines[r][c] == 0:
                mid = get_midpoint(True, r, c)
                if distance(mouse_pos, mid) < CLICK_THRESHOLD:
                    h_lines[r][c] = current_player
                    return True, check_completed_boxes(True, r, c)
    for r in range(config.GRID_Y):
        for c in range(config.GRID_X + 1):
            if v_lines[r][c] == 0:
                mid = get_midpoint(False, r, c)
                if distance(mouse_pos, mid) < CLICK_THRESHOLD:
                    v_lines[r][c] = current_player
                    return True, check_completed_boxes(False, r, c)
    return False, 0


def apply_settings(reset_board=False):
    global SPACING, BOARD_OFFSET_X, BOARD_OFFSET_Y

    # NEW: Helper to safely get text from dropdowns (handles tuple vs string quirks)
    def get_dropdown_text(dropdown):
        opt = dropdown.selected_option
        return opt[0] if isinstance(opt, tuple) else opt

    # Update Config
    try:
        config.GRID_X = int(settings_window.grid_x.get_text())
        config.GRID_Y = int(settings_window.grid_y.get_text())
    except ValueError:
        pass  # Keep current config if user typed invalid numbers

    config.PLAYER_NAMES[1] = settings_window.p1_name.get_text()
    config.PLAYER_NAMES[2] = settings_window.p2_name.get_text()

    # UPDATED: Use the helper to get the rules text
    rules_text = get_dropdown_text(settings_window.rules)
    config.RULES = "classic" if "Classic" in rules_text else "4_sides"

    color_map = {
        'Green': (34, 139, 34), 'Blue': (30, 144, 255), 'Red': (255, 0, 0),
        'Purple': (128, 0, 128), 'Orange': (255, 165, 0), 'Cyan': (0, 255, 255)
    }

    # UPDATED: Use the helper to get the color texts
    p1_color_text = get_dropdown_text(settings_window.p1_color)
    p2_color_text = get_dropdown_text(settings_window.p2_color)

    # Use .get() with a fallback color just in case
    config.PLAYER_COLORS[1] = color_map.get(p1_color_text, (34, 139, 34))
    config.PLAYER_COLORS[2] = color_map.get(p2_color_text, (30, 144, 255))

    calculate_layout()  # Recalculate board dimensions

    if reset_board:
        init_game_state()


def draw_board():
    screen.fill((240, 240, 240))
    gray = (180, 180, 180)

    for r in range(config.GRID_Y + 1):
        for c in range(config.GRID_X):
            start = (BOARD_OFFSET_X + c * SPACING, BOARD_OFFSET_Y + r * SPACING)
            end = (BOARD_OFFSET_X + (c + 1) * SPACING, BOARD_OFFSET_Y + r * SPACING)
            pygame.draw.line(screen, gray, start, end, 2)
    for r in range(config.GRID_Y):
        for c in range(config.GRID_X + 1):
            start = (BOARD_OFFSET_X + c * SPACING, BOARD_OFFSET_Y + r * SPACING)
            end = (BOARD_OFFSET_X + c * SPACING, BOARD_OFFSET_Y + (r + 1) * SPACING)
            pygame.draw.line(screen, gray, start, end, 2)

    for r in range(config.GRID_Y):
        for c in range(config.GRID_X):
            if boxes[r][c] != 0:
                color = config.PLAYER_COLORS[boxes[r][c]]
                box_surface = pygame.Surface((SPACING, SPACING), pygame.SRCALPHA)
                faint_color = color + (60,)
                box_surface.fill(faint_color)
                screen.blit(box_surface, (BOARD_OFFSET_X + c * SPACING, BOARD_OFFSET_Y + r * SPACING))

    for r in range(config.GRID_Y + 1):
        for c in range(config.GRID_X):
            if h_lines[r][c] != 0:
                start = (BOARD_OFFSET_X + c * SPACING, BOARD_OFFSET_Y + r * SPACING)
                end = (BOARD_OFFSET_X + (c + 1) * SPACING, BOARD_OFFSET_Y + r * SPACING)
                pygame.draw.line(screen, config.PLAYER_COLORS[h_lines[r][c]], start, end, LINE_THICKNESS)
    for r in range(config.GRID_Y):
        for c in range(config.GRID_X + 1):
            if v_lines[r][c] != 0:
                start = (BOARD_OFFSET_X + c * SPACING, BOARD_OFFSET_Y + r * SPACING)
                end = (BOARD_OFFSET_X + c * SPACING, BOARD_OFFSET_Y + (r + 1) * SPACING)
                pygame.draw.line(screen, config.PLAYER_COLORS[v_lines[r][c]], start, end, LINE_THICKNESS)

    for r in range(config.GRID_Y + 1):
        for c in range(config.GRID_X + 1):
            center = (BOARD_OFFSET_X + c * SPACING, BOARD_OFFSET_Y + r * SPACING)
            pygame.draw.circle(screen, (50, 50, 50), center, DOT_RADIUS)


# --- Main Game Loop ---
running = True
while running:
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if ui_manager.process_events(event):
            pass

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            # 1. Open Settings
            if event.ui_element == settings_button:
                settings_window = SettingsWindow(ui_manager)

            # 2. Handle Accept Button
            elif settings_window and event.ui_element == settings_window.accept_button:
                # Safely get the text, fallback to current config if user typed letters
                try:
                    new_x = int(settings_window.grid_x.get_text())
                    new_y = int(settings_window.grid_y.get_text())
                except ValueError:
                    new_x, new_y = config.GRID_X, config.GRID_Y

                grid_x_changed = new_x != config.GRID_X
                grid_y_changed = new_y != config.GRID_Y

                # NEW: Safely extract the rules text to check for changes
                rules_opt = settings_window.rules.selected_option
                rules_text = rules_opt[0] if isinstance(rules_opt, tuple) else rules_opt
                rules_changed = ("Classic" in rules_text) != (config.RULES == "classic")

                if grid_x_changed or grid_y_changed or rules_changed:
                    # Open the confirmation dialog
                    confirm_window = ConfirmResetWindow(ui_manager)
                else:
                    # Only visual changes (colors/names), no reset needed
                    apply_settings(reset_board=False)
                    settings_window.window.kill()
                    settings_window = None

            # 3. Handle Confirmation Dialog "Yes" Button
            elif confirm_window and event.ui_element == confirm_window.yes_btn:
                # Save local references before apply_settings resets the board
                cw = confirm_window
                sw = settings_window

                # Apply the settings and reset the board
                apply_settings(reset_board=True)

                # Now safely kill the windows using our local references
                cw.window.kill()
                if sw:
                    sw.window.kill()

                # Finally, clear the global variables
                confirm_window = None
                settings_window = None

        if event.type == pygame_gui.UI_WINDOW_CLOSE:
            if settings_window and event.ui_element == settings_window.window:
                settings_window = None
            if confirm_window and event.ui_element == confirm_window.window:
                confirm_window = None

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                init_game_state()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and not game_over and SettingsWindow is None and confirm_window is None:
                line_clicked, boxes_completed = handle_click(event.pos)
                if line_clicked:
                    if boxes_completed == 0:
                        current_player = 2 if current_player == 1 else 1
                    total_boxes = config.GRID_X * config.GRID_Y
                    score1 = sum(row.count(1) for row in boxes)
                    score2 = sum(row.count(2) for row in boxes)
                    if score1 + score2 == total_boxes:
                        game_over = True

    # 2. Drawing
    draw_board()

    score1 = sum(row.count(1) for row in boxes)
    score2 = sum(row.count(2) for row in boxes)

    # Use Player Names from config!
    p1_text = score_font.render(f"{config.PLAYER_NAMES[1]}: {score1}", True, config.PLAYER_COLORS[1])
    screen.blit(p1_text, (50, 15))

    p2_text = score_font.render(f"{config.PLAYER_NAMES[2]}: {score2}", True, config.PLAYER_COLORS[2])
    p2_rect = p2_text.get_rect(right=config.WINDOW_WIDTH - 50, top=15)
    screen.blit(p2_text, p2_rect)

    if not game_over:
        text_color = config.PLAYER_COLORS[current_player]
        turn_text = f"{config.PLAYER_NAMES[current_player]}'s Turn"
        turn_surface = font.render(turn_text, True, text_color)
        turn_rect = turn_surface.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT - BOTTOM_MARGIN // 2))
        screen.blit(turn_surface, turn_rect)

    if game_over:
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