"""
src/ui/hud.py
In-game HUD — score, combo indicator, coin count, power-up icons.
"""

import pygame
import math
from src.engine.renderer import FontManager, draw_glass_panel


class HUD:
    def __init__(self, screen_w: int, screen_h: int):
        self.w = screen_w
        self.h = screen_h
        self._score_font  = FontManager.get(52, bold=True)
        self._combo_font  = FontManager.get(32, bold=True)
        self._small_font  = FontManager.get(20)
        self._tiny_font   = FontManager.get(16)
        self._score_anims: list = []   # [(value, x, y, timer)]

    def push_score_anim(self, value: int, x: float, y: float) -> None:
        self._score_anims.append([value, x, y, 1.0])

    def update(self, dt: float) -> None:
        alive = []
        for anim in self._score_anims:
            anim[3] -= dt * 1.5
            anim[2] -= dt * 40   # float upward
            if anim[3] > 0:
                alive.append(anim)
        self._score_anims = alive

    def draw(self, surface: pygame.Surface, score: int, coins: int,
             combo: int, multiplier: int, active_powerup: str = "",
             powerup_timer: float = 0.0, fps: int = 0,
             show_fps: bool = False, biome_name: str = "") -> None:

        # Score (centered top)
        score_str = str(score)
        si = self._score_font.render(score_str, True, (255, 255, 255))
        shadow_i = self._score_font.render(score_str, True, (0, 0, 0))
        cx = self.w // 2
        surface.blit(shadow_i, shadow_i.get_rect(center=(cx+2, 52)))
        surface.blit(si, si.get_rect(center=(cx, 50)))

        # Coin counter (top left)
        coin_panel = pygame.Rect(10, 10, 110, 36)
        draw_glass_panel(surface, coin_panel, (255, 200, 0), 40, 80, 10)
        coin_surf = self._small_font.render(f"💰 {coins}", True, (255, 220, 80))
        surface.blit(coin_surf, (18, 18))

        # Combo (top right when active)
        if multiplier > 1:
            combo_str = f"x{multiplier} COMBO!"
            pulse = 0.9 + 0.1 * math.sin(pygame.time.get_ticks() * 0.008)
            combo_img = self._combo_font.render(combo_str, True, (255, 220, 0))
            combo_img = pygame.transform.scale(combo_img,
                (int(combo_img.get_width()*pulse), int(combo_img.get_height()*pulse)))
            rr = combo_img.get_rect(topright=(self.w - 10, 10))
            surface.blit(combo_img, rr)

        # Active power-up bar
        if active_powerup and powerup_timer > 0:
            self._draw_powerup_bar(surface, active_powerup, powerup_timer)

        # Biome name (briefly shown)
        if biome_name:
            bn_surf = self._tiny_font.render(biome_name.upper().replace("_", " "),
                                              True, (200, 200, 255))
            surface.blit(bn_surf, (self.w//2 - bn_surf.get_width()//2, 80))

        # Floating score pop-ups
        for anim in self._score_anims:
            val, x, y, t = anim
            alpha = int(255 * t)
            col = (255, 255, 100) if val == 1 else (0, 255, 150)
            ps = self._small_font.render(f"+{val}", True, col)
            ps.set_alpha(alpha)
            surface.blit(ps, (int(x), int(y)))

        # FPS
        if show_fps:
            fps_surf = self._tiny_font.render(f"FPS: {fps}", True, (150, 150, 150))
            surface.blit(fps_surf, (self.w - 80, self.h - 25))

    def _draw_powerup_bar(self, surface, kind, timer):
        max_time = 6.0
        t = timer / max_time
        bar_w = 150
        bar_h = 16
        bx = (self.w - bar_w) // 2
        by = self.h - 50

        # Background
        pygame.draw.rect(surface, (40, 40, 60), (bx, by, bar_w, bar_h), border_radius=8)
        # Fill
        colors = {"shield": (0,200,255), "slowmo": (200,100,255), "magnet": (255,180,0)}
        col = colors.get(kind, (255, 255, 255))
        fill_w = int(bar_w * t)
        if fill_w > 0:
            pygame.draw.rect(surface, col, (bx, by, fill_w, bar_h), border_radius=8)
        pygame.draw.rect(surface, col, (bx, by, bar_w, bar_h), 1, border_radius=8)

        label = self._tiny_font.render(kind.upper(), True, col)
        surface.blit(label, (bx + bar_w + 8, by))
