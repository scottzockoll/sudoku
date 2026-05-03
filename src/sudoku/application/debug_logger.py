from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from sudoku.game.actions import Action

if TYPE_CHECKING:
    from sudoku.core.game_state import GameState

logger = logging.getLogger("sudoku.debug")


class DebugLogger:
    def __init__(self) -> None:
        self.enabled = False

    def toggle(self) -> None:
        self.enabled = not self.enabled
        if self.enabled:
            logging.basicConfig(level=logging.DEBUG, format="%(name)s | %(message)s")
            logger.setLevel(logging.DEBUG)
            logger.debug("Debug logging enabled")
        else:
            logger.debug("Debug logging disabled")

    def log_action(self, action: Action) -> None:
        if self.enabled:
            logger.debug("action: %s", action.name)

    def log_state(self, state: GameState) -> None:
        if self.enabled:
            cell = state.grid.get(*state.cursor.position)
            logger.debug(
                "state: cursor=%s selected=%s mode=%s cell_value=%s cell_notes=%s dirty=%s won=%s",
                state.cursor.position,
                state.selected,
                state.input_mode.name,
                cell.value,
                cell.notes,
                state.dirty,
                state.is_won,
            )

    def log_key_event(self, key: int, key_name: str, mapped: Action | None) -> None:
        if self.enabled:
            if mapped is not None:
                logger.debug("key: key=%d name='%s' -> %s", key, key_name, mapped.name)
            else:
                logger.debug("key: key=%d name='%s' -> unmapped", key, key_name)

    def log_mutation(self, operation: str, **kwargs: Any) -> None:
        if self.enabled:
            details = " ".join(f"{k}={v}" for k, v in kwargs.items())
            logger.debug("mutation: %s %s", operation, details)
