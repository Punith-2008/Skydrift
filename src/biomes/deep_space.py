"""
src/biomes/deep_space.py
Biome 4 — Deep Space
Nebulas, stars, planets, asteroid fields, deep purple palette.
"""

import pygame
import random
import math
from .base_biome import BaseBiome


class DeepSpaceBiome(BaseBiome):
    NAME = "deep_space"
    MUSIC_KEY = "deep_space"
    WEATHER_MODE = "space_fog"
    TRANSITION_MODE = "fade"
    SKY_TOP = (2, 0, 8)
    SKY_BOTTOM = (8, 2, 18)
    PIPE_COLOR = (120, 60, 200)
    PIPE_ACCENT = (200, 100, 255)
    PIPE_DARK = (50, 20, 90)
    GROUND_COLOR = (30, 15, 50)
    GROUND_LINE = (120, 60, 200)
    AMBIENT_PARTICLE = "stars"

    def _build_layers(self):
        self._stars_far  = self._make_stars(200, self.w * 3, self.h, 1)
        self._stars_near = self._make_stars(80,  self.w * 2, self.h, 2)
        self._nebula_patches = self._gen_nebulas(8)
        self._planets = self._gen_planets(3)

    def _gen_nebulas(self, count):
        patches = []
        for _ in range(count):
            col = random.choice([(80,0,120),(0,60,140),(140,0,60),(0,100,80),(60,40,120)])
            patches.append({
                "x": random.randint(0, self.w * 3),
                "y": random.randint(0, self.h),
                "rx": random.randint(80, 200),
                "ry": random.randint(50, 130),
                "color": col,
                "alpha": random.randint(20, 50),
            })
        return patches

    def _gen_planets(self, count):
        planets = []
        for _ in range(count):
            col = random.choice([(180,80,40),(80,120,200),(200,160,60),(100,180,100)])
            planets.append({
                "x": random.randint(0, self.w * 3),
                "y": random.randint(int(self.h * 0.1), int(self.h * 0.6)),
                "r": random.randint(25, 70),
                "color": col,
                "ring": random.random() > 0.5,
            })
        return planets

    def draw_background(self, surface: pygame.Surface, scroll_x: float) -> None:
        self._draw_sky_gradient(surface)
        self._draw_star_field(surface, self._stars_far, 0.05, scroll_x)
        for neb in self._nebula_patches:
            nx = int((neb["x"] - scroll_x * 0.08) % (self.w * 3 + 200))
            ns = pygame.Surface((neb["rx"]*2, neb["ry"]*2), pygame.SRCALPHA)
            pygame.draw.ellipse(ns, (*neb["color"], neb["alpha"]), (0,0,neb["rx"]*2,neb["ry"]*2))
            surface.blit(ns, (nx-neb["rx"], neb["y"]-neb["ry"]), special_flags=pygame.BLEND_RGBA_ADD)
        self._draw_star_field(surface, self._stars_near, 0.12, scroll_x)
        for planet in self._planets:
            px = int((planet["x"] - scroll_x * 0.2) % (self.w * 3 + 200))
            py = planet["y"]
            r = planet["r"]
            pygame.draw.circle(surface, planet["color"], (px, py), r)
            shadow = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(shadow, (0,0,0,100), (r,r), r)
            surface.blit(shadow, (px-r+r//3, py-r))
            if planet["ring"]:
                rs = pygame.Surface((r*3, r//2), pygame.SRCALPHA)
                pygame.draw.ellipse(rs, (*planet["color"],120), (0,0,r*3,r//2), 3)
                surface.blit(rs, (px-r*3//2, py-r//4))
