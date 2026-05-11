"""
src/engine/renderer.py
Rendering utilities: glow surfaces, rounded rects, blur simulation,
alpha-blended overlays, text helpers, icon drawing.

Icon drawing
------------
draw_icon(surface, icon_name, center, size, color) draws crisp pygame-primitive
icons for all standard UI controls:
  "play"     — solid right-pointing triangle  (▶)
  "pause"    — two vertical bars              (⏸)
  "settings" — 8-tooth gear ring              (⚙)
  "back"     — left arrow                     (←)
  "close"    — × cross                        (✕)
  "resume"   — alias of "play"
"""

import pygame
import math


# ── Primitive helpers ─────────────────────────────────────────────────────────

def draw_glow(surface: pygame.Surface, color: tuple, center: tuple,
              radius: int, intensity: float = 0.8) -> None:
    """Draw a radial glow around a point using layered alpha circles."""
    glow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    for r in range(radius, 0, -max(1, radius // 12)):
        alpha = int(intensity * 255 * (1 - r / radius) ** 1.5)
        alpha = max(0, min(255, alpha))
        c = (*color[:3], alpha)
        pygame.draw.circle(glow_surf, c, (radius, radius), r)
    surface.blit(glow_surf, (center[0] - radius, center[1] - radius),
                 special_flags=pygame.BLEND_RGBA_ADD)


def draw_rounded_rect(surface: pygame.Surface, color: tuple,
                      rect: pygame.Rect, radius: int = 12) -> None:
    """Draw a filled rounded rectangle."""
    pygame.draw.rect(surface, color, rect, border_radius=radius)


def draw_rounded_rect_border(surface: pygame.Surface, color: tuple,
                              rect: pygame.Rect, radius: int = 12,
                              width: int = 2) -> None:
    pygame.draw.rect(surface, color, rect, width=width, border_radius=radius)


def draw_glass_panel(surface: pygame.Surface, rect: pygame.Rect,
                     base_color: tuple = (255, 255, 255),
                     alpha: int = 35, border_alpha: int = 80,
                     radius: int = 16) -> None:
    """Glassmorphism panel: semi-transparent fill + frosted border."""
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    r, g, b = base_color[:3]
    pygame.draw.rect(panel, (r, g, b, alpha), panel.get_rect(), border_radius=radius)
    pygame.draw.rect(panel, (r, g, b, border_alpha), panel.get_rect(),
                     width=2, border_radius=radius)
    surface.blit(panel, rect.topleft)


def draw_text(surface: pygame.Surface, text: str, font: pygame.font.Font,
              color: tuple, center: tuple,
              shadow: bool = True, shadow_color: tuple = (0, 0, 0)) -> pygame.Rect:
    """Render text centered at `center`, optionally with a drop shadow."""
    if shadow:
        s = font.render(text, True, (*shadow_color[:3], 180))
        r = s.get_rect(center=(center[0] + 2, center[1] + 2))
        surface.blit(s, r)
    img  = font.render(text, True, color)
    rect = img.get_rect(center=center)
    surface.blit(img, rect)
    return rect


def draw_gradient_rect(surface: pygame.Surface, rect: pygame.Rect,
                        color_top: tuple, color_bottom: tuple) -> None:
    """Fill a rect with a vertical gradient."""
    x, y, w, h = rect
    for i in range(h):
        t = i / max(h - 1, 1)
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * t)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * t)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * t)
        pygame.draw.line(surface, (r, g, b), (x, y + i), (x + w - 1, y + i))


def create_glow_surface(color: tuple, radius: int,
                         intensity: float = 1.0) -> pygame.Surface:
    """Pre-bake a glow surface for reuse."""
    surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    for r in range(radius, 0, -max(1, radius // 16)):
        alpha = int(intensity * 255 * (1 - r / radius) ** 1.8)
        alpha = max(0, min(255, alpha))
        pygame.draw.circle(surf, (*color[:3], alpha), (radius, radius), r)
    return surf


def lerp_color(c1: tuple, c2: tuple, t: float) -> tuple:
    """Linear interpolate between two RGB colours."""
    t = max(0.0, min(1.0, t))
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )


# ── Icon drawing ──────────────────────────────────────────────────────────────

def draw_icon(surface: pygame.Surface, icon_name: str,
              center: tuple, size: int = 16,
              color: tuple = (255, 255, 255)) -> None:
    """Draw a crisp pygame-primitive icon at *center* fitting within *size* px.

    Supported icon names (case-insensitive):
        play / resume  — solid right-pointing triangle
        pause          — two vertical bars
        settings       — 8-tooth gear
        back           — left arrow (←)
        close          — × cross (✕)
        trophy         — simple trophy silhouette
        skins / palette— overlapping circles
    """
    name = icon_name.lower().strip()
    cx, cy = int(center[0]), int(center[1])
    h = size  # half of bounding box for shorthand
    c = color

    if name in ("play", "resume", "right"):
        # Solid right-pointing triangle
        h2 = size // 2
        pts = [
            (cx - h2 // 2, cy - h2),
            (cx - h2 // 2, cy + h2),
            (cx + h2,      cy),
        ]
        pygame.draw.polygon(surface, c, pts)

    elif name == "left":
        # Solid left-pointing triangle
        h2 = size // 2
        pts = [
            (cx + h2 // 2, cy - h2),
            (cx + h2 // 2, cy + h2),
            (cx - h2,      cy),
        ]
        pygame.draw.polygon(surface, c, pts)

    elif name == "pause":
        # Two solid vertical bars
        bar_w = max(2, size // 5)
        bar_h = size
        gap   = max(2, size // 4)
        # Left bar
        pygame.draw.rect(surface, c,
                         (cx - gap - bar_w, cy - bar_h // 2, bar_w, bar_h))
        # Right bar
        pygame.draw.rect(surface, c,
                         (cx + gap,         cy - bar_h // 2, bar_w, bar_h))

    elif name == "settings":
        # 8-tooth gear: outer ring with teeth + inner circle cutout
        teeth     = 8
        r_inner   = size * 0.32
        r_outer   = size * 0.50
        r_hole    = size * 0.18
        tooth_w   = math.pi / teeth * 0.55   # angular half-width of each tooth
        pts = []
        for i in range(teeth * 2):
            angle = i * math.pi / teeth
            r = r_outer if i % 2 == 0 else r_inner
            pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
        pygame.draw.polygon(surface, c, pts)
        # Punch out centre hole (background colour approximation: draw darker circle)
        # Use a slightly darker shade so it contrasts on the gear
        hole_col = tuple(max(0, v - 80) for v in c[:3])
        pygame.draw.circle(surface, hole_col, (cx, cy), int(r_hole))

    elif name in ("back", "left_arrow"):
        # Left-pointing arrow: shaft + arrowhead
        shaft_w = max(2, size // 6)
        head_w  = size // 2
        # Shaft (horizontal bar)
        pygame.draw.rect(surface, c,
                         (cx - head_w // 2, cy - shaft_w // 2,
                          size - 2, shaft_w))
        # Arrowhead (left-pointing triangle)
        ax = cx - head_w // 2
        pts = [
            (ax,                 cy),
            (ax + head_w,        cy - head_w // 2),
            (ax + head_w,        cy + head_w // 2),
        ]
        pygame.draw.polygon(surface, c, pts)

    elif name in ("close", "x", "quit"):
        # × cross — two diagonal lines
        lw = max(2, size // 6)
        h2 = size // 2 - 1
        pygame.draw.line(surface, c, (cx - h2, cy - h2), (cx + h2, cy + h2), lw)
        pygame.draw.line(surface, c, (cx + h2, cy - h2), (cx - h2, cy + h2), lw)

    elif name in ("trophy", "score"):
        # Simple trophy cup outline
        w2 = size // 2
        # Cup body (rounded rect)
        pygame.draw.rect(surface, c,
                         (cx - w2 // 2, cy - w2, w2, w2 + 2),
                         border_radius=4)
        # Handles
        pygame.draw.arc(surface, c,
                        pygame.Rect(cx - w2 - 2, cy - w2, 8, 12),
                        math.pi * 0.5, math.pi * 1.5, max(1, size // 8))
        pygame.draw.arc(surface, c,
                        pygame.Rect(cx + w2 - 6, cy - w2, 8, 12),
                        math.pi * 1.5, math.pi * 2.5, max(1, size // 8))
        # Stem + base
        pygame.draw.rect(surface, c, (cx - 1, cy + 2, 3, w2 // 2))
        pygame.draw.rect(surface, c, (cx - w2 // 2, cy + 2 + w2 // 2, w2, 3))

    elif name in ("skins", "palette"):
        # Three overlapping filled circles
        r = max(3, size // 4)
        offsets = [(-r, r // 2), (r, r // 2), (0, -r // 2)]
        cols    = [(255, 100, 100), (100, 255, 100), (100, 100, 255)]
        for (ox, oy), tc in zip(offsets, cols):
            pygame.draw.circle(surface, tc, (cx + ox, cy + oy), r)

    elif name in ("check", "tick"):
        # Checkmark (✓)
        lw = max(2, size // 6)
        # points for the check mark relative to cx, cy
        # short leg goes down and right, long leg goes up and right
        p1 = (cx - size // 2 + 2, cy)
        p2 = (cx - size // 6, cy + size // 2 - 2)
        p3 = (cx + size // 2 - 2, cy - size // 2 + 2)
        pygame.draw.line(surface, c, p1, p2, lw)
        pygame.draw.line(surface, c, p2, p3, lw)

# ── FontManager ───────────────────────────────────────────────────────────────

class FontManager:
    """Cached font manager — avoids repeated font loading."""

    _cache: dict = {}

    @classmethod
    def get(cls, size: int, bold: bool = False) -> pygame.font.Font:
        key = (size, bold)
        if key not in cls._cache:
            # Try system fonts in preference order
            for name in ("Segoe UI", "Arial", "Helvetica", "DejaVu Sans", None):
                try:
                    if name is None:
                        cls._cache[key] = pygame.font.Font(None, size)
                    else:
                        cls._cache[key] = pygame.font.SysFont(name, size, bold=bold)
                    break
                except Exception:
                    continue
        return cls._cache[key]

    @classmethod
    def get_mono(cls, size: int) -> pygame.font.Font:
        key = ("mono", size)
        if key not in cls._cache:
            for name in ("Consolas", "Courier New", "Lucida Console", None):
                try:
                    if name is None:
                        cls._cache[key] = pygame.font.Font(None, size)
                    else:
                        cls._cache[key] = pygame.font.SysFont(name, size)
                    break
                except Exception:
                    continue
        return cls._cache[key]
