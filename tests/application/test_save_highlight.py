from pathlib import Path

from sudoku.application.save_manager import SaveManager
from sudoku.core.game_state import GameState
from sudoku.core.grid import Grid


class TestSaveHighlight:
    def test_save_and_load_preserves_highlight(self, tmp_path: Path) -> None:
        manager = SaveManager(tmp_path)
        state = GameState(grid=Grid.empty())
        state.grid.get(0, 0).highlight = 3
        state.grid.get(4, 4).highlight = 7
        manager.save(state, puzzle_id="test", slot=1)

        loaded = manager.load(slot=1)
        assert loaded is not None
        _, loaded_state = loaded
        assert loaded_state.grid.get(0, 0).highlight == 3
        assert loaded_state.grid.get(4, 4).highlight == 7
        assert loaded_state.grid.get(1, 1).highlight == 0

    def test_save_and_load_no_highlight(self, tmp_path: Path) -> None:
        manager = SaveManager(tmp_path)
        state = GameState(grid=Grid.empty())
        manager.save(state, puzzle_id="test", slot=1)

        loaded = manager.load(slot=1)
        assert loaded is not None
        _, loaded_state = loaded
        for r in range(9):
            for c in range(9):
                assert loaded_state.grid.get(r, c).highlight == 0
