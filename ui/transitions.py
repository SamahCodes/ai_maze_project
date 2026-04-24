"""
Smooth screen transitions.
Fade, slide, and overlay effects.
"""

import pygame
from config.settings import Colors, Screen, UIConfig


class TransitionManager:
    """Manages smooth transitions between game states."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.active = False
        self.alpha = 0
        self.target_alpha = 0
        self.speed = UIConfig.TRANSITION_SPEED
        self.callback = None
        self._done_callback_fired = False

    def start_fade_out(self, callback=None):
        """Start fading to black."""
        self.active = True
        self.target_alpha = 255
        self.callback = callback
        self._done_callback_fired = False

    def start_fade_in(self):
        """Start fading from black."""
        self.active = True
        self.target_alpha = 0

    def update(self):
        """Update transition state."""
        if not self.active:
            return

        if self.alpha < self.target_alpha:
            self.alpha = min(255, self.alpha + self.speed)
        elif self.alpha > self.target_alpha:
            self.alpha = max(0, self.alpha - self.speed)

        # Fire callback at peak darkness
        if (self.alpha >= 250
                and self.target_alpha == 255
                and not self._done_callback_fired):
            self._done_callback_fired = True
            if self.callback:
                self.callback()
            # Start fading back in
            self.target_alpha = 0

        # Done fading in
        if self.alpha <= 0 and self.target_alpha == 0:
            self.active = False

    def draw(self):
        """Draw transition overlay."""
        if not self.active and self.alpha <= 0:
            return

        overlay = pygame.Surface(
            (Screen.WIDTH, Screen.HEIGHT), pygame.SRCALPHA
        )
        overlay.fill((*Colors.BG_DARK, min(255, self.alpha)))
        self.screen.blit(overlay, (0, 0))

    def is_active(self) -> bool:
        return self.active