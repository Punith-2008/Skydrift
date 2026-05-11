"""
src/systems/achievements.py
Achievement system — 12 achievements with unlock tracking.
"""

import json
import os

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "assets", "data"
)
ACH_FILE = os.path.join(DATA_DIR, "achievements.json")

ACHIEVEMENTS = [
    {"id": "first_flight",   "name": "First Flight",     "desc": "Play your first game",         "icon": "🐦", "condition": lambda s: s.get("games", 0) >= 1},
    {"id": "score_10",       "name": "Getting Started",  "desc": "Reach score 10",               "icon": "🌟", "condition": lambda s: s.get("best_score", 0) >= 10},
    {"id": "score_25",       "name": "Rising Star",      "desc": "Reach score 25",               "icon": "⭐", "condition": lambda s: s.get("best_score", 0) >= 25},
    {"id": "score_50",       "name": "Sky Surfer",       "desc": "Reach score 50",               "icon": "🚀", "condition": lambda s: s.get("best_score", 0) >= 50},
    {"id": "score_100",      "name": "Century",          "desc": "Reach score 100",              "icon": "💯", "condition": lambda s: s.get("best_score", 0) >= 100},
    {"id": "coins_50",       "name": "Coin Collector",   "desc": "Collect 50 coins total",       "icon": "💰", "condition": lambda s: s.get("total_coins", 0) >= 50},
    {"id": "coins_200",      "name": "Gold Rush",        "desc": "Collect 200 coins total",      "icon": "🏆", "condition": lambda s: s.get("total_coins", 0) >= 200},
    {"id": "biomes_3",       "name": "World Traveler",   "desc": "Reach 3 different biomes",     "icon": "🌍", "condition": lambda s: s.get("max_biome_depth", 0) >= 2},
    {"id": "biomes_all",     "name": "Dimension Hopper", "desc": "See all 7 biomes",             "icon": "🌌", "condition": lambda s: s.get("max_biome_depth", 0) >= 6},
    {"id": "powerup_shield", "name": "Shielded",         "desc": "Use a shield power-up",        "icon": "🛡", "condition": lambda s: s.get("shields_used", 0) >= 1},
    {"id": "combo_x3",       "name": "Combo King",       "desc": "Get a 3x combo multiplier",    "icon": "🔥", "condition": lambda s: s.get("max_combo_mult", 0) >= 3},
    {"id": "no_powerup_25",  "name": "Pure Skill",       "desc": "Score 25 with no power-ups",   "icon": "🎯", "condition": lambda s: s.get("best_no_powerup", 0) >= 25},
]


class AchievementSystem:
    def __init__(self):
        self._unlocked: set = set()
        self._stats: dict = {}
        self._pending_unlocks: list = []   # unlocked this session for display
        self.load()

    def load(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        if os.path.exists(ACH_FILE):
            try:
                with open(ACH_FILE, "r") as f:
                    data = json.load(f)
                self._unlocked = set(data.get("unlocked", []))
                self._stats = data.get("stats", {})
            except Exception:
                pass

    def save(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(ACH_FILE, "w") as f:
            json.dump({"unlocked": list(self._unlocked), "stats": self._stats}, f, indent=2)

    def update_stats(self, **kwargs):
        for k, v in kwargs.items():
            if k.startswith("max_") or k.startswith("best"):
                self._stats[k] = max(self._stats.get(k, 0), v)
            else:
                self._stats[k] = self._stats.get(k, 0) + v

    def check(self):
        """Check all achievements, populate pending_unlocks for new ones."""
        for ach in ACHIEVEMENTS:
            if ach["id"] not in self._unlocked:
                try:
                    if ach["condition"](self._stats):
                        self._unlocked.add(ach["id"])
                        self._pending_unlocks.append(ach)
                except Exception:
                    pass
        if self._pending_unlocks:
            self.save()

    def pop_pending(self):
        p = self._pending_unlocks[:]
        self._pending_unlocks.clear()
        return p

    def get_all(self):
        return [(a, a["id"] in self._unlocked) for a in ACHIEVEMENTS]
