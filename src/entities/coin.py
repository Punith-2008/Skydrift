"""
src/entities/coin.py
Collectible coin with glow and collection animation.

Coin placement rules
--------------------
* Coins are ALWAYS placed inside the pipe gap, never inside a pipe body.
* A safety margin (COIN_GAP_MARGIN) is kept from each pipe edge so the
  player never needs frame-perfect manoeuvres.
* Five patterns are available; harder patterns unlock gradually via
  the difficulty_level parameter (derived from score in game.py).
* Every coin Y is validated/clamped through _safe_y() before spawning.
"""

import pygame
import math
import random


# ── Tunable constants ─────────────────────────────────────────────────────────
COIN_GAP_MARGIN  = 30   # pixels of clearance from each pipe edge
COIN_GAP_FALLBACK = 140  # assumed gap height when none is supplied (safe default)


class Coin:
    RADIUS = 10

    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.speed = 0.0
        self.active = False
        self.collected = False
        self._phase = 0.0
        self._anim_timer = 0.0
        self.value = 1

    def activate(self, x, y, speed, value=1):
        self.x = x; self.y = y; self.speed = speed
        self.active = True; self.collected = False
        self._phase = random.uniform(0, 6.28)
        self._anim_timer = 0.0; self.value = value

    def update(self, dt, time_scale=1.0):
        if not self.active:
            return
        if self.collected:
            self._anim_timer += dt
            if self._anim_timer > 0.5:
                self.active = False
            return
        self.x -= self.speed * dt * time_scale
        self._phase += dt * 3.0
        if self.x + self.RADIUS < -10:
            self.active = False

    def collect(self):
        if not self.collected:
            self.collected = True
            self._anim_timer = 0.0

    @property
    def rect(self):
        r = self.RADIUS
        return pygame.Rect(int(self.x) - r, int(self.y) - r, r * 2, r * 2)

    def draw(self, surface, offset=(0, 0)):
        if not self.active:
            return
        ox, oy = offset
        cx = int(self.x + ox)
        cy = int(self.y + oy)

        if self.collected:
            t = self._anim_timer / 0.5
            cy -= int(t * 30)
            alpha = int(255 * (1 - t))
            cs = pygame.Surface((self.RADIUS * 4, self.RADIUS * 4), pygame.SRCALPHA)
            pygame.draw.circle(cs, (255, 215, 0, alpha),
                               (self.RADIUS * 2, self.RADIUS * 2), self.RADIUS)
            surface.blit(cs, (cx - self.RADIUS * 2, cy - self.RADIUS * 2))
            return

        # Spinning coin illusion (x-axis squish)
        squeeze = abs(math.cos(self._phase))
        rx = max(2, int(self.RADIUS * squeeze))
        ry = self.RADIUS

        # Outer glow
        gs = pygame.Surface((ry * 4, ry * 4), pygame.SRCALPHA)
        pygame.draw.circle(gs, (255, 200, 0, 40), (ry * 2, ry * 2), ry * 2)
        surface.blit(gs, (cx - ry * 2, cy - ry * 2),
                     special_flags=pygame.BLEND_RGBA_ADD)

        # Coin body
        pygame.draw.ellipse(surface, (255, 180, 0),
                            (cx - rx, cy - ry, rx * 2, ry * 2))
        pygame.draw.ellipse(surface, (255, 230, 80),
                            (cx - rx // 2, cy - ry // 2, max(2, rx), ry))
        pygame.draw.ellipse(surface, (200, 130, 0),
                            (cx - rx, cy - ry, rx * 2, ry * 2), 1)


# ── CoinManager ───────────────────────────────────────────────────────────────

class CoinManager:
    POOL_SIZE = 30   # increased to support larger patterns

    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self._pool = [Coin() for _ in range(self.POOL_SIZE)]
        self.speed = 200.0

    # ── Lifecycle ─────────────────────────────────────────────────────────────
    def reset(self, speed):
        self.speed = speed
        for c in self._pool:
            c.active = False

    def update(self, dt, bird_rect, time_scale=1.0):
        collected = 0
        for coin in self._pool:
            coin.update(dt, time_scale)
            if coin.active and not coin.collected and coin.rect.colliderect(bird_rect):
                coin.collect()
                collected += coin.value
        return collected

    def draw(self, surface, offset=(0, 0)):
        for coin in self._pool:
            if coin.active:
                coin.draw(surface, offset)

    # ── Public spawn API ──────────────────────────────────────────────────────
    def spawn_pattern(self, start_x, gap_center_y, speed,
                      gap_h=None, difficulty_level=0):
        """Spawn a coin pattern entirely inside the pipe gap.

        Parameters
        ----------
        start_x        : left edge X for the pattern (pixels to the right of the pipe)
        gap_center_y   : vertical centre of the pipe gap
        speed          : horizontal scroll speed
        gap_h          : full height of the pipe gap (pixels); uses safe fallback if None
        difficulty_level: integer 0–4 controlling which patterns are eligible
        """
        if gap_h is None:
            gap_h = COIN_GAP_FALLBACK

        # The usable vertical range (with margin from each pipe lip)
        safe_h = gap_h - COIN_GAP_MARGIN * 2
        if safe_h < Coin.RADIUS * 4:
            # Gap is very tight — place just one centre coin
            self._place(start_x, gap_center_y, speed, value=3)
            return

        # Choose pattern based on allowed difficulty
        # Difficulty 0: single only
        # Difficulty 1: + line
        # Difficulty 2: + arc
        # Difficulty 3: + wave
        # Difficulty 4: + diamond
        max_pattern = min(difficulty_level, 4)
        pattern_pool = ["single", "line", "arc", "wave", "diamond"][:max_pattern + 1]
        pattern = random.choice(pattern_pool)

        if pattern == "single":
            self._pattern_single(start_x, gap_center_y, speed)
        elif pattern == "line":
            self._pattern_line(start_x, gap_center_y, speed)
        elif pattern == "arc":
            self._pattern_arc(start_x, gap_center_y, speed, safe_h)
        elif pattern == "wave":
            self._pattern_wave(start_x, gap_center_y, speed, safe_h)
        elif pattern == "diamond":
            self._pattern_diamond(start_x, gap_center_y, speed, safe_h)

    # ── Placement patterns ────────────────────────────────────────────────────

    def _pattern_single(self, sx, cy, speed):
        """One coin right at gap centre — always safe, high value."""
        self._place(sx + 20, cy, speed, value=3)

    def _pattern_line(self, sx, cy, speed):
        """3 coins in a horizontal line at gap centre."""
        for i in range(3):
            self._place(sx + i * 38, cy, speed, value=1)

    def _pattern_arc(self, sx, cy, speed, safe_h):
        """5 coins in a concave arc (valley shape).
        The arc peak deviation is ≤ safe_h/2.5 so coins stay well inside."""
        count = 5
        half_amp = min(safe_h * 0.35, 40)  # max vertical swing
        for i in range(count):
            t = i / (count - 1)  # 0..1
            # Valley: dips at the centre, highest at edges
            dy = math.sin(t * math.pi) * half_amp
            self._place(sx + i * 36, cy + dy, speed, value=1)

    def _pattern_wave(self, sx, cy, speed, safe_h):
        """6 coins following one full sine period across the gap."""
        count = 6
        half_amp = min(safe_h * 0.30, 35)
        for i in range(count):
            t = i / (count - 1)  # 0..1
            dy = math.sin(t * 2 * math.pi) * half_amp
            self._place(sx + i * 32, cy + dy, speed, value=1)

    def _pattern_diamond(self, sx, cy, speed, safe_h):
        """4 coins in a diamond shape (top, left, right, bottom)."""
        spread_x = 30
        spread_y = min(safe_h * 0.28, 30)
        positions = [
            (sx + spread_x,          cy - spread_y),   # top
            (sx,                     cy),               # left
            (sx + spread_x * 2,      cy),               # right
            (sx + spread_x,          cy + spread_y),   # bottom
        ]
        for x, y in positions:
            self._place(x, y, speed, value=2)

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _place(self, x, y, speed, value=1):
        """Activate a pooled coin at (x, y) — no extra clamping needed here
        because every pattern already constrains Y to the safe zone."""
        for c in self._pool:
            if not c.active:
                c.activate(float(x), float(y), speed, value)
                return
        # Pool exhausted — silently drop; no crash

    @staticmethod
    def _difficulty_from_score(score: int) -> int:
        """Map score to a difficulty level 0-4 for external callers."""
        if score < 5:
            return 0
        elif score < 15:
            return 1
        elif score < 30:
            return 2
        elif score < 60:
            return 3
        else:
            return 4
