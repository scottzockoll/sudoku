from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pygame

from sudoku.application.colors import Colors
from sudoku.application.layout import Layout
from sudoku.application.menu import MenuItemKind

if TYPE_CHECKING:
    from sudoku.application.menu import Menu


class MenuRenderer:
    def __init__(self, screen: pygame.Surface, layout: Layout) -> None:
        self._screen = screen
        self._layout = layout

        font_path = Path(__file__).parent.parent.parent.parent / "assets" / "fonts"
        self._title_font = self._load_font(font_path, "DejaVuSansMono-Bold.ttf", 36)
        self._header_font = self._load_font(font_path, "DejaVuSansMono-Bold.ttf", 16)
        self._item_font = self._load_font(font_path, "DejaVuSansMono.ttf", 20)
        self._hint_font = self._load_font(font_path, "DejaVuSansMono.ttf", 14)

    @staticmethod
    def _load_font(font_dir: Path, filename: str, size: int) -> pygame.font.Font:
        path = font_dir / filename
        if path.exists():
            return pygame.font.Font(str(path), size)
        return pygame.font.SysFont("dejavusansmono,monospace", size)

    def render(self, menu: Menu) -> None:
        self._screen.fill(Colors.BG)
        sw = self._layout.screen_width
        sh = self._layout.screen_height

        # Title
        title = self._title_font.render("SUDOKU", True, Colors.BOX_LINE)
        self._screen.blit(title, title.get_rect(center=(sw // 2, 50)))

        if not menu.items:
            msg = self._item_font.render("No puzzles found", True, Colors.GRID_LINE)
            self._screen.blit(msg, msg.get_rect(center=(sw // 2, sh // 2)))
        else:
            start_y = 100
            line_h = 32

            for i, item in enumerate(menu.items):
                y = start_y + i * line_h

                if item.kind == MenuItemKind.HEADER:
                    # Draw section header
                    text = self._header_font.render(item.label, True, Colors.GRID_LINE)
                    self._screen.blit(text, (sw // 2 - 240, y + 4))
                    # Underline
                    pygame.draw.line(
                        self._screen,
                        Colors.GRID_LINE,
                        (sw // 2 - 240, y + 24),
                        (sw // 2 + 240, y + 24),
                        1,
                    )
                elif item.kind == MenuItemKind.EMPTY_SLOT:
                    # Grayed out, not selectable
                    text = self._item_font.render(f"  {item.label}", True, Colors.GRID_LINE)
                    self._screen.blit(text, (sw // 2 - 240, y))
                else:
                    is_selected = i == menu.selected_index

                    if is_selected:
                        rect = (sw // 2 - 250, y - 2, 500, line_h - 2)
                        pygame.draw.rect(self._screen, Colors.SELECTED_CELL, rect)

                    prefix = "> " if is_selected else "  "
                    color = Colors.PLAYER_TEXT if is_selected else Colors.BOX_LINE
                    text = self._item_font.render(f"{prefix}{item.label}", True, color)
                    self._screen.blit(text, (sw // 2 - 240, y))

        # Controls hint
        hint = self._hint_font.render(
            "Up/Down: navigate    Enter/Right: select    Del: delete save    Esc: quit",
            True,
            Colors.GRID_LINE,
        )
        self._screen.blit(hint, hint.get_rect(center=(sw // 2, sh - 30)))

        pygame.display.flip()
