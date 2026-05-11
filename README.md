# SkyDrift 🎮

A production-quality **Flappy Bird inspired game** built with Python 3 + Pygame, featuring modern visuals, 8 procedurally-rendered biomes, particle effects, power-ups, achievements, and persistent leaderboards.

---

## Features

| Feature | Details |
|---------|---------|
| **8 Biomes** | Cyberpunk City, Lava Volcano, Ice World, Deep Space, Jungle Ruins, Ocean Depths, Desert Storm, Neon Digital |
| **Procedural Graphics** | All art drawn via `pygame.draw` — no external assets needed |
| **Procedural Audio** | All sounds synthesized via `numpy` at startup |
| **Particle System** | Trail, explosion, rain, snow, lava sparks, bubbles, neon glow |
| **Power-ups** | Shield, Slow-Motion, Magnet |
| **Combo Scoring** | Multiplier system up to 5× |
| **Achievements** | 12 achievements with persistent tracking |
| **Leaderboard** | Top-10 JSON leaderboard with player name + date |
| **Daily Challenge** | Seed-based daily objectives |
| **Skin System** | 6 bird skins (unlock by score milestones) |
| **Weather Effects** | Rain + lightning, snow, sandstorm, fog layers |
| **Transitions** | Fade, chromatic aberration, pixel dissolve |
| **Camera Shake** | On death and biome change |
| **Screenshot Mode** | F12 saves PNG to `/screenshots/` |

---

## Quick Start

```bash
# 1. Clone / download the project
git clone https://github.com/Punith-2008/Skydrift.git
cd Skydrift

# 2. Install dependencies
pip install pygame numpy

# 3. Run the game
python main.py
```

---

## Controls

| Key / Action | Effect |
|---|---|
| `SPACE` or `Left Click` | Flap / jump |
| `ESC` | Pause |
| `F12` | Screenshot |

---

## File Structure

```
SkyDrift/
├── main.py                     ← Entry point
├── requirements.txt
├── README.md
├── assets/
│   └── data/                   ← settings.json, leaderboard.json, achievements.json
├── screenshots/                ← F12 screenshots saved here
└── src/
    ├── engine/
    │   ├── game.py             ← State machine + main loop
    │   ├── audio.py            ← Procedural synthesis
    │   ├── camera.py           ← Shake effects
    │   ├── renderer.py         ← Glow, glass panels, fonts
    │   └── settings.py         ← JSON config
    ├── biomes/                 ← 8 unique biome classes
    ├── entities/               ← Bird, Pipe, Coin, PowerUp
    ├── effects/                ← Particles, Weather, Transitions
    ├── systems/                ← Scoring, Achievements, Leaderboard, Challenge
    └── ui/                     ← Menu, HUD, Pause, GameOver, Settings, Leaderboard
```

---

## Biome Progression

A new biome activates every **15 pipes** passed. The sequence cycles through all 8 biomes:

1. 🌆 Cyberpunk City → rain, neon buildings
2. 🌋 Lava Volcano → lava rivers, ash fog
3. ❄️ Ice World → aurora borealis, snow
4. 🌌 Deep Space → nebulas, planets
5. 🌿 Jungle Ruins → temples, vines, fireflies
6. 🌊 Ocean Depths → coral, fish schools, caustics
7. 🏜️ Desert Storm → pyramids, sandstorm, mirages
8. 💻 Neon Digital → data streams, hexagons, glowing grid

---

## Skin Unlocks

| Skin | Requirement |
|---|---|
| Classic | Always available |
| Cyber | Score 50 |
| Lava | Score 100 |
| Neon | Score 200 |
| Ghost | Score 300 |
| Cosmic | Score 500 |

---

## Requirements

- Python 3.8+
- `pygame >= 2.1.0`
- `numpy >= 1.21.0`
