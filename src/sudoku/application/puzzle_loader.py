from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sudoku.core.constraint import CageConstraint, Constraint
from sudoku.core.game_state import GameState
from sudoku.core.grid import Grid


class PuzzleLoader:
    def from_file(self, path: Path) -> GameState:
        with path.open() as f:
            data = json.load(f)
        return self.from_dict(data)

    def from_dict(self, data: dict[str, Any]) -> GameState:
        if "grid" not in data:
            raise ValueError("Puzzle data missing 'grid'")

        raw_grid = data["grid"]
        self._validate_grid(raw_grid)

        grid = Grid.from_raw(raw_grid)
        constraints = self._parse_constraints(data.get("constraints", []))

        return GameState(grid=grid, constraints=constraints)

    @staticmethod
    def _validate_grid(raw: list[list[int]]) -> None:
        if len(raw) != 9:
            raise ValueError(f"Grid must have 9 rows, got {len(raw)}")
        for i, row in enumerate(raw):
            if len(row) != 9:
                raise ValueError(f"Row {i} must have 9 columns, got {len(row)}")
            for value in row:
                if value < 0 or value > 9:
                    raise ValueError(f"Cell values must be 0-9, got {value}")

    @staticmethod
    def _parse_constraints(raw: list[dict[str, Any]]) -> list[Constraint]:
        constraints: list[Constraint] = []
        all_cage_cells: set[tuple[int, int]] = set()

        for entry in raw:
            constraint_type = entry.get("type", "")
            if constraint_type == "cage":
                cells = [(r, c) for r, c in entry["cells"]]
                target_sum = entry["sum"]
                PuzzleLoader._validate_cage(cells, target_sum, all_cage_cells)
                constraints.append(CageConstraint(target_sum=target_sum, cells=cells))
            else:
                raise ValueError(f"Unknown constraint type: {constraint_type!r}")

        return constraints

    @staticmethod
    def _validate_cage(
        cells: list[tuple[int, int]],
        target_sum: int,
        all_cage_cells: set[tuple[int, int]],
    ) -> None:
        if len(cells) < 1:
            raise ValueError("Cage must have at least 1 cell")

        if target_sum <= 0:
            raise ValueError(f"Cage sum must be positive, got {target_sum}")

        seen: set[tuple[int, int]] = set()
        for row, col in cells:
            if row < 0 or row > 8 or col < 0 or col > 8:
                raise ValueError(f"Cage cell ({row}, {col}) out of bounds")
            if (row, col) in seen:
                raise ValueError(f"Duplicate cell ({row}, {col}) within cage")
            if (row, col) in all_cage_cells:
                raise ValueError(f"Duplicate cell ({row}, {col}) across cages")
            seen.add((row, col))

        all_cage_cells.update(seen)

        if len(cells) > 1:
            PuzzleLoader._validate_cage_connected(cells)

    @staticmethod
    def _validate_cage_connected(cells: list[tuple[int, int]]) -> None:
        cell_set = set(cells)
        visited: set[tuple[int, int]] = set()
        queue = [cells[0]]
        visited.add(cells[0])

        while queue:
            row, col = queue.pop()
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                neighbor = (row + dr, col + dc)
                if neighbor in cell_set and neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        if len(visited) != len(cell_set):
            raise ValueError("Cage cells must be orthogonally connected/adjacent")
