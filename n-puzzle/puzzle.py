"""
Core puzzle logic: grid management, tile movement, animation updates.
"""

import random
import pygame
from typing import Optional, Callable, Dict, List, Tuple

from config import Layout, Animation
from models import Tile, PuzzleState
from solver import is_solvable, get_hint, GOAL_POSITIONS
from renderer import Renderer


class NPuzzle:
    """
    Full N-Puzzle game module.

    Usage (standalone):
        puzzle = NPuzzle()
        puzzle.run()

    Usage (integration):
        puzzle = NPuzzle(standalone=False)
        puzzle.init(screen, clock)
        # in your loop:
            puzzle.handle_event(event)
            puzzle.update()
            puzzle.draw()
    """

    def __init__(self, standalone: bool = True):
        self.standalone = standalone
        self.screen: Optional[pygame.Surface] = None
        self.clock: Optional[pygame.time.Clock] = None
        self.renderer: Optional[Renderer] = None

        # Puzzle state
        self.tiles: List[Tile] = []
        self.state = PuzzleState.IDLE
        self.move_count = 0
        self.hint_pos: Optional[Tuple[int, int]] = None
        self.hint_timer = 0
        self.button_rects: Dict[str, pygame.Rect] = {}
        self._solved_sparkles_spawned = False

        # Callbacks
        self._callbacks: Dict[str, Optional[Callable]] = {
            "on_solve": None,
            "on_move": None,
            "on_reset": None,
        }

    # ── setup ─────────────────────────────────────────────────

    def init(self, screen: pygame.Surface, clock: pygame.time.Clock):
        self.screen = screen
        self.clock = clock
        self.renderer = Renderer(screen)
        self._generate_puzzle()

    def set_callback(self, name: str, fn: Callable):
        if name in self._callbacks:
            self._callbacks[name] = fn

    # ── puzzle generation ─────────────────────────────────────

    def _generate_puzzle(self):
        numbers = list(range(Layout.GRID_SIZE ** 2))
        while True:
            random.shuffle(numbers)
            if is_solvable(numbers):
                break

        self.tiles = []
        for i, val in enumerate(numbers):
            row, col = divmod(i, Layout.GRID_SIZE)
            tile = Tile(value=val, grid_col=col, grid_row=row)
            sx, sy = self.renderer.tile_screen_pos(col, row)
            tile.screen_x = sx
            tile.screen_y = sy
            tile.target_x = sx
            tile.target_y = sy
            self.tiles.append(tile)

        self.state = PuzzleState.IDLE
        self.move_count = 0
        self.hint_pos = None
        self.hint_timer = 0
        self._solved_sparkles_spawned = False

        if self._callbacks["on_reset"]:
            self._callbacks["on_reset"]()

    def _get_tile(self, col: int, row: int) -> Optional[Tile]:
        for t in self.tiles:
            if t.grid_col == col and t.grid_row == row:
                return t
        return None

    def _get_empty(self) -> Tile:
        return next(t for t in self.tiles if t.is_empty)

    def _to_grid(self) -> List[List[int]]:
        grid = [[0] * Layout.GRID_SIZE for _ in range(Layout.GRID_SIZE)]
        for t in self.tiles:
            grid[t.grid_row][t.grid_col] = t.value
        return grid

    # ── tile movement ─────────────────────────────────────────

    def _try_move(self, tile: Tile) -> bool:
        if tile.is_empty or self.state == PuzzleState.ANIMATING:
            return False

        empty = self._get_empty()
        dc = empty.grid_col - tile.grid_col
        dr = empty.grid_row - tile.grid_row

        if abs(dc) + abs(dr) != 1:
            return False

        # Swap grid positions
        tile.grid_col, empty.grid_col = empty.grid_col, tile.grid_col
        tile.grid_row, empty.grid_row = empty.grid_row, tile.grid_row

        # Animation targets
        tx, ty = self.renderer.tile_screen_pos(tile.grid_col, tile.grid_row)
        tile.target_x = tx
        tile.target_y = ty
        tile.is_moving = True
        tile.glow = 1.0
        tile.bounce = -8.0      # Little hop!

        ex, ey = self.renderer.tile_screen_pos(empty.grid_col, empty.grid_row)
        empty.target_x = ex
        empty.target_y = ey
        empty.snap_to_target()

        self.state = PuzzleState.ANIMATING
        self.move_count += 1

        # Sparkle where tile lands
        self.renderer.spawn_sparkles(tx + Layout.TILE_SIZE / 2, ty + Layout.TILE_SIZE / 2, 5)

        if self._callbacks["on_move"]:
            self._callbacks["on_move"](tile.value)

        return True

    def _is_tile_correct(self, tile: Tile) -> bool:
        if tile.is_empty:
            return True
        goal_col, goal_row = GOAL_POSITIONS[tile.value]
        return tile.grid_col == goal_col and tile.grid_row == goal_row

    def _check_solved(self) -> bool:
        return all(self._is_tile_correct(t) for t in self.tiles)

    # ── update ────────────────────────────────────────────────

    def update(self):
        # Always update sparkles
        self.renderer.update_sparkles()

        if self.state == PuzzleState.ANIMATING:
            all_done = True
            for tile in self.tiles:
                if tile.is_moving:
                    dx = tile.target_x - tile.screen_x
                    dy = tile.target_y - tile.screen_y

                    if (abs(dx) < Animation.TILE_SNAP_DIST
                            and abs(dy) < Animation.TILE_SNAP_DIST):
                        tile.snap_to_target()
                    else:
                        tile.screen_x += dx * Animation.TILE_LERP_SPEED
                        tile.screen_y += dy * Animation.TILE_LERP_SPEED
                        all_done = False

                # Fade glow
                if tile.glow > 0:
                    tile.glow = max(0.0, tile.glow - Animation.GLOW_SPEED)

                # Bounce spring back
                if abs(tile.bounce) > 0.5:
                    tile.bounce *= 0.85
                else:
                    tile.bounce = 0.0

            if all_done:
                if self._check_solved():
                    self.state = PuzzleState.SOLVED
                    if self._callbacks["on_solve"]:
                        self._callbacks["on_solve"](self.move_count)
                else:
                    self.state = PuzzleState.IDLE

        elif self.state == PuzzleState.SHOWING_HINT:
            self.hint_timer -= 1
            if self.hint_timer <= 0:
                self.hint_pos = None
                self.state = PuzzleState.IDLE

        elif self.state == PuzzleState.SOLVED:
            if not self._solved_sparkles_spawned:
                cx = Layout.SCREEN_WIDTH // 2
                cy = Layout.SCREEN_HEIGHT // 2
                self.renderer.spawn_sparkles(cx, cy - 40, 30)
                self._solved_sparkles_spawned = True

    # ── event handling ────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self._generate_puzzle()
                return
            if event.key == pygame.K_h and self.state == PuzzleState.IDLE:
                self._show_hint()
                return

        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        pos = pygame.mouse.get_pos()

        # Buttons
        if "reset" in self.button_rects:
            if self.button_rects["reset"].collidepoint(pos):
                self._generate_puzzle()
                return

        if "hint" in self.button_rects:
            if self.button_rects["hint"].collidepoint(pos):
                if self.state == PuzzleState.IDLE:
                    self._show_hint()
                return

        # Tile clicks
        if self.state not in (PuzzleState.IDLE, PuzzleState.SHOWING_HINT):
            return

        if self.state == PuzzleState.SHOWING_HINT:
            self.state = PuzzleState.IDLE
            self.hint_pos = None

        for tile in self.tiles:
            if tile.is_empty:
                continue
            rect = pygame.Rect(
                tile.screen_x, tile.screen_y,
                Layout.TILE_SIZE, Layout.TILE_SIZE
            )
            if rect.collidepoint(pos):
                self._try_move(tile)
                break

    def _show_hint(self):
        grid = self._to_grid()
        result = get_hint(grid)
        if result:
            self.hint_pos = result
            self.state = PuzzleState.SHOWING_HINT
            self.hint_timer = Animation.HINT_DURATION

    # ── drawing ───────────────────────────────────────────────

    def draw(self):
        mouse_pos = pygame.mouse.get_pos()

        self.renderer.draw_background()
        self.renderer.draw_header(self.move_count, self.state)
        self.renderer.draw_grid_backing()

        # Draw tiles
        for tile in self.tiles:
            is_hint = (
                self.hint_pos is not None
                and tile.grid_col == self.hint_pos[0]
                and tile.grid_row == self.hint_pos[1]
            )
            is_hovered = False
            if not tile.is_empty and self.state == PuzzleState.IDLE:
                r = pygame.Rect(
                    tile.screen_x, tile.screen_y,
                    Layout.TILE_SIZE, Layout.TILE_SIZE
                )
                is_hovered = r.collidepoint(mouse_pos)

            self.renderer.draw_tile(
                tile,
                is_hovered=is_hovered,
                is_hint=is_hint,
                is_correct=self._is_tile_correct(tile)
            )

        # Sparkles on top of tiles
        self.renderer.draw_sparkles()

        # Buttons
        self.button_rects = self.renderer.draw_buttons(mouse_pos)

        # Solved overlay
        if self.state == PuzzleState.SOLVED:
            self.renderer.draw_solved_overlay(self.move_count)

    # ── standalone runner ─────────────────────────────────────

    def run(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (Layout.SCREEN_WIDTH, Layout.SCREEN_HEIGHT)
        )
        pygame.display.set_caption("🧩 N-Puzzle!")
        self.clock = pygame.time.Clock()
        self.renderer = Renderer(self.screen)
        self._generate_puzzle()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.handle_event(event)

            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(Animation.FPS)

        pygame.quit()

    # ── public API ────────────────────────────────────────────

    def get_stats(self) -> dict:
        return {
            "solved": self._check_solved(),
            "moves": self.move_count,
            "state": self.state.value,
        }

    def reset(self):
        self._generate_puzzle()