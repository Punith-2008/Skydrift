"""
src/biomes/volcano.py
Biome 2 — Lava Volcano
Molten rock, lava rivers, ash clouds, orange/red palette.
"""

import pygame
import random
import math
from .base_biome import BaseBiome


class VolcanoBiome(BaseBiome):
    NAME = "volcano"
    MUSIC_KEY = "volcano"
    WEATHER_MODE = "lava_fog"
    TRANSITION_MODE = "dissolve"
    SKY_TOP = (20, 5, 5)
    SKY_BOTTOM = (60, 15, 5)
    PIPE_COLOR = (180, 50, 10)
    PIPE_ACCENT = (255, 120, 0)
    PIPE_DARK = (80, 20, 5)
    GROUND_COLOR = (60, 20, 5)
    GROUND_LINE = (255, 80, 0)
    AMBIENT_PARTICLE = "lava"

    def _build_layers(self):
        self._volcanoes = self._gen_volcanoes(6)
        self._lava_rivers = self._gen_lava_rivers(4)
        self._ash_clouds = [
            {"x": random.randint(0, self.w * 2), "y": random.randint(50, 200),
             "r": random.randint(40, 90), "speed": random.uniform(15, 40)}
            for _ in range(20)
        ]

    def _gen_volcanoes(self, count):
        vols = []
        x = 0
        for _ in range(count):
            w = random.randint(100, 220)
            h = random.randint(int(self.h * 0.25), int(self.h * 0.55))
            vols.append({"x": x, "w": w, "h": h,
                          "crater_w": w // 4})
            x += w + random.randint(50, 150)
        return {"items": vols, "total_w": max(x, self.w * 2)}

    def _gen_lava_rivers(self, count):
        rivers = []
        for _ in range(count):
            rivers.append({
                "y": random.randint(int(self.h * 0.65), int(self.h * 0.82)),
                "h": random.randint(12, 30),
                "phase": random.uniform(0, 6.28),
            })
        return rivers

    def draw_background(self, surface: pygame.Surface, scroll_x: float) -> None:
        self._draw_sky_gradient(surface)
        t = pygame.time.get_ticks() / 1000.0

        # Ash clouds (far layer)
        for cloud in self._ash_clouds:
            cx = int((cloud["x"] - scroll_x * 0.1) % (self.w * 2 + cloud["r"] * 2))
            pygame.draw.circle(surface, (45, 35, 35, 100),
                                (cx, cloud["y"]), cloud["r"])

        # Volcanoes (mid layer)
        vols = self._volcanoes
        for v in vols["items"]:
            vx = int((v["x"] - scroll_x * 0.3) % vols["total_w"])
            self._draw_volcano(surface, vx, v, t)

        # Lava rivers
        for river in self._lava_rivers:
            self._draw_lava_river(surface, scroll_x, river, t)

    def _draw_volcano(self, surface, vx, v, t):
        by = self.h
        top_y = by - v["h"]
        half_w = v["w"] // 2
        # Main cone
        points = [
            (vx + half_w - v["crater_w"], top_y),
            (vx + half_w + v["crater_w"], top_y),
            (vx + v["w"], by),
            (vx, by),
        ]
        pygame.draw.polygon(surface, (50, 25, 10), points)
        # Lava glow at crater
        glow_y = top_y
        for r in range(v["crater_w"] * 2, 0, -3):
            alpha = int(80 * (1 - r / (v["crater_w"] * 2)))
            lava_bright = 0.5 + 0.5 * math.sin(t * 3)
            col = (int(255 * lava_bright), int(80 * lava_bright), 0, alpha)
            gs = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(gs, col, (r, r), r)
            surface.blit(gs, (vx + half_w - r, glow_y - r),
                          special_flags=pygame.BLEND_RGBA_ADD)

    def _draw_lava_river(self, surface, scroll_x, river, t):
        y = river["y"]
        h = river["h"]
        lava_surf = pygame.Surface((self.w, h), pygame.SRCALPHA)
        for x in range(self.w):
            wave = math.sin((x + scroll_x * 0.5) * 0.03 + t * 2 + river["phase"])
            bright = 0.7 + 0.3 * wave
            r = int(min(255, 255 * bright))
            g = int(min(180, 100 * bright))
            lava_surf.fill((r, g, 0, 200), (x, 0, 1, h))
        surface.blit(lava_surf, (0, y))
