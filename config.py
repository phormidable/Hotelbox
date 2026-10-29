# config.py

# Window settings
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600

# Grid settings (Now independent X and Y)
GRID_X = 4
GRID_Y = 4

# Player settings
PLAYER_NAMES = {1: "Player 1", 2: "Player 2"}
# config.py

PLAYER_COLOR_CHOICES = {
    "Green":  (34, 139, 34),
    "Blue":   (30, 144, 255),
    "Red":    (255, 0, 0),
    "Purple": (128, 0, 128),
    "Orange": (255, 165, 0),
    "Cyan":   (0, 255, 255),
}

COLOR_NAME_BY_RGB = {rgb: name for name, rgb in PLAYER_COLOR_CHOICES.items()}

PLAYER_COLORS = {1: PLAYER_COLOR_CHOICES["Green"],
                 2: PLAYER_COLOR_CHOICES["Blue"]}

# Rules: "classic" or "4_sides"
RULES = "4_sides"