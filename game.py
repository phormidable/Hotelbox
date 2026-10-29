import math
from model import GridModel

class Game:
    def __init__(self, grid_x: int, grid_y: int, rules: str, extra_turn_on_square: bool):
        self.model = GridModel(grid_x, grid_y, rules, extra_turn_on_square)

    def reset(self, grid_x: int = None, grid_y: int = None, rules: str = None, extra_turn_on_square: bool = None):
        self.model.reset(grid_x, grid_y, rules, extra_turn_on_square)

    @property
    def is_over(self) -> bool:
        return self.model.game_over

    def get_hovered_segment(self, mouse_pos: tuple, offset_x: int, offset_y: int, spacing: int, threshold: float) -> tuple:
        """Returns (is_horizontal, r, c) of the hovered unclaimed segment, or None."""
        mx, my = mouse_pos
        dx = mx - offset_x
        dy = my - offset_y

        # Quick bounding box check
        if dx < -threshold or dy < -threshold or dx > self.model.grid_x * spacing + threshold or dy > self.model.grid_y * spacing + threshold:
            return None

        # 1. Closest horizontal segment candidate
        c_h = int(max(0, min(dx // spacing, self.model.grid_x - 1)))
        r_h = int(max(0, min(round(dy / spacing), self.model.grid_y)))
        mx_h = offset_x + (c_h + 0.5) * spacing
        my_h = offset_y + r_h * spacing
        d_h = math.hypot(mx - mx_h, my - my_h)

        # 2. Closest vertical segment candidate
        c_v = int(max(0, min(round(dx / spacing), self.model.grid_x)))
        r_v = int(max(0, min(dy // spacing, self.model.grid_y - 1)))
        mx_v = offset_x + c_v * spacing
        my_v = offset_y + (r_v + 0.5) * spacing
        d_v = math.hypot(mx - mx_v, my - my_v)

        # 3. Determine and validate the target segment
        if d_h <= d_v and d_h < threshold:
            if self.model.h_segments[r_h][c_h].owner == 0:
                return (True, r_h, c_h)
        elif d_v < threshold:
            if self.model.v_segments[r_v][c_v].owner == 0:
                return (False, r_v, c_v)

        return None

    def handle_click(self, mouse_pos: tuple, offset_x: int, offset_y: int, spacing: int, threshold: float) -> bool:
        hovered = self.get_hovered_segment(mouse_pos, offset_x, offset_y, spacing, threshold)
        if hovered:
            is_h, r, c = hovered
            completed = self.model.claim_segment(is_h, r, c)

            # Switch turn if no squares were completed OR if the extra turn rule is disabled
            if completed == 0 or not self.model.extra_turn_on_square:
                self.model.switch_turn()

            self.model.game_over = not self.model.has_free_segments()
            return True
        return False