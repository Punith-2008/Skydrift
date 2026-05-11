"""
src/ui/settings_ui.py
Settings menu — volume, resolution, difficulty, FPS, fullscreen.

Keyboard navigation: Tab / Down / Up cycles button focus; Enter / Space activates.
Sliders are not in the keyboard cycle (mouse-only by design).
"""

import pygame
from src.engine.renderer import FontManager, draw_glass_panel
from src.ui.widgets import GlassButton, SliderWidget


class SettingsUI:
    def __init__(self, screen_w: int, screen_h: int):
        self.w = screen_w
        self.h = screen_h
        self._title_font = FontManager.get(42, bold=True)
        self._label_font = FontManager.get(22)

        cx = screen_w // 2
        sw = 260   # slider width

        # Sliders (mouse-only)
        self.sl_master = SliderWidget(pygame.Rect(cx-sw//2, 180, sw, 20),
                                      "Master Volume", 1.0, accent=(255, 255, 255))
        self.sl_music  = SliderWidget(pygame.Rect(cx-sw//2, 250, sw, 20),
                                      "Music Volume",  0.6, accent=(0, 200, 255))
        self.sl_sfx    = SliderWidget(pygame.Rect(cx-sw//2, 320, sw, 20),
                                      "SFX Volume",    0.8, accent=(0, 255, 150))
        self._sliders  = [self.sl_master, self.sl_music, self.sl_sfx]

        bw, bh = 180, 44
        # Toggle buttons (keyboard-navigable)
        self.btn_sound= GlassButton(pygame.Rect(cx-bw//2, 390, bw, bh), "SOUND: ON",
                                    accent=(0, 255, 200))
        self.btn_diff = GlassButton(pygame.Rect(cx-bw//2, 450, bw, bh), "NORMAL",
                                    accent=(255, 180, 0))
        self.btn_fs   = GlassButton(pygame.Rect(cx-bw//2, 510, bw, bh), "FULLSCREEN: OFF",
                                    accent=(200, 100, 255))
        self.btn_fps  = GlassButton(pygame.Rect(cx-bw//2, 570, bw, bh), "SHOW FPS: OFF",
                                    accent=(100, 200, 100))
        self.btn_par  = GlassButton(pygame.Rect(cx-bw//2, 630, bw, bh), "PARTICLES: ON",
                                    accent=(255, 100, 200))
        self.btn_back = GlassButton(pygame.Rect(cx-bw//2, 690, bw, bh), "BACK",
                                    accent=(255, 100, 100), icon="←")
        self._buttons = [self.btn_sound, self.btn_diff, self.btn_fs, self.btn_fps,
                         self.btn_par, self.btn_back]

        self._difficulty_cycle = ["easy", "normal", "hard"]

        # Keyboard focus — default to BACK so it's immediately reachable
        self._focus_idx = len(self._buttons) - 1
        self._buttons[self._focus_idx].focused = True

    # ── Focus helpers ─────────────────────────────────────────────────────────
    def _shift_focus(self, delta: int) -> None:
        self._buttons[self._focus_idx].focused = False
        self._focus_idx = (self._focus_idx + delta) % len(self._buttons)
        self._buttons[self._focus_idx].focused = True

    # ── Sync ─────────────────────────────────────────────────────────────────
    def sync_from(self, settings) -> None:
        self.sl_master.value = settings.volume_master
        self.sl_music.value  = settings.volume_music
        self.sl_sfx.value    = settings.volume_sfx
        self.btn_sound.text  = f"SOUND: {'ON' if settings.sound_enabled else 'OFF'}"
        self.btn_diff.text   = settings.difficulty.upper()
        self.btn_fs.text     = f"FULLSCREEN: {'ON' if settings.fullscreen else 'OFF'}"
        self.btn_fps.text    = f"SHOW FPS: {'ON' if settings.show_fps else 'OFF'}"
        self.btn_par.text    = f"PARTICLES: {'ON' if settings.particles_enabled else 'OFF'}"

    # ── Event handling ────────────────────────────────────────────────────────
    def handle_event(self, event, settings) -> str:
        for sl in self._sliders:
            sl.handle_event(event)

        # Apply sliders live
        settings.volume_master = self.sl_master.value
        settings.volume_music  = self.sl_music.value
        settings.volume_sfx    = self.sl_sfx.value

        # Keyboard navigation
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_TAB, pygame.K_DOWN):
                shift = -1 if (event.key == pygame.K_TAB and
                               pygame.key.get_mods() & pygame.KMOD_SHIFT) else 1
                self._shift_focus(shift)
            elif event.key == pygame.K_UP:
                self._shift_focus(-1)
            elif event.key == pygame.K_ESCAPE:
                settings.save()
                return "back"

        if self.btn_sound.handle_event(event):
            settings.sound_enabled = not settings.sound_enabled
            self.btn_sound.text    = f"SOUND: {'ON' if settings.sound_enabled else 'OFF'}"

        if self.btn_diff.handle_event(event):
            idx = self._difficulty_cycle.index(settings.difficulty)
            settings.difficulty = self._difficulty_cycle[(idx + 1) % 3]
            self.btn_diff.text  = settings.difficulty.upper()

        if self.btn_fs.handle_event(event):
            settings.fullscreen = not settings.fullscreen
            self.btn_fs.text    = f"FULLSCREEN: {'ON' if settings.fullscreen else 'OFF'}"
            return "toggle_fullscreen"

        if self.btn_fps.handle_event(event):
            settings.show_fps  = not settings.show_fps
            self.btn_fps.text  = f"SHOW FPS: {'ON' if settings.show_fps else 'OFF'}"

        if self.btn_par.handle_event(event):
            settings.particles_enabled = not settings.particles_enabled
            self.btn_par.text  = f"PARTICLES: {'ON' if settings.particles_enabled else 'OFF'}"

        if self.btn_back.handle_event(event):
            settings.save()
            return "back"

        return ""

    # ── Update ────────────────────────────────────────────────────────────────
    def update(self, dt: float) -> None:
        for b in self._buttons:
            b.update(dt)

    # ── Draw ──────────────────────────────────────────────────────────────────
    def draw(self, surface: pygame.Surface) -> None:
        # Dark overlay
        ov = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        ov.fill((5, 5, 20, 230))
        surface.blit(ov, (0, 0))

        # Panel
        pw, ph = 420, 600
        px = (self.w - pw) // 2
        py = 80
        draw_glass_panel(surface, pygame.Rect(px, py, pw, ph),
                         (100, 120, 200), 45, 100, 20)

        # Title
        ti = self._title_font.render("SETTINGS", True, (255, 255, 255))
        icon_size = 32
        spacing = 15
        total_w = icon_size + spacing + ti.get_width()
        start_x = self.w // 2 - total_w // 2

        from src.engine.renderer import draw_icon
        draw_icon(surface, "settings", (start_x + icon_size // 2, 120), icon_size, (255, 255, 255))
        surface.blit(ti, (start_x + icon_size + spacing, 120 - ti.get_height() // 2))

        for sl in self._sliders:
            sl.draw(surface)
        for b in self._buttons:
            b.draw(surface)

        # Navigation hint
        hint_font = FontManager.get(16)
        hint = hint_font.render("TAB / ↑↓ navigate  •  ENTER toggle  •  ESC back",
                                True, (100, 120, 160))
        surface.blit(hint, hint.get_rect(center=(self.w//2, self.h - 20)))
