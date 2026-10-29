# main.py
import pygame
import sys
import math
import config

# --- Initialization ---
pygame.init()
screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
pygame.display.set_caption("Dots and Boxes")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 32, bold=True)

# --- Layout Calculations ---
# We want a 50px margin around the grid.
# 600px total - 100px margins = 500px for the grid.
# 500px / 10 boxes = 50px per box (SPACING).
MARGIN = 50
SPACING = (config.WINDOW_WIDTH - 2 * MARGIN) // config.GRID_SIZE
DOT_RADIUS = 6
LINE_THICKNESS = 5
CLICK_THRESHOLD = SPACING / 2.5  # How close the mouse must be to a line to claim it

# --- Game State ---
# We use two 2D arrays to track the lines.
# 0 = empty, 1 = Player 1, 2 = Player 2
# h_lines has 11 rows (y) and 10 columns (x)
h_lines = [[0 for _ in range(config.GRID_SIZE)] for _ in range(config.GRID_SIZE + 1)]
# v_lines has 10 rows (y) and 11 columns (x)
v_lines = [[0 for _ in range(config.GRID_SIZE + 1)] for _ in range(config.GRID_SIZE)]

current_player = 1


# --- Helper Functions ---
def get_midpoint(is_horizontal, row, col):
    """Calculates the center pixel coordinate of a specific segment."""
    if is_horizontal:
        x = MARGIN + col * SPACING + SPACING // 2
        y = MARGIN + row * SPACING
    else:
        x = MARGIN + col * SPACING
        y = MARGIN + row * SPACING + SPACING // 2
    return x, y


def distance(p1, p2):
    """Calculates distance between two (x,y) tuples."""
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def handle_click(mouse_pos):
    """Checks if a click is close enough to a line to claim it."""
    global current_player

    # Check horizontal lines
    for r in range(config.GRID_SIZE + 1):
        for c in range(config.GRID_SIZE):
            if h_lines[r][c] == 0:  # If line is free
                mid = get_midpoint(True, r, c)
                if distance(mouse_pos, mid) < CLICK_THRESHOLD:
                    h_lines[r][c] = current_player
                    return True  # Move was successful

    # Check vertical lines
    for r in range(config.GRID_SIZE):
        for c in range(config.GRID_SIZE + 1):
            if v_lines[r][c] == 0:  # If line is free
                mid = get_midpoint(False, r, c)
                if distance(mouse_pos, mid) < CLICK_THRESHOLD:
                    v_lines[r][c] = current_player
                    return True  # Move was successful

    return False  # Click was not on a valid free line


def draw_board():
    """Draws the dots, the empty gray lines, and the claimed colored lines."""
    screen.fill((240, 240, 240))  # Light gray background

    # Draw empty segments (gray)
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

    # Draw claimed segments (player colors)
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

    # Draw dots (drawn last so they sit on top of the lines)
    for r in range(config.GRID_SIZE + 1):
        for c in range(config.GRID_SIZE + 1):
            center = (MARGIN + c * SPACING, MARGIN + r * SPACING)
            pygame.draw.circle(screen, (50, 50, 50), center, DOT_RADIUS)


# --- Main Game Loop ---
running = True
while running:
    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if handle_click(event.pos):
                    # Note: In the real game, we only switch turns if the player
                    # DID NOT complete a box. For now, we just switch every turn.
                    current_player = 2 if current_player == 1 else 1

    # 2. Drawing
    draw_board()

    # Draw UI Text
    text_color = config.PLAYER_COLORS[current_player]
    text_surface = font.render(f"Player {current_player}'s Turn", True, text_color)
    # Center the text at the bottom margin
    text_rect = text_surface.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT - MARGIN // 2))
    screen.blit(text_surface, text_rect)

    # 3. Update Display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()