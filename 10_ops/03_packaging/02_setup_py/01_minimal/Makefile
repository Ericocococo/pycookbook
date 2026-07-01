.PHONY: install build clean

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

build:
	python -m build

clean:
	rm -rf dist/ build/ *.egg-info
