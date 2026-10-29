import math
from model import GridModel


class Game:
    def __init__(self, grid_x: int, grid_y: int, rules: str):
        self.model = GridModel(grid_x, grid_y, rules)

    def reset(self, grid_x: int = None, grid_y: int = None, rules: str = None):
        self.model.reset(grid_x, grid_y, rules)

    @property
    def is_over(self) -> bool:
        return self.model.game_over

    def handle_click(self, mouse_pos: tuple, offset_x: int, offset_y: int, spacing: int, threshold: float) -> bool:
        mx, my = mouse_pos
        dx = mx - offset_x
        dy = my - offset_y

        # Quick bounding box check to instantly reject clicks way outside the board
        if dx < -threshold or dy < -threshold or dx > self.model.grid_x * spacing + threshold or dy > self.model.grid_y * spacing + threshold:
            return False

        # 1. Find the closest horizontal segment candidate
        # Integer division gives the segment column, rounding gives the exact row
        c_h = int(max(0, min(dx // spacing, self.model.grid_x - 1)))
        r_h = int(max(0, min(round(dy / spacing), self.model.grid_y)))

        mx_h = offset_x + (c_h + 0.5) * spacing
        my_h = offset_y + r_h * spacing
        d_h = math.hypot(mx - mx_h, my - my_h)

        # 2. Find the closest vertical segment candidate
        # Rounding gives the exact column, integer division gives the segment row
        c_v = int(max(0, min(round(dx / spacing), self.model.grid_x)))
        r_v = int(max(0, min(dy // spacing, self.model.grid_y - 1)))

        mx_v = offset_x + c_v * spacing
        my_v = offset_y + (r_v + 0.5) * spacing
        d_v = math.hypot(mx - mx_v, my - my_v)

        # 3. Determine the target segment
        # Prefer horizontal on exact tie (matches original implicit bias), and check threshold
        if d_h <= d_v and d_h < threshold:
            seg = self.model.h_segments[r_h][c_h]
            if seg.owner == 0:
                completed = self.model.claim_segment(True, r_h, c_h)
                if completed == 0:
                    self.model.switch_turn()
                self.model.game_over = not self.model.has_free_segments()
                return True

        elif d_v < threshold:
            seg = self.model.v_segments[r_v][c_v]
            if seg.owner == 0:
                completed = self.model.claim_segment(False, r_v, c_v)
                if completed == 0:
                    self.model.switch_turn()
                self.model.game_over = not self.model.has_free_segments()
                return True

        return False