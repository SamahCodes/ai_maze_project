"""
Standalone demo runner.
Run:  python demo.py
"""

from puzzle import NPuzzle


def main():
    def on_solve(moves):
        print(f"🎉 Puzzle solved in {moves} moves!")

    def on_reset():
        print("🔄 New puzzle generated!")

    def on_move(value):
        print(f"   Moved tile {value}")

    game = NPuzzle(standalone=True)
    game.set_callback("on_solve", on_solve)
    game.set_callback("on_reset", on_reset)
    game.set_callback("on_move", on_move)
    game.run()


if __name__ == "__main__":
    main()