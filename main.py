# main.py
import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UIButton, UITextEntryLine, UIDropDownMenu, UILabel
import sys
import math
import config

# --- Initialization ---
pygame.init()
screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
pygame.display.set_caption("Dots and Boxes")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 36, bold=True)
score_font = pygame.font.SysFont("arial", 28, bold=True)

# NEW: Initialize the pygame_gui Manager
ui_manager = pygame_gui.UIManager((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))

# --- Layout Calculations ---
MARGIN = 50
SPACING = (config.WINDOW_WIDTH - 2 * MARGIN) // config.GRID_SIZE
DOT_RADIUS = 6
LINE_THICKNESS = 5
CLICK_THRESHOLD = SPACING / 2.5


# --- Game State ---
def init_game_state():
    global h_lines, v_lines, boxes, current_player, game_over, settings_window

    h_lines = [[0 for _ in range(config.GRID_SIZE)] for _ in range(config.GRID_SIZE + 1)]
    v_lines = [[0 for _ in range(config.GRID_SIZE + 1)] for _ in range(config.GRID_SIZE)]
    boxes = [[0 for _ in range(config.GRID_SIZE)] for _ in range(config.GRID_SIZE)]

    current_player = 1
    game_over = False
    settings_window = None  # NEW: Track if settings window is open


init_game_state()

# --- NEW: Settings Button ---
# Placed in the top middle, between the two score areas
settings_button = UIButton(
    relative_rect=pygame.Rect((240, 10), (120, 35)),
    text="⚙ Settings",
    manager=ui_manager,
    tool_tip_text="Change game rules and colors"
)


# --- NEW: Settings Window Class ---
class SettingsWindow:
    def __init__(self, manager):
        self.window = UIWindow(
            rect=pygame.Rect((100, 80), (400, 460)),  # <--- Change 'relative_rect' to 'rect' here
            window_display_title="Game Settings",
            manager=manager
        )

        y_offset = 15

        # Player 1 Name
        UILabel(relative_rect=pygame.Rect((15, y_offset), (140, 30)), text="Player 1 Name:", manager=manager, container=self.window)
        self.p1_name = UITextEntryLine(relative_rect=pygame.Rect((165, y_offset), (200, 30)), manager=manager, container=self.window)
        self.p1_name.set_text("Player 1")
        y_offset += 45

        # Player 2 Name
        UILabel(relative_rect=pygame.Rect((15, y_offset), (140, 30)), text="Player 2 Name:", manager=manager, container=self.window)
        self.p2_name = UITextEntryLine(relative_rect=pygame.Rect((165, y_offset), (200, 30)), manager=manager, container=self.window)
        self.p2_name.set_text("Player 2")
        y_offset += 45

        # Grid Size X
        UILabel(relative_rect=pygame.Rect((15, y_offset), (140, 30)), text="Grid Width (X):", manager=manager, container=self.window)
        self.grid_x = UITextEntryLine(relative_rect=pygame.Rect((165, y_offset), (200, 30)), manager=manager, container=self.window)
        self.grid_x.set_text(str(config.GRID_SIZE))
        y_offset += 45

        # Grid Size Y
        UILabel(relative_rect=pygame.Rect((15, y_offset), (140, 30)), text="Grid Height (Y):", manager=manager, container=self.window)
        self.grid_y = UITextEntryLine(relative_rect=pygame.Rect((165, y_offset), (200, 30)), manager=manager, container=self.window)
        self.grid_y.set_text(str(config.GRID_SIZE))
        y_offset += 45

        # Rules Dropdown
        UILabel(relative_rect=pygame.Rect((15, y_offset), (140, 30)), text="Rules:", manager=manager, container=self.window)
        self.rules = UIDropDownMenu(
            options_list=['Classic (Any 4 sides)', '4 Sides (Same color)'],
            starting_option='4 Sides (Same color)',
            relative_rect=pygame.Rect((165, y_offset), (200, 30)),
            manager=manager,
            container=self.window
        )
        y_offset += 45

        # Color Dropdowns (Using a list of preset colors for simplicity)
        color_options = ['Green', 'Blue', 'Red', 'Purple', 'Orange', 'Cyan']

        UILabel(relative_rect=pygame.Rect((15, y_offset), (140, 30)), text="Player 1 Color:", manager=manager, container=self.window)
        self.p1_color = UIDropDownMenu(
            options_list=color_options, starting_option='Green',
            relative_rect=pygame.Rect((165, y_offset), (200, 30)),
            manager=manager, container=self.window
        )
        y_offset += 45

        UILabel(relative_rect=pygame.Rect((15, y_offset), (140, 30)), text="Player 2 Color:", manager=manager, container=self.window)
        self.p2_color = UIDropDownMenu(
            options_list=color_options, starting_option='Blue',
            relative_rect=pygame.Rect((165, y_offset), (200, 30)),
            manager=manager, container=self.window
        )


# --- Helper Functions (get_midpoint, distance, is_box_complete, etc.) ---
# [I have omitted the unchanged helper functions here for brevity,
# but keep them exactly as they were in your previous code!]

def get_midpoint(is_horizontal, row, col):
    if is_horizontal:
        x = MARGIN + col * SPACING + SPACING // 2
        y = MARGIN + row * SPACING
    else:
        x = MARGIN + col * SPACING
        y = MARGIN + row * SPACING + SPACING // 2
    return x, y


def distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def is_box_complete(r, c):
    top = h_lines[r][c]
    bottom = h_lines[r + 1][c]
    left = v_lines[r][c]
    right = v_lines[r][c + 1]
    return top != 0 and top == bottom == left == right


def check_completed_boxes(is_horizontal, r, c):
    completed_count = 0
    if is_horizontal:
        if r > 0 and is_box_complete(r - 1, c):
            if boxes[r - 1][c] == 0:
                boxes[r - 1][c] = current_player
                completed_count += 1
        if r < config.GRID_SIZE and is_box_complete(r, c):
            if boxes[r][c] == 0:
                boxes[r][c] = current_player
                completed_count += 1
    else:
        if c > 0 and is_box_complete(r, c - 1):
            if boxes[r][c - 1] == 0:
                boxes[r][c - 1] = current_player
                completed_count += 1
        if c < config.GRID_SIZE and is_box_complete(r, c):
            if boxes[r][c] == 0:
                boxes[r][c] = current_player
                completed_count += 1
    return completed_count


def handle_click(mouse_pos):
    global current_player
    for r in range(config.GRID_SIZE + 1):
        for c in range(config.GRID_SIZE):
            if h_lines[r][c] == 0:
                mid = get_midpoint(True, r, c)
                if distance(mouse_pos, mid) < CLICK_THRESHOLD:
                    h_lines[r][c] = current_player
                    return True, check_completed_boxes(True, r, c)
    for r in range(config.GRID_SIZE):
        for c in range(config.GRID_SIZE + 1):
            if v_lines[r][c] == 0:
                mid = get_midpoint(False, r, c)
                if distance(mouse_pos, mid) < CLICK_THRESHOLD:
                    v_lines[r][c] = current_player
                    return True, check_completed_boxes(False, r, c)
    return False, 0


def draw_board():
    screen.fill((240, 240, 240))
    gray = (180, 180, 180)
    for r in range(config.GRID_SIZE + 1):
        for c in range(config.GRID_SIZE):
            start = (MARGIN + c * SPACING, MARGIN + r * SPACING)
            end = (MARGIN + (c + 1) * SPACING, MARGIN + r * SPACING)
            pygame.draw.line(screen, gray, start, end, 2)
    for r in range(config.GRID_SIZE):
        for c in range(config.GRID_SIZE + 1):
            start = (MARGIN + c * SPACING, MARGIN + r * SPACING)
            end = (MARGIN + c * SPACING, MARGIN + (r + 1) * SPACING)
            pygame.draw.line(screen, gray, start, end, 2)

    for r in range(config.GRID_SIZE):
        for c in range(config.GRID_SIZE):
            if boxes[r][c] != 0:
                color = config.PLAYER_COLORS[boxes[r][c]]
                box_surface = pygame.Surface((SPACING, SPACING), pygame.SRCALPHA)
                faint_color = color + (60,)
                box_surface.fill(faint_color)
                screen.blit(box_surface, (MARGIN + c * SPACING, MARGIN + r * SPACING))

    for r in range(config.GRID_SIZE + 1):
        for c in range(config.GRID_SIZE):
            if h_lines[r][c] != 0:
                start = (MARGIN + c * SPACING, MARGIN + r * SPACING)
                end = (MARGIN + (c + 1) * SPACING, MARGIN + r * SPACING)
                pygame.draw.line(screen, config.PLAYER_COLORS[h_lines[r][c]], start, end, LINE_THICKNESS)
    for r in range(config.GRID_SIZE):
        for c in range(config.GRID_SIZE + 1):
            if v_lines[r][c] != 0:
                start = (MARGIN + c * SPACING, MARGIN + r * SPACING)
                end = (MARGIN + c * SPACING, MARGIN + (r + 1) * SPACING)
                pygame.draw.line(screen, config.PLAYER_COLORS[v_lines[r][c]], start, end, LINE_THICKNESS)

    for r in range(config.GRID_SIZE + 1):
        for c in range(config.GRID_SIZE + 1):
            center = (MARGIN + c * SPACING, MARGIN + r * SPACING)
            pygame.draw.circle(screen, (50, 50, 50), center, DOT_RADIUS)


# --- Main Game Loop ---
running = True
while running:
    # NEW: Calculate time_delta for pygame_gui animations
    time_delta = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # NEW: Pass all events to the UI manager first
        if ui_manager.process_events(event):
            pass

            # NEW: Check if the Settings button was clicked
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == settings_button:
                settings_window = SettingsWindow(ui_manager)

        # NEW: Check if the Settings window was closed
        if event.type == pygame_gui.UI_WINDOW_CLOSE:
            if settings_window and event.ui_element == settings_window.window:
                # For now, just print the values to the console to prove it works!
                print("--- SETTINGS SAVED ---")
                print(f"P1 Name: {settings_window.p1_name.get_text()}")
                print(f"P2 Name: {settings_window.p2_name.get_text()}")
                print(f"Grid X: {settings_window.grid_x.get_text()}, Grid Y: {settings_window.grid_y.get_text()}")
                print(f"Rules: {settings_window.rules.selected_option}")
                print(f"P1 Color: {settings_window.p1_color.selected_option}")
                print(f"P2 Color: {settings_window.p2_color.selected_option}")
                print("----------------------")
                settings_window = None

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                init_game_state()

        # Only allow board clicks if the game isn't over AND settings aren't open
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and not game_over and settings_window is None:
                line_clicked, boxes_completed = handle_click(event.pos)
                if line_clicked:
                    if boxes_completed == 0:
                        current_player = 2 if current_player == 1 else 1
                    total_boxes = config.GRID_SIZE * config.GRID_SIZE
                    score1 = sum(row.count(1) for row in boxes)
                    score2 = sum(row.count(2) for row in boxes)
                    if score1 + score2 == total_boxes:
                        game_over = True

    # 2. Drawing
    draw_board()

    score1 = sum(row.count(1) for row in boxes)
    score2 = sum(row.count(2) for row in boxes)

    p1_text = score_font.render(f"Player 1: {score1}", True, config.PLAYER_COLORS[1])
    screen.blit(p1_text, (MARGIN, 15))

    p2_text = score_font.render(f"Player 2: {score2}", True, config.PLAYER_COLORS[2])
    p2_rect = p2_text.get_rect(right=config.WINDOW_WIDTH - MARGIN, top=15)
    screen.blit(p2_text, p2_rect)

    if not game_over:
        text_color = config.PLAYER_COLORS[current_player]
        turn_surface = font.render(f"Player {current_player}'s Turn", True, text_color)
        turn_rect = turn_surface.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT - MARGIN // 2))
        screen.blit(turn_surface, turn_rect)

    if game_over:
        overlay = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        if score1 > score2:
            win_text = f"Player 1 Wins! ({score1} - {score2})"
            color = config.PLAYER_COLORS[1]
        elif score2 > score1:
            win_text = f"Player 2 Wins! ({score2} - {score1})"
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

    # NEW: Update and Draw the UI elements (Buttons, Windows, etc.)
    ui_manager.update(time_delta)
    ui_manager.draw_ui(screen)

    # 3. Update Display
    pygame.display.flip()

pygame.quit()
sys.exit()