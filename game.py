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
        for is_h, segments in [(True, self.model.h_segments), (False, self.model.v_segments)]:
            for r, row in enumerate(segments):
                for c, seg in enumerate(row):
                    if seg.owner == 0:
                        mx, my = seg.get_pixel_midpoint(offset_x, offset_y, spacing)
                        if math.hypot(mouse_pos[0] - mx, mouse_pos[1] - my) < threshold:
                            completed = self.model.claim_segment(is_h, r, c)
                            if completed == 0:
                                self.model.switch_turn()
                            self.model.game_over = not self.model.has_free_segments()
                            return True
        return False