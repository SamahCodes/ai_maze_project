"""
Raycasting engine.
Casts rays from player position to detect walls,
calculates wall distances and hit info for 3D rendering.
"""

import math
from typing import List, Tuple, Optional
from config.settings import Raycasting, MazeConfig


class RayHit:
    """Result of a single ray cast."""

    __slots__ = [
        'distance', 'wall_x', 'side',
        'map_x', 'map_y', 'angle'
    ]

    def __init__(self):
        self.distance: float = Raycasting.MAX_DEPTH
        self.wall_x: float = 0.0      # Where on wall (0-1) for texturing
        self.side: int = 0             # 0=vertical hit, 1=horizontal hit
        self.map_x: int = 0
        self.map_y: int = 0
        self.angle: float = 0.0


class Raycaster:
    """DDA raycasting engine."""

    def __init__(self, maze_grid: List[List[int]]):
        self.grid = maze_grid
        self.rows = len(maze_grid)
        self.cols = len(maze_grid[0]) if self.rows > 0 else 0

    def update_grid(self, maze_grid: List[List[int]]):
        """Update maze grid reference."""
        self.grid = maze_grid
        self.rows = len(maze_grid)
        self.cols = len(maze_grid[0]) if self.rows > 0 else 0

    def is_wall(self, mx: int, my: int) -> bool:
        """Check if map cell is a wall."""
        if 0 <= my < self.rows and 0 <= mx < self.cols:
            return self.grid[my][mx] == 1
        return True

    def cast_rays(
        self,
        px: float, py: float,
        angle: float
    ) -> List[RayHit]:
        """
        Cast all rays from player position.
        Returns list of RayHit objects.
        """
        rays = []
        start_angle = angle - Raycasting.HALF_FOV
        angle_step = Raycasting.FOV / Raycasting.NUM_RAYS

        for i in range(Raycasting.NUM_RAYS):
            ray_angle = start_angle + i * angle_step
            hit = self._cast_single_ray(px, py, ray_angle, angle)
            rays.append(hit)

        return rays

    def _cast_single_ray(
        self,
        px: float, py: float,
        ray_angle: float,
        player_angle: float
    ) -> RayHit:
        """Cast a single ray using DDA algorithm."""
        hit = RayHit()
        hit.angle = ray_angle

        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)

        # Prevent division by zero
        if abs(cos_a) < 1e-8:
            cos_a = 1e-8
        if abs(sin_a) < 1e-8:
            sin_a = 1e-8

        # Current map cell
        map_x = int(px)
        map_y = int(py)

        # Ray direction deltas
        delta_dist_x = abs(1.0 / cos_a)
        delta_dist_y = abs(1.0 / sin_a)

        # Step direction and initial side distances
        if cos_a > 0:
            step_x = 1
            side_dist_x = (map_x + 1.0 - px) * delta_dist_x
        else:
            step_x = -1
            side_dist_x = (px - map_x) * delta_dist_x

        if sin_a > 0:
            step_y = 1
            side_dist_y = (map_y + 1.0 - py) * delta_dist_y
        else:
            step_y = -1
            side_dist_y = (py - map_y) * delta_dist_y

        # DDA loop
        depth = 0
        side = 0

        while depth < Raycasting.MAX_DEPTH:
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
                depth += 1
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1
                depth += 1

            if self.is_wall(map_x, map_y):
                # Calculate exact distance
                if side == 0:
                    perp_dist = (
                        map_x - px + (1 - step_x) / 2
                    ) / cos_a
                else:
                    perp_dist = (
                        map_y - py + (1 - step_y) / 2
                    ) / sin_a

                # Fix fisheye distortion
                perp_dist *= math.cos(ray_angle - player_angle)
                perp_dist = max(perp_dist, 0.05)

                # Wall X coordinate (for texture mapping)
                if side == 0:
                    wall_x = py + perp_dist * sin_a
                else:
                    wall_x = px + perp_dist * cos_a
                wall_x -= math.floor(wall_x)

                hit.distance = perp_dist
                hit.wall_x = wall_x
                hit.side = side
                hit.map_x = map_x
                hit.map_y = map_y
                break

        return hit

    def cast_single(
        self,
        px: float, py: float,
        angle: float
    ) -> float:
        """Cast single ray, return distance. For AI light."""
        hit = self._cast_single_ray(px, py, angle, angle)
        return hit.distance