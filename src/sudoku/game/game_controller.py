from __future__ import annotations

from sudoku.core.game_state import GameState, InputMode
from sudoku.core.validator import Validator
from sudoku.game.actions import Action
from sudoku.game.command import UndoRedoStack


class GameController:
    def __init__(self, state: GameState) -> None:
        self._state = state
        self._undo_redo = UndoRedoStack()
        self._validator = Validator()

    def handle(self, action: Action) -> None:
        if self._state.is_won and action not in (Action.QUIT, Action.ESCAPE):
            return

        if action in _MOVE_DELTAS:
            dr, dc = _MOVE_DELTAS[action]
            self._state.move_cursor(dr, dc)
        elif action == Action.ESCAPE:
            if self._state.input_mode == InputMode.COLOR:
                self._state.toggle_color_mode()
            else:
                self._state.deselect()
        elif action == Action.TOGGLE_NOTES:
            self._state.toggle_input_mode()
        elif action == Action.TOGGLE_COLOR_MODE:
            self._state.toggle_color_mode()
        elif action == Action.UNDO:
            self._handle_undo()
        elif action == Action.REDO:
            self._handle_redo()
        elif action == Action.DELETE:
            self._handle_delete()
        elif action == Action.APPLY_COLOR:
            self._handle_apply_color()
        else:
            digit = action.digit_value()
            if digit is not None:
                self._handle_digit(digit)

    def _handle_digit(self, digit: int) -> None:
        if not self._state.selected:
            return

        # In color mode, digits select the active color
        if self._state.input_mode == InputMode.COLOR:
            self._state.active_color = digit
            self._state.mark_dirty()
            return

        row, col = self._state.cursor.position
        cell = self._state.grid.get(row, col)
        if cell.is_given:
            return

        if self._state.input_mode == InputMode.NORMAL:
            self._undo_redo.execute(
                self._state.grid, row, col, lambda g, r, c: g.set_value(r, c, digit)
            )
        else:
            self._undo_redo.execute(
                self._state.grid, row, col, lambda g, r, c: g.toggle_note(r, c, digit)
            )
        self._after_mutation()

    def _handle_delete(self) -> None:
        if not self._state.selected:
            return

        # In color mode, delete removes the highlight
        if self._state.input_mode == InputMode.COLOR:
            row, col = self._state.cursor.position
            self._state.grid.get(row, col).highlight = 0
            self._state.mark_dirty()
            return

        row, col = self._state.cursor.position
        cell = self._state.grid.get(row, col)
        if cell.is_given:
            return
        self._undo_redo.execute(self._state.grid, row, col, lambda g, r, c: g.clear_cell(r, c))
        self._after_mutation()

    def _handle_apply_color(self) -> None:
        if not self._state.selected:
            return
        if self._state.input_mode != InputMode.COLOR:
            return
        row, col = self._state.cursor.position
        cell = self._state.grid.get(row, col)
        # Toggle: if cell already has this color, remove it; otherwise apply
        if cell.highlight == self._state.active_color:
            cell.highlight = 0
        else:
            cell.highlight = self._state.active_color
        self._state.mark_dirty()

    def _handle_undo(self) -> None:
        if self._undo_redo.undo(self._state.grid):
            self._after_mutation()

    def _handle_redo(self) -> None:
        if self._undo_redo.redo(self._state.grid):
            self._after_mutation()

    def _after_mutation(self) -> None:
        self._validator.update_conflicts(self._state)
        self._state.is_won = self._validator.check_win(self._state)
        self._state.mark_dirty()


_MOVE_DELTAS: dict[Action, tuple[int, int]] = {
    Action.MOVE_UP: (-1, 0),
    Action.MOVE_DOWN: (1, 0),
    Action.MOVE_LEFT: (0, -1),
    Action.MOVE_RIGHT: (0, 1),
}
