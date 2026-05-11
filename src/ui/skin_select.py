"""
src/ui/skin_select.py
Skin selection screen.
"""

import pygame
import math
from src.engine.renderer import FontManager, draw_glass_panel, draw_glow
from src.ui.widgets import GlassButton
from src.entities.bird import SKINS, SKIN_ORDER


class SkinSelectUI:
    def __init__(self, screen_w: int, screen_h: int):
        self.w = screen_w
        self.h = screen_h
        self._title_font = FontManager.get(42, bold=True)
        self._name_font  = FontManager.get(28, bold=True)
        self._info_font  = FontManager.get(18)

        cx = screen_w//2
        bw, bh = 60, 44
        self.btn_left  = GlassButton(pygame.Rect(cx-160-bw//2, screen_h//2+20, bw, bh), "", icon="◀")
        self.btn_right = GlassButton(pygame.Rect(cx+160-bw//2, screen_h//2+20, bw, bh), "", icon="▶")
        self.btn_select= GlassButton(pygame.Rect(cx-100, screen_h//2+110, 200, 50), "SELECT", accent=(0,220,120), icon="✓")
        self.btn_back  = GlassButton(pygame.Rect(cx-90, screen_h//2+175, 180, 48), "BACK", accent=(255,100,100), icon="←")
        self._buttons  = [self.btn_left, self.btn_right, self.btn_select, self.btn_back]

        self._idx = 0
        self._anim_t = 0.0
        self._preview_t = 0.0

    def setup(self, settings) -> None:
        if settings.active_skin in SKIN_ORDER:
            self._idx = SKIN_ORDER.index(settings.active_skin)

    def handle_event(self, event, settings) -> str:
        if self.btn_left.handle_event(event):
            self._idx = (self._idx - 1) % len(SKIN_ORDER)
        if self.btn_right.handle_event(event):
            self._idx = (self._idx + 1) % len(SKIN_ORDER)
        if self.btn_select.handle_event(event):
            settings.active_skin = SKIN_ORDER[self._idx]
            settings.save()
            return "back"
        if self.btn_back.handle_event(event):
            return "back"
        return ""

    def update(self, dt: float) -> None:
        self._anim_t += dt
        self._preview_t += dt
        for b in self._buttons:
            b.update(dt)

    def draw(self, surface: pygame.Surface, settings) -> None:
        # Dark bg
        ov = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        ov.fill((5,5,20,240))
        surface.blit(ov, (0,0))

        cx = self.w//2; cy = self.h//2

        # Title
        ti = self._title_font.render("SELECT SKIN", True, (255,255,255))
        surface.blit(ti, ti.get_rect(center=(cx, 80)))

        skin_name = SKIN_ORDER[self._idx]
        skin = SKINS[skin_name]
        unlocked = skin_name in settings.unlocked_skins

        # Preview panel
        pw, ph = 200, 200
        px = cx-pw//2; py = cy-ph//2-30
        draw_glass_panel(surface, pygame.Rect(px,py,pw,ph), skin["body"], 50, 120, 20)

        # Draw bird preview (large)
        bx = cx; by = cy - 30
        hover = int(math.sin(self._preview_t*2)*8)
        r = 32
        wing_angle = 20*math.sin(self._preview_t*4)

        # Body
        pygame.draw.circle(surface, skin["body"], (bx, by+hover), r)
        # Highlight
        hl = tuple(min(255,c+60) for c in skin["body"])
        pygame.draw.circle(surface, hl, (bx-5, by+hover-6), r//2)
        # Wing
        wing_r = int(r*0.75)
        wy = by+hover + int(wing_angle*0.4)
        pygame.draw.ellipse(surface, skin["wing"],
                            (bx-r//2-wing_r, wy-wing_r//2, wing_r*2, wing_r))
        # Eye
        pygame.draw.circle(surface, (255,255,255), (bx+r//2, by+hover-r//3), 8)
        pygame.draw.circle(surface, skin["eye"], (bx+r//2+1, by+hover-r//3), 5)
        # Beak
        pygame.draw.polygon(surface, skin["beak"], [
            (bx+r, by+hover-3),(bx+r+14,by+hover),(bx+r,by+hover+3)
        ])

        # Glow under bird
        draw_glow(surface, skin["body"], (bx, by+hover), 60, 0.4)

        # Name
        locked_label = "" if unlocked else " 🔒"
        name_surf = self._name_font.render(skin_name.upper().replace("_"," ") + locked_label,
                                           True, skin["body"])
        surface.blit(name_surf, name_surf.get_rect(center=(cx, cy+80)))

        if not unlocked:
            info = self._info_font.render("Reach score 50 to unlock!", True, (180,180,200))
            surface.blit(info, info.get_rect(center=(cx, cy+112)))

        self.btn_select.enabled = unlocked
        for b in self._buttons:
            b.draw(surface)
