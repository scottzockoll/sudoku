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

    # User highlight colors (index 1-9)
    HIGHLIGHTS: dict[int, tuple[int, int, int]] = {
        1: (207, 232, 239),  # light blue
        2: (209, 237, 209),  # light green
        3: (252, 228, 190),  # light orange
        4: (210, 230, 220),  # mint
        5: (226, 210, 239),  # light purple
        6: (252, 243, 190),  # light yellow
        7: (199, 228, 210),  # teal
        8: (232, 218, 202),  # tan
        9: (215, 215, 215),  # light gray
    }

    # UI
    MODE_TEXT = (56, 108, 206)
