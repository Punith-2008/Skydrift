"""
src/entities/pipe.py
Pipe obstacle system with object pooling and biome-themed rendering.
"""

import pygame
import math
import random
from src.engine.renderer import draw_glow


PIPE_WIDTH = 72
PIPE_CAP_H = 24
PIPE_SPAWN_INTERVAL = 2.0     # seconds between spawns (adjusted by difficulty)


class Pipe:
    """A single pipe obstacle (one top + one bottom)."""

    def __init__(self):
        self.x: float = 0.0
        self.gap_y: float = 0.0     # center of the gap
        self.gap_h: int = 160
        self.speed: float = 200.0
        self.active: bool = False
        self.scored: bool = False
        self.scheme: dict = {}
        self.width: int = PIPE_WIDTH

        # Visual variation
        self.decoration_type: int = 0   # 0-3 biome decoration styles
        self._anim_phase: float = 0.0

    def activate(self, x: float, gap_y: float, gap_h: int,
                 speed: float, scheme: dict, screen_h: int) -> None:
        self.x = x
        self.gap_y = gap_y
        self.gap_h = gap_h
        self.speed = speed
        self.scheme = scheme
        self.active = True
        self.scored = False
        self.screen_h = screen_h
        self.decoration_type = random.randint(0, 3)
        self._anim_phase = random.uniform(0, 6.28)

    def update(self, dt: float, time_scale: float = 1.0) -> None:
        self.x -= self.speed * dt * time_scale
        self._anim_phase += dt * 2.0

    @property
    def off_screen(self) -> bool:
        return self.x + self.width < -10

    @property
    def top_rect(self) -> pygame.Rect:
        top_h = int(self.gap_y - self.gap_h // 2)
        return pygame.Rect(int(self.x), 0, self.width, top_h)

    @property
    def bottom_rect(self) -> pygame.Rect:
        bot_y = int(self.gap_y + self.gap_h // 2)
        return pygame.Rect(int(self.x), bot_y, self.width, self.screen_h - bot_y)

    def collides(self, bird_rect: pygame.Rect) -> bool:
        return self.top_rect.colliderect(bird_rect) or \
               self.bottom_rect.colliderect(bird_rect)

    def draw(self, surface: pygame.Surface, offset: tuple = (0, 0)) -> None:
        ox, oy = offset
        px = int(self.x + ox)
        body   = self.scheme.get("body",   (60, 180, 60))
        accent = self.scheme.get("accent", (80, 220, 80))
        dark   = self.scheme.get("dark",   (20, 80, 20))

        top_h = int(self.gap_y - self.gap_h // 2)
        bot_y = int(self.gap_y + self.gap_h // 2)
        sh = self.screen_h

        # Top pipe body
        self._draw_pipe_body(surface, px, 0, top_h, body, accent, dark, True)
        # Bottom pipe body
        self._draw_pipe_body(surface, px, bot_y, sh - bot_y, body, accent, dark, False)

        # Accent glow line on edges
        edge_alpha = int(80 + 40 * math.sin(self._anim_phase))
        edge_surf = pygame.Surface((2, max(top_h, 1)), pygame.SRCALPHA)
        edge_surf.fill((*accent, edge_alpha))
        surface.blit(edge_surf, (px + self.width - 2, oy), special_flags=pygame.BLEND_RGBA_ADD)

        edge_surf2 = pygame.Surface((2, max(sh - bot_y, 1)), pygame.SRCALPHA)
        edge_surf2.fill((*accent, edge_alpha))
        surface.blit(edge_surf2, (px + self.width - 2, bot_y + oy), special_flags=pygame.BLEND_RGBA_ADD)

    def _draw_pipe_body(self, surface, px, py, height, body, accent, dark,
                         is_top: bool):
        if height <= 0:
            return
        # Main body
        pygame.draw.rect(surface, body, (px, py, self.width, height))

        # Left dark shade
        pygame.draw.rect(surface, dark, (px, py, 8, height))

        # Right highlight
        pygame.draw.rect(surface, accent, (px + self.width - 6, py, 6, height))

        # Cap (rim at the opening)
        cap_y = py + height - PIPE_CAP_H if is_top else py
        cap_w = self.width + 10
        cap_x = px - 5
        pygame.draw.rect(surface, dark, (cap_x, cap_y, cap_w, PIPE_CAP_H), border_radius=4)
        pygame.draw.rect(surface, accent, (cap_x, cap_y, cap_w, PIPE_CAP_H), width=2, border_radius=4)

        # Horizontal stripes (panel lines)
        stripe_step = 30
        for sy in range(py + 10, py + height - PIPE_CAP_H, stripe_step):
            pygame.draw.line(surface, dark, (px + 10, sy), (px + self.width - 10, sy), 1)


class PipeManager:
    """Manages pipe pool, spawning, and collision."""

    POOL_SIZE = 12

    def __init__(self, screen_w: int, screen_h: int):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self._pool: list[Pipe] = [Pipe() for _ in range(self.POOL_SIZE)]
        self._spawn_timer: float = 0.0
        self._spawn_interval: float = PIPE_SPAWN_INTERVAL
        self.pipe_speed: float = 200.0
        self.base_speed: float = 200.0
        self.gap_size: int = 160
        self.base_gap: int = 160
        self.scheme: dict = {}
        self.scroll_x: float = 0.0    # total scroll for background sync
        self.just_spawned: list = []

    def reset(self, speed: float, gap: int, scheme: dict) -> None:
        self.pipe_speed = speed
        self.base_speed = speed
        self.gap_size = gap
        self.base_gap = gap
        self.scheme = scheme
        self._spawn_timer = 0.0
        self.scroll_x = 0.0
        for p in self._pool:
            p.active = False

    def update(self, dt: float, time_scale: float = 1.0) -> int:
        """Returns number of pipes scored this frame."""
        bird_x = self.screen_w * 0.25   # bird's fixed x position
        
        self.just_spawned.clear()

        self._spawn_timer -= dt
        if self._spawn_timer <= 0:
            self._spawn_timer = self._spawn_interval
            self._spawn_pipe()

        scored = 0
        for pipe in self._pool:
            if not pipe.active:
                continue
            pipe.update(dt, time_scale)
            # Check score: pipe just passed the bird
            if not pipe.scored and pipe.x + pipe.width < bird_x:
                pipe.scored = True
                scored += 1
            if pipe.off_screen:
                pipe.active = False

        self.scroll_x += self.pipe_speed * dt * time_scale
        return scored

    def _spawn_pipe(self) -> None:
        pipe = self._get_free_pipe()
        if pipe is None:
            return
        margin = 80
        gap_y = random.randint(margin + self.gap_size // 2,
                               self.screen_h - 70 - self.gap_size // 2)
        pipe.activate(
            x=float(self.screen_w + 20),
            gap_y=float(gap_y),
            gap_h=self.gap_size,
            speed=self.pipe_speed,
            scheme=self.scheme,
            screen_h=self.screen_h - 60,   # above ground
        )
        self.just_spawned.append((pipe.x, pipe.gap_y, pipe.gap_h))

    def _get_free_pipe(self):
        for p in self._pool:
            if not p.active:
                return p
        return None

    def check_collision(self, bird_rect: pygame.Rect) -> bool:
        for pipe in self._pool:
            if pipe.active and pipe.collides(bird_rect):
                return True
        return False

    def draw(self, surface: pygame.Surface, offset: tuple = (0, 0)) -> None:
        for pipe in self._pool:
            if pipe.active:
                pipe.draw(surface, offset)

    def increase_difficulty(self, score: int) -> None:
        """Scale speed and shrink gap based on score."""
        speed_bonus = min(score * 1.5, 150)
        self.pipe_speed = min(self.base_speed + speed_bonus, 380)

        # Progressively challenging pipe gap (shrinks as score increases)
        gap_shrink = min(score * 0.8, 50)  # Shrink by up to 50 pixels
        self.gap_size = max(self.base_gap - int(gap_shrink), 110)

        for p in self._pool:
            if p.active:
                p.speed = self.pipe_speed

    def set_scheme(self, scheme: dict) -> None:
        self.scheme = scheme
