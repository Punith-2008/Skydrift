"""
src/biomes/base_biome.py
Abstract base class for all biomes.
Each biome provides:
  - Parallax background drawing
  - Pipe color scheme
  - Ambient particle type
  - Weather mode
  - Music theme key
  - Transition mode
"""

import pygame
import math
import random
from abc import ABC, abstractmethod


class BaseBiome(ABC):
    """Abstract biome — defines the visual & audio contract."""

    # Override in subclasses
    NAME: str = "base"
    MUSIC_KEY: str = "cyberpunk"
    WEATHER_MODE: str = "none"
    TRANSITION_MODE: str = "fade"
    SKY_TOP: tuple = (20, 20, 40)
    SKY_BOTTOM: tuple = (40, 40, 80)
    PIPE_COLOR: tuple = (60, 180, 60)
    PIPE_ACCENT: tuple = (40, 220, 80)
    PIPE_DARK: tuple = (20, 80, 20)
    GROUND_COLOR: tuple = (80, 60, 30)
    GROUND_LINE: tuple = (100, 80, 50)
    AMBIENT_PARTICLE: str = "none"  # trail | sparks | bubbles | stars | lava | snow | neon | none

    def __init__(self, screen_w: int, screen_h: int):
        self.w = screen_w
        self.h = screen_h
        self.scroll_x: float = 0.0
        self._layers: list = []   # built by subclass in _build_layers()
        self._build_layers()

    # ── Must implement ─────────────────────────────────────────────────────
    @abstractmethod
    def _build_layers(self) -> None:
        """Pre-render / prepare parallax layer data."""
        ...

    @abstractmethod
    def draw_background(self, surface: pygame.Surface, scroll_x: float) -> None:
        """Draw the full background including all parallax layers."""
        ...

    # ── Optional override ──────────────────────────────────────────────────
    def draw_foreground(self, surface: pygame.Surface, scroll_x: float) -> None:
        """Draw foreground decorations on top of entities (e.g. underwater overlay)."""
        pass

    def get_pipe_scheme(self) -> dict:
        return {
            "body":   self.PIPE_COLOR,
            "accent": self.PIPE_ACCENT,
            "dark":   self.PIPE_DARK,
        }

    def get_ground_scheme(self) -> dict:
        return {
            "color": self.GROUND_COLOR,
            "line":  self.GROUND_LINE,
        }

    def get_ambient_particle(self) -> str:
        return self.AMBIENT_PARTICLE

    # ── Helpers ────────────────────────────────────────────────────────────
    @staticmethod
    def _lerp_color(c1: tuple, c2: tuple, t: float) -> tuple:
        t = max(0.0, min(1.0, t))
        return (
            int(c1[0] + (c2[0] - c1[0]) * t),
            int(c1[1] + (c2[1] - c1[1]) * t),
            int(c1[2] + (c2[2] - c1[2]) * t),
        )

    def _draw_sky_gradient(self, surface: pygame.Surface) -> None:
        """Draw a vertical gradient sky filling the whole screen."""
        for y in range(self.h):
            t = y / max(self.h - 1, 1)
            c = self._lerp_color(self.SKY_TOP, self.SKY_BOTTOM, t)
            pygame.draw.line(surface, c, (0, y), (self.w - 1, y))

    def _draw_star_field(self, surface: pygame.Surface, stars: list,
                         scroll_factor: float, scroll_x: float) -> None:
        for sx, sy, sr, sc in stars:
            x = int((sx - scroll_x * scroll_factor) % self.w)
            pygame.draw.circle(surface, sc, (x, sy), sr)

    @staticmethod
    def _make_stars(count: int, w: int, h: int, max_r: int = 2) -> list:
        stars = []
        for _ in range(count):
            br = random.randint(150, 255)
            col = (br, br, random.randint(br - 30, 255))
            stars.append((
                random.randint(0, w),
                random.randint(0, h),
                random.randint(0, max_r),
                col
            ))
        return stars
