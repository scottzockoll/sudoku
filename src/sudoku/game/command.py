from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from sudoku.core.cell import CellSnapshot
from sudoku.core.grid import Grid


@dataclass(frozen=True)
class Command:
    row: int
    col: int
    before: CellSnapshot
    after: CellSnapshot


class UndoRedoStack:
    def __init__(self) -> None:
        self._undo: list[Command] = []
        self._redo: list[Command] = []

    @property
    def can_undo(self) -> bool:
        return len(self._undo) > 0

    @property
    def can_redo(self) -> bool:
        return len(self._redo) > 0

    def execute(
        self,
        grid: Grid,
        row: int,
        col: int,
        mutate_fn: Callable[[Grid, int, int], None],
    ) -> None:
        cell = grid.get(row, col)
        before = cell.snapshot()
        mutate_fn(grid, row, col)
        after = cell.snapshot()
        if before != after:
            self._undo.append(Command(row, col, before, after))
            self._redo.clear()

    def undo(self, grid: Grid) -> bool:
        if not self._undo:
            return False
        cmd = self._undo.pop()
        grid.get(cmd.row, cmd.col).restore(cmd.before)
        self._redo.append(cmd)
        return True

    def redo(self, grid: Grid) -> bool:
        if not self._redo:
            return False
        cmd = self._redo.pop()
        grid.get(cmd.row, cmd.col).restore(cmd.after)
        self._undo.append(cmd)
        return True
