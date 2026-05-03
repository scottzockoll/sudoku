from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sudoku.core.cell import Cell, CellKind
from sudoku.core.constraint import CageConstraint, Constraint
from sudoku.core.game_state import GameState, InputMode
from sudoku.core.grid import Grid


class SaveManager:
    MAX_SLOTS = 5

    def __init__(self, saves_dir: Path) -> None:
        self._saves_dir = saves_dir
        self._saves_dir.mkdir(parents=True, exist_ok=True)

    def _slot_path(self, slot: int) -> Path:
        return self._saves_dir / f"slot_{slot}.json"

    @staticmethod
    def _validate_slot(slot: int) -> None:
        if slot < 1 or slot > SaveManager.MAX_SLOTS:
            raise ValueError(f"Slot must be 1-5, got {slot}")

    def save(self, state: GameState, puzzle_id: str, slot: int) -> None:
        self._validate_slot(slot)
        data = self._serialize(state, puzzle_id)
        path = self._slot_path(slot)
        path.write_text(json.dumps(data, indent=2))

    def load(self, slot: int) -> tuple[str, GameState] | None:
        self._validate_slot(slot)
        path = self._slot_path(slot)
        if not path.exists():
            return None
        with path.open() as f:
            data = json.load(f)
        return self._deserialize(data)

    def delete(self, slot: int) -> None:
        self._validate_slot(slot)
        path = self._slot_path(slot)
        if path.exists():
            path.unlink()

    def list_saves(self) -> dict[int, dict[str, str]]:
        saves: dict[int, dict[str, str]] = {}
        for slot in range(1, self.MAX_SLOTS + 1):
            path = self._slot_path(slot)
            if path.exists():
                with path.open() as f:
                    data = json.load(f)
                saves[slot] = {
                    "puzzle_id": data.get("puzzle_id", "unknown"),
                }
        return saves

    @staticmethod
    def _serialize(state: GameState, puzzle_id: str) -> dict[str, Any]:
        grid_data: list[list[dict[str, Any]]] = []
        for row in range(9):
            row_data: list[dict[str, Any]] = []
            for col in range(9):
                cell = state.grid.get(row, col)
                cell_data: dict[str, Any] = {
                    "kind": cell.kind.name,
                    "value": cell.value,
                    "notes": sorted(cell.notes),
                    "highlight": cell.highlight,
                }
                row_data.append(cell_data)
            grid_data.append(row_data)

        constraints_data = SaveManager._serialize_constraints(state.constraints)

        return {
            "puzzle_id": puzzle_id,
            "grid": grid_data,
            "cursor_row": state.cursor.row,
            "cursor_col": state.cursor.col,
            "selected": state.selected,
            "input_mode": state.input_mode.name,
            "active_color": state.active_color,
            "constraints": constraints_data,
        }

    @staticmethod
    def _serialize_constraints(constraints: list[Constraint]) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for constraint in constraints:
            if isinstance(constraint, CageConstraint):
                result.append(
                    {
                        "type": "cage",
                        "sum": constraint.target_sum,
                        "cells": [list(pos) for pos in constraint.cells],
                    }
                )
        return result

    @staticmethod
    def _deserialize_constraints(raw: list[dict[str, Any]]) -> list[Constraint]:
        constraints: list[Constraint] = []
        for entry in raw:
            if entry.get("type") == "cage":
                cells = [(r, c) for r, c in entry["cells"]]
                constraints.append(CageConstraint(target_sum=entry["sum"], cells=cells))
        return constraints

    @staticmethod
    def _deserialize(data: dict[str, Any]) -> tuple[str, GameState]:
        puzzle_id = data["puzzle_id"]

        cells: list[list[Cell]] = []
        for row_data in data["grid"]:
            row_cells: list[Cell] = []
            for cell_data in row_data:
                kind = CellKind[cell_data["kind"]]
                value = cell_data["value"]
                notes = set(cell_data.get("notes", []))
                cell = Cell(kind=kind, value=value, notes=notes)
                cell.highlight = cell_data.get("highlight", 0)
                row_cells.append(cell)
            cells.append(row_cells)

        grid = Grid(cells)
        constraints = SaveManager._deserialize_constraints(data.get("constraints", []))
        state = GameState(grid=grid, constraints=constraints)
        state.cursor.row = data.get("cursor_row", 0)
        state.cursor.col = data.get("cursor_col", 0)
        state.selected = data.get("selected", False)

        mode_name = data.get("input_mode", "NORMAL")
        state.input_mode = InputMode[mode_name]
        state.active_color = data.get("active_color", 1)

        return (puzzle_id, state)
