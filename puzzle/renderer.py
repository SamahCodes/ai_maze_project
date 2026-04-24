"""
Cute puzzle renderer with sparkles and animations.
"""

import math
import random
import pygame
from typing import List
from puzzle.config import Colors, Layout, Animation
from puzzle.models import Tile, PuzzleState, Sparkle


class Renderer:
    """Draws puzzle UI elements."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.sparkles: List[Sparkle] = []
        self._frame = 0

        self.font_title      = pygame.font.SysFont("comicsansms", 42, bold=True)
        self.font_subtitle   = pygame.font.SysFont("comicsansms", 18)
        self.font_tile       = pygame.font.SysFont("comicsansms", 44, bold=True)
        self.font_button     = pygame.font.SysFont("comicsansms", 20, bold=True)
        self.font_overlay_lg = pygame.font.SysFont("comicsansms", 40, bold=True)
        self.font_overlay_sm = pygame.font.SysFont("comicsansms", 22)
        self.font_emoji      = pygame.font.SysFont("segoeuiemoji", 30)
        self.font_moves      = pygame.font.SysFont("comicsansms", 20, bold=True)

    def _grid_origin(self) -> tuple:
        total_w = Layout.GRID_SIZE * Layout.TILE_SIZE + (Layout.GRID_SIZE - 1) * Layout.TILE_GAP
        x = (Layout.SCREEN_WIDTH - total_w) // 2
        return x, Layout.GRID_TOP

    def tile_screen_pos(self, col: int, row: int) -> tuple:
        ox, oy = self._grid_origin()
        return float(ox + col * (Layout.TILE_SIZE + Layout.TILE_GAP)), float(oy + row * (Layout.TILE_SIZE + Layout.TILE_GAP))

    def _center_text(self, font, text, color, cx, cy):
        surf = font.render(str(text), True, color)
        rect = surf.get_rect(center=(int(cx), int(cy)))
        self.screen.blit(surf, rect)

    def _draw_rounded_shadow(self, rect, radius, offset=4):
        shadow_rect = rect.move(offset, offset)
        pygame.draw.rect(self.screen, Colors.SHADOW, shadow_rect, border_radius=radius)

    # Sparkles
    def spawn_sparkles(self, cx, cy, count=8):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1.5, 4.0)
            self.sparkles.append(Sparkle(
                x=cx, y=cy,
                vx=math.cos(angle) * speed, vy=math.sin(angle) * speed,
                life=1.0, size=random.uniform(3, 7),
                color=random.choice([Colors.STAR_YELLOW, Colors.ACCENT, Colors.TILE_HINT, (255, 200, 220)])
            ))

    def update_sparkles(self):
        alive = []
        for s in self.sparkles:
            s.x += s.vx
            s.y += s.vy
            s.vy += 0.08
            s.life -= 0.025
            if s.life > 0:
                alive.append(s)
        self.sparkles = alive

    def draw_sparkles(self):
        for s in self.sparkles:
            alpha = max(0, int(255 * s.life))
            size = max(1, int(s.size * s.life))
            surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            points = [(size, 0), (size + size // 2, size), (size, size * 2), (size - size // 2, size)]
            pygame.draw.polygon(surf, (*s.color, alpha), points)
            self.screen.blit(surf, (int(s.x) - size, int(s.y) - size))

    # Background
    def draw_background(self):
        self._frame += 1
        self.screen.fill(Colors.BG_PRIMARY)
        for i in range(Layout.SCREEN_WIDTH):
            wave = math.sin((i + self._frame * 0.5) * 0.02) * 8
            h = int(80 + wave)
            pygame.draw.line(self.screen, Colors.BG_SECONDARY, (i, 0), (i, h))
        for i in range(8):
            bx = 60 + i * 115
            by = 40 + math.sin(self._frame * 0.03 + i) * 8
            pygame.draw.circle(self.screen, Colors.ACCENT, (int(bx), int(by)), 3 + i % 3)

    def draw_grid_backing(self):
        ox, oy = self._grid_origin()
        pad = Layout.GRID_PADDING
        total = Layout.GRID_SIZE * Layout.TILE_SIZE + (Layout.GRID_SIZE - 1) * Layout.TILE_GAP
        r = pygame.Rect(ox - pad, oy - pad, total + pad * 2, total + pad * 2)
        self._draw_rounded_shadow(r, Layout.GRID_RADIUS, 6)
        pygame.draw.rect(self.screen, Colors.BG_GRID, r, border_radius=Layout.GRID_RADIUS)

    # Header
    def draw_header(self, move_count, state):
        cx = Layout.SCREEN_WIDTH // 2
        self._center_text(self.font_emoji, "🧩", Colors.TEXT_DARK, cx - 120, Layout.TITLE_Y + 28)
        self._center_text(self.font_title, "N-Puzzle!", Colors.ACCENT_DARK, cx + 10, Layout.TITLE_Y + 26)
        self._center_text(self.font_emoji, "✨", Colors.STAR_YELLOW, cx + 130, Layout.TITLE_Y + 28)

        if state == PuzzleState.SHOWING_HINT:
            sub, color = "💡 Move the glowing tile!", Colors.ACCENT_DARK
        elif state == PuzzleState.SOLVED:
            sub, color = "🎉 You did it!", Colors.TILE_CORRECT
        else:
            sub, color = "Tap a tile next to the empty space~", Colors.TEXT_MUTED
        self._center_text(self.font_subtitle, sub, color, cx, Layout.SUBTITLE_Y + 8)
        self._center_text(self.font_moves, f"⭐ Moves: {move_count}", Colors.TEXT_DARK, cx, Layout.MOVES_Y + 16)

    # Tile
    def draw_tile(self, tile, is_hovered=False, is_hint=False, is_correct=False):
        if tile.is_empty:
            ox, oy = self._grid_origin()
            ex = ox + tile.grid_col * (Layout.TILE_SIZE + Layout.TILE_GAP)
            ey = oy + tile.grid_row * (Layout.TILE_SIZE + Layout.TILE_GAP)
            r = pygame.Rect(ex, ey, Layout.TILE_SIZE, Layout.TILE_SIZE)
            pygame.draw.rect(self.screen, Colors.SHADOW, r, width=2, border_radius=Layout.TILE_RADIUS)
            return

        x, y = tile.screen_x, tile.screen_y + tile.bounce
        s, rad = Layout.TILE_SIZE, Layout.TILE_RADIUS
        base = Colors.TILE_COLORS[tile.value] if tile.value < len(Colors.TILE_COLORS) else Colors.TILE_1

        if is_hint:
            pulse = 0.5 + 0.5 * math.sin(self._frame * 0.12)
            gs = int(8 + 6 * pulse)
            gsurf = pygame.Surface((s + gs * 2, s + gs * 2), pygame.SRCALPHA)
            a = int(100 + 80 * pulse)
            pygame.draw.rect(gsurf, (*Colors.TILE_HINT, a), gsurf.get_rect(), border_radius=rad + 6)
            self.screen.blit(gsurf, (x - gs, y - gs))
            base = Colors.TILE_HINT

        self._draw_rounded_shadow(pygame.Rect(x, y, s, s), rad, Layout.SHADOW_OFFSET)
        pygame.draw.rect(self.screen, base, pygame.Rect(x, y, s, s), border_radius=rad)

        shine = tuple(min(c + 50, 255) for c in base)
        sr = pygame.Rect(x + 4, y + 4, s - 8, s // 3)
        ss = pygame.Surface(sr.size, pygame.SRCALPHA)
        pygame.draw.rect(ss, (*shine, 90), ss.get_rect(), border_radius=rad - 2)
        self.screen.blit(ss, sr.topleft)

        if is_hovered:
            hs = pygame.Surface((s, s), pygame.SRCALPHA)
            pygame.draw.rect(hs, (*Colors.TILE_HOVER, 60), hs.get_rect(), border_radius=rad)
            self.screen.blit(hs, (x, y))

        if is_correct and not is_hint:
            self._center_text(self.font_emoji, "✓", (255, 255, 255), x + s - 18, y + 16)

        if tile.glow > 0.05:
            gs = pygame.Surface((s + 16, s + 16), pygame.SRCALPHA)
            a = int(150 * tile.glow)
            pygame.draw.rect(gs, (*Colors.ACCENT, a), gs.get_rect(), width=3, border_radius=rad + 4)
            self.screen.blit(gs, (x - 8, y - 8))

        self._center_text(self.font_tile, str(tile.value), (*Colors.TEXT_DARK, 60), x + s // 2 + 2, y + s // 2 + 2)
        self._center_text(self.font_tile, str(tile.value), Colors.TEXT_LIGHT, x + s // 2, y + s // 2)

    # Buttons
    def draw_buttons(self, mouse_pos) -> dict:
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
            bc = Colors.BTN_HOVER if hovered else color
            self._draw_rounded_shadow(rect, Layout.BUTTON_RADIUS, 3)
            pygame.draw.rect(self.screen, bc, rect, border_radius=Layout.BUTTON_RADIUS)
            sh = pygame.Rect(rect.x + 4, rect.y + 2, rect.width - 8, rect.height // 3)
            ss = pygame.Surface(sh.size, pygame.SRCALPHA)
            pygame.draw.rect(ss, (255, 255, 255, 50), ss.get_rect(), border_radius=Layout.BUTTON_RADIUS)
            self.screen.blit(ss, sh.topleft)
            self._center_text(self.font_button, label, Colors.TEXT_LIGHT, rect.centerx, rect.centery)
            rects[key] = rect
        return rects

    # Solved overlay
    def draw_solved_overlay(self, move_count):
        overlay = pygame.Surface((Layout.SCREEN_WIDTH, Layout.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((80, 50, 60, 170))
        self.screen.blit(overlay, (0, 0))
        cx, cy = Layout.SCREEN_WIDTH // 2, Layout.SCREEN_HEIGHT // 2
        t = pygame.time.get_ticks()
        pulse = 0.5 + 0.5 * math.sin(t * Animation.PULSE_SPEED)
        r = int(110 + 30 * pulse)
        gs = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        a = int(50 + 40 * pulse)
        pygame.draw.circle(gs, (*Colors.ACCENT, a), (r, r), r)
        self.screen.blit(gs, (cx - r, cy - r - 20))
        bounce = math.sin(t * 0.005) * 8
        self._center_text(self.font_emoji, "🏆", Colors.STAR_YELLOW, cx, cy - 80 + bounce)
        self._center_text(self.font_overlay_lg, "Puzzle Solved!", Colors.STAR_YELLOW, cx, cy - 20)
        self._center_text(self.font_overlay_sm, f"Completed in {move_count} moves ✨", Colors.TEXT_LIGHT, cx, cy + 30)
        self._center_text(self.font_subtitle, "Click anywhere to continue...", Colors.TEXT_MUTED, cx, cy + 70)
        self.draw_sparkles()