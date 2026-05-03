from __future__ import annotations

from pathlib import Path

import pygame

from sudoku.application.colors import Colors
from sudoku.application.layout import Layout


class DialogRenderer:
    def __init__(self, screen: pygame.Surface, layout: Layout) -> None:
        self._screen = screen
        self._layout = layout

        font_path = Path(__file__).parent.parent.parent.parent / "assets" / "fonts"
        self._title_font = self._load_font(font_path, "DejaVuSansMono-Bold.ttf", 24)
        self._item_font = self._load_font(font_path, "DejaVuSansMono.ttf", 20)
        self._hint_font = self._load_font(font_path, "DejaVuSansMono.ttf", 14)

    @staticmethod
    def _load_font(font_dir: Path, filename: str, size: int) -> pygame.font.Font:
        path = font_dir / filename
        if path.exists():
            return pygame.font.Font(str(path), size)
        return pygame.font.SysFont("dejavusansmono,monospace", size)

    def render_slot_picker(
        self,
        selected: int,
        saves: dict[int, dict[str, str]],
        max_slots: int,
    ) -> None:
        self._screen.fill(Colors.BG)
        sw = self._layout.screen_width
        sh = self._layout.screen_height

        title = self._title_font.render("SELECT SAVE SLOT", True, Colors.BOX_LINE)
        self._screen.blit(title, title.get_rect(center=(sw // 2, 80)))

        for slot in range(1, max_slots + 1):
            y = 140 + (slot - 1) * 40
            is_selected = slot == selected

            if is_selected:
                rect = (sw // 2 - 200, y - 4, 400, 36)
                pygame.draw.rect(self._screen, Colors.SELECTED_CELL, rect)

            prefix = "> " if is_selected else "  "
            if slot in saves:
                puzzle_id = saves[slot].get("puzzle_id", "unknown")
                label = f"{prefix}Slot {slot}: {puzzle_id} (in use)"
                color = Colors.PLAYER_TEXT if is_selected else (150, 100, 100)
            else:
                label = f"{prefix}Slot {slot}: empty"
                color = Colors.PLAYER_TEXT if is_selected else Colors.BOX_LINE

            text = self._item_font.render(label, True, color)
            self._screen.blit(text, (sw // 2 - 190, y))

        hint = self._hint_font.render(
            "Up/Down: navigate    Enter/Right: select    Esc: back",
            True,
            Colors.GRID_LINE,
        )
        self._screen.blit(hint, hint.get_rect(center=(sw // 2, sh - 30)))

        pygame.display.flip()

    def render_confirm(self, message: str, selected_yes: bool) -> None:
        self._screen.fill(Colors.BG)
        sw = self._layout.screen_width
        sh = self._layout.screen_height

        msg = self._title_font.render(message, True, Colors.BOX_LINE)
        self._screen.blit(msg, msg.get_rect(center=(sw // 2, sh // 2 - 60)))

        # Yes / No buttons
        for i, (label, is_this) in enumerate([("Yes", True), ("No", False)]):
            x = sw // 2 - 80 + i * 120
            y = sh // 2
            is_selected = selected_yes == is_this

            if is_selected:
                rect = (x - 30, y - 4, 100, 36)
                pygame.draw.rect(self._screen, Colors.SELECTED_CELL, rect)

            color = Colors.PLAYER_TEXT if is_selected else Colors.BOX_LINE
            text = self._item_font.render(label, True, color)
            self._screen.blit(text, text.get_rect(center=(x + 20, y + 14)))

        hint = self._hint_font.render(
            "Left/Right: choose    Enter: confirm    Esc: cancel",
            True,
            Colors.GRID_LINE,
        )
        self._screen.blit(hint, hint.get_rect(center=(sw // 2, sh - 30)))

        pygame.display.flip()

    def render_about(self, version: str) -> None:
        self._screen.fill(Colors.BG)
        sw = self._layout.screen_width
        sh = self._layout.screen_height

        title = self._title_font.render("SUDOKU", True, Colors.BOX_LINE)
        self._screen.blit(title, title.get_rect(center=(sw // 2, sh // 2 - 60)))

        lines = [
            f"version {version}",
            "",
            "made by the boys in spring 2026",
        ]
        y = sh // 2 - 30
        for line in lines:
            if line:
                text = self._item_font.render(line, True, Colors.BOX_LINE)
                self._screen.blit(text, text.get_rect(center=(sw // 2, y)))
            y += 30

        hint = self._hint_font.render("Esc: back", True, Colors.GRID_LINE)
        self._screen.blit(hint, hint.get_rect(center=(sw // 2, sh - 30)))

        pygame.display.flip()
