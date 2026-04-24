"""
Game Manager — integrates all systems.
Fixed:
  - Uses RELATIVE directions (forward/left/right/back)
  - Passes goal angle to renderer for trophy
  - Proper hint persistence
  - No double puzzle-complete trigger
"""

import math
import pygame
import sys
from typing import Optional

from config.settings import Colors, Screen, Raycasting, MazeConfig, GameStates
from engine.raycaster import Raycaster
from engine.renderer_3d import Renderer3D
from maze.maze_generator import MazeGenerator
from maze.player import Player
from maze_ai.pathfinder import MazePathfinder
from puzzle.puzzle import NPuzzle
from ui.hud import HUD
from ui.minimap import Minimap
from ui.transitions import TransitionManager


HINT_LIGHT_DURATION = 300  # 5 seconds at 60fps


class GameManager:
    """Main game controller."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (Screen.WIDTH, Screen.HEIGHT)
        )
        pygame.display.set_caption(Screen.TITLE)
        self.clock = pygame.time.Clock()

        # State
        self.state = GameStates.MAZE_EXPLORE
        self.button_rects = {}

        # Hint data
        self.hint_direction: Optional[str] = None      # Cardinal
        self.hint_relative: Optional[str] = None        # Relative
        self.hint_angle: Optional[float] = None         # Angle in radians
        self.show_hint_light = False
        self.hint_light_timer = 0
        self.direction_timer = 0
        self._puzzle_complete_handled = False

        # Fonts for popups
        self.font_big = pygame.font.SysFont("comicsansms", 44, bold=True)
        self.font_med = pygame.font.SysFont("comicsansms", 24)
        self.font_emoji = pygame.font.SysFont("segoeuiemoji", 50)
        self.font_small = pygame.font.SysFont("comicsansms", 18)
        self.font_hint = pygame.font.SysFont("comicsansms", 20)

        # Systems
        self._init_maze()
        self._init_puzzle()
        self.hud = HUD(self.screen)
        self.minimap = Minimap()
        self.transition = TransitionManager(self.screen)

    def _init_maze(self):
        """Generate maze and create systems."""
        self.maze_gen = MazeGenerator(MazeConfig.ROWS, MazeConfig.COLS)
        self.maze_grid = self.maze_gen.generate()
        sx, sy = self.maze_gen.get_start_pos()
        self.player = Player(sx, sy, 0.0)
        self.raycaster = Raycaster(self.maze_grid)
        self.renderer3d = Renderer3D(self.screen)
        self.pathfinder = MazePathfinder(self.maze_grid)

    def _init_puzzle(self):
        """Initialize puzzle."""
        self.puzzle = NPuzzle(standalone=False)
        self.puzzle.init(self.screen, self.clock)
        self._puzzle_complete_handled = False

        def on_solved(moves):
            print(f"Puzzle solved in {moves} moves!")

        self.puzzle.set_callback("on_solve", on_solved)

    def _on_puzzle_complete(self):
        """Puzzle solved → get AI direction with RELATIVE hint."""
        if self._puzzle_complete_handled:
            return
        self._puzzle_complete_handled = True

        row, col = self.player.get_grid_pos()
        goal = self.maze_gen.goal

        # Get full hint with relative direction
        hint_info = self.pathfinder.get_full_hint(
            row, col,
            goal[0], goal[1],
            self.player.angle
        )

        self.hint_direction = hint_info["cardinal"]
        self.hint_relative = hint_info["relative"]
        self.hint_angle = hint_info["angle"]
        self.show_hint_light = True
        self.hint_light_timer = HINT_LIGHT_DURATION
        self.state = GameStates.SHOW_DIRECTION
        self.direction_timer = 0

        print(f"AI Hint: cardinal={self.hint_direction}, "
              f"relative={self.hint_relative}, "
              f"angle={self.hint_angle}")

    def _reset_game(self):
        """Reset with fade."""
        def do_reset():
            self._init_maze()
            self._init_puzzle()
            self.minimap.reset()
            self.state = GameStates.MAZE_EXPLORE
            self.hint_direction = None
            self.hint_relative = None
            self.hint_angle = None
            self.show_hint_light = False
            self.hint_light_timer = 0

        self.transition.start_fade_out(callback=do_reset)

    def _player_at_intersection(self) -> bool:
        """Check if at intersection."""
        row, col = self.player.get_grid_pos()
        if 0 <= row < len(self.maze_grid) and 0 <= col < len(self.maze_grid[0]):
            return self.maze_grid[row][col] == 2
        return False

    def _get_goal_angle(self) -> float:
        """Get angle from player to goal."""
        gx, gy = self.maze_gen.get_goal_pos()
        return math.atan2(gy - self.player.y, gx - self.player.x)

    # ── events ────────────────────────────────────────────────

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if self.transition.is_active():
                continue

            # PUZZLE MODE
            if self.state == GameStates.PUZZLE_ACTIVE:
                self.puzzle.handle_event(event)
                if self.puzzle.is_complete() and not self._puzzle_complete_handled:
                    self._on_puzzle_complete()
                if (event.type == pygame.KEYDOWN
                        and event.key == pygame.K_ESCAPE):
                    self.state = GameStates.MAZE_EXPLORE
                    self._puzzle_complete_handled = False
                continue

            # DIRECTION POPUP
            if self.state == GameStates.SHOW_DIRECTION:
                if (event.type == pygame.KEYDOWN
                        or event.type == pygame.MOUSEBUTTONDOWN):
                    self.state = GameStates.MAZE_EXPLORE
                continue

            # WIN
            if self.state == GameStates.GAME_WON:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self._reset_game()
                continue

            # MAZE
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self._reset_game()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if "reset" in self.button_rects:
                    if self.button_rects["reset"].collidepoint(pos):
                        self._reset_game()
                if "ask_ai" in self.button_rects:
                    if self.button_rects["ask_ai"].collidepoint(pos):
                        if self._player_at_intersection():
                            self.state = GameStates.PUZZLE_ACTIVE
                            self.puzzle.reset()
                            self._puzzle_complete_handled = False

    # ── update ────────────────────────────────────────────────

    def update(self):
        self.transition.update()

        if self.state == GameStates.PUZZLE_ACTIVE:
            self.puzzle.update()
            if self.puzzle.is_complete() and not self._puzzle_complete_handled:
                self._on_puzzle_complete()
            return

        if self.state == GameStates.SHOW_DIRECTION:
            self.direction_timer += 1
            return

        if self.state == GameStates.GAME_WON:
            return

        # Maze exploration
        self.player.handle_input(
            pygame.key.get_pressed(), self.maze_grid
        )

        row, col = self.player.get_grid_pos()
        self.minimap.reveal(row, col)

        # Intersection check
        if self._player_at_intersection():
            self.state = GameStates.AT_INTERSECTION
        else:
            if self.state == GameStates.AT_INTERSECTION:
                self.state = GameStates.MAZE_EXPLORE

        # Goal check
        gx, gy = self.maze_gen.get_goal_pos()
        if self.player.distance_to(gx, gy) < 0.8:
            self.state = GameStates.GAME_WON

        # Hint light countdown
        if self.show_hint_light:
            self.hint_light_timer -= 1
            if self.hint_light_timer <= 0:
                self.show_hint_light = False
                self.hint_direction = None
                self.hint_relative = None
                self.hint_angle = None

    # ── drawing ───────────────────────────────────────────────

    def draw(self):
        mouse_pos = pygame.mouse.get_pos()
        self.screen.fill(Colors.BG_PRIMARY)

        # PUZZLE
        if self.state == GameStates.PUZZLE_ACTIVE:
            self.puzzle.draw()
            self.transition.draw()
            pygame.display.flip()
            return

        # 3D MAZE
        rays = self.raycaster.cast_rays(
            self.player.x, self.player.y, self.player.angle
        )

        gx, gy = self.maze_gen.get_goal_pos()
        goal_dist = self.player.distance_to(gx, gy)
        goal_angle = self._get_goal_angle()

        self.renderer3d.set_moving(self.player.is_moving)
        self.renderer3d.render_scene(
            rays,
            hint_direction=(
                self.hint_direction if self.show_hint_light else None
            ),
            hint_angle=(
                self.hint_angle if self.show_hint_light else None
            ),
            player_angle=self.player.angle,
            at_intersection=self._player_at_intersection(),
            near_goal=(goal_dist < 5),
            goal_distance=goal_dist,
            goal_angle=goal_angle,
            relative_direction=(
                self.hint_relative if self.show_hint_light else None
            ),
        )

        # HUD with compass
        at_inter = self._player_at_intersection()
        self.button_rects = self.hud.draw(
            self.player.move_count,
            self.state,
            mouse_pos,
            at_intersection=at_inter,
            player_angle=self.player.angle
        )

        # Minimap
        row, col = self.player.get_grid_pos()
        goal = self.maze_gen.goal
        self.minimap.draw(
            self.screen, self.maze_grid,
            row, col, self.player.angle,
            goal[0], goal[1]
        )

        # Direction popup (uses RELATIVE direction)
        if self.state == GameStates.SHOW_DIRECTION:
            self._draw_direction_popup()

        # Win screen
        if self.state == GameStates.GAME_WON:
            self._draw_win_screen()

        self.transition.draw()
        pygame.display.flip()

    def _draw_direction_popup(self):
        """Direction reveal card with RELATIVE direction."""
        overlay = pygame.Surface(
            (Screen.WIDTH, Screen.HEIGHT), pygame.SRCALPHA
        )
        overlay.fill((*Colors.BG_DARK, 160))
        self.screen.blit(overlay, (0, 0))

        cx = Screen.WIDTH // 2
        cy = Screen.HEIGHT // 2

        # Card
        card = pygame.Rect(cx - 200, cy - 140, 400, 280)
        pygame.draw.rect(
            self.screen, Colors.SHADOW,
            card.move(4, 4), border_radius=24
        )
        pygame.draw.rect(
            self.screen, Colors.BG_PRIMARY,
            card, border_radius=24
        )
        pygame.draw.rect(
            self.screen, Colors.ACCENT,
            card, width=3, border_radius=24
        )

        # Robot emoji
        robot = self.font_emoji.render("🤖", True, Colors.TEXT_DARK)
        self.screen.blit(
            robot, (cx - robot.get_width() // 2, cy - 120)
        )

        # Relative direction (what the player should do)
        relative_text = self.hint_relative or "FORWARD"

        # Arrow emoji based on relative direction
        relative_arrows = {
            "FORWARD": "⬆️",
            "RIGHT": "➡️",
            "LEFT": "⬅️",
            "BACK": "⬇️",
            "HERE": "⭐",
        }
        arrow = relative_arrows.get(relative_text, "✨")

        # Main instruction
        instruction = self.font_big.render(
            f"Turn {relative_text}!",
            True, Colors.ACCENT_DARK
        )
        self.screen.blit(
            instruction,
            (cx - instruction.get_width() // 2, cy - 40)
        )

        # Bouncing arrow
        bounce = math.sin(self.direction_timer * 0.1) * 8
        arrow_surf = self.font_emoji.render(arrow, True, Colors.TEXT_DARK)
        self.screen.blit(
            arrow_surf,
            (cx - arrow_surf.get_width() // 2, cy + 20 + int(bounce))
        )

        # Small hint showing cardinal for reference
        if self.hint_direction:
            cardinal_text = self.font_hint.render(
                f"(Grid direction: {self.hint_direction})",
                True, Colors.TEXT_MUTED
            )
            self.screen.blit(
                cardinal_text,
                (cx - cardinal_text.get_width() // 2, cy + 80)
            )

        # Continue hint
        cont = self.font_small.render(
            "Press any key to continue",
            True, Colors.TEXT_MUTED
        )
        self.screen.blit(
            cont, (cx - cont.get_width() // 2, cy + 110)
        )

    def _draw_win_screen(self):
        """Victory overlay with trophy."""
        overlay = pygame.Surface(
            (Screen.WIDTH, Screen.HEIGHT), pygame.SRCALPHA
        )
        overlay.fill((*Colors.BG_DARK, 180))
        self.screen.blit(overlay, (0, 0))

        cx = Screen.WIDTH // 2
        cy = Screen.HEIGHT // 2
        t = pygame.time.get_ticks()

        # Pulsing glow
        pulse = 0.5 + 0.5 * math.sin(t * 0.004)
        radius = int(120 + 30 * pulse)
        glow = pygame.Surface(
            (radius * 2, radius * 2), pygame.SRCALPHA
        )
        alpha = int(50 + 40 * pulse)
        pygame.draw.circle(
            glow, (*Colors.ACCENT, alpha),
            (radius, radius), radius
        )
        self.screen.blit(glow, (cx - radius, cy - radius - 20))

        # Spinning stars around trophy
        for i in range(6):
            star_angle = t * 0.002 + i * math.pi / 3
            star_r = 80 + 20 * math.sin(t * 0.003 + i)
            sx = cx + int(math.cos(star_angle) * star_r)
            sy = cy - 30 + int(math.sin(star_angle) * star_r)
            star = self.font_small.render("⭐", True, Colors.STAR_YELLOW)
            self.screen.blit(
                star,
                (sx - star.get_width() // 2,
                 sy - star.get_height() // 2)
            )

        # Trophy
        bounce = math.sin(t * 0.005) * 8
        trophy = self.font_emoji.render("🏆", True, Colors.STAR_YELLOW)
        self.screen.blit(
            trophy,
            (cx - trophy.get_width() // 2, cy - 90 + int(bounce))
        )

        # Text
        title = self.font_big.render(
            "Maze Cleared!", True, Colors.STAR_YELLOW
        )
        self.screen.blit(
            title, (cx - title.get_width() // 2, cy - 20)
        )

        moves_text = self.font_med.render(
            f"Total steps: {self.player.move_count} ✨",
            True, Colors.TEXT_LIGHT
        )
        self.screen.blit(
            moves_text,
            (cx - moves_text.get_width() // 2, cy + 30)
        )

        hint = self.font_small.render(
            "Press R to play again!",
            True, Colors.TEXT_MUTED
        )
        self.screen.blit(
            hint, (cx - hint.get_width() // 2, cy + 70)
        )

    # ── main loop ─────────────────────────────────────────────

    def run(self):
        """Main game loop."""
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(Screen.FPS)