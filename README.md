# SkyDrift 🎮

A production-quality **Flappy Bird inspired game** built with Python 3 + Pygame, featuring modern visuals, 7 procedurally-rendered biomes, particle effects, power-ups, achievements, and persistent leaderboards.

---

## Features

| Feature | Details |
|---------|---------|
| **7 Biomes** | Lava Volcano, Ice World, Deep Space, Jungle Ruins, Ocean Depths, Desert Storm, Neon Digital |
| **Procedural Graphics** | All art drawn via `pygame.draw` — no external assets needed |
| **Procedural Audio** | All sounds synthesized via `numpy` at startup |
| **Particle System** | Trail, explosion, rain, snow, lava sparks, bubbles, neon glow |
| **Power-ups** | Shield, Slow-Motion, Magnet |
| **Combo Scoring** | Multiplier system up to 5× |
| **Achievements** | 12 achievements with persistent tracking |
| **Leaderboard** | Top-10 JSON leaderboard with player name + date |
| **Daily Challenge** | Seed-based daily objectives |
| **Skin System** | 6 bird skins (all available by default) |
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

A new biome activates every **15 pipes** passed. The sequence cycles through all 7 biomes:

1. 🌋 Lava Volcano → lava rivers, ash fog
2. ❄️ Ice World → aurora borealis, snow
3. 🌌 Deep Space → nebulas, planets
4. 🌿 Jungle Ruins → temples, vines, fireflies
5. 🌊 Ocean Depths → coral, fish schools, caustics
6. 🏜️ Desert Storm → pyramids, sandstorm, mirages
7. 💻 Neon Digital → data streams, hexagons, glowing grid

---

## Skins

All 6 skins are unlocked and available by default from the settings menu:

- **Classic**
- **Cyber**
- **Lava**
- **Neon**
- **Ghost**
- **Cosmic**

---

## Requirements

- Python 3.8+
- `pygame >= 2.1.0`
- `numpy >= 1.21.0`
