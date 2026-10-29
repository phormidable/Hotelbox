# game.py
import helpers

class Game:
    def __init__(self, grid_x, grid_y, rules):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.rules = rules
        self.reset()

    def reset(self, grid_x=None, grid_y=None, rules=None):
        if grid_x is not None: self.grid_x = grid_x
        if grid_y is not None: self.grid_y = grid_y
        if rules is not None: self.rules = rules

        self.h_lines = [[0 for _ in range(self.grid_x)] for _ in range(self.grid_y + 1)]
        self.v_lines = [[0 for _ in range(self.grid_x + 1)] for _ in range(self.grid_y)]
        self.boxes = [[0 for _ in range(self.grid_x)] for _ in range(self.grid_y)]
        self.current_player = 1
        self.game_over = False

    def _is_box_complete(self, r, c):
        top = self.h_lines[r][c]
        bottom = self.h_lines[r + 1][c]
        left = self.v_lines[r][c]
        right = self.v_lines[r][c + 1]

        if self.rules == "classic":
            return top != 0 and bottom != 0 and left != 0 and right != 0
        else:  # 4_sides
            return top != 0 and top == bottom == left == right

    def _check_completed_boxes(self, is_horizontal, r, c):
        completed_count = 0
        if is_horizontal:
            if r > 0 and self._is_box_complete(r - 1, c):
                if self.boxes[r - 1][c] == 0:
                    self.boxes[r - 1][c] = self.current_player
                    completed_count += 1
            if r < self.grid_y and self._is_box_complete(r, c):
                if self.boxes[r][c] == 0:
                    self.boxes[r][c] = self.current_player
                    completed_count += 1
        else:
            if c > 0 and self._is_box_complete(r, c - 1):
                if self.boxes[r][c - 1] == 0:
                    self.boxes[r][c - 1] = self.current_player
                    completed_count += 1
            if c < self.grid_x and self._is_box_complete(r, c):
                if self.boxes[r][c] == 0:
                    self.boxes[r][c] = self.current_player
                    completed_count += 1
        return completed_count

    def handle_click(self, mouse_pos, offset_x, offset_y, spacing, threshold):
        # Check horizontal lines
        for r in range(self.grid_y + 1):
            for c in range(self.grid_x):
                if self.h_lines[r][c] == 0:
                    mid = helpers.get_midpoint(True, r, c, offset_x, offset_y, spacing)
                    if helpers.distance(mouse_pos, mid) < threshold:
                        self.h_lines[r][c] = self.current_player
                        return True, self._check_completed_boxes(True, r, c)

        # Check vertical lines
        for r in range(self.grid_y):
            for c in range(self.grid_x + 1):
                if self.v_lines[r][c] == 0:
                    mid = helpers.get_midpoint(False, r, c, offset_x, offset_y, spacing)
                    if helpers.distance(mouse_pos, mid) < threshold:
                        self.v_lines[r][c] = self.current_player
                        return True, self._check_completed_boxes(False, r, c)

        return False, 0

    def has_free_segments(self):
        """Robust end-game check: works for both classic and 4_sides rules."""
        return (any(v == 0 for row in self.h_lines for v in row) or
                any(v == 0 for row in self.v_lines for v in row))

    def get_scores(self):
        score1 = sum(row.count(1) for row in self.boxes)
        score2 = sum(row.count(2) for row in self.boxes)
        return score1, score2

    def switch_turn(self):
        self.current_player = 2 if self.current_player == 1 else 1