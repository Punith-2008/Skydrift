"""
src/ui/leaderboard_ui.py
Leaderboard screen — top-10 list with animated entries.
"""

import pygame
import math
from src.engine.renderer import FontManager, draw_glass_panel
from src.ui.widgets import GlassButton


RANK_COLORS = [(255,215,0),(192,192,192),(205,127,50)] + [(200,200,220)]*7


class LeaderboardUI:
    def __init__(self, screen_w: int, screen_h: int):
        self.w = screen_w
        self.h = screen_h
        self._title_font = FontManager.get(42, bold=True)
        self._entry_font = FontManager.get(24)
        self._rank_font  = FontManager.get(28, bold=True)
        self._header_font= FontManager.get(18)

        bw, bh = 180, 48
        self.btn_back = GlassButton(pygame.Rect(screen_w//2-bw//2, screen_h-70, bw, bh),
                                    "BACK", accent=(255,100,100), icon="←")
        self._anim_t = 0.0

    def handle_event(self, event) -> str:
        if self.btn_back.handle_event(event):
            return "back"
        return ""

    def update(self, dt: float) -> None:
        self._anim_t += dt
        self.btn_back.update(dt)

    def draw(self, surface: pygame.Surface, entries: list) -> None:
        # Background
        for y in range(self.h):
            t = y/max(self.h-1,1)
            pygame.draw.line(surface, (int(5+10*t),int(5+5*t),int(20+15*t)), (0,y),(self.w-1,y))

        # Panel
        pw, ph = 500, min(600, self.h - 120)
        px = (self.w-pw)//2; py = 80
        draw_glass_panel(surface, pygame.Rect(px,py,pw,ph), (100,120,200), 40, 90, 20)

        # Title
        ti = self._title_font.render("LEADERBOARD", True, (255, 215, 0))
        icon_size = 32
        spacing = 15
        total_w = icon_size + spacing + ti.get_width()
        start_x = self.w // 2 - total_w // 2

        from src.engine.renderer import draw_icon
        draw_icon(surface, "trophy", (start_x + icon_size // 2, 52), icon_size, (255, 215, 0))
        surface.blit(ti, (start_x + icon_size + spacing, 52 - ti.get_height() // 2))

        # Column headers
        hy = py + 18
        headers = [("#", px+20), ("NAME", px+70), ("SCORE", px+280), ("COINS", px+390)]
        for htext, hx in headers:
            hs = self._header_font.render(htext, True, (150,160,200))
            surface.blit(hs, (hx, hy))

        pygame.draw.line(surface, (100,120,200), (px+10,hy+22),(px+pw-10,hy+22), 1)

        # Entries
        entry_h = 44
        for i, entry in enumerate(entries[:10]):
            row_y = py + 48 + i * entry_h
            slide = min(1.0, (self._anim_t - i * 0.05) * 5)
            if slide <= 0:
                continue
            # Highlight top 3
            if i < 3:
                hs = pygame.Surface((pw-20, entry_h-4), pygame.SRCALPHA)
                a = int(30 * slide)
                hs.fill((*RANK_COLORS[i], a))
                surface.blit(hs, (px+10, row_y))

            col = RANK_COLORS[i]
            # Rank number
            rank_s = self._rank_font.render(str(i+1), True, col)
            surface.blit(rank_s, (px+22, row_y+8))
            # Name
            name_s = self._entry_font.render(entry.get("name","?"), True, (220,220,240))
            surface.blit(name_s, (px+72, row_y+10))
            # Score
            sc_s = self._entry_font.render(str(entry.get("score",0)), True, (255,255,180))
            surface.blit(sc_s, (px+282, row_y+10))
            # Coins
            co_s = self._entry_font.render(str(entry.get("coins",0)), True, (255,215,0))
            surface.blit(co_s, (px+392, row_y+10))
            # Date
            # (skip to save space)

        if not entries:
            empty = self._entry_font.render("No scores yet — play a game!", True, (140,140,160))
            surface.blit(empty, empty.get_rect(center=(self.w//2, py+ph//2)))

        self.btn_back.draw(surface)
