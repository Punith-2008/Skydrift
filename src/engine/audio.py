"""
src/engine/audio.py
Procedural audio synthesis + Pygame mixer management.
All sounds generated at runtime — no audio files required.
"""

import pygame
import numpy as np
import math
import threading


SAMPLE_RATE = 44100
CHANNELS = 2


def _to_sound(samples: np.ndarray) -> pygame.sndarray.Sound:
    """Convert a float32 mono array → stereo pygame.Sound."""
    samples = np.clip(samples, -1.0, 1.0)
    stereo = np.column_stack([samples, samples])
    arr = (stereo * 32767).astype(np.int16)
    return pygame.sndarray.make_sound(arr)


def _sine(freq: float, duration: float, amp: float = 0.5,
          fade_out: bool = True) -> np.ndarray:
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    wave = amp * np.sin(2 * np.pi * freq * t)
    if fade_out:
        env = np.linspace(1.0, 0.0, len(wave)) ** 0.5
        wave *= env
    return wave.astype(np.float32)


def _noise(duration: float, amp: float = 0.3) -> np.ndarray:
    n = int(SAMPLE_RATE * duration)
    wave = amp * (np.random.rand(n) * 2 - 1)
    env = np.linspace(1.0, 0.0, n) ** 0.3
    return (wave * env).astype(np.float32)


def _sweep(f_start: float, f_end: float, duration: float, amp: float = 0.5) -> np.ndarray:
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    freq = np.linspace(f_start, f_end, len(t))
    phase = np.cumsum(2 * np.pi * freq / SAMPLE_RATE)
    wave = amp * np.sin(phase)
    env = np.linspace(1.0, 0.0, len(wave)) ** 0.6
    return (wave * env).astype(np.float32)


def _arpeggio(notes: list, note_dur: float = 0.07, amp: float = 0.4) -> np.ndarray:
    parts = [_sine(f, note_dur, amp) for f in notes]
    return np.concatenate(parts).astype(np.float32)


def _build_biome_loop(freqs: list, duration: float = 2.0, amp: float = 0.2) -> np.ndarray:
    """
    Build a simple looping ambient tone from a list of frequencies.
    """
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    wave = np.zeros(len(t), dtype=np.float32)
    for i, f in enumerate(freqs):
        phase_offset = i * (2 * np.pi / max(len(freqs), 1))
        wave += (amp / len(freqs)) * np.sin(2 * np.pi * f * t + phase_offset)
    # Soft fade in/out for seamless looping
    fade = int(SAMPLE_RATE * 0.1)
    wave[:fade] *= np.linspace(0, 1, fade)
    wave[-fade:] *= np.linspace(1, 0, fade)
    return wave


class AudioManager:
    """
    Central audio manager.
    Synthesizes all sounds at startup and manages mixer channels.
    """

    MUSIC_CHANNEL = 0
    SFX_CHANNEL = 1
    AMBIENT_CHANNEL = 2

    # Biome music frequency sets (chords in Hz)
    BIOME_MUSIC = {
        "cyberpunk":   [110, 165, 220, 330],
        "volcano":     [82,  110, 165, 196],
        "ice_world":   [220, 330, 440, 660],
        "deep_space":  [55,  82,  110, 165],
        "jungle":      [196, 262, 330, 392],
        "ocean":       [165, 220, 330, 440],
        "desert":      [147, 196, 262, 330],
        "neon_digital":[440, 660, 880, 1100],
    }

    def __init__(self):
        self._sounds: dict = {}
        self._music_sounds: dict = {}
        self._volume_master: float = 1.0
        self._volume_music: float = 0.6
        self._volume_sfx: float = 0.8
        self._current_biome: str = ""
        self._music_channel: pygame.mixer.Channel = None
        self._sfx_channel: pygame.mixer.Channel = None
        self._ready = False

        # Build sounds in a background thread to avoid startup stall
        t = threading.Thread(target=self._synthesize_all, daemon=True)
        t.start()

    def _synthesize_all(self) -> None:
        """Generate all sounds procedurally."""
        try:
            self._sounds["flap"]      = _to_sound(_sweep(300, 600, 0.12, 0.5))
            self._sounds["hit"]       = _to_sound(_noise(0.25, 0.6))
            self._sounds["score"]     = _to_sound(_arpeggio([523, 659, 784], 0.06, 0.35))
            self._sounds["coin"]      = _to_sound(_arpeggio([784, 1047], 0.05, 0.3))
            self._sounds["powerup"]   = _to_sound(_arpeggio([523, 659, 784, 1047], 0.07, 0.35))
            self._sounds["click"]     = _to_sound(_sine(880, 0.04, 0.3))
            self._sounds["death"]     = _to_sound(np.concatenate([
                _sweep(400, 100, 0.4, 0.5), _noise(0.15, 0.2)
            ]))
            self._sounds["biome_transition"] = _to_sound(_sweep(200, 800, 0.5, 0.3))
            self._sounds["achievement"]      = _to_sound(_arpeggio(
                [523, 659, 784, 1047, 1319], 0.06, 0.3))

            # Build looping music for each biome
            for biome, freqs in self.BIOME_MUSIC.items():
                loop = _build_biome_loop(freqs, 2.0, 0.18)
                self._music_sounds[biome] = _to_sound(loop)

            self._ready = True
        except Exception as e:
            print(f"[Audio] Synthesis warning: {e}")
            self._ready = True   # Still mark ready; game will run silently

    # ── volume ───────────────────────────────────────────────────────────────
    def set_volumes(self, master: float, music: float, sfx: float) -> None:
        self._volume_master = master
        self._volume_music = music
        self._volume_sfx = sfx
        if self._music_channel:
            self._music_channel.set_volume(master * music)

    # ── SFX ──────────────────────────────────────────────────────────────────
    def play(self, name: str) -> None:
        if not self._ready:
            return
        sound = self._sounds.get(name)
        if sound is None:
            return
        try:
            ch = pygame.mixer.find_channel(True)
            if ch:
                ch.set_volume(self._volume_master * self._volume_sfx)
                ch.play(sound)
        except Exception:
            pass

    # ── Music ─────────────────────────────────────────────────────────────────
    def play_biome_music(self, biome_name: str) -> None:
        if not self._ready or biome_name == self._current_biome:
            return
        self._current_biome = biome_name
        sound = self._music_sounds.get(biome_name)
        if sound is None:
            return
        try:
            if self._music_channel is None:
                self._music_channel = pygame.mixer.Channel(self.MUSIC_CHANNEL)
            vol = self._volume_master * self._volume_music
            self._music_channel.set_volume(vol)
            self._music_channel.play(sound, loops=-1, fade_ms=800)
        except Exception:
            pass

    def stop_music(self, fade_ms: int = 500) -> None:
        if self._music_channel:
            try:
                self._music_channel.fadeout(fade_ms)
            except Exception:
                pass
        self._current_biome = ""
