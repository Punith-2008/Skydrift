"""
src/biomes/ice_world.py
Biome 3 — Frozen Ice World
Aurora borealis, icebergs, snowflakes, blue/white palette.
"""

import pygame
import random
import math
from .base_biome import BaseBiome


class IceWorldBiome(BaseBiome):
    NAME = "ice_world"
    MUSIC_KEY = "ice_world"
    WEATHER_MODE = "snow"
    TRANSITION_MODE = "fade"
    SKY_TOP = (5, 10, 30)
    SKY_BOTTOM = (20, 40, 80)
    PIPE_COLOR = (140, 200, 255)
    PIPE_ACCENT = (200, 240, 255)
    PIPE_DARK = (60, 100, 160)
    GROUND_COLOR = (180, 210, 240)
    GROUND_LINE = (220, 240, 255)
    AMBIENT_PARTICLE = "snow"

    def _build_layers(self):
        self._aurora_strips = [
            {"y": random.randint(30, 150), "h": random.randint(30, 80),
             "color": random.choice([(0, 255, 180), (0, 180, 255), (100, 255, 100)]),
             "phase": random.uniform(0, 6.28), "speed": random.uniform(0.3, 0.8)}
            for _ in range(5)
        ]
        self._stars = self._make_stars(100, self.w * 2, self.h // 2)
        self._icebergs_far = self._gen_icebergs(10, 0.15, (100, 140, 180))
        self._icebergs_near = self._gen_icebergs(6, 0.4, (160, 200, 230))

    def _gen_icebergs(self, count, speed, color):
        items = []
        x = 0
        total = self.w * 2
        for _ in range(count):
            w = random.randint(60, 160)
            h = random.randint(40, 120)
            items.append({"x": x % total, "w": w, "h": h, "color": color})
            x += random.randint(80, 200)
        return {"items": items, "total_w": max(x, total), "speed": speed}

    def draw_background(self, surface: pygame.Surface, scroll_x: float) -> None:
        self._draw_sky_gradient(surface)
        t = pygame.time.get_ticks() / 1000.0

        # Stars
        self._draw_star_field(surface, self._stars, 0.05, scroll_x)

        # Aurora
        for strip in self._aurora_strips:
            wave = math.sin(t * strip["speed"] + strip["phase"])
            alpha = int(60 + 40 * wave)
            alpha = max(20, min(100, alpha))
            col = strip["color"]
            for i in range(3):
                asurf = pygame.Surface((self.w, strip["h"] // 3 + 1), pygame.SRCALPHA)
                a2 = max(0, alpha - i * 20)
                asurf.fill((*col, a2))
                surface.blit(asurf, (0, strip["y"] + i * strip["h"] // 3),
                              special_flags=pygame.BLEND_RGBA_ADD)

        # Far icebergs
        self._draw_icebergs(surface, self._icebergs_far, scroll_x)
        self._draw_icebergs(surface, self._icebergs_near, scroll_x)

    def _draw_icebergs(self, surface, layer, scroll_x):
        total = layer["total_w"]
        speed = layer["speed"]
        for berg in layer["items"]:
            bx = int((berg["x"] - scroll_x * speed) % total)
            by = self.h - berg["h"] - 60  # above ground
            col = berg["color"]
            # Main iceberg shape (tapered top)
            half = berg["w"] // 2
            tip_offset = half // 3
            points = [
                (bx + tip_offset, by),
                (bx + berg["w"] - tip_offset, by),
                (bx + berg["w"], by + berg["h"]),
                (bx, by + berg["h"]),
            ]
            pygame.draw.polygon(surface, col, points)
            # Highlight edge
            pygame.draw.polygon(surface, (220, 240, 255), points, 1)

    def draw_foreground(self, surface: pygame.Surface, scroll_x: float) -> None:
        # Frozen ground shine
        ground_y = self.h - 60
        gs = pygame.Surface((self.w, 3), pygame.SRCALPHA)
        gs.fill((200, 230, 255, 100))
        surface.blit(gs, (0, ground_y))
