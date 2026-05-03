import sys
from pathlib import Path

from sudoku.application.app import App


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = [a for a in sys.argv[1:] if a.startswith("--")]

    puzzle_path = Path(args[0]) if args else None
    debug = "--debug" in flags

    app = App(puzzle_path=puzzle_path, debug=debug)
    app.run()


if __name__ == "__main__":
    main()
