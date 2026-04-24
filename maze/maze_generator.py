"""
Maze generator using Recursive Backtracking.
Grid values:
    0 = floor
    1 = wall
    2 = intersection
    3 = start
    4 = goal
"""

import random
from typing import List, Tuple


class MazeGenerator:
    """Generates a random perfect maze."""

    def __init__(self, rows: int, cols: int):
        self.rows = rows if rows % 2 == 1 else rows + 1
        self.cols = cols if cols % 2 == 1 else cols + 1
        self.grid: List[List[int]] = []
        self.start = (1, 1)
        self.goal = (self.rows - 2, self.cols - 2)
        self.intersections: List[Tuple[int, int]] = []

    def generate(self) -> List[List[int]]:
        """Generate maze and return grid."""
        self.grid = [
            [1 for _ in range(self.cols)]
            for _ in range(self.rows)
        ]
        self._carve(1, 1)
        self.grid[self.start[0]][self.start[1]] = 3
        self.grid[self.goal[0]][self.goal[1]] = 4
        self._find_intersections()
        return self.grid

    def _carve(self, row: int, col: int):
        """Recursive backtracking."""
        self.grid[row][col] = 0
        directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        random.shuffle(directions)

        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if (0 < nr < self.rows - 1
                    and 0 < nc < self.cols - 1
                    and self.grid[nr][nc] == 1):
                self.grid[row + dr // 2][col + dc // 2] = 0
                self._carve(nr, nc)

    def _find_intersections(self):
        """Mark cells with 3+ open neighbors."""
        self.intersections = []
        for r in range(1, self.rows - 1):
            for c in range(1, self.cols - 1):
                if self.grid[r][c] in (0, 3, 4):
                    opens = sum(
                        1 for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]
                        if self.grid[r+dr][c+dc] != 1
                    )
                    if opens >= 3:
                        self.intersections.append((r, c))
                        if self.grid[r][c] == 0:
                            self.grid[r][c] = 2

    def get_start_pos(self) -> Tuple[float, float]:
        """Player start as (x, y) float coords."""
        return (self.start[1] + 0.5, self.start[0] + 0.5)

    def get_goal_pos(self) -> Tuple[float, float]:
        """Goal as (x, y) float coords."""
        return (self.goal[1] + 0.5, self.goal[0] + 0.5)