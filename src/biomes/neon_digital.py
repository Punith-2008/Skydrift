"""
src/biomes/neon_digital.py
Biome 8 — Neon Digital Dimension
Tron-like grid, data streams, glowing geometry, electric palette.
"""

import pygame
import random
import math
from .base_biome import BaseBiome


class NeonDigitalBiome(BaseBiome):
    NAME = "neon_digital"
    MUSIC_KEY = "neon_digital"
    WEATHER_MODE = "none"
    TRANSITION_MODE = "chromatic"
    SKY_TOP = (0, 2, 15)
    SKY_BOTTOM = (0, 5, 30)
    PIPE_COLOR = (0, 255, 200)
    PIPE_ACCENT = (255, 0, 200)
    PIPE_DARK = (0, 80, 80)
    GROUND_COLOR = (0, 20, 40)
    GROUND_LINE = (0, 255, 200)
    AMBIENT_PARTICLE = "neon"

    NEON_COLS = [(0,255,200),(255,0,200),(255,200,0),(0,150,255),(200,0,255)]

    def _build_layers(self):
        self._grid_offset = 0.0
        self._data_streams = [
            {"x": random.randint(0, self.w), "speed": random.uniform(100, 300),
             "color": random.choice(self.NEON_COLS), "length": random.randint(30, 100)}
            for _ in range(20)
        ]
        self._hexagons = [
            {"x": random.randint(0, self.w * 2),
             "y": random.randint(int(self.h*0.1), int(self.h*0.8)),
             "r": random.randint(20, 60),
             "color": random.choice(self.NEON_COLS),
             "phase": random.uniform(0, 6.28),
             "rot_speed": random.uniform(-1.0, 1.0)}
            for _ in range(15)
        ]

    def draw_background(self, surface: pygame.Surface, scroll_x: float) -> None:
        self._draw_sky_gradient(surface)
        t = pygame.time.get_ticks() / 1000.0

        # Perspective grid
        self._draw_grid(surface, scroll_x, t)

        # Hexagons
        for hex_obj in self._hexagons:
            hx = int((hex_obj["x"] - scroll_x * 0.3) % (self.w * 2 + 100))
            hy = hex_obj["y"]
            r = hex_obj["r"]
            angle = t * hex_obj["rot_speed"] + hex_obj["phase"]
            col = hex_obj["color"]
            points = [
                (hx + r * math.cos(angle + i * math.pi / 3),
                 hy + r * math.sin(angle + i * math.pi / 3))
                for i in range(6)
            ]
            pulse = 0.5 + 0.5 * math.sin(t * 2 + hex_obj["phase"])
            alpha = int(60 + 80 * pulse)
            hs = pygame.Surface((r*3, r*3), pygame.SRCALPHA)
            hpoints = [(p[0] - hx + r*3//2, p[1] - hy + r*3//2) for p in points]
            pygame.draw.polygon(hs, (*col, alpha), hpoints, 2)
            surface.blit(hs, (hx - r*3//2, hy - r*3//2), special_flags=pygame.BLEND_RGBA_ADD)

        # Data streams (vertical lines flying upward)
        for stream in self._data_streams:
            sx = int((stream["x"] + scroll_x * 0.1) % self.w)
            sy = int((t * stream["speed"]) % self.h)
            col = stream["color"]
            length = stream["length"]
            for i in range(0, length, 6):
                alpha = int(200 * (1 - i / length))
                ps = pygame.Surface((2, 4), pygame.SRCALPHA)
                ps.fill((*col, alpha))
                surface.blit(ps, (sx, (sy + i) % self.h), special_flags=pygame.BLEND_RGBA_ADD)

    def _draw_grid(self, surface, scroll_x, t):
        col = (0, 80, 60)
        grid_size = 60
        offset_x = int(scroll_x * 0.5) % grid_size
        offset_y = int(t * 40) % grid_size

        for x in range(-grid_size, self.w + grid_size, grid_size):
            pygame.draw.line(surface, col, (x - offset_x, 0), (x - offset_x, self.h), 1)
        for y in range(0, self.h + grid_size, grid_size):
            pygame.draw.line(surface, col, (0, y - offset_y), (self.w, y - offset_y), 1)
