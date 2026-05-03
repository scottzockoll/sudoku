.PHONY: test lint typecheck check check-arch run format install-dev

test:
	python -m pytest

lint:
	ruff check src/ tests/
	ruff format --check src/ tests/

typecheck:
	mypy src/

check-arch:
	@echo "Checking onion architecture..."
	@! grep -rn "from sudoku\.game\|import sudoku\.game" src/sudoku/core/ 2>/dev/null || (echo "FAIL: core/ imports from game/" && exit 1)
	@! grep -rn "from sudoku\.application\|import sudoku\.application" src/sudoku/core/ 2>/dev/null || (echo "FAIL: core/ imports from application/" && exit 1)
	@! grep -rn "from sudoku\.application\|import sudoku\.application" src/sudoku/game/ 2>/dev/null || (echo "FAIL: game/ imports from application/" && exit 1)
	@echo "Architecture OK"

check: lint typecheck check-arch test

run:
	python -m sudoku

format:
	ruff format src/ tests/

install-dev:
	pip install -e ".[dev]"
