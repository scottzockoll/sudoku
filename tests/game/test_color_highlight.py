from sudoku.core.game_state import GameState, InputMode
from sudoku.core.grid import Grid
from sudoku.game.actions import Action
from sudoku.game.game_controller import GameController


def _make_controller() -> tuple[GameController, GameState]:
    grid = Grid.empty()
    state = GameState(grid=grid)
    controller = GameController(state)
    return controller, state


class TestColorMode:
    def test_toggle_color_mode(self) -> None:
        controller, state = _make_controller()
        assert state.input_mode == InputMode.NORMAL
        controller.handle(Action.TOGGLE_COLOR_MODE)
        assert state.input_mode == InputMode.COLOR
        controller.handle(Action.TOGGLE_COLOR_MODE)
        assert state.input_mode == InputMode.NORMAL

    def test_escape_exits_color_mode(self) -> None:
        controller, state = _make_controller()
        controller.handle(Action.TOGGLE_COLOR_MODE)
        assert state.input_mode == InputMode.COLOR
        controller.handle(Action.ESCAPE)
        assert state.input_mode == InputMode.NORMAL

    def test_digits_select_color_in_color_mode(self) -> None:
        controller, state = _make_controller()
        controller.handle(Action.MOVE_DOWN)  # select a cell
        controller.handle(Action.TOGGLE_COLOR_MODE)
        controller.handle(Action.DIGIT_5)
        assert state.active_color == 5
        # Cell should NOT have a value — digits pick colors, not fill cells
        assert state.grid.get(1, 0).value is None

    def test_digits_dont_fill_in_color_mode(self) -> None:
        controller, state = _make_controller()
        controller.handle(Action.MOVE_DOWN)
        controller.handle(Action.TOGGLE_COLOR_MODE)
        controller.handle(Action.DIGIT_3)
        assert state.grid.get(1, 0).value is None

    def test_default_active_color(self) -> None:
        _, state = _make_controller()
        assert state.active_color == 1


class TestApplyColor:
    def test_apply_color_to_cell(self) -> None:
        controller, state = _make_controller()
        controller.handle(Action.MOVE_DOWN)
        controller.handle(Action.TOGGLE_COLOR_MODE)
        controller.handle(Action.DIGIT_3)  # select color 3
        controller.handle(Action.APPLY_COLOR)
        assert state.grid.get(1, 0).highlight == 3

    def test_apply_color_toggle_off(self) -> None:
        controller, state = _make_controller()
        controller.handle(Action.MOVE_DOWN)
        controller.handle(Action.TOGGLE_COLOR_MODE)
        controller.handle(Action.DIGIT_3)
        controller.handle(Action.APPLY_COLOR)  # apply
        controller.handle(Action.APPLY_COLOR)  # toggle off
        assert state.grid.get(1, 0).highlight == 0

    def test_apply_color_changes_existing(self) -> None:
        controller, state = _make_controller()
        controller.handle(Action.MOVE_DOWN)
        controller.handle(Action.TOGGLE_COLOR_MODE)
        controller.handle(Action.DIGIT_3)
        controller.handle(Action.APPLY_COLOR)
        controller.handle(Action.DIGIT_7)  # switch to color 7
        controller.handle(Action.APPLY_COLOR)
        assert state.grid.get(1, 0).highlight == 7

    def test_apply_color_without_selection_does_nothing(self) -> None:
        controller, state = _make_controller()
        controller.handle(Action.TOGGLE_COLOR_MODE)
        controller.handle(Action.APPLY_COLOR)
        assert state.grid.get(0, 0).highlight == 0

    def test_apply_color_outside_color_mode_does_nothing(self) -> None:
        controller, state = _make_controller()
        controller.handle(Action.MOVE_DOWN)
        controller.handle(Action.APPLY_COLOR)
        assert state.grid.get(1, 0).highlight == 0

    def test_apply_color_on_given_cell(self) -> None:
        grid = Grid.from_raw(
            [
                [5, 0, 0, 0, 0, 0, 0, 0, 0],
                *([[0] * 9] * 8),
            ]
        )
        state = GameState(grid=grid)
        controller = GameController(state)
        state.select()
        controller.handle(Action.TOGGLE_COLOR_MODE)
        controller.handle(Action.APPLY_COLOR)
        assert state.grid.get(0, 0).highlight == 1

    def test_delete_removes_highlight_in_color_mode(self) -> None:
        controller, state = _make_controller()
        controller.handle(Action.MOVE_DOWN)
        controller.handle(Action.TOGGLE_COLOR_MODE)
        controller.handle(Action.DIGIT_5)
        controller.handle(Action.APPLY_COLOR)
        assert state.grid.get(1, 0).highlight == 5
        controller.handle(Action.DELETE)
        assert state.grid.get(1, 0).highlight == 0

    def test_color_not_affected_by_undo(self) -> None:
        controller, state = _make_controller()
        controller.handle(Action.MOVE_DOWN)
        # Apply a color
        controller.handle(Action.TOGGLE_COLOR_MODE)
        controller.handle(Action.APPLY_COLOR)
        controller.handle(Action.TOGGLE_COLOR_MODE)  # back to normal
        # Enter a digit
        controller.handle(Action.DIGIT_5)
        # Undo the digit
        controller.handle(Action.UNDO)
        # Highlight should persist
        assert state.grid.get(1, 0).highlight == 1
        assert state.grid.get(1, 0).value is None

    def test_apply_color_marks_dirty(self) -> None:
        controller, state = _make_controller()
        controller.handle(Action.MOVE_DOWN)
        controller.handle(Action.TOGGLE_COLOR_MODE)
        state.clear_dirty()
        controller.handle(Action.APPLY_COLOR)
        assert state.dirty is True
