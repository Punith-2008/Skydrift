"""
src/systems/challenge.py
Daily challenge — seed-based objective for extra replay value.
"""

import datetime
import random


CHALLENGE_TYPES = [
    {"id": "score_target",  "template": "Score {n} points today",      "metric": "score",  "range": (8, 30)},
    {"id": "coin_target",   "template": "Collect {n} coins in a run",  "metric": "coins",  "range": (5, 20)},
    {"id": "survive_pipes", "template": "Pass {n} pipes without dying", "metric": "pipes",  "range": (5, 25)},
]


class DailyChallenge:
    def __init__(self):
        self._today = datetime.date.today().isoformat()
        seed = int(self._today.replace("-", ""))
        rng = random.Random(seed)
        ctype = rng.choice(CHALLENGE_TYPES)
        n = rng.randint(*ctype["range"])
        self.description: str = ctype["template"].format(n=n)
        self.metric: str = ctype["metric"]
        self.target: int = n
        self.progress: int = 0
        self.complete: bool = False

    def update(self, score: int, coins: int, pipes: int) -> bool:
        """Returns True if just completed."""
        if self.complete:
            return False
        if self.metric == "score":
            self.progress = score
        elif self.metric == "coins":
            self.progress = coins
        elif self.metric == "pipes":
            self.progress = pipes
        if self.progress >= self.target:
            self.complete = True
            return True
        return False
