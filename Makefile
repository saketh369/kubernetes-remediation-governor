.PHONY: install test lint demo

install:
	python -m pip install -e '.[dev]'

test:
	pytest

lint:
	ruff check .

demo:
	krg examples/safe-scale.json
