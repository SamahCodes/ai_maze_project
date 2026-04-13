"""
A* solver with Manhattan Distance heuristic for the N-Puzzle.
Provides full solve path and single-step hints.
"""

import heapq
from typing import List, Tuple, Optional


GRID = 3

GOAL_POSITIONS = {}
for v in range(1, GRID * GRID):
    r, c = divmod(v - 1, GRID)
    GOAL_POSITIONS[v] = (c, r)
GOAL_POSITIONS[0] = (GRID - 1, GRID - 1)


def _state_to_tuple(state: List[List[int]]) -> tuple:
    return tuple(val for row in state for val in row)


def _tuple_to_state(t: tuple) -> List[List[int]]:
    return [list(t[i * GRID:(i + 1) * GRID]) for i in range(GRID)]


def _find_empty(state: List[List[int]]) -> Tuple[int, int]:
    for r in range(GRID):
        for c in range(GRID):
            if state[r][c] == 0:
                return r, c
    return -1, -1


def manhattan_distance(state: List[List[int]]) -> int:
    total = 0
    for r in range(GRID):
        for c in range(GRID):
            val = state[r][c]
            if val != 0:
                goal_c, goal_r = GOAL_POSITIONS[val]
                total += abs(r - goal_r) + abs(c - goal_c)
    return total


def is_solvable(flat: List[int]) -> bool:
    inversions = 0
    nums = [x for x in flat if x != 0]
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] > nums[j]:
                inversions += 1
    return inversions % 2 == 0


def solve(state: List[List[int]]) -> Optional[List[List[List[int]]]]:
    start = _state_to_tuple(state)
    goal = _state_to_tuple([
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 0]
    ])

    if start == goal:
        return [state]

    open_set = []
    heapq.heappush(open_set, (manhattan_distance(state), 0, start, [start]))
    visited = {start}

    while open_set:
        f, g, current, path = heapq.heappop(open_set)
        current_state = _tuple_to_state(current)
        er, ec = _find_empty(current_state)

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = er + dr, ec + dc
            if 0 <= nr < GRID and 0 <= nc < GRID:
                new_state = [row[:] for row in current_state]
                new_state[er][ec], new_state[nr][nc] = (
                    new_state[nr][nc], new_state[er][ec]
                )
                new_tuple = _state_to_tuple(new_state)

                if new_tuple not in visited:
                    visited.add(new_tuple)
                    new_g = g + 1
                    new_f = new_g + manhattan_distance(new_state)
                    new_path = path + [new_tuple]

                    if new_tuple == goal:
                        return [_tuple_to_state(s) for s in new_path]

                    heapq.heappush(
                        open_set,
                        (new_f, new_g, new_tuple, new_path)
                    )

    return None


def get_hint(state: List[List[int]]) -> Optional[Tuple[int, int]]:
    solution = solve(state)
    if solution is None or len(solution) < 2:
        return None

    current = state
    next_state = solution[1]
    er, ec = _find_empty(current)
    ner, nec = _find_empty(next_state)

    return (nec, ner)   # (col, row) of tile to click