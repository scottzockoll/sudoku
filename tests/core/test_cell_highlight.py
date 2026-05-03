from sudoku.core.cell import Cell, CellKind


class TestCellHighlight:
    def test_default_no_highlight(self) -> None:
        cell = Cell(kind=CellKind.PLAYER)
        assert cell.highlight == 0

    def test_set_highlight(self) -> None:
        cell = Cell(kind=CellKind.PLAYER)
        cell.highlight = 3
        assert cell.highlight == 3

    def test_cycle_highlight(self) -> None:
        cell = Cell(kind=CellKind.PLAYER)
        cell.cycle_highlight()
        assert cell.highlight == 1
        for _ in range(9):
            cell.cycle_highlight()
        assert cell.highlight == 0  # wraps back after 10 cycles total

    def test_cycle_through_all_colors(self) -> None:
        cell = Cell(kind=CellKind.PLAYER)
        seen = []
        for _ in range(10):
            cell.cycle_highlight()
            seen.append(cell.highlight)
        # Should cycle 1,2,3,4,5,6,7,8,9,0
        assert seen == [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]

    def test_given_cell_can_be_highlighted(self) -> None:
        cell = Cell(kind=CellKind.GIVEN, value=5)
        cell.cycle_highlight()
        assert cell.highlight == 1

    def test_highlight_not_affected_by_snapshot_restore(self) -> None:
        cell = Cell(kind=CellKind.PLAYER)
        cell.highlight = 5
        snap = cell.snapshot()
        cell.set_value(3)
        cell.highlight = 7
        cell.restore(snap)
        # Highlight should NOT be restored — it's independent of undo
        assert cell.highlight == 7

    def test_clear_highlight(self) -> None:
        cell = Cell(kind=CellKind.PLAYER)
        cell.highlight = 3
        cell.highlight = 0
        assert cell.highlight == 0
