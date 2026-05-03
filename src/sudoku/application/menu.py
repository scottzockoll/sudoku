from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path


class MenuItemKind(Enum):
    PUZZLE = auto()
    SAVE = auto()
    EMPTY_SLOT = auto()
    HEADER = auto()
    ABOUT = auto()


@dataclass
class PuzzleEntry:
    puzzle_id: str
    difficulty: str
    has_cages: bool
    path: Path

    @classmethod
    def from_file(cls, path: Path) -> PuzzleEntry:
        with path.open() as f:
            data = json.load(f)

        puzzle_id = data.get("id", path.stem)
        difficulty = data.get("difficulty", "unknown")
        constraints = data.get("constraints", [])
        has_cages = any(c.get("type") == "cage" for c in constraints)

        return cls(
            puzzle_id=puzzle_id,
            difficulty=difficulty,
            has_cages=has_cages,
            path=path,
        )

    @property
    def display_name(self) -> str:
        kind = "killer" if self.has_cages else "standard"
        return f"{self.puzzle_id}  [{self.difficulty}]  ({kind})"


@dataclass
class MenuItem:
    kind: MenuItemKind
    label: str
    puzzle_entry: PuzzleEntry | None = None
    save_slot: int | None = None
    save_puzzle_id: str | None = None


class Menu:
    def __init__(
        self,
        puzzles_dir: Path,
        saves: dict[int, dict[str, str]] | None = None,
    ) -> None:
        self.items: list[MenuItem] = []
        self.selected_index: int = 0
        self._build(puzzles_dir, saves or {})

    def _build(self, puzzles_dir: Path, saves: dict[int, dict[str, str]]) -> None:
        # Save slots section (always show all 5)
        self.items.append(MenuItem(kind=MenuItemKind.HEADER, label="SAVE SLOTS"))
        for slot in range(1, 6):
            if slot in saves:
                info = saves[slot]
                puzzle_id = info.get("puzzle_id", "unknown")
                self.items.append(
                    MenuItem(
                        kind=MenuItemKind.SAVE,
                        label=f"Slot {slot}: {puzzle_id}",
                        save_slot=slot,
                        save_puzzle_id=puzzle_id,
                    )
                )
            else:
                self.items.append(
                    MenuItem(
                        kind=MenuItemKind.EMPTY_SLOT,
                        label=f"Slot {slot}: [empty]",
                        save_slot=slot,
                    )
                )

        # New game section
        self.items.append(MenuItem(kind=MenuItemKind.HEADER, label="NEW GAME"))
        self._scan_puzzles(puzzles_dir)

        # About section
        self.items.append(MenuItem(kind=MenuItemKind.HEADER, label=""))
        self.items.append(MenuItem(kind=MenuItemKind.ABOUT, label="About"))

        # Start selection on first selectable item
        self._advance_to_selectable(1)

    def _scan_puzzles(self, puzzles_dir: Path) -> None:
        if not puzzles_dir.is_dir():
            return
        paths = sorted(puzzles_dir.glob("*.json"))
        for path in paths:
            try:
                entry = PuzzleEntry.from_file(path)
                self.items.append(
                    MenuItem(
                        kind=MenuItemKind.PUZZLE,
                        label=entry.display_name,
                        puzzle_entry=entry,
                    )
                )
            except (json.JSONDecodeError, KeyError):
                continue

    @property
    def entries(self) -> list[PuzzleEntry]:
        return [item.puzzle_entry for item in self.items if item.puzzle_entry is not None]

    def _is_selectable(self, index: int) -> bool:
        return self.items[index].kind not in (MenuItemKind.HEADER, MenuItemKind.EMPTY_SLOT)

    def _advance_to_selectable(self, direction: int) -> None:
        if not self.items:
            return
        for _ in range(len(self.items)):
            if self._is_selectable(self.selected_index):
                return
            self.selected_index = (self.selected_index + direction) % len(self.items)

    def move_down(self) -> None:
        if not self.items:
            return
        self.selected_index = (self.selected_index + 1) % len(self.items)
        self._advance_to_selectable(1)

    def move_up(self) -> None:
        if not self.items:
            return
        self.selected_index = (self.selected_index - 1) % len(self.items)
        self._advance_to_selectable(-1)

    @property
    def selected_item(self) -> MenuItem | None:
        if not self.items:
            return None
        item = self.items[self.selected_index]
        if item.kind == MenuItemKind.HEADER:
            return None
        return item

    @property
    def selected_entry(self) -> PuzzleEntry | None:
        item = self.selected_item
        if item is None:
            return None
        return item.puzzle_entry
