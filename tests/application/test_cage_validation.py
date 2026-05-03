import pytest

from sudoku.application.puzzle_loader import PuzzleLoader

BASE_PUZZLE: dict = {
    "id": "test",
    "difficulty": "easy",
    "grid": [[0] * 9 for _ in range(9)],
}


def _puzzle_with_cages(cages: list[dict]) -> dict:
    return {**BASE_PUZZLE, "constraints": cages}


class TestCageValidation:
    def test_valid_cage(self) -> None:
        loader = PuzzleLoader()
        data = _puzzle_with_cages([{"type": "cage", "sum": 10, "cells": [[0, 0], [0, 1]]}])
        state = loader.from_dict(data)
        assert len(state.constraints) == 1

    def test_cage_cell_out_of_bounds_row(self) -> None:
        loader = PuzzleLoader()
        data = _puzzle_with_cages([{"type": "cage", "sum": 10, "cells": [[9, 0], [0, 0]]}])
        with pytest.raises(ValueError, match="out of bounds"):
            loader.from_dict(data)

    def test_cage_cell_out_of_bounds_col(self) -> None:
        loader = PuzzleLoader()
        data = _puzzle_with_cages([{"type": "cage", "sum": 10, "cells": [[0, 9], [0, 0]]}])
        with pytest.raises(ValueError, match="out of bounds"):
            loader.from_dict(data)

    def test_cage_cell_negative(self) -> None:
        loader = PuzzleLoader()
        data = _puzzle_with_cages([{"type": "cage", "sum": 10, "cells": [[-1, 0], [0, 0]]}])
        with pytest.raises(ValueError, match="out of bounds"):
            loader.from_dict(data)

    def test_cage_sum_not_positive(self) -> None:
        loader = PuzzleLoader()
        data = _puzzle_with_cages([{"type": "cage", "sum": 0, "cells": [[0, 0], [0, 1]]}])
        with pytest.raises(ValueError, match="positive"):
            loader.from_dict(data)

    def test_cage_sum_negative(self) -> None:
        loader = PuzzleLoader()
        data = _puzzle_with_cages([{"type": "cage", "sum": -5, "cells": [[0, 0], [0, 1]]}])
        with pytest.raises(ValueError, match="positive"):
            loader.from_dict(data)

    def test_cage_duplicate_cells_within_cage(self) -> None:
        loader = PuzzleLoader()
        data = _puzzle_with_cages([{"type": "cage", "sum": 10, "cells": [[0, 0], [0, 0]]}])
        with pytest.raises(ValueError, match="[Dd]uplicate"):
            loader.from_dict(data)

    def test_cage_duplicate_cells_across_cages(self) -> None:
        loader = PuzzleLoader()
        data = _puzzle_with_cages(
            [
                {"type": "cage", "sum": 10, "cells": [[0, 0], [0, 1]]},
                {"type": "cage", "sum": 5, "cells": [[0, 1], [0, 2]]},
            ]
        )
        with pytest.raises(ValueError, match="[Dd]uplicate"):
            loader.from_dict(data)

    def test_cage_empty_cells(self) -> None:
        loader = PuzzleLoader()
        data = _puzzle_with_cages([{"type": "cage", "sum": 10, "cells": []}])
        with pytest.raises(ValueError, match="at least"):
            loader.from_dict(data)

    def test_cage_single_cell(self) -> None:
        loader = PuzzleLoader()
        data = _puzzle_with_cages([{"type": "cage", "sum": 5, "cells": [[0, 0]]}])
        # Single-cell cages are valid (the digit must equal the sum)
        state = loader.from_dict(data)
        assert len(state.constraints) == 1

    def test_multiple_valid_cages(self) -> None:
        loader = PuzzleLoader()
        data = _puzzle_with_cages(
            [
                {"type": "cage", "sum": 10, "cells": [[0, 0], [0, 1]]},
                {"type": "cage", "sum": 15, "cells": [[1, 0], [1, 1], [1, 2]]},
            ]
        )
        state = loader.from_dict(data)
        assert len(state.constraints) == 2
