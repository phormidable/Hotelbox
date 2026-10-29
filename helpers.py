# helpers.py
import math

def distance(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def get_midpoint(is_horizontal, row, col, offset_x, offset_y, spacing):
    if is_horizontal:
        x = offset_x + col * spacing + spacing // 2
        y = offset_y + row * spacing
    else:
        x = offset_x + col * spacing
        y = offset_y + row * spacing + spacing // 2
    return x, y