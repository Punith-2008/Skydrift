"""
src/biomes/desert.py
Biome 7 — Desert Storm
Sand dunes, pyramids, sandstorm particles, orange/tan palette.
"""

import pygame
import random
import math
from .base_biome import BaseBiome


class DesertBiome(BaseBiome):
    NAME = "desert"
    MUSIC_KEY = "desert"
    WEATHER_MODE = "sand"
    TRANSITION_MODE = "dissolve"
    SKY_TOP = (40, 25, 10)
    SKY_BOTTOM = (120, 80, 30)
    PIPE_COLOR = (180, 130, 50)
    PIPE_ACCENT = (240, 180, 80)
    PIPE_DARK = (100, 60, 20)
    GROUND_COLOR = (200, 160, 80)
    GROUND_LINE = (240, 200, 100)
    AMBIENT_PARTICLE = "sparks"

    def _build_layers(self):
        self._dunes_far  = self._gen_dunes(12, (140, 100, 40), 0.1)
        self._dunes_near = self._gen_dunes(8,  (180, 140, 60), 0.35)
        self._pyramids   = self._gen_pyramids(5)
        self._mirages    = [
            {"x": random.randint(0, self.w*2), "y": int(self.h*0.75),
             "w": random.randint(60, 120), "phase": random.uniform(0, 6.28)}
            for _ in range(4)
        ]

    def _gen_dunes(self, count, color, speed):
        dunes = []
        x = 0
        for _ in range(count):
            w = random.randint(120, 280)
            h = random.randint(30, 90)
            dunes.append({"x": x, "w": w, "h": h, "color": color})
            x += w - random.randint(20, 60)
        return {"items": dunes, "total_w": max(x, self.w*2), "speed": speed}

    def _gen_pyramids(self, count):
        items = []
        x = 0
        for _ in range(count):
            w = random.randint(80, 160)
            h = random.randint(70, 150)
            items.append({"x": x, "w": w, "h": h})
            x += w + random.randint(100, 250)
        return {"items": items, "total_w": max(x, self.w*2)}

    def draw_background(self, surface: pygame.Surface, scroll_x: float) -> None:
        self._draw_sky_gradient(surface)
        t = pygame.time.get_ticks() / 1000.0

        # Sun
        sun_x = int(self.w * 0.8)
        sun_y = int(self.h * 0.2)
        pygame.draw.circle(surface, (255, 200, 60), (sun_x, sun_y), 35)
        for r in range(60, 0, -5):
            alpha = int(30 * r / 60)
            gsurf = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(gsurf, (255, 180, 40, alpha), (r, r), r)
            surface.blit(gsurf, (sun_x - r, sun_y - r), special_flags=pygame.BLEND_RGBA_ADD)

        # Far dunes
        self._draw_dune_layer(surface, self._dunes_far, scroll_x)

        # Pyramids
        pyrs = self._pyramids
        for p in pyrs["items"]:
            px = int((p["x"] - scroll_x * 0.22) % pyrs["total_w"])
            py = self.h - 60 - p["h"]
            half = p["w"] // 2
            pygame.draw.polygon(surface, (100, 75, 25),
                                [(px, py + p["h"]),
                                 (px + p["w"], py + p["h"]),
                                 (px + half, py)])
            pygame.draw.polygon(surface, (130, 100, 40),
                                [(px, py + p["h"]),
                                 (px + half, py + p["h"]),
                                 (px + half, py)])

        # Near dunes
        self._draw_dune_layer(surface, self._dunes_near, scroll_x)

        # Mirages
        for mir in self._mirages:
            mx = int((mir["x"] - scroll_x * 0.5) % (self.w * 2 + 20))
            alpha = int(40 + 30 * math.sin(t * 1.5 + mir["phase"]))
            ms = pygame.Surface((mir["w"], 12), pygame.SRCALPHA)
            ms.fill((180, 220, 255, alpha))
            surface.blit(ms, (mx, mir["y"]))

    def _draw_dune_layer(self, surface, layer, scroll_x):
        total = layer["total_w"]
        speed = layer["speed"]
        for dune in layer["items"]:
            dx = int((dune["x"] - scroll_x * speed) % total)
            by = self.h - 60
            half = dune["w"] // 2
            pygame.draw.ellipse(surface, dune["color"],
                                (dx - dune["w"]//4, by - dune["h"],
                                 dune["w"], dune["h"] * 2))
