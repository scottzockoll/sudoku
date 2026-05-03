class Layout:
    def __init__(self, screen_width: int = 1024, screen_height: int = 600) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.cell_size = (min(screen_width, screen_height) - 40) // 9
        self.grid_pixel_size = self.cell_size * 9
        self.grid_x = (screen_width - self.grid_pixel_size) // 2
        self.grid_y = (screen_height - self.grid_pixel_size) // 2
        self.note_pad = 10  # inset from cell edge for note positions
        self.note_area = self.cell_size - self.note_pad * 2
        self.note_size = self.note_area // 3

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

    @staticmethod
    def is_box_border_row(row: int) -> bool:
        return row % 3 == 0

    @staticmethod
    def is_box_border_col(col: int) -> bool:
        return col % 3 == 0
