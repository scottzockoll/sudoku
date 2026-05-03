from sudoku.core.constraint import CageConstraint
from sudoku.core.grid import Grid


class TestCageSumConflict:
    def test_wrong_sum_marks_all_cells(self) -> None:
        cage = CageConstraint(target_sum=10, cells=[(0, 0), (0, 1)])
        grid = Grid.empty()
        grid.set_value(0, 0, 1)
        grid.set_value(0, 1, 2)
        # Sum is 3, target is 10 — all cells should be conflicts
        conflicts = cage.find_conflicts(grid)
        assert (0, 0) in conflicts
        assert (0, 1) in conflicts

    def test_correct_sum_no_conflicts(self) -> None:
        cage = CageConstraint(target_sum=3, cells=[(0, 0), (0, 1)])
        grid = Grid.empty()
        grid.set_value(0, 0, 1)
        grid.set_value(0, 1, 2)
        conflicts = cage.find_conflicts(grid)
        assert conflicts == set()

    def test_partial_fill_no_sum_conflict(self) -> None:
        cage = CageConstraint(target_sum=10, cells=[(0, 0), (0, 1), (0, 2)])
        grid = Grid.empty()
        grid.set_value(0, 0, 1)
        # Only 1 of 3 filled — should not flag sum conflict
        conflicts = cage.find_conflicts(grid)
        assert conflicts == set()

    def test_wrong_sum_and_duplicates(self) -> None:
        cage = CageConstraint(target_sum=10, cells=[(0, 0), (0, 1)])
        grid = Grid.empty()
        grid.set_value(0, 0, 3)
        grid.set_value(0, 1, 3)
        # Duplicates AND wrong sum — both cells should be conflicts
        conflicts = cage.find_conflicts(grid)
        assert (0, 0) in conflicts
        assert (0, 1) in conflicts

    def test_correct_sum_with_duplicates_still_conflicts(self) -> None:
        cage = CageConstraint(target_sum=6, cells=[(0, 0), (0, 1)])
        grid = Grid.empty()
        grid.set_value(0, 0, 3)
        grid.set_value(0, 1, 3)
        # Sum is correct (6) but duplicates — cells should still conflict
        conflicts = cage.find_conflicts(grid)
        assert (0, 0) in conflicts
        assert (0, 1) in conflicts
