.PHONY: install test lint typecheck coverage clean

install:
	pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check .
	ruff format --check .

fmt:
	ruff format .

typecheck:
	mypy src/

coverage:
	coverage run -m pytest
	coverage report

clean:
	rm -rf dist/ build/ *.egg-info .coverage htmlcov/
