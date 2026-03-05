# Makefile
# --------
# Usage:
# make [COMMAND]
# E.g.:
# make build

.PHONY: help install build clean clean-pycache format

help:
	clear
	head Makefile

install:
	pip install -U pip wheel
	pip install -e .[dev]

build:
	python -m build

# Clean up build artifacts
clean:
	rm -rf build/ dist/ *.egg-info

clean-pycache:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

format:
	ruff check epicpy --fix --exclude epicpy/uifiles
	ruff format epicpy --exclude epicpy/uifiles

device-format:
	ruff check devices_local --fix --no-respect-gitignore
	ruff format devices_local --no-respect-gitignore

device-reset:
	find devices_local -name "data_output.csv" -delete
	find devices_local -name "data_output_*.csv" -delete
	find devices_local -path "*/outputs/*" -type f -delete