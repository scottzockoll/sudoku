from sudoku.core.cursor import Cursor


class TestCursorCreation:
    def test_default_position(self) -> None:
        cursor = Cursor()
        assert cursor.row == 0
        assert cursor.col == 0

    def test_custom_position(self) -> None:
        cursor = Cursor(row=3, col=5)
        assert cursor.row == 3
        assert cursor.col == 5


class TestCursorMovement:
    def test_move_down(self) -> None:
        cursor = Cursor()
        cursor.move(dr=1, dc=0)
        assert cursor.row == 1
        assert cursor.col == 0

    def test_move_right(self) -> None:
        cursor = Cursor()
        cursor.move(dr=0, dc=1)
        assert cursor.row == 0
        assert cursor.col == 1

    def test_move_up(self) -> None:
        cursor = Cursor(row=3, col=0)
        cursor.move(dr=-1, dc=0)
        assert cursor.row == 2

    def test_move_left(self) -> None:
        cursor = Cursor(row=0, col=3)
        cursor.move(dr=0, dc=-1)
        assert cursor.col == 2

    def test_wrap_down(self) -> None:
        cursor = Cursor(row=8, col=0)
        cursor.move(dr=1, dc=0)
        assert cursor.row == 0

    def test_wrap_up(self) -> None:
        cursor = Cursor(row=0, col=0)
        cursor.move(dr=-1, dc=0)
        assert cursor.row == 8

    def test_wrap_right(self) -> None:
        cursor = Cursor(row=0, col=8)
        cursor.move(dr=0, dc=1)
        assert cursor.col == 0

    def test_wrap_left(self) -> None:
        cursor = Cursor(row=0, col=0)
        cursor.move(dr=0, dc=-1)
        assert cursor.col == 8

    def test_diagonal_move(self) -> None:
        cursor = Cursor(row=4, col=4)
        cursor.move(dr=1, dc=1)
        assert cursor.row == 5
        assert cursor.col == 5

    def test_diagonal_wrap(self) -> None:
        cursor = Cursor(row=8, col=8)
        cursor.move(dr=1, dc=1)
        assert cursor.row == 0
        assert cursor.col == 0


class TestCursorPosition:
    def test_position_property(self) -> None:
        cursor = Cursor(row=3, col=5)
        assert cursor.position == (3, 5)
