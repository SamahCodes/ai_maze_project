"""
Global game configuration.
Central place for ALL tunable values.
"""

import math


class Colors:
    """Cute pastel palette with depth variations."""

    # Maze walls (gradient layers for depth)
    WALL_NEAR       = (255, 154, 162)    # Coral pink (close)
    WALL_MID        = (220, 130, 145)    # Muted rose
    WALL_FAR        = (180, 110, 125)    # Deep rose (far)
    WALL_ACCENT     = (255, 183, 178)    # Peach highlight

    # Floor and ceiling
    CEILING_NEAR    = (190, 167, 232)    # Lavender
    CEILING_FAR     = (140, 120, 190)    # Deep lavender
    FLOOR_NEAR      = (181, 234, 215)    # Mint
    FLOOR_FAR       = (130, 190, 170)    # Deep mint

    # Lighting
    LIGHT_HINT      = (255, 236, 139)    # Golden hint light
    LIGHT_AMBIENT   = (255, 245, 248)    # Warm ambient
    LIGHT_GOAL      = (255, 223, 100)    # Goal glow

    # UI
    BG_PRIMARY      = (255, 245, 248)
    BG_SECONDARY    = (255, 228, 235)
    BG_DARK         = (80, 50, 60)
    ACCENT          = (255, 130, 171)
    ACCENT_DARK     = (220, 100, 140)
    TEXT_DARK       = (100, 70, 80)
    TEXT_LIGHT      = (255, 255, 255)
    TEXT_MUTED      = (180, 140, 155)
    SHADOW          = (220, 190, 200)

    # Buttons
    BTN_PRIMARY     = (255, 154, 162)
    BTN_SECONDARY   = (163, 196, 243)
    BTN_HINT        = (190, 167, 232)
    BTN_HOVER       = (255, 183, 178)

    # Player / compass
    PLAYER_COLOR    = (163, 196, 243)
    MINIMAP_WALL    = (255, 154, 162)
    MINIMAP_FLOOR   = (255, 240, 243)
    MINIMAP_PLAYER  = (99, 130, 230)
    MINIMAP_GOAL    = (255, 223, 100)
    MINIMAP_FOG     = (200, 180, 190)
    MINIMAP_VISITED = (226, 240, 203)

    # Puzzle tiles
    TILE_COLORS = [
        None,
        (255, 154, 162), (255, 183, 178), (255, 218, 193),
        (226, 240, 203), (181, 234, 215), (149, 225, 211),
        (163, 196, 243), (190, 167, 232),
    ]
    TILE_HINT       = (255, 236, 139)
    TILE_HOVER      = (255, 255, 255)
    TILE_CORRECT    = (144, 238, 144)
    STAR_YELLOW     = (255, 223, 100)


class Screen:
    """Display settings."""
    WIDTH           = 960
    HEIGHT          = 640
    FPS             = 60
    TITLE           = "AI Maze Adventure"


class Raycasting:
    """Raycasting engine settings."""
    FOV             = math.pi / 3          # 60 degrees
    HALF_FOV        = FOV / 2
    NUM_RAYS        = 240                  # Number of rays to cast
    MAX_DEPTH       = 20                   # Max ray distance
    WALL_HEIGHT     = 1.0                  # Logical wall height
    RENDER_WIDTH    = 960                  # 3D viewport width
    RENDER_HEIGHT   = 480                  # 3D viewport height
    RENDER_TOP      = 80                   # Y offset for 3D view


class MazeConfig:
    """Maze generation settings."""
    ROWS            = 15                   # Must be odd
    COLS            = 15                   # Must be odd
    CELL_SIZE       = 1.0                  # Logical size


class PlayerConfig:
    """Player movement settings."""
    MOVE_SPEED      = 0.04
    ROT_SPEED       = 0.045
    COLLISION_RADIUS = 0.2
    BOB_SPEED       = 0.08
    BOB_AMOUNT      = 3.0


class UIConfig:
    """UI layout settings."""
    HUD_HEIGHT      = 80
    MINIMAP_SIZE    = 140
    MINIMAP_MARGIN  = 15
    MINIMAP_ALPHA   = 200
    COMPASS_SIZE    = 60
    BTN_WIDTH       = 140
    BTN_HEIGHT      = 44
    BTN_RADIUS      = 22
    TRANSITION_SPEED = 12


class GameStates:
    """All possible game states."""
    MAZE_EXPLORE    = "maze_explore"
    AT_INTERSECTION = "at_intersection"
    PUZZLE_ACTIVE   = "puzzle_active"
    SHOW_DIRECTION  = "show_direction"
    GAME_WON        = "game_won"
    TRANSITION      = "transition"