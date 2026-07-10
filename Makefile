# Biomedical AI Infrastructure Lab
# Common local development commands

PYTHON := python
BUILD_DIR := builds/001-governed-biomedical-graphrag
APP_DIR := $(BUILD_DIR)
PYTHONPATH_VALUE := shared:$(BUILD_DIR)

.PHONY: help install test lint format check api ui settings-smoke clean

help:
	@echo "Biomedical AI Infrastructure Lab"
	@echo ""
	@echo "Available commands:"
	@echo "  make install        Install project with dev dependencies"
	@echo "  make test           Run pytest"
	@echo "  make lint           Run Ruff lint checks"
	@echo "  make format         Format code with Ruff"
	@echo "  make check          Run tests and lint checks"
	@echo "  make api            Run FastAPI backend"
	@echo "  make ui             Run Streamlit frontend"
	@echo "  make settings-smoke Validate settings import"
	@echo "  make clean          Remove local Python cache files"

install:
	$(PYTHON) -m pip install --upgrade pip
	pip install -e ".[dev]"

test:
	PYTHONPATH=$(PYTHONPATH_VALUE) pytest

lint:
	ruff check .

format:
	ruff format .
	ruff check . --fix

check: test lint

api:
	uvicorn app.main:app --reload --app-dir $(APP_DIR)

ui:
	streamlit run $(BUILD_DIR)/app/dashboard/streamlit_app.py

settings-smoke:
	PYTHONPATH=$(PYTHONPATH_VALUE) $(PYTHON) -c "from app.config.settings import get_settings; s = get_settings(); print(s.app_env, s.enable_pubmed, s.enable_graph_validation, s.enable_strict_safety)"

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -prune -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
