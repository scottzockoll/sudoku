from sudoku.core.constraint import CageConstraint
from sudoku.core.grid import Grid


def _make_grid_with_values(values: dict[tuple[int, int], int]) -> Grid:
    grid = Grid.empty()
    for (row, col), value in values.items():
        grid.set_value(row, col, value)
    return grid


class TestCageConstraint:
    def test_creation(self) -> None:
        cage = CageConstraint(target_sum=15, cells=[(0, 0), (0, 1), (0, 2)])
        assert cage.target_sum == 15
        assert cage.cells == [(0, 0), (0, 1), (0, 2)]
        assert cage.constraint_type == "cage"

    def test_no_conflicts_when_empty(self) -> None:
        cage = CageConstraint(target_sum=15, cells=[(0, 0), (0, 1), (0, 2)])
        grid = Grid.empty()
        assert cage.find_conflicts(grid) == set()

    def test_no_conflicts_with_unique_values(self) -> None:
        cage = CageConstraint(target_sum=6, cells=[(0, 0), (0, 1), (0, 2)])
        grid = _make_grid_with_values({(0, 0): 1, (0, 1): 2, (0, 2): 3})
        assert cage.find_conflicts(grid) == set()

    def test_duplicate_values_are_conflicts(self) -> None:
        cage = CageConstraint(target_sum=10, cells=[(0, 0), (0, 1), (0, 2)])
        grid = _make_grid_with_values({(0, 0): 5, (0, 1): 5})
        conflicts = cage.find_conflicts(grid)
        assert (0, 0) in conflicts
        assert (0, 1) in conflicts

    def test_partial_fill_no_duplicate_no_conflict(self) -> None:
        cage = CageConstraint(target_sum=10, cells=[(0, 0), (0, 1), (0, 2)])
        grid = _make_grid_with_values({(0, 0): 5})
        assert cage.find_conflicts(grid) == set()

    def test_is_satisfied_correct_sum_unique(self) -> None:
        cage = CageConstraint(target_sum=6, cells=[(0, 0), (0, 1), (0, 2)])
        grid = _make_grid_with_values({(0, 0): 1, (0, 1): 2, (0, 2): 3})
        assert cage.is_satisfied(grid) is True

    def test_is_satisfied_wrong_sum(self) -> None:
        cage = CageConstraint(target_sum=10, cells=[(0, 0), (0, 1), (0, 2)])
        grid = _make_grid_with_values({(0, 0): 1, (0, 1): 2, (0, 2): 3})
        assert cage.is_satisfied(grid) is False

    def test_is_satisfied_incomplete(self) -> None:
        cage = CageConstraint(target_sum=6, cells=[(0, 0), (0, 1), (0, 2)])
        grid = _make_grid_with_values({(0, 0): 1, (0, 1): 2})
        assert cage.is_satisfied(grid) is False

    def test_is_satisfied_duplicates(self) -> None:
        cage = CageConstraint(target_sum=6, cells=[(0, 0), (0, 1), (0, 2)])
        grid = _make_grid_with_values({(0, 0): 2, (0, 1): 2, (0, 2): 2})
        assert cage.is_satisfied(grid) is False
