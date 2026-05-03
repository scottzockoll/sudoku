import json
from pathlib import Path

from sudoku.application.menu import Menu, MenuItemKind, PuzzleEntry


def _write_puzzles(tmp_path: Path, count: int = 3) -> None:
    for i in range(count):
        data = {"id": f"p{i}", "difficulty": "easy", "grid": [[0] * 9 for _ in range(9)]}
        (tmp_path / f"p{i}.json").write_text(json.dumps(data))


class TestPuzzleEntry:
    def test_from_file(self, tmp_path: Path) -> None:
        data = {"id": "easy_001", "difficulty": "easy", "grid": [[0] * 9 for _ in range(9)]}
        path = tmp_path / "easy_001.json"
        path.write_text(json.dumps(data))
        entry = PuzzleEntry.from_file(path)
        assert entry.puzzle_id == "easy_001"
        assert entry.difficulty == "easy"
        assert entry.has_cages is False
        assert entry.path == path

    def test_from_file_with_cages(self, tmp_path: Path) -> None:
        data = {
            "id": "killer_001",
            "difficulty": "hard",
            "grid": [[0] * 9 for _ in range(9)],
            "constraints": [{"type": "cage", "sum": 10, "cells": [[0, 0], [0, 1]]}],
        }
        path = tmp_path / "killer_001.json"
        path.write_text(json.dumps(data))
        entry = PuzzleEntry.from_file(path)
        assert entry.has_cages is True

    def test_from_file_missing_id(self, tmp_path: Path) -> None:
        data = {"grid": [[0] * 9 for _ in range(9)]}
        path = tmp_path / "test.json"
        path.write_text(json.dumps(data))
        entry = PuzzleEntry.from_file(path)
        assert entry.puzzle_id == "test"

    def test_display_name_standard(self, tmp_path: Path) -> None:
        data = {"id": "easy_001", "difficulty": "easy", "grid": [[0] * 9 for _ in range(9)]}
        path = tmp_path / "easy_001.json"
        path.write_text(json.dumps(data))
        entry = PuzzleEntry.from_file(path)
        assert "easy_001" in entry.display_name
        assert "easy" in entry.display_name

    def test_display_name_killer(self, tmp_path: Path) -> None:
        data = {
            "id": "killer_001",
            "difficulty": "hard",
            "grid": [[0] * 9 for _ in range(9)],
            "constraints": [{"type": "cage", "sum": 10, "cells": [[0, 0], [0, 1]]}],
        }
        path = tmp_path / "killer_001.json"
        path.write_text(json.dumps(data))
        entry = PuzzleEntry.from_file(path)
        assert "killer" in entry.display_name.lower()


class TestMenu:
    def test_scan_puzzles(self, tmp_path: Path) -> None:
        _write_puzzles(tmp_path, 3)
        menu = Menu(tmp_path)
        assert len(menu.entries) == 3

    def test_scan_ignores_non_json(self, tmp_path: Path) -> None:
        _write_puzzles(tmp_path, 1)
        (tmp_path / "readme.txt").write_text("not a puzzle")
        menu = Menu(tmp_path)
        assert len(menu.entries) == 1

    def test_selected_entry(self, tmp_path: Path) -> None:
        _write_puzzles(tmp_path, 3)
        menu = Menu(tmp_path)
        entry = menu.selected_entry
        assert entry is not None

    def test_empty_directory(self, tmp_path: Path) -> None:
        menu = Menu(tmp_path)
        assert len(menu.entries) == 0
        assert menu.selected_entry is None

    def test_move_down_skips_headers(self, tmp_path: Path) -> None:
        _write_puzzles(tmp_path, 3)
        menu = Menu(tmp_path)
        # First selectable item should be selected
        item = menu.selected_item
        assert item is not None
        assert item.kind == MenuItemKind.PUZZLE
        # Move down should go to next puzzle, not a header
        menu.move_down()
        item = menu.selected_item
        assert item is not None
        assert item.kind == MenuItemKind.PUZZLE

    def test_move_up_skips_headers(self, tmp_path: Path) -> None:
        _write_puzzles(tmp_path, 3)
        menu = Menu(tmp_path)
        menu.move_up()
        item = menu.selected_item
        assert item is not None
        # Wrapping up from first puzzle lands on About (last selectable)
        assert item.kind == MenuItemKind.ABOUT

    def test_move_wraps(self, tmp_path: Path) -> None:
        _write_puzzles(tmp_path, 2)
        menu = Menu(tmp_path)
        # Move down past last puzzle hits About, then wraps to first selectable
        menu.move_down()  # puzzle 2
        menu.move_down()  # About
        menu.move_down()  # wraps to first selectable (puzzle 1)
        item = menu.selected_item
        assert item is not None
        assert item.kind == MenuItemKind.PUZZLE


class TestMenuWithSaves:
    def test_always_shows_5_slots(self, tmp_path: Path) -> None:
        _write_puzzles(tmp_path, 1)
        saves = {1: {"puzzle_id": "easy_001"}}
        menu = Menu(tmp_path, saves=saves)
        slot_items = [
            i for i in menu.items if i.kind in (MenuItemKind.SAVE, MenuItemKind.EMPTY_SLOT)
        ]
        assert len(slot_items) == 5

    def test_occupied_slots_are_save_kind(self, tmp_path: Path) -> None:
        _write_puzzles(tmp_path, 1)
        saves = {1: {"puzzle_id": "easy_001"}, 3: {"puzzle_id": "killer_001"}}
        menu = Menu(tmp_path, saves=saves)
        save_items = [i for i in menu.items if i.kind == MenuItemKind.SAVE]
        assert len(save_items) == 2

    def test_empty_slots_show_empty_label(self, tmp_path: Path) -> None:
        _write_puzzles(tmp_path, 1)
        menu = Menu(tmp_path)
        empty_items = [i for i in menu.items if i.kind == MenuItemKind.EMPTY_SLOT]
        assert len(empty_items) == 5
        assert all("[empty]" in i.label for i in empty_items)

    def test_empty_slots_not_selectable(self, tmp_path: Path) -> None:
        _write_puzzles(tmp_path, 1)
        menu = Menu(tmp_path)
        # With no saves, first selectable should be a puzzle, not an empty slot
        item = menu.selected_item
        assert item is not None
        assert item.kind == MenuItemKind.PUZZLE

    def test_save_slot_selectable(self, tmp_path: Path) -> None:
        _write_puzzles(tmp_path, 1)
        saves = {1: {"puzzle_id": "easy_001"}}
        menu = Menu(tmp_path, saves=saves)
        # First selectable should be the save slot
        item = menu.selected_item
        assert item is not None
        assert item.kind == MenuItemKind.SAVE
        assert item.save_slot == 1

    def test_headers_present(self, tmp_path: Path) -> None:
        _write_puzzles(tmp_path, 1)
        menu = Menu(tmp_path)
        headers = [i for i in menu.items if i.kind == MenuItemKind.HEADER and i.label]
        assert len(headers) == 2  # SAVE SLOTS + NEW GAME
        assert headers[0].label == "SAVE SLOTS"
        assert headers[1].label == "NEW GAME"

    def test_about_item_present(self, tmp_path: Path) -> None:
        _write_puzzles(tmp_path, 1)
        menu = Menu(tmp_path)
        about_items = [i for i in menu.items if i.kind == MenuItemKind.ABOUT]
        assert len(about_items) == 1
        assert about_items[0].label == "About"
