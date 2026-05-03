from sudoku.core.cell import Cell, CellKind


class TestCellCreation:
    def test_empty_player_cell(self) -> None:
        cell = Cell(kind=CellKind.PLAYER)
        assert cell.value is None
        assert cell.notes == set()
        assert cell.kind == CellKind.PLAYER
        assert cell.is_conflict is False

    def test_given_cell_with_value(self) -> None:
        cell = Cell(kind=CellKind.GIVEN, value=5)
        assert cell.value == 5
        assert cell.notes == set()
        assert cell.kind == CellKind.GIVEN

    def test_cell_with_notes(self) -> None:
        cell = Cell(kind=CellKind.PLAYER, notes={1, 3, 7})
        assert cell.notes == {1, 3, 7}
        assert cell.value is None


class TestCellProperties:
    def test_is_given(self) -> None:
        given = Cell(kind=CellKind.GIVEN, value=5)
        player = Cell(kind=CellKind.PLAYER)
        assert given.is_given is True
        assert player.is_given is False

    def test_is_empty(self) -> None:
        empty = Cell(kind=CellKind.PLAYER)
        filled = Cell(kind=CellKind.PLAYER, value=3)
        given = Cell(kind=CellKind.GIVEN, value=5)
        assert empty.is_empty is True
        assert filled.is_empty is False
        assert given.is_empty is False


class TestCellMutations:
    def test_set_value(self) -> None:
        cell = Cell(kind=CellKind.PLAYER)
        cell.set_value(5)
        assert cell.value == 5
        assert cell.notes == set()

    def test_set_value_clears_notes(self) -> None:
        cell = Cell(kind=CellKind.PLAYER, notes={1, 2, 3})
        cell.set_value(5)
        assert cell.value == 5
        assert cell.notes == set()

    def test_clear_value(self) -> None:
        cell = Cell(kind=CellKind.PLAYER, value=5)
        cell.clear()
        assert cell.value is None
        assert cell.notes == set()

    def test_clear_notes(self) -> None:
        cell = Cell(kind=CellKind.PLAYER, notes={1, 2, 3})
        cell.clear()
        assert cell.value is None
        assert cell.notes == set()

    def test_toggle_note_add(self) -> None:
        cell = Cell(kind=CellKind.PLAYER)
        cell.toggle_note(5)
        assert 5 in cell.notes

    def test_toggle_note_remove(self) -> None:
        cell = Cell(kind=CellKind.PLAYER, notes={5})
        cell.toggle_note(5)
        assert 5 not in cell.notes

    def test_toggle_note_clears_value(self) -> None:
        cell = Cell(kind=CellKind.PLAYER, value=3)
        cell.toggle_note(5)
        assert cell.value is None
        assert 5 in cell.notes

    def test_given_cell_rejects_set_value(self) -> None:
        cell = Cell(kind=CellKind.GIVEN, value=5)
        import pytest

        with pytest.raises(ValueError, match="Cannot modify given cell"):
            cell.set_value(3)

    def test_given_cell_rejects_toggle_note(self) -> None:
        cell = Cell(kind=CellKind.GIVEN, value=5)
        import pytest

        with pytest.raises(ValueError, match="Cannot modify given cell"):
            cell.toggle_note(3)

    def test_given_cell_rejects_clear(self) -> None:
        cell = Cell(kind=CellKind.GIVEN, value=5)
        import pytest

        with pytest.raises(ValueError, match="Cannot modify given cell"):
            cell.clear()


class TestCellSnapshot:
    def test_snapshot_captures_state(self) -> None:
        cell = Cell(kind=CellKind.PLAYER, value=5, notes={1, 2})
        snapshot = cell.snapshot()
        assert snapshot.value == 5
        assert snapshot.notes == frozenset({1, 2})

    def test_restore_from_snapshot(self) -> None:
        cell = Cell(kind=CellKind.PLAYER, value=5)
        snapshot = cell.snapshot()
        cell.set_value(9)
        cell.restore(snapshot)
        assert cell.value == 5
