from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pygame

from sudoku.application.colors import Colors
from sudoku.application.layout import Layout
from sudoku.core.constraint import CageConstraint
from sudoku.core.game_state import InputMode
from sudoku.core.validator import Validator

if TYPE_CHECKING:
    from sudoku.application.debug_logger import DebugLogger
    from sudoku.application.perf_overlay import PerfOverlay
    from sudoku.core.game_state import GameState


class Renderer:
    def __init__(
        self,
        screen: pygame.Surface,
        layout: Layout,
        perf: PerfOverlay,
        debug: DebugLogger | None = None,
    ) -> None:
        self._screen = screen
        self._layout = layout
        self._perf = perf
        self._debug = debug
        self._validator = Validator()

        font_path = Path(__file__).parent.parent.parent.parent / "assets" / "fonts"
        self._given_font = self._load_font(font_path, "DejaVuSansMono-Bold.ttf", 32)
        self._player_font = self._load_font(font_path, "DejaVuSansMono.ttf", 32)
        self._notes_font = self._load_font(font_path, "DejaVuSansMono.ttf", 14)
        self._mode_font = self._load_font(font_path, "DejaVuSansMono.ttf", 18)
        self._cage_font = self._load_font(font_path, "DejaVuSansMono.ttf", 10)
        self._perf_font = self._load_font(font_path, "DejaVuSansMono.ttf", 12)

    @staticmethod
    def _load_font(font_dir: Path, filename: str, size: int) -> pygame.font.Font:
        path = font_dir / filename
        if path.exists():
            return pygame.font.Font(str(path), size)
        return pygame.font.SysFont("dejavusansmono,monospace", size)

    def render(self, state: GameState) -> bool:
        if not state.dirty:
            self._perf.record_frame(drew=False)
            return False

        self._screen.fill(Colors.BG)
        self._draw_highlights(state)
        self._draw_cage_borders(state)
        self._draw_cells(state)
        self._draw_grid_lines()
        self._draw_mode_indicator(state)

        if state.input_mode == InputMode.COLOR:
            self._draw_color_palette(state)

        if state.is_won:
            self._draw_win_overlay()

        if self._perf.enabled:
            self._draw_perf_overlay()

        if self._debug is not None and self._debug.enabled:
            self._draw_debug_overlay(state)

        pygame.display.flip()
        state.clear_dirty()
        self._perf.record_frame(drew=True)
        return True

    def _draw_highlights(self, state: GameState) -> None:
        # Layer 1: User color highlights (always visible)
        for r in range(9):
            for c in range(9):
                highlight = state.grid.get(r, c).highlight
                if highlight > 0 and highlight in Colors.HIGHLIGHTS:
                    rect = self._layout.cell_rect(r, c)
                    pygame.draw.rect(self._screen, Colors.HIGHLIGHTS[highlight], rect)

        if not state.selected:
            # Still draw conflicts even without selection
            self._draw_conflict_highlights(state)
            return

        row, col = state.cursor.position
        cell = state.grid.get(row, col)

        # Layer 2: Related cells (same row/col/box)
        related = self._validator.get_related_positions(row, col)
        for r, c in related:
            if state.grid.get(r, c).highlight == 0:
                rect = self._layout.cell_rect(r, c)
                pygame.draw.rect(self._screen, Colors.RELATED_CELL_BG, rect)

        # Layer 3: Same-digit cells
        if cell.value is not None:
            same_digit = self._validator.get_same_digit_positions(state, cell.value)
            for r, c in same_digit:
                if (r, c) != (row, col):
                    rect = self._layout.cell_rect(r, c)
                    pygame.draw.rect(self._screen, Colors.SAME_DIGIT_BG, rect)

        # Layer 4: Conflicts
        self._draw_conflict_highlights(state)

        # Layer 5: Selected cell (on top)
        selected_rect = self._layout.cell_rect(row, col)
        pygame.draw.rect(self._screen, Colors.SELECTED_CELL, selected_rect)

    def _draw_conflict_highlights(self, state: GameState) -> None:
        for r in range(9):
            for c in range(9):
                if state.grid.get(r, c).is_conflict:
                    rect = self._layout.cell_rect(r, c)
                    pygame.draw.rect(self._screen, Colors.CONFLICT_BG, rect)

    def _draw_cells(self, state: GameState) -> None:
        for r in range(9):
            for c in range(9):
                cell = state.grid.get(r, c)
                cx, cy, cw, ch = self._layout.cell_rect(r, c)
                center_x = cx + cw // 2
                center_y = cy + ch // 2

                if cell.value is not None:
                    if cell.is_given:
                        font = self._given_font
                        color = Colors.GIVEN_TEXT
                    else:
                        font = self._player_font
                        color = Colors.PLAYER_TEXT

                    text = font.render(str(cell.value), True, color)
                    text_rect = text.get_rect(center=(center_x, center_y))
                    self._screen.blit(text, text_rect)
                elif cell.notes:
                    for digit in cell.notes:
                        nx, ny = self._layout.note_position(r, c, digit)
                        text = self._notes_font.render(str(digit), True, Colors.NOTES_TEXT)
                        text_rect = text.get_rect(center=(nx, ny))
                        self._screen.blit(text, text_rect)

    def _draw_grid_lines(self) -> None:
        layout = self._layout

        for i in range(10):
            if i % 3 == 0:
                width = 3
                color = Colors.BOX_LINE
            else:
                width = 1
                color = Colors.GRID_LINE

            # Horizontal
            y = layout.grid_y + i * layout.cell_size
            pygame.draw.line(
                self._screen,
                color,
                (layout.grid_x, y),
                (layout.grid_x + layout.grid_pixel_size, y),
                width,
            )

            # Vertical
            x = layout.grid_x + i * layout.cell_size
            pygame.draw.line(
                self._screen,
                color,
                (x, layout.grid_y),
                (x, layout.grid_y + layout.grid_pixel_size),
                width,
            )

    def _draw_cage_borders(self, state: GameState) -> None:
        for constraint in state.constraints:
            if isinstance(constraint, CageConstraint):
                self._draw_single_cage(constraint, state)

    def _draw_single_cage(self, cage: CageConstraint, state: GameState) -> None:
        cell_set = set(cage.cells)
        layout = self._layout
        dash_len = 5
        gap_len = 3
        pad = 4  # padding inset from cell edge

        # Draw sum label in the top-left cell of the cage
        if cage.cells:
            min_cell = min(cage.cells, key=lambda p: (p[0], p[1]))
            cx, cy, _, _ = layout.cell_rect(min_cell[0], min_cell[1])

            # Check if cage is fully filled — show red if sum is wrong
            values = [state.grid.get(r, c).value for r, c in cage.cells]
            cage_full = all(v is not None for v in values)
            if cage_full:
                actual_sum = sum(v for v in values if v is not None)
                sum_color = (
                    Colors.CAGE_SUM_ERROR if actual_sum != cage.target_sum else Colors.CAGE_SUM_TEXT
                )
            else:
                sum_color = Colors.CAGE_SUM_TEXT

            text = self._cage_font.render(str(cage.target_sum), True, sum_color)
            self._screen.blit(text, (cx + 2, cy + 1))

        # Draw dashed borders with padding inset from cell edges
        for row, col in cage.cells:
            cx, cy, cw, ch = layout.cell_rect(row, col)

            # Top edge
            if (row - 1, col) not in cell_set:
                self._draw_dashed_line(
                    cx + pad, cy + pad, cx + cw - pad, cy + pad, dash_len, gap_len
                )
            # Bottom edge
            if (row + 1, col) not in cell_set:
                self._draw_dashed_line(
                    cx + pad, cy + ch - pad, cx + cw - pad, cy + ch - pad, dash_len, gap_len
                )
            # Left edge
            if (row, col - 1) not in cell_set:
                self._draw_dashed_line(
                    cx + pad, cy + pad, cx + pad, cy + ch - pad, dash_len, gap_len
                )
            # Right edge
            if (row, col + 1) not in cell_set:
                self._draw_dashed_line(
                    cx + cw - pad, cy + pad, cx + cw - pad, cy + ch - pad, dash_len, gap_len
                )

    def _draw_dashed_line(self, x1: int, y1: int, x2: int, y2: int, dash: int, gap: int) -> None:
        dx = x2 - x1
        dy = y2 - y1
        length = max(abs(dx), abs(dy))
        if length == 0:
            return

        step = dash + gap
        pos = 0
        while pos < length:
            end = min(pos + dash, length)
            frac_start = pos / length
            frac_end = end / length
            sx = int(x1 + dx * frac_start)
            sy = int(y1 + dy * frac_start)
            ex = int(x1 + dx * frac_end)
            ey = int(y1 + dy * frac_end)
            pygame.draw.line(self._screen, Colors.CAGE_BORDER, (sx, sy), (ex, ey), 2)
            pos += step

    def _draw_mode_indicator(self, state: GameState) -> None:
        if state.input_mode == InputMode.NORMAL:
            return

        layout = self._layout
        panel_x = layout.grid_x + layout.grid_pixel_size + 15
        panel_y = layout.grid_y

        label = state.input_mode.name

        # Mode badge
        text = self._mode_font.render(label, True, Colors.MODE_TEXT)
        badge_w = text.get_width() + 16
        badge_h = text.get_height() + 8
        badge_rect = (panel_x, panel_y, badge_w, badge_h)
        pygame.draw.rect(self._screen, (230, 238, 248), badge_rect)
        pygame.draw.rect(self._screen, Colors.MODE_TEXT, badge_rect, 1)
        self._screen.blit(text, (panel_x + 8, panel_y + 4))

    def _draw_color_palette(self, state: GameState) -> None:
        layout = self._layout
        panel_x = layout.grid_x + layout.grid_pixel_size + 15
        panel_y = layout.grid_y + 40
        swatch_size = 30
        spacing = 8
        panel_w = swatch_size + 40
        panel_h = 9 * (swatch_size + spacing) + 40

        # Panel background
        pygame.draw.rect(
            self._screen, (245, 245, 245), (panel_x - 8, panel_y - 8, panel_w + 16, panel_h)
        )
        pygame.draw.rect(
            self._screen, Colors.GRID_LINE, (panel_x - 8, panel_y - 8, panel_w + 16, panel_h), 1
        )

        # Title
        title = self._notes_font.render("Colors", True, Colors.BOX_LINE)
        self._screen.blit(title, (panel_x, panel_y))

        # Swatches
        y = panel_y + 22
        for i in range(1, 10):
            color = Colors.HIGHLIGHTS.get(i, (200, 200, 200))
            is_active = i == state.active_color
            sx = panel_x
            sy = y + (i - 1) * (swatch_size + spacing)

            # Swatch rectangle
            pygame.draw.rect(self._screen, color, (sx, sy, swatch_size, swatch_size))

            # Border — thicker for active color
            border_color = Colors.PLAYER_TEXT if is_active else Colors.GRID_LINE
            border_width = 3 if is_active else 1
            pygame.draw.rect(
                self._screen, border_color, (sx, sy, swatch_size, swatch_size), border_width
            )

            # Number label
            label_color = Colors.PLAYER_TEXT if is_active else Colors.BOX_LINE
            label = self._notes_font.render(str(i), True, label_color)
            self._screen.blit(label, (sx + swatch_size + 6, sy + 6))

    def _draw_win_overlay(self) -> None:
        overlay = pygame.Surface(
            (self._layout.screen_width, self._layout.screen_height), pygame.SRCALPHA
        )
        overlay.fill((*Colors.WIN_OVERLAY, 100))
        self._screen.blit(overlay, (0, 0))

        text = self._given_font.render("SOLVED!", True, (0, 100, 0))
        text_rect = text.get_rect(
            center=(self._layout.screen_width // 2, self._layout.screen_height // 2)
        )
        self._screen.blit(text, text_rect)

    def _draw_perf_overlay(self) -> None:
        lines = [
            f"FPS: {self._perf.fps:.1f}",
            f"Draws: {self._perf.draw_count}",
            f"Skips: {self._perf.skip_count}",
        ]
        y = self._layout.screen_height - len(lines) * 16 - 5
        for line in lines:
            text = self._perf_font.render(line, True, (200, 0, 0))
            self._screen.blit(text, (5, y))
            y += 16

    def _draw_debug_overlay(self, state: GameState) -> None:
        layout = self._layout
        panel_w = layout.grid_x - 15
        panel_x = 5
        if panel_w < 80:
            return

        # State info
        cell = state.grid.get(*state.cursor.position)
        mode_str = state.input_mode.name
        cell_str = str(cell.value) if cell.value is not None else "empty"
        notes_str = ",".join(str(n) for n in sorted(cell.notes)) if cell.notes else "none"
        given_str = "yes" if cell.is_given else "no"
        conflict_str = "yes" if cell.is_conflict else "no"

        lines: list[tuple[str, tuple[int, int, int]]] = [
            ("-- DEBUG --", (200, 0, 0)),
            ("", (0, 0, 0)),
            (f"Mode: {mode_str}", (50, 50, 200)),
            (f"Cursor: ({state.cursor.row}, {state.cursor.col})", (0, 0, 0)),
            (f"Selected: {state.selected}", (0, 0, 0)),
            (f"Cell: {cell_str}", (0, 0, 0)),
            (f"Given: {given_str}", (0, 0, 0)),
            (f"Notes: {notes_str}", (0, 0, 0)),
            (f"Conflict: {conflict_str}", (0, 0, 0)),
            (f"Highlight: {cell.highlight}", (0, 0, 0)),
            (f"Active color: {state.active_color}", (0, 0, 0)),
            (f"Won: {state.is_won}", (0, 0, 0)),
            ("", (0, 0, 0)),
            ("-- CONTROLS --", (200, 0, 0)),
            ("Arrows  Move", (80, 80, 80)),
            ("1-9     Digit/color", (80, 80, 80)),
            ("N       Notes mode", (80, 80, 80)),
            ("C       Color mode", (80, 80, 80)),
            ("Enter   Apply color", (80, 80, 80)),
            ("Z       Undo", (80, 80, 80)),
            ("Y       Redo", (80, 80, 80)),
            ("Del/Bk  Clear", (80, 80, 80)),
            ("Esc     Back/deselect", (80, 80, 80)),
            ("F1      Perf overlay", (80, 80, 80)),
            ("F2      Debug overlay", (80, 80, 80)),
        ]

        # Draw background panel
        panel_h = len(lines) * 16 + 10
        panel_rect = (panel_x - 5, 5, panel_w + 5, panel_h)
        pygame.draw.rect(self._screen, (240, 240, 240), panel_rect)
        pygame.draw.rect(self._screen, (180, 180, 180), panel_rect, 1)

        y = 10
        for text_str, color in lines:
            if text_str:
                text = self._perf_font.render(text_str, True, color)
                self._screen.blit(text, (panel_x, y))
            y += 16
