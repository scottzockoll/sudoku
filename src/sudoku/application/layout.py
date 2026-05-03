class Layout:
    def __init__(self, screen_width: int = 1024, screen_height: int = 600) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.cell_size = (min(screen_width, screen_height) - 40) // 9
        self.grid_pixel_size = self.cell_size * 9
        self.grid_x = (screen_width - self.grid_pixel_size) // 2
        self.grid_y = (screen_height - self.grid_pixel_size) // 2

        # Note layout for normal cells (no cage sum)
        self.note_pad = 5
        self.note_area = self.cell_size - self.note_pad * 2
        self.note_size = self.note_area // 3

        # Note layout for cage-sum cells (shifted down to make room for sum label)
        self.cage_sum_height = 12  # height reserved for cage sum text
        self.cage_note_top = self.note_pad + self.cage_sum_height
        cage_note_area_h = self.cell_size - self.cage_note_top - self.note_pad
        self.cage_note_row_h = cage_note_area_h // 3
        self.cage_note_col_w = self.note_size  # same width as normal

    def cell_rect(self, row: int, col: int) -> tuple[int, int, int, int]:
        x = self.grid_x + col * self.cell_size
        y = self.grid_y + row * self.cell_size
        return (x, y, self.cell_size, self.cell_size)

    def note_position(self, row: int, col: int, digit: int) -> tuple[int, int]:
        cell_x, cell_y, _, _ = self.cell_rect(row, col)
        note_row = (digit - 1) // 3
        note_col = (digit - 1) % 3
        nx = cell_x + self.note_pad + note_col * self.note_size + self.note_size // 2
        ny = cell_y + self.note_pad + note_row * self.note_size + self.note_size // 2
        return (nx, ny)

    def cage_note_position(self, row: int, col: int, digit: int) -> tuple[int, int]:
        """Note position for cells that have a cage sum label in the top-left."""
        cell_x, cell_y, _, _ = self.cell_rect(row, col)
        note_row = (digit - 1) // 3
        note_col = (digit - 1) % 3
        nx = cell_x + self.note_pad + note_col * self.cage_note_col_w + self.cage_note_col_w // 2
        ny = (
            cell_y
            + self.cage_note_top
            + note_row * self.cage_note_row_h
            + self.cage_note_row_h // 2
        )
        return (nx, ny)

    @staticmethod
    def is_box_border_row(row: int) -> bool:
        return row % 3 == 0

    @staticmethod
    def is_box_border_col(col: int) -> bool:
        return col % 3 == 0
