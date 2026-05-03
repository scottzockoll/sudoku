from __future__ import annotations

from enum import Enum, auto

from sudoku.core.constraint import Constraint
from sudoku.core.cursor import Cursor
from sudoku.core.grid import Grid


class InputMode(Enum):
    NORMAL = auto()
    NOTES = auto()
    COLOR = auto()


class GameState:
    def __init__(
        self,
        grid: Grid,
        constraints: list[Constraint] | None = None,
    ) -> None:
        self.grid = grid
        self.cursor = Cursor()
        self.selected = False
        self.input_mode = InputMode.NORMAL
        self.active_color: int = 1  # 1-9, the currently selected color in color mode
        self.is_won = False
        self.constraints: list[Constraint] = constraints if constraints is not None else []
        self.dirty = True

    def mark_dirty(self) -> None:
        self.dirty = True

    def clear_dirty(self) -> None:
        self.dirty = False

    def toggle_input_mode(self) -> None:
        if self.input_mode == InputMode.NORMAL:
            self.input_mode = InputMode.NOTES
        else:
            self.input_mode = InputMode.NORMAL
        self.mark_dirty()

    def toggle_color_mode(self) -> None:
        if self.input_mode == InputMode.COLOR:
            self.input_mode = InputMode.NORMAL
        else:
            self.input_mode = InputMode.COLOR
        self.mark_dirty()

    def select(self) -> None:
        self.selected = True
        self.mark_dirty()

    def deselect(self) -> None:
        self.selected = False
        self.mark_dirty()

    def move_cursor(self, dr: int, dc: int) -> None:
        self.cursor.move(dr, dc)
        self.selected = True
        self.mark_dirty()
