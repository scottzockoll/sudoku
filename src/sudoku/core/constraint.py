from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sudoku.core.grid import Grid


class Constraint(ABC):
    @property
    @abstractmethod
    def constraint_type(self) -> str: ...

    @property
    @abstractmethod
    def cells(self) -> list[tuple[int, int]]: ...

    @abstractmethod
    def find_conflicts(self, grid: Grid) -> set[tuple[int, int]]:
        """Return positions within this constraint that are in conflict."""
        ...

    @abstractmethod
    def is_satisfied(self, grid: Grid) -> bool:
        """Return True if this constraint is fully satisfied."""
        ...


class CageConstraint(Constraint):
    def __init__(self, target_sum: int, cells: list[tuple[int, int]]) -> None:
        self.target_sum = target_sum
        self._cells = cells

    @property
    def constraint_type(self) -> str:
        return "cage"

    @property
    def cells(self) -> list[tuple[int, int]]:
        return self._cells

    def find_conflicts(self, grid: Grid) -> set[tuple[int, int]]:
        conflicts: set[tuple[int, int]] = set()

        # Check for duplicate values within cage
        seen: dict[int, list[tuple[int, int]]] = {}
        for row, col in self._cells:
            value = grid.get(row, col).value
            if value is not None:
                if value in seen:
                    conflicts.add((row, col))
                    for pos in seen[value]:
                        conflicts.add(pos)
                seen.setdefault(value, []).append((row, col))

        # Check for wrong sum when fully filled
        values: list[int] = []
        for row, col in self._cells:
            value = grid.get(row, col).value
            if value is None:
                break
            values.append(value)
        else:
            # All cells filled — check sum
            if sum(values) != self.target_sum:
                for row, col in self._cells:
                    conflicts.add((row, col))

        return conflicts

    def is_satisfied(self, grid: Grid) -> bool:
        values: list[int] = []
        for row, col in self._cells:
            value = grid.get(row, col).value
            if value is None:
                return False
            values.append(value)
        return len(values) == len(set(values)) and sum(values) == self.target_sum
