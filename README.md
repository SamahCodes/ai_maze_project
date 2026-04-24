# 🧠 AI-Assisted 3D Maze Game with N-Puzzle Challenge

## 📌 Overview

This project is a fully interactive **first-person 3D maze game** built using Python and Pygame.
It combines **real-time rendering**, **AI pathfinding**, and **puzzle-solving mechanics** to create an engaging and intelligent gameplay experience.

Unlike traditional maze games, the player cannot see the full maze. Instead, they explore it from a **first-person perspective**, making decisions based on limited visibility and strategic thinking.

To receive help from the AI, the player must solve a **sliding tile puzzle (N-Puzzle)**, creating a unique interaction between gameplay and problem-solving.

---

## 🎮 Core Features

### 🧱 3D Maze Rendering

* First-person perspective using **raycasting** (similar to early 3D games like Wolfenstein)
* Real-time rendering of walls and corridors
* Depth simulation and immersive navigation

---

### 🎮 Player System

* Movement using **WASD / Arrow keys**
* Collision detection (cannot pass through walls)
* Real-time camera updates

---

### 🗺️ Smart Minimap

* Displays a top-down representation of explored areas
* Implements **fog-of-war** (only visited locations are visible)

---

### 🤖 AI Pathfinding System

* Uses **A*** algorithm to compute the optimal path
* Does NOT reveal the full path
* Only provides the **next correct direction at intersections**

---

### 🧩 Puzzle System (N-Puzzle)

* 3×3 sliding tile puzzle
* Triggered when requesting AI help
* Must be solved to unlock AI guidance
* Includes move logic and validation

---

### 💡 Intelligent Hint System

* After solving the puzzle:

  * AI calculates the best path
  * Highlights the correct direction relative to the player
  * Uses visual cues (e.g., golden light in 3D view)

---

### 🏆 Goal System

* A goal object (trophy) is placed in the maze
* Becomes visible when the player is near
* Reaching it triggers a **victory screen**

---
🎥 Demo Video

📺 Watch the project in action:

🔗 Demo / Presentation Video:
Click here to watch
---

## 🏗️ Project Structure

```plaintext
AI_Maze_Project/
│
├── main.py                         # Entry point
├── check.py                        # Debug & diagnostics
│
├── config/
│   └── settings.py                 # Global configuration
│
├── engine/
│   ├── raycaster.py                # Raycasting logic
│   └── renderer_3d.py              # 3D rendering engine
│
├── maze/
│   ├── maze_generator.py           # Maze generation (recursive backtracking)
│   └── player.py                   # Player movement & controls
│
├── maze_ai/
│   └── pathfinder.py               # A* pathfinding algorithm
│
├── puzzle/
│   ├── config.py                   # Puzzle settings
│   ├── models.py                   # Puzzle data model
│   ├── solver.py                   # A* puzzle solver
│   ├── renderer.py                 # Puzzle UI rendering
│   └── puzzle.py                   # Puzzle controller logic
│
├── ui/
│   ├── hud.py                      # Heads-up display (AI hints, messages)
│   ├── minimap.py                  # Fog-of-war minimap
│   └── transitions.py              # Screen transitions
│
├── integration/
│   └── game_manager.py             # Core game flow & module integration
│
└── README.md
```

---

## ⚙️ Technologies Used

* **Python 3**
* **Pygame** (for rendering and interaction)
* **Algorithms:**

  * A* (Pathfinding)
  * Recursive Backtracking (Maze generation)
  * Manhattan Distance (Heuristic)

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ai-maze-project.git
cd ai-maze-project
```

### 2. Install dependencies

```bash
pip install pygame
```

---

## ▶️ Running the Game

```bash
python main.py
```

---

## 🎮 Controls

| Action          | Key              |
| --------------- | ---------------- |
| Move Forward    | W / ↑            |
| Move Backward   | S / ↓            |
| Turn Left       | A / ←            |
| Turn Right      | D / →            |
| Request AI Help | (Defined in HUD) |

---

## 🔄 Gameplay Flow

1. A random maze is generated
2. Player spawns inside the maze (first-person view)
3. Player explores using movement controls
4. When reaching an intersection:

   * Player can request AI help
5. Puzzle screen opens
6. Player solves the N-Puzzle
7. AI computes shortest path using A*
8. AI reveals ONLY the correct direction
9. Player continues navigation
10. Goal is reached → Victory screen

---

## 🧠 How It Works

### Maze Generation

* Uses **recursive backtracking**
* Produces a solvable maze with unique paths

### Raycasting Engine

* Simulates 3D by casting rays from the player’s view
* Calculates wall distances and renders vertical slices

### AI Pathfinding

* A* algorithm computes optimal route
* Heuristic: Manhattan Distance

### Puzzle Solver

* Uses A* to determine optimal moves
* Can be extended for hint generation

---

## ✨ Design Philosophy

* The player should **not see everything**
* AI assistance must be **earned, not given**
* The experience should feel like a **real game, not a demo**
* Balance between **challenge and guidance**

---

## 📈 Future Improvements

* Full 3D engine (OpenGL / Unity-style rendering)
* Dynamic maze difficulty
* Sound effects and background music
* Save/load system
* Advanced AI hints (adaptive difficulty)

---

## 👥 Team Roles 

* Maze & Rendering System
* AI Pathfinding
* Puzzle System & Solver

---

## 📜 License

This project is for educational purposes.

---

## 💡 Notes

This project demonstrates how classical AI algorithms can be integrated into interactive systems to enhance gameplay, decision-making, and user engagement.

---
