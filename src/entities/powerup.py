"""
src/entities/powerup.py
Power-up entities: Shield, SlowMo, Magnet (coin attractor).
"""

import pygame
import math
import random


POWERUP_TYPES = ["shield", "slowmo", "magnet"]

POWERUP_COLORS = {
    "shield": (0, 200, 255),
    "slowmo": (200, 100, 255),
    "magnet": (255, 180, 0),
}

POWERUP_ICONS = {
    "shield": "🛡",
    "slowmo": "⏱",
    "magnet": "🧲",
}


class PowerUp:
    RADIUS = 14

    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.speed = 0.0
        self.kind = "shield"
        self.active = False
        self.collected = False
        self._phase = 0.0
        self._anim_timer = 0.0

    def activate(self, x, y, speed, kind):
        self.x = x; self.y = y
        self.speed = speed; self.kind = kind
        self.active = True; self.collected = False
        self._phase = random.uniform(0, 6.28)
        self._anim_timer = 0.0

    def update(self, dt, time_scale=1.0):
        if not self.active:
            return
        if self.collected:
            self._anim_timer += dt
            if self._anim_timer > 0.6:
                self.active = False
            return
        self.x -= self.speed * dt * time_scale
        self._phase += dt * 2.5
        if self.x + self.RADIUS < -10:
            self.active = False

    def collect(self):
        if not self.collected:
            self.collected = True
            self._anim_timer = 0.0

    @property
    def rect(self):
        r = self.RADIUS
        return pygame.Rect(int(self.x)-r, int(self.y)-r, r*2, r*2)

    def draw(self, surface, offset=(0,0)):
        if not self.active:
            return
        ox, oy = offset
        cx = int(self.x + ox)
        cy = int(self.y + oy) + int(math.sin(self._phase) * 5)
        col = POWERUP_COLORS[self.kind]

        if self.collected:
            t = min(1.0, self._anim_timer / 0.6)
            alpha = int(255 * (1 - t))
            cy -= int(t * 40)
            r = int(self.RADIUS * (1 + t))
            ps = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(ps, (*col, alpha), (r, r), r)
            surface.blit(ps, (cx-r, cy-r), special_flags=pygame.BLEND_RGBA_ADD)
            return

        r = self.RADIUS
        # Outer glow
        for gr in range(r+12, r, -3):
            a = int(40 * (1 - (gr-r)/12))
            gs = pygame.Surface((gr*2, gr*2), pygame.SRCALPHA)
            pygame.draw.circle(gs, (*col, a), (gr, gr), gr)
            surface.blit(gs, (cx-gr, cy-gr), special_flags=pygame.BLEND_RGBA_ADD)

        # Background circle
        pygame.draw.circle(surface, (20, 20, 40), (cx, cy), r)
        pygame.draw.circle(surface, col, (cx, cy), r, 2)

        # Icon (simple geometric for each type)
        if self.kind == "shield":
            pts = [(cx, cy-r+4), (cx+r-4, cy), (cx, cy+r-4), (cx-r+4, cy)]
            pygame.draw.polygon(surface, col, pts)
        elif self.kind == "slowmo":
            pygame.draw.circle(surface, col, (cx, cy), r-4, 2)
            pygame.draw.line(surface, col, (cx, cy), (cx+6, cy-5), 2)
            pygame.draw.line(surface, col, (cx, cy-r+5), (cx, cy), 2)
        elif self.kind == "magnet":
            pygame.draw.arc(surface, col,
                            (cx-r+5, cy-r+3, (r-5)*2, (r-5)*2),
                            0, math.pi, 3)
            pygame.draw.line(surface, col, (cx-r+5, cy), (cx-r+5, cy+4), 3)
            pygame.draw.line(surface, col, (cx+r-5, cy), (cx+r-5, cy+4), 3)


class PowerUpManager:
    POOL_SIZE = 6

    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self._pool = [PowerUp() for _ in range(self.POOL_SIZE)]
        self.speed = 200.0

    def reset(self, speed):
        self.speed = speed
        for p in self._pool:
            p.active = False

    def update(self, dt, bird_rect, bird, time_scale=1.0):
        """Returns collected powerup type or None."""
        collected_type = None
        for pu in self._pool:
            pu.update(dt, time_scale)
            if pu.active and not pu.collected and pu.rect.colliderect(bird_rect):
                pu.collect()
                collected_type = pu.kind
                self._apply(pu.kind, bird)
        return collected_type

    def _apply(self, kind, bird):
        if kind == "shield":
            bird.activate_shield(6.0)
        # slowmo and magnet are handled by the game state

    def spawn_safe(self, x, y, speed):
        for pu in self._pool:
            if not pu.active:
                kind = random.choice(POWERUP_TYPES)
                pu.activate(x, y, speed, kind)
                return

    def draw(self, surface, offset=(0,0)):
        for pu in self._pool:
            if pu.active:
                pu.draw(surface, offset)
