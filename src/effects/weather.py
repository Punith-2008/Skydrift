"""
src/effects/weather.py
Weather effects: rain, snow, fog layers, lightning, sandstorm.
"""

import pygame
import random
import math


class FogLayer:
    """A single horizontally scrolling fog strip."""

    def __init__(self, y: float, height: int, color: tuple,
                 speed: float, alpha: int, width: int):
        self.y = y
        self.height = height
        self.color = color
        self.speed = speed
        self.alpha = alpha
        self.width = width
        self.offset = 0.0
        self._surf = self._build(width * 2, height, color, alpha)

    def _build(self, w: int, h: int, color: tuple, alpha: int) -> pygame.Surface:
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        # Wavy fog using vertical sine bands
        for x in range(w):
            band_alpha = alpha * (0.5 + 0.5 * math.sin(x * 0.015))
            a = int(max(0, min(255, band_alpha)))
            pygame.draw.line(surf, (*color[:3], a), (x, 0), (x, h))
        return surf

    def update(self, dt: float) -> None:
        self.offset = (self.offset + self.speed * dt) % self.width

    def draw(self, surface: pygame.Surface) -> None:
        ox = -int(self.offset)
        surface.blit(self._surf, (ox, int(self.y)))
        if ox + self._surf.get_width() < surface.get_width():
            surface.blit(self._surf, (ox + self._surf.get_width(), int(self.y)))


class WeatherSystem:
    """
    Manages weather drops (rain/snow/sand) as a lightweight numpy-free system.
    Uses a pre-allocated list for performance.
    """

    def __init__(self, screen_w: int, screen_h: int):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.mode = "none"   # rain | snow | sand | none
        self._drops: list = []
        self._fog_layers: list = []
        self._lightning_timer: float = 0.0
        self._lightning_flash: float = 0.0
        self._lightning_surf: pygame.Surface = None

    def set_mode(self, mode: str) -> None:
        if mode == self.mode:
            return
        self.mode = mode
        self._drops.clear()
        self._fog_layers.clear()
        self._lightning_flash = 0.0

        if mode == "rain":
            self._lightning_timer = random.uniform(3, 8)
        elif mode == "fog":
            self._build_fog(color=(180, 200, 220))
        elif mode == "snow_fog":
            self._build_fog(color=(200, 220, 255))
        elif mode == "lava_fog":
            self._build_fog(color=(255, 100, 40))
        elif mode == "space_fog":
            self._build_fog(color=(80, 40, 120))
        elif mode == "ocean_fog":
            self._build_fog(color=(30, 80, 160))

    def _build_fog(self, color: tuple) -> None:
        h = self.screen_h
        w = self.screen_w
        self._fog_layers = [
            FogLayer(h * 0.6, int(h * 0.4), color, 12, 35, w),
            FogLayer(h * 0.75, int(h * 0.25), color, 20, 55, w),
            FogLayer(h * 0.85, int(h * 0.15), color, 30, 75, w),
        ]

    # ── Update ────────────────────────────────────────────────────────────────
    def update(self, dt: float) -> None:
        for fl in self._fog_layers:
            fl.update(dt)

        if self.mode == "rain":
            self._update_rain(dt)
        elif self.mode == "snow":
            self._update_snow(dt)
        elif self.mode == "sand":
            self._update_sand(dt)

        # Lightning
        if self._lightning_flash > 0:
            self._lightning_flash -= dt * 3
        if self.mode == "rain":
            self._lightning_timer -= dt
            if self._lightning_timer <= 0:
                self._lightning_flash = 1.0
                self._lightning_timer = random.uniform(4, 12)

    def _update_rain(self, dt: float) -> None:
        # Spawn
        for _ in range(8):
            if len(self._drops) < 300:
                self._drops.append([
                    random.uniform(0, self.screen_w),
                    random.uniform(-20, 0),
                    random.uniform(500, 700),  # vy
                    random.uniform(8, 14),     # length
                ])
        # Move
        alive = []
        for d in self._drops:
            d[1] += d[2] * dt
            d[0] -= d[2] * 0.1 * dt  # slight diagonal
            if d[1] < self.screen_h:
                alive.append(d)
        self._drops = alive

    def _update_snow(self, dt: float) -> None:
        for _ in range(3):
            if len(self._drops) < 200:
                self._drops.append([
                    random.uniform(0, self.screen_w),
                    random.uniform(-10, 0),
                    random.uniform(50, 120),
                    random.uniform(2, 5),     # radius
                    random.uniform(-30, 30),  # vx drift
                ])
        alive = []
        for d in self._drops:
            d[1] += d[2] * dt
            d[0] += d[4] * dt
            if d[1] < self.screen_h:
                alive.append(d)
        self._drops = alive

    def _update_sand(self, dt: float) -> None:
        for _ in range(12):
            if len(self._drops) < 400:
                self._drops.append([
                    random.uniform(-50, self.screen_w * 0.3),
                    random.uniform(0, self.screen_h),
                    random.uniform(300, 600),  # vx (horizontal wind)
                    random.uniform(1, 3),      # size
                    random.uniform(-20, 20),   # vy
                ])
        alive = []
        for d in self._drops:
            d[0] += d[2] * dt
            d[1] += d[4] * dt
            if d[0] < self.screen_w + 50:
                alive.append(d)
        self._drops = alive

    # ── Draw ──────────────────────────────────────────────────────────────────
    def draw(self, surface: pygame.Surface) -> None:
        # Draw fog layers behind drops
        for fl in self._fog_layers:
            fl.draw(surface)

        if self.mode == "rain":
            self._draw_rain(surface)
        elif self.mode == "snow":
            self._draw_snow(surface)
        elif self.mode == "sand":
            self._draw_sand(surface)

        # Lightning flash overlay
        if self._lightning_flash > 0.01:
            flash_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            alpha = int(self._lightning_flash * 80)
            flash_surf.fill((220, 230, 255, alpha))
            surface.blit(flash_surf, (0, 0))

    def _draw_rain(self, surface: pygame.Surface) -> None:
        for d in self._drops:
            x, y, vy, length = d
            alpha = random.randint(120, 200)
            pygame.draw.line(surface, (150, 190, 255),
                             (int(x), int(y)),
                             (int(x - length * 0.15), int(y + length)), 1)

    def _draw_snow(self, surface: pygame.Surface) -> None:
        for d in self._drops:
            x, y, _, r, _ = d
            pygame.draw.circle(surface, (210, 230, 255), (int(x), int(y)), int(r))

    def _draw_sand(self, surface: pygame.Surface) -> None:
        for d in self._drops:
            x, y, _, size, _ = d
            color = (random.randint(200, 240), random.randint(160, 200), 80)
            pygame.draw.circle(surface, color, (int(x), int(y)), int(size))
