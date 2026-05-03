import pytest

from sudoku.core.cell import Cell, CellKind
from sudoku.core.grid import Grid


def _make_empty_grid() -> Grid:
    return Grid.empty()


def _make_grid_with_given(row: int, col: int, value: int) -> Grid:
    grid = Grid.empty()
    grid.cells[row][col] = Cell(kind=CellKind.GIVEN, value=value)
    return grid


class TestGridCreation:
    def test_empty_grid_dimensions(self) -> None:
        grid = _make_empty_grid()
        assert len(grid.cells) == 9
        for row in grid.cells:
            assert len(row) == 9

    def test_empty_grid_all_player_cells(self) -> None:
        grid = _make_empty_grid()
        for row in range(9):
            for col in range(9):
                cell = grid.get(row, col)
                assert cell.kind == CellKind.PLAYER
                assert cell.is_empty

    def test_from_raw_grid(self) -> None:
        raw = [[0] * 9 for _ in range(9)]
        raw[0][0] = 5
        raw[4][4] = 9
        grid = Grid.from_raw(raw)
        assert grid.get(0, 0).value == 5
        assert grid.get(0, 0).is_given
        assert grid.get(4, 4).value == 9
        assert grid.get(4, 4).is_given
        assert grid.get(0, 1).is_empty
        assert not grid.get(0, 1).is_given


class TestGridAccess:
    def test_get_cell(self) -> None:
        grid = _make_grid_with_given(3, 5, 7)
        cell = grid.get(3, 5)
        assert cell.value == 7
        assert cell.is_given

    def test_get_out_of_bounds(self) -> None:
        grid = _make_empty_grid()
        with pytest.raises(IndexError):
            grid.get(9, 0)

    def test_get_negative_index(self) -> None:
        grid = _make_empty_grid()
        with pytest.raises(IndexError):
            grid.get(-1, 0)


class TestGridMutations:
    def test_set_value(self) -> None:
        grid = _make_empty_grid()
        grid.set_value(0, 0, 5)
        assert grid.get(0, 0).value == 5

    def test_set_value_on_given_raises(self) -> None:
        grid = _make_grid_with_given(0, 0, 5)
        with pytest.raises(ValueError, match="Cannot modify given cell"):
            grid.set_value(0, 0, 3)

    def test_toggle_note(self) -> None:
        grid = _make_empty_grid()
        grid.toggle_note(0, 0, 3)
        assert 3 in grid.get(0, 0).notes

    def test_clear_cell(self) -> None:
        grid = _make_empty_grid()
        grid.set_value(0, 0, 5)
        grid.clear_cell(0, 0)
        assert grid.get(0, 0).is_empty


class TestGridQueries:
    def test_row_values(self) -> None:
        grid = _make_empty_grid()
        grid.set_value(0, 0, 1)
        grid.set_value(0, 3, 5)
        values = grid.row_values(0)
        assert values == [1, 5]

    def test_col_values(self) -> None:
        grid = _make_empty_grid()
        grid.set_value(0, 0, 1)
        grid.set_value(3, 0, 5)
        values = grid.col_values(0)
        assert values == [1, 5]

    def test_box_values(self) -> None:
        grid = _make_empty_grid()
        grid.set_value(0, 0, 1)
        grid.set_value(1, 1, 5)
        grid.set_value(2, 2, 9)
        values = grid.box_values(0, 0)
        assert sorted(values) == [1, 5, 9]

    def test_box_values_center_box(self) -> None:
        grid = _make_empty_grid()
        grid.set_value(3, 3, 7)
        grid.set_value(5, 5, 2)
        values = grid.box_values(4, 4)
        assert sorted(values) == [2, 7]

    def test_is_complete(self) -> None:
        grid = _make_empty_grid()
        assert grid.is_complete is False

    def test_all_positions(self) -> None:
        positions = list(Grid.all_positions())
        assert len(positions) == 81
        assert positions[0] == (0, 0)
        assert positions[-1] == (8, 8)
