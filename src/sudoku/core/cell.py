from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class CellKind(Enum):
    GIVEN = auto()
    PLAYER = auto()


@dataclass(frozen=True)
class CellSnapshot:
    value: int | None
    notes: frozenset[int]


class Cell:
    def __init__(
        self,
        kind: CellKind,
        value: int | None = None,
        notes: set[int] | None = None,
    ) -> None:
        self.kind = kind
        self.value = value
        self.notes: set[int] = notes if notes is not None else set()
        self.is_conflict: bool = False
        self.highlight: int = 0  # 0 = none, 1-9 = color index

    @property
    def is_given(self) -> bool:
        return self.kind == CellKind.GIVEN

    @property
    def is_empty(self) -> bool:
        return self.value is None

    def _check_mutable(self) -> None:
        if self.is_given:
            raise ValueError("Cannot modify given cell")

    def set_value(self, value: int) -> None:
        self._check_mutable()
        self.value = value
        self.notes.clear()

    def toggle_note(self, digit: int) -> None:
        self._check_mutable()
        self.value = None
        self.notes.symmetric_difference_update({digit})

    def clear(self) -> None:
        self._check_mutable()
        self.value = None
        self.notes.clear()

    def cycle_highlight(self) -> None:
        self.highlight = (self.highlight + 1) % 10

    def snapshot(self) -> CellSnapshot:
        return CellSnapshot(value=self.value, notes=frozenset(self.notes))

    def restore(self, snap: CellSnapshot) -> None:
        self.value = snap.value
        self.notes = set(snap.notes)
