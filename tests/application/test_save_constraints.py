from pathlib import Path

from sudoku.application.save_manager import SaveManager
from sudoku.core.constraint import CageConstraint
from sudoku.core.game_state import GameState
from sudoku.core.grid import Grid


class TestSaveConstraints:
    def test_save_and_load_preserves_cage_constraints(self, tmp_path: Path) -> None:
        manager = SaveManager(tmp_path)
        cage1 = CageConstraint(target_sum=15, cells=[(0, 0), (0, 1), (1, 0)])
        cage2 = CageConstraint(target_sum=10, cells=[(2, 2), (2, 3)])
        state = GameState(grid=Grid.empty(), constraints=[cage1, cage2])
        manager.save(state, puzzle_id="killer_001", slot=1)

        loaded = manager.load(slot=1)
        assert loaded is not None
        _, loaded_state = loaded
        assert len(loaded_state.constraints) == 2

        c1 = loaded_state.constraints[0]
        assert isinstance(c1, CageConstraint)
        assert c1.target_sum == 15
        assert c1.cells == [(0, 0), (0, 1), (1, 0)]

        c2 = loaded_state.constraints[1]
        assert isinstance(c2, CageConstraint)
        assert c2.target_sum == 10
        assert c2.cells == [(2, 2), (2, 3)]

    def test_save_and_load_no_constraints(self, tmp_path: Path) -> None:
        manager = SaveManager(tmp_path)
        state = GameState(grid=Grid.empty())
        manager.save(state, puzzle_id="easy_001", slot=1)

        loaded = manager.load(slot=1)
        assert loaded is not None
        _, loaded_state = loaded
        assert loaded_state.constraints == []

    def test_cage_rendering_data_survives_roundtrip(self, tmp_path: Path) -> None:
        """Cage target_sum and cells must survive save/load for renderer to draw them."""
        manager = SaveManager(tmp_path)
        cage = CageConstraint(target_sum=23, cells=[(3, 3), (3, 4), (4, 3), (4, 4)])
        state = GameState(grid=Grid.empty(), constraints=[cage])
        state.grid.set_value(3, 3, 9)
        state.grid.set_value(3, 4, 8)
        manager.save(state, puzzle_id="killer_test", slot=2)

        loaded = manager.load(slot=2)
        assert loaded is not None
        _, loaded_state = loaded

        # Grid values preserved
        assert loaded_state.grid.get(3, 3).value == 9
        assert loaded_state.grid.get(3, 4).value == 8

        # Cage constraint preserved
        assert len(loaded_state.constraints) == 1
        c = loaded_state.constraints[0]
        assert isinstance(c, CageConstraint)
        assert c.target_sum == 23
        assert c.cells == [(3, 3), (3, 4), (4, 3), (4, 4)]

    def test_list_saves_shows_killer_type(self, tmp_path: Path) -> None:
        manager = SaveManager(tmp_path)
        cage = CageConstraint(target_sum=10, cells=[(0, 0), (0, 1)])
        state = GameState(grid=Grid.empty(), constraints=[cage])
        manager.save(state, puzzle_id="killer_001", slot=1)

        saves = manager.list_saves()
        assert saves[1]["puzzle_id"] == "killer_001"
