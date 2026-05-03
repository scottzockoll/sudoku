from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sudoku.core.game_state import GameState
    from sudoku.core.grid import Grid


class Validator:
    def find_conflicts(self, state: GameState) -> set[tuple[int, int]]:
        conflicts: set[tuple[int, int]] = set()
        grid = state.grid

        # Row conflicts
        for row in range(9):
            self._find_duplicates_in_group([(row, col) for col in range(9)], grid, conflicts)

        # Column conflicts
        for col in range(9):
            self._find_duplicates_in_group([(row, col) for row in range(9)], grid, conflicts)

        # Box conflicts
        for box_row in range(3):
            for box_col in range(3):
                positions = [(box_row * 3 + r, box_col * 3 + c) for r in range(3) for c in range(3)]
                self._find_duplicates_in_group(positions, grid, conflicts)

        # Constraint conflicts
        for constraint in state.constraints:
            conflicts.update(constraint.find_conflicts(grid))

        return conflicts

    @staticmethod
    def _find_duplicates_in_group(
        positions: list[tuple[int, int]],
        grid: Grid,
        conflicts: set[tuple[int, int]],
    ) -> None:
        seen: dict[int, list[tuple[int, int]]] = {}
        for row, col in positions:
            value = grid.get(row, col).value
            if value is not None:
                if value in seen:
                    conflicts.add((row, col))
                    for pos in seen[value]:
                        conflicts.add(pos)
                seen.setdefault(value, []).append((row, col))

    def update_conflicts(self, state: GameState) -> None:
        conflicts = self.find_conflicts(state)
        for row, col in state.grid.all_positions():
            state.grid.get(row, col).is_conflict = (row, col) in conflicts

    def check_win(self, state: GameState) -> bool:
        if not state.grid.is_complete:
            return False
        if self.find_conflicts(state):
            return False
        return all(constraint.is_satisfied(state.grid) for constraint in state.constraints)

    def get_same_digit_positions(self, state: GameState, digit: int) -> set[tuple[int, int]]:
        positions: set[tuple[int, int]] = set()
        for row, col in state.grid.all_positions():
            if state.grid.get(row, col).value == digit:
                positions.add((row, col))
        return positions

    def get_related_positions(self, row: int, col: int) -> set[tuple[int, int]]:
        positions: set[tuple[int, int]] = set()

        # Same row
        for c in range(9):
            if c != col:
                positions.add((row, c))

        # Same col
        for r in range(9):
            if r != row:
                positions.add((r, col))

        # Same box
        box_row, box_col = (row // 3) * 3, (col // 3) * 3
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if (r, c) != (row, col):
                    positions.add((r, c))

        return positions
