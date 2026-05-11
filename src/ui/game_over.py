"""
src/ui/game_over.py
Game over screen — stats display, name input on new high score, retry/menu.

Keyboard navigation: Tab / Down / Up cycles focus between Retry and Menu;
Enter / Space activates focused button.
"""

import pygame
import math
from src.engine.renderer import FontManager, draw_glass_panel, draw_glow
from src.ui.widgets import GlassButton


class GameOverScreen:
    def __init__(self, screen_w: int, screen_h: int):
        self.w = screen_w
        self.h = screen_h
        self._title_font = FontManager.get(56, bold=True)
        self._stat_font  = FontManager.get(26)
        self._name_font  = FontManager.get(30, bold=True)
        self._hint_font  = FontManager.get(18)
        self._small_font = FontManager.get(20)

        cx = screen_w // 2
        bw, bh = 200, 52
        self.btn_retry = GlassButton(pygame.Rect(cx-bw-10, screen_h//2+190, bw, bh),
                                     "RETRY",     accent=(0,220,120),   icon="▶")
        self.btn_menu  = GlassButton(pygame.Rect(cx+10,    screen_h//2+190, bw, bh),
                                     "MAIN MENU", accent=(255,100,100), icon="←")
        self._buttons  = [self.btn_retry, self.btn_menu]

        # Keyboard focus — default to Retry
        self._focus_idx = 0
        self._buttons[0].focused = True

        # State
        self._score = 0
        self._best  = 0
        self._coins = 0
        self._combo = 0
        self._is_hs = False
        self._name  = ""
        self._cursor_blink = 0.0
        self._anim_t   = 0.0
        self._new_rank = 0

    # ── Focus helpers ─────────────────────────────────────────────────────────
    def _shift_focus(self, delta: int) -> None:
        self._buttons[self._focus_idx].focused = False
        self._focus_idx = (self._focus_idx + delta) % len(self._buttons)
        self._buttons[self._focus_idx].focused = True

    # ── Setup ────────────────────────────────────────────────────────────────
    def setup(self, score: int, best: int, coins: int, combo: int,
              is_high_score: bool) -> None:
        self._score    = score
        self._best     = best
        self._coins    = coins
        self._combo    = combo
        self._is_hs    = is_high_score
        self._anim_t   = 0.0
        # Reset focus to Retry when screen is shown
        for b in self._buttons:
            b.focused = False
        self._focus_idx = 0
        self._buttons[0].focused = True

    # ── Event handling ────────────────────────────────────────────────────────
    def handle_event(self, event) -> str:
        """Returns action string: retry | menu | ''"""
        # Keyboard navigation
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_TAB, pygame.K_RIGHT):
                shift = -1 if (event.key == pygame.K_TAB and
                               pygame.key.get_mods() & pygame.KMOD_SHIFT) else 1
                self._shift_focus(shift)
            elif event.key in (pygame.K_UP, pygame.K_LEFT):
                self._shift_focus(-1)
            elif event.key in (pygame.K_DOWN,):
                self._shift_focus(1)

        if self.btn_retry.handle_event(event): return "retry"
        if self.btn_menu.handle_event(event):  return "menu"
        return ""

    # ── Update ────────────────────────────────────────────────────────────────
    def update(self, dt: float) -> None:
        self._anim_t += dt
        for b in self._buttons:
            b.update(dt)

    # ── Draw ─────────────────────────────────────────────────────────────────
    def draw(self, surface: pygame.Surface) -> None:
        # Dark overlay
        ov = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        ov.fill((5, 0, 15, 200))
        surface.blit(ov, (0, 0))

        cx = self.w // 2
        cy = self.h // 2

        # Animated red glow
        glow_pulse = 0.6 + 0.4 * math.sin(self._anim_t * 2)
        draw_glow(surface, (200, 20, 20), (cx, cy-60), int(200*glow_pulse), 0.25)

        # Main panel
        pw, ph = 440, 400
        px = cx - pw // 2
        py = cy - ph // 2 - 20
        draw_glass_panel(surface, pygame.Rect(px, py, pw, ph),
                         (180, 80, 80), 40, 100, 24)

        # Game Over title (slide in)
        slide_in = min(1.0, self._anim_t * 3)
        title_y  = py + 45 - int((1 - slide_in) * 40)
        ti = self._title_font.render("GAME OVER", True, (255, 80, 80))
        surface.blit(ti, ti.get_rect(center=(cx, title_y)))

        # Stats
        stats_y = py + 110
        stats = [
            ("SCORE",     str(self._score), (255, 255, 100)),
            ("BEST",      str(self._best),  (255, 180,   0)),
            ("COINS",     str(self._coins), (255, 215,   0)),
            ("MAX COMBO", f"x{self._combo}", (0,  200, 255)),
        ]
        for i, (label, value, col) in enumerate(stats):
            row_y = stats_y + i * 46
            ls = self._stat_font.render(label, True, (160, 160, 180))
            vs = self._stat_font.render(value, True, col)
            surface.blit(ls, (px + 30, row_y))
            surface.blit(vs, (px + pw - vs.get_width() - 30, row_y))

        # High score message
        hs_y = py + 115 + len(stats) * 46
        if self._is_hs:
            hs_surf = self._small_font.render("🎉 NEW HIGH SCORE!", True, (255, 220, 0))
            surface.blit(hs_surf, hs_surf.get_rect(center=(cx, hs_y)))

        # Buttons
        for b in self._buttons:
            b.draw(surface)

        # Navigation hint
        nav = self._hint_font.render("TAB / ←→ navigate  •  ENTER activate", True, (100, 120, 160))
        surface.blit(nav, nav.get_rect(center=(cx, self.h - 20)))
