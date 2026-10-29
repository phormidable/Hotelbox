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
score_font = pygame.font.SysFont("arial", 28, bold=True)

# --- Layout Calculations ---
MARGIN = 50
SPACING = (config.WINDOW_WIDTH - 2 * MARGIN) // config.GRID_SIZE
DOT_RADIUS = 6
LINE_THICKNESS = 5
CLICK_THRESHOLD = SPACING / 2.5

# --- Game State ---
h_lines = [[0 for _ in range(config.GRID_SIZE)] for _ in range(config.GRID_SIZE + 1)]
v_lines = [[0 for _ in range(config.GRID_SIZE + 1)] for _ in range(config.GRID_SIZE)]

# NEW: Track which player completed which box.
# 0 = empty, 1 = Player 1, 2 = Player 2
boxes = [[0 for _ in range(config.GRID_SIZE)] for _ in range(config.GRID_SIZE)]

current_player = 1


# --- Helper Functions ---
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
    """Checks if all 4 sides of a specific box (r, c) are drawn."""
    return (h_lines[r][c] != 0 and
            h_lines[r + 1][c] != 0 and
            v_lines[r][c] != 0 and
            v_lines[r][c + 1] != 0)


def check_completed_boxes(is_horizontal, r, c):
    """
    Checks the boxes adjacent to the line just drawn.
    Returns the number of boxes completed.
    """
    completed_count = 0

    if is_horizontal:
        # Check the box ABOVE the line
        if r > 0 and is_box_complete(r - 1, c):
            if boxes[r - 1][c] == 0:  # Prevent double counting
                boxes[r - 1][c] = current_player
                completed_count += 1
        # Check the box BELOW the line
        if r < config.GRID_SIZE and is_box_complete(r, c):
            if boxes[r][c] == 0:
                boxes[r][c] = current_player
                completed_count += 1
    else:
        # Check the box to the LEFT of the line
        if c > 0 and is_box_complete(r, c - 1):
            if boxes[r][c - 1] == 0:
                boxes[r][c - 1] = current_player
                completed_count += 1
        # Check the box to the RIGHT of the line
        if c < config.GRID_SIZE and is_box_complete(r, c):
            if boxes[r][c] == 0:
                boxes[r][c] = current_player
                completed_count += 1

    return completed_count


def handle_click(mouse_pos):
    """Returns a tuple: (was_a_line_clicked, how_many_boxes_were_completed)"""
    global current_player

    # Check horizontal lines
    for r in range(config.GRID_SIZE + 1):
        for c in range(config.GRID_SIZE):
            if h_lines[r][c] == 0:
                mid = get_midpoint(True, r, c)
                if distance(mouse_pos, mid) < CLICK_THRESHOLD:
                    h_lines[r][c] = current_player
                    return True, check_completed_boxes(True, r, c)

    # Check vertical lines
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

    # 1. Draw empty segments (gray)
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

    # 2. Draw completed boxes (faint player colors)
    for r in range(config.GRID_SIZE):
        for c in range(config.GRID_SIZE):
            if boxes[r][c] != 0:
                color = config.PLAYER_COLORS[boxes[r][c]]
                # Create a transparent surface to draw a faint rectangle
                box_surface = pygame.Surface((SPACING, SPACING), pygame.SRCALPHA)
                faint_color = color + (60,)  # Add alpha transparency (60 out of 255)
                box_surface.fill(faint_color)

                rect_x = MARGIN + c * SPACING
                rect_y = MARGIN + r * SPACING
                screen.blit(box_surface, (rect_x, rect_y))

    # 3. Draw claimed segments (solid player colors)
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

    # 4. Draw dots (on top of everything)
    for r in range(config.GRID_SIZE + 1):
        for c in range(config.GRID_SIZE + 1):
            center = (MARGIN + c * SPACING, MARGIN + r * SPACING)
            pygame.draw.circle(screen, (50, 50, 50), center, DOT_RADIUS)


# --- Main Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                line_clicked, boxes_completed = handle_click(event.pos)

                if line_clicked:
                    # THE GOLDEN RULE OF DOTS AND BOXES:
                    # If you complete a box, you get another turn!
                    if boxes_completed == 0:
                        current_player = 2 if current_player == 1 else 1

    # 2. Drawing
    draw_board()

    # --- Draw UI: Scores at the top ---
    score1 = sum(row.count(1) for row in boxes)
    score2 = sum(row.count(2) for row in boxes)

    # Player 1 Score (Left aligned)
    p1_text = score_font.render(f"Player 1: {score1}", True, config.PLAYER_COLORS[1])
    screen.blit(p1_text, (MARGIN, 15))

    # Player 2 Score (Right aligned)
    p2_text = score_font.render(f"Player 2: {score2}", True, config.PLAYER_COLORS[2])
    p2_rect = p2_text.get_rect(right=config.WINDOW_WIDTH - MARGIN, top=15)
    screen.blit(p2_text, p2_rect)

    # --- Draw UI: Turn indicator at the bottom ---
    text_color = config.PLAYER_COLORS[current_player]
    turn_surface = font.render(f"Player {current_player}'s Turn", True, text_color)
    turn_rect = turn_surface.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT - MARGIN // 2))
    screen.blit(turn_surface, turn_rect)

    # 3. Update Display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()