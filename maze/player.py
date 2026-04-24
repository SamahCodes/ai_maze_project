"""
First-person player controller.
Handles position, rotation, smooth movement, collision.
"""

import math
from typing import List
from config.settings import PlayerConfig, MazeConfig


class Player:
    """First-person maze player."""

    def __init__(self, x: float, y: float, angle: float = 0.0):
        self.x = x
        self.y = y
        self.angle = angle
        self.move_count = 0
        self.is_moving = False

        # Smooth movement
        self._vel_x = 0.0
        self._vel_y = 0.0
        self._vel_rot = 0.0

    def handle_input(self, keys, maze_grid: List[List[int]]):
        """Process keyboard input for movement."""
        speed = PlayerConfig.MOVE_SPEED
        rot = PlayerConfig.ROT_SPEED
        self.is_moving = False

        # Rotation
        if keys[119] if len(keys) > 119 else False:  # fallback
            pass

        import pygame
        pressed = pygame.key.get_pressed()

        # Rotation with left/right arrows
        if pressed[pygame.K_LEFT] or pressed[pygame.K_a]:
            self.angle -= rot
            self.is_moving = True
        if pressed[pygame.K_RIGHT] or pressed[pygame.K_d]:
            self.angle += rot
            self.is_moving = True

        # Forward/backward
        dx, dy = 0.0, 0.0
        if pressed[pygame.K_UP] or pressed[pygame.K_w]:
            dx += math.cos(self.angle) * speed
            dy += math.sin(self.angle) * speed
            self.is_moving = True
        if pressed[pygame.K_DOWN] or pressed[pygame.K_s]:
            dx -= math.cos(self.angle) * speed * 0.6
            dy -= math.sin(self.angle) * speed * 0.6
            self.is_moving = True

        # Strafe (Q/E)
        if pressed[pygame.K_q]:
            dx += math.cos(self.angle - math.pi/2) * speed * 0.6
            dy += math.sin(self.angle - math.pi/2) * speed * 0.6
            self.is_moving = True
        if pressed[pygame.K_e]:
            dx += math.cos(self.angle + math.pi/2) * speed * 0.6
            dy += math.sin(self.angle + math.pi/2) * speed * 0.6
            self.is_moving = True

        # Apply with collision
        if dx != 0 or dy != 0:
            self._move_with_collision(dx, dy, maze_grid)
            if abs(dx) > 0.001 or abs(dy) > 0.001:
                self.move_count += 1

        # Normalize angle
        self.angle %= (2 * math.pi)

    def _move_with_collision(
        self,
        dx: float, dy: float,
        grid: List[List[int]]
    ):
        """Move with wall collision detection."""
        r = PlayerConfig.COLLISION_RADIUS

        # Try X movement
        new_x = self.x + dx
        if not self._hits_wall(new_x, self.y, r, grid):
            self.x = new_x

        # Try Y movement
        new_y = self.y + dy
        if not self._hits_wall(self.x, new_y, r, grid):
            self.y = new_y

    def _hits_wall(
        self,
        x: float, y: float,
        r: float,
        grid: List[List[int]]
    ) -> bool:
        """Check if position + radius overlaps any wall."""
        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 0

        # Check corners of bounding box
        for cx, cy in [
            (x - r, y - r), (x + r, y - r),
            (x - r, y + r), (x + r, y + r)
        ]:
            mx, my = int(cx), int(cy)
            if mx < 0 or my < 0 or my >= rows or mx >= cols:
                return True
            if grid[my][mx] == 1:
                return True

        return False

    def get_grid_pos(self) -> tuple:
        """Return (row, col) grid position."""
        return (int(self.y), int(self.x))

    def is_at_cell(self, grid: List[List[int]], cell_type: int) -> bool:
        """Check if player is on a specific cell type."""
        row, col = self.get_grid_pos()
        if 0 <= row < len(grid) and 0 <= col < len(grid[0]):
            return grid[row][col] == cell_type
        return False

    def distance_to(self, tx: float, ty: float) -> float:
        """Distance to a target point."""
        return math.sqrt((self.x - tx)**2 + (self.y - ty)**2)

    def angle_to(self, tx: float, ty: float) -> float:
        """Angle from player to target."""
        return math.atan2(ty - self.y, tx - self.x)

    def reset(self, x: float, y: float, angle: float = 0.0):
        """Reset player state."""
        self.x = x
        self.y = y
        self.angle = angle
        self.move_count = 0
        self.is_moving = False