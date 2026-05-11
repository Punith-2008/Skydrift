"""
src/ui/widgets.py
Glassmorphism UI widgets: GlassButton, SliderWidget, AnimatedCounter, NotificationBanner.

GlassButton icon rendering
---------------------------
Icons are drawn with pygame primitives via renderer.draw_icon() so they are
always crisp and readable regardless of font support.

Supported icon keyword strings (passed as `icon=` argument):
    "play"      ▶  solid triangle
    "pause"     ⏸  two bars
    "settings"  ⚙  gear
    "back"      ←  left arrow
    "close"     ✕  × cross
    "trophy"    🏆  trophy cup
    "skins"     🎨  palette circles
    ""          (no icon)
"""

import pygame
import math
from src.engine.renderer import FontManager, draw_glass_panel, draw_rounded_rect, draw_icon


# Icon name aliases so legacy string values still work
_ICON_ALIASES = {
    "▶": "play",
    "⏸": "pause",
    "⚙": "settings",
    "←": "back",
    "✕": "close",
    "🏆": "trophy",
    "🎨": "skins",
    "resume": "play",
    "▶ ": "play",
    "◀": "left",
    "✓": "check",
}


def _resolve_icon(icon: str) -> str:
    """Map a Unicode glyph or keyword to a canonical draw_icon name."""
    s = icon.strip()
    return _ICON_ALIASES.get(s, s)


class GlassButton:
    """Glassmorphism button with hover/press animation, focus ring, and click flash.

    Icons are rendered as pygame primitives — no font glyph required.
    """

    def __init__(self, rect: pygame.Rect, text: str,
                 font_size: int = 26,
                 color: tuple = (255, 255, 255),
                 accent: tuple = (0, 200, 255),
                 icon: str = ""):
        self.rect    = rect
        self.text    = text
        self.color   = color
        self.accent  = accent
        self.icon    = _resolve_icon(icon)   # canonical name for draw_icon()
        self._font   = FontManager.get(font_size, bold=True)
        self._hover  = False
        self._press  = False
        self._hover_t = 0.0
        self._click_t = 0.0
        self._focused = False
        self._enabled = True

    # ── Properties ────────────────────────────────────────────────────────────
    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, v):
        self._enabled = v

    @property
    def focused(self):
        return self._focused

    @focused.setter
    def focused(self, v: bool):
        self._focused = v

    # ── Event handling ────────────────────────────────────────────────────────
    def handle_event(self, event) -> bool:
        """Returns True if button was activated."""
        if not self._enabled:
            return False

        if event.type == pygame.MOUSEMOTION:
            self._hover = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self._press = True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._press and self.rect.collidepoint(event.pos):
                self._press = False
                self._click_t = 1.0
                return True
            self._press = False

        elif event.type == pygame.KEYDOWN and self._focused:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._click_t = 1.0
                return True

        return False

    # ── Update ────────────────────────────────────────────────────────────────
    def update(self, dt: float) -> None:
        target = 1.0 if self._hover else 0.0
        self._hover_t += (target - self._hover_t) * min(dt * 8, 1.0)
        if self._click_t > 0:
            self._click_t = max(0.0, self._click_t - dt * 5)

    # ── Draw ──────────────────────────────────────────────────────────────────
    def draw(self, surface: pygame.Surface) -> None:
        t = self._hover_t

        # Panel background
        base_alpha   = int(40 + 40 * t)
        border_alpha = int(80 + 120 * t)
        draw_glass_panel(surface, self.rect,
                         self.accent if t > 0.3 else (255, 255, 255),
                         base_alpha, border_alpha, radius=14)

        # Keyboard focus ring
        if self._focused:
            ring_pulse = 0.7 + 0.3 * math.sin(pygame.time.get_ticks() * 0.006)
            ring_alpha = int(220 * ring_pulse)
            ring_surf  = pygame.Surface(
                (self.rect.width + 8, self.rect.height + 8), pygame.SRCALPHA)
            pygame.draw.rect(ring_surf, (*self.accent, ring_alpha),
                             ring_surf.get_rect(), width=2, border_radius=17)
            surface.blit(ring_surf, (self.rect.x - 4, self.rect.y - 4))

        # Scale on hover / press
        scale = 1.0 + 0.05 * t
        if self._press:
            scale = 0.92

        # Text colour
        col = tuple(int(self.color[i] + (self.accent[i] - self.color[i]) * t * 0.5)
                    for i in range(3))
        if not self._enabled:
            col = (100, 100, 100)

        # ── Layout: [icon]  [text] ────────────────────────────────────────────
        icon_size = int(self.rect.height * 0.42)   # scale icon to button height
        ICON_PAD  = 8    # gap between icon and text

        text_surf = self._font.render(self.text, True, col)

        if self.icon:
            total_w = icon_size + ICON_PAD + text_surf.get_width()
            start_x = self.rect.centerx - total_w // 2

            # Draw icon primitive
            icon_cx = int(start_x + icon_size // 2)
            icon_cy = self.rect.centery
            if scale != 1.0:
                icon_size = int(icon_size * scale)
            icon_col = col if not self._enabled else col
            draw_icon(surface, self.icon, (icon_cx, icon_cy), icon_size, icon_col)

            # Draw text to the right of the icon
            text_x = start_x + icon_size + ICON_PAD
            if scale != 1.0:
                tw = int(text_surf.get_width() * scale)
                th = int(text_surf.get_height() * scale)
                text_surf = pygame.transform.scale(text_surf, (tw, th))
            text_y = self.rect.centery - text_surf.get_height() // 2
            surface.blit(text_surf, (text_x, text_y))
        else:
            # Text-only, centred
            if scale != 1.0:
                tw = int(text_surf.get_width() * scale)
                th = int(text_surf.get_height() * scale)
                text_surf = pygame.transform.scale(text_surf, (tw, th))
            rr = text_surf.get_rect(center=self.rect.center)
            surface.blit(text_surf, rr)

        # Glow underline when hovered
        if t > 0.1:
            uw = int(self.rect.width * 0.7 * t)
            us = pygame.Surface((uw, 2), pygame.SRCALPHA)
            us.fill((*self.accent, int(200 * t)))
            surface.blit(us, (self.rect.centerx - uw // 2, self.rect.bottom - 4))

        # Pulsing outer glow ring on hover
        if t > 0.3:
            pulse       = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() * 0.004)
            glow_alpha  = int(60 * t * pulse)
            gw = self.rect.width  + 16
            gh = self.rect.height + 16
            gs = pygame.Surface((gw, gh), pygame.SRCALPHA)
            pygame.draw.rect(gs, (*self.accent, glow_alpha),
                             gs.get_rect(), border_radius=18)
            surface.blit(gs, (self.rect.x - 8, self.rect.y - 8),
                         special_flags=pygame.BLEND_RGBA_ADD)

        # Click-flash overlay
        if self._click_t > 0:
            flash_alpha = int(180 * self._click_t)
            fs = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            fs.fill((255, 255, 255, flash_alpha))
            pygame.draw.rect(fs, (0, 0, 0, 0), fs.get_rect(), border_radius=14)
            surface.blit(fs, self.rect.topleft, special_flags=pygame.BLEND_RGBA_ADD)


# ── SliderWidget ──────────────────────────────────────────────────────────────

class SliderWidget:
    """Horizontal slider for volume/settings."""

    def __init__(self, rect: pygame.Rect, label: str, value: float,
                 min_val: float = 0.0, max_val: float = 1.0,
                 accent: tuple = (0, 200, 255)):
        self.rect      = rect
        self.label     = label
        self.value     = value
        self.min_val   = min_val
        self.max_val   = max_val
        self.accent    = accent
        self._dragging = False
        self._font       = FontManager.get(20)
        self._label_font = FontManager.get(18)

    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self._dragging = True
                self._update_value(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._dragging = False
        elif event.type == pygame.MOUSEMOTION and self._dragging:
            self._update_value(event.pos[0])
            return True
        return False

    def _update_value(self, mouse_x: int) -> None:
        t = (mouse_x - self.rect.x) / max(self.rect.width, 1)
        self.value = self.min_val + (self.max_val - self.min_val) * max(0.0, min(1.0, t))

    def draw(self, surface: pygame.Surface) -> None:
        track_y = self.rect.centery
        pygame.draw.line(surface, (60, 60, 80),
                         (self.rect.left, track_y), (self.rect.right, track_y), 4)
        t      = (self.value - self.min_val) / max(self.max_val - self.min_val, 0.001)
        fill_x = self.rect.left + int(self.rect.width * t)
        pygame.draw.line(surface, self.accent,
                         (self.rect.left, track_y), (fill_x, track_y), 4)
        pygame.draw.circle(surface, self.accent,    (fill_x, track_y), 10)
        pygame.draw.circle(surface, (255, 255, 255), (fill_x, track_y), 6)
        label_surf = self._label_font.render(self.label, True, (200, 200, 220))
        surface.blit(label_surf, (self.rect.left, self.rect.top - 22))
        val_pct  = int(self.value / max(self.max_val, 0.001) * 100)
        val_surf = self._font.render(f"{val_pct}%", True, self.accent)
        surface.blit(val_surf, (self.rect.right + 10, track_y - 10))


# ── AnimatedCounter ───────────────────────────────────────────────────────────

class AnimatedCounter:
    """Smoothly animates to a target integer value."""

    def __init__(self, value: int = 0):
        self._display = float(value)
        self._target  = float(value)
        self._speed   = 8.0

    def set_target(self, v: int) -> None:
        self._target = float(v)

    def update(self, dt: float) -> None:
        self._display += (self._target - self._display) * min(dt * self._speed, 1.0)

    @property
    def display_value(self) -> int:
        return int(round(self._display))


# ── NotificationBanner ────────────────────────────────────────────────────────

class NotificationBanner:
    """Achievement / power-up notification that fades in and out."""

    def __init__(self, screen_w: int):
        self.screen_w   = screen_w
        self._queue:    list = []
        self._current:  dict = None
        self._timer:    float = 0.0
        self._duration: float = 2.5
        self._font  = FontManager.get(24, bold=True)
        self._small = FontManager.get(18)

    def push(self, title: str, subtitle: str = "",
             color: tuple = (0, 200, 255)) -> None:
        self._queue.append({"title": title, "subtitle": subtitle, "color": color})

    def update(self, dt: float) -> None:
        if self._current is None and self._queue:
            self._current = self._queue.pop(0)
            self._timer   = self._duration
        if self._current:
            self._timer -= dt
            if self._timer <= 0:
                self._current = None

    def draw(self, surface: pygame.Surface) -> None:
        if not self._current:
            return
        slide = int((1.0 - min(1.0, (self._duration - self._timer) * 4)) * (-60))
        w, h  = 340, 60
        x = (self.screen_w - w) // 2
        y = 10 + slide
        panel = pygame.Surface((w, h), pygame.SRCALPHA)
        col   = self._current["color"]
        pygame.draw.rect(panel, (*col, 40),  (0, 0, w, h), border_radius=12)
        pygame.draw.rect(panel, (*col, 150), (0, 0, w, h), width=2, border_radius=12)
        surface.blit(panel, (x, y))
        title_surf = self._font.render(self._current["title"], True, (255, 255, 255))
        surface.blit(title_surf, (x + 16, y + 8))
        if self._current["subtitle"]:
            sub_surf = self._small.render(self._current["subtitle"], True, (180, 200, 220))
            surface.blit(sub_surf, (x + 16, y + 36))
