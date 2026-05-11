"""
src/engine/game.py
Main game class — state machine, game loop, all subsystem coordination.

States: MENU | PLAYING | PAUSED | GAME_OVER | LEADERBOARD | SETTINGS | SKINS
"""

import pygame
import math
import random
import os
import sys

from src.engine.settings import Settings
from src.engine.audio import AudioManager
from src.engine.camera import Camera
from src.engine.renderer import FontManager, draw_gradient_rect

from src.biomes.volcano     import VolcanoBiome
from src.biomes.ice_world   import IceWorldBiome
from src.biomes.deep_space  import DeepSpaceBiome
from src.biomes.jungle      import JungleBiome
from src.biomes.ocean       import OceanBiome
from src.biomes.desert      import DesertBiome
from src.biomes.neon_digital import NeonDigitalBiome

from src.entities.bird    import Bird
from src.entities.pipe    import PipeManager
from src.entities.coin    import CoinManager
from src.entities.powerup import PowerUpManager

from src.effects.particles   import ParticleEmitter
from src.effects.weather     import WeatherSystem
from src.effects.transitions import BiomeTransition

from src.systems.scoring      import ScoringSystem
from src.systems.achievements import AchievementSystem
from src.systems.challenge    import DailyChallenge

from src.ui.menu          import MainMenu
from src.ui.hud           import HUD
from src.ui.pause         import PauseMenu
from src.ui.game_over     import GameOverScreen
from src.ui.settings_ui  import SettingsUI
from src.ui.skin_select   import SkinSelectUI
from src.ui.widgets       import NotificationBanner


# ── Constants ─────────────────────────────────────────────────────────────────
GROUND_H = 60
BIOME_CHANGE_EVERY = 15    # pipes passed before biome change
GROUND_SCROLL_SPEED = 1.0  # relative to pipe speed


class GameState:
    MENU        = "menu"
    PLAYING     = "playing"
    PAUSED      = "paused"
    GAME_OVER   = "game_over"
    SETTINGS    = "settings"
    SKINS       = "skins"


class Game:
    """Top-level game class. Call run() to start the main loop."""

    def __init__(self):
        self.settings = Settings.load()
        self._init_display()

        self.clock = pygame.time.Clock()
        self.state = GameState.MENU
        self._prev_state = GameState.MENU

        # Core systems
        self.audio   = AudioManager()
        self.camera  = Camera()
        self.scoring = ScoringSystem()
        self.achievements = AchievementSystem()
        self.challenge    = DailyChallenge()

        W, H = self.settings.width, self.settings.height

        self._biome_classes = [
            OceanBiome, VolcanoBiome, IceWorldBiome, DeepSpaceBiome,
            JungleBiome, DesertBiome, NeonDigitalBiome
        ]
        self._biomes = [cls(W, H) for cls in self._biome_classes]
        self._biome_idx = 0
        self._biome_name_timer = 0.0

        # Entities
        self.bird     = Bird(W * 0.25, H * 0.5, self.settings.active_skin)
        self.pipes    = PipeManager(W, H)
        self.coins    = CoinManager(W, H)
        self.powerups = PowerUpManager(W, H)

        # Effects
        self.particles  = ParticleEmitter()
        self.weather    = WeatherSystem(W, H)
        self.transition = BiomeTransition(W, H)

        # Ground scroll
        self._ground_scroll = 0.0
        self._ground_tiles  = self._build_ground_tiles()

        # Power-up state
        self._active_powerup  = ""
        self._powerup_timer   = 0.0
        self._slowmo_scale    = 1.0
        self._magnet_active   = False

        # Screens
        self.menu        = MainMenu(W, H)
        self.hud         = HUD(W, H)
        self.pause_menu  = PauseMenu(W, H)
        self.game_over   = GameOverScreen(W, H)
        self.settings_ui = SettingsUI(W, H)
        self.skin_ui     = SkinSelectUI(W, H)
        self.notify      = NotificationBanner(W)

        self._settings_from_state = GameState.MENU  # where to return after settings

        # Screenshot counter
        self._screenshot_idx = 0

        # Force unlock all skins per user request
        all_skins = ["classic", "cyber", "lava", "ghost", "neon", "cosmic"]
        for s in all_skins:
            if s not in self.settings.unlocked_skins:
                self.settings.unlocked_skins.append(s)
        self.settings.save()

        # Start menu music
        sb = getattr(self.settings, 'starting_biome', 'ocean')
        vol = self.settings.volume_master if getattr(self.settings, 'sound_enabled', True) else 0.0
        self.audio.set_volumes(vol, self.settings.volume_music, self.settings.volume_sfx)
        self.audio.play_biome_music(sb)
        self.menu.btn_biome.text = f"BIOME: {sb.upper().replace('_', ' ')}"

    # ── Display init ──────────────────────────────────────────────────────────
    def _init_display(self):
        W, H = self.settings.width, self.settings.height
        flags = pygame.FULLSCREEN if self.settings.fullscreen else 0
        self.screen = pygame.display.set_mode((W, H), flags)
        pygame.display.set_caption("SkyDrift")

    def _toggle_fullscreen(self):
        s = self.settings
        s.fullscreen = not s.fullscreen
        pygame.display.quit()
        pygame.display.init()
        flags = pygame.FULLSCREEN if s.fullscreen else 0
        self.screen = pygame.display.set_mode((s.width, s.height), flags)
        pygame.display.set_caption("SkyDrift")

    # ── Ground tiles ─────────────────────────────────────────────────────────
    def _build_ground_tiles(self):
        """Pre-build a repeating ground tile surface."""
        W = self.settings.width
        tile_w = 40
        tiles = []
        for tx in range(0, W * 2, tile_w):
            tiles.append(tx)
        return tiles

    # ── Game reset ────────────────────────────────────────────────────────────
    def _start_game(self):
        W, H = self.settings.width, self.settings.height
        
        sb = getattr(self.settings, 'starting_biome', 'ocean')
        self._biome_idx = 0
        for i, b in enumerate(self._biomes):
            if b.NAME == sb:
                self._biome_idx = i
                break
                
        biome = self._biomes[self._biome_idx]

        # Reset all entities
        self.bird = Bird(W * 0.25, H * 0.5, self.settings.active_skin)
        self.pipes.reset(self.settings.pipe_speed_base,
                         self.settings.pipe_gap,
                         biome.get_pipe_scheme())
        self.coins.reset(self.settings.pipe_speed_base)
        self.powerups.reset(self.settings.pipe_speed_base)
        self.particles.clear()
        self.scoring.reset()

        self._ground_scroll = 0.0
        self._active_powerup = ""
        self._powerup_timer  = 0.0
        self._slowmo_scale   = 1.0
        self._magnet_active  = False
        self._biome_name_timer = 3.0

        self._no_powerup_run = True   # track for achievement

        # Weather
        self.weather.set_mode(biome.WEATHER_MODE)
        # Music
        self.audio.play_biome_music(biome.MUSIC_KEY)
        # Achievements
        self.achievements.update_stats(games=1)

        self.state = GameState.PLAYING

    # ── Main loop ─────────────────────────────────────────────────────────────
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(self.settings.fps_limit) / 1000.0
            dt = min(dt, 0.05)  # cap at 50ms to avoid spiral of death

            # ── Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F12:
                        self._take_screenshot()
                    if event.key in (pygame.K_ESCAPE, pygame.K_p) and self.state == GameState.PLAYING:
                        self.state = GameState.PAUSED
                self._handle_event(event)

            # ── Update
            self._update(dt)

            # ── Draw
            self._draw()
            pygame.display.flip()

        self.settings.save()

    def _handle_event(self, event):
        s = self.state

        if s == GameState.MENU:
            action = self.menu.handle_event(event, self.settings)
            if action == "play":
                self.audio.play("click")
                self._start_game()
            elif action in ("cycle_biome_next", "cycle_biome_prev"):
                self.audio.play("click")
                b_list = ["ocean", "volcano", "ice_world", "deep_space", "jungle", "desert", "neon_digital"]
                current = getattr(self.settings, 'starting_biome', 'ocean')
                idx = b_list.index(current) if current in b_list else 0
                if action == "cycle_biome_next":
                    next_biome = b_list[(idx + 1) % len(b_list)]
                else:
                    next_biome = b_list[(idx - 1) % len(b_list)]
                self.settings.starting_biome = next_biome
                self.settings.save()
                self.menu.btn_biome.text = f"BIOME: {next_biome.upper().replace('_', ' ')}"
                self.audio.play_biome_music(next_biome)
            elif action == "quit":
                self.audio.play("click")
                # Instead of just breaking, we can post a QUIT event
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif action == "settings":
                self.audio.play("click")
                self.settings_ui.sync_from(self.settings)
                self._settings_from_state = GameState.MENU
                self.state = GameState.SETTINGS
            elif action == "skins":
                self.audio.play("click")
                self.skin_ui.setup(self.settings)
                self.state = GameState.SKINS

        elif s == GameState.PLAYING:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_UP):
                self.bird.flap(self.settings.jump_velocity)
                self.audio.play("flap")
                self._emit_flap_trail()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.bird.flap(self.settings.jump_velocity)
                self.audio.play("flap")
                self._emit_flap_trail()

        elif s == GameState.PAUSED:
            action = self.pause_menu.handle_event(event)
            if action == "resume":
                self.audio.play("click")
                self.state = GameState.PLAYING
            elif action == "settings":
                self.audio.play("click")
                self.settings_ui.sync_from(self.settings)
                self._settings_from_state = GameState.PAUSED
                self.state = GameState.SETTINGS
            elif action == "menu":
                self.audio.play("click")
                self.state = GameState.MENU
                self.audio.play_biome_music(getattr(self.settings, 'starting_biome', 'ocean'))

        elif s == GameState.GAME_OVER:
            action = self.game_over.handle_event(event)
            if action == "retry":
                self.audio.play("click")
                self._start_game()
            elif action == "menu":
                self.audio.play("click")
                self.state = GameState.MENU
                self.audio.play_biome_music(getattr(self.settings, 'starting_biome', 'ocean'))

        elif s == GameState.SETTINGS:
            action = self.settings_ui.handle_event(event, self.settings)
            if action == "back":
                self.audio.play("click")
                vol = self.settings.volume_master if getattr(self.settings, 'sound_enabled', True) else 0.0
                self.audio.set_volumes(vol, self.settings.volume_music, self.settings.volume_sfx)
                self.state = self._settings_from_state
            elif action == "toggle_fullscreen":
                self._toggle_fullscreen()

        elif s == GameState.SKINS:
            action = self.skin_ui.handle_event(event, self.settings)
            if action == "back":
                self.audio.play("click")
                self.state = GameState.MENU

    # ── Update ────────────────────────────────────────────────────────────────
    def _update(self, dt: float):
        s = self.state
        self.camera.update(dt)
        self.notify.update(dt)

        if s == GameState.MENU:
            self.menu.update(dt)

        elif s == GameState.PLAYING:
            self._update_playing(dt)

        elif s == GameState.PAUSED:
            self.pause_menu.update(dt)

        elif s == GameState.GAME_OVER:
            self.game_over.update(dt)



        elif s == GameState.SETTINGS:
            self.settings_ui.update(dt)

        elif s == GameState.SKINS:
            self.skin_ui.update(dt)

        self.transition.update(dt)

    def _update_playing(self, dt: float):
        ts = self._slowmo_scale   # time scale

        # Power-up timers
        if self._active_powerup:
            self._powerup_timer -= dt
            if self._powerup_timer <= 0:
                self._deactivate_powerup()

        # Bird
        biome = self._biomes[self._biome_idx]
        self.bird.update(dt, self.settings.gravity, 650.0,
                         self.settings.height - GROUND_H, ts)

        # Particle trail
        if self.bird.alive and self.settings.particles_enabled:
            skin = self.bird.skin
            self.particles.emit_trail(self.bird.x - 10, self.bird.y,
                                      skin["trail"], count=1)

        scored_pipes = 0
        if self.bird.alive:
            # Pipes
            scored_pipes = self.pipes.update(dt, ts)
            if scored_pipes > 0:
                for _ in range(scored_pipes):
                    pts = self.scoring.add_pipe(self.bird.x, self.bird.y)
                    self.hud.push_score_anim(pts, self.bird.x - 20, self.bird.y - 30)
                self.audio.play("score")
                if self.settings.particles_enabled:
                    self.particles.emit_score_pop(self.bird.x, self.bird.y)

            # Spawn safe coins/powerups linked to newly spawned pipes
            for px, py, ph in self.pipes.just_spawned:
                roll = random.random()
                if roll < 0.08:  # 8% chance to spawn a powerup
                    self.powerups.spawn_safe(px + 40, py, self.pipes.pipe_speed)
                elif roll < 0.70:  # 62% chance to spawn coin patterns
                    diff_lvl = self.coins._difficulty_from_score(self.scoring.score)
                    self.coins.spawn_pattern(
                        px + 40, py, self.pipes.pipe_speed,
                        gap_h=ph, difficulty_level=diff_lvl
                    )

            # Coins
            collected_coins = self.coins.update(dt, self.bird.rect, ts)
            if collected_coins > 0:
                self.scoring.add_coins(collected_coins)
                self.achievements.update_stats(total_coins=collected_coins)
                self.audio.play("coin")
                if self.settings.particles_enabled:
                    self.particles.emit_sparks(self.bird.x, self.bird.y, (255,215,0))

            # Power-ups
            collected_pu = self.powerups.update(dt, self.bird.rect, self.bird, ts)
            if collected_pu:
                self._activate_powerup(collected_pu)
                self._no_powerup_run = False

            # Magnet effect: pull coins
            if self._magnet_active:
                for coin in self.coins._pool:
                    if coin.active and not coin.collected:
                        dx = self.bird.x - coin.x
                        dy = self.bird.y - coin.y
                        dist = max(1, math.sqrt(dx*dx + dy*dy))
                        if dist < 200:
                            coin.x += dx / dist * 150 * dt * ts
                            coin.y += dy / dist * 150 * dt * ts

            # Ground scroll
            self._ground_scroll = (self._ground_scroll + self.pipes.pipe_speed * dt * ts) % (self.settings.width * 2)

            # Difficulty scaling
            self.pipes.increase_difficulty(self.scoring.score)
            self.coins.speed = self.pipes.pipe_speed
            self.powerups.speed = self.pipes.pipe_speed

        # Particles & weather
        self.particles.update(dt)
        self.weather.update(dt)
        self.scoring.update(dt)
        self.hud.update(dt)

        # Ambient particles
        if self.settings.particles_enabled:
            self._emit_ambient(biome, dt)

        # Biome name display timer
        if self._biome_name_timer > 0:
            self._biome_name_timer -= dt

        # Collision
        if self.bird.alive:
            self._check_collisions()

        # Biome change
        if scored_pipes > 0:
            prev_pipes = self.scoring.session_pipes - scored_pipes
            curr_pipes = self.scoring.session_pipes
            if (prev_pipes // BIOME_CHANGE_EVERY) < (curr_pipes // BIOME_CHANGE_EVERY):
                self._advance_biome()

        # Bird death animation done
        if not self.bird.alive and self.bird.death_done:
            self._end_game()

        # Achievements
        self._tick_achievements()

    def _check_collisions(self):
        br = self.bird.rect
        # Ground
        if self.bird.y + self.bird.RADIUS >= self.settings.height - GROUND_H:
            if not self.bird.shielded:
                self._kill_bird()
            return
        # Ceiling
        if self.bird.y - self.bird.RADIUS <= 0:
            if not self.bird.shielded:
                self._kill_bird()
            return
        # Pipes
        if self.pipes.check_collision(br):
            if not self.bird.shielded:
                self._kill_bird()

    def _kill_bird(self):
        self.bird.kill()
        self.audio.play("death")
        self.camera.shake(10, 0.5)
        self.scoring.break_combo()
        if self.settings.particles_enabled:
            self.particles.emit_explosion(self.bird.x, self.bird.y,
                                          self.bird.skin["body"], 40, 250)

    def _advance_biome(self):
        next_idx = (self._biome_idx + 1) % len(self._biomes)
        next_biome = self._biomes[next_idx]

        def _on_transition():
            self._biome_idx = next_idx
            self.pipes.set_scheme(next_biome.get_pipe_scheme())
            self.weather.set_mode(next_biome.WEATHER_MODE)
            self.audio.play_biome_music(next_biome.MUSIC_KEY)
            self._biome_name_timer = 3.0

        self.transition.start(_on_transition, self._biomes[self._biome_idx].TRANSITION_MODE)
        self.audio.play("biome_transition")
        self.achievements.update_stats(max_biome_depth=next_idx)

    def _activate_powerup(self, kind: str):
        self._active_powerup = kind
        self._powerup_timer = 6.0
        self.audio.play("powerup")
        self.notify.push(f"{kind.upper()} ACTIVE!", "Power-up collected!", (0,200,255))
        if kind == "slowmo":
            self._slowmo_scale = 0.4
        elif kind == "magnet":
            self._magnet_active = True
        self.achievements.update_stats(shields_used=1 if kind=="shield" else 0)

    def _deactivate_powerup(self):
        if self._active_powerup == "slowmo":
            self._slowmo_scale = 1.0
        elif self._active_powerup == "magnet":
            self._magnet_active = False
        self._active_powerup = ""
        self._powerup_timer = 0.0

    def _emit_ambient(self, biome, dt: float):
        ap = biome.get_ambient_particle()
        if ap == "none":
            return
        W, H = self.settings.width, self.settings.height
        if ap == "lava" and random.random() < dt * 8:
            self.particles.emit_lava(random.randint(0, W), H - GROUND_H)
        elif ap == "bubbles" and random.random() < dt * 5:
            self.particles.emit_bubble(random.randint(0, W), H - GROUND_H)
        elif ap == "stars" and random.random() < dt * 10:
            self.particles.emit_star(random.randint(0, W), random.randint(0, H//2))
        elif ap == "neon" and random.random() < dt * 4:
            col = random.choice([(0,255,200),(255,0,200),(255,200,0)])
            self.particles.emit_neon(random.randint(0, W), random.randint(50, H-100), col)
        elif ap == "sparks" and random.random() < dt * 3:
            self.particles.emit_sparks(random.randint(0, W), H - GROUND_H,
                                       (255,180,0))
        elif ap == "snow" and random.random() < dt * 5:
            self.particles.emit_snow(random.randint(0, W), 0)

    def _emit_flap_trail(self):
        if not self.settings.particles_enabled:
            return
        for _ in range(6):
            self.particles.emit_trail(self.bird.x - 8, self.bird.y + 5,
                                      self.bird.skin["trail"], 1, 80)

    def _tick_achievements(self):
        self.achievements.update_stats(
            best_score=self.scoring.score,
            max_combo_mult=self.scoring.multiplier,
            best_no_powerup=self.scoring.score if self._no_powerup_run else 0,
        )
        self.achievements.check()
        for ach in self.achievements.pop_pending():
            self.notify.push(f"🏅 {ach['name']}", ach["desc"], (255,180,0))
            self.audio.play("achievement")

    def _end_game(self):
        score = self.scoring.score
        coins = self.scoring.coins
        is_hs = score > self.settings.high_score and score > 0
        best  = max(self.settings.high_score, score)

        if self.settings.high_score < score:
            self.settings.high_score = score
        self.settings.total_coins += coins
        self.settings.save()

        # Unlock skins by score
        if score >= 50 and "cyber" not in self.settings.unlocked_skins:
            self.settings.unlock_skin("cyber")
            self.notify.push("Skin Unlocked!", "Cyber bird is yours!", (0,200,255))
        if score >= 100 and "lava" not in self.settings.unlocked_skins:
            self.settings.unlock_skin("lava")
        if score >= 200 and "neon" not in self.settings.unlocked_skins:
            self.settings.unlock_skin("neon")
        if score >= 300 and "ghost" not in self.settings.unlocked_skins:
            self.settings.unlock_skin("ghost")
            self.notify.push("Skin Unlocked!", "Ghost bird is yours!", (200,200,255))
        if score >= 400 and "cosmic" not in self.settings.unlocked_skins:
            self.settings.unlock_skin("cosmic")
            self.notify.push("Skin Unlocked!", "Cosmic bird is yours!", (150,0,255))

        # Daily challenge
        self.challenge.update(score, coins, self.scoring.session_pipes)

        self.game_over.setup(score, best, coins,
                             self.scoring.multiplier, is_hs)
        self.audio.stop_music(500)
        self.state = GameState.GAME_OVER

    # ── Draw ──────────────────────────────────────────────────────────────────
    def _draw(self):
        surf = self.screen
        s = self.state

        if s == GameState.MENU:
            self.menu.draw(surf, self.settings)

        elif s in (GameState.PLAYING, GameState.PAUSED):
            self._draw_game(surf)
            if s == GameState.PAUSED:
                self.pause_menu.draw(surf)

        elif s == GameState.GAME_OVER:
            self._draw_game(surf)
            self.game_over.draw(surf)

        elif s == GameState.SETTINGS:
            self._draw_settings_bg(surf)
            self.settings_ui.draw(surf)

        elif s == GameState.SKINS:
            self.skin_ui.draw(surf, self.settings)

        # Transition overlay (always on top)
        self.transition.draw(surf)
        # Notifications
        self.notify.draw(surf)

    def _draw_settings_bg(self, surface):
        for y in range(self.settings.height):
            t = y / max(self.settings.height-1,1)
            pygame.draw.line(surface, (int(5+15*t),int(5+10*t),int(20+25*t)),
                             (0,y),(self.settings.width-1,y))

    def _draw_game(self, surface: pygame.Surface):
        W, H = self.settings.width, self.settings.height
        ox, oy = self.camera.apply_offset()
        biome = self._biomes[self._biome_idx]

        # Background
        biome.draw_background(surface, self.pipes.scroll_x)

        # Weather
        if self.settings.weather_enabled:
            self.weather.draw(surface)

        # Particles (behind entities)
        self.particles.draw(surface, (ox, oy))

        # Entities
        self.pipes.draw(surface, (ox, oy))
        self.coins.draw(surface, (ox, oy))
        self.powerups.draw(surface, (ox, oy))
        self.bird.draw(surface, (ox, oy))

        # Foreground biome decorations
        biome.draw_foreground(surface, self.pipes.scroll_x)

        # Ground
        self._draw_ground(surface, biome, ox)

        # HUD
        biome_label = biome.NAME.replace("_"," ").title() if self._biome_name_timer > 0 else ""
        self.hud.draw(
            surface,
            score=self.scoring.score,
            coins=self.scoring.coins,
            combo=self.scoring.combo,
            multiplier=self.scoring.multiplier,
            active_powerup=self._active_powerup,
            powerup_timer=self._powerup_timer,
            fps=int(self.clock.get_fps()),
            show_fps=self.settings.show_fps,
            biome_name=biome_label,
        )

        # Daily challenge strip
        self._draw_challenge(surface)

    def _draw_ground(self, surface, biome, ox: int):
        W, H = self.settings.width, self.settings.height
        ground_y = H - GROUND_H
        scheme = biome.get_ground_scheme()

        # Ground fill
        pygame.draw.rect(surface, scheme["color"], (0, ground_y, W, GROUND_H))
        # Top line
        pygame.draw.line(surface, scheme["line"], (0, ground_y), (W, ground_y), 3)

        # Scrolling ground pattern
        tile_w = 40
        for tx in range(0, W + tile_w, tile_w):
            offset_x = int(self._ground_scroll) % tile_w
            px = tx - offset_x + ox
            pygame.draw.line(surface, (*scheme["line"], 80) if len(scheme["line"]) > 3 else scheme["line"],
                             (px, ground_y + 10), (px, H), 1)

    def _draw_challenge(self, surface):
        if self.challenge.complete:
            return
        W = self.settings.width
        desc = self.challenge.description
        prog = f"{min(self.challenge.progress, self.challenge.target)}/{self.challenge.target}"
        tf = FontManager.get(15)
        ds = tf.render(f"📅 {desc} [{prog}]", True, (180, 180, 100))
        surface.blit(ds, (W//2 - ds.get_width()//2, self.settings.height - 22))

    def _take_screenshot(self):
        os.makedirs("screenshots", exist_ok=True)
        name = f"screenshots/skydrift_{self._screenshot_idx:04d}.png"
        pygame.image.save(self.screen, name)
        self._screenshot_idx += 1
        self.notify.push("Screenshot saved!", name, (0,255,100))
