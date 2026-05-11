"""
src/engine/camera.py
Camera effects: screen shake, zoom, smooth scroll offset.
"""

import math
import random


class Camera:
    """Applies a shake offset to all draw calls for cinematic impact."""

    def __init__(self):
        self.shake_x: float = 0.0
        self.shake_y: float = 0.0
        self._shake_intensity: float = 0.0
        self._shake_duration: float = 0.0
        self._shake_timer: float = 0.0
        self._shake_freq: float = 30.0   # Hz

        self.zoom: float = 1.0
        self._zoom_target: float = 1.0
        self._zoom_speed: float = 3.0

    # ── public API ───────────────────────────────────────────────────────────
    def shake(self, intensity: float = 8.0, duration: float = 0.35) -> None:
        """Trigger a screen shake effect."""
        self._shake_intensity = intensity
        self._shake_duration = duration
        self._shake_timer = duration

    def set_zoom(self, target: float, speed: float = 3.0) -> None:
        self._zoom_target = target
        self._zoom_speed = speed

    def update(self, dt: float) -> None:
        # Shake decay
        if self._shake_timer > 0:
            self._shake_timer -= dt
            progress = self._shake_timer / max(self._shake_duration, 0.001)
            amp = self._shake_intensity * progress
            self.shake_x = random.uniform(-amp, amp)
            self.shake_y = random.uniform(-amp, amp)
        else:
            self.shake_x = 0.0
            self.shake_y = 0.0
            self._shake_timer = 0.0

        # Smooth zoom
        self.zoom += (self._zoom_target - self.zoom) * min(dt * self._zoom_speed, 1.0)

    def apply_offset(self) -> tuple:
        """Returns (offset_x, offset_y) to add to draw positions."""
        return (int(self.shake_x), int(self.shake_y))
