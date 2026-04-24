"""
HUD with compass indicator showing player facing direction.
"""

import math
import pygame
from config.settings import Colors, Screen, UIConfig, GameStates


class HUD:
    """Game HUD with buttons, status, and compass."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self._frame = 0

        self.font_title = pygame.font.SysFont("comicsansms", 24, bold=True)
        self.font_status = pygame.font.SysFont("comicsansms", 16)
        self.font_btn = pygame.font.SysFont("comicsansms", 17, bold=True)
        self.font_compass = pygame.font.SysFont("comicsansms", 12, bold=True)
        self.font_compass_dir = pygame.font.SysFont("comicsansms", 10)

    def draw(
        self,
        moves: int,
        game_state: str,
        mouse_pos: tuple,
        at_intersection: bool = False,
        player_angle: float = 0.0
    ) -> dict:
        """Draw HUD, return button rects."""
        self._frame += 1
        rects = {}

        # Background bar
        bar = pygame.Surface(
            (Screen.WIDTH, UIConfig.HUD_HEIGHT), pygame.SRCALPHA
        )
        bar.fill((*Colors.BG_SECONDARY, 230))
        self.screen.blit(bar, (0, 0))

        # Border
        pygame.draw.line(
            self.screen, Colors.SHADOW,
            (0, UIConfig.HUD_HEIGHT),
            (Screen.WIDTH, UIConfig.HUD_HEIGHT), 2
        )

        # Floating dots decoration
        for i in range(10):
            bx = 50 + i * 95
            by = 12 + math.sin(self._frame * 0.03 + i * 0.7) * 4
            pygame.draw.circle(
                self.screen, Colors.ACCENT, (int(bx), int(by)), 3
            )

        # Title
        title = self.font_title.render(
            "🧩 AI Maze Adventure ✨", True, Colors.ACCENT_DARK
        )
        self.screen.blit(title, (20, 18))

        # Status text
        status_map = {
            GameStates.MAZE_EXPLORE: "🚶 Explore the maze...",
            GameStates.AT_INTERSECTION: "💎 Intersection! Click 'Ask AI'",
            GameStates.PUZZLE_ACTIVE: "🧩 Solve the puzzle!",
            GameStates.SHOW_DIRECTION: "🤖 AI shows the way!",
            GameStates.GAME_WON: "🏆 You escaped!",
        }
        status = status_map.get(game_state, "")

        if at_intersection:
            pulse = 0.5 + 0.5 * math.sin(self._frame * 0.12)
            color = (
                int(Colors.ACCENT_DARK[0] * (0.7 + 0.3 * pulse)),
                int(Colors.ACCENT_DARK[1] * (0.7 + 0.3 * pulse)),
                int(Colors.ACCENT_DARK[2] * (0.7 + 0.3 * pulse)),
            )
        else:
            color = Colors.TEXT_MUTED

        self.screen.blit(
            self.font_status.render(status, True, color), (20, 50)
        )

        # Moves counter
        self.screen.blit(
            self.font_status.render(
                f"⭐ Steps: {moves}", True, Colors.TEXT_DARK
            ),
            (Screen.WIDTH // 2 - 40, 50)
        )

        # Compass
        self._draw_compass(player_angle)

        # Buttons
        btn_x = Screen.WIDTH - 310
        buttons = [
            ("🔄 Reset", "reset", btn_x, Colors.BTN_PRIMARY),
            ("💡 Ask AI", "ask_ai", btn_x + 155, Colors.BTN_HINT),
        ]

        for label, key, bx, base_color in buttons:
            rect = pygame.Rect(
                bx, 22, UIConfig.BTN_WIDTH, UIConfig.BTN_HEIGHT
            )
            hovered = rect.collidepoint(mouse_pos)

            enabled = True
            if key == "ask_ai" and not at_intersection:
                enabled = False

            if not enabled:
                btn_color = Colors.SHADOW
            elif hovered:
                btn_color = Colors.BTN_HOVER
            else:
                btn_color = base_color

            # Shadow
            pygame.draw.rect(
                self.screen, Colors.SHADOW,
                rect.move(2, 2), border_radius=UIConfig.BTN_RADIUS
            )
            # Button body
            pygame.draw.rect(
                self.screen, btn_color, rect,
                border_radius=UIConfig.BTN_RADIUS
            )
            # Shine
            shine = pygame.Rect(
                rect.x + 4, rect.y + 2,
                rect.width - 8, rect.height // 3
            )
            s = pygame.Surface(shine.size, pygame.SRCALPHA)
            pygame.draw.rect(
                s, (255, 255, 255, 45),
                s.get_rect(), border_radius=UIConfig.BTN_RADIUS
            )
            self.screen.blit(s, shine.topleft)
            # Label
            text = self.font_btn.render(label, True, Colors.TEXT_LIGHT)
            self.screen.blit(text, text.get_rect(center=rect.center))

            rects[key] = rect

        return rects

    def _draw_compass(self, player_angle: float):
        """Draw a cute circular compass showing facing direction."""
        cx = Screen.WIDTH // 2 + 60
        cy = 30
        radius = 22

        # Background circle
        pygame.draw.circle(
            self.screen, (*Colors.BG_PRIMARY, 220), (cx, cy), radius + 2
        )
        pygame.draw.circle(
            self.screen, Colors.ACCENT, (cx, cy), radius + 2, 2
        )

        # Direction labels (N/S/E/W relative to grid)
        dirs = [
            ("E", 0.0),
            ("S", math.pi / 2),
            ("W", math.pi),
            ("N", 3 * math.pi / 2),
        ]
        for label, angle in dirs:
            lx = cx + int(math.cos(angle) * (radius - 6))
            ly = cy + int(math.sin(angle) * (radius - 6))
            text = self.font_compass_dir.render(
                label, True, Colors.TEXT_MUTED
            )
            self.screen.blit(
                text,
                text.get_rect(center=(lx, ly))
            )

        # Player direction arrow
        arrow_len = radius - 4
        ax = cx + int(math.cos(player_angle) * arrow_len)
        ay = cy + int(math.sin(player_angle) * arrow_len)

        # Arrow line
        pygame.draw.line(
            self.screen, Colors.ACCENT_DARK,
            (cx, cy), (ax, ay), 3
        )

        # Arrow tip
        pygame.draw.circle(
            self.screen, Colors.ACCENT_DARK, (ax, ay), 4
        )

        # Center dot
        pygame.draw.circle(
            self.screen, Colors.BTN_HINT, (cx, cy), 3
        )

        # Facing label
        facing = self._angle_to_facing(player_angle)
        face_text = self.font_compass.render(
            facing, True, Colors.TEXT_DARK
        )
        self.screen.blit(
            face_text,
            face_text.get_rect(center=(cx, cy + radius + 12))
        )

    def _angle_to_facing(self, angle: float) -> str:
        """Convert angle to human-readable facing."""
        normalized = angle % (2 * math.pi)
        index = round(normalized / (math.pi / 4)) % 8

        facings = ["E", "SE", "S", "SW", "W", "NW", "N", "NE"]
        return facings[index]