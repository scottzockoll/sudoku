from pathlib import Path

from sudoku.application.menu import Menu, MenuItemKind
from sudoku.application.save_manager import SaveManager
from sudoku.core.game_state import GameState
from sudoku.core.grid import Grid


def _setup_saves(tmp_path: Path) -> tuple[Path, SaveManager]:
    puzzles_dir = tmp_path / "puzzles"
    puzzles_dir.mkdir()
    saves_dir = tmp_path / "saves"
    return puzzles_dir, SaveManager(saves_dir)


class TestMenuAfterDelete:
    def test_deleted_slot_becomes_empty(self, tmp_path: Path) -> None:
        puzzles_dir, save_manager = _setup_saves(tmp_path)
        state = GameState(grid=Grid.empty())
        save_manager.save(state, puzzle_id="easy_001", slot=1)

        # Before delete: slot 1 is a SAVE item
        saves = save_manager.list_saves()
        menu = Menu(puzzles_dir, saves=saves)
        slot_items = [i for i in menu.items if i.save_slot == 1]
        assert len(slot_items) == 1
        assert slot_items[0].kind == MenuItemKind.SAVE

        # Delete slot 1
        save_manager.delete(slot=1)

        # After delete: rebuild menu — slot 1 should be EMPTY_SLOT
        saves = save_manager.list_saves()
        menu = Menu(puzzles_dir, saves=saves)
        slot_items = [i for i in menu.items if i.save_slot == 1]
        assert len(slot_items) == 1
        assert slot_items[0].kind == MenuItemKind.EMPTY_SLOT
        assert "[empty]" in slot_items[0].label

    def test_deleted_slot_not_selectable(self, tmp_path: Path) -> None:
        puzzles_dir, save_manager = _setup_saves(tmp_path)
        state = GameState(grid=Grid.empty())
        save_manager.save(state, puzzle_id="easy_001", slot=1)
        save_manager.delete(slot=1)

        saves = save_manager.list_saves()
        menu = Menu(puzzles_dir, saves=saves)

        # The selected item should NOT be the empty slot
        item = menu.selected_item
        # With no puzzles and no saves, there's nothing selectable
        assert item is None or item.kind != MenuItemKind.EMPTY_SLOT

    def test_other_slots_preserved_after_delete(self, tmp_path: Path) -> None:
        puzzles_dir, save_manager = _setup_saves(tmp_path)
        state = GameState(grid=Grid.empty())
        save_manager.save(state, puzzle_id="puzzle_a", slot=1)
        save_manager.save(state, puzzle_id="puzzle_b", slot=3)

        # Delete slot 1 only
        save_manager.delete(slot=1)

        saves = save_manager.list_saves()
        menu = Menu(puzzles_dir, saves=saves)

        # Slot 1 should be empty
        slot1 = [i for i in menu.items if i.save_slot == 1]
        assert slot1[0].kind == MenuItemKind.EMPTY_SLOT

        # Slot 3 should still be a save
        slot3 = [i for i in menu.items if i.save_slot == 3]
        assert slot3[0].kind == MenuItemKind.SAVE
        assert "puzzle_b" in slot3[0].label

    def test_menu_still_has_5_slots_after_delete(self, tmp_path: Path) -> None:
        puzzles_dir, save_manager = _setup_saves(tmp_path)
        state = GameState(grid=Grid.empty())
        for slot in range(1, 6):
            save_manager.save(state, puzzle_id=f"p{slot}", slot=slot)

        save_manager.delete(slot=2)
        save_manager.delete(slot=4)

        saves = save_manager.list_saves()
        menu = Menu(puzzles_dir, saves=saves)

        slot_items = [
            i for i in menu.items if i.kind in (MenuItemKind.SAVE, MenuItemKind.EMPTY_SLOT)
        ]
        assert len(slot_items) == 5

        save_items = [i for i in slot_items if i.kind == MenuItemKind.SAVE]
        empty_items = [i for i in slot_items if i.kind == MenuItemKind.EMPTY_SLOT]
        assert len(save_items) == 3
        assert len(empty_items) == 2
