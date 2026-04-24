"""
Project structure checker.
Run:  python check.py
Verifies all folders, files, and imports work correctly.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 55)
print("  AI Maze Adventure — Project Structure Check")
print("=" * 55)
print()

all_good = True

# Check folders and __init__.py
folders = ['config', 'engine', 'maze', 'maze_ai', 'puzzle', 'ui', 'integration']
print("📁 Checking folders...\n")

for folder in folders:
    path = os.path.join(os.path.dirname(__file__), folder)
    init_path = os.path.join(path, '__init__.py')
    exists = os.path.isdir(path)
    has_init = os.path.isfile(init_path)

    if exists and has_init:
        print(f"  ✅ {folder}/")
        print(f"     ✅ __init__.py")
    elif exists and not has_init:
        print(f"  ✅ {folder}/")
        print(f"     ❌ __init__.py  MISSING!")
        print(f"        Fix: Create empty file  {folder}/__init__.py")
        all_good = False
    else:
        print(f"  ❌ {folder}/  FOLDER MISSING!")
        print(f"        Fix: Create folder  {folder}/")
        print(f"        Fix: Create empty file  {folder}/__init__.py")
        all_good = False
    print()

# Check all required files
files = [
    'main.py',
    'check.py',
    'config/settings.py',
    'engine/raycaster.py',
    'engine/renderer_3d.py',
    'maze/maze_generator.py',
    'maze/player.py',
    'maze_ai/pathfinder.py',
    'puzzle/config.py',
    'puzzle/models.py',
    'puzzle/solver.py',
    'puzzle/renderer.py',
    'puzzle/puzzle.py',
    'ui/hud.py',
    'ui/minimap.py',
    'ui/transitions.py',
    'integration/game_manager.py',
]

print("📄 Checking files...\n")
for f in files:
    path = os.path.join(os.path.dirname(__file__), f)
    if os.path.isfile(path):
        print(f"  ✅ {f}")
    else:
        print(f"  ❌ {f}  MISSING!")
        all_good = False

print()

# Check imports
if all_good:
    print("📦 Checking imports...\n")

    imports = [
        ("config.settings", "from config.settings import Colors, Screen, Raycasting"),
        ("engine.raycaster", "from engine.raycaster import Raycaster"),
        ("engine.renderer_3d", "from engine.renderer_3d import Renderer3D"),
        ("maze.maze_generator", "from maze.maze_generator import MazeGenerator"),
        ("maze.player", "from maze.player import Player"),
        ("maze_ai.pathfinder", "from maze_ai.pathfinder import MazePathfinder"),
        ("puzzle.config", "from puzzle.config import Colors as PColors"),
        ("puzzle.models", "from puzzle.models import Tile, PuzzleState"),
        ("puzzle.solver", "from puzzle.solver import solve, get_hint"),
        ("ui.hud", "from ui.hud import HUD"),
        ("ui.minimap", "from ui.minimap import Minimap"),
        ("ui.transitions", "from ui.transitions import TransitionManager"),
    ]

    for name, cmd in imports:
        try:
            exec(cmd)
            print(f"  ✅ {name}")
        except Exception as e:
            print(f"  ❌ {name}")
            print(f"     Error: {e}")
            all_good = False

    # Special check for puzzle renderer (needs pygame)
    try:
        import pygame
        pygame.init()
        screen = pygame.display.set_mode((100, 100))
        from puzzle.renderer import Renderer
        print(f"  ✅ puzzle.renderer")
        from puzzle.puzzle import NPuzzle
        print(f"  ✅ puzzle.puzzle")
        pygame.quit()
    except Exception as e:
        print(f"  ❌ puzzle.renderer or puzzle.puzzle")
        print(f"     Error: {e}")
        all_good = False

    # Final integration check
    try:
        import pygame
        pygame.init()
        screen = pygame.display.set_mode((100, 100))
        from integration.game_manager import GameManager
        print(f"  ✅ integration.game_manager")
        pygame.quit()
    except Exception as e:
        print(f"  ❌ integration.game_manager")
        print(f"     Error: {e}")
        all_good = False

print()
print("=" * 55)
if all_good:
    print("  🎉 Everything looks great!")
    print("  Run:  python main.py")
else:
    print("  ⚠️  Fix the issues above, then run check again.")
    print("  Run:  python check.py")
print("=" * 55)