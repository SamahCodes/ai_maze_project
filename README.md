# ai_maze_project# 🧠 AI-Assisted Maze Navigation with N-Puzzle Challenge

## 📌 Overview

This project is an interactive game that combines **maze navigation**, **artificial intelligence**, and **puzzle solving** into a single experience.

The player explores a maze from a limited perspective and encounters decision points (intersections). At these points, the player can request help from an AI system — but only after solving an **N-Puzzle (3×3)** challenge.

---

## 🎯 Features

### 🧩 Maze System

* Grid-based maze
* Player movement with collision detection
* Intersection detection (decision points)
* Limited visibility (not top-view)

### 🤖 Maze AI (Pathfinding)

* Uses **BFS or A*** algorithm
* Computes shortest path
* Reveals **only the correct direction at intersections** (not the full path)

### 🧠 Puzzle System (N-Puzzle)

* 3×3 sliding puzzle
* Tile movement system
* Win condition detection
* Move counter (optional)

### ⚡ Puzzle AI (Solver)

* Uses **A*** algorithm
* Manhattan Distance heuristic
* Can provide:

  * Next optimal move (Hint)
  * Step-by-step assistance

### 🎨 GUI (Pygame)

* Interactive game window
* Separate screens:

  * Maze Screen
  * Puzzle Screen
* Modern UI with styled tiles and smooth interactions

---

## 🏗️ Project Structure

```
AI_Maze_Project/
│
├── main.py
│
├── maze/
│   ├── maze.py
│   ├── player.py
│
├── maze_ai/
│   ├── pathfinder.py
│
├── puzzle/
│   ├── puzzle_game.py
│   ├── puzzle_solver.py
│   ├── main_puzzle.py
│
├── puzzle_ai/
│   ├── puzzle_solver.py
│
└── README.md
```

---

## ⚙️ Technologies Used

* **Python 3**
* **Pygame** (for GUI and game rendering)
* **Algorithms:**

  * Breadth-First Search (BFS)
  * A* Search
  * Manhattan Distance Heuristic

---

## 🚀 Installation

### 1. Clone the repository

```
git clone https://github.com/your-username/ai-maze-project.git
cd ai-maze-project
```

### 2. Install dependencies

```
pip install pygame
```

---

## ▶️ Running the Project

### Run Puzzle Module

```
cd puzzle
python main_puzzle.py
```

### Run Full Game (when integrated)

```
python main.py
```

---

## 🎮 Controls

### Maze

* Arrow Keys → Move player
* Key (e.g. H) → Request AI help

### Puzzle

* Arrow Keys → Move tiles
* H → Get hint from AI

---

## 🧠 How It Works

1. Player navigates the maze
2. At an intersection → player can request AI help
3. Puzzle screen appears
4. Player solves the N-Puzzle
5. AI reveals the correct direction
6. Player continues toward the goal

---

## ✨ Unique Idea

* AI does **not** reveal the full solution
* Player must **earn guidance**
* Dual AI system:

  * Maze AI (navigation)
  * Puzzle AI (solver & hints)

---

## 📈 Future Improvements

* 3D visualization (ray casting)
* Dynamic maze generation
* Difficulty levels
* Timer and scoring system
* Sound effects and animations

---

## 👥 Team Roles

*Sahar Reda Helmy  **Maze System & Movement**
*Sahar Osama Elseed **Maze AI (Pathfinding)**
*Samah Mohamed Salah **Puzzle System + Puzzle AI**

---

## 📜 License

This project is for educational purposes.

---

## 💡 Author Notes

This project demonstrates how AI algorithms can be integrated into interactive systems to enhance problem-solving and user engagement.

---
