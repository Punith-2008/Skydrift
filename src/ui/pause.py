"""
src/ui/pause.py
Pause menu overlay.

Keyboard navigation: Tab / Down / Up arrows cycle focus; Enter / Space activates.
ESC or P resumes (existing behaviour preserved).
"""

import pygame
from src.engine.renderer import FontManager, draw_glass_panel
from src.ui.widgets import GlassButton


class PauseMenu:
    def __init__(self, screen_w: int, screen_h: int):
        self.w = screen_w
        self.h = screen_h
        self._font = FontManager.get(48, bold=True)
        self._hint = FontManager.get(20)
        cx, cy = screen_w // 2, screen_h // 2
        bw, bh = 200, 50

        self.btn_resume   = GlassButton(pygame.Rect(cx-bw//2, cy-10,  bw, bh), "RESUME",    accent=(0,220,120),   icon="▶")
        self.btn_settings = GlassButton(pygame.Rect(cx-bw//2, cy+70,  bw, bh), "SETTINGS",  accent=(200,100,255), icon="⚙")
        self.btn_menu     = GlassButton(pygame.Rect(cx-bw//2, cy+150, bw, bh), "MAIN MENU", accent=(255,100,100), icon="←")
        self._buttons     = [self.btn_resume, self.btn_settings, self.btn_menu]

        # Keyboard focus — default to Resume
        self._focus_idx = 0
        self._buttons[self._focus_idx].focused = True

    # ── Focus helpers ─────────────────────────────────────────────────────────
    def _reset_focus(self) -> None:
        """Called each time the pause menu becomes active."""
        for b in self._buttons:
            b.focused = False
        self._focus_idx = 0
        self._buttons[0].focused = True

    def _shift_focus(self, delta: int) -> None:
        self._buttons[self._focus_idx].focused = False
        self._focus_idx = (self._focus_idx + delta) % len(self._buttons)
        self._buttons[self._focus_idx].focused = True

    # ── Event handling ────────────────────────────────────────────────────────
    def handle_event(self, event) -> str:
        # Quick resume via ESC / P
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "resume"

        # Keyboard navigation
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_TAB, pygame.K_DOWN):
                shift = -1 if (event.key == pygame.K_TAB and
                               pygame.key.get_mods() & pygame.KMOD_SHIFT) else 1
                self._shift_focus(shift)
            elif event.key == pygame.K_UP:
                self._shift_focus(-1)

        if self.btn_resume.handle_event(event):   return "resume"
        if self.btn_settings.handle_event(event): return "settings"
        if self.btn_menu.handle_event(event):     return "menu"
        return ""

    # ── Update ────────────────────────────────────────────────────────────────
    def update(self, dt: float) -> None:
        for b in self._buttons:
            b.update(dt)

    # ── Draw ──────────────────────────────────────────────────────────────────
    def draw(self, surface: pygame.Surface) -> None:
        # Dim overlay
        ov = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        ov.fill((0, 0, 20, 160))
        surface.blit(ov, (0, 0))

        # Panel
        pw, ph = 280, 290
        px = (self.w - pw) // 2
        py = (self.h - ph) // 2 - 30
        draw_glass_panel(surface, pygame.Rect(px, py, pw, ph),
                         (100, 120, 200), 50, 100, 20)

        # Title
        ti = self._font.render("PAUSED", True, (255, 255, 255))
        icon_size = 36
        spacing = 15
        total_w = icon_size + spacing + ti.get_width()
        start_x = self.w // 2 - total_w // 2

        from src.engine.renderer import draw_icon
        draw_icon(surface, "pause", (start_x + icon_size // 2, py + 50), icon_size, (255, 255, 255))
        surface.blit(ti, (start_x + icon_size + spacing, py + 50 - ti.get_height() // 2))

        for b in self._buttons:
            b.draw(surface)

        hint = self._hint.render("ESC to resume  •  TAB / ↑↓ to navigate",
                                 True, (120, 140, 180))
        surface.blit(hint, hint.get_rect(center=(self.w//2, self.h - 20)))
