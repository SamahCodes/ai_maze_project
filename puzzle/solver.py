"""
A* solver with Manhattan Distance for 3x3 N-Puzzle.
Fixed:
  - get_hint returns correct tile to click (not empty position)
  - Proper solvability check
  - Clean A* with no duplicate processing
"""

import heapq
from typing import List, Tuple, Optional

GRID = 3

# Goal positions: value -> (col, row)
# value 1 at (0,0), value 2 at (1,0), ... value 8 at (1,2), value 0 at (2,2)
GOAL_POSITIONS = {}
for v in range(1, GRID * GRID):
    r, c = divmod(v - 1, GRID)
    GOAL_POSITIONS[v] = (c, r)
GOAL_POSITIONS[0] = (GRID - 1, GRID - 1)


def _state_to_tuple(state: List[List[int]]) -> tuple:
    """Convert 2D grid to hashable tuple."""
    return tuple(val for row in state for val in row)


def _tuple_to_state(t: tuple) -> List[List[int]]:
    """Convert tuple back to 2D grid."""
    return [list(t[i * GRID:(i + 1) * GRID]) for i in range(GRID)]


def _find_empty(state: List[List[int]]) -> Tuple[int, int]:
    """Find (row, col) of empty tile (value 0)."""
    for r in range(GRID):
        for c in range(GRID):
            if state[r][c] == 0:
                return r, c
    return -1, -1


def manhattan_distance(state: List[List[int]]) -> int:
    """Total Manhattan distance for all tiles."""
    total = 0
    for r in range(GRID):
        for c in range(GRID):
            val = state[r][c]
            if val != 0:
                goal_c, goal_r = GOAL_POSITIONS[val]
                total += abs(r - goal_r) + abs(c - goal_c)
    return total


def is_solvable(flat: List[int]) -> bool:
    """
    Check if flat puzzle list is solvable.
    For 3x3: solvable if inversion count is even.
    """
    inversions = 0
    nums = [x for x in flat if x != 0]
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] > nums[j]:
                inversions += 1
    return inversions % 2 == 0


def solve(state: List[List[int]]) -> Optional[List[List[List[int]]]]:
    """
    Full A* solve.
    Returns list of states from start to goal, or None.
    Uses closed set to prevent revisiting.
    """
    start_tuple = _state_to_tuple(state)
    goal_tuple = _state_to_tuple([[1, 2, 3], [4, 5, 6], [7, 8, 0]])

    if start_tuple == goal_tuple:
        return [state]

    # (f_score, g_score, counter, state_tuple, path)
    counter = 0
    h = manhattan_distance(state)
    open_set = [(h, 0, counter, start_tuple, [start_tuple])]
    counter += 1
    closed = set()

    while open_set:
        f, g, _, current_tuple, path = heapq.heappop(open_set)

        if current_tuple in closed:
            continue
        closed.add(current_tuple)

        if current_tuple == goal_tuple:
            return [_tuple_to_state(s) for s in path]

        current_state = _tuple_to_state(current_tuple)
        er, ec = _find_empty(current_state)

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = er + dr, ec + dc
            if 0 <= nr < GRID and 0 <= nc < GRID:
                new_state = [row[:] for row in current_state]
                new_state[er][ec], new_state[nr][nc] = (
                    new_state[nr][nc], new_state[er][ec]
                )
                new_tuple = _state_to_tuple(new_state)

                if new_tuple not in closed:
                    new_g = g + 1
                    new_h = manhattan_distance(new_state)
                    new_f = new_g + new_h
                    new_path = path + [new_tuple]
                    heapq.heappush(
                        open_set,
                        (new_f, new_g, counter, new_tuple, new_path)
                    )
                    counter += 1

    return None


def get_hint(state: List[List[int]]) -> Optional[Tuple[int, int]]:
    """
    Get the tile that should be clicked next.
    Returns (col, row) of the tile to move, or None.

    Logic:
      1. Solve the puzzle to get optimal path
      2. Compare current state with next state
      3. Find which tile moved (the one that swapped with empty)
      4. Return that tile's position in the CURRENT state
    """
    solution = solve(state)

    if solution is None or len(solution) < 2:
        return None

    current = state
    next_state = solution[1]

    # Find where empty cell IS in current state
    cur_empty_r, cur_empty_c = _find_empty(current)

    # Find where empty cell IS in next state
    next_empty_r, next_empty_c = _find_empty(next_state)

    # The tile that moved is the one that WAS at the next-empty position
    # in the CURRENT state. That's because in the next state, that position
    # became empty (the tile moved away from there into the old empty spot).

    # So the tile to click is at (next_empty_r, next_empty_c) in CURRENT state
    tile_value = current[next_empty_r][next_empty_c]

    # Verify this tile is adjacent to empty (sanity check)
    dr = abs(next_empty_r - cur_empty_r)
    dc = abs(next_empty_c - cur_empty_c)
    if dr + dc != 1:
        # Something wrong, fallback
        return None

    # Return as (col, row) to match our tile coordinate system
    return (next_empty_c, next_empty_r)