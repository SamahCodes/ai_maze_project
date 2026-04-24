"""
A* pathfinder for maze.
Fixed:
  - Returns RELATIVE directions (forward/left/right/back)
    based on player facing, not cardinal grid directions
  - Proper angle calculations
  - Full hint info with path length
"""

import math
import heapq
from typing import List, Tuple, Optional


class MazePathfinder:
    """A* maze solver with relative direction hints."""

    def __init__(self, grid: List[List[int]]):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows > 0 else 0

    def update_grid(self, grid: List[List[int]]):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows > 0 else 0

    def _walkable(self, r: int, c: int) -> bool:
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return self.grid[r][c] != 1
        return False

    def find_path(
        self,
        start: Tuple[int, int],
        goal: Tuple[int, int]
    ) -> Optional[List[Tuple[int, int]]]:
        """A* pathfinding with proper closed set."""
        if start == goal:
            return [start]

        counter = 0
        h = abs(start[0] - goal[0]) + abs(start[1] - goal[1])
        heap = [(h, counter, start)]
        counter += 1
        came_from = {}
        g_score = {start: 0}
        closed = set()

        while heap:
            f, _, current = heapq.heappop(heap)

            if current in closed:
                continue
            closed.add(current)

            if current == goal:
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path

            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nb = (current[0] + dr, current[1] + dc)
                if not self._walkable(nb[0], nb[1]):
                    continue
                if nb in closed:
                    continue
                ng = g_score[current] + 1
                if ng < g_score.get(nb, float('inf')):
                    came_from[nb] = current
                    g_score[nb] = ng
                    h = abs(nb[0] - goal[0]) + abs(nb[1] - goal[1])
                    heapq.heappush(heap, (ng + h, counter, nb))
                    counter += 1

        return None

    def _get_cardinal_direction(
        self,
        from_pos: Tuple[int, int],
        to_pos: Tuple[int, int]
    ) -> Optional[str]:
        """Get cardinal direction between adjacent cells."""
        dr = to_pos[0] - from_pos[0]
        dc = to_pos[1] - from_pos[1]
        if dr == -1 and dc == 0:
            return "up"
        if dr == 1 and dc == 0:
            return "down"
        if dr == 0 and dc == -1:
            return "left"
        if dr == 0 and dc == 1:
            return "right"
        return None

    def _cardinal_to_angle(self, cardinal: str) -> float:
        """
        Convert cardinal direction to angle.
        Matches player coordinate system:
          0      = right  (col increases)
          π/2    = down   (row increases)
          π      = left   (col decreases)
          3π/2   = up     (row decreases)
        """
        angle_map = {
            "right": 0.0,
            "down": math.pi / 2,
            "left": math.pi,
            "up": 3 * math.pi / 2,
        }
        return angle_map.get(cardinal, 0.0)

    def _cardinal_to_index(self, cardinal: str) -> int:
        """Cardinal to index: right=0, down=1, left=2, up=3."""
        return {"right": 0, "down": 1, "left": 2, "up": 3}.get(cardinal, 0)

    def _player_angle_to_index(self, player_angle: float) -> int:
        """
        Convert player angle to nearest cardinal index.
        0=right, 1=down, 2=left, 3=up
        """
        normalized = player_angle % (2 * math.pi)
        index = round(normalized / (math.pi / 2)) % 4
        return index

    def cardinal_to_relative(
        self, cardinal: str, player_angle: float
    ) -> str:
        """
        Convert cardinal direction to relative direction
        based on where the player is facing.

        Returns: 'FORWARD', 'RIGHT', 'LEFT', or 'BACK'
        """
        hint_idx = self._cardinal_to_index(cardinal)
        player_idx = self._player_angle_to_index(player_angle)

        # Relative = hint - player (mod 4)
        relative = (hint_idx - player_idx) % 4

        relative_map = {
            0: "FORWARD",
            1: "RIGHT",
            2: "BACK",
            3: "LEFT",
        }
        return relative_map[relative]

    def get_full_hint(
        self,
        player_row: int,
        player_col: int,
        goal_row: int,
        goal_col: int,
        player_angle: float = 0.0
    ) -> dict:
        """
        Get complete hint with both cardinal and relative directions.
        Returns dict with all hint info.
        """
        path = self.find_path(
            (player_row, player_col),
            (goal_row, goal_col)
        )

        if path is None:
            return {
                "cardinal": None,
                "relative": None,
                "angle": None,
                "path_length": -1,
                "found": False,
            }

        if len(path) < 2:
            return {
                "cardinal": None,
                "relative": "HERE",
                "angle": None,
                "path_length": 0,
                "found": True,
            }

        # Get cardinal direction of first step
        cardinal = self._get_cardinal_direction(path[0], path[1])

        if cardinal is None:
            return {
                "cardinal": None,
                "relative": None,
                "angle": None,
                "path_length": len(path) - 1,
                "found": False,
            }

        # Convert to angle for 3D light
        angle = self._cardinal_to_angle(cardinal)

        # Convert to relative direction based on player facing
        relative = self.cardinal_to_relative(cardinal, player_angle)

        return {
            "cardinal": cardinal,
            "relative": relative,
            "angle": angle,
            "path_length": len(path) - 1,
            "found": True,
        }