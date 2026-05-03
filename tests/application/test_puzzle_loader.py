import json
from pathlib import Path

import pytest

from sudoku.application.puzzle_loader import PuzzleLoader
from sudoku.core.constraint import CageConstraint

VALID_PUZZLE = {
    "id": "test_001",
    "difficulty": "easy",
    "grid": [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ],
}

VALID_KILLER_PUZZLE = {
    "id": "killer_001",
    "difficulty": "hard",
    "grid": [[0] * 9 for _ in range(9)],
    "constraints": [
        {"type": "cage", "sum": 15, "cells": [[0, 0], [0, 1], [1, 0]]},
        {"type": "cage", "sum": 10, "cells": [[0, 2], [0, 3]]},
    ],
}


class TestPuzzleLoaderFromDict:
    def test_load_standard_puzzle(self) -> None:
        loader = PuzzleLoader()
        state = loader.from_dict(VALID_PUZZLE)
        assert state.grid.get(0, 0).value == 5
        assert state.grid.get(0, 0).is_given
        assert state.grid.get(0, 2).is_empty
        assert not state.grid.get(0, 2).is_given
        assert state.constraints == []

    def test_load_killer_puzzle(self) -> None:
        loader = PuzzleLoader()
        state = loader.from_dict(VALID_KILLER_PUZZLE)
        assert len(state.constraints) == 2
        cage = state.constraints[0]
        assert isinstance(cage, CageConstraint)
        assert cage.target_sum == 15
        assert cage.cells == [(0, 0), (0, 1), (1, 0)]

    def test_missing_grid(self) -> None:
        loader = PuzzleLoader()
        with pytest.raises(ValueError, match="missing 'grid'"):
            loader.from_dict({"id": "bad"})

    def test_wrong_row_count(self) -> None:
        loader = PuzzleLoader()
        data = {**VALID_PUZZLE, "grid": [[0] * 9 for _ in range(8)]}
        with pytest.raises(ValueError, match="9 rows"):
            loader.from_dict(data)

    def test_wrong_col_count(self) -> None:
        loader = PuzzleLoader()
        grid = [[0] * 9 for _ in range(9)]
        grid[0] = [0] * 8
        data = {**VALID_PUZZLE, "grid": grid}
        with pytest.raises(ValueError, match="9 columns"):
            loader.from_dict(data)

    def test_value_out_of_range(self) -> None:
        loader = PuzzleLoader()
        grid = [[0] * 9 for _ in range(9)]
        grid[0][0] = 10
        data = {**VALID_PUZZLE, "grid": grid}
        with pytest.raises(ValueError, match="0-9"):
            loader.from_dict(data)

    def test_negative_value(self) -> None:
        loader = PuzzleLoader()
        grid = [[0] * 9 for _ in range(9)]
        grid[0][0] = -1
        data = {**VALID_PUZZLE, "grid": grid}
        with pytest.raises(ValueError, match="0-9"):
            loader.from_dict(data)

    def test_unknown_constraint_type(self) -> None:
        loader = PuzzleLoader()
        data = {
            **VALID_PUZZLE,
            "constraints": [{"type": "unknown", "cells": [[0, 0]]}],
        }
        with pytest.raises(ValueError, match="Unknown constraint type"):
            loader.from_dict(data)

    def test_no_constraints_field_defaults_empty(self) -> None:
        loader = PuzzleLoader()
        state = loader.from_dict(VALID_PUZZLE)
        assert state.constraints == []


class TestPuzzleLoaderFromFile:
    def test_load_from_json_file(self, tmp_path: Path) -> None:
        path = tmp_path / "test.json"
        path.write_text(json.dumps(VALID_PUZZLE))
        loader = PuzzleLoader()
        state = loader.from_file(path)
        assert state.grid.get(0, 0).value == 5

    def test_file_not_found(self) -> None:
        loader = PuzzleLoader()
        with pytest.raises(FileNotFoundError):
            loader.from_file(Path("/nonexistent/puzzle.json"))
