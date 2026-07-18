.PHONY: sync format check check-lock test docs clean fetch-robot check-ontophora check-ontoplexis check-ontopoiesis test-ontophora test-ontoplexis test-ontopoiesis

ROBOT_VERSION := 1.9.10
ROBOT_JAR := packages/ontoplexis/.cache/robot/robot.jar
ROBOT_URL := https://github.com/ontodev/robot/releases/download/v$(ROBOT_VERSION)/robot.jar

sync:
	uv sync --locked --all-packages --all-groups

format:
	uv run --directory packages/ontophora ruff check --fix .
	uv run --directory packages/ontophora ruff format .
	uv run --directory packages/ontoplexis ruff check --fix .
	uv run --directory packages/ontoplexis ruff format .
	uv run --directory packages/ontopoiesis ruff check --fix .
	uv run --directory packages/ontopoiesis ruff format .

check: check-lock check-ontophora check-ontoplexis check-ontopoiesis

check-lock:
	uv lock --check

check-ontophora:
	uv run --directory packages/ontophora ruff check .
	uv run --directory packages/ontophora ruff format --check .
	uv run --directory packages/ontophora ty check
	uv run --directory packages/ontophora pytest

check-ontoplexis: fetch-robot
	uv run --directory packages/ontoplexis ruff check .
	uv run --directory packages/ontoplexis ruff format --check .
	uv run --directory packages/ontoplexis ty check
	uv run --directory packages/ontoplexis pytest

check-ontopoiesis:
	uv run --directory packages/ontopoiesis ruff check .
	uv run --directory packages/ontopoiesis ruff format --check .
	uv run --directory packages/ontopoiesis ty check
	uv run --directory packages/ontopoiesis pytest

test: test-ontophora test-ontoplexis test-ontopoiesis

test-ontophora:
	uv run --directory packages/ontophora pytest

test-ontoplexis: fetch-robot
	uv run --directory packages/ontoplexis pytest

test-ontopoiesis:
	uv run --directory packages/ontopoiesis pytest

fetch-robot:
	@if [ ! -f $(ROBOT_JAR) ]; then \
		mkdir -p $(dir $(ROBOT_JAR)); \
		wget -q -O $(ROBOT_JAR).tmp $(ROBOT_URL) && mv $(ROBOT_JAR).tmp $(ROBOT_JAR); \
	fi

docs:
	uv run zensical build --clean --strict

clean:
	rm -rf .cache .venv site
	rm -rf packages/*/.cache packages/*/.hypothesis packages/*/.pytest_cache packages/*/.ruff_cache packages/*/.venv packages/*/build packages/*/dist packages/*/htmlcov packages/*/site packages/*/src/*.egg-info
