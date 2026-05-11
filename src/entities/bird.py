"""
src/entities/bird.py
Player entity — physics, flap animation, skins, trail, death animation.
"""

import pygame
import math
import random
from src.engine.renderer import draw_glow


# Bird skin definitions (all drawn procedurally)
SKINS = {
    "classic":   {"body": (255, 220, 50),  "wing": (255, 180, 0),  "eye": (30,30,30),   "beak": (255,120,0),  "trail": (255,255,150)},
    "cyber":     {"body": (0, 220, 255),   "wing": (0, 140, 255),  "eye": (255,0,200),  "beak": (0,255,200),  "trail": (0,200,255)},
    "lava":      {"body": (255, 80, 0),    "wing": (200, 40, 0),   "eye": (255,220,0),  "beak": (255,180,0),  "trail": (255,120,0)},
    "ghost":     {"body": (200, 220, 255), "wing": (160, 180, 220),"eye": (80,100,200), "beak": (180,200,255),"trail": (180,200,255)},
    "neon":      {"body": (0, 255, 120),   "wing": (0, 200, 80),   "eye": (255,0,255),  "beak": (0,255,200),  "trail": (0,255,100)},
    "cosmic":    {"body": (180, 60, 255),  "wing": (120, 0, 200),  "eye": (255,255,0),  "beak": (200,100,255),"trail": (200,100,255)},
}

SKIN_ORDER = list(SKINS.keys())


class Bird:
    """Player-controlled bird with delta-time physics and wing animation."""

    RADIUS = 18
    GRAVITY_SCALE = 1.0

    def __init__(self, x: float, y: float, skin: str = "classic"):
        self.x = x
        self.y = y
        self.vy = 0.0
        self.angle = 0.0          # visual tilt (degrees)
        self.alive = True
        self.skin = SKINS.get(skin, SKINS["classic"])

        # Wing animation
        self._wing_angle = 0.0
        self._wing_dir = 1
        self._flap_anim = 0.0    # 0–1, plays on each flap

        # Hover (menu only)
        self._hover_phase = random.uniform(0, 6.28)

        # Death animation
        self._death_vy = 0.0
        self._death_spin = 0.0
        self._death_timer = 0.0
        self.death_done = False

        # Shield / slow-mo flags
        self.shielded = False
        self.shield_timer = 0.0
        self._shield_pulse = 0.0

        # Squash/stretch on flap
        self._squash = 1.0
        self._stretch = 1.0

    # ── Flap ────────────────────────────────────────────────────────────────
    def flap(self, jump_vel: float) -> None:
        if not self.alive:
            return
        self.vy = jump_vel
        self._flap_anim = 1.0
        self._squash = 0.7
        self._stretch = 1.4

    # ── Update ───────────────────────────────────────────────────────────────
    def update(self, dt: float, gravity: float, terminal_vel: float,
               floor_y: float, time_scale: float = 1.0) -> None:
        if not self.alive:
            self._update_death(dt, floor_y)
            return

        eff_dt = dt * time_scale

        # Physics
        self.vy += gravity * eff_dt
        self.vy = min(self.vy, terminal_vel)
        self.y += self.vy * eff_dt

        # Visual tilt: nose down when falling, level/up when rising
        target_angle = max(-30.0, min(90.0, self.vy * 0.06))
        self.angle += (target_angle - self.angle) * min(8.0 * eff_dt, 1.0)

        # Wing flap animation
        if self._flap_anim > 0:
            self._wing_angle = -40.0 * self._flap_anim
            self._flap_anim -= dt * 5.0
        else:
            # Idle gentle flap
            self._wing_angle = 15.0 * math.sin(pygame.time.get_ticks() * 0.005)
            self._flap_anim = 0

        # Squash/stretch recovery
        self._squash += (1.0 - self._squash) * min(dt * 8, 1.0)
        self._stretch += (1.0 - self._stretch) * min(dt * 8, 1.0)

        # Shield
        if self.shielded:
            self.shield_timer -= dt
            self._shield_pulse = (self._shield_pulse + dt * 4) % (2 * math.pi)
            if self.shield_timer <= 0:
                self.shielded = False

    def update_hover(self, dt: float) -> None:
        """Gentle up/down hover for menu screen."""
        self._hover_phase += dt * 2.0
        self.y += math.sin(self._hover_phase) * 0.8
        self._wing_angle = 20.0 * math.sin(self._hover_phase * 2)

    def _update_death(self, dt: float, floor_y: float) -> None:
        self._death_timer += dt
        self._death_vy += 1200 * dt  # heavier gravity for fast fall
        self.y += self._death_vy * dt
        self._death_spin += 500 * dt
        self.angle = self._death_spin % 360
        
        # Stop at ground
        if self.y + self.RADIUS >= floor_y:
            self.y = floor_y - self.RADIUS
            self.death_done = True

    def kill(self) -> None:
        if self.alive:
            self.alive = False
            self._death_vy = -200.0

    def activate_shield(self, duration: float = 5.0) -> None:
        self.shielded = True
        self.shield_timer = duration

    # ── Collision rect ────────────────────────────────────────────────────────
    @property
    def rect(self) -> pygame.Rect:
        r = self.RADIUS - 4   # slightly smaller for fairness
        return pygame.Rect(int(self.x) - r, int(self.y) - r, r*2, r*2)

    # ── Draw ──────────────────────────────────────────────────────────────────
    def draw(self, surface: pygame.Surface, offset: tuple = (0, 0)) -> None:
        ox, oy = offset
        cx = int(self.x + ox)
        cy = int(self.y + oy)
        r = self.RADIUS
        skin = self.skin

        # Build a temporary surface to apply rotation
        size = r * 4
        bird_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        bc = (size // 2, size // 2)

        # Squash/stretch scale
        rx = int(r * self._stretch)
        ry = int(r * self._squash)

        # Body
        pygame.draw.ellipse(bird_surf, skin["body"],
                            (bc[0]-rx, bc[1]-ry, rx*2, ry*2))
        # Belly highlight
        hl_col = tuple(min(255, c+60) for c in skin["body"])
        pygame.draw.ellipse(bird_surf, hl_col,
                            (bc[0]-rx//2, bc[1]-ry//2, rx, ry))

        # Wing
        wing_r = int(r * 0.7)
        wing_cx = bc[0] - rx // 3
        wing_cy = int(bc[1] + self._wing_angle * 0.3)
        pygame.draw.ellipse(bird_surf, skin["wing"],
                            (wing_cx - wing_r, wing_cy - wing_r//2, wing_r*2, wing_r))

        # Eye
        eye_x = bc[0] + rx // 2
        eye_y = bc[1] - ry // 4
        pygame.draw.circle(bird_surf, (255, 255, 255), (eye_x, eye_y), 5)
        pygame.draw.circle(bird_surf, skin["eye"], (eye_x + 1, eye_y), 3)

        # Beak
        beak_x = bc[0] + rx
        beak_y = bc[1]
        pygame.draw.polygon(bird_surf, skin["beak"], [
            (beak_x, beak_y - 3),
            (beak_x + 10, beak_y),
            (beak_x, beak_y + 3),
        ])

        # Rotate
        rotated = pygame.transform.rotate(bird_surf, -self.angle)
        rr = rotated.get_rect(center=(cx, cy))
        surface.blit(rotated, rr)

        # Shield aura
        if self.shielded:
            pulse = 0.7 + 0.3 * math.sin(self._shield_pulse)
            shield_r = int(r * 1.6 * pulse)
            ss = pygame.Surface((shield_r*2, shield_r*2), pygame.SRCALPHA)
            pygame.draw.circle(ss, (0, 200, 255, 60), (shield_r, shield_r), shield_r)
            pygame.draw.circle(ss, (0, 200, 255, 120), (shield_r, shield_r), shield_r, 2)
            surface.blit(ss, (cx - shield_r, cy - shield_r), special_flags=pygame.BLEND_RGBA_ADD)
