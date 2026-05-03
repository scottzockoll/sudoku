class Colors:
    # Background
    BG = (252, 252, 252)

    # Grid lines
    GRID_LINE = (196, 196, 196)
    BOX_LINE = (51, 51, 51)

    # Cell text
    GIVEN_TEXT = (44, 44, 44)
    PLAYER_TEXT = (56, 108, 206)
    NOTES_TEXT = (86, 132, 210)

    # Cell highlights
    SELECTED_CELL = (192, 216, 239)
    SAME_DIGIT_BG = (203, 226, 247)
    RELATED_CELL_BG = (228, 237, 246)
    CONFLICT_BG = (246, 191, 188)

    # Win
    WIN_OVERLAY = (152, 224, 152)

    # Cages
    CAGE_BORDER = (100, 100, 100)
    CAGE_SUM_TEXT = (90, 90, 90)
    CAGE_SUM_ERROR = (210, 50, 50)

    # User highlight colors (index 1-9, each a distinct hue)
    HIGHLIGHTS: dict[int, tuple[int, int, int]] = {
        1: (200, 225, 245),  # blue
        2: (200, 235, 200),  # green
        3: (250, 225, 185),  # orange
        4: (250, 245, 190),  # yellow
        5: (225, 205, 240),  # purple
        6: (245, 210, 225),  # pink
        7: (195, 235, 230),  # teal
        8: (235, 215, 195),  # peach
        9: (215, 215, 215),  # gray
    }

    # UI
    MODE_TEXT = (56, 108, 206)
