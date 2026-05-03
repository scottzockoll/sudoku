from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from sudoku.game.actions import Action

if TYPE_CHECKING:
    from sudoku.core.game_state import GameState

logger = logging.getLogger("sudoku.debug")


class DebugLogger:
    _initialized = False

    def __init__(self) -> None:
        self.enabled = False
        if not DebugLogger._initialized:
            # Silence all loggers by default
            logging.root.setLevel(logging.ERROR)
            # Remove any existing handlers, add one clean one
            logging.root.handlers.clear()
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(name)s | %(message)s"))
            logging.root.addHandler(handler)
            logger.setLevel(logging.ERROR)
            DebugLogger._initialized = True

    def toggle(self) -> None:
        self.enabled = not self.enabled
        if self.enabled:
            logger.setLevel(logging.DEBUG)
            logger.debug("Debug logging enabled")
        else:
            logger.debug("Debug logging disabled")
            logger.setLevel(logging.ERROR)

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
