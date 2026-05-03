from pathlib import Path

import pytest

from sudoku.application.save_manager import SaveManager
from sudoku.core.game_state import GameState, InputMode
from sudoku.core.grid import Grid


def _make_state_with_moves() -> GameState:
    grid = Grid.empty()
    grid.set_value(0, 0, 5)
    grid.set_value(1, 1, 3)
    grid.toggle_note(2, 2, 7)
    grid.toggle_note(2, 2, 8)
    state = GameState(grid=grid)
    state.cursor.row = 3
    state.cursor.col = 4
    state.selected = True
    return state


class TestSaveManager:
    def test_save_creates_file(self, tmp_path: Path) -> None:
        manager = SaveManager(tmp_path)
        state = _make_state_with_moves()
        manager.save(state, puzzle_id="easy_001", slot=1)
        assert (tmp_path / "slot_1.json").exists()

    def test_save_and_load_preserves_values(self, tmp_path: Path) -> None:
        manager = SaveManager(tmp_path)
        state = _make_state_with_moves()
        manager.save(state, puzzle_id="easy_001", slot=1)
        loaded = manager.load(slot=1)
        assert loaded is not None
        puzzle_id, loaded_state = loaded
        assert puzzle_id == "easy_001"
        assert loaded_state.grid.get(0, 0).value == 5
        assert loaded_state.grid.get(1, 1).value == 3

    def test_save_and_load_preserves_notes(self, tmp_path: Path) -> None:
        manager = SaveManager(tmp_path)
        state = _make_state_with_moves()
        manager.save(state, puzzle_id="easy_001", slot=1)
        loaded = manager.load(slot=1)
        assert loaded is not None
        _, loaded_state = loaded
        assert loaded_state.grid.get(2, 2).notes == {7, 8}

    def test_save_and_load_preserves_cursor(self, tmp_path: Path) -> None:
        manager = SaveManager(tmp_path)
        state = _make_state_with_moves()
        manager.save(state, puzzle_id="easy_001", slot=1)
        loaded = manager.load(slot=1)
        assert loaded is not None
        _, loaded_state = loaded
        assert loaded_state.cursor.row == 3
        assert loaded_state.cursor.col == 4

    def test_save_and_load_preserves_given_cells(self, tmp_path: Path) -> None:
        manager = SaveManager(tmp_path)
        grid = Grid.from_raw(
            [
                [5, 0, 0, 0, 0, 0, 0, 0, 0],
                *([[0] * 9] * 8),
            ]
        )
        state = GameState(grid=grid)
        manager.save(state, puzzle_id="test", slot=1)
        loaded = manager.load(slot=1)
        assert loaded is not None
        _, loaded_state = loaded
        assert loaded_state.grid.get(0, 0).is_given
        assert loaded_state.grid.get(0, 0).value == 5

    def test_load_nonexistent_slot(self, tmp_path: Path) -> None:
        manager = SaveManager(tmp_path)
        assert manager.load(slot=1) is None

    def test_slot_range(self, tmp_path: Path) -> None:
        manager = SaveManager(tmp_path)
        state = _make_state_with_moves()
        for slot in range(1, 6):
            manager.save(state, puzzle_id=f"puzzle_{slot}", slot=slot)
        for slot in range(1, 6):
            loaded = manager.load(slot=slot)
            assert loaded is not None
            assert loaded[0] == f"puzzle_{slot}"

    def test_invalid_slot_save(self, tmp_path: Path) -> None:
        manager = SaveManager(tmp_path)
        state = _make_state_with_moves()
        with pytest.raises(ValueError, match="1-5"):
            manager.save(state, puzzle_id="test", slot=0)
        with pytest.raises(ValueError, match="1-5"):
            manager.save(state, puzzle_id="test", slot=6)

    def test_invalid_slot_load(self, tmp_path: Path) -> None:
        manager = SaveManager(tmp_path)
        with pytest.raises(ValueError, match="1-5"):
            manager.load(slot=0)

    def test_list_saves(self, tmp_path: Path) -> None:
        manager = SaveManager(tmp_path)
        state = _make_state_with_moves()
        manager.save(state, puzzle_id="easy_001", slot=1)
        manager.save(state, puzzle_id="killer_001", slot=3)
        saves = manager.list_saves()
        assert 1 in saves
        assert 3 in saves
        assert 2 not in saves
        assert saves[1]["puzzle_id"] == "easy_001"
        assert saves[3]["puzzle_id"] == "killer_001"

    def test_delete_save(self, tmp_path: Path) -> None:
        manager = SaveManager(tmp_path)
        state = _make_state_with_moves()
        manager.save(state, puzzle_id="test", slot=1)
        manager.delete(slot=1)
        assert manager.load(slot=1) is None

    def test_overwrite_save(self, tmp_path: Path) -> None:
        manager = SaveManager(tmp_path)
        state1 = _make_state_with_moves()
        manager.save(state1, puzzle_id="puzzle_a", slot=1)

        state2 = GameState(grid=Grid.empty())
        state2.grid.set_value(0, 0, 9)
        manager.save(state2, puzzle_id="puzzle_b", slot=1)

        loaded = manager.load(slot=1)
        assert loaded is not None
        assert loaded[0] == "puzzle_b"
        assert loaded[1].grid.get(0, 0).value == 9

    def test_save_preserves_input_mode(self, tmp_path: Path) -> None:
        manager = SaveManager(tmp_path)
        state = _make_state_with_moves()
        state.toggle_input_mode()
        assert state.input_mode == InputMode.NOTES
        manager.save(state, puzzle_id="test", slot=1)
        loaded = manager.load(slot=1)
        assert loaded is not None
        _, loaded_state = loaded
        assert loaded_state.input_mode == InputMode.NOTES
