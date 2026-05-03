from sudoku.core.grid import Grid
from sudoku.game.command import UndoRedoStack


class TestUndoRedoStack:
    def test_execute_records_change(self) -> None:
        grid = Grid.empty()
        stack = UndoRedoStack()
        stack.execute(grid, 0, 0, lambda g, r, c: g.set_value(r, c, 5))
        assert grid.get(0, 0).value == 5
        assert stack.can_undo

    def test_undo_restores_previous_state(self) -> None:
        grid = Grid.empty()
        stack = UndoRedoStack()
        stack.execute(grid, 0, 0, lambda g, r, c: g.set_value(r, c, 5))
        result = stack.undo(grid)
        assert result is True
        assert grid.get(0, 0).value is None

    def test_redo_reapplies_change(self) -> None:
        grid = Grid.empty()
        stack = UndoRedoStack()
        stack.execute(grid, 0, 0, lambda g, r, c: g.set_value(r, c, 5))
        stack.undo(grid)
        result = stack.redo(grid)
        assert result is True
        assert grid.get(0, 0).value == 5

    def test_undo_on_empty_stack(self) -> None:
        grid = Grid.empty()
        stack = UndoRedoStack()
        assert stack.undo(grid) is False

    def test_redo_on_empty_stack(self) -> None:
        grid = Grid.empty()
        stack = UndoRedoStack()
        assert stack.redo(grid) is False

    def test_new_action_clears_redo(self) -> None:
        grid = Grid.empty()
        stack = UndoRedoStack()
        stack.execute(grid, 0, 0, lambda g, r, c: g.set_value(r, c, 5))
        stack.undo(grid)
        assert stack.can_redo
        stack.execute(grid, 0, 0, lambda g, r, c: g.set_value(r, c, 9))
        assert not stack.can_redo

    def test_no_op_change_not_recorded(self) -> None:
        grid = Grid.empty()
        stack = UndoRedoStack()
        # Setting value when cell already empty and doing nothing
        stack.execute(grid, 0, 0, lambda g, r, c: None)
        assert not stack.can_undo

    def test_multiple_undo(self) -> None:
        grid = Grid.empty()
        stack = UndoRedoStack()
        stack.execute(grid, 0, 0, lambda g, r, c: g.set_value(r, c, 1))
        stack.execute(grid, 0, 0, lambda g, r, c: g.set_value(r, c, 2))
        stack.execute(grid, 0, 0, lambda g, r, c: g.set_value(r, c, 3))

        stack.undo(grid)
        assert grid.get(0, 0).value == 2
        stack.undo(grid)
        assert grid.get(0, 0).value == 1
        stack.undo(grid)
        assert grid.get(0, 0).value is None

    def test_undo_redo_notes(self) -> None:
        grid = Grid.empty()
        stack = UndoRedoStack()
        stack.execute(grid, 0, 0, lambda g, r, c: g.toggle_note(r, c, 5))
        assert 5 in grid.get(0, 0).notes

        stack.undo(grid)
        assert 5 not in grid.get(0, 0).notes

        stack.redo(grid)
        assert 5 in grid.get(0, 0).notes

    def test_can_undo_property(self) -> None:
        grid = Grid.empty()
        stack = UndoRedoStack()
        assert stack.can_undo is False
        stack.execute(grid, 0, 0, lambda g, r, c: g.set_value(r, c, 5))
        assert stack.can_undo is True

    def test_can_redo_property(self) -> None:
        grid = Grid.empty()
        stack = UndoRedoStack()
        stack.execute(grid, 0, 0, lambda g, r, c: g.set_value(r, c, 5))
        assert stack.can_redo is False
        stack.undo(grid)
        assert stack.can_redo is True
