"""
src/effects/particles.py
Generic, high-performance particle system.
Supports: trail, explosion, ambient, rain, snow, sparks, bubbles, stars.
"""

import pygame
import random
import math
from typing import List, Optional


class Particle:
    """Single lightweight particle."""

    __slots__ = [
        "x", "y", "vx", "vy", "life", "max_life",
        "color", "radius", "gravity", "alpha_decay",
        "shrink", "glow", "trail"
    ]

    def __init__(self, x: float, y: float, vx: float, vy: float,
                 life: float, color: tuple, radius: float = 3.0,
                 gravity: float = 0.0, alpha_decay: bool = True,
                 shrink: bool = True, glow: bool = False, trail: bool = False):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.color = color
        self.radius = radius
        self.gravity = gravity
        self.alpha_decay = alpha_decay
        self.shrink = shrink
        self.glow = glow
        self.trail = trail

    @property
    def alive(self) -> bool:
        return self.life > 0

    @property
    def progress(self) -> float:
        """0 = just born, 1 = dead."""
        return 1.0 - (self.life / self.max_life)

    def update(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        self.life -= dt

    def draw(self, surface: pygame.Surface, offset: tuple = (0, 0)) -> None:
        prog = self.progress
        alpha = int(255 * (1.0 - prog)) if self.alpha_decay else 255
        r = self.radius * (1.0 - prog * 0.7) if self.shrink else self.radius
        r = max(0.5, r)
        alpha = max(0, min(255, alpha))

        px = int(self.x + offset[0])
        py = int(self.y + offset[1])
        ir = int(r)

        if self.glow and ir > 2:
            # Cheap glow: draw larger transparent circle first
            gsurf = pygame.Surface((ir * 4, ir * 4), pygame.SRCALPHA)
            pygame.draw.circle(gsurf, (*self.color[:3], alpha // 3),
                               (ir * 2, ir * 2), ir * 2)
            pygame.draw.circle(gsurf, (*self.color[:3], alpha),
                               (ir * 2, ir * 2), ir)
            surface.blit(gsurf, (px - ir * 2, py - ir * 2),
                         special_flags=pygame.BLEND_RGBA_ADD)
        else:
            if alpha > 10 and ir > 0:
                psurf = pygame.Surface((ir * 2 + 1, ir * 2 + 1), pygame.SRCALPHA)
                pygame.draw.circle(psurf, (*self.color[:3], alpha), (ir, ir), ir)
                surface.blit(psurf, (px - ir, py - ir))


class ParticleEmitter:
    """
    Manages a pool of particles.
    Provides preset configurations for different effect types.
    """

    MAX_PARTICLES = 600

    def __init__(self):
        self._particles: List[Particle] = []

    def count(self) -> int:
        return len(self._particles)

    def clear(self) -> None:
        self._particles.clear()

    # ── Emission helpers ──────────────────────────────────────────────────────
    def _spawn(self, p: Particle) -> None:
        if len(self._particles) < self.MAX_PARTICLES:
            self._particles.append(p)

    def emit_trail(self, x: float, y: float, color: tuple,
                   count: int = 2, speed: float = 40) -> None:
        for _ in range(count):
            vx = random.uniform(-speed * 0.5, speed * 0.1)
            vy = random.uniform(-speed * 0.3, speed * 0.3)
            self._spawn(Particle(x, y, vx, vy,
                                 life=random.uniform(0.2, 0.5),
                                 color=color, radius=random.uniform(2, 5),
                                 gravity=60, alpha_decay=True, shrink=True,
                                 glow=True, trail=True))

    def emit_explosion(self, x: float, y: float, color: tuple,
                       count: int = 30, speed: float = 200) -> None:
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            spd = random.uniform(speed * 0.3, speed)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd
            self._spawn(Particle(x, y, vx, vy,
                                 life=random.uniform(0.4, 0.9),
                                 color=color, radius=random.uniform(3, 7),
                                 gravity=200, glow=True))

    def emit_sparks(self, x: float, y: float, color: tuple,
                    count: int = 6, speed: float = 120) -> None:
        for _ in range(count):
            angle = random.uniform(-math.pi, 0)  # upward arc
            spd = random.uniform(speed * 0.5, speed)
            self._spawn(Particle(x, y,
                                 math.cos(angle) * spd,
                                 math.sin(angle) * spd,
                                 life=random.uniform(0.3, 0.7),
                                 color=color, radius=random.uniform(1.5, 3.5),
                                 gravity=300, glow=True))

    def emit_ambient(self, x: float, y: float, color: tuple,
                     vy: float = -20, spread: float = 80) -> None:
        self._spawn(Particle(
            random.uniform(x - spread, x + spread), y,
            random.uniform(-15, 15), vy,
            life=random.uniform(1.5, 3.0),
            color=color, radius=random.uniform(2, 4),
            gravity=0, alpha_decay=True, shrink=False, glow=False
        ))

    def emit_rain_drop(self, x: float, y: float, color: tuple = (150, 200, 255)) -> None:
        self._spawn(Particle(x, y, random.uniform(-10, -5), random.uniform(400, 600),
                             life=random.uniform(0.5, 1.0),
                             color=color, radius=1.0,
                             gravity=0, alpha_decay=False, shrink=False))

    def emit_snow(self, x: float, y: float, color: tuple = (220, 240, 255)) -> None:
        self._spawn(Particle(x, y,
                             random.uniform(-30, 30),
                             random.uniform(40, 90),
                             life=random.uniform(3.0, 6.0),
                             color=color, radius=random.uniform(2, 4),
                             gravity=5, alpha_decay=False, shrink=False))

    def emit_bubble(self, x: float, y: float, color: tuple = (100, 180, 255)) -> None:
        self._spawn(Particle(x, y,
                             random.uniform(-20, 20),
                             random.uniform(-60, -30),
                             life=random.uniform(2.0, 4.0),
                             color=color, radius=random.uniform(3, 7),
                             gravity=-10, alpha_decay=True, shrink=False, glow=True))

    def emit_star(self, x: float, y: float) -> None:
        col = random.choice([(255, 255, 255), (200, 220, 255), (255, 220, 180)])
        self._spawn(Particle(x, y, random.uniform(-5, 5), random.uniform(-5, 5),
                             life=random.uniform(0.5, 2.0),
                             color=col, radius=random.uniform(0.5, 2.5),
                             gravity=0, alpha_decay=True, shrink=True, glow=False))

    def emit_lava(self, x: float, y: float) -> None:
        colors = [(255, 100, 0), (255, 60, 0), (255, 180, 0)]
        col = random.choice(colors)
        self._spawn(Particle(x, y,
                             random.uniform(-40, 40),
                             random.uniform(-120, -60),
                             life=random.uniform(0.6, 1.2),
                             color=col, radius=random.uniform(3, 6),
                             gravity=200, glow=True))

    def emit_neon(self, x: float, y: float, color: tuple, count: int = 3) -> None:
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            spd = random.uniform(30, 100)
            self._spawn(Particle(x, y,
                                 math.cos(angle) * spd,
                                 math.sin(angle) * spd,
                                 life=random.uniform(0.3, 0.7),
                                 color=color, radius=random.uniform(2, 5),
                                 gravity=0, glow=True))

    def emit_score_pop(self, x: float, y: float) -> None:
        """Confetti burst when scoring."""
        colors = [(255, 215, 0), (0, 255, 128), (0, 200, 255),
                  (255, 100, 200), (255, 255, 100)]
        for _ in range(20):
            col = random.choice(colors)
            angle = random.uniform(0, 2 * math.pi)
            spd = random.uniform(80, 220)
            self._spawn(Particle(x, y, math.cos(angle) * spd, math.sin(angle) * spd,
                                 life=random.uniform(0.5, 1.0),
                                 color=col, radius=random.uniform(3, 6),
                                 gravity=150, glow=True))

    # ── Update & Draw ─────────────────────────────────────────────────────────
    def update(self, dt: float) -> None:
        for p in self._particles:
            p.update(dt)
        self._particles = [p for p in self._particles if p.alive]

    def draw(self, surface: pygame.Surface, offset: tuple = (0, 0)) -> None:
        for p in self._particles:
            p.draw(surface, offset)
