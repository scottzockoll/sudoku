import pytest

from sudoku.application.puzzle_loader import PuzzleLoader

BASE_PUZZLE: dict = {
    "id": "test",
    "difficulty": "easy",
    "grid": [[0] * 9 for _ in range(9)],
}


def _puzzle_with_cages(cages: list[dict]) -> dict:
    return {**BASE_PUZZLE, "constraints": cages}


class TestCageAdjacency:
    def test_adjacent_horizontal(self) -> None:
        loader = PuzzleLoader()
        data = _puzzle_with_cages([{"type": "cage", "sum": 10, "cells": [[0, 0], [0, 1]]}])
        state = loader.from_dict(data)
        assert len(state.constraints) == 1

    def test_adjacent_vertical(self) -> None:
        loader = PuzzleLoader()
        data = _puzzle_with_cages([{"type": "cage", "sum": 10, "cells": [[0, 0], [1, 0]]}])
        state = loader.from_dict(data)
        assert len(state.constraints) == 1

    def test_adjacent_l_shape(self) -> None:
        loader = PuzzleLoader()
        data = _puzzle_with_cages([{"type": "cage", "sum": 15, "cells": [[0, 0], [0, 1], [1, 0]]}])
        state = loader.from_dict(data)
        assert len(state.constraints) == 1

    def test_adjacent_square(self) -> None:
        loader = PuzzleLoader()
        data = _puzzle_with_cages(
            [{"type": "cage", "sum": 20, "cells": [[0, 0], [0, 1], [1, 0], [1, 1]]}]
        )
        state = loader.from_dict(data)
        assert len(state.constraints) == 1

    def test_non_adjacent_diagonal(self) -> None:
        loader = PuzzleLoader()
        data = _puzzle_with_cages([{"type": "cage", "sum": 10, "cells": [[0, 0], [1, 1]]}])
        with pytest.raises(ValueError, match="[Cc]onnected|[Aa]djacent"):
            loader.from_dict(data)

    def test_non_adjacent_gap(self) -> None:
        loader = PuzzleLoader()
        data = _puzzle_with_cages([{"type": "cage", "sum": 10, "cells": [[0, 0], [0, 2]]}])
        with pytest.raises(ValueError, match="[Cc]onnected|[Aa]djacent"):
            loader.from_dict(data)

    def test_non_adjacent_split_group(self) -> None:
        loader = PuzzleLoader()
        # Two disconnected groups: (0,0)-(0,1) and (2,2)-(2,3)
        data = _puzzle_with_cages(
            [{"type": "cage", "sum": 20, "cells": [[0, 0], [0, 1], [2, 2], [2, 3]]}]
        )
        with pytest.raises(ValueError, match="[Cc]onnected|[Aa]djacent"):
            loader.from_dict(data)

    def test_single_cell_is_connected(self) -> None:
        loader = PuzzleLoader()
        data = _puzzle_with_cages([{"type": "cage", "sum": 5, "cells": [[4, 4]]}])
        state = loader.from_dict(data)
        assert len(state.constraints) == 1

    def test_long_snake(self) -> None:
        loader = PuzzleLoader()
        # Snake: (0,0)-(0,1)-(0,2)-(1,2)-(1,1)
        data = _puzzle_with_cages(
            [{"type": "cage", "sum": 25, "cells": [[0, 0], [0, 1], [0, 2], [1, 2], [1, 1]]}]
        )
        state = loader.from_dict(data)
        assert len(state.constraints) == 1
