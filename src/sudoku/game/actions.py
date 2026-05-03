from enum import Enum, auto


class Action(Enum):
    MOVE_UP = auto()
    MOVE_DOWN = auto()
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    DIGIT_1 = auto()
    DIGIT_2 = auto()
    DIGIT_3 = auto()
    DIGIT_4 = auto()
    DIGIT_5 = auto()
    DIGIT_6 = auto()
    DIGIT_7 = auto()
    DIGIT_8 = auto()
    DIGIT_9 = auto()
    DELETE = auto()
    TOGGLE_NOTES = auto()
    UNDO = auto()
    REDO = auto()
    TOGGLE_COLOR_MODE = auto()
    APPLY_COLOR = auto()
    ESCAPE = auto()
    QUIT = auto()

    def digit_value(self) -> int | None:
        digit_map = {
            Action.DIGIT_1: 1,
            Action.DIGIT_2: 2,
            Action.DIGIT_3: 3,
            Action.DIGIT_4: 4,
            Action.DIGIT_5: 5,
            Action.DIGIT_6: 6,
            Action.DIGIT_7: 7,
            Action.DIGIT_8: 8,
            Action.DIGIT_9: 9,
        }
        return digit_map.get(self)
