"""
src/engine/settings.py
Settings management — load/save to JSON, dataclass with defaults.
"""

import json
import os
from dataclasses import dataclass, field, asdict
from typing import List

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "assets", "data"
)
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")


@dataclass
class Settings:
    # Audio
    volume_master: float = 1.0
    volume_music: float = 0.6
    volume_sfx: float = 0.8
    sound_enabled: bool = True

    # Display
    width: int = 1280
    height: int = 720
    fps_limit: int = 60
    fullscreen: bool = False
    show_fps: bool = False

    # Gameplay
    difficulty: str = "normal"   # easy | normal | hard
    player_name: str = "Player"

    # Progression
    high_score: int = 0
    total_coins: int = 0
    unlocked_skins: List[str] = field(default_factory=lambda: [
        "classic", "cyber", "lava", "ghost", "neon", "cosmic"
    ])
    active_skin: str = "classic"

    # Feature flags
    particles_enabled: bool = True
    weather_enabled: bool = True
    screen_shake_enabled: bool = True

    # ── computed helpers ─────────────────────────────────────────────────────
    @property
    def gravity(self) -> float:
        return {"easy": 700, "normal": 900, "hard": 1100}[self.difficulty]

    @property
    def jump_velocity(self) -> float:
        return {"easy": -340, "normal": -390, "hard": -430}[self.difficulty]

    @property
    def pipe_speed_base(self) -> float:
        return {"easy": 160, "normal": 210, "hard": 270}[self.difficulty]

    @property
    def pipe_gap(self) -> int:
        return {"easy": 200, "normal": 165, "hard": 135}[self.difficulty]

    # ── persistence ──────────────────────────────────────────────────────────
    def save(self) -> None:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(SETTINGS_FILE, "w") as f:
            json.dump(asdict(self), f, indent=2)

    @classmethod
    def load(cls) -> "Settings":
        if not os.path.exists(SETTINGS_FILE):
            s = cls()
            s.save()
            return s
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
            # Filter only known fields to avoid crashes on old files
            valid = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
            return cls(**valid)
        except Exception:
            return cls()

    def unlock_skin(self, skin_id: str) -> None:
        if skin_id not in self.unlocked_skins:
            self.unlocked_skins.append(skin_id)
