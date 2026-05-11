"""
src/ui/menu.py
Animated main menu with bird hover animation, skin selector preview.

Keyboard navigation: Tab / Down / Up arrows cycle focus; Enter / Space activates.
"""

import pygame
import math
import random
from src.engine.renderer import FontManager, draw_glass_panel, draw_glow, draw_text
from src.ui.widgets import GlassButton
from src.entities.bird import SKINS, SKIN_ORDER


class MainMenu:
    def __init__(self, screen_w: int, screen_h: int):
        self.w = screen_w
        self.h = screen_h

        # Fonts
        self._title_font = FontManager.get(72, bold=True)
        self._sub_font   = FontManager.get(24)
        self._hint_font  = FontManager.get(18)

        # Buttons
        bw, bh = 260, 56
        cx = screen_w // 2
        start_y = screen_h // 2 - 40
        spacing = 75
        self.btn_play       = GlassButton(pygame.Rect(cx-bw//2, start_y,          bw, bh), "PLAY",            accent=(0,220,120),   icon="▶")
        self.btn_biome_prev = GlassButton(pygame.Rect(cx-bw//2 - 50, start_y+spacing, 40, bh), "<",             accent=(0,200,255))
        self.btn_biome      = GlassButton(pygame.Rect(cx-bw//2, start_y+spacing,  bw, bh), "BIOME: OCEAN",    accent=(0,200,255),   icon="🌍")
        self.btn_biome_next = GlassButton(pygame.Rect(cx+bw//2 + 10, start_y+spacing, 40, bh), ">",             accent=(0,200,255))
        self.btn_quit     = GlassButton(pygame.Rect(cx-bw//2, start_y+spacing*2,bw, bh), "QUIT",            accent=(255,100,100), icon="✕")

        # Corner secondary buttons
        self.btn_skins    = GlassButton(pygame.Rect(20,              screen_h-65, 120, 45), "SKINS",    accent=(255,180,0),   icon="🎨")
        self.btn_settings = GlassButton(pygame.Rect(screen_w-140,   screen_h-65, 120, 45), "SETTINGS", accent=(200,100,255), icon="⚙")

        # Ordered list used for focus cycling (Tab / arrow keys)
        self._buttons     = [self.btn_play, self.btn_biome_prev, self.btn_biome, self.btn_biome_next,
                             self.btn_quit, self.btn_skins, self.btn_settings]
        self._focus_idx   = 0
        self._buttons[self._focus_idx].focused = True

        # Stars background
        self._stars = [(random.randint(0, screen_w), random.randint(0, screen_h),
                        random.randint(0, 2), random.randint(120, 255)) for _ in range(120)]

        # Skin selector state
        self._skin_idx  = 0
        self._skin_anim = 0.0

        # Animation
        self._t       = 0.0
        self._title_y = 0.0

    # ── Focus helpers ─────────────────────────────────────────────────────────
    def _shift_focus(self, delta: int) -> None:
        self._buttons[self._focus_idx].focused = False
        self._focus_idx = (self._focus_idx + delta) % len(self._buttons)
        self._buttons[self._focus_idx].focused = True

    # ── Event handling ────────────────────────────────────────────────────────
    def handle_event(self, event, settings) -> str:
        """Returns action string: play | skins | leaderboard | settings | quit | ''"""
        # Keyboard navigation
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_TAB, pygame.K_DOWN):
                shift = -1 if (event.key == pygame.K_TAB and
                               pygame.key.get_mods() & pygame.KMOD_SHIFT) else 1
                self._shift_focus(shift)
            elif event.key == pygame.K_UP:
                self._shift_focus(-1)

        # Let each button handle the event (mouse + Enter/Space via focused flag)
        if self.btn_play.handle_event(event):       return "play"
        if self.btn_biome_prev.handle_event(event): return "cycle_biome_prev"
        if self.btn_biome_next.handle_event(event): return "cycle_biome_next"
        if self.btn_biome.handle_event(event):      return "cycle_biome_next"
        if self.btn_quit.handle_event(event):       return "quit"
        if self.btn_skins.handle_event(event):    return "skins"
        if self.btn_settings.handle_event(event): return "settings"
        return ""

    # ── Update ────────────────────────────────────────────────────────────────
    def update(self, dt: float) -> None:
        self._t += dt
        self._title_y   = math.sin(self._t * 1.2) * 5
        self._skin_anim += dt * 3.0
        for btn in self._buttons:
            btn.update(dt)

    # ── Draw ──────────────────────────────────────────────────────────────────
    def draw(self, surface: pygame.Surface, settings) -> None:
        # Sky gradient
        for y in range(self.h):
            t = y / max(self.h-1, 1)
            r = int(5 + 15*t); g = int(5 + 10*t); b = int(20 + 30*t)
            pygame.draw.line(surface, (r, g, b), (0, y), (self.w-1, y))

        # Stars
        for sx, sy, sr, sb in self._stars:
            twinkle = 0.6 + 0.4 * math.sin(self._t * 2 + sx * 0.1)
            a = int(sb * twinkle)
            pygame.draw.circle(surface, (a, a, a), (sx, sy), sr)

        # Floating particles
        for i in range(8):
            px = int((self.w * 0.1 + i * self.w * 0.12 + math.sin(self._t + i) * 30))
            py = int(self.h * 0.8 + math.cos(self._t * 0.7 + i) * 50 - i * 10)
            col = [(0,200,255),(255,0,200),(255,180,0),(0,255,120)][i % 4]
            a   = int(60 + 40 * math.sin(self._t + i))
            ps  = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.circle(ps, (*col, a), (10, 10), 10)
            surface.blit(ps, (px-10, py-10), special_flags=pygame.BLEND_RGBA_ADD)

        # Title
        ty = int(self.h * 0.18 + self._title_y)
        draw_text(surface, "SKYDRIFT", self._title_font,
                  (255, 255, 255), (self.w//2, ty), shadow=True, shadow_color=(0,100,200))
        # Subtitle shimmer
        t_col = (int(150 + 105*math.sin(self._t*2)),
                 int(200 + 55*math.sin(self._t*2+1)),
                 255)
        draw_text(surface, "A Flappy Bird Experience", self._sub_font,
                  t_col, (self.w//2, ty+65), shadow=False)

        # Glow behind title
        draw_glow(surface, (0,100,255), (self.w//2, ty), 120, 0.3)

        # Skin preview bird
        self._draw_skin_preview(surface, settings)

        # Buttons
        for btn in self._buttons:
            btn.draw(surface)

        # Navigation hint
        hint = self._hint_font.render("SPACE / CLICK to flap  •  TAB / ↑↓ to navigate",
                                      True, (100, 120, 160))
        surface.blit(hint, hint.get_rect(center=(self.w//2, self.h-20)))

    def _draw_skin_preview(self, surface, settings):
        """Small bird preview near title."""
        bx = int(self.w * 0.5 - 80)
        by = int(self.h * 0.18 + self._title_y + 15)
        skin    = SKINS.get(settings.active_skin, SKINS["classic"])
        hover_y = by + int(math.sin(self._t * 2) * 6)
        r = 14
        pygame.draw.circle(surface, skin["body"],  (bx, hover_y), r)
        pygame.draw.circle(surface, skin["wing"],  (bx-4, hover_y+3), r-5)
        pygame.draw.circle(surface, (255,255,255), (bx+5, hover_y-3), 5)
        pygame.draw.circle(surface, skin["eye"],   (bx+6, hover_y-3), 3)
        pygame.draw.polygon(surface, skin["beak"], [
            (bx+r, hover_y-2), (bx+r+7, hover_y), (bx+r, hover_y+2)
        ])
