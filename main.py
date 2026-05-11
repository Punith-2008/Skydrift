"""
SkyDrift — Flappy Bird Inspired Game
=====================================
A production-quality Flappy Bird game with modern visuals,
8 biomes, particles, power-ups, achievements, and persistent leaderboard.

Run:
    python main.py

Requirements:
    pip install pygame numpy
"""

import sys
import os

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame

def main():
    pygame.init()
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.mixer.init()

    from src.engine.game import Game
    game = Game()
    game.run()

    pygame.mixer.quit()
    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
