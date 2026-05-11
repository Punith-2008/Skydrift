"""
src/effects/transitions.py
Biome transition effects: fade, chromatic wipe, pixel dissolve.
"""

import pygame
import random
import math


class BiomeTransition:
    """
    Handles animated transitions between biomes.
    Modes: fade, chromatic, dissolve.
    """

    def __init__(self, screen_w: int, screen_h: int):
        self.w = screen_w
        self.h = screen_h
        self.active = False
        self.progress = 0.0   # 0 → 1: fade out; 1 → 2: fade in
        self.duration = 0.8   # seconds for full transition
        self._speed = 1.0 / self.duration
        self._callback = None
        self.mode = "fade"    # fade | chromatic | dissolve

        # Dissolve grid
        self._tiles = []

    def start(self, callback=None, mode: str = "fade") -> None:
        """Begin transition. `callback` is called at the midpoint (peak black)."""
        self.active = True
        self.progress = 0.0
        self._callback = callback
        self.mode = mode
        self._mid_fired = False

        if mode == "dissolve":
            tile = 32
            cols = (self.w + tile - 1) // tile
            rows = (self.h + tile - 1) // tile
            self._tiles = []
            for row in range(rows):
                for col in range(cols):
                    self._tiles.append({
                        "x": col * tile, "y": row * tile,
                        "w": tile, "h": tile,
                        "threshold": random.random()
                    })

    def update(self, dt: float) -> None:
        if not self.active:
            return
        self.progress += self._speed * dt * 2  # 0→1 out, 1→2 in

        if self.progress >= 1.0 and not self._mid_fired:
            self._mid_fired = True
            if self._callback:
                self._callback()

        if self.progress >= 2.0:
            self.active = False
            self.progress = 0.0

    def draw(self, surface: pygame.Surface) -> None:
        if not self.active:
            return

        p = self.progress
        alpha = int(255 * (1.0 - abs(p - 1.0)))  # peak at p=1

        if self.mode == "fade":
            self._draw_fade(surface, alpha)
        elif self.mode == "chromatic":
            self._draw_chromatic(surface, p, alpha)
        elif self.mode == "dissolve":
            self._draw_dissolve(surface, p, alpha)

    def _draw_fade(self, surface: pygame.Surface, alpha: int) -> None:
        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        surface.blit(overlay, (0, 0))

    def _draw_chromatic(self, surface: pygame.Surface, p: float, alpha: int) -> None:
        # Draw R/G/B channel offsets then fade
        if p < 1.0:
            # Expanding chromatic bands
            off = int((1.0 - p) * 30)
            r_surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            r_surf.fill((255, 0, 0, min(alpha, 60)))
            surface.blit(r_surf, (-off, 0), special_flags=pygame.BLEND_RGBA_ADD)

            b_surf = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            b_surf.fill((0, 0, 255, min(alpha, 60)))
            surface.blit(b_surf, (off, 0), special_flags=pygame.BLEND_RGBA_ADD)

        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        surface.blit(overlay, (0, 0))

    def _draw_dissolve(self, surface: pygame.Surface, p: float, alpha: int) -> None:
        t = p if p < 1.0 else 2.0 - p   # 0→1 reveal both ways
        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        for tile in self._tiles:
            if tile["threshold"] < t:
                a = min(255, alpha + 80)
                pygame.draw.rect(overlay, (0, 0, 0, a),
                                 (tile["x"], tile["y"], tile["w"], tile["h"]))
        surface.blit(overlay, (0, 0))
