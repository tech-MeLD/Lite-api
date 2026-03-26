PYTHON ?= python

.PHONY: install dev run test lint format typecheck check precommit docker-up docker-down

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e .

dev:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e .[dev]

run:
	uvicorn app.main:app --reload

test:
	pytest

lint:
	ruff check .

format:
	ruff format .

typecheck:
	mypy app

check: lint typecheck test

precommit:
	pre-commit run --all-files

docker-up:
	docker compose up --build

docker-down:
	docker compose down
