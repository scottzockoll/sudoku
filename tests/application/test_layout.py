from sudoku.application.layout import Layout


class TestLayoutDimensions:
    def test_default_screen_size(self) -> None:
        layout = Layout()
        assert layout.screen_width == 1024
        assert layout.screen_height == 600

    def test_cell_size(self) -> None:
        layout = Layout()
        assert layout.cell_size == 62

    def test_grid_pixel_size(self) -> None:
        layout = Layout()
        assert layout.grid_pixel_size == 558  # 62 * 9

    def test_grid_centered_horizontally(self) -> None:
        layout = Layout()
        # Grid should be centered: (1024 - 558) // 2 = 233
        assert layout.grid_x == 233

    def test_grid_top(self) -> None:
        layout = Layout()
        assert layout.grid_y == 21  # (600 - 558) // 2


class TestLayoutCellRect:
    def test_top_left_cell(self) -> None:
        layout = Layout()
        x, y, w, h = layout.cell_rect(0, 0)
        assert x == layout.grid_x
        assert y == layout.grid_y
        assert w == 62
        assert h == 62

    def test_second_cell(self) -> None:
        layout = Layout()
        x, y, w, h = layout.cell_rect(0, 1)
        assert x == layout.grid_x + 62
        assert y == layout.grid_y

    def test_bottom_right_cell(self) -> None:
        layout = Layout()
        x, y, w, h = layout.cell_rect(8, 8)
        assert x == layout.grid_x + 62 * 8
        assert y == layout.grid_y + 62 * 8


class TestLayoutNotePosition:
    def test_note_positions_3x3_grid(self) -> None:
        layout = Layout()
        # Digit 1 should be at position (0, 0) in the 3x3 sub-grid, with padding
        nx, ny = layout.note_position(0, 0, 1)
        cell_x, cell_y, _, _ = layout.cell_rect(0, 0)
        pad = layout.note_pad
        nw = layout.note_size
        assert nx == cell_x + pad + 0 * nw + nw // 2
        assert ny == cell_y + pad + 0 * nw + nw // 2

    def test_note_digit_5_is_center(self) -> None:
        layout = Layout()
        # Digit 5: (5-1)//3=1, (5-1)%3=1 → center of 3x3
        nx, ny = layout.note_position(0, 0, 5)
        cell_x, cell_y, _, _ = layout.cell_rect(0, 0)
        pad = layout.note_pad
        nw = layout.note_size
        assert nx == cell_x + pad + 1 * nw + nw // 2
        assert ny == cell_y + pad + 1 * nw + nw // 2

    def test_note_digit_9_is_bottom_right(self) -> None:
        layout = Layout()
        # Digit 9: (9-1)//3=2, (9-1)%3=2 → bottom-right
        nx, ny = layout.note_position(0, 0, 9)
        cell_x, cell_y, _, _ = layout.cell_rect(0, 0)
        pad = layout.note_pad
        nw = layout.note_size
        assert nx == cell_x + pad + 2 * nw + nw // 2
        assert ny == cell_y + pad + 2 * nw + nw // 2


class TestLayoutBoxBorders:
    def test_is_box_border_row(self) -> None:
        layout = Layout()
        assert layout.is_box_border_row(0) is True
        assert layout.is_box_border_row(3) is True
        assert layout.is_box_border_row(6) is True
        assert layout.is_box_border_row(1) is False

    def test_is_box_border_col(self) -> None:
        layout = Layout()
        assert layout.is_box_border_col(0) is True
        assert layout.is_box_border_col(3) is True
        assert layout.is_box_border_col(6) is True
        assert layout.is_box_border_col(2) is False
