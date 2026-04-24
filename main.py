"""
AI Maze Adventure — Main Entry Point
Run:  python main.py
"""

from integration.game_manager import GameManager


def main():
    game = GameManager()
    game.run()


if __name__ == "__main__":
    main()
    