# game.py
import helpers
from model import GridModel


class Game:
    def __init__(self, grid_x: int, grid_y: int, rules: str):
        self.model = GridModel(grid_x, grid_y, rules)

    def reset(self, grid_x: int = None, grid_y: int = None, rules: str = None):
        self.model.reset(grid_x, grid_y, rules)

    def handle_click(self, mouse_pos: tuple, offset_x: int, offset_y: int, spacing: int, threshold: float) -> bool:
        """Returns True if a valid line was claimed."""
        # Check horizontal segments
        for r in range(self.model.grid_y + 1):
            for c in range(self.model.grid_x):
                segment = self.model.h_segments[r][c]
                if segment.owner == 0:
                    mid = segment.get_pixel_midpoint(offset_x, offset_y, spacing)
                    if helpers.distance(mouse_pos, mid) < threshold:
                        completed = self.model.claim_segment(True, r, c)
                        if completed == 0:
                            self.model.switch_turn()
                        if not self.model.has_free_segments():
                            self.model.game_over = True
                        return True

        # Check vertical segments
        for r in range(self.model.grid_y):
            for c in range(self.model.grid_x + 1):
                segment = self.model.v_segments[r][c]
                if segment.owner == 0:
                    mid = segment.get_pixel_midpoint(offset_x, offset_y, spacing)
                    if helpers.distance(mouse_pos, mid) < threshold:
                        completed = self.model.claim_segment(False, r, c)
                        if completed == 0:
                            self.model.switch_turn()
                        if not self.model.has_free_segments():
                            self.model.game_over = True
                        return True

        return False

    # Properties to expose model state
    @property
    def grid_x(self):
        return self.model.grid_x

    @property
    def grid_y(self):
        return self.model.grid_y

    @property
    def h_segments(self):
        return self.model.h_segments

    @property
    def v_segments(self):
        return self.model.v_segments

    @property
    def squares(self):
        return self.model.squares

    @property
    def points(self):
        return self.model.points

    @property
    def current_player(self):
        return self.model.current_player

    @property
    def game_over(self):
        return self.model.game_over

    def get_scores(self):
        return self.model.get_scores()