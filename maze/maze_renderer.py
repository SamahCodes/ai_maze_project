"""
Cute 2D maze renderer.
Draws walls as thick rounded blocks, floor as soft tiles,
decorations, player character, and goal marker.
"""

import math
import pygame
from typing import List, Tuple, Optional
from config.settings import GameColors, GameLayout


class MazeRenderer:
    """Renders the maze with cute 2D visuals."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.cell = GameLayout.CELL_SIZE
        self.ox = GameLayout.MAZE_OFFSET_X
        self.oy = GameLayout.MAZE_OFFSET_Y
        self._frame = 0

        # Fonts
        self.font_hud    = pygame.font.SysFont("comicsansms", 22, bold=True)
        self.font_small  = pygame.font.SysFont("comicsansms", 16)
        self.font_emoji  = pygame.font.SysFont("segoeuiemoji", 24)
        self.font_big    = pygame.font.SysFont("comicsansms", 40, bold=True)
        self.font_dir    = pygame.font.SysFont("comicsansms", 28, bold=True)

        # Pre-render wall texture surface
        self._wall_surface = None

    def _cell_rect(self, row: int, col: int) -> pygame.Rect:
        """Get screen rect for a grid cell."""
        return pygame.Rect(
            self.ox + col * self.cell,
            self.oy + row * self.cell,
            self.cell, self.cell
        )

    # ── background ────────────────────────────────────────────

    def draw_background(self):
        """Soft gradient background."""
        self._frame += 1
        self.screen.fill(GameColors.BG_PRIMARY)

        # Top decorative bar
        bar = pygame.Surface((GameLayout.SCREEN_WIDTH, 80), pygame.SRCALPHA)
        bar.fill((*GameColors.BG_SECONDARY, 180))
        self.screen.blit(bar, (0, 0))

        # Floating dots
        for i in range(8):
            bx = 60 + i * 110
            by = 35 + math.sin(self._frame * 0.025 + i * 0.8) * 6
            size = 3 + (i % 3)
            pygame.draw.circle(
                self.screen, GameColors.ACCENT,
                (int(bx), int(by)), size
            )

    # ── maze grid ─────────────────────────────────────────────

    def draw_maze(
        self,
        grid: List[List[int]],
        hint_direction: Optional[str] = None,
        player_pos: Optional[Tuple[int, int]] = None
    ):
        """Draw the full maze grid."""
        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 0

        for r in range(rows):
            for c in range(cols):
                cell_val = grid[r][c]
                rect = self._cell_rect(r, c)

                if cell_val == 1:
                    self._draw_wall(rect, r, c, grid)
                else:
                    self._draw_floor(rect, r, c)

                    if cell_val == 2:
                        self._draw_intersection(rect)
                    elif cell_val == 3:
                        self._draw_start_marker(rect)
                    elif cell_val == 4:
                        self._draw_goal(rect)

    def _draw_wall(
        self,
        rect: pygame.Rect,
        row: int, col: int,
        grid: List[List[int]]
    ):
        """Draw a cute rounded wall block."""
        # Main wall
        pygame.draw.rect(
            self.screen, GameColors.WALL_PRIMARY,
            rect, border_radius=6
        )

        # Top highlight
        highlight = pygame.Rect(rect.x + 2, rect.y + 2, rect.width - 4, rect.height // 3)
        h_surf = pygame.Surface(highlight.size, pygame.SRCALPHA)
        pygame.draw.rect(h_surf, (255, 255, 255, 40), h_surf.get_rect(), border_radius=4)
        self.screen.blit(h_surf, highlight.topleft)

        # Bottom shadow
        shadow = pygame.Rect(rect.x + 2, rect.y + rect.height * 2 // 3, rect.width - 4, rect.height // 3 - 2)
        s_surf = pygame.Surface(shadow.size, pygame.SRCALPHA)
        pygame.draw.rect(s_surf, (*GameColors.WALL_SHADOW, 50), s_surf.get_rect(), border_radius=4)
        self.screen.blit(s_surf, shadow.topleft)

    def _draw_floor(self, rect: pygame.Rect, row: int, col: int):
        """Draw checkerboard pastel floor."""
        color = GameColors.FLOOR if (row + col) % 2 == 0 else GameColors.FLOOR_ALT
        pygame.draw.rect(self.screen, color, rect)

        # Tiny dot pattern
        if (row + col) % 3 == 0:
            cx = rect.centerx
            cy = rect.centery
            pygame.draw.circle(self.screen, GameColors.BG_SECONDARY, (cx, cy), 2)

    def _draw_intersection(self, rect: pygame.Rect):
        """Draw intersection marker with pulse."""
        pulse = 0.5 + 0.5 * math.sin(self._frame * 0.06)
        size = int(8 + 4 * pulse)

        # Glow
        glow_surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
        alpha = int(40 + 30 * pulse)
        pygame.draw.circle(
            glow_surf, (*GameColors.INTERSECT_GLOW, alpha),
            (size * 2, size * 2), size * 2
        )
        self.screen.blit(
            glow_surf,
            (rect.centerx - size * 2, rect.centery - size * 2)
        )

        # Diamond
        cx, cy = rect.centerx, rect.centery
        points = [
            (cx, cy - size),
            (cx + size, cy),
            (cx, cy + size),
            (cx - size, cy),
        ]
        pygame.draw.polygon(self.screen, GameColors.INTERSECT_COLOR, points)
        pygame.draw.polygon(self.screen, GameColors.TEXT_LIGHT, points, 2)

    def _draw_start_marker(self, rect: pygame.Rect):
        """Draw start position marker."""
        pygame.draw.rect(
            self.screen, GameColors.PATH_CORRECT,
            rect, border_radius=4
        )
        text = self.font_small.render("S", True, GameColors.TEXT_DARK)
        tr = text.get_rect(center=rect.center)
        self.screen.blit(text, tr)

    def _draw_goal(self, rect: pygame.Rect):
        """Draw animated goal marker."""
        # Pulsing golden glow
        pulse = 0.5 + 0.5 * math.sin(self._frame * 0.08)
        glow_size = int(self.cell * 0.8 + 8 * pulse)
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        alpha = int(50 + 40 * pulse)
        pygame.draw.circle(
            glow_surf, (*GameColors.GOAL_GLOW, alpha),
            (glow_size, glow_size), glow_size
        )
        self.screen.blit(
            glow_surf,
            (rect.centerx - glow_size, rect.centery - glow_size)
        )

        # Star shape
        cx, cy = rect.centerx, rect.centery
        s = int(12 + 3 * pulse)
        star_points = []
        for i in range(10):
            angle = math.pi / 2 + i * math.pi / 5
            r = s if i % 2 == 0 else s // 2
            star_points.append((
                cx + int(r * math.cos(angle)),
                cy - int(r * math.sin(angle))
            ))
        pygame.draw.polygon(self.screen, GameColors.GOAL_PRIMARY, star_points)
        pygame.draw.polygon(self.screen, GameColors.GOAL_SECONDARY, star_points, 2)

    # ── player ────────────────────────────────────────────────

    def draw_player(
        self,
        screen_x: float,
        screen_y: float,
        facing: str = "right"
    ):
        """Draw cute character at pixel position."""
        cx = screen_x + self.cell // 2
        cy = screen_y + self.cell // 2
        radius = self.cell // 2 - 4

        # Body shadow
        pygame.draw.circle(
            self.screen, GameColors.SHADOW,
            (int(cx + 2), int(cy + 3)), radius
        )

        # Body
        pygame.draw.circle(
            self.screen, GameColors.PLAYER_PRIMARY,
            (int(cx), int(cy)), radius
        )

        # Shine
        shine_offset = radius // 3
        pygame.draw.circle(
            self.screen, GameColors.PLAYER_SECONDARY,
            (int(cx - shine_offset), int(cy - shine_offset)),
            radius // 3
        )

        # Eyes
        eye_offset_x = 5 if facing in ("right", "down") else -5
        eye_y = cy - 3

        # Left eye
        pygame.draw.circle(
            self.screen, GameColors.TEXT_LIGHT,
            (int(cx - 5), int(eye_y)), 4
        )
        pygame.draw.circle(
            self.screen, GameColors.PLAYER_EYE,
            (int(cx - 5 + eye_offset_x // 3), int(eye_y)), 2
        )

        # Right eye
        pygame.draw.circle(
            self.screen, GameColors.TEXT_LIGHT,
            (int(cx + 5), int(eye_y)), 4
        )
        pygame.draw.circle(
            self.screen, GameColors.PLAYER_EYE,
            (int(cx + 5 + eye_offset_x // 3), int(eye_y)), 2
        )

        # Cheeks
        pygame.draw.circle(
            self.screen, GameColors.PLAYER_CHEEK,
            (int(cx - 9), int(cy + 3)), 3
        )
        pygame.draw.circle(
            self.screen, GameColors.PLAYER_CHEEK,
            (int(cx + 9), int(cy + 3)), 3
        )

        # Smile
        smile_rect = pygame.Rect(cx - 4, cy + 2, 8, 6)
        pygame.draw.arc(
            self.screen, GameColors.PLAYER_EYE,
            smile_rect, 3.14, 2 * 3.14, 2
        )

    # ── HUD ───────────────────────────────────────────────────

    def draw_hud(
        self,
        moves: int,
        state_text: str,
        mouse_pos: tuple
    ) -> dict:
        """Draw top HUD bar. Returns button rects."""
        # HUD background
        hud_rect = pygame.Rect(0, 0, GameLayout.SCREEN_WIDTH, GameLayout.HUD_HEIGHT)
        pygame.draw.rect(self.screen, GameColors.BG_SECONDARY, hud_rect)
        pygame.draw.line(
            self.screen, GameColors.SHADOW,
            (0, GameLayout.HUD_HEIGHT),
            (GameLayout.SCREEN_WIDTH, GameLayout.HUD_HEIGHT), 2
        )

        # Title
        title = self.font_hud.render("🧩 AI Maze Adventure ✨", True, GameColors.ACCENT_DARK)
        self.screen.blit(title, (20, 10))

        # Moves
        moves_text = self.font_small.render(
            f"⭐ Steps: {moves}  |  {state_text}",
            True, GameColors.TEXT_DARK
        )
        self.screen.blit(moves_text, (20, 45))

        # Buttons
        rects = {}
        btn_x = GameLayout.SCREEN_WIDTH - 320

        buttons = [
            ("🔄 Reset", "reset", btn_x, GameColors.BTN_PRIMARY),
            ("💡 Ask AI", "ask_ai", btn_x + 160, GameColors.BTN_HINT),
        ]

        for label, key, bx, color in buttons:
            rect = pygame.Rect(
                bx, 18,
                GameLayout.BUTTON_WIDTH,
                GameLayout.BUTTON_HEIGHT
            )
            hovered = rect.collidepoint(mouse_pos)
            btn_color = GameColors.BTN_HOVER if hovered else color

            # Shadow
            pygame.draw.rect(
                self.screen, GameColors.SHADOW,
                rect.move(2, 2),
                border_radius=GameLayout.BUTTON_RADIUS
            )
            pygame.draw.rect(
                self.screen, btn_color, rect,
                border_radius=GameLayout.BUTTON_RADIUS
            )

            # Shine
            shine = pygame.Rect(rect.x + 4, rect.y + 2, rect.width - 8, rect.height // 3)
            s_surf = pygame.Surface(shine.size, pygame.SRCALPHA)
            pygame.draw.rect(s_surf, (255, 255, 255, 50), s_surf.get_rect(), border_radius=GameLayout.BUTTON_RADIUS)
            self.screen.blit(s_surf, shine.topleft)

            # Label
            text = self.font_small.render(label, True, GameColors.TEXT_LIGHT)
            tr = text.get_rect(center=rect.center)
            self.screen.blit(text, tr)

            rects[key] = rect

        return rects

    # ── direction popup ───────────────────────────────────────

    def draw_direction_popup(self, direction: str):
        """Show cute direction indicator."""
        overlay = pygame.Surface(
            (GameLayout.SCREEN_WIDTH, GameLayout.SCREEN_HEIGHT),
            pygame.SRCALPHA
        )
        overlay.fill((*GameColors.BG_DARK_OVERLAY, 150))
        self.screen.blit(overlay, (0, 0))

        cx = GameLayout.SCREEN_WIDTH // 2
        cy = GameLayout.SCREEN_HEIGHT // 2

        # Card background
        card = pygame.Rect(cx - 160, cy - 100, 320, 200)
        pygame.draw.rect(
            self.screen, GameColors.SHADOW,
            card.move(4, 4), border_radius=20
        )
        pygame.draw.rect(
            self.screen, GameColors.BG_PRIMARY,
            card, border_radius=20
        )
        pygame.draw.rect(
            self.screen, GameColors.ACCENT,
            card, width=3, border_radius=20
        )

        # Arrow emoji
        arrows = {
            "up": "⬆️", "down": "⬇️",
            "left": "⬅️", "right": "➡️"
        }
        arrow = arrows.get(direction, "❓")

        self._center_text(self.font_emoji, "🤖 AI says:", GameColors.TEXT_MUTED, cx, cy - 60)
        self._center_text(self.font_big, f"Go {direction.upper()}!", GameColors.ACCENT_DARK, cx, cy)

        # Bouncing arrow
        bounce = math.sin(self._frame * 0.1) * 8
        self._center_text(self.font_big, arrow, GameColors.TEXT_DARK, cx, cy + 55 + bounce)

        self._center_text(self.font_small, "Press any key to continue", GameColors.TEXT_MUTED, cx, cy + 90)

    def draw_win_screen(self, total_moves: int):
        """Draw victory overlay."""
        overlay = pygame.Surface(
            (GameLayout.SCREEN_WIDTH, GameLayout.SCREEN_HEIGHT),
            pygame.SRCALPHA
        )
        overlay.fill((*GameColors.BG_DARK_OVERLAY, 180))
        self.screen.blit(overlay, (0, 0))

        cx = GameLayout.SCREEN_WIDTH // 2
        cy = GameLayout.SCREEN_HEIGHT // 2

        # Pulsing circle
        pulse = 0.5 + 0.5 * math.sin(self._frame * 0.05)
        radius = int(120 + 30 * pulse)
        glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        alpha = int(50 + 40 * pulse)
        pygame.draw.circle(glow, (*GameColors.ACCENT, alpha), (radius, radius), radius)
        self.screen.blit(glow, (cx - radius, cy - radius - 20))

        bounce = math.sin(self._frame * 0.06) * 6

        self._center_text(self.font_emoji, "🏆", GameColors.STAR_YELLOW, cx, cy - 70 + bounce)
        self._center_text(self.font_big, "Maze Cleared!", GameColors.STAR_YELLOW, cx, cy - 20)
        self._center_text(self.font_hud, f"Total steps: {total_moves} ✨", GameColors.TEXT_LIGHT, cx, cy + 30)
        self._center_text(self.font_small, "Press R to play again!", GameColors.TEXT_MUTED, cx, cy + 70)

    def _center_text(self, font, text, color, cx, cy):
        surf = font.render(str(text), True, color)
        rect = surf.get_rect(center=(int(cx), int(cy)))
        self.screen.blit(surf, rect)