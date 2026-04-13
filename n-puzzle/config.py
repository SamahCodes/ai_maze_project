"""
Configuration constants for the N-Puzzle module.
Cute & playful theme.
"""


class Colors:
    """Soft pastel candy palette."""

    # Backgrounds
    BG_PRIMARY      = (255, 245, 248)   # Soft pink white
    BG_SECONDARY    = (255, 228, 235)   # Light rose
    BG_GRID         = (255, 218, 227)   # Grid backing

    # Tiles
    TILE_1          = (255, 154, 162)   # Coral pink
    TILE_2          = (255, 183, 178)   # Peach
    TILE_3          = (255, 218, 193)   # Apricot
    TILE_4          = (226, 240, 203)   # Mint green
    TILE_5          = (181, 234, 215)   # Seafoam
    TILE_6          = (149, 225, 211)   # Teal mint
    TILE_7          = (163, 196, 243)   # Periwinkle
    TILE_8          = (190, 167, 232)   # Lavender

    TILE_COLORS = [
        None,       # index 0 = empty
        TILE_1,
        TILE_2,
        TILE_3,
        TILE_4,
        TILE_5,
        TILE_6,
        TILE_7,
        TILE_8,
    ]

    # States
    TILE_HOVER      = (255, 255, 255)   # White glow on hover
    TILE_HINT       = (255, 236, 139)   # Sunny yellow
    TILE_CORRECT    = (144, 238, 144)   # Soft green check

    # UI
    ACCENT          = (255, 130, 171)   # Hot pink
    ACCENT_DARK     = (220, 100, 140)   # Deeper pink
    TEXT_DARK       = (100, 70, 80)     # Warm brown
    TEXT_LIGHT      = (255, 255, 255)   # White
    TEXT_MUTED      = (180, 140, 155)   # Muted rose
    SHADOW          = (220, 190, 200)   # Soft pink shadow
    STAR_YELLOW     = (255, 223, 100)   # Star/sparkle color
    OVERLAY         = (80, 50, 60)      # Dark overlay

    # Buttons
    BTN_PRIMARY     = (255, 154, 162)   # Coral
    BTN_SECONDARY   = (163, 196, 243)   # Periwinkle
    BTN_HOVER       = (255, 183, 178)   # Peach hover


class Layout:
    """Screen and grid layout settings."""
    SCREEN_WIDTH    = 600
    SCREEN_HEIGHT   = 750
    GRID_SIZE       = 3
    TILE_SIZE       = 130
    TILE_GAP        = 10
    TILE_RADIUS     = 20
    GRID_TOP        = 210
    GRID_PADDING    = 16
    GRID_RADIUS     = 24
    BUTTON_Y        = 650
    BUTTON_WIDTH    = 150
    BUTTON_HEIGHT   = 50
    BUTTON_RADIUS   = 25     # Pill shape
    BUTTON_GAP      = 40
    SHADOW_OFFSET   = 5
    TITLE_Y         = 30
    SUBTITLE_Y      = 105
    MOVES_Y         = 140
    EMOJI_SIZE      = 40


class Animation:
    """Animation timing constants."""
    TILE_LERP_SPEED   = 0.18
    TILE_SNAP_DIST    = 1.5
    GLOW_SPEED        = 0.10
    HINT_DURATION     = 100      # frames (~1.7s at 60fps)
    PULSE_SPEED       = 0.004
    BOUNCE_SPEED      = 0.06
    SPARKLE_SPEED     = 0.08
    FPS               = 60