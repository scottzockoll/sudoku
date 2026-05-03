from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from sudoku.game.actions import Action

if TYPE_CHECKING:
    from sudoku.application.debug_logger import DebugLogger


class InputHandler:
    KEY_MAP: dict[int, Action] = {
        pygame.K_UP: Action.MOVE_UP,
        pygame.K_DOWN: Action.MOVE_DOWN,
        pygame.K_LEFT: Action.MOVE_LEFT,
        pygame.K_RIGHT: Action.MOVE_RIGHT,
        pygame.K_1: Action.DIGIT_1,
        pygame.K_2: Action.DIGIT_2,
        pygame.K_3: Action.DIGIT_3,
        pygame.K_4: Action.DIGIT_4,
        pygame.K_5: Action.DIGIT_5,
        pygame.K_6: Action.DIGIT_6,
        pygame.K_7: Action.DIGIT_7,
        pygame.K_8: Action.DIGIT_8,
        pygame.K_9: Action.DIGIT_9,
        pygame.K_DELETE: Action.DELETE,
        pygame.K_BACKSPACE: Action.DELETE,
        pygame.K_n: Action.TOGGLE_NOTES,
        pygame.K_c: Action.TOGGLE_COLOR_MODE,
        pygame.K_RETURN: Action.APPLY_COLOR,
        pygame.K_z: Action.UNDO,
        pygame.K_y: Action.REDO,
        pygame.K_ESCAPE: Action.ESCAPE,
    }

    def __init__(self, debug: DebugLogger | None = None) -> None:
        self._debug = debug

    def process_events(self) -> list[Action]:
        actions: list[Action] = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                actions.append(Action.QUIT)
            elif event.type == pygame.KEYDOWN:
                action = self.KEY_MAP.get(event.key)
                if self._debug is not None:
                    key_name = pygame.key.name(event.key)
                    self._debug.log_key_event(event.key, key_name, action)
                if action is not None:
                    actions.append(action)
        return actions
