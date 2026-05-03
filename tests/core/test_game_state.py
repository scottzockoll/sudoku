from sudoku.core.constraint import CageConstraint
from sudoku.core.game_state import GameState, InputMode
from sudoku.core.grid import Grid


class TestGameStateCreation:
    def test_default_state(self) -> None:
        grid = Grid.empty()
        state = GameState(grid=grid)
        assert state.grid is grid
        assert state.cursor.row == 0
        assert state.cursor.col == 0
        assert state.selected is False
        assert state.input_mode == InputMode.NORMAL
        assert state.is_won is False
        assert state.constraints == []

    def test_state_with_constraints(self) -> None:
        grid = Grid.empty()
        cage = CageConstraint(target_sum=15, cells=[(0, 0), (0, 1)])
        state = GameState(grid=grid, constraints=[cage])
        assert len(state.constraints) == 1
        assert state.constraints[0] is cage


class TestGameStateDirtyFlag:
    def test_starts_dirty(self) -> None:
        state = GameState(grid=Grid.empty())
        assert state.dirty is True

    def test_clear_dirty(self) -> None:
        state = GameState(grid=Grid.empty())
        state.clear_dirty()
        assert state.dirty is False

    def test_mark_dirty(self) -> None:
        state = GameState(grid=Grid.empty())
        state.clear_dirty()
        state.mark_dirty()
        assert state.dirty is True


class TestGameStateInputMode:
    def test_toggle_mode(self) -> None:
        state = GameState(grid=Grid.empty())
        assert state.input_mode == InputMode.NORMAL
        state.toggle_input_mode()
        assert state.input_mode == InputMode.NOTES
        state.toggle_input_mode()
        assert state.input_mode == InputMode.NORMAL

    def test_toggle_mode_marks_dirty(self) -> None:
        state = GameState(grid=Grid.empty())
        state.clear_dirty()
        state.toggle_input_mode()
        assert state.dirty is True


class TestGameStateSelection:
    def test_select(self) -> None:
        state = GameState(grid=Grid.empty())
        state.clear_dirty()
        state.select()
        assert state.selected is True
        assert state.dirty is True

    def test_deselect(self) -> None:
        state = GameState(grid=Grid.empty())
        state.select()
        state.clear_dirty()
        state.deselect()
        assert state.selected is False
        assert state.dirty is True

    def test_move_cursor_selects(self) -> None:
        state = GameState(grid=Grid.empty())
        state.clear_dirty()
        state.move_cursor(1, 0)
        assert state.selected is True
        assert state.cursor.row == 1
        assert state.dirty is True
