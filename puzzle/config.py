"""
Puzzle configuration.
Screen size matches the main game for seamless integration.
"""


class Colors:
    """Soft pastel candy palette."""
    BG_PRIMARY      = (255, 245, 248)
    BG_SECONDARY    = (255, 228, 235)
    BG_GRID         = (255, 218, 227)

    TILE_1          = (255, 154, 162)
    TILE_2          = (255, 183, 178)
    TILE_3          = (255, 218, 193)
    TILE_4          = (226, 240, 203)
    TILE_5          = (181, 234, 215)
    TILE_6          = (149, 225, 211)
    TILE_7          = (163, 196, 243)
    TILE_8          = (190, 167, 232)

    TILE_COLORS = [None, TILE_1, TILE_2, TILE_3, TILE_4, TILE_5, TILE_6, TILE_7, TILE_8]

    TILE_HOVER      = (255, 255, 255)
    TILE_HINT       = (255, 236, 139)
    TILE_CORRECT    = (144, 238, 144)

    ACCENT          = (255, 130, 171)
    ACCENT_DARK     = (220, 100, 140)
    TEXT_DARK       = (100, 70, 80)
    TEXT_LIGHT      = (255, 255, 255)
    TEXT_MUTED      = (180, 140, 155)
    SHADOW          = (220, 190, 200)
    STAR_YELLOW     = (255, 223, 100)

    BTN_PRIMARY     = (255, 154, 162)
    BTN_SECONDARY   = (163, 196, 243)
    BTN_HOVER       = (255, 183, 178)


class Layout:
    """Puzzle layout — MATCHES main game screen size."""
    SCREEN_WIDTH    = 960      # Same as Screen.WIDTH
    SCREEN_HEIGHT   = 640      # Same as Screen.HEIGHT
    GRID_SIZE       = 3
    TILE_SIZE       = 120
    TILE_GAP        = 10
    TILE_RADIUS     = 20
    GRID_TOP        = 180
    GRID_PADDING    = 16
    GRID_RADIUS     = 24
    BUTTON_Y        = 560
    BUTTON_WIDTH    = 150
    BUTTON_HEIGHT   = 50
    BUTTON_RADIUS   = 25
    BUTTON_GAP      = 40
    SHADOW_OFFSET   = 5
    TITLE_Y         = 20
    SUBTITLE_Y      = 85
    MOVES_Y         = 115


class Animation:
    """Animation settings."""
    TILE_LERP_SPEED   = 0.18
    TILE_SNAP_DIST    = 1.5
    GLOW_SPEED        = 0.10
    HINT_DURATION     = 100
    PULSE_SPEED       = 0.004
    BOUNCE_SPEED      = 0.06
    FPS               = 60