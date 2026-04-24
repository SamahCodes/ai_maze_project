"""
Data models for the N-Puzzle module.
"""

from enum import Enum
from dataclasses import dataclass


class PuzzleState(Enum):
    """Possible states of the puzzle."""
    IDLE         = "idle"
    ANIMATING    = "animating"
    SHOWING_HINT = "showing_hint"
    SOLVED       = "solved"


@dataclass
class Tile:
    """Represents a single puzzle tile."""
    value: int
    grid_col: int
    grid_row: int

    # Screen positions (for smooth animation)
    screen_x: float = 0.0
    screen_y: float = 0.0
    target_x: float = 0.0
    target_y: float = 0.0

    # Animation state
    is_moving: bool  = False
    glow: float      = 0.0
    bounce: float    = 0.0      # Bounce offset for fun feedback
    scale: float     = 1.0      # Pop scale

    @property
    def is_empty(self) -> bool:
        return self.value == 0

    def snap_to_target(self):
        """Instantly move to target position."""
        self.screen_x = self.target_x
        self.screen_y = self.target_y
        self.is_moving = False
        self.glow = 0.0


@dataclass
class Sparkle:
    """A tiny decorative sparkle particle."""
    x: float
    y: float
    vx: float
    vy: float
    life: float      # 1.0 -> 0.0
    size: float
    color: tuple