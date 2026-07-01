.PHONY: install install-dev build clean

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

install-docs:
	pip install -e ".[docs]"

build:
	python -m build

clean:
	rm -rf dist/ build/ *.egg-info
