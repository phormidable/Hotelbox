# config.py

# Window settings
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600

# Grid defaults
GRID_DEFAULT_X = 4
GRID_DEFAULT_Y = 4

# Player defaults
DEFAULT_PLAYER_NAMES = {1: "Player 1", 2: "Player 2"}

PLAYER_COLOR_CHOICES = {
    "Green":  (34, 139, 34),
    "Blue":   (30, 144, 255),
    "Red":    (255, 0, 0),
    "Purple": (128, 0, 128),
    "Orange": (255, 165, 0),
    "Yellow":   (0, 255, 255),
}

COLOR_NAME_BY_RGB = {rgb: name for name, rgb in PLAYER_COLOR_CHOICES.items()}

DEFAULT_PLAYER_COLORS = {
    1: PLAYER_COLOR_CHOICES["Green"],
    2: PLAYER_COLOR_CHOICES["Blue"]
}

# Rules default
DEFAULT_RULES = "4_sides"

# Visual constants
LINE_THICKNESS = 5
DOT_RADIUS = 6

# Layout constants
TOP_MARGIN = 90
BOTTOM_MARGIN = 60