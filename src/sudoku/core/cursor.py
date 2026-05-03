class Cursor:
    def __init__(self, row: int = 0, col: int = 0) -> None:
        self.row = row
        self.col = col

    @property
    def position(self) -> tuple[int, int]:
        return (self.row, self.col)

    def move(self, dr: int, dc: int) -> None:
        self.row = (self.row + dr) % 9
        self.col = (self.col + dc) % 9
