"""
src/systems/scoring.py
Combo scoring system — multiplier, streak tracking, session stats.
"""


class ScoringSystem:
    """Tracks score, combo streak, multiplier and session statistics."""

    COMBO_THRESHOLD = 5      # pipes without dying to activate combo
    MAX_MULTIPLIER = 5

    def __init__(self):
        self.score: int = 0
        self.combo: int = 0
        self.multiplier: int = 1
        self.coins: int = 0
        self.session_pipes: int = 0
        self.session_coins: int = 0
        self._combo_display_timer: float = 0.0
        self._score_anim_queue: list = []   # list of (value, x, y) for pop-ups

    def reset(self) -> None:
        self.score = 0
        self.combo = 0
        self.multiplier = 1
        self.coins = 0
        self.session_pipes = 0
        self.session_coins = 0
        self._combo_display_timer = 0.0
        self._score_anim_queue.clear()

    def add_pipe(self, x: float = 0, y: float = 0) -> int:
        """Record a passed pipe. Returns points awarded."""
        self.combo += 1
        self.session_pipes += 1
        self.multiplier = min(self.MAX_MULTIPLIER,
                              1 + (self.combo // self.COMBO_THRESHOLD))
        pts = 1 * self.multiplier
        self.score += pts
        self._combo_display_timer = 1.5
        self._score_anim_queue.append((pts, x, y))
        return pts

    def add_coins(self, amount: int) -> None:
        self.coins += amount
        self.session_coins += amount

    def break_combo(self) -> None:
        self.combo = 0
        self.multiplier = 1

    def update(self, dt: float) -> None:
        self._combo_display_timer = max(0, self._combo_display_timer - dt)
        # Trim old animations
        self._score_anim_queue = self._score_anim_queue[-10:]

    def pop_score_anims(self) -> list:
        anims = self._score_anim_queue[:]
        self._score_anim_queue.clear()
        return anims

    @property
    def showing_combo(self) -> bool:
        return self._combo_display_timer > 0 and self.multiplier > 1
