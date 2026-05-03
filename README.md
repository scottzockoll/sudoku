# Sudoku

A hardware sudoku device built with a Raspberry Pi Zero, 1024x600 HDMI display, and a custom QMK keyboard (Raspberry Pi Pico).

## Features

- Standard and killer sudoku (cage constraints with sum validation)
- Normal mode, notes mode, and color highlighting mode
- Undo/redo
- 5 save slots with auto-save
- Puzzle selection menu
- Dirty-flag rendering for minimal power usage
- Debug overlay (F2) and perf overlay (F1)
- Cross-platform: Mac, Windows, Pi Zero

## Controls

| Key | Action |
|---|---|
| Arrows | Move cursor |
| 1-9 | Enter digit (normal) / toggle note (notes) / select color (color) |
| N | Toggle notes mode |
| C | Toggle color mode |
| Enter | Apply color (in color mode) |
| Z | Undo |
| Y | Redo |
| Delete/Backspace | Clear cell |
| Escape | Deselect / exit mode / back |
| F1 | Toggle perf overlay |
| F2 | Toggle debug overlay |

## Setup

**Mac/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

**Windows:**

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

## Run

```bash
python -m sudoku

# With debug logging
python -m sudoku --debug
```

## Development

```bash
make check    # lint + typecheck + architecture check + tests
make test     # tests only
make lint     # ruff check + format check
make typecheck # mypy
make format   # auto-format
```

## Architecture

Onion architecture with three layers:

- **core/** — pure Python models and rules (Cell, Grid, Cursor, Constraint, Validator)
- **game/** — actions, undo/redo commands, game controller
- **application/** — pygame renderer, input handler, menus, save system

Inner layers never import from outer layers, enforced by `make check-arch`.

## Hardware

- Raspberry Pi Zero (any model)
- 1024x600 HDMI display
- Raspberry Pi Pico flashed with QMK firmware

### QMK Key Mapping

Map physical buttons to these keycodes in your QMK keymap:

| Button | Keycode |
|---|---|
| Digits 1-9 | `KC_1` - `KC_9` |
| Arrow keys | `KC_UP`, `KC_DOWN`, `KC_LEFT`, `KC_RIGHT` |
| Undo | `KC_Z` |
| Redo | `KC_Y` |
| Notes toggle | `KC_N` |
| Color mode | `KC_C` |
| Delete | `KC_DELETE` |
| Escape | `KC_ESCAPE` |

### Pi Zero Deployment

```bash
sudo cp sudoku.service /etc/systemd/system/
sudo systemctl enable sudoku
sudo systemctl start sudoku
```

## Puzzle Format

```json
{
  "id": "puzzle_name",
  "difficulty": "easy",
  "grid": [[5, 3, 0, ...], ...],
  "constraints": [
    {"type": "cage", "sum": 15, "cells": [[0,0], [0,1], [1,0]]}
  ]
}
```

Grid values: `0` = empty, `1-9` = given. Constraints are optional.
