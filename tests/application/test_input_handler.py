from sudoku.application.input_handler import InputHandler
from sudoku.game.actions import Action


class TestKeyMap:
    def test_all_required_actions_mapped(self) -> None:
        """Every non-QUIT action must have at least one key mapped to it."""
        mapped_actions = set(InputHandler.KEY_MAP.values())
        required = {
            Action.MOVE_UP,
            Action.MOVE_DOWN,
            Action.MOVE_LEFT,
            Action.MOVE_RIGHT,
            Action.DIGIT_1,
            Action.DIGIT_2,
            Action.DIGIT_3,
            Action.DIGIT_4,
            Action.DIGIT_5,
            Action.DIGIT_6,
            Action.DIGIT_7,
            Action.DIGIT_8,
            Action.DIGIT_9,
            Action.DELETE,
            Action.TOGGLE_NOTES,
            Action.TOGGLE_COLOR_MODE,
            Action.APPLY_COLOR,
            Action.UNDO,
            Action.REDO,
            Action.ESCAPE,
        }
        missing = required - mapped_actions
        assert missing == set(), f"Actions not mapped to any key: {missing}"

    def test_no_duplicate_key_mappings(self) -> None:
        """Each key should map to exactly one action."""
        keys = list(InputHandler.KEY_MAP.keys())
        assert len(keys) == len(set(keys)), "Duplicate keys in KEY_MAP"
