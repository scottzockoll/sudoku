from __future__ import annotations

from collections.abc import Iterator

from sudoku.core.cell import Cell, CellKind


class Grid:
    def __init__(self, cells: list[list[Cell]]) -> None:
        self.cells = cells

    @classmethod
    def empty(cls) -> Grid:
        cells = [[Cell(kind=CellKind.PLAYER) for _ in range(9)] for _ in range(9)]
        return cls(cells)

    @classmethod
    def from_raw(cls, raw: list[list[int]]) -> Grid:
        cells: list[list[Cell]] = []
        for row in raw:
            cell_row: list[Cell] = []
            for value in row:
                if value == 0:
                    cell_row.append(Cell(kind=CellKind.PLAYER))
                else:
                    cell_row.append(Cell(kind=CellKind.GIVEN, value=value))
            cells.append(cell_row)
        return cls(cells)

    def get(self, row: int, col: int) -> Cell:
        if row < 0 or row >= 9 or col < 0 or col >= 9:
            raise IndexError(f"Position ({row}, {col}) out of bounds")
        return self.cells[row][col]

    def set_value(self, row: int, col: int, value: int) -> None:
        self.get(row, col).set_value(value)

    def toggle_note(self, row: int, col: int, digit: int) -> None:
        self.get(row, col).toggle_note(digit)

    def clear_cell(self, row: int, col: int) -> None:
        self.get(row, col).clear()

    def row_values(self, row: int) -> list[int]:
        return [cell.value for cell in self.cells[row] if cell.value is not None]

    def col_values(self, col: int) -> list[int]:
        values: list[int] = []
        for row in range(9):
            v = self.cells[row][col].value
            if v is not None:
                values.append(v)
        return values

    def box_values(self, row: int, col: int) -> list[int]:
        box_row, box_col = (row // 3) * 3, (col // 3) * 3
        values: list[int] = []
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                v = self.cells[r][c].value
                if v is not None:
                    values.append(v)
        return values

    @property
    def is_complete(self) -> bool:
        return all(self.cells[r][c].value is not None for r in range(9) for c in range(9))

    @staticmethod
    def all_positions() -> Iterator[tuple[int, int]]:
        for r in range(9):
            for c in range(9):
                yield (r, c)
