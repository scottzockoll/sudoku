from sudoku.core.constraint import CageConstraint
from sudoku.core.game_state import GameState
from sudoku.core.grid import Grid
from sudoku.core.validator import Validator

# A valid completed sudoku for testing win detection
VALID_SOLUTION = [
    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, 6, 7],
    [8, 5, 9, 7, 6, 1, 4, 2, 3],
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9],
]


def _make_state_with_values(values: dict[tuple[int, int], int]) -> GameState:
    grid = Grid.empty()
    for (row, col), value in values.items():
        grid.set_value(row, col, value)
    return GameState(grid=grid)


def _make_solved_state() -> GameState:
    grid = Grid.from_raw(VALID_SOLUTION)
    return GameState(grid=grid)


class TestValidatorConflicts:
    def test_no_conflicts_empty_grid(self) -> None:
        state = _make_state_with_values({})
        validator = Validator()
        conflicts = validator.find_conflicts(state)
        assert conflicts == set()

    def test_row_conflict(self) -> None:
        state = _make_state_with_values({(0, 0): 5, (0, 3): 5})
        validator = Validator()
        conflicts = validator.find_conflicts(state)
        assert (0, 0) in conflicts
        assert (0, 3) in conflicts

    def test_col_conflict(self) -> None:
        state = _make_state_with_values({(0, 0): 5, (3, 0): 5})
        validator = Validator()
        conflicts = validator.find_conflicts(state)
        assert (0, 0) in conflicts
        assert (3, 0) in conflicts

    def test_box_conflict(self) -> None:
        state = _make_state_with_values({(0, 0): 5, (2, 2): 5})
        validator = Validator()
        conflicts = validator.find_conflicts(state)
        assert (0, 0) in conflicts
        assert (2, 2) in conflicts

    def test_no_false_positives(self) -> None:
        state = _make_state_with_values({(0, 0): 1, (0, 1): 2, (0, 2): 3})
        validator = Validator()
        conflicts = validator.find_conflicts(state)
        assert conflicts == set()

    def test_cage_conflicts_included(self) -> None:
        cage = CageConstraint(target_sum=10, cells=[(0, 0), (1, 1)])
        grid = Grid.empty()
        grid.set_value(0, 0, 5)
        grid.set_value(1, 1, 5)
        state = GameState(grid=grid, constraints=[cage])
        validator = Validator()
        conflicts = validator.find_conflicts(state)
        assert (0, 0) in conflicts
        assert (1, 1) in conflicts


class TestValidatorUpdateConflicts:
    def test_update_sets_conflict_flags(self) -> None:
        state = _make_state_with_values({(0, 0): 5, (0, 3): 5})
        validator = Validator()
        validator.update_conflicts(state)
        assert state.grid.get(0, 0).is_conflict is True
        assert state.grid.get(0, 3).is_conflict is True
        assert state.grid.get(0, 1).is_conflict is False

    def test_update_clears_old_conflicts(self) -> None:
        state = _make_state_with_values({(0, 0): 5, (0, 3): 5})
        validator = Validator()
        validator.update_conflicts(state)
        state.grid.clear_cell(0, 3)
        validator.update_conflicts(state)
        assert state.grid.get(0, 0).is_conflict is False


class TestValidatorWin:
    def test_win_valid_solution(self) -> None:
        state = _make_solved_state()
        validator = Validator()
        assert validator.check_win(state) is True

    def test_no_win_incomplete(self) -> None:
        state = _make_state_with_values({(0, 0): 5})
        validator = Validator()
        assert validator.check_win(state) is False

    def test_no_win_with_conflicts(self) -> None:
        # Fill the grid but with a conflict
        grid = Grid.from_raw(VALID_SOLUTION)
        # Swap two values to create a conflict
        # (0,0) is 5, (0,1) is 3 — change (0,1) to 5
        grid.cells[0][1] = grid.cells[0][0]  # duplicate the cell
        state = GameState(grid=grid)
        validator = Validator()
        assert validator.check_win(state) is False

    def test_no_win_cage_unsatisfied(self) -> None:
        # Valid standard solution but cage constraint not met
        cage = CageConstraint(target_sum=99, cells=[(0, 0), (0, 1)])
        state = GameState(grid=Grid.from_raw(VALID_SOLUTION), constraints=[cage])
        validator = Validator()
        assert validator.check_win(state) is False

    def test_win_with_satisfied_cage(self) -> None:
        # 5 + 3 = 8
        cage = CageConstraint(target_sum=8, cells=[(0, 0), (0, 1)])
        state = GameState(grid=Grid.from_raw(VALID_SOLUTION), constraints=[cage])
        validator = Validator()
        assert validator.check_win(state) is True


class TestValidatorSameDigit:
    def test_same_digit_positions(self) -> None:
        state = _make_state_with_values({(0, 0): 5, (3, 3): 5, (8, 8): 5})
        validator = Validator()
        positions = validator.get_same_digit_positions(state, 5)
        assert positions == {(0, 0), (3, 3), (8, 8)}

    def test_same_digit_no_matches(self) -> None:
        state = _make_state_with_values({(0, 0): 1})
        validator = Validator()
        positions = validator.get_same_digit_positions(state, 5)
        assert positions == set()


class TestValidatorRelatedPositions:
    def test_related_positions_count(self) -> None:
        validator = Validator()
        positions = validator.get_related_positions(0, 0)
        # 8 in same row + 8 in same col + 4 in same box (not double-counted)
        assert len(positions) == 20

    def test_related_positions_excludes_self(self) -> None:
        validator = Validator()
        positions = validator.get_related_positions(4, 4)
        assert (4, 4) not in positions

    def test_related_positions_center(self) -> None:
        validator = Validator()
        positions = validator.get_related_positions(4, 4)
        # Same row
        for c in range(9):
            if c != 4:
                assert (4, c) in positions
        # Same col
        for r in range(9):
            if r != 4:
                assert (r, 4) in positions
        # Same box (3,3)-(5,5)
        assert (3, 3) in positions
        assert (5, 5) in positions
