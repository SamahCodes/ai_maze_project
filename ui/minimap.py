"""
Fog-of-war minimap.
Only shows cells the player has visited.
"""

import math
import pygame
from typing import List, Set, Tuple
from config.settings import Colors, Screen, UIConfig


class Minimap:
    """Tiny corner minimap with fog of war."""

    def __init__(self):
        self.visited: Set[Tuple[int, int]] = set()
        self.size = UIConfig.MINIMAP_SIZE
        self.margin = UIConfig.MINIMAP_MARGIN

    def reveal(self, row: int, col: int):
        """Mark a cell as visited."""
        self.visited.add((row, col))
        # Also reveal neighbors
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1),(0,0)]:
            self.visited.add((row+dr, col+dc))

    def reset(self):
        """Clear fog."""
        self.visited.clear()

    def draw(
        self,
        screen: pygame.Surface,
        grid: List[List[int]],
        player_row: int,
        player_col: int,
        player_angle: float,
        goal_row: int,
        goal_col: int
    ):
        """Draw minimap in bottom-right corner."""
        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 0
        if rows == 0 or cols == 0:
            return

        cell = max(2, self.size // max(rows, cols))
        map_w = cols * cell
        map_h = rows * cell

        # Create minimap surface
        surf = pygame.Surface((map_w + 4, map_h + 4), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))

        # Background
        bg_rect = pygame.Rect(0, 0, map_w + 4, map_h + 4)
        pygame.draw.rect(
            surf, (*Colors.BG_PRIMARY, UIConfig.MINIMAP_ALPHA),
            bg_rect, border_radius=8
        )

        # Draw cells
        for r in range(rows):
            for c in range(cols):
                rect = pygame.Rect(c * cell + 2, r * cell + 2, cell, cell)

                if (r, c) not in self.visited:
                    # Fog
                    pygame.draw.rect(surf, (*Colors.MINIMAP_FOG, 180), rect)
                    continue

                val = grid[r][c]
                if val == 1:
                    pygame.draw.rect(
                        surf, (*Colors.MINIMAP_WALL, 200), rect
                    )
                elif val == 4:
                    pygame.draw.rect(
                        surf, (*Colors.MINIMAP_GOAL, 220), rect
                    )
                else:
                    color = Colors.MINIMAP_VISITED if (r, c) in self.visited else Colors.MINIMAP_FLOOR
                    pygame.draw.rect(surf, (*color, 180), rect)

        # Player dot
        px = int(player_col * cell + 2 + cell // 2)
        py = int(player_row * cell + 2 + cell // 2)
        pygame.draw.circle(surf, Colors.MINIMAP_PLAYER, (px, py), cell)

        # Direction line
        dx = int(math.cos(player_angle) * cell * 2)
        dy = int(math.sin(player_angle) * cell * 2)
        pygame.draw.line(
            surf, Colors.TEXT_LIGHT,
            (px, py), (px + dx, py + dy), 2
        )

        # Goal marker (if visited)
        if (goal_row, goal_col) in self.visited:
            gx = int(goal_col * cell + 2 + cell // 2)
            gy = int(goal_row * cell + 2 + cell // 2)
            pygame.draw.circle(surf, Colors.MINIMAP_GOAL, (gx, gy), cell)

        # Border
        pygame.draw.rect(
            surf, (*Colors.ACCENT, 150),
            bg_rect, width=2, border_radius=8
        )

        # Position on screen
        dest_x = Screen.WIDTH - map_w - self.margin - 4
        dest_y = Screen.HEIGHT - map_h - self.margin - 4
        screen.blit(surf, (dest_x, dest_y))