"""
Cute & playful renderer for the N-Puzzle.
Rounded candy tiles, sparkles, bouncy animations.
"""

import math
import random
import pygame
from typing import List
from config import Colors, Layout, Animation
from models import Tile, PuzzleState, Sparkle


class Renderer:
    """Draws all puzzle UI elements with a cute theme."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.sparkles: List[Sparkle] = []
        self._frame = 0

        # Fonts — cute rounded style
        self.font_title      = pygame.font.SysFont("comicsansms", 48, bold=True)
        self.font_subtitle   = pygame.font.SysFont("comicsansms", 20)
        self.font_tile       = pygame.font.SysFont("comicsansms", 50, bold=True)
        self.font_button     = pygame.font.SysFont("comicsansms", 22, bold=True)
        self.font_overlay_lg = pygame.font.SysFont("comicsansms", 46, bold=True)
        self.font_overlay_sm = pygame.font.SysFont("comicsansms", 24)
        self.font_emoji      = pygame.font.SysFont("segoeuiemoji", 36)
        self.font_moves      = pygame.font.SysFont("comicsansms", 22, bold=True)

    # ── helpers ───────────────────────────────────────────────

    def _grid_origin(self) -> tuple:
        total_w = (
            Layout.GRID_SIZE * Layout.TILE_SIZE
            + (Layout.GRID_SIZE - 1) * Layout.TILE_GAP
        )
        x = (Layout.SCREEN_WIDTH - total_w) // 2
        y = Layout.GRID_TOP
        return x, y

    def tile_screen_pos(self, col: int, row: int) -> tuple:
        ox, oy = self._grid_origin()
        x = ox + col * (Layout.TILE_SIZE + Layout.TILE_GAP)
        y = oy + row * (Layout.TILE_SIZE + Layout.TILE_GAP)
        return float(x), float(y)

    def _center_text(self, font, text, color, cx, cy):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=(int(cx), int(cy)))
        self.screen.blit(surf, rect)

    def _draw_rounded_shadow(self, rect, radius, offset=4):
        shadow_rect = rect.move(offset, offset)
        pygame.draw.rect(
            self.screen, Colors.SHADOW,
            shadow_rect, border_radius=radius
        )

    # ── sparkle particles ─────────────────────────────────────

    def spawn_sparkles(self, cx: float, cy: float, count: int = 8):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1.5, 4.0)
            self.sparkles.append(Sparkle(
                x=cx, y=cy,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=1.0,
                size=random.uniform(3, 7),
                color=random.choice([
                    Colors.STAR_YELLOW,
                    Colors.ACCENT,
                    Colors.TILE_HINT,
                    (255, 200, 220),
                ])
            ))

    def update_sparkles(self):
        alive = []
        for s in self.sparkles:
            s.x += s.vx
            s.y += s.vy
            s.vy += 0.08       # gravity
            s.life -= 0.025
            if s.life > 0:
                alive.append(s)
        self.sparkles = alive

    def draw_sparkles(self):
        for s in self.sparkles:
            alpha = max(0, int(255 * s.life))
            size = max(1, int(s.size * s.life))
            surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)

            # Star shape = diamond
            points = [
                (size, 0),
                (size + size // 2, size),
                (size, size * 2),
                (size - size // 2, size),
            ]
            color_a = (*s.color, alpha)
            pygame.draw.polygon(surf, color_a, points)
            self.screen.blit(surf, (int(s.x) - size, int(s.y) - size))

    # ── background ────────────────────────────────────────────

    def draw_background(self):
        self._frame += 1
        self.screen.fill(Colors.BG_PRIMARY)

        # Soft wavy decoration at top
        for i in range(Layout.SCREEN_WIDTH):
            wave = math.sin((i + self._frame * 0.5) * 0.02) * 8
            height = int(90 + wave)
            pygame.draw.line(
                self.screen,
                Colors.BG_SECONDARY,
                (i, 0), (i, height)
            )

        # Floating dots decoration
        for i in range(6):
            bx = 80 + i * 95
            by = 50 + math.sin(self._frame * 0.03 + i) * 10
            size = 4 + (i % 3)
            pygame.draw.circle(
                self.screen, Colors.ACCENT, (int(bx), int(by)), size
            )

    # ── grid backing ──────────────────────────────────────────

    def draw_grid_backing(self):
        ox, oy = self._grid_origin()
        pad = Layout.GRID_PADDING
        total = (
            Layout.GRID_SIZE * Layout.TILE_SIZE
            + (Layout.GRID_SIZE - 1) * Layout.TILE_GAP
        )
        backing_rect = pygame.Rect(
            ox - pad, oy - pad,
            total + pad * 2, total + pad * 2
        )
        self._draw_rounded_shadow(backing_rect, Layout.GRID_RADIUS, 6)
        pygame.draw.rect(
            self.screen, Colors.BG_GRID,
            backing_rect, border_radius=Layout.GRID_RADIUS
        )

    # ── header ────────────────────────────────────────────────

    def draw_header(self, move_count: int, state: PuzzleState):
        cx = Layout.SCREEN_WIDTH // 2

        # Title with emoji
        self._center_text(
            self.font_emoji, "🧩",
            Colors.TEXT_DARK, cx - 130, Layout.TITLE_Y + 32
        )
        self._center_text(
            self.font_title, "N-Puzzle!",
            Colors.ACCENT_DARK, cx + 10, Layout.TITLE_Y + 30
        )
        self._center_text(
            self.font_emoji, "✨",
            Colors.STAR_YELLOW, cx + 140, Layout.TITLE_Y + 32
        )

        # Subtitle
        if state == PuzzleState.SHOWING_HINT:
            sub = "💡 Move the glowing tile!"
            color = Colors.ACCENT_DARK
        elif state == PuzzleState.SOLVED:
            sub = "🎉 You did it!"
            color = Colors.TILE_CORRECT
        else:
            sub = "Tap a tile next to the empty space~"
            color = Colors.TEXT_MUTED

        self._center_text(
            self.font_subtitle, sub, color,
            cx, Layout.SUBTITLE_Y + 10
        )

        # Move counter with star
        moves_str = f"⭐ Moves: {move_count}"
        self._center_text(
            self.font_moves, moves_str,
            Colors.TEXT_DARK, cx, Layout.MOVES_Y + 20
        )

    # ── single tile ───────────────────────────────────────────

    def draw_tile(
        self,
        tile: Tile,
        is_hovered: bool = False,
        is_hint: bool = False,
        is_correct: bool = False
    ):
        if tile.is_empty:
            # Draw cute dotted placeholder
            ox, oy = self._grid_origin()
            ex = ox + tile.grid_col * (Layout.TILE_SIZE + Layout.TILE_GAP)
            ey = oy + tile.grid_row * (Layout.TILE_SIZE + Layout.TILE_GAP)
            r = pygame.Rect(ex, ey, Layout.TILE_SIZE, Layout.TILE_SIZE)
            pygame.draw.rect(
                self.screen, Colors.SHADOW,
                r, width=2, border_radius=Layout.TILE_RADIUS
            )
            return

        x = tile.screen_x
        y = tile.screen_y + tile.bounce
        s = Layout.TILE_SIZE
        rad = Layout.TILE_RADIUS

        # Pick tile color
        base_color = Colors.TILE_COLORS[tile.value] if tile.value < len(Colors.TILE_COLORS) else Colors.TILE_1

        if is_hint:
            # Pulsing yellow glow
            pulse = 0.5 + 0.5 * math.sin(self._frame * 0.12)
            glow_size = int(8 + 6 * pulse)
            glow_surf = pygame.Surface(
                (s + glow_size * 2, s + glow_size * 2), pygame.SRCALPHA
            )
            alpha = int(100 + 80 * pulse)
            pygame.draw.rect(
                glow_surf,
                (*Colors.TILE_HINT, alpha),
                glow_surf.get_rect(),
                border_radius=rad + 6
            )
            self.screen.blit(glow_surf, (x - glow_size, y - glow_size))
            base_color = Colors.TILE_HINT

        # Shadow
        self._draw_rounded_shadow(
            pygame.Rect(x, y, s, s), rad, Layout.SHADOW_OFFSET
        )

        # Main tile body
        tile_rect = pygame.Rect(x, y, s, s)
        pygame.draw.rect(
            self.screen, base_color,
            tile_rect, border_radius=rad
        )

        # Inner highlight (top-left shine)
        shine_color = tuple(min(c + 50, 255) for c in base_color)
        shine_rect = pygame.Rect(x + 4, y + 4, s - 8, s // 3)
        shine_surf = pygame.Surface(shine_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            shine_surf,
            (*shine_color, 90),
            shine_surf.get_rect(),
            border_radius=rad - 2
        )
        self.screen.blit(shine_surf, shine_rect.topleft)

        # Hover white overlay
        if is_hovered:
            hover_surf = pygame.Surface((s, s), pygame.SRCALPHA)
            pygame.draw.rect(
                hover_surf,
                (*Colors.TILE_HOVER, 60),
                hover_surf.get_rect(),
                border_radius=rad
            )
            self.screen.blit(hover_surf, (x, y))

        # Correct position indicator — small star
        if is_correct and not is_hint:
            self._center_text(
                self.font_emoji, "✓",
                (255, 255, 255, 180),
                x + s - 18, y + 16
            )

        # Moving glow ring
        if tile.glow > 0.05:
            glow_surf = pygame.Surface((s + 16, s + 16), pygame.SRCALPHA)
            alpha = int(150 * tile.glow)
            pygame.draw.rect(
                glow_surf,
                (*Colors.ACCENT, alpha),
                glow_surf.get_rect(),
                width=3, border_radius=rad + 4
            )
            self.screen.blit(glow_surf, (x - 8, y - 8))

        # Tile number (with subtle shadow)
        num_str = str(tile.value)
        self._center_text(
            self.font_tile, num_str,
            (*Colors.TEXT_DARK, 60),
            x + s // 2 + 2, y + s // 2 + 2
        )
        self._center_text(
            self.font_tile, num_str,
            Colors.TEXT_LIGHT,
            x + s // 2, y + s // 2
        )

    # ── buttons ───────────────────────────────────────────────

    def draw_buttons(self, mouse_pos: tuple) -> dict:
        total_w = 2 * Layout.BUTTON_WIDTH + Layout.BUTTON_GAP
        start_x = (Layout.SCREEN_WIDTH - total_w) // 2
        y = Layout.BUTTON_Y

        rects = {}
        buttons = [
            ("🔄 New Game", "reset", start_x, Colors.BTN_PRIMARY),
            ("💡 Hint", "hint", start_x + Layout.BUTTON_WIDTH + Layout.BUTTON_GAP, Colors.BTN_SECONDARY),
        ]

        for label, key, bx, color in buttons:
            rect = pygame.Rect(bx, y, Layout.BUTTON_WIDTH, Layout.BUTTON_HEIGHT)
            hovered = rect.collidepoint(mouse_pos)

            btn_color = Colors.BTN_HOVER if hovered else color

            # Shadow
            self._draw_rounded_shadow(rect, Layout.BUTTON_RADIUS, 3)

            # Pill button
            pygame.draw.rect(
                self.screen, btn_color,
                rect, border_radius=Layout.BUTTON_RADIUS
            )

            # Shine
            shine = pygame.Rect(
                rect.x + 6, rect.y + 3,
                rect.width - 12, rect.height // 3
            )
            shine_surf = pygame.Surface(shine.size, pygame.SRCALPHA)
            pygame.draw.rect(
                shine_surf, (255, 255, 255, 50),
                shine_surf.get_rect(),
                border_radius=Layout.BUTTON_RADIUS
            )
            self.screen.blit(shine_surf, shine.topleft)

            # Label
            self._center_text(
                self.font_button, label,
                Colors.TEXT_LIGHT,
                rect.centerx, rect.centery
            )

            rects[key] = rect

        return rects

    # ── solved overlay ────────────────────────────────────────

    def draw_solved_overlay(self, move_count: int):
        # Dark overlay
        overlay = pygame.Surface(
            (Layout.SCREEN_WIDTH, Layout.SCREEN_HEIGHT),
            pygame.SRCALPHA
        )
        overlay.fill((*Colors.OVERLAY, 170))
        self.screen.blit(overlay, (0, 0))

        cx = Layout.SCREEN_WIDTH // 2
        cy = Layout.SCREEN_HEIGHT // 2

        # Big pulsing circle
        t = pygame.time.get_ticks()
        pulse = 0.5 + 0.5 * math.sin(t * Animation.PULSE_SPEED)
        radius = int(110 + 30 * pulse)
        glow_surf = pygame.Surface(
            (radius * 2, radius * 2), pygame.SRCALPHA
        )
        alpha = int(50 + 40 * pulse)
        pygame.draw.circle(
            glow_surf, (*Colors.ACCENT, alpha),
            (radius, radius), radius
        )
        self.screen.blit(glow_surf, (cx - radius, cy - radius - 20))

        # Trophy / celebration emojis
        bounce = math.sin(t * 0.005) * 8
        self._center_text(
            self.font_emoji, "🏆",
            Colors.STAR_YELLOW,
            cx, cy - 80 + bounce
        )

        # Text
        self._center_text(
            self.font_overlay_lg,
            "Puzzle Solved!",
            Colors.STAR_YELLOW,
            cx, cy - 20
        )
        self._center_text(
            self.font_overlay_sm,
            f"Completed in {move_count} moves ✨",
            Colors.TEXT_LIGHT,
            cx, cy + 30
        )
        self._center_text(
            self.font_subtitle,
            "Click 'New Game' to play again!",
            Colors.TEXT_MUTED,
            cx, cy + 70
        )

        # Draw sparkles on top
        self.draw_sparkles()