build:
	python3 -m build

test:
	python3 -m pytest -v tests

.PHONY: build test
