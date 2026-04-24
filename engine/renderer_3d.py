"""
3D first-person renderer.
Fixed:
  - Correct hint light direction
  - Trophy/goal rendering in 3D
  - Better visual effects
"""

import math
import pygame
from typing import List, Optional, Tuple
from config.settings import Colors, Raycasting, PlayerConfig
from engine.raycaster import RayHit


class Renderer3D:
    """Pseudo-3D first-person renderer with goal trophy."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self._frame = 0
        self.head_bob = 0.0
        self._is_moving = False

        self.viewport = pygame.Surface(
            (Raycasting.RENDER_WIDTH, Raycasting.RENDER_HEIGHT)
        )
        self.col_width = max(
            1, Raycasting.RENDER_WIDTH // Raycasting.NUM_RAYS
        )

        self.font_emoji = pygame.font.SysFont("segoeuiemoji", 28)
        self.font_trophy_lg = pygame.font.SysFont("segoeuiemoji", 60)
        self.font_trophy_md = pygame.font.SysFont("segoeuiemoji", 40)
        self.font_trophy_sm = pygame.font.SysFont("segoeuiemoji", 24)
        self.font_label = pygame.font.SysFont("comicsansms", 16, bold=True)

    def set_moving(self, moving: bool):
        self._is_moving = moving

    def render_scene(
        self,
        rays: List[RayHit],
        hint_direction: Optional[str] = None,
        hint_angle: Optional[float] = None,
        player_angle: float = 0.0,
        at_intersection: bool = False,
        near_goal: bool = False,
        goal_distance: float = 999.0,
        goal_angle: Optional[float] = None,
        relative_direction: Optional[str] = None,
    ):
        """Render full 3D scene."""
        self._frame += 1
        self.viewport.fill((0, 0, 0))

        if self._is_moving:
            self.head_bob = (
                math.sin(self._frame * PlayerConfig.BOB_SPEED)
                * PlayerConfig.BOB_AMOUNT
            )
        else:
            self.head_bob *= 0.9
            if abs(self.head_bob) < 0.1:
                self.head_bob = 0.0

        self._draw_ceiling()
        self._draw_floor()
        self._draw_walls(rays)

        # Draw trophy at goal if visible
        if goal_angle is not None and goal_distance < 15:
            self._draw_trophy(
                goal_angle, player_angle,
                goal_distance, rays
            )

        # Draw hint light
        if hint_angle is not None:
            self._draw_hint_light(
                hint_angle, player_angle,
                relative_direction
            )

        if near_goal:
            self._draw_goal_glow(goal_distance)

        if at_intersection:
            self._draw_intersection_marker()

        self._draw_vignette()
        self.screen.blit(self.viewport, (0, Raycasting.RENDER_TOP))

    def _clamp_y(self, y: int) -> int:
        return max(0, min(Raycasting.RENDER_HEIGHT - 1, y))

    # ── ceiling & floor ───────────────────────────────────────

    def _draw_ceiling(self):
        h = Raycasting.RENDER_HEIGHT // 2
        for y in range(h):
            t = y / h
            r = int(Colors.CEILING_FAR[0] +
                    (Colors.CEILING_NEAR[0] - Colors.CEILING_FAR[0]) * t)
            g = int(Colors.CEILING_FAR[1] +
                    (Colors.CEILING_NEAR[1] - Colors.CEILING_FAR[1]) * t)
            b = int(Colors.CEILING_FAR[2] +
                    (Colors.CEILING_NEAR[2] - Colors.CEILING_FAR[2]) * t)
            yy = self._clamp_y(int(y + self.head_bob))
            pygame.draw.line(
                self.viewport, (r, g, b),
                (0, yy), (Raycasting.RENDER_WIDTH, yy)
            )

    def _draw_floor(self):
        h = Raycasting.RENDER_HEIGHT // 2
        for y in range(h):
            t = y / h
            r = int(Colors.FLOOR_FAR[0] +
                    (Colors.FLOOR_NEAR[0] - Colors.FLOOR_FAR[0]) * t)
            g = int(Colors.FLOOR_FAR[1] +
                    (Colors.FLOOR_NEAR[1] - Colors.FLOOR_FAR[1]) * t)
            b = int(Colors.FLOOR_FAR[2] +
                    (Colors.FLOOR_NEAR[2] - Colors.FLOOR_FAR[2]) * t)
            sy = self._clamp_y(
                int(Raycasting.RENDER_HEIGHT - y - 1 + self.head_bob)
            )
            pygame.draw.line(
                self.viewport, (r, g, b),
                (0, sy), (Raycasting.RENDER_WIDTH, sy)
            )

    # ── walls ─────────────────────────────────────────────────

    def _draw_walls(self, rays: List[RayHit]):
        center_y = Raycasting.RENDER_HEIGHT // 2

        for i, hit in enumerate(rays):
            if hit.distance >= Raycasting.MAX_DEPTH:
                continue

            wall_h = min(
                Raycasting.RENDER_HEIGHT * 2,
                int(Raycasting.RENDER_HEIGHT / (hit.distance + 0.0001))
            )
            top = int(center_y - wall_h // 2 + self.head_bob)
            x = i * self.col_width
            shade = min(1.0, hit.distance / Raycasting.MAX_DEPTH)

            if hit.side == 0:
                base = Colors.WALL_NEAR
            else:
                base = (
                    int(Colors.WALL_NEAR[0] * 0.78),
                    int(Colors.WALL_NEAR[1] * 0.78),
                    int(Colors.WALL_NEAR[2] * 0.78),
                )

            r = max(0, min(255, int(base[0] * (1 - shade * 0.7))))
            g = max(0, min(255, int(base[1] * (1 - shade * 0.7))))
            b = max(0, min(255, int(base[2] * (1 - shade * 0.7))))
            color = (r, g, b)

            wall_rect = pygame.Rect(x, top, self.col_width + 1, wall_h)
            pygame.draw.rect(self.viewport, color, wall_rect)

            if wall_h > 10:
                highlight = (
                    min(255, color[0] + 35),
                    min(255, color[1] + 35),
                    min(255, color[2] + 35),
                )
                pygame.draw.line(
                    self.viewport, highlight,
                    (x, max(0, top)),
                    (x + self.col_width, max(0, top)), 2
                )

            if i > 0 and abs(rays[i - 1].distance - hit.distance) > 0.5:
                edge = (
                    max(0, color[0] - 30),
                    max(0, color[1] - 30),
                    max(0, color[2] - 30),
                )
                bottom = top + wall_h
                pygame.draw.line(
                    self.viewport, edge,
                    (x, max(0, top)),
                    (x, min(Raycasting.RENDER_HEIGHT, bottom)), 2
                )

    # ── trophy at goal ────────────────────────────────────────

    def _draw_trophy(
        self,
        goal_angle: float,
        player_angle: float,
        distance: float,
        rays: List[RayHit]
    ):
        """Draw a trophy/star at the goal position in 3D space."""
        # Angle difference
        diff = goal_angle - player_angle
        while diff > math.pi:
            diff -= 2 * math.pi
        while diff < -math.pi:
            diff += 2 * math.pi

        # Only draw if within FOV
        if abs(diff) > Raycasting.HALF_FOV * 0.95:
            return

        # Screen X position
        normalized = diff / Raycasting.FOV
        screen_x = int(
            Raycasting.RENDER_WIDTH / 2
            + normalized * Raycasting.RENDER_WIDTH
        )

        # Check if wall is blocking the trophy
        ray_index = int(
            (diff + Raycasting.HALF_FOV) / Raycasting.FOV
            * Raycasting.NUM_RAYS
        )
        ray_index = max(0, min(len(rays) - 1, ray_index))
        if rays[ray_index].distance < distance * 0.9:
            return  # Wall is closer, trophy hidden

        # Size based on distance (closer = bigger)
        base_size = max(20, min(120, int(200 / (distance + 0.5))))

        # Vertical position (centered, slight bob)
        center_y = Raycasting.RENDER_HEIGHT // 2
        trophy_y = int(center_y - base_size // 3 + self.head_bob)

        # Pulsing glow behind trophy
        pulse = 0.5 + 0.5 * math.sin(self._frame * 0.06)
        glow_r = int(base_size * 1.5 + base_size * 0.5 * pulse)
        glow_alpha = int(30 + 25 * pulse)

        glow_surf = pygame.Surface(
            (glow_r * 2, glow_r * 2), pygame.SRCALPHA
        )
        # Multiple glow layers
        for layer in range(5):
            r = glow_r - layer * (glow_r // 5)
            a = min(255, glow_alpha + layer * 8)
            if r > 0:
                pygame.draw.circle(
                    glow_surf,
                    (255, 223, 100, a),
                    (glow_r, glow_r), r
                )
        self.viewport.blit(
            glow_surf,
            (screen_x - glow_r, trophy_y - glow_r + base_size // 2)
        )

        # Draw star shape
        star_size = base_size // 2
        self._draw_star(
            screen_x, trophy_y + base_size // 4,
            star_size, (255, 223, 100), (255, 200, 60)
        )

        # Trophy emoji on top (pick size based on distance)
        if distance < 3:
            font = self.font_trophy_lg
        elif distance < 6:
            font = self.font_trophy_md
        else:
            font = self.font_trophy_sm

        trophy_surf = font.render("🏆", True, (255, 223, 100))
        self.viewport.blit(
            trophy_surf,
            (screen_x - trophy_surf.get_width() // 2,
             trophy_y - trophy_surf.get_height() // 4)
        )

        # "EXIT" label below
        if distance < 8:
            shade = max(0, 1.0 - distance / 8.0)
            label_alpha = int(200 * shade)
            label = self.font_label.render("EXIT", True, (255, 255, 255))
            label_y = trophy_y + base_size
            # Simple alpha blit
            label_surf = pygame.Surface(label.get_size(), pygame.SRCALPHA)
            label_surf.blit(label, (0, 0))
            label_surf.set_alpha(label_alpha)
            self.viewport.blit(
                label_surf,
                (screen_x - label.get_width() // 2, label_y)
            )

    def _draw_star(self, cx, cy, size, color, outline_color):
        """Draw a 5-pointed star."""
        points = []
        for i in range(10):
            angle = -math.pi / 2 + i * math.pi / 5
            r = size if i % 2 == 0 else size // 2
            points.append((
                int(cx + r * math.cos(angle)),
                int(cy + r * math.sin(angle))
            ))
        if len(points) >= 3:
            pygame.draw.polygon(self.viewport, color, points)
            pygame.draw.polygon(self.viewport, outline_color, points, 2)

    # ── hint light ────────────────────────────────────────────

    def _draw_hint_light(
        self,
        hint_angle: float,
        player_angle: float,
        relative_direction: Optional[str] = None
    ):
        """
        Draw golden light in the correct direction.
        Both angles are in [0, 2π].
        """
        diff = hint_angle - player_angle

        # Normalize to [-π, π]
        while diff > math.pi:
            diff -= 2 * math.pi
        while diff < -math.pi:
            diff += 2 * math.pi

        # Only render if within extended FOV
        if abs(diff) > Raycasting.HALF_FOV * 1.5:
            # If direction is behind, show arrow at screen edge
            if relative_direction:
                self._draw_edge_indicator(diff, relative_direction)
            return

        # Screen X position
        normalized = diff / Raycasting.FOV
        screen_x = int(
            Raycasting.RENDER_WIDTH / 2
            + normalized * Raycasting.RENDER_WIDTH
        )
        screen_x = max(30, min(Raycasting.RENDER_WIDTH - 30, screen_x))

        # Pulsing glow
        pulse = 0.5 + 0.5 * math.sin(self._frame * 0.08)
        radius = int(50 + 25 * pulse)
        alpha = int(50 + 40 * pulse)

        glow_surf = pygame.Surface(
            (radius * 2, radius * 2), pygame.SRCALPHA
        )
        for layer in range(5):
            r = radius - layer * (radius // 5)
            a = min(255, alpha + layer * 12)
            if r > 0:
                pygame.draw.circle(
                    glow_surf,
                    (*Colors.LIGHT_HINT, a),
                    (radius, radius), r
                )

        center_y = Raycasting.RENDER_HEIGHT // 3
        self.viewport.blit(
            glow_surf,
            (screen_x - radius, center_y - radius)
        )

        # Sparkle
        sparkle = self.font_emoji.render("✨", True, Colors.LIGHT_HINT)
        self.viewport.blit(
            sparkle,
            (screen_x - sparkle.get_width() // 2,
             Raycasting.RENDER_HEIGHT // 2 - 50)
        )

        # Light beam on floor
        beam_w = int(radius * 0.8)
        beam_h = Raycasting.RENDER_HEIGHT // 3
        beam_surf = pygame.Surface((beam_w, beam_h), pygame.SRCALPHA)
        beam_alpha = int(15 + 12 * pulse)
        beam_surf.fill((*Colors.LIGHT_HINT, beam_alpha))
        self.viewport.blit(
            beam_surf,
            (screen_x - beam_w // 2, Raycasting.RENDER_HEIGHT // 2)
        )

        # Direction label in 3D view
        if relative_direction:
            label = self.font_label.render(
                f"← {relative_direction} →",
                True, Colors.LIGHT_HINT
            )
            self.viewport.blit(
                label,
                (screen_x - label.get_width() // 2,
                 Raycasting.RENDER_HEIGHT // 2 - 80)
            )

    def _draw_edge_indicator(self, diff: float, direction: str):
        """Draw arrow at screen edge when hint is behind player."""
        pulse = 0.5 + 0.5 * math.sin(self._frame * 0.1)
        alpha = int(120 + 80 * pulse)

        if diff > 0:
            # Hint is to the right
            x = Raycasting.RENDER_WIDTH - 50
            arrow = "→"
        else:
            # Hint is to the left
            x = 50
            arrow = "←"

        y = Raycasting.RENDER_HEIGHT // 2

        # Arrow background
        bg = pygame.Surface((80, 40), pygame.SRCALPHA)
        pygame.draw.rect(
            bg, (*Colors.LIGHT_HINT, int(alpha * 0.4)),
            bg.get_rect(), border_radius=10
        )
        self.viewport.blit(bg, (x - 40, y - 20))

        # Arrow text
        arrow_surf = self.font_label.render(
            f"{arrow} {direction}",
            True, Colors.LIGHT_HINT
        )
        self.viewport.blit(
            arrow_surf,
            (x - arrow_surf.get_width() // 2,
             y - arrow_surf.get_height() // 2)
        )

    # ── effects ───────────────────────────────────────────────

    def _draw_goal_glow(self, distance: float):
        intensity = max(0.0, 1.0 - distance / 5.0)
        if intensity <= 0:
            return
        pulse = 0.5 + 0.5 * math.sin(self._frame * 0.06)
        alpha = int((30 + 40 * pulse) * intensity)
        overlay = pygame.Surface(
            (Raycasting.RENDER_WIDTH, Raycasting.RENDER_HEIGHT),
            pygame.SRCALPHA
        )
        overlay.fill((*Colors.LIGHT_GOAL, alpha))
        self.viewport.blit(overlay, (0, 0))

    def _draw_intersection_marker(self):
        pulse = 0.5 + 0.5 * math.sin(self._frame * 0.1)
        alpha = int(20 + 25 * pulse)
        overlay = pygame.Surface(
            (Raycasting.RENDER_WIDTH, Raycasting.RENDER_HEIGHT),
            pygame.SRCALPHA
        )
        border = 25
        w = Raycasting.RENDER_WIDTH
        h = Raycasting.RENDER_HEIGHT
        for i in range(border):
            a = int(alpha * (1 - i / border))
            if a <= 0:
                continue
            c = (*Colors.BTN_HINT, a)
            pygame.draw.line(overlay, c, (0, i), (w, i))
            pygame.draw.line(overlay, c, (0, h - i), (w, h - i))
            pygame.draw.line(overlay, c, (i, 0), (i, h))
            pygame.draw.line(overlay, c, (w - i, 0), (w - i, h))
        self.viewport.blit(overlay, (0, 0))

    def _draw_vignette(self):
        vignette = pygame.Surface(
            (Raycasting.RENDER_WIDTH, Raycasting.RENDER_HEIGHT),
            pygame.SRCALPHA
        )
        w = Raycasting.RENDER_WIDTH
        h = Raycasting.RENDER_HEIGHT
        for cx, cy in [(0, 0), (w, 0), (0, h), (w, h)]:
            for r in range(0, 200, 12):
                a = int(25 * (1 - r / 200))
                if a > 0:
                    pygame.draw.circle(
                        vignette, (0, 0, 0, a),
                        (cx, cy), 200 - r
                    )
        self.viewport.blit(vignette, (0, 0))