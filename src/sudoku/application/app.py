from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pygame

from sudoku.application.debug_logger import DebugLogger
from sudoku.application.dialog_renderer import DialogRenderer
from sudoku.application.input_handler import InputHandler
from sudoku.application.layout import Layout
from sudoku.application.menu import Menu, MenuItemKind
from sudoku.application.menu_renderer import MenuRenderer
from sudoku.application.perf_overlay import PerfOverlay
from sudoku.application.puzzle_loader import PuzzleLoader
from sudoku.application.renderer import Renderer
from sudoku.application.save_manager import SaveManager
from sudoku.core.game_state import GameState
from sudoku.game.actions import Action
from sudoku.game.game_controller import GameController


@dataclass
class MenuSelection:
    kind: str  # "puzzle" or "save"
    puzzle_path: Path | None = None
    save_slot: int | None = None


def _get_version() -> str:
    import subprocess

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return "dev"


class App:
    def __init__(self, puzzle_path: Path | None = None, debug: bool = False) -> None:
        self._puzzle_path = puzzle_path
        self._running = False
        self._debug_on_start = debug

    @staticmethod
    def _puzzles_dir() -> Path:
        return Path(__file__).parent.parent.parent.parent / "puzzles"

    @staticmethod
    def _saves_dir() -> Path:
        return Path(__file__).parent.parent.parent.parent / "saves"

    def run(self) -> None:
        pygame.init()
        try:
            self._main()
        finally:
            pygame.quit()

    def _main(self) -> None:
        layout = Layout()
        screen = pygame.display.set_mode((layout.screen_width, layout.screen_height))
        pygame.display.set_caption("Sudoku")

        debug = DebugLogger()
        if self._debug_on_start:
            debug.toggle()

        input_handler = InputHandler(debug=debug)
        save_manager = SaveManager(self._saves_dir())
        dialog = DialogRenderer(screen, layout)
        self._running = True

        if self._puzzle_path is not None:
            self._run_game_from_puzzle(
                screen, layout, self._puzzle_path, 1, debug, input_handler, save_manager
            )
        else:
            while self._running:
                selection = self._run_menu(
                    screen, layout, debug, input_handler, save_manager, dialog
                )
                if selection is None:
                    return
                if selection.kind == "puzzle" and selection.puzzle_path is not None:
                    slot = self._run_slot_picker(
                        screen, layout, input_handler, save_manager, dialog
                    )
                    if slot is None:
                        continue  # user cancelled, go back to menu
                    self._run_game_from_puzzle(
                        screen,
                        layout,
                        selection.puzzle_path,
                        slot,
                        debug,
                        input_handler,
                        save_manager,
                    )
                elif selection.kind == "save" and selection.save_slot is not None:
                    self._run_game_from_save(
                        screen, layout, selection.save_slot, debug, input_handler, save_manager
                    )
                elif selection.kind == "about":
                    self._run_about(dialog, input_handler)

    def _run_menu(
        self,
        screen: pygame.Surface,
        layout: Layout,
        debug: DebugLogger,
        input_handler: InputHandler,
        save_manager: SaveManager,
        dialog: DialogRenderer,
    ) -> MenuSelection | None:
        saves = save_manager.list_saves()
        menu = Menu(self._puzzles_dir(), saves=saves)
        menu_renderer = MenuRenderer(screen, layout)
        menu_renderer.render(menu)

        while self._running:
            event = pygame.event.wait()
            pygame.event.post(event)

            actions = input_handler.process_events()
            needs_redraw = False
            did_delete = False

            for action in actions:
                if action == Action.QUIT:
                    self._running = False
                    return None
                if action == Action.ESCAPE:
                    self._running = False
                    return None
                if action == Action.MOVE_UP:
                    menu.move_up()
                    needs_redraw = True
                elif action == Action.MOVE_DOWN:
                    menu.move_down()
                    needs_redraw = True
                elif action in (Action.MOVE_RIGHT,):
                    result = self._select_menu_item(menu)
                    if result is not None:
                        return result
                elif action == Action.DELETE:
                    # Delete save slot if a save is selected
                    item = menu.selected_item
                    if item is not None and item.kind == MenuItemKind.SAVE and item.save_slot:
                        confirmed = self._run_confirm(
                            dialog,
                            input_handler,
                            f"Delete slot {item.save_slot}?",
                        )
                        if confirmed:
                            save_manager.delete(item.save_slot)
                        # Rebuild menu, flush stale events, redraw
                        saves = save_manager.list_saves()
                        menu = Menu(self._puzzles_dir(), saves=saves)
                        pygame.event.clear()
                        menu_renderer.render(menu)
                        did_delete = True
                        break

            if did_delete:
                continue

            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN] or keys[pygame.K_KP_ENTER]:
                result = self._select_menu_item(menu)
                if result is not None:
                    return result

            if needs_redraw:
                menu_renderer.render(menu)

        return None

    @staticmethod
    def _select_menu_item(menu: Menu) -> MenuSelection | None:
        item = menu.selected_item
        if item is None:
            return None
        if item.kind == MenuItemKind.PUZZLE and item.puzzle_entry is not None:
            return MenuSelection(kind="puzzle", puzzle_path=item.puzzle_entry.path)
        if item.kind == MenuItemKind.SAVE and item.save_slot is not None:
            return MenuSelection(kind="save", save_slot=item.save_slot)
        if item.kind == MenuItemKind.ABOUT:
            return MenuSelection(kind="about")
        return None

    def _run_slot_picker(
        self,
        screen: pygame.Surface,
        layout: Layout,
        input_handler: InputHandler,
        save_manager: SaveManager,
        dialog: DialogRenderer,
    ) -> int | None:
        saves = save_manager.list_saves()
        selected = 1
        dialog.render_slot_picker(selected, saves, SaveManager.MAX_SLOTS)

        while self._running:
            event = pygame.event.wait()
            pygame.event.post(event)

            actions = input_handler.process_events()
            needs_redraw = False

            for action in actions:
                if action == Action.QUIT:
                    self._running = False
                    return None
                if action == Action.ESCAPE:
                    return None
                if action == Action.MOVE_UP:
                    selected = ((selected - 2) % SaveManager.MAX_SLOTS) + 1
                    needs_redraw = True
                elif action == Action.MOVE_DOWN:
                    selected = (selected % SaveManager.MAX_SLOTS) + 1
                    needs_redraw = True
                elif action == Action.MOVE_RIGHT:
                    return self._confirm_slot(selected, saves, dialog, input_handler)

            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN] or keys[pygame.K_KP_ENTER]:
                return self._confirm_slot(selected, saves, dialog, input_handler)

            if needs_redraw:
                dialog.render_slot_picker(selected, saves, SaveManager.MAX_SLOTS)

        return None

    def _confirm_slot(
        self,
        slot: int,
        saves: dict[int, dict[str, str]],
        dialog: DialogRenderer,
        input_handler: InputHandler,
    ) -> int | None:
        if slot in saves:
            confirmed = self._run_confirm(dialog, input_handler, f"Overwrite slot {slot}?")
            if not confirmed:
                return None
        return slot

    def _run_confirm(
        self,
        dialog: DialogRenderer,
        input_handler: InputHandler,
        message: str,
    ) -> bool:
        selected_yes = False
        dialog.render_confirm(message, selected_yes)

        while self._running:
            event = pygame.event.wait()
            pygame.event.post(event)

            actions = input_handler.process_events()
            needs_redraw = False

            for action in actions:
                if action == Action.QUIT:
                    self._running = False
                    return False
                if action == Action.ESCAPE:
                    return False
                if action in (Action.MOVE_LEFT, Action.MOVE_RIGHT):
                    selected_yes = not selected_yes
                    needs_redraw = True

            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN] or keys[pygame.K_KP_ENTER]:
                return selected_yes

            if needs_redraw:
                dialog.render_confirm(message, selected_yes)

        return False

    def _run_about(
        self,
        dialog: DialogRenderer,
        input_handler: InputHandler,
    ) -> None:
        dialog.render_about(_get_version())

        while self._running:
            event = pygame.event.wait()
            pygame.event.post(event)

            actions = input_handler.process_events()
            for action in actions:
                if action in (Action.QUIT,):
                    self._running = False
                    return
                if action in (Action.ESCAPE, Action.MOVE_LEFT):
                    return

            keys = pygame.key.get_pressed()
            if keys[pygame.K_RETURN] or keys[pygame.K_KP_ENTER]:
                return

    def _run_game_from_puzzle(
        self,
        screen: pygame.Surface,
        layout: Layout,
        puzzle_path: Path,
        slot: int,
        debug: DebugLogger,
        input_handler: InputHandler,
        save_manager: SaveManager,
    ) -> None:
        loader = PuzzleLoader()
        state = loader.from_file(puzzle_path)

        with puzzle_path.open() as f:
            data = json.load(f)
        puzzle_id_str: str = data.get("id", puzzle_path.stem)

        self._run_game(
            screen, layout, state, puzzle_id_str, slot, debug, input_handler, save_manager
        )

    def _run_game_from_save(
        self,
        screen: pygame.Surface,
        layout: Layout,
        slot: int,
        debug: DebugLogger,
        input_handler: InputHandler,
        save_manager: SaveManager,
    ) -> None:
        loaded = save_manager.load(slot)
        if loaded is None:
            return
        puzzle_id, state = loaded
        self._run_game(screen, layout, state, puzzle_id, slot, debug, input_handler, save_manager)

    _PERF_TIMER_EVENT = pygame.USEREVENT + 1

    def _set_perf_timer(self, perf: PerfOverlay) -> None:
        if perf.enabled:
            pygame.time.set_timer(self._PERF_TIMER_EVENT, 500)
        else:
            pygame.time.set_timer(self._PERF_TIMER_EVENT, 0)

    def _run_game(
        self,
        screen: pygame.Surface,
        layout: Layout,
        state: GameState,
        puzzle_id: str,
        slot: int,
        debug: DebugLogger,
        input_handler: InputHandler,
        save_manager: SaveManager,
    ) -> None:
        perf = PerfOverlay()
        controller = GameController(state)
        renderer = Renderer(screen, layout, perf, debug=debug)

        while self._running:
            event = pygame.event.wait()
            # Perf timer tick — just mark dirty so overlay redraws
            if event.type == self._PERF_TIMER_EVENT:
                if perf.enabled:
                    state.mark_dirty()
            else:
                pygame.event.post(event)

            actions = input_handler.process_events()
            mutated = False
            for action in actions:
                if action == Action.QUIT:
                    pygame.time.set_timer(self._PERF_TIMER_EVENT, 0)
                    save_manager.save(state, puzzle_id, slot)
                    self._running = False
                    return
                debug.log_action(action)
                controller.handle(action)
                debug.log_state(state)
                if action not in (
                    Action.MOVE_UP,
                    Action.MOVE_DOWN,
                    Action.MOVE_LEFT,
                    Action.MOVE_RIGHT,
                    Action.ESCAPE,
                    Action.TOGGLE_NOTES,
                    Action.TOGGLE_COLOR_MODE,
                    Action.APPLY_COLOR,
                ):
                    mutated = True

            # Auto-save after grid mutations
            if mutated:
                save_manager.save(state, puzzle_id, slot)

            keys = pygame.key.get_pressed()
            if keys[pygame.K_F1]:
                perf.toggle()
                self._set_perf_timer(perf)
                state.mark_dirty()
            if keys[pygame.K_F2]:
                debug.toggle()
                state.mark_dirty()
            if keys[pygame.K_ESCAPE] and self._puzzle_path is None:
                pygame.time.set_timer(self._PERF_TIMER_EVENT, 0)
                save_manager.save(state, puzzle_id, slot)
                return

            renderer.render(state)
