# model.py

class Point:
    """Represents a dot in the grid."""

    def __init__(self, r: int, c: int):
        self.r = r
        self.c = c


class Segment:
    """Represents a line segment between two points."""

    def __init__(self, start: Point, end: Point, is_horizontal: bool):
        self.start = start
        self.end = end
        self.is_horizontal = is_horizontal
        self.owner = 0  # 0 = unclaimed, 1 = player 1, 2 = player 2

    def get_pixel_midpoint(self, offset_x: int, offset_y: int, spacing: int) -> tuple[int, int]:
        """Returns the pixel coordinates of this segment's midpoint."""
        if self.is_horizontal:
            x = offset_x + self.start.c * spacing + spacing // 2
            y = offset_y + self.start.r * spacing
        else:
            x = offset_x + self.start.c * spacing
            y = offset_y + self.start.r * spacing + spacing // 2
        return x, y


class Square:
    """Represents a box on the grid, with references to its 4 segments."""

    def __init__(self, top: Segment, bottom: Segment, left: Segment, right: Segment):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right
        self.completed_by = 0  # 0 = not complete, 1 = player 1, 2 = player 2

    @property
    def sides_drawn(self) -> bool:
        """True if all 4 sides have been claimed by anyone."""
        return (self.top.owner != 0 and self.bottom.owner != 0 and
                self.left.owner != 0 and self.right.owner != 0)

    @property
    def is_complete_classic(self) -> bool:
        """For classic rules: complete when all 4 sides are drawn."""
        return self.sides_drawn

    @property
    def is_complete_4_sides(self) -> bool:
        """For 4_sides rules: complete when all 4 sides belong to same player."""
        if not self.sides_drawn:
            return False
        owners = {self.top.owner, self.bottom.owner, self.left.owner, self.right.owner}
        return len(owners) == 1

    def is_complete(self, rules: str) -> bool:
        """Check if square is complete according to the given rules."""
        if rules == "classic":
            return self.is_complete_classic
        else:
            return self.is_complete_4_sides


class GridModel:
    """The core data model for the Dots and Boxes game."""

    def __init__(self, grid_x: int, grid_y: int, rules: str):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.rules = rules
        self.reset()

    def reset(self, grid_x: int = None, grid_y: int = None, rules: str = None):
        if grid_x is not None: self.grid_x = grid_x
        if grid_y is not None: self.grid_y = grid_y
        if rules is not None: self.rules = rules

        # Create points
        self.points = [[Point(r, c) for c in range(self.grid_x + 1)]
                       for r in range(self.grid_y + 1)]

        # Create horizontal segments
        self.h_segments = []
        for r in range(self.grid_y + 1):
            row = []
            for c in range(self.grid_x):
                seg = Segment(self.points[r][c], self.points[r][c + 1], is_horizontal=True)
                row.append(seg)
            self.h_segments.append(row)

        # Create vertical segments
        self.v_segments = []
        for r in range(self.grid_y):
            row = []
            for c in range(self.grid_x + 1):
                seg = Segment(self.points[r][c], self.points[r + 1][c], is_horizontal=False)
                row.append(seg)
            self.v_segments.append(row)

        # Create squares, wiring them to shared segments
        self.squares = []
        for r in range(self.grid_y):
            row = []
            for c in range(self.grid_x):
                top = self.h_segments[r][c]
                bottom = self.h_segments[r + 1][c]
                left = self.v_segments[r][c]
                right = self.v_segments[r][c + 1]
                square = Square(top, bottom, left, right)
                row.append(square)
            self.squares.append(row)

        self.current_player = 1
        self.game_over = False
        self.remaining_segments = (self.grid_y + 1) * self.grid_x + self.grid_y * (self.grid_x + 1)

    def claim_segment(self, is_horizontal: bool, r: int, c: int) -> int:
        """Claims a segment and returns number of squares completed."""
        if is_horizontal:
            segment = self.h_segments[r][c]
        else:
            segment = self.v_segments[r][c]

        if segment.owner != 0:
            return 0  # Already claimed

        segment.owner = self.current_player
        self.remaining_segments -= 1

        # Check adjacent squares
        completed_count = 0
        squares_to_check = []

        if is_horizontal:
            if r > 0: squares_to_check.append(self.squares[r - 1][c])
            if r < self.grid_y: squares_to_check.append(self.squares[r][c])
        else:
            if c > 0: squares_to_check.append(self.squares[r][c - 1])
            if c < self.grid_x: squares_to_check.append(self.squares[r][c])

        for square in squares_to_check:
            if square.completed_by == 0 and square.is_complete(self.rules):
                square.completed_by = self.current_player
                completed_count += 1

        return completed_count

    def has_free_segments(self) -> bool:
        """O(1) check using the counter."""
        return self.remaining_segments > 0

    def get_scores(self) -> tuple[int, int]:
        score1 = sum(1 for row in self.squares for square in row if square.completed_by == 1)
        score2 = sum(1 for row in self.squares for square in row if square.completed_by == 2)
        return score1, score2

    def switch_turn(self):
        self.current_player = 2 if self.current_player == 1 else 1