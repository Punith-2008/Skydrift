"""
src/systems/leaderboard.py
Persistent JSON leaderboard — top-10 entries with name, score, date.
"""

import json
import os
from datetime import datetime

DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "assets", "data"
)
LEADERBOARD_FILE = os.path.join(DATA_DIR, "leaderboard.json")

MAX_ENTRIES = 10


class Leaderboard:
    def __init__(self):
        self._entries: list = []
        self.load()

    def load(self) -> None:
        os.makedirs(DATA_DIR, exist_ok=True)
        if os.path.exists(LEADERBOARD_FILE):
            try:
                with open(LEADERBOARD_FILE, "r") as f:
                    self._entries = json.load(f)
            except Exception:
                self._entries = []
        else:
            self._entries = []

    def save(self) -> None:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(LEADERBOARD_FILE, "w") as f:
            json.dump(self._entries, f, indent=2)

    def is_high_score(self, score: int) -> bool:
        if len(self._entries) < MAX_ENTRIES:
            return score > 0
        return score > self._entries[-1]["score"]

    def add_entry(self, name: str, score: int, coins: int = 0) -> int:
        """Add entry, keep sorted, return rank (1-based)."""
        entry = {
            "name": name[:16],
            "score": score,
            "coins": coins,
            "date": datetime.now().strftime("%Y-%m-%d"),
        }
        self._entries.append(entry)
        self._entries.sort(key=lambda e: e["score"], reverse=True)
        self._entries = self._entries[:MAX_ENTRIES]
        self.save()
        # Find rank
        for i, e in enumerate(self._entries):
            if e is entry or (e["name"] == entry["name"] and
                              e["score"] == entry["score"]):
                return i + 1
        return MAX_ENTRIES

    def get_entries(self) -> list:
        return self._entries[:]

    def get_best(self) -> int:
        if not self._entries:
            return 0
        return self._entries[0]["score"]
