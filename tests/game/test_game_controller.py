from sudoku.core.cell import CellKind
from sudoku.core.game_state import GameState, InputMode
from sudoku.core.grid import Grid
from sudoku.game.actions import Action
from sudoku.game.game_controller import GameController


def _make_controller() -> tuple[GameController, GameState]:
    grid = Grid.empty()
    state = GameState(grid=grid)
    controller = GameController(state)
    return controller, state


def _make_controller_with_given(row: int, col: int, value: int) -> tuple[GameController, GameState]:
    grid = Grid.empty()
    grid.cells[row][col] = __import__("sudoku.core.cell", fromlist=["Cell"]).Cell(
        kind=CellKind.GIVEN, value=value
    )
    state = GameState(grid=grid)
    controller = GameController(state)
    return controller, state


class TestGameControllerMovement:
    def test_move_up(self) -> None:
        controller, state = _make_controller()
        controller.handle(Action.MOVE_DOWN)
        assert state.cursor.row == 1
        assert state.selected is True

    def test_move_selects(self) -> None:
        controller, state = _make_controller()
        assert state.selected is False
        controller.handle(Action.MOVE_RIGHT)
        assert state.selected is True

    def test_all_directions(self) -> None:
        controller, state = _make_controller()
        controller.handle(Action.MOVE_DOWN)
        controller.handle(Action.MOVE_RIGHT)
        assert state.cursor.position == (1, 1)
        controller.handle(Action.MOVE_UP)
        controller.handle(Action.MOVE_LEFT)
        assert state.cursor.position == (0, 0)


class TestGameControllerDigitInput:
    def test_digit_in_normal_mode(self) -> None:
        controller, state = _make_controller()
        controller.handle(Action.MOVE_DOWN)  # select a cell
        controller.handle(Action.DIGIT_5)
        assert state.grid.get(1, 0).value == 5

    def test_digit_in_notes_mode(self) -> None:
        controller, state = _make_controller()
        controller.handle(Action.MOVE_DOWN)
        controller.handle(Action.TOGGLE_NOTES)
        controller.handle(Action.DIGIT_5)
        assert 5 in state.grid.get(1, 0).notes
        assert state.grid.get(1, 0).value is None

    def test_digit_without_selection_does_nothing(self) -> None:
        controller, state = _make_controller()
        controller.handle(Action.DIGIT_5)
        # No cell should be modified since nothing is selected
        assert state.grid.get(0, 0).is_empty

    def test_digit_on_given_cell_does_nothing(self) -> None:
        controller, state = _make_controller_with_given(0, 0, 5)
        state.select()
        controller.handle(Action.DIGIT_3)
        assert state.grid.get(0, 0).value == 5

    def test_all_digits(self) -> None:
        controller, state = _make_controller()
        digits = [
            Action.DIGIT_1,
            Action.DIGIT_2,
            Action.DIGIT_3,
            Action.DIGIT_4,
            Action.DIGIT_5,
            Action.DIGIT_6,
            Action.DIGIT_7,
            Action.DIGIT_8,
            Action.DIGIT_9,
        ]
        for i, action in enumerate(digits):
            # Place each digit in row i, col 0
            state.cursor.row = i
            state.cursor.col = 0
            state.select()
            controller.handle(action)
            assert state.grid.get(i, 0).value == i + 1


class TestGameControllerDelete:
    def test_delete_clears_cell(self) -> None:
        controller, state = _make_controller()
        controller.handle(Action.MOVE_DOWN)
        controller.handle(Action.DIGIT_5)
        controller.handle(Action.DELETE)
        assert state.grid.get(1, 0).is_empty

    def test_delete_without_selection_does_nothing(self) -> None:
        controller, state = _make_controller()
        controller.handle(Action.DELETE)  # should not crash

    def test_delete_given_cell_does_nothing(self) -> None:
        controller, state = _make_controller_with_given(0, 0, 5)
        state.select()
        controller.handle(Action.DELETE)
        assert state.grid.get(0, 0).value == 5


class TestGameControllerEscape:
    def test_escape_deselects(self) -> None:
        controller, state = _make_controller()
        controller.handle(Action.MOVE_DOWN)
        assert state.selected is True
        controller.handle(Action.ESCAPE)
        assert state.selected is False


class TestGameControllerToggleNotes:
    def test_toggle_notes(self) -> None:
        controller, state = _make_controller()
        assert state.input_mode == InputMode.NORMAL
        controller.handle(Action.TOGGLE_NOTES)
        assert state.input_mode == InputMode.NOTES
        controller.handle(Action.TOGGLE_NOTES)
        assert state.input_mode == InputMode.NORMAL


class TestGameControllerUndo:
    def test_undo_digit(self) -> None:
        controller, state = _make_controller()
        controller.handle(Action.MOVE_DOWN)
        controller.handle(Action.DIGIT_5)
        assert state.grid.get(1, 0).value == 5
        controller.handle(Action.UNDO)
        assert state.grid.get(1, 0).is_empty

    def test_redo_digit(self) -> None:
        controller, state = _make_controller()
        controller.handle(Action.MOVE_DOWN)
        controller.handle(Action.DIGIT_5)
        controller.handle(Action.UNDO)
        controller.handle(Action.REDO)
        assert state.grid.get(1, 0).value == 5


class TestGameControllerConflicts:
    def test_conflicts_updated_after_digit(self) -> None:
        controller, state = _make_controller()
        state.select()
        controller.handle(Action.DIGIT_5)
        controller.handle(Action.MOVE_RIGHT)
        controller.handle(Action.DIGIT_5)
        assert state.grid.get(0, 0).is_conflict
        assert state.grid.get(0, 1).is_conflict

    def test_conflicts_cleared_after_undo(self) -> None:
        controller, state = _make_controller()
        state.select()
        controller.handle(Action.DIGIT_5)
        controller.handle(Action.MOVE_RIGHT)
        controller.handle(Action.DIGIT_5)
        controller.handle(Action.UNDO)
        assert not state.grid.get(0, 0).is_conflict
