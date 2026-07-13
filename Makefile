# GraphRoute-TS — reproducible developer commands.
# Everything runs inside the uv-managed project environment.

.DEFAULT_GOAL := help
UV := uv

.PHONY: help sync verify fmt lint type test leakage smoke check jupyter clean-pyc

help: ## Show this help.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

sync: ## Create/refresh the environment from the lockfile.
	$(UV) sync --extra ml --extra retrieval --extra tsfm

verify: ## Environment health check (read-only).
	$(UV) run python scripts/environment_check.py

fmt: ## Format code with ruff.
	$(UV) run ruff format src tests scripts

lint: ## Lint with ruff.
	$(UV) run ruff check src tests scripts

type: ## Type-check with mypy.
	$(UV) run mypy

test: ## Run fast unit tests.
	$(UV) run pytest -q -m unit

leakage: ## Run leakage / split-integrity tests.
	$(UV) run pytest -q -m leakage

smoke: ## Run the environment smoke tests.
	$(UV) run pytest -q -m "unit or leakage" tests/unit/test_smoke.py

check: fmt lint type test leakage ## Run all fast checks.

jupyter: ## Launch JupyterLab.
	$(UV) run jupyter lab

clean-pyc: ## Remove Python caches (safe).
	find . -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
	rm -rf .ruff_cache .mypy_cache .pytest_cache
