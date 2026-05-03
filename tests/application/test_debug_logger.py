import logging

from sudoku.application.debug_logger import DebugLogger
from sudoku.core.game_state import GameState
from sudoku.core.grid import Grid
from sudoku.game.actions import Action


class TestDebugLogger:
    def test_disabled_by_default(self) -> None:
        logger = DebugLogger()
        assert logger.enabled is False

    def test_toggle(self) -> None:
        logger = DebugLogger()
        logger.toggle()
        assert logger.enabled is True
        logger.toggle()
        assert logger.enabled is False

    def test_log_action_when_enabled(self, caplog: logging.LogRecord) -> None:
        logger = DebugLogger()
        logger.toggle()
        with caplog.at_level(logging.DEBUG, logger="sudoku.debug"):
            logger.log_action(Action.DIGIT_5)
        assert "DIGIT_5" in caplog.text

    def test_log_action_when_disabled(self, caplog: logging.LogRecord) -> None:
        logger = DebugLogger()
        with caplog.at_level(logging.DEBUG, logger="sudoku.debug"):
            logger.log_action(Action.DIGIT_5)
        assert "DIGIT_5" not in caplog.text

    def test_log_state_when_enabled(self, caplog: logging.LogRecord) -> None:
        logger = DebugLogger()
        logger.toggle()
        state = GameState(grid=Grid.empty())
        state.cursor.row = 3
        state.cursor.col = 5
        state.selected = True
        with caplog.at_level(logging.DEBUG, logger="sudoku.debug"):
            logger.log_state(state)
        assert "cursor=(3, 5)" in caplog.text
        assert "selected=True" in caplog.text
        assert "mode=NORMAL" in caplog.text

    def test_log_key_event_when_enabled(self, caplog: logging.LogRecord) -> None:
        logger = DebugLogger()
        logger.toggle()
        with caplog.at_level(logging.DEBUG, logger="sudoku.debug"):
            logger.log_key_event(key=113, key_name="q", mapped=None)
        assert "key=113" in caplog.text
        assert "name='q'" in caplog.text
        assert "unmapped" in caplog.text

    def test_log_key_event_mapped(self, caplog: logging.LogRecord) -> None:
        logger = DebugLogger()
        logger.toggle()
        with caplog.at_level(logging.DEBUG, logger="sudoku.debug"):
            logger.log_key_event(key=49, key_name="1", mapped=Action.DIGIT_1)
        assert "DIGIT_1" in caplog.text

    def test_log_mutation_when_enabled(self, caplog: logging.LogRecord) -> None:
        logger = DebugLogger()
        logger.toggle()
        with caplog.at_level(logging.DEBUG, logger="sudoku.debug"):
            logger.log_mutation("set_value", row=0, col=0, value=5)
        assert "set_value" in caplog.text
        assert "row=0" in caplog.text
        assert "col=0" in caplog.text
        assert "5" in caplog.text
