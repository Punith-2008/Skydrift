"""
src/biomes/ocean.py
Biome 6 — Ocean Depths
Underwater scene, coral, fish schools, bubbles, teal/blue palette.
"""

import pygame
import random
import math
from .base_biome import BaseBiome


class OceanBiome(BaseBiome):
    NAME = "ocean"
    MUSIC_KEY = "ocean"
    WEATHER_MODE = "ocean_fog"
    TRANSITION_MODE = "fade"
    SKY_TOP = (5, 30, 70)
    SKY_BOTTOM = (10, 60, 120)
    PIPE_COLOR = (20, 120, 160)
    PIPE_ACCENT = (0, 200, 200)
    PIPE_DARK = (10, 60, 90)
    GROUND_COLOR = (20, 60, 100)
    GROUND_LINE = (0, 180, 200)
    AMBIENT_PARTICLE = "bubbles"

    def _build_layers(self):
        self._coral = self._gen_coral(20)
        self._fish_schools = [
            {"x": random.randint(0, self.w*2),
             "y": random.randint(int(self.h*0.2), int(self.h*0.7)),
             "speed": random.uniform(80, 180),
             "count": random.randint(4, 10),
             "color": random.choice([(255,140,0),(255,80,80),(200,200,100),(100,200,255)])}
            for _ in range(8)
        ]
        self._caustics = self._gen_caustics()

    def _gen_coral(self, count):
        items = []
        x = 0
        for _ in range(count):
            col = random.choice([(255,80,80),(255,160,0),(200,0,200),(0,200,200)])
            items.append({
                "x": x % (self.w * 2),
                "h": random.randint(20, 60),
                "w": random.randint(6, 14),
                "color": col,
                "branches": random.randint(2, 5)
            })
            x += random.randint(20, 80)
        return items

    def _gen_caustics(self):
        caustics = []
        for _ in range(15):
            caustics.append({
                "x": random.randint(0, self.w),
                "y": random.randint(0, self.h),
                "r": random.randint(20, 60),
                "phase": random.uniform(0, 6.28),
            })
        return caustics

    def draw_background(self, surface: pygame.Surface, scroll_x: float) -> None:
        self._draw_sky_gradient(surface)
        t = pygame.time.get_ticks() / 1000.0

        # Caustic light beams
        for caus in self._caustics:
            pulse = 0.3 + 0.7 * (0.5 + 0.5 * math.sin(t * 1.5 + caus["phase"]))
            r = int(caus["r"] * pulse)
            csurf = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(csurf, (0, 180, 220, 25), (r, r), r)
            surface.blit(csurf, (caus["x"] - r, caus["y"] - r),
                          special_flags=pygame.BLEND_RGBA_ADD)

        # Coral
        for coral in self._coral:
            cx = int((coral["x"] - scroll_x * 0.4) % (self.w * 2 + 20))
            self._draw_coral(surface, cx, coral)

        # Fish schools
        for fish in self._fish_schools:
            fx = int((fish["x"] - scroll_x * 0.7 + pygame.time.get_ticks() * fish["speed"] * 0.0001) % (self.w * 2))
            for i in range(fish["count"]):
                fsx = fx + int(math.sin(t * 2 + i) * 15)
                fsy = fish["y"] + int(math.cos(t * 1.5 + i * 1.2) * 10) + i * 8
                pygame.draw.circle(surface, fish["color"], (fsx, fsy), 5)
                pygame.draw.polygon(surface, fish["color"], [
                    (fsx - 8, fsy), (fsx - 14, fsy - 4), (fsx - 14, fsy + 4)
                ])

    def _draw_coral(self, surface, cx, coral):
        base_y = self.h - 65
        col = coral["color"]
        pygame.draw.line(surface, col,
                         (cx, base_y), (cx, base_y - coral["h"]), coral["w"])
        for b in range(coral["branches"]):
            t_val = (b + 1) / (coral["branches"] + 1)
            branch_y = base_y - int(coral["h"] * t_val)
            side = 1 if b % 2 == 0 else -1
            pygame.draw.line(surface, col,
                             (cx, branch_y),
                             (cx + side * 20, branch_y - 15), coral["w"] - 2)

    def draw_foreground(self, surface: pygame.Surface, scroll_x: float) -> None:
        # Subtle blue water overlay
        ov = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        ov.fill((0, 60, 120, 15))
        surface.blit(ov, (0, 0))
