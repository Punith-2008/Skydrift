"""
src/biomes/jungle.py
Biome 5 — Jungle Ruins
Ancient temples, vines, fireflies, green/gold palette.
"""

import pygame
import random
import math
from .base_biome import BaseBiome


class JungleBiome(BaseBiome):
    NAME = "jungle"
    MUSIC_KEY = "jungle"
    WEATHER_MODE = "fog"
    TRANSITION_MODE = "dissolve"
    SKY_TOP = (10, 25, 10)
    SKY_BOTTOM = (20, 50, 20)
    PIPE_COLOR = (60, 140, 30)
    PIPE_ACCENT = (120, 200, 40)
    PIPE_DARK = (20, 60, 10)
    GROUND_COLOR = (40, 70, 15)
    GROUND_LINE = (80, 160, 30)
    AMBIENT_PARTICLE = "sparks"

    def _build_layers(self):
        self._temples = self._gen_temples(5)
        self._trees_far = self._gen_tree_layer(20, 0.2, (20,50,15))
        self._trees_near = self._gen_tree_layer(14, 0.5, (30,70,20))
        self._vines = [
            {"x": random.randint(0, self.w*2), "len": random.randint(50,150),
             "sway_phase": random.uniform(0, 6.28)}
            for _ in range(30)
        ]

    def _gen_temples(self, count):
        items = []
        x = 0
        for _ in range(count):
            w = random.randint(80, 180)
            h = random.randint(60, 140)
            items.append({"x": x, "w": w, "h": h, "tiers": random.randint(2,4)})
            x += w + random.randint(80, 200)
        return {"items": items, "total_w": max(x, self.w*2)}

    def _gen_tree_layer(self, count, speed, color):
        items = []
        x = 0
        for _ in range(count):
            w = random.randint(40, 90)
            h = random.randint(60, 120)
            items.append({"x": x, "w": w, "h": h, "color": color})
            x += w + random.randint(10, 50)
        return {"items": items, "total_w": max(x, self.w*2), "speed": speed}

    def draw_background(self, surface: pygame.Surface, scroll_x: float) -> None:
        self._draw_sky_gradient(surface)
        t = pygame.time.get_ticks() / 1000.0

        # Far trees
        self._draw_trees(surface, self._trees_far, scroll_x)
        # Temples
        tmpl = self._temples
        for v in tmpl["items"]:
            tx = int((v["x"] - scroll_x * 0.25) % tmpl["total_w"])
            self._draw_temple(surface, tx, v)
        # Near trees
        self._draw_trees(surface, self._trees_near, scroll_x)
        # Vines
        for vine in self._vines:
            vx = int((vine["x"] - scroll_x * 0.6) % (self.w * 2 + 20))
            sway = int(8 * math.sin(t * 0.8 + vine["sway_phase"]))
            pygame.draw.line(surface, (20, 80, 10),
                             (vx, 0), (vx + sway, vine["len"]), 2)

    def _draw_temple(self, surface, tx, v):
        by = self.h - 60
        tiers = v["tiers"]
        tier_h = v["h"] // tiers
        for i in range(tiers):
            tw = v["w"] - i * (v["w"] // (tiers + 1))
            tx_off = (v["w"] - tw) // 2
            ty = by - (i + 1) * tier_h
            pygame.draw.rect(surface, (80, 70, 40),
                             (tx + tx_off, ty, tw, tier_h))
            pygame.draw.rect(surface, (100, 90, 60),
                             (tx + tx_off, ty, tw, tier_h), 1)

    def _draw_trees(self, surface, layer, scroll_x):
        total = layer["total_w"]
        speed = layer["speed"]
        for tree in layer["items"]:
            bx = int((tree["x"] - scroll_x * speed) % total)
            by = self.h - 60 - tree["h"]
            # Trunk
            pygame.draw.rect(surface, (40,25,10),
                             (bx + tree["w"]//2 - 4, by + tree["h"]//2, 8, tree["h"]//2))
            # Canopy
            col = tree["color"]
            pygame.draw.circle(surface, col, (bx + tree["w"]//2, by + tree["h"]//3), tree["w"]//2)
            pygame.draw.circle(surface, (min(255,col[0]+20), min(255,col[1]+30), min(255,col[2]+10)),
                               (bx + tree["w"]//2 - 8, by + tree["h"]//3 - 5), tree["w"]//3)
